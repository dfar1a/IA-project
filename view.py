import cards as c
import board as b
import pygame
import utils
import game
import time
import math

resources = "resources/"
WIDTH = 1400
HEIGHT = 1000  # Increased height for better spacing


class CardView:
    dir = resources + "cards/"
    image_extension = ".png"

    # Card Size
    scale_factor = 0.2
    width = 500 * scale_factor
    height = 726 * scale_factor

    def __init__(self, card: c.Card):
        self.pos = (0, 0)
        self.dest = self.pos
        self.card = card
        self.image = pygame.transform.smoothscale_by(
            pygame.image.load(self.__str__()), self.scale_factor
        )

        # Glow effect properties
        self.glow_enabled = False
        self.glow_color = (255, 255, 100)  # Default yellow glow
        self.glow_intensity = 0.7  # Between 0.0 and 1.0
        self.glow_size = 10  # Pixels around the card

    def __str__(self):
        return self.dir + self.card.__str__() + self.image_extension

    def setPos(self, pos: tuple[int, int]):
        self.dest = pos

    def move(self):
        v = 5e-2
        self.pos = tuple(
            ((self.dest[i] - self.pos[i]) * v) + self.pos[i] for i in range(2)
        )

    def glow(self, enable=True, color=None, intensity=None, size=None):
        """Enable or disable the glow effect and set its properties"""
        self.glow_enabled = enable
        self.time = time.time()
        if color is not None:
            self.glow_color = color
        if intensity is not None:
            self.glow_intensity = max(0.0, min(1.0, intensity))  # Clamp between 0 and 1
        if size is not None:
            self.glow_size = max(1, size)  # Ensure positive size

    def draw_glow(self, screen: pygame.Surface) -> None:
        """Draw a glowing effect around the card"""
        if (time.time() - self.time) > 2 * math.pi:
            self.glow_enabled = False
        if not self.glow_enabled:
            return

        self.glow_intensity = abs(math.sin(time.time() - self.time))

        # Create a surface for the glow effect with alpha channel
        glow_surface = pygame.Surface(
            (self.width + self.glow_size * 2, self.height + self.glow_size * 2),
            pygame.SRCALPHA,
        )

        # Calculate base alpha for the glow
        base_alpha = int(150 * self.glow_intensity)

        # Draw multiple rectangles with decreasing alpha for a soft glow
        for i in range(self.glow_size, 0, -1):
            # Calculate alpha for this layer (decreases as we move outward)
            alpha = int(base_alpha * (i / self.glow_size))

            # Create color with alpha
            glow_color_with_alpha = (
                self.glow_color[0],
                self.glow_color[1],
                self.glow_color[2],
                alpha,
            )

            # Draw rounded rectangle for this glow layer
            rect = pygame.Rect(
                self.glow_size - i,
                self.glow_size - i,
                self.width + i * 2,
                self.height + i * 2,
            )
            pygame.draw.rect(
                glow_surface,
                glow_color_with_alpha,
                rect,
                border_radius=8,  # Rounded corners
            )

        # Draw the glow surface on the screen
        screen.blit(
            glow_surface, (self.pos[0] - self.glow_size, self.pos[1] - self.glow_size)
        )

    def draw(self, screen: pygame.Surface) -> None:
        self.move()

        # Draw glow effect if enabled
        if self.glow_enabled:
            self.draw_glow(screen)

        # Draw the card image
        screen.blit(self.image, self.pos)


class Placeholder:
    placeholder_image = resources + "placeholder.jpg"

    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.image = pygame.image.load(self.placeholder_image)
        self.image = pygame.transform.scale(
            self.image, (CardView.width, CardView.height)
        )

    # Draw empty placeholder
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.pos)


class CardColumnView(Placeholder):

    def __init__(self, cards: list[CardView], pos: tuple[int, int]):
        self.gap = CardView.height * 0.26  # Space between stacked cards
        self.size = [CardView.width, CardView.height]
        self.cards = []
        super().__init__(pos)
        for card in cards:
            self.cards.append(card)
        self.positionCards()

    def positionCards(self):
        i = 0
        for card in self.cards:
            card.setPos((self.pos[0], self.pos[1] + self.gap * i))
            i += 1
        self.size[1] = CardView.height + self.gap * (i - 1)

    def insert(self, card: CardView):
        self.gap = (
            self.gap - CardView.height * 0.26 * (0.10)
            if len(self.cards) > 5
            else self.gap
        )
        self.cards.append(card)
        self.positionCards()

    def pop(self):
        self.gap = (
            self.gap + CardView.height * 0.26 * (0.10)
            if len(self.cards) > 5
            else self.gap
        )
        self.cards.pop()
        if len(self.cards) > 1:
            self.size[1] -= self.gap
        self.positionCards()

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        pos = list(self.pos)

        for card in self.cards:
            card.draw(screen)


class FoundationView(Placeholder):
    size = (CardView.width, CardView.height)

    def __init__(self, pos: tuple[int, int]):
        self.cards = []
        super().__init__(pos)

    def insert(self, card: CardView) -> None:
        self.cards.append(card)
        card.setPos(self.pos)

    def draw(self, screen: pygame.Surface) -> None:
        if len(self.cards) <= 1:
            super().draw(screen)
        if len(self.cards) > 1:
            self.cards[-2].draw(screen)
        if len(self.cards) > 0:
            self.cards[-1].draw(screen)  # ✅ Show top card


class BoardView:
    background = pygame.image.load("resources/background.jpg")

    def __init__(self, columns, foundations):
        self.columns = columns
        self.foundations = foundations

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))  # ✅ Fix: Always redraw background
        for column in self.columns:
            column.draw(screen)
        for foundation in self.foundations:
            foundation.draw(screen)


class GameBar:
    BAR_HEIGHT = 75

    class Button(utils.Button):
        BUTTON_HEIGHT = 30
        last_button = 0

        def __init__(self, text, hpos, callback, margin=0):
            pos = (
                (
                    hpos
                    if (hpos > (GameBar.Button.last_button + 20))
                    else (GameBar.Button.last_button + 20)
                ),
                GameBar.BAR_HEIGHT / 2 - GameBar.Button.BUTTON_HEIGHT / 2,
            )
            font_size = 20
            size = [len(text) * font_size * 0.4 + 20, GameBar.Button.BUTTON_HEIGHT]
            GameBar.Button.last_button = pos[0] + size[0]
            colors = {
                "normal": (255, 187, 0),  # Dark gray
                "hover": (250, 204, 77),  # Medium gray
                "pressed": (219, 161, 0),  # Very dark gray
                "disabled": (189, 139, 2),  # Light gray
            }
            super().__init__(
                text, pos, size, callback, margin, font_size, colors, False
            )

    def __init__(self, context) -> None:
        self.bar = pygame.rect.Rect(0, 0, WIDTH, GameBar.BAR_HEIGHT)
        self.background = pygame.Color(37, 94, 46, a=12)
        self.context = context
        self.buttons = [
            GameBar.Button("Undo", 50, lambda: print("pressed")),
            GameBar.Button("Auto-complete", 100, self.context.toggle_ai),
            GameBar.Button("Hint", 250, self.context.set_hint),
        ]
        self.lablels = [
            utils.Label(
                "Time:", "", (WIDTH - 250, GameBar.BAR_HEIGHT // 2 - 25 // 2), 25
            )
        ]

    def ai_ready(self, state: bool) -> None:
        self.buttons[1].set_enabled(state)
        self.buttons[2].set_enabled(state)

    def draw(self, screen):
        pygame.draw.rect(screen, self.background, self.bar)
        for button in self.buttons:
            button.draw(screen)
        for label in self.lablels:
            label.set_value(utils.format_time(pygame.time.get_ticks()))
            label.draw(screen)

    def check_click(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            button.check_click(event)
