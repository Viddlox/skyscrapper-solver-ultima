from typing import TYPE_CHECKING
from functools import cache
from itertools import permutations

from .grid_manager import *
from .constants import Actions, PermutationSet, Prefill, PreComputeDebugKey, PreComputeDebugValue, IntersectionConstraints
if TYPE_CHECKING:
    from .game import Game


def initialize_permutations(g: "Game", debug=False) -> bool:
    print("Starting pre-computation..")
    for i in range(g.n):
        row_prefill_constraints = tuple(
            (col, val) for row, col, val in g.prefill_cells if row == i
        )
        row_intersection_constraints = tuple(
            (col_idx, frozenset({perm[i] for perm in g.col_permutations[col_idx]}))
            for col_idx in range(len(g.col_permutations))
            if g.col_permutations[col_idx]
        )
        left_clue, right_clue = get_clues_for_row(g.clues, g.n, i)

        valid_row_perms = generate_permutations(
            g.n, left_clue, right_clue, row_prefill_constraints, row_intersection_constraints)

        if not valid_row_perms:
            return False
        g.row_permutations.append(valid_row_perms)
        
        for col_idx in range(len(g.col_permutations)):
            g.dirty_intersections.add((i, col_idx))

        if not propagate_intersection_constraints(g):
            return False

        col_prefill_constraints = tuple(
            (row, val) for row, col, val in g.prefill_cells if col == i
        )
        col_intersection_constraints = tuple(
            (row_idx, frozenset({perm[i] for perm in g.row_permutations[row_idx]}))
            for row_idx in range(len(g.row_permutations))
            if g.row_permutations[row_idx]
        )
        top_clue, bottom_clue = get_clues_for_col(g.clues, g.n, i)
        valid_col_perms = generate_permutations(
            g.n, top_clue, bottom_clue, col_prefill_constraints, col_intersection_constraints)

        if not valid_col_perms:
            return False
        g.col_permutations.append(valid_col_perms)
        
        for row_idx in range(len(g.row_permutations)):
            g.dirty_intersections.add((row_idx, i))

        if not propagate_intersection_constraints(g):
            return False

        if debug:
            row_debug_cache_key = PreComputeDebugKey("ROW", i)
            g.pre_compute_debug_cache[row_debug_cache_key] = PreComputeDebugValue(
                left_clue, right_clue, len(valid_row_perms))
            col_debug_cache_key = PreComputeDebugKey("COL", i)
            g.pre_compute_debug_cache[col_debug_cache_key] = PreComputeDebugValue(
                top_clue, bottom_clue, len(valid_col_perms))

    if not propagate_intersection_constraints(g):
        return False

    initialize_propagation_queue(g)
    return True


def propagate_intersection_constraints(g: "Game") -> bool:
    while g.dirty_intersections:
        row_idx, col_idx = g.dirty_intersections.pop()

        row_values = {perm[col_idx] for perm in g.row_permutations[row_idx]}
        col_values = {perm[row_idx] for perm in g.col_permutations[col_idx]}
        valid_values = row_values & col_values

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

        # if row of row_idx changed, then ALL intersections in row or col may be affected
        if len(g.row_permutations[row_idx]) < old_row_count:
            for col in range(len(g.col_permutations)):
                if col != col_idx:
                    g.dirty_intersections.add((row_idx, col))
        if len(g.col_permutations[col_idx]) < old_col_count:
            for row in range(len(g.row_permutations)):
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


def satisfies_prefill(perm: tuple, prefill_constraints: Tuple[Prefill, ...]) -> bool:
    for pos, val in prefill_constraints:
        if perm[pos] != val:
            return False
    return True


def satisfies_intersection_constraints(perm: tuple, intersection_constraints: IntersectionConstraints = ()) -> bool:
    for pos, valid_values in intersection_constraints:
        if perm[pos] not in valid_values:
            return False
    return True


@cache
def generate_permutations(n: int, clue: int, opp_clue: int,
                          prefill_constraints: Tuple[Prefill, ...],
                          intersection_constraints: IntersectionConstraints = ()) -> "PermutationSet":
    if clue == 1:
        remaining = list(range(1, n))
        valid_perms = set()
        for perm in permutations(remaining):
            full_perm = (n,) + perm
            if (count_visible_reverse(full_perm) == opp_clue and
                    satisfies_prefill(full_perm, prefill_constraints) and
                    satisfies_intersection_constraints(full_perm, intersection_constraints)):
                valid_perms.add(full_perm)
        return valid_perms

    if clue == n:
        perm = tuple(range(1, n + 1))
        if (count_visible_reverse(perm) == opp_clue and
                satisfies_prefill(perm, prefill_constraints) and
                satisfies_intersection_constraints(perm, intersection_constraints)):
            return {perm}
        return set()

    if opp_clue == 1:
        remaining = list(range(1, n))
        valid_perms = set()
        for perm in permutations(remaining):
            full_perm = perm + (n,)
            if (count_visible_start(full_perm) == clue and
                    satisfies_prefill(full_perm, prefill_constraints) and
                    satisfies_intersection_constraints(full_perm, intersection_constraints)):
                valid_perms.add(full_perm)
        return valid_perms

    if opp_clue == n:
        perm = tuple(range(n, 0, -1))
        if (count_visible_start(perm) == clue and
                satisfies_prefill(perm, prefill_constraints) and
                satisfies_intersection_constraints(perm, intersection_constraints)):
            return {perm}
        return set()

    valid_perms = set()
    for perm in permutations(range(1, n + 1)):
        if (count_visible_start(perm) == clue and
                count_visible_reverse(perm) == opp_clue and
                satisfies_prefill(perm, prefill_constraints) and
                satisfies_intersection_constraints(perm, intersection_constraints)):
            valid_perms.add(perm)
    return valid_perms
