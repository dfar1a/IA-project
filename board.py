import cards as c
import pygame

# Define screen dimensions
WIDTH = 1400
HEIGHT = 1000  # Increased height for better spacing


class CardColumn:
    def __init__(self, cards: list[c.Card]):
        self.cards = cards

    def is_empty(self):
        return len(self.cards) == 0

    def top(self) -> c.Card:
        return self.cards[-1] if not self.is_empty() else None

    def pop(self) -> None:
        return self.cards.pop() if not self.is_empty() else None

    def insert(self, card: c.Card) -> bool:
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


class Foundation:
    def __init__(self, suite: c.CardSuite):
        self.cards = []
        self.suite = suite

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
