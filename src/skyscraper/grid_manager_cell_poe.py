from typing import List


def get_cell_indices_from_row_index(row_index: int, n: int) -> List[int]:
    return [row_index * n + i for i in range(n)]


def get_cell_indices_from_col_index(col_index: int, n: int) -> List[int]:
    return [col_index + i * n for i in range(n)]


def get_row_indices_from_cell_index(cell_index: int, n: int) -> List[int]:
    y = cell_index // n
    return [i for i in get_cell_indices_from_row_index(y, n) if i != cell_index]


def get_col_indices_from_cell_index(cell_index: int, n: int) -> List[int]:
    x = cell_index % n
    return [i for i in get_cell_indices_from_col_index(x, n) if i != cell_index]


def get_cell_indices_from_clue_index(clue_index: int, n: int) -> List[int]:
    if clue_index < n:
        return get_cell_indices_from_col_index(clue_index, n)
    elif clue_index < 2 * n:
        col_index = clue_index - n
        return get_cell_indices_from_col_index(col_index, n)[::-1]
    elif clue_index < 3 * n:
        row_index = clue_index - 2 * n
        return get_cell_indices_from_row_index(row_index, n)
    elif clue_index < 4 * n:
        row_index = clue_index - 3 * n
        return get_cell_indices_from_row_index(row_index, n)[::-1]


def get_cross_indices_from_cell_index(cell_index: int, n: int, cache: dict) -> List[int]:
    if cell_index not in cache:
        cache[cell_index] = (
            get_row_indices_from_cell_index(cell_index, n) +
            get_col_indices_from_cell_index(cell_index, n)
        )
    return cache[cell_index]
