from heapq import *
import solver


def bfs(root: solver.TreeNode) -> solver.TreeNode | None:
    visited_states = set()
    queue = [root]
    move_card = {
        solver.MoveType.foundation: solver.move_col_foundation,
        solver.MoveType.column: solver.move_col_col,
    }
    visited_states.add(hash(root.state))

    while queue and len(visited_states) < 5 * 10**4 and not solver.AsyncBFSSolver._stop:
        current_board = heappop(queue)

        if current_board.state.is_game_won():
            return current_board

        moves = solver.get_possible_moves(current_board.state)
        i = 0

        for move in moves:
            if i >= 5:
                break
            state = move_card[move[0]](current_board.state, move[1], move[2])

            if state != None and hash(state) not in visited_states:
                node = solver.TreeNode(state)
                if node.score < 0:
                    print("Known state")
                current_board.add_child(node, move)
                visited_states.add(hash(state))
                heappush(queue, node)
                i += 1

    return None
