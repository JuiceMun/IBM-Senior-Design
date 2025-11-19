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

with open('../data/queueing-network/queue_linear_example.json', 'r') as file:
    queue_network = json.load(file)

def assign_service_rates(queue_network: dict):
    """
    Pick random values for service rate (μ). All of the μ_i should 
    follow the constraint in the queue network. 

    Args:         queue_network (dict): The incomplete default queue network application
        schema. 

    Returns:
        queue_network (dict): The queue network application will randomly 
        picked service rates. 
    """
    queues = queue_network["system"]["queues"]
    constraint = queue_network["system"]["constraint"]["service_rate_sum"]
    n = len(queues)

    np.random.seed(42)
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

def compute_queue_lambdas(main_lambda, queues, entry_id):
    """
    Compute the lambda for each of the queue based on their routing probability 
    and main lambda. 

    Args: 
        main_lambda (int): The main lambda entering the queue network.
        queues (list[dict]): A list of queues, where each queue has a `id`,
        `service_rate`, and `next_queue` field.
        entry_id (int): Where the main lambda will enter in the queue. 

    Returns:
        lambdas (dict): The queue id is the key, and the computed lambda for each queue 
        are the values. 
    """
    lambdas = {q["id"]: 0.0 for q in queues}
    lambdas[entry_id] = main_lambda
    
    for q in queues:
        q_id = q["id"]
        for nxt in q["next_queue"]:
            if nxt["id"] == "External": # Reached end of the queue 
                break 

            prob = nxt["probability"] / 100.0 # Convert to a probability where between 0 to 1
            routed = lambdas[q_id] * prob # We already assigned the first queue a lambda value (via entry point)
            lambdas[nxt["id"]] = lambdas.get(nxt["id"], 0) + routed
    return lambdas

def generate_data(queue_network: json, time, main_lambda, k, alpha, C):
    """
    Generate synthethic datas. 

    Args: 
        queue_network (dict): The queue network application.
        main_lambda (int): The starting main_lambda value. 
        k (float): How long is the dependency of λ is. 
        alpha (float): How much λ is dependent on the previous time point.
        C (float): Constant 

    Returns:
        timeline (dict): Synthetic data.  
    """
    system = queue_network["system"]
    queues = system["queues"]
    entry_id = system["entry_points"]

    # Initialize backlog and lambda tracking
    backlog = {q["id"]: 0.0 for q in queues}
    main_lambdas = []
    timeline = []

    for t in range(time):
        curr_time = t + 1
        print(f"\nTime: {curr_time}")

        # Compute main lambda
        if curr_time == 1: 
            curr_main_lambda = main_lambda
            main_lambdas.append(curr_main_lambda)
        else: 
            curr_main_lambda = compute_curr_lambda(main_lambdas, k, alpha, C)
            main_lambdas.append(curr_main_lambda)

        print("λ_main =", curr_main_lambda)

        # Compute queue lambdas (main λ + backlog)
        queue_lambdas = {}
        """
        # Old code for linear example...
        for q in queues:
            q_id = q["id"]
            queue_lambdas[q_id] = curr_main_lambda + backlog[q_id] # Setting each queue to main lambda plus any backlog
        """
        queue_lambdas = compute_queue_lambdas(curr_main_lambda, queues, entry_id)
        for q in queues:
            q_id = q["id"]
            queue_lambdas[q_id] += backlog[q_id]
        
        print("Queue λ values:", queue_lambdas)

        # Compute delays  
        delays = {}
        
        for q in queues: 
            q_id = q["id"]
            mu = q["service_rate"]
            lam = queue_lambdas[q_id]
            delays[q_id] = 1/(mu-lam) 

        # Compute served and update backlog
        served = {}
        new_backlog = {}

        for q in queues:
            q_id = q["id"]
            mu = q["service_rate"]
            lam = queue_lambdas[q_id]

            served[q_id] = min(mu, lam)
            new_backlog[q_id] = max(0, lam - mu)

        backlog = new_backlog

        print("Delays:", delays)
        print("Served:", served)
        print("Backlog:", backlog)

        # Record timestep summary
        timeline.append({
            "time": curr_time,
            "lambda_main": curr_main_lambda,
            "queue_lambdas": queue_lambdas,
            "served": served, # Evenually remove
            "backlog": backlog.copy(), # Evenually remove 
            "delays": delays
        })

    return timeline

# An example 
k = 3
alpha = 0.4
generate_data(queue_network, 10, 0.1, k, alpha, 0.05)