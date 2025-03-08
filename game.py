import pygame
import board as b
import cards as c
import controller as control

# Increased window size for better spacing and proper alignment
WIDTH = 1400
HEIGHT = 1000


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    game_board = control.BoardController()

    selected_card = None
    selected_column = None
    original_column = None
    dragging = False
    drag_offset_x = 0
    drag_offset_y = 0

    while running:
        screen.fill((0, 128, 0))  # Green background for a classic card table look
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                card, column = game_board.model.get_clicked_card(
                    event.pos[0], event.pos[1]
                )
                if card:
                    selected_card = card
                    selected_column = column
                    original_column = (
                        column  # Save the original column for invalid moves
                    )
                    dragging = True
                    drag_offset_x = event.pos[0] - column.x
                    drag_offset_y = event.pos[1] - (
                        column.y + (column.n_cards() - 1) * column.gap
                    )

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_card:
                    valid_move = False

                    # Check if moved to another column
                    for col in game_board.model.columns:
                        if (
                            col.x <= event.pos[0] <= col.x + c.Card.width
                            and col.y <= event.pos[1] <= col.y + c.Card.height
                        ):
                            if game_board.model.move_card_column_column(
                                selected_card, original_column, col
                            ):
                                valid_move = True
                                break

                    # Check if moved to a foundation
                    if not valid_move:
                        for foundation in game_board.model.foundations:
                            if (
                                foundation.x
                                <= event.pos[0]
                                <= foundation.x + c.Card.width
                                and foundation.y
                                <= event.pos[1]
                                <= foundation.y + c.Card.height
                            ):
                                if game_board.model.move_card_column_foundation(
                                    selected_card, original_column, foundation
                                ):
                                    valid_move = True
                                    break

                    # If move is invalid, return card to original column
                    if not valid_move:
                        original_column.insert(selected_card)

                    selected_card = None
                    dragging = False

        game_board.update(screen)

        # Draw dragging card
        if dragging and selected_card:
            screen.blit(
                selected_card.image, (mouse_x - drag_offset_x, mouse_y - drag_offset_y)
            )

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
