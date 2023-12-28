from knapsack import Knapsack, KnapConfig, KnapItem

def DFS(idx=0, sum_val = 0, sum_weight = 0, limit_weight=0, arr = [], items=[]):
    if idx == len(items):
        return sum_val, arr
    max_val = 0
    max_arr = []
    for i in range(idx, len(items)):
        if sum_weight + items[i].weight <= limit_weight:
            n_val, n_arr = DFS(
                    idx=i+1,
                    sum_val=sum_val + items[i].value, 
                    sum_weight=sum_weight + items[i].weight, 
                    limit_weight=limit_weight, 
                    arr=arr+[items[i].id], 
                    items=items
                )
            if n_val > max_val:
                max_val = n_val
                max_arr = n_arr
    return max_val, max_arr

def main():
    # Problem formulation
    config = KnapConfig(
        num=60,
        weightUpper=10,
        weightLower=1,
        valueUpper=5,
        valueLower=1,
        weightLimit=20
    )
    knapsack = Knapsack(config=config)
    knapsack.generate()
    print(knapsack.get_items())
    
    # DFS
    val, arr = DFS(
        idx=0,
        sum_val=0,
        sum_weight=0,
        limit_weight=config.weightLimit,
        arr=[],
        items=knapsack.get_items()
    )
    weight = sum([items.weight for items in knapsack.get_items() if items.id in arr])
    print(f"value: {val}, weight: {weight}, arr: {arr}")
    
    
    

if __name__ == '__main__':
    main()