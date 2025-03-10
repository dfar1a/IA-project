import cards as c


class CardColumn:
    def __init__(self, cards: list[c.Card]):
        self.cards = cards

    def is_empty(self):
        return len(self.cards) == 0

    def top(self) -> c.Card:
        return self.cards[-1] if not self.is_empty() else None

    def pop(self) -> None:
        return self.cards.pop() if not self.is_empty() else None
    
    def can_insert(self, card: c.Card) -> bool:
        return self.is_empty() or (self.top().cardValue.value == card.cardValue.value + 1)

    def insert(self, card: c.Card) -> bool:
        """Insert a card if it follows Baker's Dozen rules."""
        if self.can_insert(card):
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
    
    def can_insert(self, card: c.Card) -> bool:
        emptyAndAce = self.is_empty() and card.cardValue.value == c.CardValue.ace
        isNext = not self.is_empty() and self.top().cardSuite == card.cardSuite and card.cardValue.value == self.top().next

        return emptyAndAce or isNext
    
    def insert(self, card: c.Card) -> bool:
        """Move to foundation only in ascending order and correct suit."""
        if self.can_insert(card):
            self.cards.append(card)
            return True
        return False

    def is_full(self) -> bool:
        return self.top() and self.top().cardValue.value == c.CardValue.king


class Board:
    def __init__(self, columns: list[CardColumn], foundations: list[Foundation]):
        self.columns = columns
        self.foundations = foundations

    def is_valid_move_column_to_column(self, from_col: CardColumn, to_col: CardColumn) -> bool:
        """Check if a move between columns is valid."""
        if from_col.is_empty():
            return False
        return to_col.can_insert(from_col.top())  # Check if the top card can be inserted

    def is_valid_move_column_to_foundation(self, col: CardColumn, foundation: Foundation) -> bool:
        """Check if a move from column to foundation is valid."""
        if col.is_empty():
            return False
        return foundation.can_insert(col.top())  # Check if the foundation accepts it
