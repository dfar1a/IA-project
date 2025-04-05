import solver
import signal
import time
from heapq import heappush, heappop
import multiprocessing
import pickle
import os


class DFSSolver:
    def __init__(self, root: solver.TreeNode, max_depth=50):
        self.root = root
        self.max_depth = max_depth
        self.visited = {}
        self._stop = False
        self.solution = None
        self.start_time = time.time()
        self.timeout = 30  # seconds

    def set_stop(self):
        self._stop = True

    def should_stop(self):
        return (self._stop or solver.AsyncSolver._stop or 
                (time.time() - self.start_time) > self.timeout)

    def dfs(self, node: solver.TreeNode, depth=0):
        if self.should_stop() or depth > self.max_depth:
            return None

        # Check for win condition
        if node.state.is_game_won():
            return node

        state_hash = hash(node.state)
        
        # Skip if we've seen this state at a better depth
        if state_hash in self.visited and self.visited[state_hash] <= depth:
            return None
            
        self.visited[state_hash] = depth

        # Get possible moves and prioritize them
        moves = solver.get_possible_moves(node.state)
        if not moves:
            return None

        # Prioritize foundation moves first
        moves.sort(key=lambda m: (m[0] != solver.MoveType.foundation, m[1], m[2]))

        # Try each move
        for move in moves:
            if self.should_stop():
                return None

            move_func = solver.move_col_foundation if move[0] == solver.MoveType.foundation else solver.move_col_col
            new_state = move_func(node.state, move[1], move[2])

            if new_state is None or hash(new_state) in self.visited:
                continue

            child = solver.TreeNode(new_state)
            node.add_child(child, move)

            result = self.dfs(child, depth + 1)
            if result:
                return result

        return None


def run_dfs(board):
    """Main DFS function that can be called from other processes"""
    print("Starting DFS solver for small board...")
    root = solver.TreeNode(board)
    searcher = DFSSolver(root, max_depth=100)  # Increased max_depth for small board

    # Set up signal handler for graceful termination
    def stop_handler(*args):
        searcher.set_stop()
    signal.signal(signal.SIGTERM, stop_handler)

    try:
        solution = searcher.dfs(root)
        if solution:
            print("DFS found solution!")
            return solver.backtrack_solution(solution)
        else:
            print("DFS couldn't find solution")
            return None
    except Exception as e:
        print(f"DFS solver error: {e}")
        return None


def dfs_process_worker(start_node, process_id, solution_queue, stop_event):
    """Worker process that performs DFS from a given starting node"""
    print(f"Process {process_id} starting DFS from depth {start_node.actualCost}")
    
    solver = DFSSolver(start_node, max_depth=100)
    solver.timeout = 20  # Shorter timeout for worker processes
    
    def handle_signal(*args):
        solver.set_stop()
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        solution = solver.dfs(start_node)
        if solution and not stop_event.is_set():
            print(f"Process {process_id} found solution!")
            try:
                solution_queue.put(pickle.dumps(solver.backtrack_solution(solution)))
            except Exception as e:
                print(f"Process {process_id} failed to serialize solution: {e}")
    except Exception as e:
        print(f"Process {process_id} error: {e}")


def dfs_distributed(root: solver.TreeNode) -> solver.TreeNode | None:
    """DFS implementation that distributes different starting nodes across processes"""
    print("Using distributed DFS with multiprocessing")
    
    num_processes = max(1, multiprocessing.cpu_count() - 1)
    initial_nodes = [root]  # For DFS, we don't need multiple starting points
    
    solution_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    
    processes = []
    
    try:
        # Start DFS processes
        for i, node in enumerate(initial_nodes):
            if i >= num_processes:
                break
                
            process = multiprocessing.Process(
                target=dfs_process_worker,
                args=(node, i, solution_queue, stop_event)
            )
            process.start()
            processes.append(process)
            time.sleep(0.1)  # Small delay between process starts
            
        # Wait for solution or timeout
        solution = None
        timeout = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not solution_queue.empty():
                try:
                    solution_data = solution_queue.get(block=False)
                    solution = pickle.loads(solution_data)
                    stop_event.set()
                    break
                except Exception as e:
                    print(f"Error getting solution: {e}")
                    
            time.sleep(0.1)
            
            # Check if all processes died
            if all(not p.is_alive() for p in processes):
                break
                
    finally:
        stop_event.set()
        for p in processes:
            if p.is_alive():
                p.terminate()
            p.join()
            
    return solution


def terminate_all_processes():
    """Cleanup function for consistency with BFS solver"""
    pass  # DFS doesn't maintain global process list


def kill_all(*args):
    """Handler for external kill signals"""
    print("Received kill signal - terminating DFS processes")
    os._exit(1)