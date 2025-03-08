import cards as c
import view as v
import random as r
import pygame

# Define screen dimensions
WIDTH = 1400
HEIGHT = 1000  # Increased height for better spacing


class CardColumn:
    gap = v.CardView.height * 0.26

    def __init__(self, cards: list[c.Card], x, y):
        self.cards = cards.copy()
        self.x = x
        self.y = y
        self.placeholder = pygame.image.load("resources/placeholder.jpg")
        self.placeholder = pygame.transform.scale(
            self.placeholder, (v.CardView.width, v.CardView.height)
        )

    def is_empty(self):
        return len(self.cards) == 0

    def top(self):
        return self.cards[-1] if not self.is_empty() else None

    def pop(self):
        return self.cards.pop() if not self.is_empty() else None

    def insert(self, card: c.Card):
        """Insert a card if it follows Baker's Dozen rules."""
        if self.is_empty():
            self.cards.append(card)
            return True
        elif self.top().cardValue.value == card.cardValue.value + 1:
            self.cards.append(card)
            return True
        return False

    def n_cards(self) -> int:
        return len(self.cards)

    def render(self, screen):
        pos_y = self.y
        if self.is_empty():
            screen.blit(self.placeholder, (self.x, self.y))
        else:
            for card in self.cards:
                screen.blit(card.image, (self.x, pos_y))
                pos_y += self.gap

    def get_card_at(self, mouse_x, mouse_y):
        """Detects if the top card was clicked."""
        if self.x <= mouse_x <= self.x + v.CardView.width:
            pos_y = self.y + (self.n_cards() - 1) * self.gap
            if pos_y <= mouse_y <= pos_y + v.CardView.height:
                return self.top()
        return None


class Foundation:
    def __init__(self, suite: c.CardSuite, x, y):
        self.cards = []
        self.suite = suite
        self.x = x
        self.y = y
        self.placeholder = pygame.image.load("resources/placeholder.jpg")
        self.placeholder = pygame.transform.scale(
            self.placeholder, (v.CardView.width, v.CardView.height)
        )

    def is_empty(self):
        return len(self.cards) == 0

    def top(self) -> c.Card:
        return self.cards[-1] if self.cards else None

    def insert(self, card: c.Card) -> bool:
        """Move to foundation only in ascending order and correct suit."""
        if not self.cards and card.cardValue.value == c.CardValue.ace:
            self.cards.append(card)
            return True
        elif (
            self.cards
            and self.top().cardSuite == card.cardSuite
            and card.cardValue.value == self.top().cardValue.value + 1
        ):
            self.cards.append(card)
            return True
        return False

    def is_full(self) -> bool:
        return self.top() and self.top().cardValue.value == c.CardValue.king

    def draw(self, screen):
        if self.cards:
            screen.blit(self.top().image, (self.x, self.y))
        else:
            screen.blit(self.placeholder, (self.x, self.y))


class Board:
    background = pygame.image.load("resources/background.jpg")

    def __init__(self, columns: list[CardColumn], foundations: list[Foundation]):
        self.columns = columns
        self.foundations = foundations

    def move_card_column_column(
        self, card: c.Card, from_column: CardColumn, to_column: CardColumn
    ) -> bool:
        """Moves the top card from one column to another if the move is valid."""
        if from_column.is_empty():
            return False  # No card to move

        if to_column.insert(card):
            from_column.pop()  # Remove only if move is valid
            return True

        return False  # Invalid move

    def move_card_column_foundation(
        self, card: c.Card, from_column: CardColumn, foundation: Foundation
    ) -> bool:
        """Moves a card from a column to a foundation if valid."""
        if from_column.is_empty():
            return False

        if foundation.insert(card):
            from_column.pop()  # Remove only if move is valid
            return True

        return False  # Invalid move

    def get_clicked_card(self, mouse_x, mouse_y):
        """Detects which column was clicked and returns the top card."""
        for column in self.columns:
            card = column.get_card_at(mouse_x, mouse_y)
            if card:
                return card, column
        return None, None
