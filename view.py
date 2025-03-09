import cards as c
import board as b
import pygame


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
        self.card = card
        self.image = pygame.transform.smoothscale_by(
            pygame.image.load(self.__str__()), self.scale_factor
        )

    def __str__(self):
        return self.dir + self.card.__str__() + self.image_extension


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
    gap = CardView.height * 0.26

    def __init__(self, cards: list[CardView], pos: tuple[int, int]):
        self.cards = cards
        super().__init__(pos)

    def draw(self, screen: pygame.Surface) -> None:
        if len(self.cards) == 0:
            super().draw(screen)
        else:
            pos = list(self.pos)
            for card in self.cards:
                screen.blit(card.image, tuple(pos))
                pos[1] += self.gap


class FoundationView(Placeholder):

    def __init__(self, cards: list[CardView], pos: tuple[int, int]):
        self.cards = cards
        super().__init__(pos)

    def draw(self, screen: pygame.Surface) -> None:
        if len(self.cards) == 0:
            super().draw(screen)
        else:
            screen.blit(self.cards[-1].image, self.pos)


class BoardView:
    background = pygame.image.load("resources/background.jpg")

    def __init__(self, columns, foundations):
        self.columns = columns
        self.foundations = foundations

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))
        for column in self.columns:
            column.draw(screen)
        for foundation in self.foundations:
            foundation.draw(screen)
