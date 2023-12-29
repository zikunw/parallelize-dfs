from dfsUtil import *
from singleThreadDFS import *
from multiThreadDFS import *

def compareResult(result1, result2):
    if len(result1) != len(result2):
        return False
    
    for i in range(len(result1)):
        if result1[i] != result2[i]:
            return False
    
    return True

if __name__ == "__main__":
    # ======== single thread dfs ======== 
    print("Single thread dfs:")
    # dfs operator stack
    ops = []
    ops.append(OP("source", 2))
    ops.append(OP("map", 4))
    ops.append(OP("sink", 2))

    # final results
    plans = []
    # current placement plan
    curPlace = []

    OuterDFS(ops, curPlace, plans)

    # dfs results
    for i in range(len(plans)):
        print(i+1, plans[i])
        
    # ======== multi thread dfs ========
    print("\nMulti thread dfs:")
    # dfs operator stack
    ops = []
    ops.append(OP("source", 2))
    ops.append(OP("map", 4))
    ops.append(OP("sink", 2))
    
    # final results
    multiplans = []
    # current placement plan
    curPlace = []
    
    MultiOuterDFS(ops, curPlace, multiplans)
    
    # dfs results
    for i in range(len(multiplans)):
        print(i+1, multiplans[i])
        
    # ======== compare results ========
    print("Compare results: ", compareResult(plans, multiplans))

    


