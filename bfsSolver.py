import solver
from heapq import *
import signal


class BFS:
    def __init__(self):
        self.visited_states = set()
        self._stop_flag = False

    def set_stop_flag(self):
        self._stop_flag = True

    def should_stop(self):
        # Check both our internal flag and AsyncSolver's flag
        return self._stop_flag or solver.AsyncSolver._stop

    def bfs(self, root: solver.TreeNode) -> list[solver.TreeNode]:
        move_card = {
            solver.MoveType.foundation: solver.move_col_foundation,
            solver.MoveType.column: solver.move_col_col,
        }
        pq = [root]
        self.visited_states.add(hash(root.state))

        # Check if we should stop
        while pq and not self.should_stop():
            print(len(pq))
            explored_node = pq.pop(0)
            if explored_node.state.is_game_won():
                return explored_node
            moves = solver.get_possible_moves(explored_node.state)

            for move in moves:
                # Check if we should stop

                state = move_card[move[0]](explored_node.state, move[1], move[2])

                if state is not None and hash(state) not in self.visited_states:
                    self.visited_states.add(hash(explored_node.state))
                    node = solver.TreeNode(state, explored_node)
                    explored_node.add_child(node, move)
                    pq.append(node)

        return None


# This function is used by the AsyncSolver to run IDA*
def run_bfs(board):
    solver = BFS()

    def signal_handler(*args):
        solver.set_stop_flag()

    signal.signal(signal.SIGTERM, signal_handler)

    return solver.bfs(board)
