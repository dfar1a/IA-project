from heapq import *
import solver
import multiprocessing
import threading
import pickle
import time
import os
import signal

_all_processes = []  # Global list to track all processes


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


processes = []


def kill_all(*args):
    """Handler for external kill signals - terminates all processes"""
    print("Received kill signal - terminating all processes")
    terminate_all_processes()

    # Exit more forcefully if being called from signal handler
    if args:
        os._exit(1)


def bfs(root: solver.TreeNode) -> solver.TreeNode | None:
    """Main BFS function that distributes work across processes or threads"""
    # Check if we're already in a child process
    in_child_process = multiprocessing.current_process().name != "MainProcess"

    # Use multiprocessing for main process
    return bfs_distributed(root)


def expand_initial_nodes(
    root: solver.TreeNode, num_nodes: int
) -> list[solver.TreeNode]:
    """Expand the root node to create starting points for different processes"""
    initial_nodes = []
    queue = [root]
    visited = {hash(root.state)}

    # Move function mapping
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }

    # Expand root to get initial nodes
    while queue and len(initial_nodes) < num_nodes:
        current = heappop(queue)

        # Check for win condition immediately
        if current.state.is_game_won():
            return [current]  # Return winning node immediately

        # Get possible moves from this state
        moves = solver.get_possible_moves(current.state)

        for move in moves[:5]:  # Limit initial expansion
            state = move_card[move[0]](current.state, move[1], move[2])

            if state is None or hash(state) in visited:
                continue

            visited.add(hash(state))
            node = solver.TreeNode(state)
            node.parent = current
            current.add_child(node, move)

            # Add to both initial nodes and expansion queue
            initial_nodes.append(node)
            heappush(queue, node)

            # Break if we have enough initial nodes
            if len(initial_nodes) >= num_nodes:
                break

    # If we couldn't expand enough, just use what we have
    return initial_nodes if initial_nodes else [root]


def bfs_distributed(root: solver.TreeNode) -> solver.TreeNode | None:
    """BFS implementation that distributes different starting nodes across processes"""
    print("Using distributed BFS with multiprocessing")
    global _all_processes

    # Terminate any existing processes first
    terminate_all_processes()

    num_processes = max(1, multiprocessing.cpu_count() - 1)

    # Create initial nodes for distribution
    initial_nodes = expand_initial_nodes(root, num_processes)

    # Check for immediate solution
    if any(node.state.is_game_won() for node in initial_nodes):
        return next(node for node in initial_nodes if node.state.is_game_won())

    # Set up multiprocessing resources
    solution_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # Track processes for this run
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

            # Check if any processes died unexpectedly
            alive_count = sum(1 for p in run_processes if p.is_alive())
            if alive_count == 0:
                print("All processes terminated unexpectedly")
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

        # Update global process list - remove terminated processes
        _all_processes = [(p, e) for p, e in _all_processes if p.is_alive()]

    return solution


def bfs_process_worker(start_node, process_id, solution_queue, stop_event):
    """Worker process that performs BFS from a given starting node"""
    print(f"Process {process_id} starting BFS from depth {start_node.actualCost}")

    # Set up data structures for this process
    visited_states = {hash(start_node.state)}
    queue = [start_node]
    states_processed = 0
    max_states = 10**5  # Limit states to process

    # Better signal handling with nonlocal variable
    should_exit = False

    def handle_signal(*args):
        nonlocal should_exit
        should_exit = True

    # Set up signal handler
    signal.signal(signal.SIGTERM, handle_signal)

    # Move function mapping
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }

    try:
        while (
            queue
            and not stop_event.is_set()
            and not should_exit
            and states_processed < max_states
        ):
            current_board = heappop(queue)

            # Check win condition
            if current_board.state.is_game_won():
                print(f"Process {process_id} found solution!")
                try:
                    solution_queue.put(pickle.dumps(current_board))
                except:
                    print(f"Process {process_id} failed to put solution in queue")
                return

            # Get possible moves
            moves = solver.get_possible_moves(current_board.state)

            # Explore each move
            for move in moves[:8]:  # Limit moves per state
                if stop_event.is_set() or should_exit:
                    break

                state = move_card[move[0]](current_board.state, move[1], move[2])

                if state is None:
                    continue

                state_hash = hash(state)
                if state_hash in visited_states:
                    continue

                visited_states.add(state_hash)

                # Create new node and link to parent
                node = solver.TreeNode(state)
                node.parent = current_board
                current_board.add_child(node, move)

                # Add to queue
                heappush(queue, node)

            states_processed += 1

            # Check stop event periodically to reduce CPU usage
            if states_processed % 100 == 0:
                if stop_event.is_set() or should_exit:
                    break
    except Exception as e:
        print(f"Process {process_id} error: {e}")
    finally:
        pass


class AsyncBFSSolver:
    _stop = False

    def __init__(self):
        self.process = None

    def stop(self):
        AsyncBFSSolver._stop = True
        if self.process and self.process.is_alive():
            self.process.terminate()
        # Also stop all BFS worker processes
        import bfsSolver  # Import here to avoid circular imports

        bfsSolver.terminate_all_processes()
