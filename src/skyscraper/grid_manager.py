from typing import List, Tuple

from .game import game


def get_cell_indices_from_row_index(row_index: int) -> List[int]:
    return [row_index * game.n + i for i in range(game.n)]


def get_cell_indices_from_col_index(col_index: int) -> List[int]:
    return [col_index + i * game.n for i in range(game.n)]


def get_cell_indices_from_clue_index(clue_index: int) -> List[int]:
    if clue_index < game.n:
        return get_cell_indices_from_col_index(clue_index, game.n)
    elif clue_index < 2 * game.n:
        col_index = clue_index - game.n
        return get_cell_indices_from_col_index(col_index, game.n)[::-1]
    elif clue_index < 3 * game.n:
        row_index = clue_index - 2 * game.n
        return get_cell_indices_from_row_index(row_index, game.n)
    elif clue_index < 4 * game.n:
        row_index = clue_index - 3 * game.n
        return get_cell_indices_from_row_index(row_index, game.n)[::-1]


def get_intersection_from_cell_index(cell_index: int) -> Tuple[int, int]:
    return divmod(cell_index, game.n)


def get_cell_index_from_row_col(row: int, col: int) -> int:
    return row * game.n + col


def get_clue_indices_for_row(row_index: int) -> Tuple[int, int]:
    return (2 * game.n + row_index, 3 * game.n + row_index)


def get_clue_indices_for_col(col_index: int) -> Tuple[int, int]:
    return (col_index, game.n + col_index)
