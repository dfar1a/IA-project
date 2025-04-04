import solver
from heapq import *
import signal
import time


class IDAStar:
    def __init__(self, board):
        self.visited_states = set()
        self.height = 10
        self.root = solver.TreeNode(board)
        self._stop_flag = False

    def set_stop_flag(self):
        self._stop_flag = True

    def should_stop(self):
        # Check both our internal flag and AsyncSolver's flag
        return self._stop_flag or solver.AsyncSolver._stop

    def dfs(self, root: solver.TreeNode, depth: int) -> list[solver.TreeNode]:
        leaves = []
        move_card = {
            solver.MoveType.foundation: solver.move_col_foundation,
            solver.MoveType.column: solver.move_col_col,
        }
        self.visited_states.add(hash(root.state))
        pq = []

        if root.state.is_game_won():
            return [root]

        if depth == self.height:
            return [root]

        # Check if we should stop
        if self.should_stop():
            return []

        moves = solver.get_possible_moves(root.state)

        for move in moves:
            # Check if we should stop
            if self.should_stop():
                return []

            state = move_card[move[0]](root.state, move[1], move[2])

            if state is not None and hash(state) not in self.visited_states:
                node = solver.TreeNode(state)
                root.add_child(node, move)
                heappush(pq, node)

        while pq and not self.should_stop():
            node = heappop(pq)
            leaves.extend(self.dfs(node, depth + 1))

            # Periodically check if we should stop
            if len(leaves) % 100 == 0 and self.should_stop():
                return leaves

        return leaves

    def runIDAS(self):
        """Run IDA* search with periodic checks to stop if requested"""
        queue = self.dfs(self.root, 0)
        heapify(queue)

        iterations = 0
        while queue and not self.should_stop():
            current_state = heappop(queue)

            if current_state.state.is_game_won():
                return current_state

            for leaf in self.dfs(current_state, 0):
                heappush(queue, leaf)

            iterations += 1
            if iterations % 10 == 0:
                # Periodically give up control to allow checking stop flag
                time.sleep(0.001)

        return None


# This function is used by the AsyncSolver to run IDA*
def run_idastar(board):
    ida = IDAStar(board)

    def signal_handler(*args):
        ida.set_stop_flag()

    signal.signal(signal.SIGTERM, signal_handler)

    return ida.runIDAS()
