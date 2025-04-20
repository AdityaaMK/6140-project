#!/usr/bin/env python3
import subprocess
import time
import glob
import os
import statistics
import csv

DATA_DIR    = "/Users/arjuna/School/6140/project/6140-project/code/data"
SA_SCRIPT   = "/Users/arjuna/School/6140/project/6140-project/code/algos.py"
TIME_LIMIT  = 600
OUTPUT_CSV  = "approx_results.csv"
OUTPUT_DIR  = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)  # ensure output directory exists

def run_one(inst_path):
    start = time.time()
    subprocess.run([
        "python3",
        SA_SCRIPT,
        "-inst", inst_path,
        "-alg", "Approx",
        "-time", str(TIME_LIMIT)
    ], check=True)
    elapsed = time.time() - start

    inst_name = os.path.splitext(os.path.basename(inst_path))[0]
    sol_file = os.path.join(OUTPUT_DIR, f"{inst_name}_Approx_{TIME_LIMIT}.sol")
    with open(sol_file) as f:
        size = int(f.readline().strip())  # read solution size
    return inst_path, elapsed, size

def main():
    patterns = [os.path.join(DATA_DIR, "small*.in"),
                os.path.join(DATA_DIR, "large*.in")]
    instances = sorted(sum((glob.glob(p) for p in patterns), []))

    results = [run_one(inst) for inst in instances]

    inst_times = {inst: [] for inst in instances}
    inst_sizes = {inst: [] for inst in instances}

    for inst, elapsed, size in results:
        inst_times[inst].append(elapsed)
        inst_sizes[inst].append(size)

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
