# Set Cover Problem Solver

This project provides attempts to solve the Set Cover Problem using various algorithms. An executable is provided to allow users to specify different algorithms, time limits, and random seeds for reproducibility.

## Algorithms Implemented

The following algorithms are implemented in `algos.py`:

- **Greedy Approximation Algorithm**: A heuristic approach that iteratively selects the subset covering the most uncovered elements.
- **Branch and Bound Algorithm**: An exact algorithm using backtracking with lower and upper bounds to find the optimal solution.
- **Simulated Annealing**: A variant of local search that uses a probabilistic approach for approximating the global optimum of a given function. 
- **Random Restart Hill Climbing**: A variant of local search that repeatedly applies hill climbing from random starting points.

## Usage

The executable can be run from the command line with the following format:

```python
python -inst <filename> -alg [BnB|Approx|LS1|LS2] -time <cutoff in seconds> -seed <random seed>
```

### Parameters

- `-inst <filename>`: The path to the dataset file.
- `-alg [BnB|Approx|LS1|LS2]`: The algorithm to use.
- `-time <cutoff in seconds>`: The maximum time allowed for the algorithm to run.
- `-seed <random seed>`: The random seed for reproducibility (only applicable for randomized methods).

## Output

The program generates two types of output files:

1. **Solution Files**: Contain the quality and the indices of the subsets selected.
   - Format: `<instance>_<method>_<cutoff>_<randSeed>.sol`
   - Example: `example_LS1_600_4.sol`

2. **Solution Trace Files**: Record the quality of the best solution found at each timestamp.
   - Format: `<instance>_<method>_<cutoff>_<randSeed>.trace`
   - Example: `example_LS1_600_4.trace`

## File Structure

- `algos.py`: Contains the implementation of all algorithms.
- `run_<algorithm>_batch.py`: Scripts to run batch experiments for each algorithm.
- `<algorithm>_output/`: Directory where output files are stored.
- `data/`: Directory containing dataset files.

## Running the Code

To execute the program, use the command format provided above. Ensure that the dataset file is correctly specified and located in the `data/` directory.

## Example

```python
python -inst data/small1.in -alg LS1 -time 600 -seed 10
```

This command runs the Local Search 1 algorithm on `small1.in` with a 600-second cutoff and a random seed of 10.

