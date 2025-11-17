import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --------------------------------------------------
# Step 1: Example synthetic data (λ and delay W)
# --------------------------------------------------

lambda_q1 = np.array([0.15, 0.20, 0.25, 0.30])
W_q1      = np.array([2.5, 3.2, 4.1, 5.0])

lambda_q2 = np.array([0.10, 0.15, 0.20, 0.25])
W_q2      = np.array([4.0, 5.2, 6.8, 8.0])

lambda_q3 = np.array([0.05, 0.10, 0.15, 0.20])
W_q3      = np.array([7.0, 9.0, 12.0, 15.0])

# Combine all queues' data into one dataset
lambda_all = np.concatenate([lambda_q1, lambda_q2, lambda_q3])
W_all = np.concatenate([W_q1, W_q2, W_q3])
queue_idx = np.concatenate([
    np.zeros(len(lambda_q1), dtype=int),
    np.ones(len(lambda_q2), dtype=int),
    2 * np.ones(len(lambda_q3), dtype=int)
])

N = 3  # Number of queues

# --------------------------------------------------
# Step 2: Define the M/M/1 delay model with sum constraint
# --------------------------------------------------
def combined_delay(lmbda_and_idx, *mu_params):
    """
    lmbda_and_idx: tuple (lambda array, queue_idx array)
    mu_params: first N-1 mu values are free parameters
    last mu is computed as 1 - sum(others)
    """
    lmbda, q_idx = lmbda_and_idx
    mu_vals = list(mu_params) + [1 - sum(mu_params)]  # sum constraint
    mu_vals = np.array(mu_vals)

    W_pred = np.zeros_like(lmbda, dtype=float)
    for i in range(len(lmbda)):
        q = int(q_idx[i])
        if mu_vals[q] <= lmbda[i]:
            W_pred[i] = 1e6  # overloaded (huge delay)
        else:
            W_pred[i] = 1.0 / (mu_vals[q] - lmbda[i])
    return W_pred

# --------------------------------------------------
# Step 3: Fit the model using curve_fit
# --------------------------------------------------
p0 = [1.0 / N] * (N - 1)  # initial guess
popt, _ = curve_fit(combined_delay, (lambda_all, queue_idx), W_all, p0=p0, maxfev=20000)

# Compute all μ values (last one is constrained)
mu_est = np.append(popt, 1 - sum(popt))

print("Estimated μ values for each queue:")
for i, m in enumerate(mu_est, start=1):
    print(f"μ{i} = {m:.4f}")
print("Sum of all μ =", round(mu_est.sum(), 4))

# --------------------------------------------------
# Step 4: Visualize the fitted curves
# --------------------------------------------------
plt.figure(figsize=(8,5))
colors = ['r','g','b']
for q in range(N):
    mask = queue_idx == q
    plt.scatter(lambda_all[mask], W_all[mask], color=colors[q], label=f"Queue {q+1} Data")
    l_space = np.linspace(0, max(lambda_all[mask])*1.1, 100)
    W_fit = 1.0 / (mu_est[q] - l_space)
    plt.plot(l_space, W_fit, color=colors[q], linestyle="--", label=f"Queue {q+1} Fit")

plt.xlabel("λ (Arrival Rate)")
plt.ylabel("W (Delay)")
plt.title("Curve Fit for μ Estimation (Sum Constraint: Σμ=1)")
plt.legend()
plt.grid(True)
plt.show()

# --------------------------------------------------
# Step 5: Increase λmain gradually to find bottleneck
# --------------------------------------------------
# Let's assume each queue gets a fraction of λmain
fractions = np.array([1.0, 0.6, 0.4])  # Example proportions

# As λmain increases, λ_i = fraction_i * λmain
lambda_main_values = np.linspace(0.01, 1.0, 200)
overload_points = []

for q in range(N):
    lambda_j = fractions[q] * lambda_main_values
    # find where λ_j = μ_j (first overload)
    idx = np.argmax(lambda_j >= mu_est[q])
    if idx == 0:
        overload_lambda = np.nan
    else:
        overload_lambda = lambda_main_values[idx]
    overload_points.append(overload_lambda)

system_max_lambda = np.nanmin(overload_points)
bottleneck_queue = np.nanargmin(overload_points) + 1

print("\nSystem Analysis:")
print("----------------")
for i in range(N):
    print(f"Queue {i+1}: Overload at λ_main ≈ {overload_points[i]:.3f}")
print(f"\nBottleneck Queue: Q{bottleneck_queue}")
print(f"Maximum λ_main the system can support: {system_max_lambda:.3f}")
