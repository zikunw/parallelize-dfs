import copy
from dfsUtil import *
from dfs import ProcessStatus

def MultiOuterDFS(ops, curPlace, plans, plans_lock, processes_status, process_status_lock, processes_queue):
    
    #print("OuterDFS: ops = ", [op.name for op in ops], "curPlace = ", curPlace)
    
    if len(ops) == 0:
        with plans_lock:
            plans.append(copy.deepcopy(curPlace))
        return

    currentOP = ops[-1] #ops.pop()
    nodeList = []  # record temp placement for the current op
    MultiInnerDFS(currentOP, ops[:-1], currentOP.parallelim, curPlace, nodeList, plans, plans_lock, processes_status, process_status_lock, processes_queue)

def MultiInnerDFS(op, ops, leftTasks, curPlace, nodeList, plans, plans_lock, processes_status, process_status_lock, processes_queue):
    
    #print("InnerDFS: op = ", op.name, "leftTasks = ", leftTasks, "curPlace = ", curPlace, "nodeList = ", nodeList)
    
    # Terminating condition
    if leftTasks <= 0:
        
        # if there are idle processes, send the task to the idle process
        with process_status_lock:
            idle_process_idx = -1
            for j in range(len(processes_status)):
                if processes_status[j] == ProcessStatus.WAITING.value:
                    idle_process_idx = j
                    break
            if idle_process_idx != -1:
                processes_queue[idle_process_idx].put((ops, curPlace + [strNodeList(nodeList)]))
                processes_status[idle_process_idx] = ProcessStatus.HAS_TASK.value
                return
        
        # explore next op
        MultiOuterDFS(ops, curPlace + [strNodeList(nodeList)], plans, plans_lock, processes_status, process_status_lock, processes_queue)
        return

    upperBound = min(3, leftTasks)
    
    for i in range(upperBound):
        taskPlaced = i+1
        MultiInnerDFS(op, ops, leftTasks-taskPlaced, curPlace, nodeList + [op.name + str(taskPlaced)], plans, plans_lock,  processes_status, process_status_lock, processes_queue)