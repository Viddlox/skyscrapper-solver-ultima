from typing import List, Set, Deque, DefaultDict
from collections import deque, defaultdict
from dataclasses import dataclass, field

from .input_parser import parse_input
from .pre_compute import initialize_permutations
from .backtrack import backtrack
from .constants import *


@dataclass
class Game:
    row_permutations: List[Set[Permutation]] = field(default_factory=list)
    col_permutations: List[Set[Permutation]] = field(default_factory=list)
    clues: List[int] = field(default_factory=list)
    n: int = 0
    prefill_cells: Set[Prefill] = field(default_factory=set)
    queue: Deque[QueueItem] = field(default_factory=deque)
    intersection_cache: DefaultDict[IntersectionKey, bool] = field(
        default_factory=lambda: defaultdict(bool)
    )
    elimination_cache: EliminationCache = field(default_factory=dict)
    assigned_rows: Set[int] = field(default_factory=set)
    assigned_cols: Set[int] = field(default_factory=set)
    decision_stack: List[DecisionPoint] = field(default_factory=list)
    state_snapshots: List[GameState] = field(default_factory=list)
    pre_compute_debug_cache: PreComputeDebugCache = field(default_factory=dict)

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
        self.row_permutations.clear()
        self.col_permutations.clear()
        self.clues.clear()
        self.n = 0
        self.prefill_cells.clear()
        self.queue.clear()
        self.intersection_cache.clear()
        self.assigned_rows.clear()
        self.assigned_cols.clear()
        self.decision_stack.clear()
        self.state_snapshots.clear()
        self.elimination_cache.clear()
        self.pre_compute_debug_cache.clear()

    def save_state(self) -> None:
        snapshot = GameState(
            row_permutations=[perms.copy() for perms in self.row_permutations],
            col_permutations=[perms.copy() for perms in self.col_permutations],
            assigned_rows=self.assigned_rows.copy(),
            assigned_cols=self.assigned_cols.copy(),
            queue=self.queue.copy()
        )
        self.state_snapshots.append(snapshot)

    def restore_state(self) -> bool:
        if not self.state_snapshots:
            return False

        snapshot = self.state_snapshots.pop()
        self.row_permutations = snapshot.row_permutations
        self.col_permutations = snapshot.col_permutations
        self.assigned_rows = snapshot.assigned_rows
        self.assigned_cols = snapshot.assigned_cols
        self.queue = snapshot.queue
        return True

    def isSolved(self) -> bool:
        return all(len(row_perms) == 1 for row_perms in self.row_permutations)

    def output_grid(self) -> str:
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

    def start(self, input_clues: str, input_prefill: str, debug=False) -> str:
        self.reset()
        if not parse_input(self, input_clues, input_prefill):
            return "Bad input argument provided"            
        
        if not initialize_permutations(self, debug):
            return "Unsolvable during pre-computation"
        
        if debug:
            print("\n== Pre-computation Summary ==")
            print(f"Grid size: {self.n}x{self.n}")
            print(f"Clues: {self.clues}\n")

            print(f"{'Line':<4} | {'Idx':^3} | {'Clues (Start-End)':^17} | {'Pruned From → To':^18} | {'Reduction':>9}")
            print("-" * 65)

            for i in range(self.n):
                for line_type in ["ROW", "COL"]:
                    key = PreComputeDebugKey(line_type, i)
                    info = self.pre_compute_debug_cache.get(key)
                    if not info:
                        continue
                    current_len = len(self.row_permutations[i]) if line_type == "ROW" else len(self.col_permutations[i])
                    reduction_pct = 100.0 * (1 - current_len / info.prevCount) if info.prevCount else 0.0
                    print(f"{line_type:<4} | {i:^3} | ({info.clue_start},{info.clue_end}){'':<12} | {info.prevCount:>6} → {current_len:<5} | {reduction_pct:>8.1f}%")

        if self.isSolved():
            print("Solved by pre-computation!")
            return self.output_grid()
        
        print("\nStarting backtracking...\n")
        if not backtrack(self):
            return "No solution found"
        return self.output_grid()
