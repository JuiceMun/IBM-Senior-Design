import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from program_files import config

# --------------------------------------------------
# Step 2: Define delay model with μ sum constraint
# --------------------------------------------------

def combined_delay(lmbda_and_idx, *mu_params):
    lmbda, q_idx = lmbda_and_idx

    # Last μ enforces sum = 1
    mu_vals = list(mu_params) + [1 - sum(mu_params)]
    mu_vals = np.array(mu_vals)

    W_pred = np.zeros_like(lmbda, dtype=float)

    for i in range(len(lmbda)):
        q = int(q_idx[i])

        if mu_vals[q] <= lmbda[i]:
            W_pred[i] = 1e6  # overload protection
        else:
            W_pred[i] = 1.0 / (mu_vals[q] - lmbda[i])

    return W_pred


def run(csv_file_name:str):
    # --------------------------------------------------
    # Step 1: Load CSV Data
    # --------------------------------------------------
    cfg = config.get_config("dev_config.ini")
    data_path = cfg.get("paths","processed_data_dir")+"\\"+csv_file_name
    df = pd.read_csv(data_path)

    # Extract lambda values per queue
    lambda_q1 = df["queue_lambdas.Q1"].values
    lambda_q2 = df["queue_lambdas.Q2"].values
    lambda_q3 = df["queue_lambdas.Q3"].values

    # Extract delays
    W_q1 = df["delays.Q1"].values
    W_q2 = df["delays.Q2"].values
    W_q3 = df["delays.Q3"].values

    # Number of queues
    N = 3

    # Combine all queues' data into one dataset
    lambda_all = np.concatenate([lambda_q1, lambda_q2, lambda_q3])
    W_all = np.concatenate([W_q1, W_q2, W_q3])
    queue_idx = np.concatenate([
        np.zeros(len(df), dtype=int),
        np.ones(len(df), dtype=int),
        2 * np.ones(len(df), dtype=int)
    ])

    # --------------------------------------------------
    # Step 3: Fit μ values
    # --------------------------------------------------

    p0 = [1.0 / N] * (N - 1)
    popt, _ = curve_fit(
        combined_delay,
        (lambda_all, queue_idx),
        W_all,
        p0=p0,
        maxfev=20000
    )

    mu_est = np.append(popt, 1 - sum(popt))

    print("Estimated μ values for each queue:")
    for i, m in enumerate(mu_est, start=1):
        print(f"μ{i} = {m:.4f}")
    print("Sum of all μ =", round(mu_est.sum(), 4))

    # --------------------------------------------------
    # Step 4: Plot actual vs fitted curves
    # --------------------------------------------------

    plt.figure(figsize=(8, 5))
    colors = ['r', 'g', 'b']

    for q in range(N):
        mask = queue_idx == q
        plt.scatter(
            lambda_all[mask],
            W_all[mask],
            color=colors[q],
            label=f"Queue {q+1} Data"
        )

        l_space = np.linspace(0, max(lambda_all[mask]) * 1.1, 200)
        W_fit = 1.0 / (mu_est[q] - l_space)

        plt.plot(
            l_space,
            W_fit,
            color=colors[q],
            linestyle="--",
            label=f"Queue {q+1} Fit"
        )

    plt.xlabel("λ (Arrival Rate)")
    plt.ylabel("W (Delay)")
    plt.title("Curve Fit for μ Estimation (Sum Constraint: Σμ=1)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # --------------------------------------------------
    # Step 5: Use REAL λ_main Proportions for Bottleneck Detection
    # --------------------------------------------------

    lambda_main = df["lambda_main"].values

    # Fractions derived from CSV
    frac_q1 = lambda_q1 / lambda_main
    frac_q2 = lambda_q2 / lambda_main
    frac_q3 = lambda_q3 / lambda_main

    fractions = np.array([
        frac_q1.mean(),
        frac_q2.mean(),
        frac_q3.mean(),
    ])

    print("\nUsing average queue proportions:", fractions)

    lambda_main_values = np.linspace(0.01, 2.0, 1000)
    overload_points = []

    for q in range(N):
        lambda_j = fractions[q] * lambda_main_values
        idx = np.argmax(lambda_j >= mu_est[q])

        if idx == 0 and lambda_j[0] < mu_est[q]:
            overload_lambda = np.nan
        else:
            overload_lambda = lambda_main_values[idx]

        overload_points.append(overload_lambda)

    system_max_lambda = np.nanmin(overload_points)
    bottleneck_queue = np.nanargmin(overload_points) + 1

    # --------------------------------------------------
    # Final Output
    # --------------------------------------------------

    print("\nSystem Analysis:")
    print("----------------")
    for i in range(N):
        print(f"Queue {i+1}: Overload at λ_main ≈ {overload_points[i]:.4f}")

    print(f"\nBottleneck Queue: Q{bottleneck_queue}")
    print(f"Maximum λ_main the system can support: {system_max_lambda:.4f}")

