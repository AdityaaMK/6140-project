#!/usr/bin/env python3
import os
import csv

OUTPUT_DIR = "/Users/arjuna/School/6140/project/6140-project/code/output"
INSTANCES = ["large10"]
TIME_LIMIT = 600
SEEDS = range(1, 11)
LS_NUM = "LS2"

with open("ls2_runtimes.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Runtimes"])
    for inst in INSTANCES:
        for seed in SEEDS:
            trace_file = os.path.join(
                OUTPUT_DIR,
                f"{inst}_{LS_NUM}_{TIME_LIMIT}_{seed}.trace"
            )
            # load the trace and grab the last timestamp
            with open(trace_file) as f:
                lines = [line.split() for line in f if line.strip()]
                last_time = float(lines[-1][0])
            writer.writerow([f"{last_time:.4f}"])
print("wrote runtimes.csv")
