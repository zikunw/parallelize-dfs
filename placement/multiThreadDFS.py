import copy
from dfsUtil import *
from dfs import ProcessStatus

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