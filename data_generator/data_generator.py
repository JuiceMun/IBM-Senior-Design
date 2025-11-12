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

# No noise is added as of now. BUT SHOULD BE IMPLEMENTED (prehaps in another function?). 
# For ease of testing, there's no noise added. 
def compute_curr_lambda(main_lambdas, k, alpha, C) -> float:
    """
    Compute λ_main for the current timepoint based on previous timepoints. 
    Let t be the timepoint. So t+1 is the current time point, and the lambda 
    is computed as follow: 

    λ_{t+1} = αλ_t + α²λ_{t-1} + ... + αᵏλ_{t+1−k} + C
    
    Args: 
        main_lambdas (list[int]): List keeping track of all the main_lambda values from 
        all the time point. 
        k (float): How long is the dependency of λ is. 
        alpha (float): How much λ is dependent on the previous time point.
        C (float): Constant 

    Returns:
        main_lambda (float): The lambda value of the current time point. 
    """
    main_lambda = 0.0
    n = len(main_lambdas)
    
    # Loop over the last k previous lambdas
    for i in range(1, k+1):
        if n - i < 0:
            break  # Not enough history yet, so loop over existing ones
        main_lambda += (alpha ** i) * main_lambdas[-i]

    main_lambda += C
    return main_lambda

# These 2 should equal to each other 
print(compute_curr_lambda([0.2,0.3,0.4], 2, 0.5, 0.1))
print((0.5*0.4)+((0.5**2)*0.3)+0.1) # k = 2, alpha = 0.5, C = 0.1

# These 2 should equal to each other 
print(compute_curr_lambda([0.3], 2, 0.5, 0.1)) # When there is not enough history 
print(0.5*0.3+0.1) # k = 2, alpha = 0.5, C = 0.1