import argparse
import time
from src.skyscraper.game import Game


def main():
    parser = argparse.ArgumentParser(
        description="🧱 NxN Skyscraper Puzzle Solver",
        epilog=(
            "Example usage:\n"
            "  python3 main.py '2123232123142221'\n"
            "  python3 main.py '2123232123142221' '1,2,4 3,1,4'\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "clues",
        type=str,
        help=(
            "Edge clue string.\n"
            "Ordered as: top, bottom, left, right — concatenated without spaces.\n"
            "Example for 4x4: '2123232123142221'"
        )
    )
    parser.add_argument(
        "--prefill",
        type=str,
        default="",
        help=(
            "Optional: Space-separated list of pre-filled cells.\n"
            "Each entry is in 'row,col,value' format.\n"
            "Example: '1,2,4 3,1,4' sets cell (1,2)=4 and (3,1)=4"
        )
    )

    args = parser.parse_args()
    g = Game()
    start = time.perf_counter()
    print(f"\n{g.start(args.clues, args.prefill)}")
    end = time.perf_counter()
    duration = (end - start) * 1000
    print(f"Solved in: {duration:.3f} ms")

if __name__ == "__main__":
    main()
