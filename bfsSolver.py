import pygame
from controller import BoardController

class BFSSolver:
    def run_ai(game_board):
        """Runs the AI by making moves continuously until no valid moves remain."""
        moves = BFSSolver.get_possible_moves(game_board.model)

        if not moves:
            print("No more valid moves. AI stopped.")
              # Stop AI when no more moves exist

        if moves:
            move = moves[0]
                #if self.apply_move(self.game_board, move):  # ✅ Apply move
            if move[0] == "foundation":
                game_board.move_card_column_foundation(game_board.columns[move[1]], game_board.foundations[move[2]])
            elif move[0] == "column":
                game_board.move_card_column_column(game_board.columns[move[1]], game_board.columns[move[2]])
            moves.remove(move)
        else:
                print("No more valid moves. AI stopped.")
            

    def get_possible_moves(board)->list[tuple[str, int, int]]:
        """Returns a list of possible moves in the given board state."""
        moves = []

        # ✅ Move Aces to the Foundation First (only once)
        for i, col in enumerate(board.columns):
            if not col.is_empty() and col.top().cardValue.value == 1:  # Check if Ace
                for f, foundation in enumerate(board.foundations):
                    if board.is_valid_move_column_to_foundation(col, foundation):  
                        print(f"✅ Moving Ace from Column {i} to Foundation {f}")
                        moves.append(("foundation", i, f))  # ✅ Return immediately

        # ✅ Move Other Cards to Foundation
        for i, col in enumerate(board.columns):
            if not col.is_empty():
                for f, foundation in enumerate(board.foundations):
                    if board.is_valid_move_column_to_foundation(col, foundation):  
                        print(f"✅ Moving {col.top()} from Column {i} to Foundation {f}")
                        moves.append(("foundation", i, f))  # ✅ Return immediately

        # ✅ Move Cards Between Columns
        for i, from_col in enumerate(board.columns):
            if from_col.is_empty():
                continue
            for j, to_col in enumerate(board.columns):
                if i != j and board.is_valid_move_column_to_column(from_col, to_col):  
                    print(f"✅ Moving {from_col.top()} from Column {i} to Column {j}")
                    moves.append(("column", i, j))  # ✅ Return immediately

        return moves
