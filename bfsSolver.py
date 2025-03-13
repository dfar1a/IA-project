import board as b
import cards as c
from controller import BoardController
from collections import deque
from heapq import *
import pickle
import threading


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
        self.thread = threading.Thread(target=self.run_bfs)
        self.running = False

    def stop(self):
        AsyncBFSSolver._stop = True

    def save_data(self):
        save_data_pickle("learn.data", self.learn)

    def run_bfs(self):
        """Executa BFS em background sem bloquear o jogo."""
        AsyncBFSSolver._stop = False
        self.running = True
        self.solution = BFSSolver.run_ai(self.initstate)
        self.running = False

    def start(self):
        """Inicia a pesquisa BFS numa thread separada."""
        self.thread.start()

    def is_running(self):
        """Verifica se a pesquisa ainda está a decorrer."""
        return self.running

    def get_solution(self):
        """Retorna a solução se já tiver sido encontrada."""
        if not self.is_running():
            solution = self.solution
            if solution != None and solution.next != None:
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

        for column in state.columns:
            cards = column.cards

            #         score += 0.5 * (cards[i + 1].cardSuite != cards[i].cardSuite)

            for i, card in enumerate(cards):
                if card in nextCards:
                    score += 2 * (len(cards) - i - 1) ** 1.5

        score += 13 * 4 - sumLen

        return score

    def __init__(self, state: b.Board, parent=None):
        self.state = state
        self.parent = parent
        self.children = dict()
        self.next = None
        self.score = TreeNode.evaluate(state)

    def add_child(self, child_node, transition):
        self.children[child_node] = transition
        child_node.parent = self

    def __lt__(self, other):
        return isinstance(other, TreeNode) and self.score < other.score


class BFSSolver:

    @staticmethod
    def bfs(root: TreeNode) -> TreeNode | None:
        visited_states = set()
        queue = [root]
        move_card = {
            MoveType.foundation: move_col_foundation,
            MoveType.column: move_col_col,
        }
        visited_states.add(hash(root.state))

        while queue and len(visited_states) < 5 * 10**4 and not AsyncBFSSolver._stop:
            current_board = heappop(queue)

            if current_board.state.is_game_won():
                return current_board

            moves = BFSSolver.get_possible_moves(current_board.state)

            for move in moves:
                state = move_card[move[0]](current_board.state, move[1], move[2])

                if state != None and hash(state) not in visited_states:
                    node = TreeNode(state)
                    if node.score < 0:
                        print("Known state")
                    current_board.add_child(node, move)
                    visited_states.add(hash(state))
                    heappush(queue, node)

        return None

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

    @staticmethod
    def run_ai(game_board):
        v = TreeNode(game_board)
        print("AI running")
        solution = BFSSolver.bfs(v)

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

    @staticmethod
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
        # # Free Aces (Move Blocking Cards)**
        # aces_blocked = BFSSolver.get_blocked_aces(board)
        # for ace_col in aces_blocked:
        #     if not board.columns[ace_col].is_empty():
        #         top_card = board.columns[ace_col].top()
        #         for target_col in range(len(board.columns)):
        #             if ace_col != target_col and board.is_valid_move_column_to_column(
        #                 board.columns[ace_col], board.columns[target_col]
        #             ):
        #                 print(
        #                     f"✅ Moving {top_card} from Column {ace_col} to Column {target_col} to free Ace"
        #                 )
        #                 moves.append((MoveType.column, ace_col, target_col))

        # # Move Next Sequential Cards to the Foundation (Ordered by Suit)**
        # for f, foundation in enumerate(board.foundations):
        #     if not foundation.is_empty():
        #         next_card_value = foundation.top().cardValue.value + 1
        #         sorted_columns = sorted(
        #             enumerate(board.columns),
        #             key=lambda x: (
        #                 x[1].top().cardSuite.value
        #                 if not x[1].is_empty()

        #                 else float("inf")
        #             ),
        #         )

        #         for i, col in sorted_columns:
        #             if (
        #                 not col.is_empty()
        #                 and col.top().cardValue.value == next_card_value
        #             ):
        #                 if board.is_valid_move_column_to_foundation(col, foundation):
        #                     print(
        #                         f"✅ Moving {col.top()} from Column {i} to Foundation {f}"
        #                     )
        #                     moves.append((MoveType.foundation, i, f))

        # # Smart Column Moves (Only If It Helps Foundation)**
        # if not moves:
        #     for i, from_col in enumerate(board.columns):
        #         if from_col.is_empty():
        #             continue
        #         for j, to_col in enumerate(board.columns):
        #             if i != j and board.is_valid_move_column_to_column(
        #                 from_col, to_col
        #             ):
        #                 # ✅ Check if this move actually helps free a foundation move
        #                 if BFSSolver.will_help_foundation(board, from_col, to_col):
        #                     print(
        #                         f"✅ Moving {from_col.top()} from Column {i} to Column {j}"
        #                     )
        #                     moves.append((MoveType.column, i, j))

        return moves

    @staticmethod
    def get_blocked_aces(board):
        """Finds columns where an Ace is blocked by another card."""
        blocked_aces = []
        for i, col in enumerate(board.columns):
            if not col.is_empty():
                top_card = col.top()
                if top_card.cardValue.value == c.CardValue.ace:
                    continue
                for card in col.cards:
                    if card.cardValue.value == c.CardValue.ace:
                        blocked_aces.append(i)
                        break
        return blocked_aces

    @staticmethod
    def will_help_foundation(board, from_col, to_col):
        """Determines if moving a card will help unlock a foundation move."""
        # Check if the move frees up a card that can be moved to a foundation
        if from_col.is_empty() or to_col.is_empty():
            return False

        from_card = from_col.top()
        to_card = to_col.top()

        # If moving this card will expose a card that can go to foundation, do it
        if from_col.n_cards() > 1:
            below_card = from_col.cards[-2]
            for foundation in board.foundations:
                if board.is_valid_move_column_to_foundation(from_col, foundation):
                    return True

        # If moving this card allows another move that will expose an Ace, do it
        if BFSSolver.get_blocked_aces(board):
            return True

        return False

    @staticmethod
    def board_to_string(board) -> str:
        """Converts the board state into a string representation for tracking."""
        return (
            "|".join("".join(str(card) for card in col.cards) for col in board.columns)
            + "||"
            + "|".join(
                "".join(str(card) for card in f.cards) for f in board.foundations
            )
        )
