import copy
from dfsUtil import *

def OuterDFS(ops, curPlace, plans):
    
    #print("OuterDFS: ops = ", [op.name for op in ops], "curPlace = ", curPlace)
    
    if len(ops) == 0:
        plans.append(copy.deepcopy(curPlace))
        return

    currentOP = ops.pop()
    nodeList = []  # record temp placement for the current op
    
    InnerDFS(currentOP, ops, currentOP.parallelim, curPlace, nodeList, plans)

    ops.append(currentOP)

def InnerDFS(op, ops, leftTasks, curPlace, nodeList, plans):
    
    #print("InnerDFS: op = ", op.name, "leftTasks = ", leftTasks, "curPlace = ", curPlace, "nodeList = ", nodeList)
    
    # Terminating condition
    if leftTasks <= 0:
        # update curPlace
        curPlace.append(strNodeList(nodeList))

        # explore next op
        OuterDFS(ops, curPlace, plans)

        # backtrace curPlace
        curPlace.pop()
        return

    upperBound = min(3, leftTasks)
    for i in range(upperBound):
        
        taskPlaced = i+1
        # update nodeList
        nodeList.append(op.name + str(taskPlaced))

        InnerDFS(op, ops, leftTasks-taskPlaced, curPlace, nodeList, plans)

        # backtrace nodeList
        nodeList.pop()
