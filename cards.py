import pygame

card_resources = "resources/cards/"
image_extension = ".png"


class CardValue:
    names = {1: "ace", 11: "jack", 12: "queen", 13: "king"}
    ace = 1
    jack = 11
    queen = 12
    king = 13

    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        if self.value > 1 and self.value < 11:
            return str(self.value)
        else:
            return CardValue.names[self.value]

    def __eq__(self, other):
        return self.value == other.value


class CardSuite:
    names = {0: "clubs", 1: "spades", 2: "hearts", 3: "diamonds"}
    clubs = 0
    spades = 1
    hearts = 2
    diamonds = 3

    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return CardSuite.names[self.value]

    def __eq__(self, other):
        return self.value == other.value


class Card:
    def __init__(self, cardValue: CardValue, cardSuite: CardSuite):
        self.cardValue = cardValue
        self.cardSuite = cardSuite
        self.image = pygame.transform.smoothscale_by(
            pygame.image.load(self.__str__()), 0.2
        )

    def prev(self):
        return CardValue(self.cardValue.value - 1)

    def next(self):
        return CardValue(self.cardValue.value + 1)

    def __str__(self):
        return (
            card_resources
            + self.cardValue.__str__()
            + "_of_"
            + self.cardSuite.__str__()
            + image_extension
        )
