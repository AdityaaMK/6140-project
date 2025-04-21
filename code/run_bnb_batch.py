#!/usr/bin/env python3
import subprocess
import time
import glob
import os
import statistics
import csv

from multiprocessing import Pool, cpu_count
import subprocess
import time
import glob
import os
import statistics
import csv

DATA_DIR = "/Users/sakethchaluvadi/Desktop/6140-project/code/data"
SA_SCRIPT = "local_search_algos.py"
TIME_LIMIT = 600
SEEDS = list(range(1, 11))
OUTPUT_CSV = "bnb_results_600.csv"
OUTPUT_DIR = "bnb_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_one(inst_path):
    start = time.time()
    subprocess.run([
        "python3",
        SA_SCRIPT,
        "-inst", inst_path,
        "-alg", "BnB",
        "-time", str(TIME_LIMIT),
    ], check=True)
    elapsed = time.time() - start

    inst_name = os.path.splitext(os.path.basename(inst_path))[0]
    sol_pattern = os.path.join(
        OUTPUT_DIR, f"{inst_name}_BnB_{TIME_LIMIT}.sol")
    with open(sol_pattern) as f:
        size = int(f.readline().strip())  # read solution size
    return inst_path, elapsed, size


def main():
    # collect all instances
    patterns = [os.path.join(DATA_DIR, "small*.in"),
                os.path.join(DATA_DIR, "large*.in")]
    instances = sorted(sum((glob.glob(p) for p in patterns), []))

    # build task list (inst, seed)
    tasks = [(inst) for inst in instances]

    # run in parallel with multiprocessing
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(run_one, tasks)

    # aggregate by instance
    inst_times = {inst: [] for inst in instances}
    inst_sizes = {inst: [] for inst in instances}

    for inst, elapsed, size in results:
        inst_times[inst].append(min(TIME_LIMIT, elapsed))
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

