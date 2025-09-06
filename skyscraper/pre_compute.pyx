from functools import cache
from itertools import permutations
from .game cimport Game
cimport cython

from .grid_manager cimport *

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.overflowcheck(False)
cdef bint initialize_permutations(Game g):
    cdef int i, col_idx, row_idx, n = g.n
    cdef int left_clue, right_clue, top_clue, bottom_clue
    
    g.full_domain = tuple(range(1, n + 1))
    g.cell_range = tuple(range(1, n))

    clues = g.clues
    prefills = g.prefills
    full_domain = g.full_domain
    cell_range = g.cell_range
    row_permutations = g.row_permutations
    col_permutations = g.col_permutations
    dirty_intersections = g.dirty_intersections

    for i in range(n):
        row_prefill_list = []
        for row, col, val in prefills:
            if row == i:
                row_prefill_list.append((col, val))
        row_prefill_constraints = tuple(sorted(row_prefill_list))
        
        left_clue, right_clue = get_clues_for_row(clues, n, i)
        valid_row_perms = generate_permutations(
            n, full_domain, cell_range, left_clue, right_clue, row_prefill_constraints
        )

        if not valid_row_perms:
            return False
        row_permutations.append(valid_row_perms)
        
        for col_idx in range(n):
            dirty_intersections.add((i, col_idx))

        col_prefill_list = []
        for row, col, val in prefills:
            if col == i:
                col_prefill_list.append((row, val))
        col_prefill_constraints = tuple(sorted(col_prefill_list))
        
        top_clue, bottom_clue = get_clues_for_col(clues, n, i)
        valid_col_perms = generate_permutations(
            n, full_domain, cell_range, top_clue, bottom_clue, col_prefill_constraints
        )

        if not valid_col_perms:
            return False
        col_permutations.append(valid_col_perms)
        
        for row_idx in range(n):
            dirty_intersections.add((row_idx, i))

    return propagate_intersection_constraints(g)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.overflowcheck(False)
cdef bint propagate_intersection_constraints(Game g):
    cdef int row_idx, col_idx, old_row_count, old_col_count
    cdef int col, row, n = g.n
    
    dirty_intersections = g.dirty_intersections
    row_permutations = g.row_permutations
    col_permutations = g.col_permutations
    
    while dirty_intersections:
        row_idx, col_idx = dirty_intersections.pop()

        row_perms = row_permutations[row_idx]
        col_perms = col_permutations[col_idx]

        valid_values = {perm[col_idx] for perm in row_perms} & {perm[row_idx] for perm in col_perms}

        if not valid_values:
            return False

        old_row_count = len(row_perms)
        old_col_count = len(col_perms)

        row_permutations[row_idx] = {
            perm for perm in row_perms if perm[col_idx] in valid_values
        }
        col_permutations[col_idx] = {
            perm for perm in col_perms if perm[row_idx] in valid_values
        }

        if len(row_permutations[row_idx]) < old_row_count:
            for col in range(n):
                if col != col_idx:
                    dirty_intersections.add((row_idx, col))
        if len(col_permutations[col_idx]) < old_col_count:
            for row in range(n):
                if row != row_idx:
                    dirty_intersections.add((row, col_idx))

        if not row_permutations[row_idx] or not col_permutations[col_idx]:
            return False

    return True

@cache
def generate_permutations(int n, tuple full_domain, tuple cell_range, int clue, int opp_clue, tuple prefill_constraints):
    cdef int perm_len = len(prefill_constraints)

    if perm_len > 0:
        return resolve_prefilled_permutations(
            n, full_domain, clue, opp_clue, prefill_constraints
        )

    if clue == 0 and opp_clue == 0:
        return {
            perm for perm in permutations(full_domain)
        }

    if clue == n:
        perm = tuple(range(1, n + 1))
        return {perm} if (opp_clue == 0 or count_visible_reverse(perm, opp_clue)) else set()

    if opp_clue == n:
        perm = tuple(range(n, 0, -1))
        return {perm} if count_visible_start(perm, clue) else set()

    if clue == 1:
        valid_perms = set()
        for perm in permutations(cell_range):
            full_perm = (n,) + perm
            if count_visible_reverse(full_perm, opp_clue):
                valid_perms.add(full_perm)
        return valid_perms

    if opp_clue == 1:
        valid_perms = set()
        for perm in permutations(cell_range):
            full_perm = perm + (n,)
            if count_visible_start(full_perm, clue):
                valid_perms.add(full_perm)
        return valid_perms

    if opp_clue == 0:
        valid_perms = set()
        for perm in permutations(full_domain):
            if count_visible_start(perm, clue):
                valid_perms.add(perm)
        return valid_perms

    if clue == 0:
        valid_perms = set()
        for perm in permutations(full_domain):
            if count_visible_reverse(perm, opp_clue):
                valid_perms.add(perm)
        return valid_perms

    valid_perms = set()
    for perm in permutations(full_domain):
        if count_visible_start(perm, clue) and count_visible_reverse(perm, opp_clue):
            valid_perms.add(perm)
    return valid_perms

@cache
def resolve_prefilled_permutations(int n, tuple full_domain, int clue, int opp_clue, tuple prefill_constraints):
    cdef int pos, val, i
    cdef int perm_len = len(prefill_constraints)
    cdef int free_pos_len, avail_vals_len
    
    template = [None] * n
    used_values = set()

    for i in range(perm_len):
        pos, val = prefill_constraints[i]
        template[pos] = val
        used_values.add(val)

    free_positions = []
    for i in range(n):
        if template[i] is None:
            free_positions.append(i)
    
    available_values = []
    for v in full_domain:
        if v not in used_values:
            available_values.append(v)
    available_values = tuple(available_values)

    free_pos_len = len(free_positions)
    avail_vals_len = len(available_values)

    if avail_vals_len != free_pos_len:
        return set()

    if clue == 0 and opp_clue == 0:
        curr_perm = template[:]
        valid_perms = set()
        for perm_values in permutations(available_values):
            for i in range(free_pos_len):
                curr_perm[free_positions[i]] = perm_values[i]
            valid_perms.add(tuple(curr_perm))
        return valid_perms

    curr_perm = template[:]
    valid_perms = set()

    for perm_values in permutations(available_values):
        for i in range(free_pos_len):
            curr_perm[free_positions[i]] = perm_values[i]
        
        curr_tuple = tuple(curr_perm)
        if count_visible_start(curr_tuple, clue) and count_visible_reverse(curr_tuple, opp_clue):
            valid_perms.add(curr_tuple)

    return valid_perms