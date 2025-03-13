import json
from collections import defaultdict

class TrieNode:
    """Node in a Trie data structure."""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    """Trie (Prefix Tree) for storing valid words."""
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str):
        """Inserts a word into the Trie."""
        node = self.root
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.is_end_of_word = True
    
    def search_prefix(self, prefix: str):
        """Searches for a prefix in the Trie."""
        node = self.root
        for letter in prefix:
            if letter not in node.children:
                return None
            node = node.children[letter]
        return node
    
    def is_word(self, word: str) -> bool:
        """Checks if a word exists in the Trie."""
        node = self.search_prefix(word)
        return node is not None and node.is_end_of_word
    
    def starts_with(self, prefix: str) -> bool:
        """Checks if a prefix exists in the Trie."""
        return self.search_prefix(prefix) is not None

# Possible directions to move in Boggle
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

class BoggleSolver:
    """Finds all valid words in a Boggle board."""
    def __init__(self, board: list[list[str]], dictionary: set[str]):
        self.board = board
        self.n = len(board)
        self.trie = Trie()
        self.load_dictionary(dictionary)
        self.found_paths = {}
    
    def load_dictionary(self, dictionary: set[str]):
        """Loads words longer than two letters into the Trie."""
        for word in dictionary:
            if len(word) > 2:
                self.trie.insert(word)
    
    def is_valid(self, r: int, c: int, visited: set) -> bool:
        """Checks if a position is within bounds and not visited."""
        return 0 <= r < self.n and 0 <= c < self.n and (r, c) not in visited
    
    def dfs(self, r: int, c: int, node: TrieNode, word: str, path: list):
        """Performs DFS to find all valid words following Boggle adjacency rules."""
        letter = self.board[r][c]
        if letter not in node.children:
            return
        
        node = node.children[letter]
        word += letter
        path.append((r, c))
        
        if node.is_end_of_word and word not in self.found_paths:
            self.found_paths[word] = list(path)
        
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if self.is_valid(nr, nc, path):
                self.dfs(nr, nc, node, word, path[:])
    
    def find_words(self):
        """Finds all words in the Boggle board."""
        for r in range(self.n):
            for c in range(self.n):
                self.dfs(r, c, self.trie.root, "", [])
    
    def save_paths(self, filename="word_paths.json"):
        """Saves found words' paths and lengths to a file."""
        paths_data = [
            {"path": path, "length": len(path)} 
            for path in self.found_paths.values()
        ]
        with open(filename, "w") as file:
            json.dump(paths_data, file, indent=4)
    
    def solve_and_save(self):
        """Runs the solver and saves the results to a file."""
        self.find_words()
        self.save_paths()
        print(f"Found {len(self.found_paths)} words. Saved to word_paths.json")

if __name__ == "__main__":
    # Example usage
    # You can replace with your own Boggle game!
    board = [
        ["T", "A", "P", "S"],
        ["O", "G", "D", "E"],
        ["E", "S", "T", "N"],
        ["R", "A", "P", "O"]
    ]
    
    dictionary_file = "dictionary.txt"  # Replace with your file path to dictionary.txt
    
    with open(dictionary_file, "r") as f:
        dictionary = set(word.strip().upper() for word in f.readlines())
    
    solver = BoggleSolver(board, dictionary)
    solver.solve_and_save()
