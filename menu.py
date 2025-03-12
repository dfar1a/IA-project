import pygame
import sys
import game as g
import bfsSolver as bfs_solver
import controller as control  # Import the game controller
pygame.init()

WIDTH, HEIGHT = 1280, 720
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 70
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 50, 50)
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 50)

BACKGROUND = pygame.image.load("resources/menu2.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))


class Button:
    def __init__(self, text, pos, callback):
        self.text = text
        self.pos = pos
        self.callback = callback
        self.rect = pygame.Rect(pos[0], pos[1], BUTTON_WIDTH, BUTTON_HEIGHT)

    def draw(self, screen):
        color = (
            BUTTON_HOVER_COLOR
            if self.rect.collidepoint(pygame.mouse.get_pos())
            else BUTTON_COLOR
        )
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


def start_game():
    pygame.quit()
    g.main()


def show_help():
    print("nao implementado")


def show_high_score():
    print("nao implementado")


def show_more_games():
    print("nao implementado")

def start_ai_game():
    pygame.quit()  # Quit menu
    g.run_ai_mode()  # Start AI mode

buttons = [
    Button("Jogar", (WIDTH // 2 - BUTTON_WIDTH // 2, 250), start_game),
    Button("Jogar (IA)", (WIDTH // 2 - BUTTON_WIDTH // 2, 350), start_ai_game),
    Button("Ajuda", (WIDTH // 2 - BUTTON_WIDTH // 2, 450), show_help),
    Button("Pontuação Máx.", (WIDTH // 2 - BUTTON_WIDTH // 2, 550), show_high_score),
    Button("Mais Jogos", (WIDTH // 2 - BUTTON_WIDTH // 2, 650), show_more_games),
]

def menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Baker's Dozen")

    while True:
        screen.blit(BACKGROUND, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.check_click(event)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    menu()