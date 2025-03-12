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
        return (self.top().cardValue.value == card.cardValue.value + 1)

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
        isNext = (
            not self.is_empty()
            and self.top().cardSuite == card.cardSuite
            and card.cardValue.value == self.top().cardValue.value + 1  # FIXED
        )
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
        """Check if a move between columns is valid (descending order)."""
        if from_col.is_empty():
            return False

        from_card = from_col.top()

        # ❌ Kings cannot be moved
        if from_card.cardValue.value == c.CardValue.king:
            return False  

        # ✅ Can only place a card onto a column if it's **1 rank lower**
        if to_col.is_empty():
            return False  # Empty column can accept any card (except Kings)
        
        return to_col.top().cardValue.value == from_card.cardValue.value + 1

    def is_valid_move_column_to_foundation(self, column: CardColumn, foundation: Foundation) -> bool:
        """Check if a move from column to foundation is valid."""
        if column.is_empty():
            return False  # No card to move

        card = column.top()

        # ✅ Allow Aces to go to empty foundations
        if foundation.is_empty():
            return card.cardValue.value == c.CardValue.ace

        # ✅ Check if card is the next in sequence and same suit
        top_foundation_card = foundation.top()

        return (card.cardSuite == top_foundation_card.cardSuite and
                card.cardValue.value == top_foundation_card.cardValue.value + 1)


    def is_game_won(self) -> bool:
        """Check if the game is won (all foundations have Kings on top)."""
        return all(f.is_full() for f in self.foundations)
