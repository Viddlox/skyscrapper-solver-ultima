from .constants import Actions
from .grid_manager_cell_poe import get_cell_indices_from_clue_index, get_cross_indices_from_cell_index, get_cell_indices_from_row_index, get_cell_indices_from_col_index

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game


def init_edge_clue_constraints(g: "Game") -> None:
    for i, clue in enumerate(g.clues):
        cell_indices = get_cell_indices_from_clue_index(i, g.n)
        if 1 < clue < g.n:
            for d, idx in enumerate(cell_indices):
                constrain_cell_with_clue(clue, d + 1, idx, g)
        elif clue == 1:
            resolve_and_enqueue(cell_indices[0], g.n, g)
        elif clue == g.n:
            for d, idx in enumerate(cell_indices):
                resolve_and_enqueue(idx, d + 1, g)
    queue_processor(g)


def queue_processor(g: "Game") -> None:
    while g.queue_cell_poe:
        action = g.queue_cell_poe.popleft()
        if action['type'] == Actions.PROPAGATE_CONSTRAINTS_FROM_RESOLVED_CELL:
            propagate_from_resolved_cell(action['cell_index'], g)

        if len(g.queue_cell_poe) % 5 == 0:
            find_hidden_singles(g)


def constrain_and_enqueue(cell_index: int, value_to_delete: int, g: "Game") -> None:
    if cell_index in g.prefill_cells_cell_poe:
        return

    cell = g.grid_cell_poe[cell_index]

    if len(cell) == 1 and value_to_delete in cell:
        raise ValueError(
            f"Trying to delete the only value {value_to_delete} from cell {cell_index}")

    is_mutated = value_to_delete in cell
    cell.discard(value_to_delete)

    if len(cell) == 0:
        raise ValueError(f"Cell {cell_index} is empty")

    if is_mutated and len(cell) == 1:
        g.queue_cell_poe.append({
            'type': Actions.PROPAGATE_CONSTRAINTS_FROM_RESOLVED_CELL,
            'cell_index': cell_index
        })

    if is_mutated:
        poe_search_and_enqueue(cell_index, value_to_delete, g)


def resolve_and_enqueue(cell_index: int, value_to_resolve_to: int, g: "Game") -> None:
    if cell_index in g.prefill_cells_cell_poe:
        return

    for cell_value in list(g.grid_cell_poe[cell_index]):
        if cell_value != value_to_resolve_to:
            constrain_and_enqueue(cell_index, cell_value, g)


def poe_search_and_enqueue(modified_cell_index: int, deleted_value: int, g: "Game") -> None:
    cross_indices = get_cross_indices_from_cell_index(
        modified_cell_index, g.n, g.intersection_cache_cell_poe)
    filtered_indices = [
        i for i in cross_indices if deleted_value in g.grid_cell_poe[i]]
    if len(filtered_indices) == 1:
        resolve_and_enqueue(filtered_indices[0], deleted_value, g)


def propagate_from_resolved_cell(cell_index: int, g: "Game") -> None:
    cell = g.grid_cell_poe[cell_index]
    if len(cell) > 1:
        raise Exception("Constraint propagation on a non-resolved cell!")
    value_to_eliminate = next(iter(cell))
    cross_indices = get_cross_indices_from_cell_index(
        cell_index, g.n, g.intersection_cache_cell_poe)
    for idx in cross_indices:
        constrain_and_enqueue(idx, value_to_eliminate, g)


def constrain_cell_with_clue(clue: int, pos: int, cell_index: int, g: "Game") -> None:
    minimum = g.n - clue + pos + 1
    for i in range(minimum, g.n + 1):
        constrain_and_enqueue(cell_index, i, g)


def find_hidden_singles(g: "Game") -> None:
    for i in range(g.n):
        row_indices = get_cell_indices_from_row_index(i, g.n)
        col_indices = get_cell_indices_from_col_index(i, g.n)

        for value in range(1, g.n + 1):
            possible_row_cells = [
                i for i in row_indices if value in g.grid_cell_poe[i]]
            if len(possible_row_cells) == 1:
                resolve_and_enqueue(possible_row_cells[0], value, g)
            possible_col_cells = [
                i for i in col_indices if value in g.grid_cell_poe[i]]
            if len(possible_col_cells) == 1:
                resolve_and_enqueue(possible_col_cells[0], value, g)
