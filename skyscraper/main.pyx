import argparse
import time
cimport cython
from .game cimport Game
from .pre_compute cimport initialize_permutations
from .backtrack cimport dfs


def main():
    parser = argparse.ArgumentParser(
        description="🧱 NxN Skyscraper Puzzle Solver",
        epilog=(
            "Example usage:\n"
            "  python3 skyscraper '2123232123142221'\n"
            "  python3 skyscraper '2123232123142221' '1,2,4 3,1,4'\n"
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
    
    cdef Game game = Game()
    cdef double start = time.perf_counter()
    result = solve_puzzle(game, args.clues, args.prefill)
    cdef double end = time.perf_counter()
    
    print(f"\n{result}")
    cdef double duration = (end - start) * 1000
    print(f"Solved in: {duration:.3f} ms")


@cython.boundscheck(False)
@cython.wraparound(False)
cdef str solve_puzzle(Game game, str input_clues, str input_prefill):
    game.reset()
    
    if not game.parse_input(input_clues, input_prefill):
        return "Bad input argument provided"

    print(f"\nGrid size: {game.n}x{game.n}\n")
    print(f"Clues: {game.clues}\n")

    if not initialize_permutations(game):
        print("Starting pre-compute via permutation filtration..\n")
        return "Unsolvable during pre-compute"

    if game.is_solved():
        print("Solved by permutation filtration!")
        return game.output_grid()

    print("\nStarting backtracking...\n")
    if not dfs(game):
        return "No solution found\n"
    
    print("Solved by backtracking")
    return game.output_grid()


if __name__ == "__main__":
    main()