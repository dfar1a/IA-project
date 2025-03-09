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
    def __init__(self, columns: list[CardColumn], foundations: list[Foundation]):
        self.columns = columns
        self.foundations = foundations
