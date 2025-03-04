import cards as c
import random as r
import pygame


class CardColumn:
    def __init__(self, cards: list[c.Card]):
        self.cards = cards.copy()

    def is_empty(self):
        return len(self.cards) == 0

    def top(self):
        return self.cards[-1]

    def pop(self):
        self.cards.pop()

    def insert(self, card: c.Card):
        if card.next() == self.top().cardValue and not self.is_empty():
            self.cards.append(card)
            return True
        return False


class Foundation:
    def __init__(self, suite: c.CardSuite):
        self.cards = list()
        self.suite = suite

    def top(self) -> c.Card:
        return self.cards[-1]

    def insert(self, card: c.Card) -> bool:
        if card.cardSuite == self.suite and card.prev() == self.top().cardValue:
            self.cards.append(card)
            return True
        return False

    def isFull(self) -> bool:
        return self.top().cardValue.value == c.CardValue.king


class board:
    background = pygame.image.load("resources/background.jpg")

    def __init__(self):
        deck = list()
        self.columns = list()
        self.foundations = [Foundation(suite) for suite in range(4)]

        for i in range(52):
            cv = c.CardValue(i // 4 + 1)
            cs = c.CardSuite(i % 4)
            deck.append(c.Card(cv, cs))

        r.shuffle(deck)

        for i in range(13):
            column = CardColumn(deck[i * 4 : i * 4 + 4])
            self.columns.append(column)

    def move_card_column_column(self, fromCol: CardColumn, toCol: CardColumn) -> bool:
        if not fromCol.is_empty():
            card = fromCol.top()
            if toCol.insert(card):
                fromCol.pop()
                return True
        return False

    def move_card_column_foundation(self, col: CardColumn, foundation: Foundation):
        if not col.is_empty():
            card = col.top()
            if foundation.insert(card):
                col.pop()
                return True
        return False

    def check_win(self) -> bool:
        for foundation in self.foundations:
            if not foundation.isFull():
                return False
        return True

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.columns[0].top().load, (50, 50))


if __name__ == "__main__":
    board()
