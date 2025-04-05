from heapq import *
import solver
import multiprocessing
import pickle
import time
import os
import signal

# Global tracking for processes
_all_processes = []  # (process, stop_event) pairs


class TreeNode(solver.TreeNode):
    def evaluate(self, state):
        return super().evaluate(state) + self.actualCost


def terminate_all_processes():
    """Terminate all running BFS solver processes"""
    global _all_processes

    if not _all_processes:
        return

    print(f"Terminating {len(_all_processes)} BFS processes...")

    # First try to signal processes to stop gracefully
    for p, stop_event in _all_processes:
        if p.is_alive():
            stop_event.set()

    # Give processes a moment to terminate gracefully
    time.sleep(0.2)

    # Then forcefully terminate any remaining processes
    for p, _ in _all_processes:
        if p.is_alive():
            try:
                print(f"Forcefully terminating process {p.name} (PID: {p.pid})")
                p.terminate()
                p.join(0.5)

                # If still alive on Unix systems, try SIGKILL
                if p.is_alive() and hasattr(signal, "SIGKILL"):
                    print(f"Sending SIGKILL to process {p.pid}")
                    os.kill(p.pid, signal.SIGKILL)
            except Exception as e:
                print(f"Error terminating process: {e}")

    # Clear the list
    _all_processes.clear()
    print("All BFS processes terminated")


def kill_all(*args):
    """Handler for external kill signals - terminates all processes"""
    print("Received kill signal - terminating all processes")
    terminate_all_processes()

    # Exit more forcefully if being called from signal handler
    if args:
        os._exit(1)


visited_states = set()


# Core BFS algorithm - shared between all implementations
def bfs_core(
    start_node,
    max_states=10**5,
    stop_check_fn=None,
    on_solution_fn=None,
    process_id=0,
    visit_nodes=-1,
    a_star=False,
):
    """[:max_moves_per_state]led with solution node if found
        process_id: ID for logging
        max_moves_per_state: How many moves to consider from each state

    Returns:
        Solution node if found and on_solution_fn is None, otherwise None
    """
    # Initialize defaults
    global visited_states
    visited_states.add(hash(start_node.state))

    if stop_check_fn is None:
        stop_check_fn = lambda: False  # Never stop by default

    # Set up queue and counters
    queue = [start_node]
    states_processed = 0

    # Move function mapping - avoid repeated lookups
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }

    # Main BFS loop
    try:
        while queue and not stop_check_fn() and states_processed < max_states:
            current_board = heappop(queue)

            # Check win condition
            if current_board.state.is_game_won():
                print(f"BFS Core {process_id} found solution!")
                if on_solution_fn:
                    on_solution_fn(current_board)
                    return None, states_processed  # Solution handled by callback
                else:
                    return current_board, states_processed  # Return solution directly
            elif visit_nodes != -1 and len(queue) >= visit_nodes:
                return queue

            # Get and explore possible moves
            moves = solver.get_possible_moves(current_board.state)
            for move in moves:
                # Check if we should stop
                if stop_check_fn():
                    return None, states_processed

                # Apply move and check validity
                state = move_card[move[0]](current_board.state, move[1], move[2])
                if state is None:
                    continue

                # Check if already visited
                state_hash = hash(state)
                if state_hash in visited_states:
                    continue

                visited_states.add(state_hash)

                # Create new node and link to parent
                node = (
                    TreeNode(state, current_board)
                    if a_star
                    else solver.TreeNode(state, current_board)
                )

                current_board.add_child(node, move)

                # Add to queue
                heappush(queue, node)

            # Update counters and periodically check stopping condition
            states_processed += 1
            if states_processed % 100 == 0 and stop_check_fn():
                return None, states_processed

            # Status updates
            if states_processed % 1000 == 0:
                print(
                    f"BFS Core {process_id} processed {states_processed} states, queue size: {len(queue)}"
                )

    except Exception as e:
        print(f"BFS Core {process_id} error: {e}")
        return None, states_processed

    print(f"BFS Core {process_id} exhausted after {states_processed} states")
    return None, states_processed


def expand_initial_nodes(
    root: solver.TreeNode, num_nodes: int
) -> list[solver.TreeNode]:
    """Expand the root node to create starting points for different processes"""

    # Run core BFS to expand enough nodes
    initial_nodes = bfs_core(
        root,
        max_states=num_nodes * 10,  # Higher limit to find enough nodes
        visit_nodes=num_nodes,
    )

    # If we couldn't expand enough, just use what we have
    return initial_nodes if initial_nodes else [root]


def bfs_process_worker(start_node, process_id, solution_queue, stop_event):
    """Worker process that performs BFS from a given starting node"""
    print(f"Process {process_id} starting BFS from depth {start_node.actualCost}")

    # Set up signal handler for clean termination
    should_exit = False

    def handle_signal(*args):
        nonlocal should_exit
        should_exit = True

    signal.signal(signal.SIGTERM, handle_signal)

    # Create stop check function that combines event and signal
    def should_stop():
        return stop_event.is_set() or should_exit

    # Create solution handler function
    def on_solution(solution_node):
        try:
            solution_queue.put(pickle.dumps(solution_node))
        except Exception as e:
            print(f"Process {process_id} failed to queue solution: {e}")

    # Run the core BFS algorithm
    bfs_core(
        start_node,
        max_states=10**5,
        stop_check_fn=should_stop,
        on_solution_fn=on_solution,
        process_id=process_id,
    )


def bfs_distributed(root: solver.TreeNode) -> solver.TreeNode | None:
    """BFS implementation that distributes different starting nodes across processes"""
    print("Using distributed BFS with multiprocessing")
    global _all_processes

    # Terminate any existing processes first
    terminate_all_processes()

    # Determine number of processes
    num_processes = max(1, (multiprocessing.cpu_count() - 1) // 2)

    # Create initial nodes for distribution
    initial_nodes = expand_initial_nodes(root, num_processes)

    # Check for immediate solution in initial nodes
    for node in initial_nodes:
        if node.state.is_game_won():
            return node

    # Set up multiprocessing resources
    solution_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    run_processes = []

    try:
        # Start a BFS process for each initial node
        for i, node in enumerate(initial_nodes):
            process = multiprocessing.Process(
                target=bfs_process_worker, args=(node, i, solution_queue, stop_event)
            )
            process.daemon = True
            process.start()
            run_processes.append(process)
            # Track globally for cleanup
            _all_processes.append((process, stop_event))
            time.sleep(0.05)  # Small delay to stagger startup

        # Wait for a solution or timeout
        solution = None
        timeout = 60  # 1 minute timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            if not solution_queue.empty():
                try:
                    solution_data = solution_queue.get(block=False)
                    solution = pickle.loads(solution_data)
                    stop_event.set()  # Signal all processes to stop
                    break
                except Exception as e:
                    print(f"Error getting solution: {e}")
            time.sleep(0.1)

            # Check if all processes have died
            if not any(p.is_alive() for p in run_processes):
                break

    finally:
        # Always ensure processes are stopped
        stop_event.set()

        # Clean up processes
        for p in run_processes:
            if p.is_alive():
                p.join(0.5)  # Give a shorter timeout
                if p.is_alive():
                    p.terminate()

        # Update global process list
        _all_processes = [(p, e) for p, e in _all_processes if p.is_alive()]

    return solution


def bfs_single_core(
    start_node: solver.TreeNode, a_star: bool
) -> solver.TreeNode | None:
    """Single-core BFS implementation that runs in the current process"""
    print("Using single-core BFS")

    # Use the AsyncSolver._stop flag for stopping
    def should_stop():
        return solver.AsyncSolver._stop

    # Run the core BFS algorithm directly
    return bfs_core(
        start_node,
        max_states=10**5 * 3,
        stop_check_fn=should_stop,
        process_id="single",
        a_star=a_star,
    )


class AsyncBFSSolver:
    _stop = False

    def __init__(self):
        self.process = None

    def stop(self):
        AsyncBFSSolver._stop = True
        if self.process and self.process.is_alive():
            self.process.terminate()
        # Also stop all BFS worker processes

        terminate_all_processes()
