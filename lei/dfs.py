from dfsUtil import *
import singleThreadDFS as singleDFS
import multiThreadDFS as multiDFS

if __name__ == "__main__":
    
    ########################## Multi DFS ##########################

    ops = []
    ops.append(OP("source", 12))
    ops.append(OP("map", 8))
    ops.append(OP("sink", 6))
    ops.append(OP("good", 4))

    plans = []
    curPlace = []

    # Initialize process pool
    numProcess = 20
    sharedPool = SharedPool(numProcess)
    pool = ProcessPool(sharedPool, multiDFS.processInit, multiDFS.InnerDFS, plans)
    
    # Each process has a dedicated period of runtime before trying to start new process
    # This time is randomized between range [lower, higher]
    lower = 0.1
    higher = 0.15
    timeManager = TimeManager(lower, higher)

    # Start DFS
    print("[Multi] DFS start...")
    start = time.time()
    # Explore the 1st OP
    currentOP = ops.pop()
    nodeList = []
    if sharedPool.acquireProcess():
        args = (currentOP, ops, currentOP.parallelim, curPlace, nodeList, [], timeManager)
        sharedPool.scheduleProcess(args)
    # Start the main process loop
    pool.start()
    end = time.time()

    # Multi DFS runtime
    multiRuntime = end-start
    print("Multi runtime:", multiRuntime)

    # Structure to validate the results
    multiSet = set()
    for i in range(len(pool.plans)):
        key = planToString(pool.plans[i])
        multiSet.add(key)


    ########################## Single DFS ##########################

    ops = []
    ops.append(OP("source", 12))
    ops.append(OP("map", 8))
    ops.append(OP("sink", 6))
    ops.append(OP("good", 4))

    plans = []
    curPlace = []

    # Start DFS
    print("[Single] DFS start...")
    start = time.time()
    singleDFS.OuterDFS(ops, curPlace, plans)
    print("[Single] DFS finish")
    end = time.time()

    # Single DFS runtime
    singleRuntime = end-start
    print("Single runtime:", singleRuntime)

    # Structure to validate the results
    singleSet = set()
    for i in range(len(plans)):
        key = planToString(plans[i])
        singleSet.add(key)


    ####################### Validate results ########################

    print("[Validation] Validate results...")
    print("Single/Multi has the same results:", multiSet == singleSet)