from typing import TYPE_CHECKING, Tuple
from functools import cache
from itertools import permutations

from .grid_manager import *
from .constants import Actions, PermutationSet, Prefill, PreComputeDebugKey, PreComputeDebugValue

if TYPE_CHECKING:
    from .game import Game


def initialize_permutations(g: "Game", debug=False) -> bool:
    print("Starting pre-computation..")
    for i in range(g.n):
        row_prefill_constraints = tuple(
            (col, val) for row, col, val in g.prefill_cells if row == i
        )
        left_clue, right_clue = get_clues_for_row(g.clues, g.n, i)
        valid_row_perms = generate_permutations(
            g.n, left_clue, right_clue, row_prefill_constraints
        )

        if not valid_row_perms:
            return False
        g.row_permutations.append(valid_row_perms)
        for col_idx in range(g.n):
            g.dirty_intersections.add((i, col_idx))

        col_prefill_constraints = tuple(
            (row, val) for row, col, val in g.prefill_cells if col == i
        )
        top_clue, bottom_clue = get_clues_for_col(g.clues, g.n, i)
        valid_col_perms = generate_permutations(
            g.n, top_clue, bottom_clue, col_prefill_constraints
        )

        if not valid_col_perms:
            return False
        g.col_permutations.append(valid_col_perms)
        for row_idx in range(g.n):
            g.dirty_intersections.add((row_idx, i))

        if debug:
            g.pre_compute_debug_cache[PreComputeDebugKey("ROW", i)] = PreComputeDebugValue(
                left_clue, right_clue, len(valid_row_perms)
            )
            g.pre_compute_debug_cache[PreComputeDebugKey("COL", i)] = PreComputeDebugValue(
                top_clue, bottom_clue, len(valid_col_perms)
            )

    if not propagate_intersection_constraints(g):
        return False

    initialize_propagation_queue(g)
    return True


def propagate_intersection_constraints(g: "Game") -> bool:
    while g.dirty_intersections:
        row_idx, col_idx = g.dirty_intersections.pop()

        row_perms = g.row_permutations[row_idx]
        col_perms = g.col_permutations[col_idx]

        row_values = {perm[col_idx] for perm in row_perms}
        col_values = {perm[row_idx] for perm in col_perms}
        valid_values = row_values & col_values

        if not valid_values:
            return False

        old_row_count = len(row_perms)
        old_col_count = len(col_perms)

        g.row_permutations[row_idx] = {
            perm for perm in row_perms if perm[col_idx] in valid_values
        }
        g.col_permutations[col_idx] = {
            perm for perm in col_perms if perm[row_idx] in valid_values
        }

        if len(g.row_permutations[row_idx]) < old_row_count:
            for col in range(g.n):
                if col != col_idx:
                    g.dirty_intersections.add((row_idx, col))
        if len(g.col_permutations[col_idx]) < old_col_count:
            for row in range(g.n):
                if row != row_idx:
                    g.dirty_intersections.add((row, col_idx))

        if not g.row_permutations[row_idx] or not g.col_permutations[col_idx]:
            return False
    return True


def initialize_propagation_queue(g: "Game") -> None:
    for i in range(g.n):
        if len(g.row_permutations[i]) == 1:
            g.queue.append(
                {"type": Actions.ASSIGN_ROW_PERMUTATION, "index": i})
            g.assigned_rows.add(i)
        if len(g.col_permutations[i]) == 1:
            g.queue.append(
                {"type": Actions.ASSIGN_COL_PERMUTATION, "index": i})
            g.assigned_cols.add(i)


@cache
def generate_permutations(
    n: int, clue: int, opp_clue: int, prefill_constraints: Tuple[Prefill, ...]
) -> PermutationSet:
    full_domain = tuple(range(1, n + 1))
    remaining = tuple(range(1, n))  # used for clue == 1 or opp_clue == 1

    check_prefill = (
        (lambda perm: all(perm[pos] ==
         val for pos, val in prefill_constraints))
        if prefill_constraints else (lambda _: True)
    )

    if clue == 0 and opp_clue == 0:
        return {
            perm for perm in permutations(full_domain)
            if check_prefill(perm)
        }

    if clue == n:
        perm = tuple(range(1, n + 1))
        return {perm} if (opp_clue == 0 or count_visible_reverse(perm) == opp_clue) and check_prefill(perm) else set()

    if opp_clue == n:
        perm = tuple(range(n, 0, -1))
        return {perm} if count_visible_start(perm) == clue and check_prefill(perm) else set()

    if clue == 1:
        return {
            (n,) + perm for perm in permutations(remaining)
            if check_prefill((n,) + perm) and count_visible_reverse((n,) + perm) == opp_clue
        }

    if opp_clue == 1:
        return {
            perm + (n,) for perm in permutations(remaining)
            if check_prefill(perm + (n,)) and count_visible_start(perm + (n,)) == clue
        }

    if opp_clue == 0:
        return {
            perm for perm in permutations(full_domain)
            if check_prefill(perm) and count_visible_start(perm) == clue
        }

    if clue == 0:
        return {
            perm for perm in permutations(full_domain)
            if check_prefill(perm) and count_visible_reverse(perm) == opp_clue
        }

    return {
        perm for perm in permutations(full_domain)
        if check_prefill(perm)
        and count_visible_start(perm) == clue
        and count_visible_reverse(perm) == opp_clue
    }
