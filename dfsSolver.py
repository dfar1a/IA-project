import solver
from heapq import *
import signal


class DFS:
    def __init__(self, board):
        self.visited_states = set()
        self.root = solver.TreeNode(board)
        self._stop_flag = False

    def set_stop_flag(self):
        self._stop_flag = True

    def should_stop(self):
        # Check both our internal flag and AsyncSolver's flag
        return self._stop_flag or solver.AsyncSolver._stop

    def dfs(self, root: solver.TreeNode) -> list[solver.TreeNode]:
        move_card = {
            solver.MoveType.foundation: solver.move_col_foundation,
            solver.MoveType.column: solver.move_col_col,
        }
        self.visited_states.add(hash(root.state))
        pq = []

        if root.state.is_game_won():
            self.set_stop_flag()
            return root

        # Check if we should stop
        if self.should_stop():
            return None

        moves = solver.get_possible_moves(root.state)

        for move in moves:
            # Check if we should stop
            if self.should_stop():
                return None

            state = move_card[move[0]](root.state, move[1], move[2])

            if state is not None and hash(state) not in self.visited_states:
                node = solver.TreeNode(state, root)
                root.add_child(node, move)
                pq.append(node)

        sol = None
        while pq and not self.should_stop():
            node = pq.pop()
            sol = self.dfs(node) if sol is None else sol

        return sol


# This function is used by the AsyncSolver to run IDA*
def run_dfs(board):
    solver = DFS(board)

    def signal_handler(*args):
        solver.set_stop_flag()

    signal.signal(signal.SIGTERM, signal_handler)

    return solver.dfs(solver.root)
