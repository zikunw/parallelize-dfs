from dfsUtil import *
from singleThreadDFS import *
from multiThreadDFS import *
from stackSingleThreadDFS import *

import multiprocessing as mp
from enum import Enum
import time
import os

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

if __name__ == "__main__":
    # dfs operator stack
    ops = []
    ops.append(OP("source", 4))
    ops.append(OP("map", 10))
    ops.append(OP("filter", 8))
    ops.append(OP("sink", 4))
    
    # ops.append(OP("source", 2))
    # ops.append(OP("map", 4))
    # ops.append(OP("sink", 2))
    
    # ops.append(OP("source", 12))
    # ops.append(OP("map", 8))
    # ops.append(OP("sink", 6))
    # ops.append(OP("good", 4))
    
    # multiplans, multitime = runMulti(ops, 4)
    singleplans, singletime = runSingle(ops)
    
    # for plan in singleplans:
    #     print(" ".join(plan))
    
    # stackSinglePlans, stackSingleTime = stackDFS(ops)
        
    # ======== compare results ========
    # print("Compare results: ", compareResult(singleplans, multiplans))
    # # if not compareResult(singleplans, multiplans):
    # #     for i in range(len(singleplans)):
    # #         print("i = ", i)
    # #         print("Single: ", singleplans[i])
    # #         print("Multi: ", multiplans[i])
    print("Single size: ", len(singleplans))
    # print("Multi size:  ", len(multiplans))
    # print("StackSingle size: ", len(stackSinglePlans))
    print("Single time: ", singletime)
    # print("Multi time:  ", multitime)
    # print("StackSingle time: ", stackSingleTime)

    


