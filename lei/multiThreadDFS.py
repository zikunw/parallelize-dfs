import copy
from dfsUtil import *


def OuterDFS(ops, curPlace, plans, timeManager):    
    if len(ops) == 0:
        plans.append(copy.deepcopy(curPlace))
        return
    
    currentOP = ops.pop()
    nodeList = []  # record placement for the current op    
    
    InnerDFS(currentOP, ops, currentOP.parallelim, curPlace, nodeList, plans, timeManager)
    
    ops.append(currentOP)

def InnerDFS(op, ops, leftTasks, curPlace, nodeList, plans, timeManager):
    # declare the shared variable
    global sharedPool

    if leftTasks <= 0:
        # update curPlace
        curPlace.append(strNodeList(nodeList))

        # explore next op
        OuterDFS(ops, curPlace, plans, timeManager)

        # backtrace curPlace
        curPlace.pop()
        return plans

    upperBound = min(3, leftTasks)
    for i in range(upperBound):
        taskPlaced = i+1
        # update nodeList
        nodeList.append(op.name + str(taskPlaced))

        if timeManager.timeOut():
            # try to allocate a new process to split the work
            if sharedPool.acquireProcess():
                newTimeManager = copy.deepcopy(timeManager)
                newTimeManager.updateNextTime()
                args = (op, ops, leftTasks-taskPlaced, curPlace, nodeList, [], newTimeManager)
                sharedPool.scheduleProcess(args)
            # all processes are running -> local execution
            else:
                timeManager.updateNextTime()
                InnerDFS(op, ops, leftTasks-taskPlaced, curPlace, nodeList, plans, timeManager)
        else:
            InnerDFS(op, ops, leftTasks-taskPlaced, curPlace, nodeList, plans, timeManager)

        # backtrace nodeList
        nodeList.pop()

    # used by inter-process communication
    return plans


# Initialization function for each process
def processInit(_sharedPool):
    global sharedPool
    sharedPool = _sharedPool