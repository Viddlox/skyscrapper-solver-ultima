from typing import List, Set, Deque, DefaultDict
from collections import deque, defaultdict
from dataclasses import dataclass, field

from .input_parser import parse_input
from .pre_solve_perm import initialize_permutations
from .pre_solve_cell import init_edge_clue_constraints, queue_processor
from .backtrack_perm import backtrack
from .backtrack_cell import backtrack as backtrack_cell
from .constants import *


@dataclass
class Game:
    n: int = 0
    full_domain: Tuple[int, ...] = field(default_factory=tuple)
    cell_range: Tuple[int, ...] = field(default_factory=tuple)
    row_permutations: List[Set[Permutation]] = field(default_factory=list)
    col_permutations: List[Set[Permutation]] = field(default_factory=list)
    clues: List[int] = field(default_factory=list)
    prefills: Set[Prefill] = field(default_factory=set)
    queue: Deque[QueueItem] = field(default_factory=deque)
    dirty_intersections: Set[Tuple[int, int]] = field(default_factory=set)
    intersection_cache: DefaultDict[IntersectionKey, bool] = field(
        default_factory=lambda: defaultdict(bool)
    )
    elimination_cache: EliminationCache = field(default_factory=dict)
    assigned_rows: Set[int] = field(default_factory=set)
    assigned_cols: Set[int] = field(default_factory=set)
    decision_stack: List[DecisionPoint] = field(default_factory=list)
    state_snapshots: List[GameState] = field(default_factory=list)
    grid_cell: List[Set[int]] = field(default_factory=list)
    queue_cell: Deque[QueueItem] = field(default_factory=deque)
    intersection_cache_cell: Dict[int,
                                  List[int]] = field(default_factory=dict)
    prefills_cell: Set[int] = field(default_factory=set)
    should_use_cell_solve: bool = False
    cell_state_snapshots: List['CellSolveGameState'] = field(
        default_factory=list)

    def cleanup_caches(self) -> None:
        if len(self.elimination_cache) > MAX_ELIMINATION_CACHE_SIZE:
            recent_keys = list(self.elimination_cache.keys())[-1000:]
            new_cache = {k: self.elimination_cache[k] for k in recent_keys}
            self.elimination_cache = new_cache

        if len(self.intersection_cache) > MAX_INTERSECTION_CACHE_SIZE:
            recent_keys = list(self.intersection_cache.keys())[-1000:]
            new_cache = {k: self.intersection_cache[k] for k in recent_keys}
            self.intersection_cache = new_cache

    def reset(self):
        self.row_permutations = []
        self.col_permutations = []
        self.clues.clear()
        self.n = 0
        self.prefills.clear()
        self.queue.clear()
        self.intersection_cache = defaultdict(bool)
        self.assigned_rows.clear()
        self.assigned_cols.clear()
        self.decision_stack.clear()
        self.state_snapshots.clear()
        self.elimination_cache.clear()
        self.dirty_intersections.clear()
        self.cell_range = ()
        self.full_domain = ()
        self.grid_cell.clear()
        self.queue_cell.clear()
        self.prefills.clear()
        self.intersection_cache_cell = defaultdict(list)
        self.should_use_cell_solve = False
        self.cell_state_snapshots.clear()

    def save_state(self) -> None:
        snapshot = GameState(
            row_permutations=[frozenset(perms)
                              for perms in self.row_permutations],
            col_permutations=[frozenset(perms)
                              for perms in self.col_permutations],
            assigned_rows=frozenset(self.assigned_rows),
            assigned_cols=frozenset(self.assigned_cols),
            queue=self.queue.copy()
        )
        self.state_snapshots.append(snapshot)

    def restore_state(self) -> bool:
        if not self.state_snapshots:
            return False
        snapshot = self.state_snapshots.pop()
        self.row_permutations = [set(perms)
                                 for perms in snapshot.row_permutations]
        self.col_permutations = [set(perms)
                                 for perms in snapshot.col_permutations]
        self.assigned_rows = set(snapshot.assigned_rows)
        self.assigned_cols = set(snapshot.assigned_cols)
        self.queue = snapshot.queue
        return True

    def save_cell_solve_state(self) -> None:
        snapshot = CellSolveGameState(
            grid=[frozenset(cell) for cell in self.grid_cell],
            fixed_cells=frozenset(self.prefills),
            queue=self.queue_cell.copy()
        )
        self.cell_state_snapshots.append(snapshot)

    def restore_cell_solve_state(self) -> bool:
        if not self.cell_state_snapshots:
            return False
        snapshot = self.cell_state_snapshots.pop()
        self.grid_cell = [set(cell) for cell in snapshot.grid]
        self.prefills = set(snapshot.fixed_cells)
        self.queue_cell = snapshot.queue
        return True

    def is_solved(self) -> bool:
        if self.should_use_cell_solve:
            return all(len(cell) == 1 for cell in self.grid_cell)
        return all(len(row_perms) == 1 for row_perms in self.row_permutations)

    def output_grid(self) -> str:
        if self.should_use_cell_solve:
            return '\n'.join(
                ' '.join(
                    str(next(iter(self.grid_cell[i+j]))) for j in range(self.n))
                for i in range(0, len(self.grid_cell), self.n)
            ) + '\n'
        grid = []
        for _, row_perms in enumerate(self.row_permutations):
            if len(row_perms) == 1:
                perm = next(iter(row_perms))
                grid.append(list(perm))
            else:
                grid.append(['?'] * self.n)
        result = []
        for row in grid:
            result.append(' '.join(str(cell) for cell in row))
        return '\n'.join(result) + '\n'

    def set_prefill_cell(self, cell_index: int, value: int) -> None:
        if not (1 <= value <= self.n):
            raise ValueError(f"Invalid value {value} for cell {cell_index}")

        self.grid_cell[cell_index] = {value}
        self.prefills.add(cell_index)

        self.queue_cell.append({
            'type': Actions.PROPAGATE_CONSTRAINTS_FROM_RESOLVED_CELL,
            'cell_index': cell_index
        })

    def constraint_list_factory(self) -> set:
        return set(i + 1 for i in range(self.n))

    def grid_factory(self) -> List[Set[int]]:
        return [self.constraint_list_factory() for _ in range(self.n**2)]

    def start(self, input_clues: str, input_prefill: str) -> str:
        self.reset()
        if not parse_input(self, input_clues, input_prefill):
            return "Bad input argument provided"

        print("\n== Grid Details ==")
        print(f"Grid size: {self.n}x{self.n}")
        print(f"Clues: {self.clues}\n")

        if self.should_use_cell_solve:
            print("Starting pre-solve via cell..\n")
            queue_processor(self)
            init_edge_clue_constraints(self)
            if self.is_solved():
                print("Solved by cell method!")
                return self.output_grid()
            else:
                if backtrack_cell(self):
                    print("Solved by cell method backtracking!")
                    return self.output_grid()
                else:
                    print(
                        "Cell method backtracking failed, trying permutation solver...\n")

        if not initialize_permutations(self):
            print("Starting pre-solve via permutation constraining..\n")
            return "Unsolvable during pre-solve"

        if self.is_solved():
            print("Solved by permutation constraining!")
            return self.output_grid()

        print("\nStarting backtracking...\n")
        if not backtrack(self):
            return "No solution found\n"
        return self.output_grid()
