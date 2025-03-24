import cards as c
import board as b
import pygame
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

    def __str__(self):
        return self.dir + self.card.__str__() + self.image_extension

    def setPos(self, pos: tuple[int, int]):
        self.dest = pos

    def move(self):
        v = 5e-2
        self.pos = tuple(
            ((self.dest[i] - self.pos[i]) * v) + self.pos[i] for i in range(2)
        )

    def draw(self, screen: pygame.Surface) -> None:
        self.move()
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
    gap = CardView.height * 0.26  # Space between stacked cards

    def __init__(self, cards: list[CardView], pos: tuple[int, int]):
        self.height = CardView.height
        self.cards = []
        super().__init__(pos)
        for card in cards:
            card.setPos((self.pos[0], self.pos[1] + self.gap * len(self.cards)))
            if len(self.cards) > 1:
                self.height += self.gap
            self.cards.append(card)

    def insert(self, card: CardView):
        card.setPos((self.pos[0], self.pos[1] + self.gap * len(self.cards)))
        if len(self.cards) > 1:
            self.height += self.gap
        self.cards.append(card)

    def pop(self):
        self.cards.pop()
        if len(self.cards) > 1:
            self.height -= self.gap

    def draw(self, screen: pygame.Surface) -> None:
        if len(self.cards) == 0:
            super().draw(screen)
        else:
            pos = list(self.pos)
            for card in self.cards:
                card.draw(screen)
                pos[1] += self.gap  # ✅ Stack cards correctly


class FoundationView(Placeholder):
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
