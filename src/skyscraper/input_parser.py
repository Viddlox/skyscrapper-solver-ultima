def parse_input(game_instance, input_clues: str, input_prefill: str) -> bool:
    if not input_clues.strip():
        return False
    try:
        clues = [int(i) for i in input_clues.split()]
    except ValueError:
        return False
    if len(clues) % 4 != 0 or len(clues) < 8:
        return False

    n = len(clues) // 4
    max_clue_count = 0
    for clue in clues:
        if not (1 <= clue <= n):
            return False
        if clue == n:
            max_clue_count += 1
            if max_clue_count > 2:
                return False

    game_instance.clues = clues
    game_instance.n = n

    if input_prefill.strip():
        try:
            process_prefilled_cells(game_instance, input_prefill.strip())
        except ValueError:
            return False
    return True


def process_prefilled_cells(game_instance, input_prefill: str) -> None:
    for curr in input_prefill:
        parts = curr.split(',')
        if len(parts) != 3:
            raise ValueError(f"Invalid prefill format: {curr}")
        try:
            row, col, val = map(int, parts)
        except ValueError:
            raise ValueError(f"Invalid prefill values: {curr}")
        if not (1 <= row <= game_instance.n and 1 <= col <= game_instance.n):
            raise ValueError(f"Coordinates out of bounds: {curr}")
        if not (1 <= val <= game_instance.n):
            raise ValueError(f"Invalid cell value: {curr}")
        game_instance.prefill_cells.add((row, col, val))
