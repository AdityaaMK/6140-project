'''
This file contains a simulated annealing algorithm for the set cover problem.
It uses a greedy start and a cooling factor alpha similar to the lecture. The algorithm runs until it cannot
find a better solution within a certain number of iterations and the best solution it has found is written to a file.
The solution file name includes the instance, method, and seed. Additionally, a trace file is written which contains the best solution found so far at each time step.
'''
import random
import math
import time
import argparse
import os

OUTPUT_DIR = "output"


def read_instance(file):
    '''reads set cover instance from file'''
    with open(file) as f:
        n, m = map(int, f.readline().split())
        subsets = []
        for _ in range(m):
            line = list(map(int, f.readline().split()))
            subsets.append(set(line[1:]))
    return n, subsets


def find_candidate_sol(n, subsets, solution=None):
    '''greedy: pick subset covering most uncovered elements until all covered'''
    uncovered = set(range(1, n + 1))
    if solution:
        for i in solution:
            uncovered -= subsets[i]
    else:
        solution = set()
    while uncovered:
        best_idx, best_size = 0, 0
        for idx, subset in enumerate(subsets):
            intersection = uncovered.intersection(subset)
            if len(intersection) > best_size:  # pick largest intersection
                best_idx, best_size = idx, len(intersection)
        solution.add(best_idx)
        uncovered -= subsets[best_idx]
    return solution


def cost(solution):
    '''returns cost of solution - in this case number of subsets'''
    return len(solution)


def covers_all(n, subsets, solution):
    '''checks if solution covers all elements'''
    covered = set()
    for idx in solution:
        covered |= subsets[idx]
    return len(covered) == n


def get_neighbor(n, subsets, current_sol):
    '''create neighbor by flipping membership of a subset, then find new candidate sol if needed'''
    idx = random.randint(0, len(subsets)-1)
    neighbor = set(current_sol)
    if idx in neighbor:
        neighbor.remove(idx)
    else:
        neighbor.add(idx)
    if not covers_all(n, subsets, neighbor):
        neighbor = find_candidate_sol(n, subsets, neighbor)
    return neighbor


def simulated_annealing(n, subsets, time_limit, T_0, alpha, max_no_improvement=10000):
    '''simulated annealing algorithm similar to lecture description'''
    start = time.time()
    current_sol = find_candidate_sol(n, subsets)  # generate initial solution
    best = set(current_sol)
    T = T_0
    trace = [(0.0, cost(best))]
    no_improvement = 0
    while time.time() - start < time_limit:
        elapsed = time.time() - start
        T *= alpha  # decrease temp by cooling factor
        neighbor = get_neighbor(n, subsets, current_sol)
        delta = cost(current_sol) - cost(neighbor)
        if delta > 0 or random.random() < math.exp(delta/T):
            current_sol = neighbor
            if cost(current_sol) < cost(best):
                best = set(current_sol)
                trace.append((elapsed, cost(best)))
                no_improvement = 0
            else:
                no_improvement += 1
            if no_improvement >= max_no_improvement:
                print("No improvement for", max_no_improvement, "iterations")
                break
    return best, trace


def write_sol(instance, method, cutoff, seed, sol):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(instance))[0]
    fname = f"{base}_{method}_{cutoff}"
    if seed is not None:
        fname += f"_{seed}"
    fname += ".sol"
    out_path = os.path.join(OUTPUT_DIR, fname)
    with open(out_path, "w") as f:
        f.write(str(len(sol)) + '\n')
        f.write(' '.join(str(i+1) for i in sorted(sol)) + '\n')


def write_trace(instance, method, cutoff, seed, trace):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(instance))[0]
    fname = f"{base}_{method}_{cutoff}"
    if seed is not None:
        fname += f"_{seed}"
    fname += ".trace"
    out_path = os.path.join(OUTPUT_DIR, fname)
    with open(out_path, "w") as f:
        for t, q in trace:
            f.write(f"{t:.4f} {q}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-inst', required=True)
    parser.add_argument(
        '-alg', choices=['LS1', 'LS2', 'BnB', 'Approx'], required=True)
    parser.add_argument('-time', type=float, required=True)
    parser.add_argument('-seed', type=int)
    args = parser.parse_args()

    random.seed(args.seed)
    n, subsets = read_instance(args.inst)
    if args.alg == 'LS1':
        best, trace = simulated_annealing(
            n, subsets, args.time, T_0=1.0, alpha=0.98)
        write_sol(args.inst, 'LS1', int(args.time), args.seed, best)
        write_trace(args.inst, 'LS1', int(args.time), args.seed, trace)


if __name__ == '__main__':
    main()
