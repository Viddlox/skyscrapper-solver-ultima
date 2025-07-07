from typing import TYPE_CHECKING, Tuple, Optional
from .grid_manager import *
from .constants import Actions, Permutation, DecisionPoint
from .pre_compute import propagate_intersection_constraints

if TYPE_CHECKING:
    from .game import Game


def backtrack(g: "Game") -> bool:
    """Main backtracking algorithm with MCV, LCV, and forward checking"""
    if g.isSolved():
        return True
    
    # Periodic cache cleanup for long searches
    if len(g.decision_stack) % 100 == 0:
        g.cleanup_caches()

    # Most Constrained Variable (MCV) heuristic
    line_type, line_idx = get_most_constrained_line(g)
    if line_type is None:
        return False

    # Get permutations for this line
    perms = g.row_permutations[line_idx] if line_type == "row" else g.col_permutations[line_idx]

    # Sort permutations by Least Constraining Value (LCV) heuristic
    sorted_perms = sorted(perms, key=lambda perm: count_potential_eliminations(
        g, line_type, line_idx, perm))

    for permutation in sorted_perms:
        # Save state before making assignment
        g.save_state()

        # Make assignment with forward checking
        if make_assignment_forward_check(g, line_type, line_idx, permutation):
            # Record decision for backtracking
            eliminated = perms - {permutation}
            decision = DecisionPoint(
                line_type, line_idx, permutation, eliminated)
            g.decision_stack.append(decision)

            # Recursive call
            if backtrack(g):
                return True

            # Backtrack: remove decision and restore state
            g.decision_stack.pop()

        # Restore state (whether assignment failed or recursive call failed)
        g.restore_state()

    return False

def get_most_constrained_line(g: "Game") -> Tuple[Optional[str], Optional[int]]:
    best_type, best_idx, best_count = None, None, float('inf')
    for i, perms in enumerate(g.row_permutations):
        if i not in g.assigned_rows:
            perm_count = len(perms)
            if 1 < perm_count < best_count:
                best_type, best_idx, best_count = "row", i, perm_count
    
    for i, perms in enumerate(g.col_permutations):
        if i not in g.assigned_cols:
            perm_count = len(perms)
            if 1 < perm_count < best_count:
                best_type, best_idx, best_count = "col", i, perm_count
    return best_type, best_idx


def count_potential_eliminations(g: "Game", decision_type: str, idx: int, permutation: Permutation) -> int:
    # Create cache key for this elimination calculation
    cache_key = (decision_type, idx, permutation, get_game_state_hash(g))

    # Check cache first
    if cache_key in g.elimination_cache:
        return g.elimination_cache[cache_key]

    elimination_count = 0

    if decision_type == "row":
        # Count eliminations in intersecting columns
        for col_idx in range(g.n):
            required_value = permutation[col_idx]
            # Count how many column permutations would be eliminated
            for col_perm in g.col_permutations[col_idx]:
                if col_perm[idx] != required_value:
                    elimination_count += 1
    else:  # decision_type == "col"
        # Count eliminations in intersecting rows
        for row_idx in range(g.n):
            required_value = permutation[row_idx]
            # Count how many row permutations would be eliminated
            for row_perm in g.row_permutations[row_idx]:
                if row_perm[idx] != required_value:
                    elimination_count += 1

    # Cache the result
    g.elimination_cache[cache_key] = elimination_count
    return elimination_count


def get_game_state_hash(g: "Game") -> int:
    row_sizes = tuple(len(perms) for perms in g.row_permutations)
    col_sizes = tuple(len(perms) for perms in g.col_permutations)
    return hash((row_sizes, col_sizes))


def get_least_constraining_permutation(g: "Game", decision_type: str, idx: int) -> Permutation:
    perms = g.row_permutations[idx] if decision_type == "row" else g.col_permutations[idx]

    if not perms:
        return None

    best_perm = None
    least_eliminations = float('inf')

    for perm in perms:
        eliminations = count_potential_eliminations(
            g, decision_type, idx, perm)
        if eliminations < least_eliminations:
            least_eliminations = eliminations
            best_perm = perm

    return best_perm


def make_assignment_forward_check(g: "Game", decision_type: str, idx: int, permutation: Permutation) -> bool:
    """
    Make assignment and perform forward checking via constraint propagation.
    Uses existing intersection constraint system for maximum efficiency.
    """
    # Make the assignment
    if decision_type == "row":
        g.row_permutations[idx] = {permutation}
        g.assigned_rows.add(idx)
        # Add to queue for propagation
        g.queue.append({"type": Actions.ASSIGN_ROW_PERMUTATION, "index": idx})
    else:
        g.col_permutations[idx] = {permutation}
        g.assigned_cols.add(idx)
        # Add to queue for propagation
        g.queue.append({"type": Actions.ASSIGN_COL_PERMUTATION, "index": idx})

    # Forward checking: propagate constraints and detect conflicts early
    try:
        success = propagate_intersection_constraints(g)
        if not success:
            return False

        # Additional forward checking: ensure no empty permutation sets
        for i in range(g.n):
            if not g.row_permutations[i] or not g.col_permutations[i]:
                return False

        return True
    except Exception:
        # Any exception during propagation indicates a conflict
        return False