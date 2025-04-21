'''
Plotting script for LS1 trac.
This script generates two plots:
1. Qualified Runtime Distributions (QRTD) - CDF of time to reach each quality threshold.
2. Solution Quality Distributions (SQD) - CDF of relative error at specific time points.
'''
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "/Users/arjuna/School/6140/project/6140-project/code/data"  # directory with *.in and *.out
OUTPUT_DIR = "/Users/arjuna/School/6140/project/6140-project/code/output"  # directory with *.trace files
INSTANCES = ["large1", "large10"]
TIME_LIMIT = 600
SEEDS = list(range(1,11))
Q_STARS = [0.8, 1, 1.2, 1.4, 1.6]  # relative quality thresholds
TIME_POINTS = [0.1, 0.3, 1.0, 3.3, 10.0]  # times for SQD
markers = ['o', 's', '^', 'D', 'x']

# load optimal vals
opt = {}
for inst in INSTANCES:
    with open(os.path.join(DATA_DIR, f"{inst}.out")) as f:
        opt[inst] = int(f.readline().strip())
# load traces
traces = {inst: [] for inst in INSTANCES}
for inst in INSTANCES:
    for seed in SEEDS:
        pattern = os.path.join(
            OUTPUT_DIR, f"{inst}_LS2_{int(TIME_LIMIT)}_{seed}.trace") # ls1 or ls 2
        files = glob.glob(pattern)
        if not files:
            raise FileNotFoundError(f"No trace for {pattern}")
        with open(files[0]) as f:
            trace = [tuple(map(float, line.split())) for line in f]
        traces[inst].append(trace)

# qrtd plot logic
plt.figure()
for inst in INSTANCES:
    # compute times to reach each quality threshold
    times_for_q = {q: [] for q in Q_STARS}
    for trace in traces[inst]:
        for q in Q_STARS:
            threshold = opt[inst] * (1 + q)  # calculate threshold
            # find earliest time where quality <= threshold
            t_solved = TIME_LIMIT
            for t, sol_size in trace:
                if sol_size <= threshold:
                    t_solved = t
                    break
            if t_solved != TIME_LIMIT:
                times_for_q[q].append(t_solved)
    # plot CDF for each q*
    for i, q in enumerate(Q_STARS):
        xs = np.sort(times_for_q[q])
        ys = np.arange(1, len(xs) + 1) / len(xs)
        plt.plot(xs, ys, label=f"{inst}, q*={int(q*100)}%",
                 marker=markers[i])
    plt.xlabel("Time (s)")
    plt.ylabel("Fraction of runs solved")
    plt.title("Qualified Runtime Distributions (QRTD)")
    plt.legend()
    plt.show()

# sqd plot logic
plt.figure()
for inst in INSTANCES:
    errs_at_t = {tp: [] for tp in TIME_POINTS}
    for trace in traces[inst]:
        for tp in TIME_POINTS:
            # best solution quality up to time tp
            best_quality = trace[0][1]
            for t, sol_size in trace:
                if t <= tp:
                    best_quality = sol_size
                else:
                    break
            rel_err = (best_quality - opt[inst]) / opt[inst]
            errs_at_t[tp].append(rel_err)
    # plot CDF of relative error at each time
    for i, tp in enumerate(TIME_POINTS):
        xs = np.sort(errs_at_t[tp])
        ys = np.arange(1, len(xs) + 1) / len(xs)
        plt.plot(xs, ys, label=f"{inst}, t={tp}s", marker=markers[i])
    plt.xlabel("Relative Error")
    plt.ylabel("Fraction of runs ≤ error")
    plt.title("Solution Quality Distributions (SQD)")
    plt.legend()
    plt.show()
