import cards as c


class CardColumn:
    def __init__(self, cards: tuple[c.Card]):
        self.cards = tuple(cards)

    def copy(self):
        return CardColumn(self.cards)

    def is_empty(self):
        return len(self.cards) == 0

    def top(self) -> c.Card:
        return self.cards[-1] if not self.is_empty() else None

    def pop(self) -> c.Card | None:
        card = None
        if not self.is_empty():
            self.cards = list(self.cards)
            card = self.cards.pop()
            self.cards = tuple(self.cards)
        return card

    def can_insert(self, card: c.Card) -> bool:
        return not self.is_empty() and self.top().cardValue == card.next()

    def insert(self, card: c.Card) -> bool:
        """Insert a card if it follows Baker's Dozen rules."""
        if self.can_insert(card):
            self.cards = list(self.cards)
            self.cards.append(card)
            self.cards = tuple(self.cards)
            return True
        return False

    def n_cards(self) -> int:
        return len(self.cards)

    def __hash__(self):
        return hash(self.cards)

    def __eq__(self, other):
        return isinstance(other, CardColumn) and self.cards == other.cards


class Foundation:
    def __init__(self, suite: c.CardSuite, cards=tuple()):
        self.cards = tuple(cards)
        self.suite = suite

    def copy(self):
        return Foundation(self.suite, self.cards)

    def is_empty(self):
        return len(self.cards) == 0

    def top(self) -> c.Card:
        return self.cards[-1] if self.cards else None

    def can_insert(self, card: c.Card) -> bool:
        emptyAndAce = self.is_empty() and card.cardValue.value == c.CardValue.ace
        isNext = (
            not self.is_empty()
            and self.top().cardSuite == card.cardSuite
            and card.cardValue == self.top().next()
        )

        return emptyAndAce or isNext

    def insert(self, card: c.Card) -> bool:
        """Move to foundation only in ascending order and correct suit."""
        if self.can_insert(card):
            self.cards = list(self.cards)
            self.cards.append(card)
            self.cards = tuple(self.cards)
            return True
        return False

    def is_full(self) -> bool:
        return self.top() and self.top().cardValue.value == c.CardValue.king

    def __hash__(self):
        return hash((self.cards))

    def __eq__(self, other):
        return isinstance(other, Foundation) and self.cards == other.cards


class Board:
    def __init__(self, columns: tuple[CardColumn], foundations: tuple[Foundation]):
        self.columns = tuple(columns)
        self.foundations = tuple(foundations)

    def copy(self):
        columns = [column.copy() for column in self.columns]
        foundations = [foundation.copy() for foundation in self.foundations]
        return Board(columns, foundations)

    def is_valid_move_column_to_column(
        self, from_col: CardColumn, to_col: CardColumn
    ) -> bool:
        """Check if a move between columns is valid."""
        if from_col.is_empty():
            return False
        return to_col.can_insert(
            from_col.top()
        )  # Check if the top card can be inserted

    def is_valid_move_column_to_foundation(
        self, col: CardColumn, foundation: Foundation
    ) -> bool:
        """Check if a move from column to foundation is valid."""
        if col.is_empty():
            return False  # No card to move

        return foundation.can_insert(col.top())

    def is_game_won(self) -> bool:
        """Check if the game is won (all foundations have Kings on top)."""
        return all(f.is_full() for f in self.foundations)

    def __hash__(self):
        return hash((self.columns, self.foundations))

    def __eq__(self, other):
        return (
            isinstance(other, Board)
            and self.foundations == other.foundations
            and self.columns == self.columns
        )
