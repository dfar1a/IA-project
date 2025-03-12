import pygame
import board as b
import cards as c
from controller import BoardController
from collections import deque

class BFSSolver:
    @staticmethod
    def run_ai(game_board):
        """Runs BFS-based AI to solve the game with smarter move prioritization."""
        visited_states = set()
        queue = deque([game_board.model])

        while queue:
            current_board = queue.popleft()
            moves = BFSSolver.get_possible_moves(current_board)

            if not moves:
                print("🎯 No more valid moves. AI stopped.")
                break

            move = moves.pop(0) 
            success = False

            pygame.time.delay(500) 

            if move[0] == "foundation":
                success = game_board.move_card_column_foundation(
                    game_board.columns[move[1]], game_board.foundations[move[2]]
                )
            elif move[0] == "column":
                success = game_board.move_card_column_column(
                    game_board.columns[move[1]], game_board.columns[move[2]]
                )

            if success:
                board_state = BFSSolver.board_to_string(game_board.model)
                if board_state not in visited_states:
                    visited_states.add(board_state)
                    queue.append(game_board.model)

                game_board.update(pygame.display.get_surface())
                pygame.display.update()
            else:
                print(f"❌ Move {move} was invalid, skipping.")

    @staticmethod
    def get_possible_moves(board) -> list[tuple[str, int, int]]:
        """Returns a prioritized list of possible moves in the given board state."""
        moves = []

        #Move Aces to the Foundation First**
        for i, col in enumerate(board.columns):
            if not col.is_empty() and col.top().cardValue.value == c.CardValue.ace:
                for f, foundation in enumerate(board.foundations):
                    if board.is_valid_move_column_to_foundation(col, foundation):
                        print(f"✅ Moving Ace from Column {i} to Foundation {f}")
                        moves.append(("foundation", i, f))

        # Free Aces (Move Blocking Cards)**
        aces_blocked = BFSSolver.get_blocked_aces(board)
        for ace_col in aces_blocked:
            if not board.columns[ace_col].is_empty():
                top_card = board.columns[ace_col].top()
                for target_col in range(len(board.columns)):
                    if ace_col != target_col and board.is_valid_move_column_to_column(
                        board.columns[ace_col], board.columns[target_col]
                    ):
                        print(
                            f"✅ Moving {top_card} from Column {ace_col} to Column {target_col} to free Ace"
                        )
                        moves.append(("column", ace_col, target_col))

        # Move Next Sequential Cards to the Foundation (Ordered by Suit)**
        for f, foundation in enumerate(board.foundations):
            if not foundation.is_empty():
                next_card_value = foundation.top().cardValue.value + 1
                sorted_columns = sorted(
                    enumerate(board.columns),
                    key=lambda x: x[1].top().cardSuite.value if not x[1].is_empty() else float("inf"),
                )

                for i, col in sorted_columns:
                    if not col.is_empty() and col.top().cardValue.value == next_card_value:
                        if board.is_valid_move_column_to_foundation(col, foundation):
                            print(f"✅ Moving {col.top()} from Column {i} to Foundation {f}")
                            moves.append(("foundation", i, f))

        # Smart Column Moves (Only If It Helps Foundation)**
        if not moves:
            for i, from_col in enumerate(board.columns):
                if from_col.is_empty():
                    continue
                for j, to_col in enumerate(board.columns):
                    if i != j and board.is_valid_move_column_to_column(from_col, to_col):
                        # ✅ Check if this move actually helps free a foundation move
                        if BFSSolver.will_help_foundation(board, from_col, to_col):
                            print(f"✅ Moving {from_col.top()} from Column {i} to Column {j}")
                            moves.append(("column", i, j))

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
        #Check if the move frees up a card that can be moved to a foundation
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
        return "|".join(
            "".join(str(card) for card in col.cards) for col in board.columns
        ) + "||" + "|".join(
            "".join(str(card) for card in f.cards) for f in board.foundations
        )
