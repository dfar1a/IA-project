import pickle
import threading
import cards as c
from controller import BoardController
from heapq import *
import random
import importlib
import multiprocessing
import signal
import time
import psutil

from typing import TYPE_CHECKING

import board as b


class TreeNode:
    def evaluate(self, state: b.Board) -> float:
        cost = AsyncSolver.learn.get(hash(state))
        if cost != None:
            return -(10**3) // (cost + 1)

        score = 0
        nextCards = {
            (found.get_suite().value): (found.next()) for found in state.foundations
        }

        lenFounds = [len(found.cards) for found in state.foundations]
        sumLen = sum(lenFounds)
        minLen = min(lenFounds)
        maxLen = max(lenFounds)

        for column in state.columns:
            cards = column.cards

            for i, card in enumerate(cards):
                nextCard = nextCards.get(card.cardSuite.value)
                if nextCard is None:
                    nextCard = nextCards.get(c.CardSuite.any)
                if card.cardValue.value - nextCard.cardValue.value < (
                    len(cards) - i - 1
                ):
                    score += (
                        len(cards)
                        - i
                        - 1
                        - (card.cardValue.value - nextCard.cardValue.value)
                    )

        score += 13 * 4 - sumLen

        return score + random.random()  # + self.actualCost

    def __init__(self, state: b.Board, parent=None):
        self.state = state
        self.parent = parent
        self.children = dict()
        self.next = None
        self.actualCost = self.parent.actualCost + 1 if self.parent is not None else 0
        self.score = self.evaluate(state)

    def add_child(self, child_node: "TreeNode", transition: tuple[str, int, int]):
        self.children[child_node] = transition
        child_node.parent = self

    def __lt__(self, other):
        return isinstance(other, TreeNode) and self.score < other.score


def execute_next_move(root: TreeNode, board: BoardController):
    if root.next != None:
        next, move = root.next

        if move[0] == MoveType.column:
            board.move_card_column_column(
                board.columns[move[1]], board.columns[move[2]]
            )
        elif move[0] == MoveType.foundation:
            board.move_card_column_foundation(
                board.columns[move[1]], board.foundations[move[2]]
            )

        return next
    return None


def get_next_move(root: TreeNode, board: BoardController):
    if root.next != None:
        move = root.next[1]

    return board.columns[move[1]].top()


def save_data_pickle(filename, data):
    with open(filename, "wb") as file:
        pickle.dump(data, file)


def load_data_pickle(filename):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except:
        return dict()


class AsyncSolver:
    """Base class for asynchronous solvers with shared functionality"""

    learn = load_data_pickle("learn.data")
    _stop = False

    def __init__(self, game_board, solver_type="bfs"):
        self.initstate = game_board.model
        self.solution = None
        self.process = None
        self.running = False
        self.result_queue = multiprocessing.Queue()
        self.solver_type = solver_type.lower()  # 'bfs' or 'idastar'
        self.start_time = 0
        self.stop_time = 0
        self.maxMemUsed = 0
        self.sumMemUsed = 0
        self.measuresMemUsed = 0
        self.states_processed = 0

    def get_moves(self):
        count = 0
        while self.extract_solution() is not None:
            count += 1
        return count

    def stop(self):
        AsyncSolver._stop = True
        if self.process and self.process.is_alive():
            self.process.terminate()

    def get_states_processed(self):
        return self.states_processed

    def get_max_mem_used(self):
        return self.maxMemUsed

    def get_avg_mem_used(self):
        return self.sumMemUsed / self.measuresMemUsed if self.measuresMemUsed else 0

    def get_time_elapsed(self):
        return self.stop_time - self.start_time

    def save_data(self):
        save_data_pickle("learn.data", self.learn)

    def _run_solver_process(self, initstate, result_queue):
        """Execute selected solver in a separate process and put result in queue"""
        AsyncSolver._stop = False
        print(f"AI process running using {self.solver_type.upper()} solver")
        v = TreeNode(initstate)

        solution = None
        self.start_time = time.time_ns()
        if self.solver_type == "bfs":
            bfsSolver = importlib.import_module("bfsSolver")
            signal.signal(signal.SIGTERM, bfsSolver.kill_all)
            solution = bfsSolver.bfs_distributed(v)
        elif self.solver_type == "idastar":
            idastar = importlib.import_module("idaStarSolver")
            ida = idastar.IDAStar(initstate)
            solution = ida.runIDAS()
        elif self.solver_type == "bfs-single_core":
            bfsSolver = importlib.import_module("bfsSolver")
            solution, self.states_processed = bfsSolver.bfs_single_core(v)
        
        elif self.solver_type == "dfs":
            dfsSolver = importlib.import_module("dfsSolver")
            game = Game()
            game.board = initstate.copy()
            solution_moves = dfs_solver(game)
  
            if solution_moves:
                # Reconstrói a árvore a partir da lista de movimentos
                for move in solution_moves:
                    (i, j), card = move
                    next_state = move_col_col(initstate, i, j)
                    if next_state is None:
                        next_state = move_col_foundation(initstate, i, j)
                    if next_state is None:
                        continue
                    child = TreeNode(next_state)
                    v.add_child(child, ("column", i, j))  # ou foundation se for o caso
                    v.next = (child, ("column", i, j))
                    v = child
        solution = v
        self.stop_time = time.time_ns()
        v = solution
        if solution:
            print(f"{self.solver_type.upper()} solver found solution")
            # Process the solution to create next moves
            depth = 0
            v = solution
            while v.parent is not None:
                data = AsyncSolver.learn.get(hash(v.state))
                if data is None or depth < data:
                    AsyncSolver.learn[hash(v.state)] = depth
                depth += 1
                parent = v.parent
                parent.next = (v, parent.children[v])
                v = parent

            # Put the initial solution node in queue along with timing information

        result_queue.put(
            pickle.dumps((v, self.start_time, self.stop_time, self.states_processed))
        )

    def run_solver(self):
        """Start the solver in a separate process"""
        AsyncSolver._stop = False
        self.running = True
        # Create a non-daemon process
        self.process = multiprocessing.Process(
            target=self._run_solver_process, args=(self.initstate, self.result_queue)
        )
        self.process.daemon = False  # Set to False to allow child processes
        self.process.start()

        # Poll for results in a separate thread
        threading.Thread(target=self._monitor_process, daemon=True).start()
        # Poll memmory usage
        threading.Thread(
            target=self.measure_memory_consumption,
            daemon=True,
            args=(self.process.pid,),
        ).start()

    def measure_memory_consumption(self, pid: int):
        while self.process.is_alive():
            process = psutil.Process(pid)
            mem = process.memory_info().rss
            self.maxMemUsed = max(mem, self.maxMemUsed)
            self.sumMemUsed += mem
            self.measuresMemUsed += 1
            time.sleep(1)

    def _monitor_process(self):
        """Monitor the solver process and get result when ready"""
        try:
            result = self.result_queue.get()
            if result:
                unpacked_result = pickle.loads(result)
                if isinstance(unpacked_result, tuple) and len(unpacked_result) == 4:
                    (
                        self.solution,
                        self.start_time,
                        self.stop_time,
                        self.states_processed,
                    ) = unpacked_result
        except:
            self.solution = None
        finally:
            self.running = False

    def start(self):
        """Start the solver process"""
        self.run_solver()

    def is_running(self):
        """Check if solver is still running"""
        return self.running

    def has_solution(self) -> bool:
        return not self.is_running() and self.solution is not None

    def get_solution(self) -> TreeNode:
        if not self.is_running():
            return self.solution
        return None

    def extract_solution(self) -> TreeNode:
        """Return solution if found"""
        if not self.is_running():
            solution = self.solution
            if solution is not None and solution.next is not None:
                self.solution = solution.next[0]
            else:
                self.solution = None
            return solution
        return None

    def set_solver_type(self, solver_type):
        """Change solver type - must be called before start()"""
        if not self.is_running():
            self.solver_type = solver_type.lower()
            return True
        return False


class MoveType:
    foundation = 0
    column = 1


def move_col_col(state: b.Board, from_col: int, to_col: int):
    new_state = state.copy()
    col1 = new_state.columns[from_col]
    col2 = new_state.columns[to_col]
    if new_state.is_valid_move_column_to_column(col1, col2):
        col2.insert(col1.top())
        col1.pop()
        return new_state
    return None


def move_col_foundation(state: b.Board, from_col: int, to_found: int):
    new_state = state.copy()
    col = new_state.columns[from_col]
    found = new_state.foundations[to_found]
    if new_state.is_valid_move_column_to_foundation(col, found):
        found.insert(col.top())
        col.pop()
        return new_state
    return None


def run_ai(game_board):
    v = TreeNode(game_board)
    print("AI running")
    bfsSolver = importlib.import_module("bfsSolver")

    solution = bfsSolver.bfs(v)

    if solution != None:
        print("Solution found")
        v = solution
        depth = 0
        while v.parent != None:
            data = AsyncSolver.learn.get(hash(v.state))
            if data == None or depth < data:
                AsyncSolver.learn[hash(v.state)] = depth
            depth += 1
            parent = v.parent
            parent.next = (v, parent.children[v])
            v = parent
        return v
    else:
        print("Solution not found")
        return None


def get_possible_moves(board) -> list[tuple[str, int, int]]:
    """Returns a prioritized list of possible moves in the given board state."""
    moves = []
    minLen = min([len(found.cards) for found in board.foundations])
    # Move Aces to the Foundation First**
    for i, col in enumerate(board.columns):
        if not col.is_empty() and col.top().cardValue.value == (minLen + 1):
            for f, foundation in enumerate(board.foundations):
                if board.is_valid_move_column_to_foundation(col, foundation):
                    return [(MoveType.foundation, i, f)]

    for i, col in enumerate(board.columns):
        for f, foundation in enumerate(board.foundations):
            if board.is_valid_move_column_to_foundation(col, foundation):
                moves.append((MoveType.foundation, i, f))

    for i, col1 in enumerate(board.columns):
        for f, col2 in enumerate(board.columns):
            if i != f and board.is_valid_move_column_to_column(col1, col2):
                moves.append((MoveType.column, i, f))

    return moves
