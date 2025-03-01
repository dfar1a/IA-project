import cards as c


class CardColumn:
    def __init__(self, cards: list):
        self.cards = cards.copy()

    def is_empty(self):
        return len(self.cards) == 0

    def top(self):
        return self.cards[-1]

    def pop(self):
        card = self.top()
        self.pop()
        return card

    def insert(self, card: c.Card):
        if card.next() == self.top().cardValue and not self.is_empty():
            self.cards.insert(card)
            return True
        return False


class foundation:
    def __init__(self, suite: c.CardSuite):
        self.cards = list()
        self.suite = suite

    def top(self):
        return self.cards[-1]

    def insert(self, card: c.Card):
        if card.cardSuite == self.suite and card.prev() == self.top().cardValue:
            pass
