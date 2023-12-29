from knapsack import Knapsack, KnapConfig
import random
import time
import multiprocessing
from enum import Enum

class ProcessStatus(Enum):
    UNINIT = 0
    RUNNING = 1
    WAITING = 2
    HAS_TASK = 3

def run(idx, q, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue):
    print(f"Process {idx} started.")
    process_status_lock.acquire()
    processes_status[idx] = ProcessStatus.WAITING.value # finish and waiting for input
    process_status_lock.release()
    
    while True:
        msg = q.get(block=True)
        i, sum_val, sum_weight, limit_weight, arr, items = msg
        process_status_lock.acquire()
        print(f"Process status: {[i for i in processes_status]}")
        processes_status[idx] = ProcessStatus.RUNNING.value
        process_status_lock.release()
        print(f"Process {idx} received msg.")
        DFS(i, sum_val, sum_weight, limit_weight, arr, items, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue)
        print(f"Process {idx} finished.")
        process_status_lock.acquire()
        if processes_status[idx] == ProcessStatus.RUNNING.value:
            processes_status[idx] = ProcessStatus.WAITING.value
        process_status_lock.release()
            
def manager_run(processes_status, process_status_lock):
    while True:
        process_status_lock.acquire()
        stopped = True
        #print(f"Process status: {[i for i in processes_status]}")
        for i in range(len(processes_status)):
            if processes_status[i] != ProcessStatus.WAITING.value:
                stopped = False
                break
        if stopped:
            print("All processes finished.")
            break
        process_status_lock.release()
        
        time.sleep(0.01) 

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
        
    # cut-off by layer
    divise = False
    if idx <= len(items) / 10:
        divise = True
        
    for i in range(idx, len(items)):
        if sum_weight + items[i].weight <= limit_weight:
            # if there are idle processes, send the task to the idle process
            if divise:
                process_status_lock.acquire()
                idle_process_idx = -1
                for j in range(len(processes_status)):
                    if processes_status[j] == ProcessStatus.WAITING.value:
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
                    processes_status[idle_process_idx] = ProcessStatus.HAS_TASK.value
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
    random_seed = 0 #123 #12431 #2540 #16
    random.seed(random_seed)
    
    # Create a knapsack problem
    config = KnapConfig(
        num=40,
        weightUpper=10,
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
    
    num_process = 8
    processes_status = multiprocessing.Array('i', num_process) # Status of processes
    process_status_lock = multiprocessing.Lock()
    processes = []
    processes_queue = []
    for i in range(num_process):
        q = multiprocessing.Queue()
        processes_queue.append(q)
        p = multiprocessing.Process(target=run, args=(i, q, best_val, best_arr, lock, processes_status, process_status_lock, processes_queue))
        processes.append(p)
        processes_status[i] = ProcessStatus.UNINIT.value
    
    for p in processes:
        p.start()
        
    # wait for all processes to be initialized
    while True:
        process_status_lock.acquire()
        all_init = True
        for i in range(len(processes_status)):
            if processes_status[i] != ProcessStatus.WAITING.value:
                all_init = False
                break
        if all_init:
            process_status_lock.release()
            break
        process_status_lock.release()
        time.sleep(0.01)
    
    print("All processes initialized.")
    
    # init for the first process
    processes_status[0] = ProcessStatus.RUNNING.value
    processes_queue[0].put(knapsack_obj)
    
    # init a manager process
    # once all processes are finished, the manager process will be finished
    manager_process = multiprocessing.Process(target=manager_run, args=(processes_status, process_status_lock))
    manager_process.start()
    
    manager_process.join()
    parallelize_time = time.time() - start
    
    best_arr = [i for i in best_arr if i != -1]
    
    print(f"Parallelize: best_val: {best_val.value}, best_arr: {best_arr[:]} time: {parallelize_time}")
    
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
    print(f"Single:      best_val: {val}, best_arr: {arr} time: {single_time}")
    
if __name__ == '__main__':
    main()