cimport cython

from .game cimport *
from .pre_compute cimport propagate_intersection_constraints

cdef int ASSIGN_ROW_PERMUTATION = 1
cdef int ASSIGN_COL_PERMUTATION = 2
cdef int NO_ACTION = -1

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.overflowcheck(False)
cdef bint dfs(Game g):
    if g.is_solved():
        return True

    cdef int action, idx
    action, idx = get_most_constrained_line(g)
    if action == NO_ACTION:
        return False

    perms = g.row_permutations[idx] if action == ASSIGN_ROW_PERMUTATION else g.col_permutations[idx]
    for permutation in perms:
        g.save_state()
        if make_assignment_forward_check(g, action, idx, permutation):
            if dfs(g):
                return True
        g.restore_state()
    return False

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.overflowcheck(False)
cdef (int, int) get_most_constrained_line(Game g):
    cdef int i, perm_count, best_count = 2147483647
    cdef int best_idx = -1
    cdef int best_action = NO_ACTION
    
    row_permutations = g.row_permutations
    col_permutations = g.col_permutations
    assigned_rows = g.assigned_rows
    assigned_cols = g.assigned_cols
    
    cdef int row_count = len(row_permutations)
    cdef int col_count = len(col_permutations)

    for i in range(row_count):
        if i not in assigned_rows:
            perm_count = len(row_permutations[i])
            if perm_count == 0:
                return NO_ACTION, -1
            if perm_count == 2:
                return ASSIGN_ROW_PERMUTATION, i
            if 1 < perm_count < best_count:
                best_action = ASSIGN_ROW_PERMUTATION
                best_idx = i
                best_count = perm_count

    for i in range(col_count):
        if i not in assigned_cols:
            perm_count = len(col_permutations[i])
            if perm_count == 0:
                return NO_ACTION, -1
            if perm_count == 2:
                return ASSIGN_COL_PERMUTATION, i
            if 1 < perm_count < best_count:
                best_action = ASSIGN_COL_PERMUTATION
                best_idx = i
                best_count = perm_count
    
    return best_action, best_idx

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.overflowcheck(False)
cdef bint make_assignment_forward_check(Game g, int action, int idx, tuple permutation):
    cdef int col, row, i, n = g.n
    
    row_permutations = g.row_permutations
    col_permutations = g.col_permutations
    assigned_rows = g.assigned_rows
    assigned_cols = g.assigned_cols
    dirty_intersections = g.dirty_intersections
    
    if action == ASSIGN_ROW_PERMUTATION:
        row_permutations[idx] = {permutation}
        assigned_rows.add(idx)
        for col in range(len(col_permutations)):
            dirty_intersections.add((idx, col))
    else:
        col_permutations[idx] = {permutation}
        assigned_cols.add(idx)
        for row in range(len(row_permutations)):
            dirty_intersections.add((row, idx))

    try:
        if not propagate_intersection_constraints(g):
            return False

        for i in range(n):
            if not row_permutations[i] or not col_permutations[i]:
                return False
        return True
    except Exception:
        return False