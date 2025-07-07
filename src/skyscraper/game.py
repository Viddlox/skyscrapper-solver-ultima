from typing import List, Set, Deque, Tuple, DefaultDict, Union
from collections import deque, defaultdict
from dataclasses import dataclass, field

from .input_parser import parse_input
from .pre_compute import initialize_permutations
from .constants import *


@dataclass
class DecisionPoint:
    decision_type: str
    index: int
    chosen_permutation: Permutation
    eliminated_permutations: PermutationSet


@dataclass
class GameState:
    """Snapshot of game state for restoration"""
    row_permutations: List[PermutationSet]
    col_permutations: List[PermutationSet]
    assigned_rows: Set[int]
    assigned_cols: Set[int]
    queue: Deque[QueueItem]


@dataclass
class ConflictInfo:
    conflict_type: ConflictType
    # row/col index or (row, col) for intersection
    location: Union[int, Tuple[int, int]]
    description: str


@dataclass
class Game:
    row_permutations: List[Set[Permutation]] = field(default_factory=list)
    col_permutations: List[Set[Permutation]] = field(default_factory=list)
    clues: List[int] = field(default_factory=list)
    n: int = 0
    prefill_cells: Set[Prefill] = field(default_factory=set)
    queue: Deque[QueueItem] = field(default_factory=deque)
    permutation_cache: DefaultDict[ClueConstraints, PermutationSet] = field(
        default_factory=lambda: defaultdict(set)
    )
    intersection_cache: DefaultDict[IntersectionKey, bool] = field(
        default_factory=lambda: defaultdict(bool)
    )
    assigned_rows: Set[int] = field(default_factory=set)
    assigned_cols: Set[int] = field(default_factory=set)
    decision_stack: List[DecisionPoint] = field(default_factory=list)
    state_snapshots: List[GameState] = field(default_factory=list)
    conflict_detected: bool = False
    conflict_info: ConflictInfo = None

    def reset(self):
        self.row_permutations.clear()
        self.col_permutations.clear()
        self.clues.clear()
        self.n = 0
        self.prefill_cells.clear()
        self.queue.clear()
        self.permutation_cache.clear()
        self.intersection_cache.clear()
        self.assigned_rows.clear()
        self.assigned_cols.clear()
        self.decision_stack.clear()
        self.state_snapshots.clear()
        self.conflict_detected = False
        self.conflict_info = None

    def save_state(self) -> None:
        """Save current state before making a decision"""
        snapshot = GameState(
            row_permutations=[perms.copy() for perms in self.row_permutations],
            col_permutations=[perms.copy() for perms in self.col_permutations],
            assigned_rows=self.assigned_rows.copy(),
            assigned_cols=self.assigned_cols.copy(),
            queue=self.queue.copy()
        )
        self.state_snapshots.append(snapshot)

    def restore_state(self) -> bool:
        """Restore to previous state, return False if no states to restore"""
        if not self.state_snapshots:
            return False

        snapshot = self.state_snapshots.pop()
        self.row_permutations = snapshot.row_permutations
        self.col_permutations = snapshot.col_permutations
        self.assigned_rows = snapshot.assigned_rows
        self.assigned_cols = snapshot.assigned_cols
        self.queue = snapshot.queue
        self.conflict_detected = False
        self.conflict_info = None
        return True

    def isSolved(self) -> bool:
        return all(len(row_perms) == 1 for row_perms in self.row_permutations)

    def output_grid(self) -> str:
        if not self.isSolved():
            result = []
            for row_idx in range(self.n):
                row_line = []
                for col_idx in range(self.n):
                    possible_values = self.get_constrained_values(
                        row_idx, col_idx)
                    if len(possible_values) == 1:
                        row_line.append(str(next(iter(possible_values))))
                    else:
                        row_line.append(str(possible_values))
                result.append(' '.join(row_line))
            return '\n'.join(result) + '\n'
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

    def get_constrained_values(self, row_idx: int, col_idx: int) -> Set[int]:
        row_values = {perm[col_idx] for perm in self.row_permutations[row_idx]}
        col_values = {perm[row_idx] for perm in self.col_permutations[col_idx]}
        return row_values & col_values

    def start(self, input_clues, input_prefill) -> str:
        self.reset()
        if not parse_input(self, input_clues, input_prefill):
            return "Bad input argument provided"
        initialize_permutations(self)
        return self.output_grid()


game = Game()
