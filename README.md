# Blind Boggle Board Reconstructor

This project reconstructs a hidden Boggle board using a list of valid word paths and a dictionary.

The repository includes two solver implementations:

- board_reconstruct.py — Original solver (constraint table / CP-style approach)
- better_board_reconstruct.py — New high-performance solver (bitset + constraint propagation)


## High Performance Solver (better_board_reconstruct.py)

The new solver dramatically improves performance by replacing the original dictionary scanning and constraint table generation with a bitset-based constraint propagation algorithm.

### Algorithm Overview

The solver works by modeling the problem as a constraint system between:

- Possible letters for each board cell
- Possible dictionary words for each word path

Instead of repeatedly scanning dictionary words, the solver:

1. Precomputes dictionary lookup tables:

   index[word_length][position][letter] -> bitset of word IDs

2. Maintains:
   - Letter domains for each board cell (bitmask of A–Z)
   - Candidate word sets for each path (bitset of dictionary words)

3. Repeatedly propagates constraints:
   - Cell domains restrict path candidate words
   - Path candidate words restrict cell domains

4. Uses backtracking only when propagation cannot fully solve the board.


## Performance Improvement

Typical performance improvement observed:

| Solver | Runtime |
|---|---|
| board_reconstruct.py | ~10 minutes |
| better_board_reconstruct.py | ~2 seconds |

(Times depend on dictionary size and number of paths.)


## Repository Structure

README.md  
better_board_reconstruct.py   - Fast solver (recommended)  
board_reconstruct.py          - Original solver (reference / comparison)  
dictionary.txt                - Word list  
word_path_finder.py           - Tool to generate word paths  


## Usage

Run the fast solver:

python better_board_reconstruct.py

Run the original solver:

python board_reconstruct.py


## Key Technical Ideas

This solver uses several performance-oriented techniques commonly used in constraint solving and optimization systems:

- Bitset-based candidate tracking
- Constraint propagation before search
- Smallest-candidate branching (reduces backtracking)
- Precomputed dictionary indexing

These techniques reduce repeated dictionary scans and allow the solver to eliminate large portions of the search space very quickly.


## Background

This project was originally implemented using a constraint table approach.

The newer solver was developed to reduce runtime by focusing on:

- Faster candidate filtering
- Better propagation of constraints
- Reduced reliance on brute-force search


## Future Improvements (Ideas)

Possible future enhancements:

- Prefix caching for shared path segments
- Additional branching heuristics
- Visualization of constraint propagation
- Solver benchmarking tools
