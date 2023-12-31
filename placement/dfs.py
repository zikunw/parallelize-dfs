from dfsUtil import *
from singleThreadDFS import *
from multiThreadDFS import *

import multiprocessing as mp
from enum import Enum
import time
import os

worker_result_path = lambda idx: f"temp/worker_{idx}_result.txt"

class ProcessStatus(Enum):
    UNINIT = 0
    RUNNING = 1
    WAITING = 2
    HAS_TASK = 3

def compareResult(result1, result2): 
    if len(result1) != len(result2):
        return False
    
    for i in range(len(result1)):
        if result1[i] != result2[i]:
            return False
    
    return True

# ======== single thread dfs ======== 
def runSingle(ops):
    
    start = time.time()
    
    # final results
    plans = []
    # current placement plan
    curPlace = []

    OuterDFS(ops, curPlace, plans)
    
    end = time.time()
        
    return plans, end-start

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
            
        print(f"Process {idx} received msg.")
        MultiOuterDFS(worker_result_file, ops, ops_index, curPlace, plans, processes_status, process_status_lock, processes_queue)
        print(f"Process {idx} finished.")
        
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
    ops = sorted(ops, key=lambda x: x.parallelim)
    print("Sorted ops: ", [op.name for op in ops])
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

if __name__ == "__main__":
    # dfs operator stack
    ops = []
    # ops.append(OP("source", 4))
    # ops.append(OP("map", 10))
    # ops.append(OP("filter", 8))
    # ops.append(OP("sink", 4))
    
    # ops.append(OP("source", 2))
    # ops.append(OP("map", 4))
    # ops.append(OP("sink", 2))
    
    ops.append(OP("source", 12))
    ops.append(OP("map", 8))
    ops.append(OP("sink", 6))
    ops.append(OP("good", 4))
    
    singleplans, singletime = runSingle(ops)
    multiplans, multitime = runMulti(ops, 4)
        
    # ======== compare results ========
    # print("Compare results: ", compareResult(singleplans, multiplans))
    # # if not compareResult(singleplans, multiplans):
    # #     for i in range(len(singleplans)):
    # #         print("i = ", i)
    # #         print("Single: ", singleplans[i])
    # #         print("Multi: ", multiplans[i])
    print("Single size: ", len(singleplans))
    print("Multi size:  ", len(multiplans))
    print("Single time: ", singletime)
    print("Multi time:  ", multitime)

    


