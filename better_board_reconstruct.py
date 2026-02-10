import json
from collections import defaultdict

# --- EDIT THESE TWO PATHS ---
PATHS_FILE = "/path/to/word_paths.json" 
DICT_FILE  = "/path/to/dictionary.txt"
# ---------------------------

ALL = (1 << 26) - 1  # 26-letter domain bitmask


def iter_bits(x):
    """Yield indices of 1-bits in x."""
    while x:
        lsb = x & -x
        yield lsb.bit_length() - 1
        x ^= lsb


def bitcount(x):
    return x.bit_count() if hasattr(int, "bit_count") else bin(x).count("1")


def load_paths():
    """Returns (paths_as_coords, nrows, ncols, max_len)."""
    data = json.load(open(PATHS_FILE, "r", encoding="utf-8"))

    raw = []
    max_r = max_c = 0
    max_len = 0

    for item in data:
        coords = [tuple(p) for p in item["path"]]
        L = len(coords)  # trust the actual path length
        raw.append((coords, L))

        for r, c in coords:
            if r > max_r: max_r = r
            if c > max_c: max_c = c

        if L > max_len: max_len = L

    return raw, max_r + 1, max_c + 1, max_len


def load_dictionary(max_len):
    """words_by_len[L] = [WORD, WORD, ...] (uppercased)."""
    words_by_len = defaultdict(list)

    with open(DICT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w or not w.isalpha():
                continue
            w = w.upper()
            L = len(w)
            if 1 <= L <= max_len:
                words_by_len[L].append(w)

    return words_by_len


def build_index(words_by_len):
    """
    index[L][pos][letter] = bitset of word IDs with that letter at that position
    all_mask[L] = bitset with all word IDs for that length
    """
    index = {}
    all_mask = {}

    for L, words in words_by_len.items():
        m = len(words)
        if m == 0:
            continue

        all_mask[L] = (1 << m) - 1
        pos_tables = []

        for pos in range(L):
            letter_bits = [0] * 26
            for wid, w in enumerate(words):
                li = ord(w[pos]) - 65
                if 0 <= li < 26:
                    letter_bits[li] |= (1 << wid)
            pos_tables.append(letter_bits)

        index[L] = pos_tables

    return index, all_mask


def allowed_words_for_pos(index_pos, allowed_letters_mask):
    """OR together word-bitsets for all allowed letters at one position."""
    out = 0
    m = allowed_letters_mask
    while m:
        lsb = m & -m
        letter = lsb.bit_length() - 1
        out |= index_pos[letter]
        m ^= lsb
    return out


def compute_path_candidates(path_cells, L, domains, index, all_mask):
    """Return bitset of candidate word IDs for this path."""
    if L not in index:
        return 0

    cand = all_mask[L]
    idxL = index[L]

    for pos, cell in enumerate(path_cells):
        allowed = domains[cell]
        if allowed == 0:
            return 0
        cand &= allowed_words_for_pos(idxL[pos], allowed)
        if cand == 0:
            return 0

    return cand


def possible_letters_at_pos(cands, index_pos):
    """Which letters appear among candidate words at this (length,pos)?"""
    mask = 0
    for letter in range(26):
        if cands & index_pos[letter]:
            mask |= (1 << letter)
    return mask


def propagate(domains, path_cands, paths, index, all_mask, n_cells):
    """
    Tighten:
      - path candidates from cell domains
      - cell domains from path candidates
    until stable
    """
    changed = True
    while changed:
        changed = False

        # Update each path's candidate set from current cell domains
        for pid, (cells, L) in enumerate(paths):
            new_pc = compute_path_candidates(cells, L, domains, index, all_mask)
            if new_pc == 0:
                return False
            if new_pc != path_cands[pid]:
                path_cands[pid] = new_pc
                changed = True

        # Update cell domains from path candidate sets
        new_domains = [ALL] * n_cells
        for pid, (cells, L) in enumerate(paths):
            cands = path_cands[pid]
            idxL = index[L]
            for pos, cell in enumerate(cells):
                new_domains[cell] &= possible_letters_at_pos(cands, idxL[pos])
                if new_domains[cell] == 0:
                    return False

        # Intersect with existing domains
        for i in range(n_cells):
            nd = new_domains[i] & domains[i]
            if nd == 0:
                return False
            if nd != domains[i]:
                domains[i] = nd
                changed = True

    return True


def solved(domains):
    """All cells are single letters."""
    for d in domains:
        if d & (d - 1):
            return False
    return True


def choose_branch_path(path_cands):
    """Path with fewest candidates (>1)."""
    best = None
    best_cnt = 10**9
    for pid, c in enumerate(path_cands):
        cnt = bitcount(c)
        if 1 < cnt < best_cnt:
            best_cnt = cnt
            best = pid
    return best


def solve(domains, path_cands, paths, index, all_mask, n_cells, words_by_len):
    """DFS + propagate."""
    if not propagate(domains, path_cands, paths, index, all_mask, n_cells):
        return None

    if solved(domains):
        return domains

    pid = choose_branch_path(path_cands)
    if pid is None:
        return None  # should be solved already, but just in case

    cells, L = paths[pid]
    words = words_by_len[L]
    candidates = path_cands[pid]

    for wid in iter_bits(candidates):
        w = words[wid]

        d2 = domains[:]       # copy state
        pc2 = path_cands[:]   # copy state
        pc2[pid] = 1 << wid   # force that path to this word

        ok = True
        for pos, cell in enumerate(cells):
            letter = ord(w[pos]) - 65
            mask = 1 << letter
            if d2[cell] & mask == 0:
                ok = False
                break
            d2[cell] = mask

        if not ok:
            continue

        res = solve(d2, pc2, paths, index, all_mask, n_cells, words_by_len)
        if res is not None:
            return res

    return None


def mask_to_letter(mask):
    return chr(65 + (mask.bit_length() - 1))


def main():
    raw_paths, nrows, ncols, max_len = load_paths()
    words_by_len = load_dictionary(max_len)
    index, all_mask = build_index(words_by_len)

    # Convert coordinate paths to linear cell IDs
    paths = []
    for coords, L in raw_paths:
        cell_ids = [r * ncols + c for (r, c) in coords]
        paths.append((cell_ids, L))

    n_cells = nrows * ncols
    domains = [ALL] * n_cells
    path_cands = [all_mask.get(L, 0) for (_, L) in paths]

    sol = solve(domains, path_cands, paths, index, all_mask, n_cells, words_by_len)

    if sol is None:
        print("No solution found.")
        return

    for r in range(nrows):
        row = [mask_to_letter(sol[r * ncols + c]) for c in range(ncols)]
        print(" ".join(row))


if __name__ == "__main__":
    main()
