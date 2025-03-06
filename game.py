import pygame
import board as b
import menu as m


def main():
    """Function to run the actual game loop after selecting 'Jogar' from the menu."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    game_board = b.board()

    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit game loop

        # Render the game board
        game_board.render(screen)

        # Update the screen
        pygame.display.flip()
        clock.tick(60)  # Limit FPS to 60

    pygame.quit()


if __name__ == "__main__":
    m.menu()
