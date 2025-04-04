import pygame
import cards as c
import view as v
import controller as control
from solver import AsyncSolver, execute_next_move, get_next_move
import utils
from stopwatch import Stopwatch
from pause_menu import PauseMenu
import json
# Increased window size for better spacing and proper alignment
WIDTH = 1400
HEIGHT = 1000


class SolitaireGame:
    def __init__(self, use_ai=False):
        # Game state variables
        self.use_ai = use_ai
        self.running = True
        self.return_to_menu = False
        self.ai_paused = False
        self.game_paused = False

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
        self.game_stopwatch = Stopwatch()
        self.game_stopwatch.start()

        # Game components
        self.game_board = control.BoardController()
        self.game_bar = v.GameBar(self)

        # AI solver
        self.solver = AsyncSolver(self.game_board)
        self.solver.start()
        self.board_state = hash(self.game_board.model)

        # Create pause menu
        self.pause_menu = PauseMenu((WIDTH, HEIGHT))
        self.pause_menu.set_callbacks(
            resume_cb=self.pause_play,  # Resume game
            new_game_cb=self.new_game,  # Reset game
            main_menu_cb=self.return_to_main_menu,  # Go back to main menu
            exit_cb=self.exit_game,  # Exit game
        )

    def toggle_ai(self):
        self.use_ai = not self.use_ai

    def pause_play(self):
        """Toggle game pause state"""
        if self.pause_menu.active:
            self.pause_menu.hide()
            self.game_stopwatch.start()
        else:
            self.pause_menu.show()
            self.game_stopwatch.stop()

        self.game_paused = self.pause_menu.active

    def new_game(self):
        """Reset the game to a new state"""
        self.game_board = control.BoardController()
        self.game_stopwatch.reset()
        self.game_stopwatch.start()
        self.solver.stop()
        self.solver = AsyncSolver(self.game_board)
        self.solver.start()
        self.board_state = hash(self.game_board.model)
        self.game_paused = False
        self.pause_menu.hide()

    def exit_game(self):
        """Close the game"""
        self.running = False

    def return_to_main_menu(self):
        """Return to the main menu"""
        self.running = False
        self.return_to_menu = True  # Flag to indicate we want to return to menu

        # Clean up resources
        self.solver.stop()
        self.solver.save_data()

    def handle_events(self):
        """Handle pygame events and user interactions"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # Check pause menu events first
            if self.pause_menu.handle_event(event):
                continue

            self.game_bar.check_click(event)

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.pause_play()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_paused:
                self.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP and not self.game_paused:
                self.handle_mouse_up()

        # Update dragging card position if needed and not paused
        if self.dragging and self.selected_card and not self.game_paused:
            self.selected_card.view.dest = self.selected_card.view.pos = (
                mouse_x - self.drag_offset_x,
                mouse_y - self.drag_offset_y,
            )

    def handle_mouse_down(self, event):
        """Handle mouse button down events"""
        if self.game_paused:
            return
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

    def handle_mouse_up(self):
        """Handle mouse button up events"""

        self.game_board.selectedCard = None

        if not self.selected_card:
            return

        valid_move = self.try_move_to_column() or self.try_move_to_foundation()

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
                + self.original_column.view.size[1]
                - v.CardView.height,
            )
            self.original_column.insert(self.selected_card)

        # Reset dragging state
        self.selected_card = None
        self.dragging = False
        self.ai_paused = False  # Resume the AI when dragging stops

    def try_move_to_column(self):
        """Try to move the selected card to a column"""
        for col in self.game_board.columns:
            if utils.collide(
                col.view.pos,
                col.view.size,
                self.selected_card.view.pos,
                (v.CardView.width, v.CardView.height),
            ):
                if self.game_board.move_card_column_column(self.original_column, col):
                    return True
        return False

    def try_move_to_foundation(self):
        """Try to move the selected card to a foundation"""
        for foundation in self.game_board.foundations:
            if utils.collide(
                foundation.view.pos,
                foundation.view.size,
                self.selected_card.view.pos,
                (v.CardView.width, v.CardView.height),
            ):
                if self.game_board.move_card_column_foundation(
                    self.original_column, foundation
                ):
                    return True
        return False

    def set_hint(self):
        print("hint")
        sol = self.solver.get_solution()
        if sol is not None:
            get_next_move(sol, self.game_board).view.glow(True)

    def update_ai(self):
        """Update AI solver state and execute AI moves"""
        if self.solver.has_solution():
            self.game_bar.ai_ready(True)
        else:
            self.game_bar.ai_ready(False)

        if hash(self.game_board.model) != self.board_state:
            # Board state changed by user, restart solver
            self.game_bar.ai_ready(False)
            self.solver.stop()
            self.solver = AsyncSolver(self.game_board)
            self.solver.start()
            self.board_state = hash(self.game_board.model)

        if self.ai_paused or not self.use_ai or self.game_paused:
            return

        # Check if it's time to make an AI move
        if pygame.time.get_ticks() % 500 < self.clock.get_time():
            state = self.solver.extract_solution()

            if state is not None:
                execute_next_move(state, self.game_board)
                self.board_state = hash(self.game_board.model)

    def cleanup(self):
        """Clean up all game resources"""
        if hasattr(self, "solver") and self.solver:
            self.solver.stop()
            self.solver.save_data()

    def display_win_message(self):
        # Get the time in seconds
        elapsed_ms = pygame.time.get_ticks()
        elapsed_time = elapsed_ms // 1000  # whole seconds
        time_str = f"{elapsed_time}s"

        font = pygame.font.Font(None, 80)
        small_font = pygame.font.Font(None, 40)

        message = font.render("🎉 You Won! 🎉", True, (255, 255, 0))
        message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))

        # Input setup
        input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 70, 300, 50)
        name = ""
        input_color = pygame.Color("dodgerblue2")

        # Buttons
        button_font = pygame.font.Font(None, 50)
        play_button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 320, 70)
        menu_button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 100, 320, 70)
        play_text = button_font.render("Play Again", True, (0, 0, 0))
        menu_text = button_font.render("Main Menu", True, (0, 0, 0))

        while True:
            self.screen.fill((0, 128, 0))
            self.game_board.update(self.screen)
            self.game_bar.draw(self.screen)

            # Draw win message and input prompt
            self.screen.blit(message, message_rect)
            prompt = small_font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(prompt, (input_box.x, input_box.y - 35))

            name_text = small_font.render(name, True, input_color)
            self.screen.blit(name_text, (input_box.x + 5, input_box.y + 10))
            pygame.draw.rect(self.screen, input_color, input_box, 2)

            # Draw buttons
            pygame.draw.rect(self.screen, (255, 215, 0), play_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 165, 0), menu_button_rect, border_radius=10)
            self.screen.blit(play_text, play_text.get_rect(center=play_button_rect.center))
            self.screen.blit(menu_text, menu_text.get_rect(center=menu_button_rect.center))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.save_score(name.strip() or "Anonymous", time_str)
                        self.new_game()
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 20:
                            name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        self.save_score(name.strip() or "Anonymous", time_str)
                        self.new_game()
                        return
                    elif menu_button_rect.collidepoint(event.pos):
                        self.save_score(name.strip() or "Anonymous", time_str)
                        self.return_to_main_menu()
                        return


    def save_score(self, name, time_str):
        data = {"name": name, "time": time_str}
        try:
            with open("scores.json", "r") as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = []

        scores.append(data)

        with open("scores.json", "w") as f:
            json.dump(scores, f, indent=4)

    def run(self):
        """Main game loop"""
        try:
            while self.running:
                # Handle events first (user input)
                self.handle_events()

                # Update game board (handles animations)
                self.game_board.update(self.screen)
                self.game_bar.draw(self.screen)

                # Update AI after game board update (so animations have started)
                self.update_ai()

                # Draw pause menu on top if active
                self.pause_menu.draw(self.screen)

                # Final display refresh
                pygame.display.update()
                self.clock.tick(60)

               # Add this inside your main loop, after everything is drawn:
                # Check both model AND view are fully synced to Kings on foundations
                if self.game_board.model.is_game_won() and self.game_board.is_game_won_visual():
                    self.game_stopwatch.stop() 
                    self.display_win_message()

        finally:
            # Always clean up resources, even if there's an error
            self.cleanup()


def main():
    """Main game entry point"""
    # Initialize pygame if it's not already initialized
    if not pygame.get_init():
        pygame.init()

    keep_running = True
    while keep_running:
        # Create and run game
        game = SolitaireGame()
        game.run()

        # Check if we should return to the main menu
        if game.return_to_menu:
            # Import here to avoid circular imports
            import menu

            # Call menu and get its return action
            action = menu.menu()

            # Process the menu's return action
            if action == "START_GAME":
                # We'll start a new game in the next loop iteration
                continue
            elif action == "QUIT":
                # Exit the game loop
                keep_running = False
        else:
            # Normal exit (not returning to menu)
            keep_running = False

    # Final cleanup
    pygame.quit()


if __name__ == "__main__":
    main()