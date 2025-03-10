import pygame
from controller import BoardController

class BFSSolver:
    def __init__(self, game_board: BoardController):
        self.game_board = game_board  # Store the game board

    def run_ai(self, screen):
        """Runs the AI by making moves continuously until no valid moves remain."""
        running = True

        while running:
            pygame.event.pump()  # Allow quitting events
            screen.fill((0, 128, 0))  # Green background

            moves = self.get_possible_moves(self.game_board.model)

            if not moves:
                print("No more valid moves. AI stopped.")
                break  # Stop AI when no more moves exist

            move_made = False
            for move in moves:
                if self.apply_move(self.game_board, move):  # ✅ Apply move
                    self.game_board.update(screen)  # ✅ Redraw board
                    pygame.display.update()  # ✅ Ensure UI refreshes
                    pygame.time.delay(500)  # ✅ Slow down for visibility
                    move_made = True
                    break  # ✅ Apply one move per loop, then refresh

            if not move_made:
                print("No more valid moves. AI stopped.")
                break

        self.game_board.update(screen)  # ✅ Force final UI update
        pygame.display.update()


    def get_possible_moves(self, board):
        """Returns a list of possible moves in the given board state."""
        moves = []

        # ✅ Move Aces to the Foundation First (only once)
        for i, col in enumerate(board.columns):
            if not col.is_empty() and col.top().cardValue.value == 1:  # Check if Ace
                for f, foundation in enumerate(board.foundations):
                    if board.is_valid_move_column_to_foundation(col, foundation):  
                        print(f"✅ Moving Ace from Column {i} to Foundation {f}")
                        return [("foundation", i, f)]  # ✅ Return immediately

        # ✅ Move Other Cards to Foundation
        for i, col in enumerate(board.columns):
            if not col.is_empty():
                for f, foundation in enumerate(board.foundations):
                    if board.is_valid_move_column_to_foundation(col, foundation):  
                        print(f"✅ Moving {col.top()} from Column {i} to Foundation {f}")
                        return [("foundation", i, f)]  # ✅ Return immediately

        # ✅ Move Cards Between Columns
        for i, from_col in enumerate(board.columns):
            if from_col.is_empty():
                continue
            for j, to_col in enumerate(board.columns):
                if i != j and board.is_valid_move_column_to_column(from_col, to_col):  
                    print(f"✅ Moving {from_col.top()} from Column {i} to Column {j}")
                    return [("column", i, j)]  # ✅ Return immediately

        return moves


    def apply_move(self, game_board, move):
        """Applies an AI move and ensures board updates properly."""
        move_type, from_idx, to_idx = move
        success = False

        if move_type == "column":
            from_col = game_board.columns[from_idx]
            to_col = game_board.columns[to_idx]

            if not from_col.is_empty():
                moved_card = from_col.cards[-1]  # ✅ Get top card
                success = game_board.model.move_card_column_to_column_ai(from_col.model, to_col.model)
                if success:
                    from_col.cards.pop()  # ✅ Remove from original column
                    from_col.view.cards.pop()  # ✅ Remove from UI
                    to_col.cards.append(moved_card)  # ✅ Add to new column
                    to_col.view.cards.append(moved_card.view)  # ✅ Add to UI

        elif move_type == "foundation":
            from_col = game_board.columns[from_idx]
            foundation = game_board.foundations[to_idx]

            if not from_col.is_empty():
                moved_card = from_col.cards[-1]  # ✅ Get top card
                success = game_board.model.move_card_column_to_foundation_ai(from_col.model, foundation.model)
                if success:
                    from_col.cards.pop()  # ✅ Remove from original column
                    from_col.view.cards.pop()  # ✅ Remove from UI
                    foundation.cards.append(moved_card)  # ✅ Add to foundation
                    foundation.view.cards.append(moved_card.view)  # ✅ Add to UI

        if success:
            print(f"✅ AI moved {move}, updating board")
            game_board.update_model()  # ✅ Ensure board logic updates
            game_board.update(pygame.display.get_surface())  # ✅ Force UI refresh
            pygame.display.update()  # ✅ Ensure UI updates

        return success

