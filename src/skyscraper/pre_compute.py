from typing import TYPE_CHECKING
from itertools import permutations

from .grid_manager import *
from .constants import Actions
if TYPE_CHECKING:
    from .constants import PermutationSet
    from .game import Game


def initialize_permutations(g: "Game") -> None:
    for i in range(g.n):
        left_clue, right_clue = get_clues_for_row(g.clues, g.n, i)
        valid_row_perms = generate_permutations(g.n, left_clue, right_clue)
        g.row_permutations.append(valid_row_perms)

        top_clue, bottom_clue = get_clues_for_col(g.clues, g.n, i)
        valid_col_perms = generate_permutations(g.n, top_clue, bottom_clue)
        g.col_permutations.append(valid_col_perms)
    apply_prefill_constraints(g)
    propagate_intersection_constraints(g)
    initialize_propagation_queue(g)

def initialize_propagation_queue(g: "Game") -> None:
    """Add solved lines to queue for further propagation"""
    for i in range(g.n):
        if len(g.row_permutations[i]) == 1:
            g.queue.append(
                {"type": Actions.ASSIGN_ROW_PERMUTATION, "index": i})
            g.assigned_rows.add(i)

        if len(g.col_permutations[i]) == 1:
            g.queue.append(
                {"type": Actions.ASSIGN_COL_PERMUTATION, "index": i})
            g.assigned_cols.add(i)


def apply_prefill_constraints(g: "Game") -> None:
    """Apply prefilled cells to eliminate incompatible permutations"""
    for row, col, value in g.prefill_cells:
        g.row_permutations[row] = {
            perm for perm in g.row_permutations[row]
            if perm[col] == value
        }
        g.col_permutations[col] = {
            perm for perm in g.col_permutations[col]
            if perm[row] == value
        }


def propagate_intersection_constraints(g: "Game") -> None:
    """Apply intersection constraints after initial generation"""
    changed = True
    while changed:
        changed = False
        for row_idx in range(g.n):
            for col_idx in range(g.n):
                row_values = {perm[col_idx]
                              for perm in g.row_permutations[row_idx]}
                col_values = {perm[row_idx]
                              for perm in g.col_permutations[col_idx]}
                valid_values = row_values & col_values
                # Filter incompatible permutations
                old_row_count = len(g.row_permutations[row_idx])
                old_col_count = len(g.col_permutations[col_idx])
                g.row_permutations[row_idx] = {
                    perm for perm in g.row_permutations[row_idx]
                    if perm[col_idx] in valid_values
                }
                g.col_permutations[col_idx] = {
                    perm for perm in g.col_permutations[col_idx]
                    if perm[row_idx] in valid_values
                }
                if (len(g.row_permutations[row_idx]) < old_row_count or
                        len(g.col_permutations[col_idx]) < old_col_count):
                    changed = True

def generate_permutations(n: int, clue: int, opp_clue: int) -> "PermutationSet":
    if clue == 1:
        remaining = list(range(1, n))
        return {(n,) + perm for perm in permutations(remaining)
                if count_visible_reverse((n,) + perm) == opp_clue}
    if clue == n:
        perm = tuple(range(1, n + 1))
        return {perm} if count_visible_reverse(perm) == opp_clue else set()
    if opp_clue == 1:
        remaining = list(range(1, n))
        return {perm + (n,) for perm in permutations(remaining)
                if count_visible_start(perm + (n,)) == clue}
    if opp_clue == n:
        perm = tuple(range(n, 0, -1))
        return {perm} if count_visible_start(perm) == clue else set()

    valid_perms = set()
    for perm in permutations(range(1, n + 1)):
        if (count_visible_start(perm) == clue and
                count_visible_reverse(perm) == opp_clue):
            valid_perms.add(perm)
    return valid_perms
