from heapq import *
import solver
import multiprocessing
import threading
import pickle
import time
import os


def bfs(root: solver.TreeNode) -> solver.TreeNode | None:
    """Main BFS function that distributes work across processes or threads"""
    # Check if we're already in a child process
    in_child_process = multiprocessing.current_process().name != "MainProcess"

    if in_child_process:
        # Use threading for nested process
        return bfs_threading(root)
    else:
        # Use multiprocessing for main process
        return bfs_distributed(root)


def expand_initial_nodes(root, num_nodes):
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

    num_processes = max(1, multiprocessing.cpu_count() - 1)

    # Create initial nodes for distribution
    initial_nodes = expand_initial_nodes(root, num_processes)

    # Check if we already found a solution during initial expansion
    if any(node.state.is_game_won() for node in initial_nodes):
        for node in initial_nodes:
            if node.state.is_game_won():
                return node

    # Set up multiprocessing resources
    solution_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # Start a BFS process for each initial node
    processes = []
    for i, node in enumerate(initial_nodes):
        process = multiprocessing.Process(
            target=bfs_process_worker, args=(node, i, solution_queue, stop_event)
        )
        process.daemon = True
        process.start()
        processes.append(process)
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
            except:
                pass
        time.sleep(0.1)

    # Signal processes to stop
    stop_event.set()

    # Clean up processes
    for p in processes:
        p.join(1)  # Wait 1 second
        if p.is_alive():
            p.terminate()

    return solution


def bfs_process_worker(start_node, process_id, solution_queue, stop_event):
    """Worker process that performs BFS from a given starting node"""
    print(f"Process {process_id} starting BFS from depth {start_node.actualCost}")

    # Set up data structures for this process
    visited_states = {hash(start_node.state)}
    queue = [start_node]
    states_processed = 0
    max_states = 10**5  # Limit states to process

    # Move function mapping
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }

    while queue and not stop_event.is_set() and states_processed < max_states:
        current_board = heappop(queue)

        # Check win condition
        if current_board.state.is_game_won():
            print(f"Process {process_id} found solution!")
            solution_queue.put(pickle.dumps(current_board))
            return

        # Get possible moves
        moves = solver.get_possible_moves(current_board.state)

        # Explore each move
        for move in moves[:8]:  # Limit moves per state
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

        # Check stop event periodically
        if states_processed % 100 == 0 and stop_event.is_set():
            break

    print(f"Process {process_id} finished after exploring {states_processed} states")


def bfs_threading(root: solver.TreeNode) -> solver.TreeNode | None:
    """BFS implementation using threads - for when we're already in a child process"""
    print("Using threading-based BFS")

    num_threads = max(1, multiprocessing.cpu_count() - 1)

    # Create initial nodes for distribution
    initial_nodes = expand_initial_nodes(root, num_threads)

    # Check if we already found a solution during initial expansion
    for node in initial_nodes:
        if node.state.is_game_won():
            return node

    # Set up shared data structures
    solution = [None]
    solution_found = threading.Event()
    threads = []

    # Start a thread for each initial node
    for i, node in enumerate(initial_nodes):
        thread = threading.Thread(
            target=bfs_thread_worker, args=(node, i, solution, solution_found)
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.02)  # Small delay to stagger startup

    # Wait for a solution or timeout
    timeout = 60  # 1 minute timeout
    start_time = time.time()

    while time.time() - start_time < timeout:
        if solution_found.is_set():
            break
        time.sleep(0.1)

    # Signal threads to stop
    solution_found.set()

    # Wait for threads to finish
    for thread in threads:
        thread.join(0.2)

    return solution[0]


def bfs_thread_worker(start_node, thread_id, solution, solution_found):
    """Worker thread that performs BFS from a given starting node"""
    print(f"Thread {thread_id} starting BFS from depth {start_node.actualCost}")

    # Set up data structures for this thread
    visited_states = {hash(start_node.state)}
    queue = [start_node]
    states_processed = 0
    max_states = 5 * 10**4  # Limit states to process

    # Move function mapping
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }

    while queue and not solution_found.is_set() and states_processed < max_states:
        current_board = heappop(queue)

        # Check win condition
        if current_board.state.is_game_won():
            print(f"Thread {thread_id} found solution!")
            solution[0] = current_board
            solution_found.set()
            return

        # Get possible moves
        moves = solver.get_possible_moves(current_board.state)

        # Explore each move
        for move in moves[:8]:  # Limit moves per state
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

        # Check solution found periodically
        if states_processed % 100 == 0 and solution_found.is_set():
            break

    print(f"Thread {thread_id} finished after exploring {states_processed} states")
