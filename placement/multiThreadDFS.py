import copy
from dfsUtil import *
import time
import os
from enum import Enum
import multiprocessing as mp 

worker_result_path = lambda idx: f"temp/worker_{idx}_result.txt"

class ProcessStatus(Enum):
    UNINIT = 0
    RUNNING = 1
    WAITING = 2
    HAS_TASK = 3
    
# ======== multi thread dfs ========
def run(idx, ops, plans, processes_status, process_status_lock, processes_queue):
    message_queue = processes_queue[idx]
    print(f"Process {idx} started.")
    # finish and waiting for input
    with process_status_lock:
        processes_status[idx] = ProcessStatus.WAITING.value 
    
    worker_result_file = open(worker_result_path(idx), "w")
    
    while True:
        msg = message_queue.get(block=True)
        
        if msg == "terminate":
            worker_result_file.close()
            return
        
        ops_index, curPlace = msg # For now, only one message type (for outer dfs)
        
        with process_status_lock:
            processes_status[idx] = ProcessStatus.RUNNING.value
            
        #print(f"Process {idx} received msg.")
        MultiOuterDFS(worker_result_file, ops, ops_index, curPlace, plans, processes_status, process_status_lock, processes_queue)
        #print(f"Process {idx} finished.")
        
        with process_status_lock:
            if processes_status[idx] == ProcessStatus.RUNNING.value:
                processes_status[idx] = ProcessStatus.WAITING.value
        
def manager_run(processes_status, process_status_lock):
    #print("Manager process started.")
    while True:
        with process_status_lock:
            stopped = True
            for i in range(len(processes_status)):
                if processes_status[i] != ProcessStatus.WAITING.value:
                    stopped = False
                    break
            if stopped:
                print("All processes finished.")
                return
        time.sleep(0.01)

def runMulti(ops, num_processes=4):
    with mp.Manager() as manager:
        start = time.time()
        # final results
        plans = [manager.list() for i in range(num_processes)]
        process_status_lock = manager.Lock()
        processes_status = manager.Array('i', range(num_processes))
        processes = []
        processes_queue = [manager.Queue() for i in range(num_processes)]
        for idx in range(num_processes):
            processes.append(mp.Process(target=run, args=(
                    idx,
                    ops,
                    plans[idx],
                    processes_status,
                    process_status_lock,
                    processes_queue
                )))
            processes_status[idx] = ProcessStatus.UNINIT.value
            
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
        processes_queue[0].put((0, [])) # (ops_index, curPlace)
        
        manager_run(processes_status, process_status_lock)
        
        # wait for all processes to be finished
        for i in range(len(processes)):
            processes_queue[i].put("terminate")
            
        for p in processes:
            p.join()
        
        total_plans = []
        for i in range(num_processes):
            with open(worker_result_path(i), "r") as f:
                for line in f:
                    total_plans.append(line.strip())
                    
        # remove temp files
        for i in range(num_processes):
            os.remove(worker_result_path(i))
            
        end = time.time()
        
        return total_plans, end-start

def MultiOuterDFS(worker_result_file, ops, ops_index, curPlace, plans, processes_status, process_status_lock, processes_queue):
    
    #print("OuterDFS: ops = ", [op.name for op in ops], "curPlace = ", curPlace)
    
    if len(ops) == ops_index:
        worker_result_file.write(str(curPlace) + "\n")
        return

    currentOP = ops[-ops_index] #ops.pop()
    nodeList = []  # record temp placement for the current op
    MultiInnerDFS(worker_result_file, currentOP, ops, ops_index+1, currentOP.parallelim, curPlace, nodeList, plans, processes_status, process_status_lock, processes_queue)

def MultiInnerDFS(worker_result_file, op, ops, ops_index, leftTasks, curPlace, nodeList, plans, processes_status, process_status_lock, processes_queue):
    
    #print("InnerDFS: op = ", op.name, "leftTasks = ", leftTasks, "curPlace = ", curPlace, "nodeList = ", nodeList)
    
    # Terminating condition
    if leftTasks <= 0:
        
        # check cut-off
        # HACK: the cut off should be adjusted according to the number of ops in total
        #       use magic number for now
        if len(ops)-ops_index >= 2:
            # if there are idle processes, send the task to the idle process
            with process_status_lock:
                idle_process_idx = -1
                for j in range(len(processes_status)):
                    if processes_status[j] == ProcessStatus.WAITING.value:
                        idle_process_idx = j
                        break
                if idle_process_idx != -1:
                    processes_queue[idle_process_idx].put((ops_index, [strNodeList(nodeList)] + curPlace))
                    processes_status[idle_process_idx] = ProcessStatus.HAS_TASK.value
                    return
        
        # explore next op
        MultiOuterDFS(worker_result_file, ops, ops_index, [strNodeList(nodeList)] + curPlace, plans, processes_status, process_status_lock, processes_queue)
        return

    upperBound = min(3, leftTasks)
    
    for i in range(upperBound):
        taskPlaced = i+1
        MultiInnerDFS(worker_result_file, op, ops, ops_index, leftTasks-taskPlaced, curPlace, nodeList + [op.name + str(taskPlaced)], plans, processes_status, process_status_lock, processes_queue)