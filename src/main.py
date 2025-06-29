import sys
from skyscraper.game import game
from .utils import benchmark

ENABLE_DEBUG = True

if __name__ == "__main__":
    arg_length = len(sys.argv)
    if not 1 < arg_length < 4:
        print("Usage: python3 main.py '<puzzle_string>' '<prefill_string>'")
        sys.exit(1)
    clue_input = sys.argv[1]
    prefill_input = sys.argv[2] if len(sys.argv) > 2 else ""
    if ENABLE_DEBUG:
        benchmark(game.start, clue_input, prefill_input)
    else:
        print('\n' + game.start(clue_input, prefill_input))
