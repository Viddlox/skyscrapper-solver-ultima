from typing import List, Set, Deque, Tuple, TypedDict, TypeAlias, Dict, NamedTuple
from enum import Enum
from dataclasses import dataclass

MAX_ELIMINATION_CACHE_SIZE = 5000
MAX_INTERSECTION_CACHE_SIZE = 5000


class Actions(Enum):
    ASSIGN_ROW_PERMUTATION = 1
    ASSIGN_COL_PERMUTATION = 2


class QueueItem(TypedDict):
    type: Actions
    index: int


Permutation: TypeAlias = Tuple[int, ...]
PermutationSet: TypeAlias = Set[Permutation]
ClueConstraints: TypeAlias = Tuple[int, ...]
IntersectionKey: TypeAlias = Tuple[Permutation, Permutation, int]
Prefill: TypeAlias = Tuple[int, int, int]
# (decision_type, idx, permutation, state_hash)
EliminationKey: TypeAlias = Tuple[str, int, Permutation, int]
EliminationCache: TypeAlias = Dict[EliminationKey, int]
IntersectionConstraints: TypeAlias = Tuple[Tuple[int, frozenset[int]], ...]

class PreComputeDebugKey(NamedTuple):
    line_type: str
    index: int


class PreComputeDebugValue(NamedTuple):
    clue_start: int
    clue_end: int
    prevCount: int


PreComputeDebugCache: TypeAlias = Dict[PreComputeDebugKey,
                                       PreComputeDebugValue]


@dataclass
class DecisionPoint:
    decision_type: str
    index: int
    chosen_permutation: Permutation
    eliminated_permutations: PermutationSet


@dataclass
class GameState:
    row_permutations: List[PermutationSet]
    col_permutations: List[PermutationSet]
    assigned_rows: Set[int]
    assigned_cols: Set[int]
    queue: Deque[QueueItem]
