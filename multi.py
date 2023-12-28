from knapsack import Knapsack, KnapConfig
import time
import multiprocessing

def run(idx, q, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue):
    print(f"Process {idx} started.")
    while True:
        msg = q.get(block=True)
        i, sum_val, sum_weight, limit_weight, arr, items = msg
        DFS(i, sum_val, sum_weight, limit_weight, arr, items, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue)
        #print(f"Process {idx} finished.")
        process_status_lock.acquire()
        processes_status[idx] = False # finish and waiting for input
        process_status_lock.release()
            
def manager_run(processes_status, process_status_lock):
    while True:
        process_status_lock.acquire()
        if all(processes_status) == False:
            process_status_lock.release()
            print(f"All tasks finished.")
            break
        process_status_lock.release()
        
        time.sleep(0.1) 

def DFS(idx, sum_val, sum_weight, limit_weight, arr, items, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue):
    if idx == len(items):
        lock.acquire()
        if sum_val > best_val.value:
            best_val.value = sum_val
            for i in range(len(best_arr)):
                best_arr[i] = -1
            for i in range(len(arr)):
                best_arr[i] = arr[i]
        lock.release()
        
    for i in range(idx, len(items)):
        if sum_weight + items[i].weight <= limit_weight:
            # if there are idle processes, send the task to the idle process
            process_status_lock.acquire()
            idle_process_idx = -1
            for j in range(len(processes_status)):
                if processes_status[j] == False:
                    idle_process_idx = j
                    break
            if idle_process_idx != -1:
                processes_queue[idle_process_idx].put((
                    i+1, 
                    sum_val + items[i].value,
                    sum_weight + items[i].weight, 
                    limit_weight, 
                    arr+[items[i].id], 
                    items
                ))
                processes_status[idle_process_idx] = True
                process_status_lock.release()
                continue
            process_status_lock.release()
            
            DFS(
                idx=i+1,
                sum_val=sum_val + items[i].value, 
                sum_weight=sum_weight + items[i].weight, 
                limit_weight=limit_weight, 
                arr=arr+[items[i].id], 
                items=items,
                best_val=best_val,
                best_arr=best_arr,
                lock=lock,
                processes_status=processes_status,
                process_status_lock=process_status_lock,
                processes_queue=processes_queue
            )
    return

# for comparison
def single_DFS(idx, sum_val, sum_weight, limit_weight, arr, items):
    if idx == len(items):
        return sum_val, arr
    max_val = 0
    max_arr = []
    for i in range(idx, len(items)):
        if sum_weight + items[i].weight <= limit_weight:
            n_val, n_arr = single_DFS(
                    idx=i+1,
                    sum_val=sum_val + items[i].value, 
                    sum_weight=sum_weight + items[i].weight, 
                    limit_weight=limit_weight, 
                    arr=arr+[items[i].id], 
                    items=items
                )
            if n_val > max_val:
                max_val = n_val
                max_arr = n_arr
    return max_val, max_arr

def main():
    # Create a knapsack problem
    config = KnapConfig(
        num=40,
        weightUpper=20,
        weightLower=1,
        valueUpper=5,
        valueLower=1,
        weightLimit=30
    )
    knapsack = Knapsack(config=config)
    knapsack.generate()
    items = knapsack.get_items()
    
    #===========================================================================
    # Parallelize
    #===========================================================================
    
    start = time.time()
    # DFS probelm formulation (args: idx, sum_val, sum_weight, limit_weight, arr, items)
    knapsack_obj = (0, 0, 0, config.weightLimit, [], items)
    
    # answer for knapsack problem
    best_val = multiprocessing.Value('i', 0)
    best_arr = multiprocessing.Array('i', len(knapsack_obj[5])) # length of items (this is the maximum length of arr)
    lock = multiprocessing.Lock()
    
    num_process = 5
    processes_status = multiprocessing.Array('b', num_process) # True: running, False: waiting for input
    process_status_lock = multiprocessing.Lock()
    processes = []
    processes_queue = []
    for i in range(num_process):
        q = multiprocessing.Queue()
        processes_queue.append(q)
        p = multiprocessing.Process(target=run, args=(i, q, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue))
        processes.append(p)
        processes_status[i] = False # True: running, False: waiting for input
    
    for p in processes:
        p.start()
    
    # init for the first process
    processes_status[0] = True
    processes_queue[0].put(knapsack_obj)
    
    # init a manager process
    # once all processes are finished, the manager process will be finished
    manager_process = multiprocessing.Process(target=manager_run, args=(processes_status, process_status_lock))
    manager_process.start()
    
    manager_process.join()
    parallelize_time = time.time() - start
    print(f"Parallelize: best_val: {best_val.value}, best_arr: {best_arr[:]}")
    print(f"Parallelize time: {parallelize_time}")
    
    # kill all processes
    for p in processes:
        p.terminate()
        
    #===========================================================================
    # Single
    #===========================================================================
    start = time.time()
    # for comparison
    val, arr = single_DFS(
        idx=0,
        sum_val=0,
        sum_weight=0,
        limit_weight=config.weightLimit,
        arr=[],
        items=items
    )
    single_time = time.time() - start
    print(f"Single:      best_val: {val}, best_arr: {arr}")
    print(f"Single time:      {single_time}")
    
    

if __name__ == '__main__':
    main()