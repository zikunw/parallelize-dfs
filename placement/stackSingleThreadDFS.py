import copy
from dfsUtil import *
from enum import Enum
import time

class searchType(Enum):
    Outer = 0
    Inner = 1

def stackDFS(ops):
    
    start = time.time()
    
    plans = []
    searchSpace = []
    searchSpace.append((searchType.Outer, (0, []))) # (, (ops_index, curPlace)) 
    
    while searchSpace != []:
        type, nextSearch = searchSpace.pop()
        if type == searchType.Outer:
            ops_index, curPlace = nextSearch
            if len(ops) == ops_index:
                plans.append(curPlace)
                continue
            currentOP = ops[-ops_index]
            nodeList = []  # record temp placement for the current op
            searchSpace.append((searchType.Inner, (currentOP, ops, ops_index+1, currentOP.parallelim, curPlace, nodeList)))
        elif type == searchType.Inner:
            op, ops, ops_index, leftTasks, curPlace, nodeList = nextSearch
            if leftTasks <= 0:
                searchSpace.append((searchType.Outer, (ops_index, [strNodeList(nodeList)] + curPlace)))
                continue
            upperBound = min(3, leftTasks)
            for i in range(upperBound):
                taskPlaced = i+1
                searchSpace.append((searchType.Inner, (op, ops, ops_index, leftTasks-taskPlaced, curPlace, nodeList + [op.name + str(taskPlaced)])))
        else:
            raise Exception("Unknown search type: " + str(type))
    
    return plans, time.time()-start