cdef class GameState:
    cdef list row_permutations
    cdef list col_permutations
    cdef frozenset assigned_rows
    cdef frozenset assigned_cols


cdef class Game:
    cdef int n
    cdef tuple full_domain
    cdef tuple cell_range
    cdef list row_permutations
    cdef list col_permutations
    cdef list clues
    cdef set prefills
    cdef set dirty_intersections
    cdef set assigned_rows
    cdef set assigned_cols
    cdef list state_snapshots

    cdef void reset(self)
    cdef void save_state(self)
    cdef bint restore_state(self)
    cdef bint is_solved(self)
    cdef str output_grid(self)
    cdef bint parse_input(self, str input_clues, str input_prefill)
    cdef void process_prefilled_cells(self, list input_prefill)
