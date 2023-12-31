import copy
from dfsUtil import *


def OuterDFS(ops, curPlace, plans):
    if len(ops) == 0:
        plans.append(copy.deepcopy(curPlace))
        return

    currentOP = ops.pop()
    nodeList = []  # record placement for the current op
    
    InnerDFS(currentOP, ops, currentOP.parallelim, curPlace, nodeList, plans)

    ops.append(currentOP)

def InnerDFS(op, ops, leftTasks, curPlace, nodeList, plans):
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
