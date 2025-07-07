#!/usr/bin/env python3

import sys
from src.skyscraper.game import game
from src.utils.benchmark import benchmark

ENABLE_DEBUG = True

def main():
    if not 1 < len(sys.argv) < 4:
        print("Usage: python main.py '<puzzle_string>' '<prefill_string>'")
        sys.exit(1)
    clue_input = sys.argv[1]
    prefill_input = sys.argv[2] if len(sys.argv) > 2 else ""
    if ENABLE_DEBUG:
        benchmark(game.start, clue_input, prefill_input)
    else:
        print('\n' + game.start(clue_input, prefill_input))
if __name__ == "__main__":
    main() 