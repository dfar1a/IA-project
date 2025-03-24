import pickle
import threading
import board as b
import cards as c
from controller import BoardController
from heapq import *
import random
import importlib
import multiprocessing


class TreeNode:
    def evaluate(state: b.Board):
        cost = AsyncBFSSolver.learn.get(hash(state))
        if cost != None:
            return -(10**3) // (cost + 1)

        score = 0
        nextCards = {
            (
                c.Card(found.top().next, found.top().cardSuite)
                if found.top() is not None
                else c.Card(c.CardValue.ace, found.suite)
            )
            for found in state.foundations
        }

        lenFounds = [len(found.cards) for found in state.foundations]
        sumLen = sum(lenFounds)
        minLen = min(lenFounds)
        maxLen = max(lenFounds)

        for column in state.columns:
            cards = column.cards

            # for i in range(len(cards) - 1):
            #     score += 0.2 * (cards[i + 1].cardSuite != cards[i].cardSuite)

            for i, card in enumerate(cards):
                if card in nextCards:
                    score += 2 ** (len(cards) - i - 1)

        score += 13 * 4 - sumLen

        return score + random.random()

    def __init__(self, state: b.Board, parent=None):
        self.state = state
        self.parent = parent
        self.children = dict()
        self.next = None
        self.score = TreeNode.evaluate(state)
        self.actualCost = self.setActualCost()

    def setActualCost(self):
        if self.parent is not None:
            return self.parent.actualCost + 1
        else:
            return 0

    def add_child(self, child_node, transition):
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


def save_data_pickle(filename, data):
    with open(filename, "wb") as file:
        pickle.dump(data, file)


def load_data_pickle(filename):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except:
        return dict()


class AsyncBFSSolver:
    learn = load_data_pickle("learn.data")
    _stop = False

    def __init__(self, game_board):
        self.initstate = game_board.model
        self.solution = None
        self.process = None
        self.running = False
        self.result_queue = multiprocessing.Queue()

    def stop(self):
        AsyncBFSSolver._stop = True
        if self.process and self.process.is_alive():
            self.process.terminate()

    def save_data(self):
        save_data_pickle("learn.data", self.learn)

    def _run_bfs_process(self, initstate, result_queue):
        """Execute BFS in a separate process and put result in queue"""
        AsyncBFSSolver._stop = False
        print("AI process running")
        v = TreeNode(initstate)
        bfsSolver = importlib.import_module("bfsSolver")
        solution = bfsSolver.bfs(v)

        if solution:
            print("Process found solution")
            # Process the solution to create next moves
            depth = 0
            v = solution
            while v.parent is not None:
                data = AsyncBFSSolver.learn.get(hash(v.state))
                if data is None or depth < data:
                    AsyncBFSSolver.learn[hash(v.state)] = depth
                depth += 1
                parent = v.parent
                parent.next = (v, parent.children[v])
                v = parent

            # Put the initial solution node in queue
            result_queue.put(pickle.dumps(v))
        else:
            result_queue.put(None)

    def run_bfs(self):
        """Start the BFS in a separate process"""
        AsyncBFSSolver._stop = False
        self.running = True
        # Create a non-daemon process
        self.process = multiprocessing.Process(
            target=self._run_bfs_process, args=(self.initstate, self.result_queue)
        )
        self.process.daemon = False  # Set to False to allow child processes
        self.process.start()

        # Poll for results in a separate thread
        threading.Thread(target=self._monitor_process, daemon=True).start()

    def _monitor_process(self):
        """Monitor the BFS process and get result when ready"""
        try:
            result = self.result_queue.get(timeout=120)  # 2 minute timeout
            if result:
                self.solution = pickle.loads(result)
        except:
            self.solution = None
        finally:
            self.running = False

    def start(self):
        """Start the BFS process"""
        self.run_bfs()

    def is_running(self):
        """Check if BFS is still running"""
        if self.process:
            return self.process.is_alive() and self.running
        return self.running

    def get_solution(self):
        """Return solution if found"""
        if not self.is_running():
            solution = self.solution
            if solution is not None and solution.next is not None:
                self.solution = solution.next[0]
            else:
                self.solution = None
            return solution
        return None


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
            data = AsyncBFSSolver.learn.get(hash(v.state))
            if data == None or depth < data:
                AsyncBFSSolver.learn[hash(v.state)] = depth
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
