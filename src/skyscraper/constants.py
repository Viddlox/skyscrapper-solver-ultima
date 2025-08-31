from typing import List, Set, Deque, Tuple, TypedDict, TypeAlias
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

CELL_SOLVE_PREFILL_THRESHOLD = 0.15


class Actions(Enum):
    ASSIGN_ROW_PERMUTATION = 1
    ASSIGN_COL_PERMUTATION = 2
    PROPAGATE_CONSTRAINTS_FROM_RESOLVED_CELL = 3


class QueueItem(TypedDict):
    type: Actions
    index: int


Permutation: TypeAlias = Tuple[int, ...]
PermutationSet: TypeAlias = Set[Permutation]
Prefill: TypeAlias = Tuple[int, int, int]


@dataclass
class GameState:
    row_permutations: List[PermutationSet]
    col_permutations: List[PermutationSet]
    assigned_rows: Set[int]
    assigned_cols: Set[int]
    queue: Deque[QueueItem]


@dataclass
class CellSolveGameState:
    grid: List[Set[int]] = field(default_factory=list)
    fixed_cells: Set[int] = field(default_factory=set)
    queue: Deque = field(default_factory=deque)
