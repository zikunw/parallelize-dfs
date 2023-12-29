import copy
from dfsUtil import *

def MultiOuterDFS(ops, curPlace, plans):
    
    #print("OuterDFS: ops = ", [op.name for op in ops], "curPlace = ", curPlace)
    
    if len(ops) == 0:
        plans.append(copy.deepcopy(curPlace))
        return

    currentOP = ops[-1] #ops.pop()
    nodeList = []  # record temp placement for the current op
    MultiInnerDFS(currentOP, ops[:-1], currentOP.parallelim, curPlace, nodeList, plans)

def MultiInnerDFS(op, ops, leftTasks, curPlace, nodeList, plans):
    
    #print("InnerDFS: op = ", op.name, "leftTasks = ", leftTasks, "curPlace = ", curPlace, "nodeList = ", nodeList)
    
    # Terminating condition
    if leftTasks <= 0:
        # explore next op
        MultiOuterDFS(ops, curPlace + [strNodeList(nodeList)], plans)
        return

    upperBound = min(3, leftTasks)
    for i in range(upperBound):
        taskPlaced = i+1
        MultiInnerDFS(op, ops, leftTasks-taskPlaced, curPlace, nodeList + [op.name + str(taskPlaced)], plans)