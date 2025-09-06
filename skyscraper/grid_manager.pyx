cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple get_clue_indices_for_row(int n, int row_index):
    return 2 * n + row_index, 3 * n + row_index

@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple get_clue_indices_for_col(int n, int col_index):
    return col_index, n + col_index

@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple get_clues_for_row(object clues, int n, int row_index):
    cdef int left_idx, right_idx
    left_idx, right_idx = get_clue_indices_for_row(n, row_index)
    return clues[left_idx], clues[right_idx]

@cython.boundscheck(False)
@cython.wraparound(False)
cdef tuple get_clues_for_col(object clues, int n, int col_index):
    cdef int top_idx, bottom_idx
    top_idx, bottom_idx = get_clue_indices_for_col(n, col_index)
    return clues[top_idx], clues[bottom_idx]

@cython.boundscheck(False)
@cython.wraparound(False)
cdef bint count_visible_start(tuple perm, int target):
    if target <= 0:
        return target == 0

    cdef int visible = 0
    cdef int max_height = 0
    cdef int height
    cdef int i, n = len(perm)

    for i in range(n):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
            if visible > target:
                return False
    return visible == target


@cython.boundscheck(False)
@cython.wraparound(False)
cdef bint count_visible_reverse(tuple perm, int target):
    if target <= 0:
        return target == 0

    cdef int visible = 0
    cdef int max_height = 0
    cdef int height
    cdef int i, n = len(perm)

    for i in range(n - 1, -1, -1):
        height = perm[i]
        if height > max_height:
            visible += 1
            max_height = height
            if visible > target:
                return False
    return visible == target

