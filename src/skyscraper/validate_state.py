from typing import List, Set
from game import game

def constraint_list_factory() -> set:
    return set(i + 1 for i in range(game.n))


def grid_factory() -> List[Set[int]]:
    return [constraint_list_factory() for _ in range(game.n**2)]


def get_current_grid_state() -> str:
    grid = []
    for row_perms in game.row_permutations:
        if len(row_perms == 1):
            perm = next(iter(row_perms))
            grid.extend(str(cell) for cell in perm)
        else:
            grid.extend('?')
    return ' '.join(grid)


def isSolved() -> bool:
    return all(len(row_perms) == 1 for row_perms in game.row_permutations)
