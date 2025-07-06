from typing import Set, Tuple, TypedDict, TypeAlias
from enum import Enum


class Actions(Enum):
    PROPAGATE_ROW_CONSTRAINTS = 1
    PROPAGATE_COL_CONSTRAINTS = 2
    ASSIGN_ROW_PERMUTATION = 3
    ASSIGN_COL_PERMUTATION = 4


class QueueItem(TypedDict):
    type: Actions
    index: int


class ConflictType(Enum):
    EMPTY_PERMUTATION_SET = "empty_permutation_set"
    INTERSECTION_INCOMPATIBILITY = "intersection_incompatibility"
    CLUE_VIOLATION = "clue_violation"


Permutation: TypeAlias = Tuple[int, ...]
PermutationSet: TypeAlias = Set[Permutation]
ClueConstraints: TypeAlias = Tuple[int, ...]
IntersectionKey: TypeAlias = Tuple[Permutation, Permutation, int]
Prefill: TypeAlias = Tuple[int, int, int]
