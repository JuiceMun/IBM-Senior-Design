import json
import csv
import numpy as np

"""
Note: 
- Later implement a config file that'll set the values of k and alpha
- An idea to is to output the synthetic data into a csv file
"""

"""
Procedure: 
1) Obtain a queue network graph.
2) Generate random values for the service rate, but still satisfy 
constraint.
3) Vary main arrival rate (λ_main). This arrival rate should be 
between 0 and 1 for any time period.
4) Compute λ_i for each of the queue. Then compute delay for each 
of the queue. 
5) Add noise to the appropriate values. 
"""

with open('queue_linear_example.json', 'r') as file:
    queue_network = json.load(file)

def assign_service_rates(queue_network: dict):
    """
    Pick random values for service rate (μ). All of the μ_i should 
    follow the constraint in the queue network. 

    Args: 
        queue_network (dict): The incomplete default queue network application 
        schema. 

    Returns:
        queue_network (dict): The queue network application will randomly 
        picked service rates. 
    """
    queues = queue_network["system"]["queues"]
    constraint = queue_network["system"]["constraint"]["service_rate_sum"]
    n = len(queues)
    
    x = np.random.rand(n)
    nums = (x / x.sum()) * constraint  # Normalize to the value of the constraint
    
    for i, q in enumerate(queues):
        q["service_rate"] = float(nums[i])
    
    print("Assigned service rates:", nums)
    print("Sum:", nums.sum()) # Checking to see if it adds up
    return queue_network

print(assign_service_rates(queue_network))
