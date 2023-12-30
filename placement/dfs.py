from dfsUtil import *
from singleThreadDFS import *
from multiThreadDFS import *

import multiprocessing as mp
from enum import Enum
import time

class ProcessStatus(Enum):
    UNINIT = 0
    RUNNING = 1
    WAITING = 2
    HAS_TASK = 3

def compareResult(result1, result2):
    result1 = sorted(result1)
    result2 = sorted(result2)
    
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
def run(idx, plans, plans_lock, processes_status, process_status_lock, processes_queue):
    message_queue = processes_queue[idx]
    print(f"Process {idx} started.")
    process_status_lock.acquire()
    processes_status[idx] = ProcessStatus.WAITING.value # finish and waiting for input
    process_status_lock.release()
    
    while True:
        msg = message_queue.get(block=True)
        ops, curPlace = msg # For now, only one message type (for outer dfs)
        
        with process_status_lock:
            processes_status[idx] = ProcessStatus.RUNNING.value
            
        print(f"Process {idx} received msg.")
        MultiOuterDFS(ops, curPlace, plans, plans_lock, processes_status, process_status_lock, processes_queue)
        print(f"Process {idx} finished.")
        
        with process_status_lock:
            if processes_status[idx] == ProcessStatus.RUNNING.value:
                processes_status[idx] = ProcessStatus.WAITING.value
        
def manager_run(processes_status, process_status_lock):
    while True:
        with process_status_lock:
            stopped = True
            for i in range(len(processes_status)):
                if processes_status[i] != ProcessStatus.WAITING.value:
                    stopped = False
                    break
            if stopped:
                print("All processes finished.")
                break
        
        time.sleep(0.01)

def runMulti(ops, num_processes=4):
    with mp.Manager() as manager:
        start = time.time()
        # final results
        plans_lock = manager.Lock()
        plans = manager.list()
        
        process_status_lock = manager.Lock()
        processes_status = manager.Array('i', range(num_processes))
        processes = []
        processes_queue = []
        for idx in range(num_processes):
            processes_queue.append(manager.Queue())
            processes.append(mp.Process(target=run, args=(
                idx,
                plans,
                plans_lock,
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
        processes_queue[0].put((ops, []))
        
        # init a manager process
        # once all processes are finished, the manager process will be finished
        manager_process = mp.Process(target=manager_run, args=(processes_status, process_status_lock))
        manager_process.start()
        
        manager_process.join()
        
        # kill all processes
        for p in processes:
            p.terminate()
            
        end = time.time()
        
        return list(plans), end-start

if __name__ == "__main__":
    # dfs operator stack
    ops = []
    ops.append(OP("source", 4))
    ops.append(OP("map", 8))
    ops.append(OP("filter", 8))
    ops.append(OP("sink", 2))
    
    singleplans, singletime = runSingle(ops)
    multiplans, multitime = runMulti(ops, 4)
        
    # ======== compare results ========
    print("Compare results: ", compareResult(singleplans, multiplans))
    if not compareResult(singleplans, multiplans):
        for i in range(len(singleplans)):
            print("i = ", i)
            print("Single: ", singleplans[i])
            print("Multi: ", multiplans[i])
    print("Single size: ", len(singleplans))
    print("Multi size:  ", len(multiplans))
    print("Single time: ", singletime)
    print("Multi time:  ", multitime)

    


