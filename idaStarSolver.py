import solver
from heapq import *


class TreeNode(solver.TreeNode):
    def __lt__(self, other):
        return isinstance(other, TreeNode) and (self.actualCost) < (other.actualCost)


class IDAStar:
    def __init__(self, board):
        self.visited_states = set()
        self.height = 1
        self.root = TreeNode(board)

    def dfs(self, root: solver.TreeNode, depth: int) -> list[solver.TreeNode]:
        leaves = []
        move_card = {
            solver.MoveType.foundation: solver.move_col_foundation,
            solver.MoveType.column: solver.move_col_col,
        }
        self.visited_states.add(hash(root.state))
        pq = []

        if root.state.is_game_won() or depth == self.height:
            return [root]

        moves = solver.get_possible_moves(root.state)

        for move in moves:
            state = move_card[move[0]](root.state, move[1], move[2])

            if state != None and hash(state) not in self.visited_states:
                heappush(pq, TreeNode(state))

        while pq and not solver.AsyncBFSSolver._stop:
            node = heappop(pq)
            if node.score < 0:
                print("Known state")
            root.add_child(node, move)
            leaves.extend(self.dfs(node, depth + 1))

        return leaves

    def runIDAS(self):
        queue = self.dfs(self.root, 0)
        heapify(queue)
        while queue:
            current_state = heappop(queue)

            if current_state.state.is_game_won():
                return current_state

            for leaf in self.dfs(current_state, 0):
                heappush(queue, leaf)

        return None
