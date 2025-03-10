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

    def is_valid_move_column_to_column(self, from_col: CardColumn, to_col: CardColumn) -> bool:
        """Check if a move between columns is valid."""
        if from_col.is_empty():
            return False
        return to_col.insert(from_col.top())  # Check if the top card can be inserted

    def is_valid_move_column_to_foundation(self, col: CardColumn, foundation: Foundation) -> bool:
        """Check if a move from column to foundation is valid."""
        if col.is_empty():
            return False
        return foundation.insert(col.top())  # Check if the foundation accepts it

    def move_card_column_column(self, from_col: CardColumn, to_col: CardColumn) -> bool:
        """Move a card between columns if valid."""
        if self.is_valid_move_column_to_column(from_col, to_col):
            to_col.insert(from_col.pop())
            return True
        return False

    def move_card_column_foundation(self, col: CardColumn, foundation: Foundation) -> bool:
        """Move a card from a column to a foundation if valid."""
        if self.is_valid_move_column_to_foundation(col, foundation):
            foundation.insert(col.pop())
            return True
        return False
    
    def move_card_column_to_foundation_ai(self, col, foundation):
        """Move a card from a column to a foundation if valid (AI only)."""
        if self.is_valid_move_column_to_foundation(col, foundation):
            card = col.pop()  # ✅ Remove from column
            foundation.insert(card)  # ✅ Add to foundation

            # ✅ Ensure UI updates correctly
            if col.view.cards:
                col.view.cards.pop()  # ✅ Remove from column UI
            foundation.view.cards.append(card.view)  # ✅ Add to foundation UI

            print(f"✅ AI moved {card} to Foundation {foundation.suite}")

            return True
        return False

    def move_card_column_to_column_ai(self, from_col, to_col):
        """Move a card between columns if valid (AI only)."""
        if self.is_valid_move_column_to_column(from_col, to_col):
            card = from_col.pop()
            to_col.insert(card)

            # ✅ **Fix UI Update**
            from_col.view.cards.pop()  # Remove from old column UI
            to_col.view.cards.append(card.view)  # Add to new column UI

            print(f"✅ AI moved {card} from Column to Column, updating board")
            return True
        return False

