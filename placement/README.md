## Placement

I went through several iterations and optimization process for this method.

### Iteration 1: rewrite function to adjust to parallelism.

Changed all the recursion from popping and appending to a global array to copy the entire array to the recursive call. This is because for each parallelized task we want them to only depended on the function call parameters, so that we can divide and delegate tasks more easily. 

For example in the outDFS:
```python
currentOP = ops.pop()
nodeList = [] # record temp placement for the current op
InnerDFS(currentOP, ops, currentOP.parallelim, curPlace, nodeList, plans)
ops.append(currentOP)
```

To this:
```python
currentOP = ops[-1] #ops.pop()
nodeList = [] # record temp placement for the current op
MultiInnerDFS(currentOP, ops[:-1], currentOP.parallelim, curPlace, nodeList, plans)
```

In the future we can change the parameter so that it only passes index of the corresponding array, and all processes can read from a shared global array (that will not be changed). This should be able to increase the throughput in the future.

### Iteration 2: Naive parallel approach

I implemented an naive parallel for the double recursion, without any optimization. Basically the process is trying to delegate the `OuterDFS` function every time when we need to call it (in the end of `innerDFS` function).

```python
# inside inner dfs
# Terminating condition
if leftTasks <= 0:
	# if there are idle processes, send the task to the idle process
	with process_status_lock:
		idle_process_idx = -1
			for j in range(len(processes_status)):
				if processes_status[j] == ProcessStatus.WAITING.value:
				idle_process_idx = j
				break

	if idle_process_idx != -1:
		processes_queue[idle_process_idx].put((ops, curPlace + [strNodeList(nodeList)]))
		processes_status[idle_process_idx] = ProcessStatus.HAS_TASK.value
		return

	# if there are no avaliable threads, explore next op
	MultiOuterDFS(ops, curPlace + [strNodeList(nodeList)], plans, plans_lock, processes_status, process_status_lock, processes_queue)
	return
```

There are other ways that we can do this, we can also parallelize so that we also delegate the `innerDFS` function. This is something we could try in the future.

This is the raw performance when there are 4 sources, 16 map nodes and 2 sinks (4 worker processes):
```
Single time:  0.49239015579223633
Multi time:   39.99130702018738
```

### Iteration 3: Cut-off

In the `InnerDFS`, before I delegate the task to another process, I perform a check on the depth of the tree, we only try to delegate the task it is close enough to the root (big enough size):

```python
if len(ops) >= 1:
	...
```

When cut-off is greater or equal than 1:
```
Single time:  0.491426944732666
Multi time:   17.015933990478516
```

When cut-off is greater or equal than 2:
```
Single time:  0.49138402938842773
Multi time:   9.113759994506836
```

I did not test 3 cutoff because in our test case it is essentially only letting one worker run all the time. This clearly works better in a setting where there exists more types of operators:
```
setting:
4 worker processes
ops.append(OP("source", 4))
ops.append(OP("map", 8))
ops.append(OP("filter", 8))
ops.append(OP("sink", 2))

result:
Single time:  0.3259420394897461
Multi time:   6.939192056655884
```

### Iteration 4: Sending index instead of entire `ops` list

Modified so that all nodes has the entire `ops` list first, the task message now only contains the index of the current task:
```python
processes_queue[0].put((0, [])) # (ops_index, curPlace)
```

Results in slightly faster runtime:
```
Single size:  91854
Multi size:   91854
Single time:  0.3253748416900635
Multi time:   6.460827827453613
```

### Iteration 5: Pushing result plan into a queue instead of locking primitive:

Instead of using locks, the processes now push result onto a queue:
```python
if len(ops) == ops_index:
	plans_queue.put(copy.deepcopy(curPlace))
return
```

Result:
```
Single size:  91854
Multi size:   91854
Single time:  0.3284647464752197
Multi time:   5.873038053512573
```

This increase the overall speed, however, I also realized collecting plans from the queue now takes up more. than 50% of the total runtime. I should start working on spawning up another process to collect the data while other workers are running.

```
All processes finished.
All plans collected. 3.7002718448638916
```

### Iteration 6: Using a separate process to collect the queue result while the workers are running:

The original parent process will start collecting from queue as soon as the system started:
``` python
plans = []
while True: #not plans_queue.empty():
	plan = plans_queue.get()
	if plan == "STOP":
		break
	plans.append(plan)
print("All plans collected.")
```

The stop condition is passed in by the modified manager process:
```python
def manager_run(processes_status, process_status_lock, plans_queue):
	while True:
		with process_status_lock:
			stopped = True
			for i in range(len(processes_status)):
				if processes_status[i] != ProcessStatus.WAITING.value:
					stopped = False
					break
			if stopped:
				plans_queue.put("STOP")
				print("All processes finished.")
				return
	time.sleep(0.01)
```

Result in several seconds faster:
```
Single size:  91854
Multi size:   91854
Single time:  0.33064699172973633
Multi time:   4.16757607460022
```