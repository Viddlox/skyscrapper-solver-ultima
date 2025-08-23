from typing import TYPE_CHECKING
from .constants import CELL_SOLVE_PREFILL_THRESHOLD

if TYPE_CHECKING:
    from .game import Game


def parse_input(g: "Game", input_clues: str, input_prefill: str) -> bool:
    if not input_clues.strip():
        return False
    try:
        clean_input = input_clues.replace(" ", "")
        clues = [int(char) for char in clean_input]
    except ValueError:
        return False

    if len(clues) % 4 != 0 or len(clues) < 8:
        return False

    n = len(clues) // 4
    max_clue_count = 0
    for clue in clues:
        if not (0 <= clue <= n):
            return False
        if clue == n:
            max_clue_count += 1
            if max_clue_count > 2:
                return False

    g.clues = clues
    g.n = n

    if input_prefill.strip():
        try:
            process_prefilled_cells(g, input_prefill.strip().split())
        except ValueError:
            return False

    total_cells = g.n**2
    prefill_count = len(g.prefills)
    prefill_ratio = prefill_count / total_cells if total_cells > 0 else 0.0
    g.should_use_cell_solve = (prefill_ratio > CELL_SOLVE_PREFILL_THRESHOLD or
                             prefill_count > 8)
    return True


def process_prefilled_cells(g: "Game", input_prefill: str) -> None:
    g.grid_cell = g.grid_factory()
    for curr in input_prefill:
        parts = curr.split(',')
        if len(parts) != 3:
            raise ValueError(f"Invalid prefill format: {curr}")
        try:
            row, col, val = map(int, parts)
        except ValueError:
            raise ValueError(f"Invalid prefill values: {curr}")
        if not (1 <= row <= g.n and 1 <= col <= g.n):
            raise ValueError(f"Coordinates out of bounds: {curr}")
        if not (1 <= val <= g.n):
            raise ValueError(f"Invalid cell value: {curr}")
        row -= 1
        col -= 1
        g.prefills.add((row, col, val))
        cell_index = (row) * g.n + (col)
        g.set_prefill_cell(cell_index, val)