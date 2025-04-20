#!/usr/bin/env python3
from multiprocessing import Pool, cpu_count
import subprocess
import time
import glob
import os
import statistics
import csv

DATA_DIR = "/Users/arjuna/School/6140/project/6140-project/code/data"
SA_SCRIPT = "/Users/arjuna/School/6140/project/6140-project/code/algos.py"
TIME_LIMIT = 600
SEEDS = list(range(1, 11))
OUTPUT_CSV = "ls2_results.csv"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)  # ensure output directory exists
 

def run_one(args):
    inst_path, seed = args
    start = time.time()
    subprocess.run([
        "python3",
        SA_SCRIPT,
        "-inst", inst_path,
        "-alg", "LS2",
        "-time", str(TIME_LIMIT),
        "-seed", str(seed)
    ], check=True)
    elapsed = time.time() - start

    inst_name = os.path.splitext(os.path.basename(inst_path))[0]
    sol_pattern = os.path.join(
        OUTPUT_DIR, f"{inst_name}_LS2_{TIME_LIMIT}_{seed}.sol")
    with open(sol_pattern) as f:
        size = int(f.readline().strip())  # read solution size
    return inst_path, elapsed, size


def main():
    # collect all instances
    patterns = [os.path.join(DATA_DIR, "small*.in"),
                os.path.join(DATA_DIR, "large*.in")]
    instances = sorted(sum((glob.glob(p) for p in patterns), []))

    # build task list (inst, seed)
    tasks = [(inst, seed) for inst in instances for seed in SEEDS]

    # run in parallel with multiprocessing
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(run_one, tasks)

    # aggregate by instance
    inst_times = {inst: [] for inst in instances}
    inst_sizes = {inst: [] for inst in instances}

    for inst, elapsed, size in results:
        inst_times[inst].append(elapsed)
        inst_sizes[inst].append(size)

    # write CSV
    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Instance", "AvgTime(s)", "AvgSize", "RelErr"])
        for inst in instances:
            opt_file = inst[:-3] + ".out"
            with open(opt_file) as f:
                optimal = int(f.readline().strip())

            avg_time = statistics.mean(inst_times[inst])
            avg_size = statistics.mean(inst_sizes[inst])
            rel_err = (avg_size - optimal) / optimal

            inst_name = os.path.basename(inst)[:-3]
            writer.writerow([
                inst_name,
                f"{avg_time:.3f}",
                f"{avg_size:.3f}",
                f"{rel_err:.3f}"
            ])

    print(f"Done! Results written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
