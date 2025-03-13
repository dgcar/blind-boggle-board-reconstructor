# Boggle Board Reconstructor

## **Overview**
This project consists of two Python scripts that work together to **decode a Boggle board's letter placements** using only the **word paths**—without knowing the letters beforehand. 

The challenge is to reconstruct the Boggle board **using only the structure of word paths**, ensuring that the placed letters form valid words from a given dictionary.

---

## **How It Works**
### **1️⃣ Finding Word Paths – `word_path_finder.py`**
This script **analyzes a known Boggle board (with letters)** to extract all **valid word paths** and saves them in a JSON file.  
- It uses a **Trie (prefix tree)** for fast word lookups.
- It explores **all possible words** using Depth-First Search (DFS).
- The found word paths are **saved in `word_paths.json`** (without letters).

 **Input:**  
- A known `NxN` **Boggle board (with letters).**  
- A dictionary file (`dictionary.txt`).  

 **Output:**  
- `word_paths.json` containing word paths **without knowing the letters.**  

---

### **2️⃣ Reconstructing the Board – `board_reconstruct.py`**
This script takes only the **word paths** (not letters!) and a dictionary to **determine the board's letter placements.**  
- Uses **Constraint Programming (CSP)** to enforce valid letter placements.  
- Ensures that all paths lead to real words from the dictionary.  
- Solves the board without knowing any letters beforehand!  

 **Input:**  
- `word_paths.json` (from `word_path_finder.py`).  
- A dictionary file (`dictionary.txt`).  

 **Output:**  
- A reconstructed **Boggle board with letters.**  

---

## **Installation & Usage**
### **Setup**
Clone the repository:
```bash
git clone https://github.com/yourusername/boggle-board-reconstructor.git
cd boggle-board-reconstructor
```

### **Install dependencies:**
```bash
pip install ortools
```
Ensure you have a dictionary file (dictionary.txt).

### **Step 1: Generate Word Paths**
Run word_path_finder.py to extract valid word paths from a known Boggle board:
```bash
python word_path_finder.py
```
This will create word_paths.json.


### **Step 2: Reconstruct the Board**
Run board_reconstruct.py to build the board using only the word paths:
```bash
python board_reconstruct.py
```
If successful, it will print the reconstructed Boggle board.


## **Example**
### **Original Boggle Board (Known Only to `word_path_finder.py`):**
```mathematica
T  A  P  S
O  G  D  E
E  S  T  N
R  A  P  O
```
### **Extracted Word Paths (Saved in word_paths.json):**
```json
[
    {"path": [[0,0], [0,1], [0,2]], "length": 3},
    {"path": [[1,1], [1,2], [2,2], [2,3]], "length": 4}
]
```

### **Reconstructed Board (Output of board_reconstruct.py):**
```mathematica
T  A  P  S
O  G  D  E
E  S  T  N
R  A  P  O
```
The program correctly reconstructs the board using only word paths!


## **Why This Is Cool 😎**
- It solves a logic puzzle by reconstructing the board without knowing any letters!
- Efficient algorithms (Trie-based word search + Constraint Programming).
- A unique approach to reverse-engineering letter placements.
