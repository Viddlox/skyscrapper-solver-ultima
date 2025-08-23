from typing import List, Set, TYPE_CHECKING, Optional
from .grid_manager_cell import get_cell_indices_from_clue_index, get_cross_indices_from_cell_index
from .pre_solve_cell import resolve_and_enqueue, queue_processor

if TYPE_CHECKING:
    from .game import Game


def backtrack(g: "Game") -> bool:
    if not is_valid_state(g.grid_cell, g.n):
        return False
    if g.is_solved():
        return True

    cell_index = get_most_constrained_cell_optimized(g)
    if cell_index is None:
        return False

    values = get_least_constrained_values(cell_index, g)

    for val in values:
        g.save_cell_solve_state()
        try:
            resolve_and_enqueue(cell_index, val, g)
            queue_processor(g)
            if not validate_current_path(g):
                raise Exception("Invalid path")
            if backtrack(g):
                return True
        except Exception:
            pass
        g.restore_cell_solve_state()
    return False


def is_valid_state(grid: List[Set[int]], n: int) -> bool:
    for i in range(n):
        row_vals = set()
        for j in range(n):
            idx = i * n + j
            if len(grid[idx]) == 1:
                val = next(iter(grid[idx]))
                if val in row_vals:
                    return False
                row_vals.add(val)

        col_vals = set()
        for j in range(n):
            idx = j * n + i
            if len(grid[idx]) == 1:
                val = next(iter(grid[idx]))
                if val in col_vals:
                    return False
                col_vals.add(val)
    return True


def get_most_constrained_cell_optimized(g: "Game") -> Optional[int]:
    min_choices = float('inf')
    best_cell = None
    for i, cell in enumerate(g.grid_cell):
        if len(cell) > 1 and i not in g.prefills_cell:
            choice_count = len(cell)
            if choice_count == 2:
                return i
            if choice_count < min_choices:
                min_choices = choice_count
                best_cell = i
    return best_cell


def get_least_constrained_values(cell_index: int, g: "Game") -> List[int]:
    values = list(g.grid_cell[cell_index])

    if len(values) <= 3:
        return values

    def score(val: int) -> int:
        peers = get_cross_indices_from_cell_index(
            cell_index, g.n, g.intersection_cache_cell)
        eliminations = sum(1 for idx in peers if val in g.grid_cell[idx])
        near_solved = sum(1 for idx in peers if len(
            g.grid_cell[idx]) == 2 and val in g.grid_cell[idx])
        return -(eliminations + near_solved * 3)

    return sorted(values, key=score)


def validate_current_path(g: "Game") -> bool:
    for clue_idx, clue in enumerate(g.clues):
        if clue == 0:
            continue

        indices = get_cell_indices_from_clue_index(clue_idx, g.n)
        sequence = []
        for idx in indices:
            if len(g.grid_cell[idx]) != 1:
                break
            sequence.append(next(iter(g.grid_cell[idx])))
        else:
            if count_visible(sequence) != clue:
                return False
    return True


def count_visible(sequence: List[int]) -> int:
    if not sequence:
        return 0
    visible = 1
    tallest = sequence[0]

    for i in range(1, len(sequence)):
        if sequence[i] > tallest:
            visible += 1
            tallest = sequence[i]
    return visible
