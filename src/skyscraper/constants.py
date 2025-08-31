from typing import List, Set, Tuple, TypedDict, TypeAlias
from enum import Enum
from dataclasses import dataclass

class Actions(Enum):
    ASSIGN_ROW_PERMUTATION = 1
    ASSIGN_COL_PERMUTATION = 2


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