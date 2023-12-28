from dfsUtil import *
from singleThreadDFS import *

if __name__ == "__main__":
    
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

    


