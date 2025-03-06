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

    def n_cards(self) -> int:
        return len(self.cards)

    def render(self, screen, pos: list[int, int]):
        gap = self.cards[0].image.get_height() * 0.26
        for i in range(self.n_cards() - 1):
            pos[1] += gap
            screen.blit(self.cards[i].image, pos)

        pos[1] += gap
        screen.blit(
            self.top().image,
            pos,
        )


class Foundation:
    def __init__(self, suite: c.CardSuite, x, y):
        self.cards = list()
        self.suite = suite
        self.x = x
        self.y = y

    def top(self) -> c.Card:
        return self.cards[-1]

    def insert(self, card: c.Card) -> bool:
        if card.cardSuite == self.suite and card.prev() == self.top().cardValue:
            self.cards.append(card)
            return True
        return False

    def isFull(self) -> bool:
        return self.top().cardValue.value == c.CardValue.king

    def draw(self, screen) -> None:
        if len(self.cards) != 0:
            screen.blit(self.top().image, (self.x, self.y))


class board:
    background = pygame.image.load("resources/background.jpg")

    def __init__(self):
        deck = list()
        self.columns = list()

        self.foundations = [
            Foundation(suite, 1100, 150 * suite + 50) for suite in range(4)
        ]

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
        pos = [0, 0]
        i = 0
        for column in self.columns:
            width = column.top().image.get_width()
            heigth = column.top().image.get_height()
            pos[0] = 50 + (width + 50) * (i % 7)
            pos[1] = 50 + (heigth * 2) * (i // 7)
            column.render(screen, pos)
            i += 1

        for found in self.foundations:
            found.draw(screen)
        # mouse_pos = pygame.mouse.get_pos()
        # initial_pos = [
        #     50,
        #     50 + 726 * 0.2 * 0.26 * (len(self.columns[0].cards) - 1),
        # ]
        # if pygame.mouse.get_pressed()[0]:
        #     pos = mouse_pos
        # else:
        #     pos = initial_pos

        # screen.blit(
        #     self.columns[0].top().load,
        #     pos,
        # )


if __name__ == "__main__":
    board()
