from typing import TYPE_CHECKING, Tuple, Optional, Set, List
from .grid_manager_perm import *
from .constants import Actions, Permutation
from .pre_solve_perm import propagate_intersection_constraints

if TYPE_CHECKING:
    from .game import Game


def backtrack(g: "Game") -> bool:
    if g.is_solved():
        return True

    action, idx = get_most_constrained_line(g)
    if action is None:
        return False

    perms = g.row_permutations[idx] if action == Actions.ASSIGN_ROW_PERMUTATION else g.col_permutations[idx]
    sorted_perms = get_least_constrained_perms(g, action, perms)

    for permutation in sorted_perms:
        g.save_state()
        if make_assignment_forward_check(g, action, idx, permutation):
            if backtrack(g):
                return True
        g.restore_state()
    return False

def get_most_constrained_line(g: "Game") -> Tuple[Optional[Actions], Optional[int]]:
    best_action, best_idx, best_count = None, None, float('inf')

    for i, perms in enumerate(g.row_permutations):
        if i not in g.assigned_rows:
            perm_count = len(perms)
            if perm_count == 0:
                return None, None
            if perm_count == 2:
                return Actions.ASSIGN_ROW_PERMUTATION, i
            if 1 < perm_count < best_count:
                best_action, best_idx, best_count = Actions.ASSIGN_ROW_PERMUTATION, i, perm_count

    for i, perms in enumerate(g.col_permutations):
        if i not in g.assigned_cols:
            perm_count = len(perms)
            if perm_count == 0:
                return None, None
            if perm_count == 2:
                return Actions.ASSIGN_COL_PERMUTATION, i
            if 1 < perm_count < best_count:
                best_action, best_idx, best_count = Actions.ASSIGN_COL_PERMUTATION, i, perm_count
    return best_action, best_idx


def get_least_constrained_perms(g: "Game", action: Actions, perms: Set[Permutation]) -> List[Permutation]:
    def score(_: Permutation) -> int:
        total = 0
        if action == Actions.ASSIGN_ROW_PERMUTATION:
            for col_idx in range(g.n):
                if col_idx not in g.assigned_cols:
                    total += len(g.col_permutations[col_idx])
        else:
            for row_idx in range(g.n):
                if row_idx not in g.assigned_rows:
                    total += len(g.row_permutations[row_idx])
        return total
    perm_list = list(perms)
    if len(perm_list) <= 3:
        return perm_list
    return sorted(perm_list, key=score)


def make_assignment_forward_check(g: "Game", action: Actions, idx: int, permutation: Permutation) -> bool:
    if action == Actions.ASSIGN_ROW_PERMUTATION:
        g.row_permutations[idx] = {permutation}
        g.assigned_rows.add(idx)
        g.queue.append({"type": action, "index": idx})
        for col in range(len(g.col_permutations)):
            g.dirty_intersections.add((idx, col))
    else:
        g.col_permutations[idx] = {permutation}
        g.assigned_cols.add(idx)
        g.queue.append({"type": action, "index": idx})
        for row in range(len(g.row_permutations)):
            g.dirty_intersections.add((row, idx))

    try:
        success = propagate_intersection_constraints(g)
        if not success:
            return False
        for i in range(g.n):
            if not g.row_permutations[i] or not g.col_permutations[i]:
                return False
        return True
    except Exception:
        return False
