from __future__ import annotations
import random
import math
from typing import Any

# This is the class for the knapsack problem
class Knapsack():
    def __init__(self, config: KnapConfig):
        self.conf = config
        self.items = []
    
    def generate(self):
        for i in range(self.conf.num):
            self.items.append(KnapItem(i, self.conf))
            
    def get_items(self):
        return self.items
            
    def __str__(self):
        return f"Knapsack({self.conf})"
    
    
class KnapConfig():
    def __init__(self, 
                 num: int = 30, 
                 weightUpper: int = 20, 
                 weightLower: int = 1, 
                 valueUpper: int = 20,
                 valueLower: int = 1,
                 weightLimit: float = 10):
        self.num = num
        self.weightUpper = weightUpper
        self.weightLower = weightLower
        self.valueUpper = valueUpper
        self.valueLower = valueLower
        self.weightLimit = weightLimit
        
class KnapItem():
    def __init__(self, id: int, config: KnapConfig):
        self.weight = random.randint(config.weightLower, config.weightUpper)
        self.value = random.randint(config.valueLower, config.valueUpper)
        self.id = id
        
    def __str__(self):
        return f"(id:{self.id}, w:{self.weight}, v:{self.value})"
    
    def __repr__(self):
        return self.__str__()
    
def main():
    config = KnapConfig()
    knapsack = Knapsack(config=config)
    knapsack.generate()
    print(knapsack.get_items())

if __name__ == '__main__':
    main()