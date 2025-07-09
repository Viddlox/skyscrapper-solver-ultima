import argparse
from src.skyscraper.game import Game
from src.utils.benchmark import benchmark


def main():
    parser = argparse.ArgumentParser(
        description="🧱 NxN Skyscraper Puzzle Solver",
        epilog=(
            "Example usage:\n"
            "  python3 main.py '2123232123142221'\n"
            "  python3 main.py '2123232123142221' --prefill '1,2,4 3,1,4'\n"
            "  python3 main.py '2123232123142221' --debug\n"
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Optional: Enable debug mode with benchmark timing output."
    )
    args = parser.parse_args()
    g = Game()
    if args.debug:
        benchmark(g.start, args.clues, args.prefill, args.debug)
    else:
        print('\n' + g.start(args.clues, args.prefill, args.debug))


if __name__ == "__main__":
    main()
