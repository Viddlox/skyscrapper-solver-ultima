from typing import List, Set, Deque, Tuple, TypedDict, DefaultDict
from collections import deque, defaultdict
from enum import Enum
from dataclasses import dataclass, field

from .input_parser import parse_input

class Actions(Enum):
    PROPAGATE_ROW_CONSTRAINTS = 1
    PROPAGATE_COL_CONSTRAINTS = 2
    ASSIGN_ROW_PERMUTATION = 3
    ASSIGN_COL_PERMUTATION = 4


class QueueItem(TypedDict):
    type: Actions
    index: int


@dataclass
class Game:
    row_permutations: List[Set[Tuple[int, ...]]] = field(default_factory=list)
    col_permutations: List[Set[Tuple[int, ...]]] = field(default_factory=list)
    clues: List[int] = field(default_factory=list)
    n: int = 0
    prefill_cells: Set[Tuple[int, int, int]] = field(default_factory=set)
    queue: Deque[QueueItem] = field(default_factory=deque)
    permutation_cache: DefaultDict[Tuple[int, ...], Set[Tuple[int, ...]]] = field(
        default_factory=lambda: defaultdict(set)
    )
    intersection_cache: DefaultDict[Tuple[Tuple[int, ...], Tuple[int, ...], int], bool] = field(
        default_factory=lambda: defaultdict(bool)
    )
    assigned_rows: Set[int] = field(default_factory=set)
    assigned_cols: Set[int] = field(default_factory=set)
    
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
        
    def output_grid(self) -> str:
        grid = []
        for row_perms in self.row_permutations:
            perm = next(iter(row_perms))
            grid.extend(str(cell) for cell in perm)
        return ' '.join(grid)
    
    def start(self, input_clues, input_prefill) -> str:
        if not parse_input(self, input_clues, input_prefill):
            return "Bad input argumemnt provided"
        return self.output_grid()


game = Game()