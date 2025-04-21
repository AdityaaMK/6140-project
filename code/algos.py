'''
This file contains all algorithms for the set cover problem.
It includes:
- Greedy approximation algorithm
- Branch and bound algorithm
- Simulated annealing algorithm
- Random restart hill climbing algorithm

The algorithms are implemented in a way that they can be run from the command line with the following arguments:
- -inst: the instance file
- -alg: the algorithm to use (LS1, LS2, BnB, Approx)
- -time: the time limit in seconds
- -seed: the random seed (optional)
'''
import random
import math
import time
import argparse
import os
import heapq

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

def greedy_candidate_sol(n, subsets, solution=None):
    '''greedy approximation algorithm: pick subset covering most uncovered elements until all covered, used for bnb, greedy and local search'''
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


def find_bnb_sol(n, subsets, time_limit):
    '''exact branch-and-bound algorithm: backtracking algorithm using a lower bound and upper bound for the set cover problem similar to lecture description'''
    start = time.time()
    trace = []
    # Initial upper bound found by greedy_candidate_sol
    best_solution = greedy_candidate_sol(n, subsets)
    best_size = len(best_solution)

    root_uncovered = frozenset(range(1, n + 1))
    subset_ids = frozenset(range(len(subsets)))
    max_set_size = max(len(subset) for subset in subsets)
    root_lb = math.ceil(len(root_uncovered) / max_set_size)

    # Priority queue: (lower_bound, current depth, current chosen sets, uncovered elements, remaining sets)
    frontier = [(root_lb, 0, frozenset(), root_uncovered, subset_ids)]
    heapq.heapify(frontier)
    visited = set()

    # frontier size maximum for memory management
    MAX_FRONTIER = 100_000

    trace.append((0.0, best_size))
    while frontier and time.time() - start < time_limit:
        elapsed = time.time() - start

        lb, k, chosen_sets, uncovered, rem_sets = heapq.heappop(frontier)

        # Prune if lower bound is worse than best found solution
        if lb >= best_size:
            continue

        # Success condition: all elements are covered
        if not uncovered:
            print(f"New best solution with {k} sets found")
            best_solution = set(chosen_sets)
            best_size = k
            trace.append((elapsed, best_size))
            continue

        state_key = (uncovered, chosen_sets)
        if state_key in visited:
            continue
        visited.add(state_key)

        # Pick one uncovered element and try all sets that include it
        elem = next(iter(uncovered))
        for i in rem_sets:
            if elem in subsets[i]:
                new_chosen_sets = chosen_sets | {i}
                new_uncovered = uncovered - subsets[i]
                new_rem_sets = rem_sets - {i}

                new_lb = (k + 1) + math.ceil(len(new_uncovered) / max_set_size)
                if new_lb < best_size:
                    if len(frontier) < MAX_FRONTIER:
                        heapq.heappush(frontier, (new_lb, k + 1, new_chosen_sets, new_uncovered, new_rem_sets))

    return best_solution, trace

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
    '''create neighbor by randomly flipping membership of a subset, then find new candidate sol if needed'''
    idx = random.randint(0, len(subsets)-1)
    neighbor = set(current_sol)
    if idx in neighbor:
        neighbor.remove(idx)
    else:
        neighbor.add(idx)
    if not covers_all(n, subsets, neighbor):
        neighbor = greedy_candidate_sol(n, subsets, neighbor)
    return neighbor


def simulated_annealing(n, subsets, time_limit, T_0, alpha, max_no_improvement=10000):
    '''simulated annealing algorithm: first variant of a local search algorithm as presented in lecture'''
    start = time.time()
    current_sol = greedy_candidate_sol(n, subsets)  # generate initial solution
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


def random_init(n, subsets):
    uncovered = set(range(1, n+1))
    sol = set()
    while uncovered:
        candidates = [i for i in range(
            len(subsets)) if len(uncovered.intersection(subsets[i])) > 0]
        idx = random.choice(candidates)
        sol.add(idx)
        uncovered -= subsets[idx]
    return sol


def get_best_neighbor(n, subsets, current_sol):
    best_cost = cost(current_sol)
    best_sol = None
    for i in range(len(subsets)):
        neigh = set(current_sol)
        if i in neigh:
            neigh.remove(i)
        else:
            neigh.add(i)
        if not covers_all(n, subsets, neigh):
            neigh = greedy_candidate_sol(n, subsets, neigh)
        if cost(neigh) < best_cost:
            best_cost = cost(neigh)
            best_sol = neigh
    return best_sol


def random_restart_hill_climbing(n, subsets, time_limit, max_no_improvement=10000): 
    '''simulated annealing algorithm: second variant of a local search algorithm as presented in lecture'''
    start = time.time()
    best = None
    trace = []
    no_improvement = 0

    current = random_init(n, subsets)
    while not covers_all(n, subsets, current):
        current = random_init(n, subsets)
    
    best = set(current)
    trace.append((0.0, cost(best)))
    while True:
        elapsed = time.time() - start
        if elapsed > time_limit:
            break
        current = random_init(n, subsets) # made it fully random instead of greedy
        while True:
            if time.time() - start > time_limit:
                return best, trace
            neighbor = get_best_neighbor(n, subsets, current)
            if neighbor is None:
                break
            current = neighbor
            if cost(current) < cost(best):
                best = set(current)
                trace.append((time.time() - start, cost(best)))
                no_improvement = 0
            else:
                no_improvement += 1
            if no_improvement >= max_no_improvement:
                print("No improvement for", max_no_improvement, "iterations")
                return best, trace
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
    elif args.alg == 'LS2':
        best, trace = random_restart_hill_climbing(
            n, subsets, args.time, max_no_improvement=500)
        write_sol(args.inst, 'LS2', int(args.time), args.seed, best)
        write_trace(args.inst, 'LS2', int(args.time), args.seed, trace)
    elif args.alg == 'BnB':
        best, trace = find_bnb_sol(n, subsets, args.time)
        write_sol(args.inst, 'BnB', int(args.time), None, best)
        write_trace(args.inst, 'BnB', int(args.time), None, trace) 
    elif args.alg == 'Approx':
        best = greedy_candidate_sol(n, subsets)
        write_sol(args.inst, 'Approx', int(args.time), None, best)   


if __name__ == '__main__':
    main()
