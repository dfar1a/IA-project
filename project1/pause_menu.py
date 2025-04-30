import pygame
from utils import Button, Label
from typing import List, Callable, Optional, Tuple


class PauseMenu:
    """
    A pause menu overlay with a semi-transparent background.

    The menu displays a set of buttons and can be toggled on/off.
    When active, it renders a semi-transparent overlay on top of the game.
    """

    def __init__(
        self,
        screen_size: Tuple[int, int],
        title: str = "Paused",
        background_alpha: int = 180,  # 0-255 transparency (0=clear, 255=opaque)
    ):
        self.screen_width, self.screen_height = screen_size
        self.title = title
        self.background_alpha = background_alpha
        self.active = False
        self.buttons: List[Button] = []

        # Create semi-transparent overlay surface
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.overlay.fill((30, 30, 40, background_alpha))  # Dark blue-gray with alpha

        # Create title font
        self.title_font = pygame.font.Font(None, 80)
        self.title_label = self.title_font.render(title, True, (255, 255, 255))
        self.title_rect = self.title_label.get_rect(
            center=(self.screen_width // 2, 150)
        )

        # Menu panel dimensions
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (self.screen_width - self.panel_width) // 2
        self.panel_y = (self.screen_height - self.panel_height) // 2

        # Create default buttons
        self.create_default_buttons()

    def create_default_buttons(self):
        """Create the default set of buttons for the pause menu"""
        button_width = 300
        button_height = 70
        button_colors = {"normal": (227, 52, 52), "hover": (255, 56, 56)}
        button_x = (self.screen_width - button_width) // 2
        start_y = self.panel_y + 75  # Start a bit higher to fit all buttons
        button_spacing = 90  # Slightly reduced spacing to fit all buttons

        # Resume button
        self.resume_button = Button(
            text="Resume Game",
            pos=(button_x, start_y),
            size=(button_width, button_height),
            callback=self.toggle,
            effects={
                "gradient": True,
                "shadow": True,
                "hover_animation": True,
                "rounded_corners": 15,
            },
            colors=button_colors,  # Green
        )

        # New Game button
        self.new_game_button = Button(
            text="New Game",
            pos=(button_x, start_y + button_spacing),
            size=(button_width, button_height),
            callback=lambda: None,  # Will be set by game
            effects={
                "gradient": True,
                "shadow": True,
                "hover_animation": True,
                "rounded_corners": 15,
            },
            colors=button_colors,  # Blue
        )

        # Main Menu button
        self.main_menu_button = Button(
            text="Main Menu",
            pos=(button_x, start_y + 2 * button_spacing),
            size=(button_width, button_height),
            callback=lambda: None,  # Will be set by game
            effects={
                "gradient": True,
                "shadow": True,
                "hover_animation": True,
                "rounded_corners": 15,
            },
            colors=button_colors,  # Purple
        )

        # Exit button
        self.exit_button = Button(
            text="Exit Game",
            pos=(button_x, start_y + 3 * button_spacing),
            size=(button_width, button_height),
            callback=lambda: None,  # Will be set by game
            effects={
                "gradient": True,
                "shadow": True,
                "hover_animation": True,
                "rounded_corners": 15,
            },
            colors=button_colors,  # Red
        )

        # Add buttons to list
        self.buttons = [
            self.resume_button,
            self.new_game_button,
            self.main_menu_button,
            self.exit_button,
        ]

    def set_callbacks(
        self,
        resume_cb: Callable,
        new_game_cb: Callable,
        main_menu_cb: Callable,
        exit_cb: Callable,
    ):
        """Set callbacks for the default buttons"""
        self.resume_button.callback = resume_cb
        self.new_game_button.callback = new_game_cb
        self.main_menu_button.callback = main_menu_cb
        self.exit_button.callback = exit_cb

    def add_button(self, button: Button):
        """Add a custom button to the pause menu"""
        self.buttons.append(button)

    def toggle(self):
        """Toggle the pause menu visibility"""
        self.active = not self.active
        return self.active

    def show(self):
        """Show the pause menu"""
        self.active = True

    def hide(self):
        """Hide the pause menu"""
        self.active = False

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events when the menu is active"""
        if not self.active:
            return False

        # Handle button clicks
        for button in self.buttons:
            if button.check_click(event):
                return True

        # Close menu if Escape is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle()
            return True

        return False

    def draw(self, screen: pygame.Surface):
        """Draw the pause menu if active"""
        if not self.active:
            return

        # Draw semi-transparent overlay
        screen.blit(self.overlay, (0, 0))

        # Draw menu panel
        pygame.draw.rect(
            screen,
            (33, 97, 31),
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
            border_radius=20,
        )

        # Add a subtle border
        pygame.draw.rect(
            screen,
            (14, 43, 14),
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
            width=2,
            border_radius=20,
        )

        # Draw title
        screen.blit(self.title_label, self.title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
