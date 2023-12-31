import copy
from dfsUtil import *
from enum import Enum
import time

class searchType(Enum):
    Outer = 0
    Inner = 1
    
class ProcessStatus(Enum):
    UNINIT = 0
    RUNNING = 1
    WAITING = 2
    HAS_TASK = 3
    
worker_result_path = lambda idx: f"temp/worker_{idx}_result.txt"
    
def run(idx, ops, processes_status, process_status_lock, processes_queue):
    message_queue = processes_queue[idx]
    print(f"Process {idx} started.")
    
    # finish and waiting for input
    with process_status_lock:
        processes_status[idx] = ProcessStatus.WAITING.value
    worker_result_file = open(worker_result_path(idx), "w")
        
    plans = []
    searchSpace = []
    
    # initial search if idx == 0
    if idx == 0:
        searchSpace.append((searchType.Outer, (0, [])))
        
    while True:
        # if there is nothing to search,
        # enter idle mode
        if searchSpace == []:
            # issue a request to other processes
            with process_status_lock:
                processes_status[idx] = ProcessStatus.WAITING.value
            message_queue.put("request")
           
    
        while searchSpace != []:
            type, nextSearch = searchSpace.pop()
            newSearches, newPlans = processSearch(type, nextSearch)
            searchSpace += newSearches
            plans += newPlans
    
    return

def processSearch(type, nextSearch):
    newSearches = []
    plans = []
    if type == searchType.Outer:
        ops_index, curPlace = nextSearch
        if len(ops) == ops_index:
            plans.append(curPlace)
            return newSearches, plans
        currentOP = ops[-ops_index]
        nodeList = []  # record temp placement for the current op
        newSearches.append((searchType.Inner, (currentOP, ops, ops_index+1, currentOP.parallelim, curPlace, nodeList)))
    elif type == searchType.Inner:
        op, ops, ops_index, leftTasks, curPlace, nodeList = nextSearch
        if leftTasks <= 0:
            newSearches.append((searchType.Outer, (ops_index, [strNodeList(nodeList)] + curPlace)))
            return newSearches, plans
        upperBound = min(3, leftTasks)
        for i in range(upperBound):
            taskPlaced = i+1
            newSearches.append((searchType.Inner, (op, ops, ops_index, leftTasks-taskPlaced, curPlace, nodeList + [op.name + str(taskPlaced)])))
    else:
        raise Exception("Unknown search type: " + str(type))
    
    return newSearches, plans

if __name__ == "__main__":
    pass