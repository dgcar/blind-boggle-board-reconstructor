import json
import os
from collections import defaultdict
from ortools.sat.python import cp_model

class BoggleBoardReconstructor:
    """Reconstructs a Boggle board given word paths and a dictionary."""
    
    def __init__(self, board_size: int, word_paths_file: str, dictionary_file: str):
        """Initializes the board reconstructor with required files."""
        self.board_size = board_size
        self.word_paths_file = word_paths_file
        self.dictionary_file = dictionary_file
        self.word_paths = self.load_word_paths()
        self.words_by_length = defaultdict(set)
        self.valid_words = self.load_dictionary()
        self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
        self.letter_options = defaultdict(set)
        self.build_constraints()
    
    def load_word_paths(self):
        """Loads word paths from a JSON file."""
        if not os.path.exists(self.word_paths_file):
            raise FileNotFoundError(f"Word paths file {self.word_paths_file} not found.")
        with open(self.word_paths_file, "r") as file:
            paths_data = json.load(file)
        return [tuple(tuple(coord) for coord in entry["path"]) for entry in paths_data]
    
    def load_dictionary(self):
        """Loads a dictionary from a file, filtering out two-letter words."""
        if not os.path.exists(self.dictionary_file):
            raise FileNotFoundError(f"Dictionary file {self.dictionary_file} not found.")
        with open(self.dictionary_file, "r") as file:
            words = set(word.strip().upper() for word in file.readlines() if len(word.strip()) > 2)
        for word in words:
            self.words_by_length[len(word)].add(word)
        return words
    
    def build_constraints(self):
        """Prepares letter constraints based on word paths."""
        for path in self.word_paths:
            length = len(path)
            if length in self.words_by_length:
                for word in self.words_by_length[length]:
                    for (coord, letter) in zip(path, word):
                        self.letter_options[tuple(coord)].add(ord(letter) - ord('A'))
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in self.letter_options:
                    self.letter_options[(r, c)] = set(range(26))
    
    def solve_with_csp(self):
        """Solves the Boggle board using constraint programming (CSP)."""
        model = cp_model.CpModel()
        variables = {}
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                domain = list(self.letter_options[(r, c)])
                variables[(r, c)] = model.NewIntVarFromDomain(cp_model.Domain.FromValues(domain), f"cell_{r}_{c}")
        
        for path in self.word_paths:
            length = len(path)
            if length in self.words_by_length:
                possible_words = [word for word in self.words_by_length[length]]
                word_vars = [variables[(r, c)] for r, c in path]
                encoded_words = [[ord(letter) - ord('A') for letter in word] for word in possible_words]
                model.AddAllowedAssignments(word_vars, encoded_words)
        
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            for (r, c), var in variables.items():
                self.board[r][c] = chr(solver.Value(var) + ord('A'))
            return True
        return False
    
    def reconstruct_board(self):
        """Attempts to solve the board and returns the result."""
        if self.solve_with_csp():
            return self.board
        return None

    def display_board(self):
        """Prints the reconstructed board."""
        for row in self.board:
            print(' '.join(row))

if __name__ == "__main__":
    # Example usage:
    board_size = 4
    word_paths_file = "word_paths.json"  # Replace with your file path to the word paths file
    dictionary_file = "dictionary.txt"  # Replace with your file path to dictionary.txt

    reconstructor = BoggleBoardReconstructor(board_size, word_paths_file, dictionary_file)
    board = reconstructor.reconstruct_board()
    if board:
        reconstructor.display_board()
    else:
        print("No valid board found.")
