import multiprocessing
import threading
import time
import random

class OP:
    def __init__(self, name, parallelim):
        self.name = name
        self.parallelim = parallelim

def strNodeList(nodeList):
    return ''.join(entry for entry in nodeList)

def planToString(plan):
    return '-'.join(i for i in plan)

class TimeManager:
    def __init__(self, lowBound, highBound):
        self.lowBound = lowBound
        self.highBound = highBound
        self.nextTime = time.time()
    
    def updateNextTime(self):
        processDuration = random.uniform(self.lowBound, self.highBound)
        self.nextTime = time.time() + processDuration

    def timeOut(self):
        return time.time() >= self.nextTime

# Structure maintained in all processes
class SharedPool:
    def __init__(self, totalProcess):
        self.queue = multiprocessing.SimpleQueue()
        self.lock = multiprocessing.Lock()
        self.avaiProcess = multiprocessing.Value("i", totalProcess)

    def scheduleProcess(self, args):
        self.queue.put(args)

    def terminate(self):
        self.queue.put(None)

    def acquireProcess(self):
        with self.lock:
            if self.avaiProcess.value > 0:
                self.avaiProcess.value -= 1
                return True
            else:
                return False

# Structure maintained in the main process
class ProcessPool:
    def __init__(self, sharedPool, processInitFunc, processFunc, plans):
        self.totalProcess = sharedPool.avaiProcess.value
        self.sharedPool = sharedPool
        self.pool = multiprocessing.Pool(processes=self.totalProcess, initializer=processInitFunc, initargs=(self.sharedPool,))
        self.processFunc = processFunc
        # application specific data
        self.plans = plans

    def start(self):
        while True:
            processArgs = self.sharedPool.queue.get()
            if processArgs is None:
                break
            # start process
            self.pool.apply_async(self.processFunc, args=processArgs, callback=self.endProcess)

        print("[Multi] DFS finish")
        self.pool.close()
        self.pool.join()

    def endProcess(self, result):
        # append the results from child processes to main process
        self.plans.extend(result)
        # add the terminated process back to the process pool
        with self.sharedPool.lock:
            self.sharedPool.avaiProcess.value += 1
            if self.sharedPool.avaiProcess.value == self.totalProcess:
                self.sharedPool.terminate()