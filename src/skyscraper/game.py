from typing import List, Set
from dataclasses import dataclass, field

from .input_parser import parse_input
from .pre_compute import initialize_permutations
from .backtrack import dfs
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
    dirty_intersections: Set[Tuple[int, int]] = field(default_factory=set)
    assigned_rows: Set[int] = field(default_factory=set)
    assigned_cols: Set[int] = field(default_factory=set)
    state_snapshots: List[GameState] = field(default_factory=list)

    def reset(self):
        self.row_permutations = []
        self.col_permutations = []
        self.clues.clear()
        self.n = 0
        self.prefills.clear()
        self.assigned_rows.clear()
        self.assigned_cols.clear()
        self.state_snapshots.clear()
        self.dirty_intersections.clear()
        self.cell_range = ()
        self.full_domain = ()

    def save_state(self) -> None:
        snapshot = GameState(
            row_permutations=[frozenset(perms)
                              for perms in self.row_permutations],
            col_permutations=[frozenset(perms)
                              for perms in self.col_permutations],
            assigned_rows=frozenset(self.assigned_rows),
            assigned_cols=frozenset(self.assigned_cols),
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
        return True

    def is_solved(self) -> bool:
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

    def constraint_list_factory(self) -> set:
        return set(i + 1 for i in range(self.n))

    def grid_factory(self) -> List[Set[int]]:
        return [self.constraint_list_factory() for _ in range(self.n**2)]

    def start(self, input_clues: str, input_prefill: str) -> str:
        self.reset()
        if not parse_input(self, input_clues, input_prefill):
            return "Bad input argument provided"

        print(f"\nGrid size: {self.n}x{self.n}\n")
        print(f"Clues: {self.clues}\n")

        if not initialize_permutations(self):
            print("Starting pre-compute via permutation filtration..\n")
            return "Unsolvable during pre-compute"

        if self.is_solved():
            print("Solved by permutation filtration!")
            return self.output_grid()

        print("\nStarting backtracking...\n")
        if not dfs(self):
            return "No solution found\n"
        print("Solved by backtracking")
        return self.output_grid()
