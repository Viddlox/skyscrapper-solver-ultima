from typing import List, Tuple
from functools import cache

from .constants import Permutation


def get_clue_indices_for_row(n: int, row_index: int) -> Tuple[int, int]:
    return (2 * n + row_index, 3 * n + row_index)


def get_clue_indices_for_col(n: int, col_index: int) -> Tuple[int, int]:
    return (col_index, n + col_index)


def get_clues_for_row(clues: List[int], n: int, row_index: int) -> Tuple[int, int]:
    left_idx, right_idx = get_clue_indices_for_row(n, row_index)
    return (clues[left_idx], clues[right_idx])


def get_clues_for_col(clues: List[int], n: int, col_index: int) -> Tuple[int, int]:
    top_idx, bottom_idx = get_clue_indices_for_col(n, col_index)
    return (clues[top_idx], clues[bottom_idx])


@cache
def count_visible_reverse(perm: "Permutation") -> int:
    visible, max_height = 0, 0
    for i in range(len(perm) - 1, -1, -1):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
    return visible


@cache
def count_visible_start(perm: "Permutation") -> int:
    visible, max_height = 0, 0
    for height in perm:
        if height > max_height:
            visible += 1
            max_height = height
    return visible
