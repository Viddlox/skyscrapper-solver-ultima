from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .constants import Permutation


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
    top = clues[0:n]
    bottom = clues[n:2*n]
    left = clues[2*n:3*n]
    right = clues[3*n:4*n]
    return (top, bottom, left, right)

def count_visible_reverse(perm: "Permutation") -> int:
    visible, max_height = 0, 0
    for i in range(len(perm) - 1, -1, -1):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
    return visible


def count_visible_start(perm: "Permutation") -> int:
    visible, max_height = 0, 0
    for height in perm:
        if height > max_height:
            visible += 1
            max_height = height
    return visible


def count_visible_up_to_position(perm: "Permutation", end_pos: int) -> int:
    visible, max_height = 0, 0
    for i in range(end_pos + 1):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
    return visible


def count_visible_up_to_position_reverse(perm: "Permutation", start_pos: int) -> int:
    visible, max_height = 0, 0
    for i in range(len(perm) - 1, start_pos - 1, -1):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
    return visible
