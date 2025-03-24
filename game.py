import pygame
import cards as c
import view as v
import controller as control
from solver import AsyncBFSSolver, execute_next_move

# Increased window size for better spacing and proper alignment
WIDTH = 1400
HEIGHT = 1000


class SolitaireGame:
    def __init__(self, use_ai=False):
        # Game state variables
        self.use_ai = use_ai
        self.running = True
        self.ai_paused = False

        # Card interaction variables
        self.selected_card = None
        self.original_column = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Initialize pygame components
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Game components
        self.game_board = control.BoardController()

        # AI solver
        self.solver = AsyncBFSSolver(self.game_board)
        self.solver.start()
        self.board_state = hash(self.game_board.model)

    def handle_events(self):
        """Handle pygame events and user interactions"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

        # Update dragging card position if needed
        if self.dragging and self.selected_card:
            self.selected_card.view.dest = self.selected_card.view.pos = (
                mouse_x - self.drag_offset_x,
                mouse_y - self.drag_offset_y,
            )

    def handle_mouse_down(self, event):
        """Handle mouse button down events"""
        card, column = self.game_board.get_clicked_card(event.pos[0], event.pos[1])

        if card:
            self.game_board.selectedCard = card
            col_x, col_y = column.view.pos
            self.selected_card = card
            self.original_column = column
            self.dragging = True
            self.drag_offset_x = event.pos[0] - col_x
            self.drag_offset_y = event.pos[1] - (
                col_y + (column.model.n_cards() - 1) * column.view.gap
            )
            self.ai_paused = True  # Pause the AI when dragging starts

    def handle_mouse_up(self, event):
        """Handle mouse button up events"""

        self.game_board.selectedCard = None

        if not self.selected_card:
            return

        valid_move = self.try_move_to_column(event.pos) or self.try_move_to_foundation(
            event.pos
        )

        # If move is invalid, return card to original column
        if not valid_move:
            # Calculate the correct position in the original column
            col_x, col_y = self.original_column.view.pos
            card_index = len(self.original_column.cards) - 1
            target_y = col_y + (card_index * self.original_column.view.gap)

            # Set the destination for animation instead of immediate insertion
            self.selected_card.view.dest = (
                self.original_column.view.pos[0],
                self.original_column.view.pos[1]
                + self.original_column.view.height
                - v.CardView.height
                + self.original_column.view.gap,
            )
            self.original_column.insert(self.selected_card)

        # Reset dragging state
        self.selected_card = None
        self.dragging = False
        self.ai_paused = False  # Resume the AI when dragging stops

    def try_move_to_column(self, pos):
        """Try to move the selected card to a column"""
        for col in self.game_board.columns:
            col_x, col_y = col.view.pos
            if (
                col_x <= pos[0] <= col_x + v.CardView.width
                and col_y <= pos[1] <= col_y + col.view.height
            ):
                if self.game_board.move_card_column_column(self.original_column, col):
                    return True
        return False

    def try_move_to_foundation(self, pos):
        """Try to move the selected card to a foundation"""
        for foundation in self.game_board.foundations:
            found_x, found_y = foundation.view.pos
            if (
                found_x <= pos[0] <= found_x + v.CardView.width
                and found_y <= pos[1] <= found_y + v.CardView.height
            ):
                if self.game_board.move_card_column_foundation(
                    self.original_column, foundation
                ):
                    return True
        return False

    def update_ai(self):
        """Update AI solver state and execute AI moves"""
        if self.ai_paused or not self.use_ai:
            return

        # Check if it's time to make an AI move
        if pygame.time.get_ticks() % 500 < self.clock.get_time():
            state = self.solver.get_solution()

            if state is not None:
                execute_next_move(state, self.game_board)
                self.board_state = hash(self.game_board.model)
            elif hash(self.game_board.model) != self.board_state:
                # Board state changed by user, restart solver
                self.solver.stop()
                self.solver = AsyncBFSSolver(self.game_board)
                self.solver.start()
                self.board_state = hash(self.game_board.model)

    def run(self):
        """Main game loop"""
        while self.running:
            self.update_ai()
            self.game_board.update(self.screen)
            self.handle_events()
            pygame.display.update()
            self.clock.tick(60)

        self.solver.save_data()
        pygame.quit()


def main(use_ai=False):
    game = SolitaireGame(use_ai)
    game.run()


if __name__ == "__main__":
    main()
