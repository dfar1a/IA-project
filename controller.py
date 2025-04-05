import cards as c
import view as v
import random as r
import board as b
import pygame

WIDTH = 1400
HEIGHT = 1000  # Increased height for better spacing


class CardController:

    def __init__(self, cardValue: c.CardValue, cardSuite: c.CardSuite):
        self.model = c.Card(cardValue, cardSuite)
        self.view = v.CardView(self.model)

    def get_image(self):
        return self.view.image


class ColumnController:
    def __init__(self, cards: list[CardController], pos: tuple[int, int]):
        self.cards = cards
        self.model = b.CardColumn([card.model for card in cards])
        self.view = v.CardColumnView([card.view for card in cards], pos)

    def get_card_at(self, mouse_x, mouse_y) -> CardController:
        """Detects if the top card was clicked."""
        x = self.view.pos[0]
        y = self.view.pos[1]

        if x <= mouse_x <= x + v.CardView.width and len(self.cards) != 0:
            pos_y = y + (self.model.n_cards() - 1) * self.view.gap
            if pos_y <= mouse_y <= pos_y + v.CardView.height:
                return self.cards[-1]
        return None

    def is_empty(self) -> bool:
        return self.model.is_empty()

    def insert(self, card: CardController) -> bool:
        if self.model.insert(card.model):
            self.cards.append(card)
            self.view.insert(card.view)
            print(f"Inserted {card} into foundation, updating UI")
            return True
        return False

    def top(self) -> CardController:
        return self.cards[-1]

    def pop(self) -> None:
        if not self.is_empty():
            removed_card = self.cards.pop()
            self.model.pop()
            self.view.pop()
            print(f"Removed {removed_card} from column, updating UI")


class FoundationController:
    def __init__(self, pos: tuple[int, int]):
        self.model = b.Foundation()
        self.view = v.FoundationView(pos)
        self.cards = list()

    def insert(self, card: CardController) -> bool:
        if self.model.insert(card.model):
            self.cards.append(card)
            self.view.insert(card.view)
            print(f"Inserted {card} into foundation, updating UI")
            return True
        return False



def create_deck() -> list[CardController]:
    deck = [
        CardController(c.CardValue(i // 4 + 1), c.CardSuite(i % 4)) for i in range(48)
    ]
    kings = [
        CardController(c.CardValue(c.CardValue.king), c.CardSuite(suite))
        for suite in c.CardSuite.get_suites()
    ]
    pos = set()
    for i in range(len(kings)):
        choice = r.randrange(0, 52, 4)
        while choice in pos:
            choice += 1
        pos.add(choice)

    shuffled_deck = [None for i in range(52)]

    i = 0
    for p in pos:
        shuffled_deck[p] = kings[i]
        i += 1

    r.shuffle(deck)

    i = 0

    for j in range(len(shuffled_deck)):
        if shuffled_deck[j] == None:
            shuffled_deck[j] = deck[i]
            i += 1

    return shuffled_deck

def create_mini_deck() -> list[CardController]:
    # Create all cards from Ace (1) to 3 for all 4 suits → total 12 cards
    deck = [
        CardController(c.CardValue(i // 4 + 1), c.CardSuite(i % 4)) for i in range(12)
    ]

    # Create the 4s (one per suit)
    fours = [
        CardController(c.CardValue(4), c.CardSuite(suite))
        for suite in c.CardSuite.get_suites()
    ]

    # Pick unique positions in deck to insert 4s
    pos = set()
    for i in range(4):
        choice = r.randrange(0, 16, 4)
        while choice in pos:
            choice += 1
        pos.add(choice)

    # Prepare final deck of 16 cards
    shuffled_deck = [None] * 16

    for i, p in enumerate(pos):
        shuffled_deck[p] = fours[i]

    r.shuffle(deck)

    i = 0
    for j in range(len(shuffled_deck)):
        if shuffled_deck[j] is None:
            shuffled_deck[j] = deck[i]
            i += 1

    return shuffled_deck


class BoardController:

    def __init__(self,board_mode="big"):
        self.board_mode = board_mode 
        column_width = v.CardView.width + 20  # Padding between columns
        row_spacing = v.CardView.height * 2.5  # More space between rows
        start_x = (WIDTH - column_width * 7) / 2
        start_y = HEIGHT / 8  # More space at the top
        foundation_x = start_x + column_width * 7 + 50  # More space from columns
        foundation_y = start_y
        print(f"[DEBUG] BoardController initialized with mode: {self.board_mode}")
        self.moves = 0

        # Shffle all cards except the kings

        if board_mode == "small":
            deck = create_mini_deck()
            assert len(deck) == 16, f"[ERROR] Mini deck must have 16 cards, got {len(deck)}"
            self.columns = [
                ColumnController(
                    deck[i * 4: i * 4 + 4],
                    (start_x + i * column_width, start_y),
                )
                for i in range(4)
            ]
            self.foundations = [
                FoundationController(
                    (foundation_x, foundation_y + i * (v.CardView.height + 30))
                )
                for i in range(4)
            ]

        else:
            deck = create_deck()
            assert len(deck) == 52, f"[ERROR] Big deck must have 52 cards, got {len(deck)}"
            self.columns = [
                ColumnController(
                    deck[i * 4 : i * 4 + 4],
                    (start_x + (i % 7) * column_width, start_y + (i // 7) * row_spacing),
                )
                for i in range(13)
            ]
            self.foundations = [
                FoundationController(
                    (foundation_x, foundation_y + i * (v.CardView.height + 30))
                )
                for i in range(4)
            ]

        self.model = b.Board(
            [column.model for column in self.columns],
            [foundation.model for foundation in self.foundations],
            mode=board_mode
        )
        self.view = v.BoardView(
            [column.view for column in self.columns],
            [foundation.view for foundation in self.foundations],
        )
        self.selectedCard = None

    def update(self, screen: pygame.Surface) -> None:
        self.view.draw(screen)
        if self.selectedCard is not None:
            self.selectedCard.view.draw(screen)

    def get_clicked_card(self, mouse_x, mouse_y) -> CardController:
        """Detects which column was clicked and returns the top card."""
        for column in self.columns:
            card = column.get_card_at(mouse_x, mouse_y)
            if card:
                return card, column
        return None, None

    def move_card_column_column(
        self,
        from_column: ColumnController,
        to_column: ColumnController,
    ) -> bool:
        """Moves the top card from one column to another if the move is valid."""
        if from_column.is_empty():
            return False  # No card to move

        card = from_column.top()

        if to_column.is_empty():
            print(f"Invalid move: Cannot move {card} to an empty column!")
            return False  # Return immediately without popping

        # Check if the move is valid
        if to_column.insert(card):
            self.moves += 1
            from_column.pop()  # Remove only if move is valid
            return True

        print(f"Move {card} to column failed, returning card to original column!")
        return False  # Invalid move

    def move_card_column_foundation(
        self, from_column: ColumnController, foundation: FoundationController
    ) -> bool:
        """Moves a card from a column to a foundation if valid."""
        if from_column.is_empty():
            return False

        card = from_column.top()
        print(f"[DEBUG] Attempting to move {card} to foundation...")

        if foundation.insert(card):
            self.moves += 1
            from_column.pop()

            # Update board model
            self.model = b.Board(
                [col.model for col in self.columns],
                [f.model for f in self.foundations],
                mode=self.board_mode
            )

            return True

        print(f"[DEBUG] Move failed: {card} cannot go to foundation.")
        return False
    
    def is_game_won_visual(self) -> bool:
        if self.board_mode == "small":
            for foundation in self.foundations:
                if not foundation.cards or foundation.cards[-1].model.cardValue.value != 4:
                    return False
        else:
            for foundation in self.foundations:
                if not foundation.cards or foundation.cards[-1].model.cardValue.value != c.CardValue.king:
                    return False
        return True

