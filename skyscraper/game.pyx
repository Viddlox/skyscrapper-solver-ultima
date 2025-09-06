cimport cython

cdef class GameState:
    def __init__(self, list row_permutations, list col_permutations, 
                 frozenset assigned_rows, frozenset assigned_cols):
        self.row_permutations = row_permutations
        self.col_permutations = col_permutations
        self.assigned_rows = assigned_rows
        self.assigned_cols = assigned_cols


cdef class Game:
    cdef void save_state(self)
    cdef bint restore_state(self)
    cdef bint is_solved(self)
    cdef str output_grid(self)
    cdef bint parse_input(self, str input_clues, str input_prefill)
    cdef void process_prefilled_cells(self, list input_prefill)
    
    def __init__(self):
        self.n = 0
        self.full_domain = ()
        self.cell_range = ()
        self.row_permutations = []
        self.col_permutations = []
        self.clues = []
        self.prefills = set()
        self.dirty_intersections = set()
        self.assigned_rows = set()
        self.assigned_cols = set()
        self.state_snapshots = []

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef void reset(self):
        self.row_permutations = []
        self.col_permutations = []
        self.clues = []
        self.n = 0
        self.prefills = set()
        self.assigned_rows = set()
        self.assigned_cols = set()
        self.state_snapshots = []
        self.dirty_intersections = set()
        self.cell_range = ()
        self.full_domain = ()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef void save_state(self):
        cdef GameState snapshot = GameState(
            [frozenset(perms) for perms in self.row_permutations],
            [frozenset(perms) for perms in self.col_permutations],
            frozenset(self.assigned_rows),
            frozenset(self.assigned_cols)
        )
        self.state_snapshots.append(snapshot)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef bint restore_state(self):
        if not self.state_snapshots:
            return False
        cdef GameState snapshot = self.state_snapshots.pop()
        self.row_permutations = [set(perms) for perms in snapshot.row_permutations]
        self.col_permutations = [set(perms) for perms in snapshot.col_permutations]
        self.assigned_rows = set(snapshot.assigned_rows)
        self.assigned_cols = set(snapshot.assigned_cols)
        return True

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef bint is_solved(self):
        cdef int i
        for i in range(len(self.row_permutations)):
            if len(self.row_permutations[i]) != 1:
                return False
        return True

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef str output_grid(self):
        cdef list grid = []
        cdef tuple perm
        cdef int i
        for i in range(len(self.row_permutations)):
            row_perms = self.row_permutations[i]
            if len(row_perms) == 1:
                perm = next(iter(row_perms))
                grid.append(list(perm))
            else:
                grid.append(['?'] * self.n)
        cdef list result = []
        for row in grid:
            result.append(' '.join(str(cell) for cell in row))
        return '\n'.join(result) + '\n'

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.cdivision(True)
    @cython.overflowcheck(False)
    cdef bint parse_input(self, str input_clues, str input_prefill):
        if not input_clues.strip():
            return False
        
        cdef str clean_input
        cdef list clues
        cdef int n, max_clue_count = 0
        cdef int clue, i
        cdef int clues_len
        
        try:
            clean_input = input_clues.replace(" ", "")
            clues = [int(char) for char in clean_input]
        except ValueError:
            return False

        clues_len = len(clues)
        if clues_len % 4 != 0 or clues_len < 8:
            return False

        n = clues_len // 4
        
        for i in range(clues_len):
            clue = clues[i]
            if not (0 <= clue <= n):
                return False
            if clue == n:
                max_clue_count += 1
                if max_clue_count > 2:
                    return False

        self.clues = clues
        self.n = n

        if input_prefill.strip():
            try:
                self.process_prefilled_cells(input_prefill.strip().split())
            except ValueError:
                return False
        return True

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.cdivision(True)
    @cython.overflowcheck(False)
    cdef void process_prefilled_cells(self, list input_prefill):
        cdef str curr
        cdef list parts
        cdef int row, col, val
        cdef int i, parts_len
        cdef int n = self.n
        
        for i in range(len(input_prefill)):
            curr = input_prefill[i]
            parts = curr.split(',')
            parts_len = len(parts)
            
            if parts_len != 3:
                raise ValueError(f"Invalid prefill format: {curr}")
            
            try:
                row = int(parts[0])
                col = int(parts[1]) 
                val = int(parts[2])
            except ValueError:
                raise ValueError(f"Invalid prefill values: {curr}")
            
            if not (1 <= row <= n and 1 <= col <= n):
                raise ValueError(f"Coordinates out of bounds: {curr}")
            if not (1 <= val <= n):
                raise ValueError(f"Invalid cell value: {curr}")
            
            row -= 1
            col -= 1
            self.prefills.add((row, col, val))