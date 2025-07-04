from typing import List, Tuple

def get_clue_indices_for_row(n: int, row_index: int) -> Tuple[int, int]:
    """Get the left and right clue indices for a row"""
    return (2 * n + row_index, 3 * n + row_index)


def get_clue_indices_for_col(n: int, col_index: int) -> Tuple[int, int]:
    """Get the top and bottom clue indices for a column"""
    return (col_index, n + col_index)


def get_clues_for_row(clues: List[int], n: int, row_index: int) -> Tuple[int, int]:
    """Get the actual clue values (left, right) for a row"""
    left_idx, right_idx = get_clue_indices_for_row(n, row_index)
    return (clues[left_idx], clues[right_idx])


def get_clues_for_col(clues: List[int], n: int, col_index: int) -> Tuple[int, int]:
    """Get the actual clue values (top, bottom) for a column"""
    top_idx, bottom_idx = get_clue_indices_for_col(n, col_index)
    return (clues[top_idx], clues[bottom_idx])


def decode_clue_layout(clues: List[int], n: int) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Decode flat clue list into directional clue lists.
    """
    top = clues[0:n]
    bottom = clues[n:2*n]  
    left = clues[2*n:3*n]
    right = clues[3*n:4*n]
    return (top, bottom, left, right)


def get_intersection_position(row_idx: int, col_idx: int) -> Tuple[int, int]:
    """Get the intersection position - just returns the same coordinates"""
    return (row_idx, col_idx)


def is_valid_position(row_idx: int, col_idx: int, n: int) -> bool:
    """Check if row/col indices are valid for grid size n"""
    return 0 <= row_idx < n and 0 <= col_idx < n
