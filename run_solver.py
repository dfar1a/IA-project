import importlib
import csv
import multiprocessing
import os
import gc

Times = 5000
SolverTypes = ["bfs-single_core"]
NUM_PROCESSES = (multiprocessing.cpu_count() - 1) // 2

csv_lock = multiprocessing.Lock()


def write_to_csv(results: dict, filename="solver_results.csv"):
    """Write results to CSV file, creating it if it doesn't exist"""
    with csv_lock:
        file_exists = os.path.isfile(filename)

        with open(filename, "a", newline="") as csvfile:
            fieldnames = results.keys()

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(results)

        return filename


def solver_worker(dummy_arg=None):
    controller = importlib.import_module("controller")
    Solver = importlib.import_module("solver")

    for solver_type in SolverTypes:
        for _ in range(Times // (multiprocessing.cpu_count() - 1)):
            solver_type = "bfs-single_core"

            board = controller.BoardController()
            seed = board.get_seed()

            solver = Solver.AsyncSolver(board, "bfs-single_core")
            solver.start()

            while solver.is_running():
                continue  # Wait for the solver to find the solution

            if not solver.has_solution():
                print("Solution not found")

            results = {
                "solver_type": solver_type,
                "solution_found": 1 if solver.has_solution() else 0,
                "time_elapsed": solver.get_time_elapsed()
                / 10**9,  # Convert ns to seconds
                "max_memory_mb": solver.get_max_mem_used()
                / (1024**2),  # Convert bytes to MB
                "avg_memory_mb": solver.get_avg_mem_used()
                / (1024**2),  # Convert bytes to MB
                "states_processed": solver.get_states_processed(),
                "moves": solver.get_moves(),
                "seed": seed.hex(),
            }

            del board
            del solver
            gc.collect()

            write_to_csv(results)

            for key in results:
                print(f"{key}: {results[key]}")
            print()


def main():

    processes = []
    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=solver_worker, args=(i,))
        p.daemon = False  # IMPORTANT: Set processes as non-daemonic
        p.start()
        processes.append(p)

    try:
        # Wait for all processes to complete
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Terminating processes...")
        for p in processes:
            p.terminate()
        print("Processes terminated.")


if __name__ == "__main__":
    main()
