import pygame
import cv2
import sys
import game as g
import bfsSolver as bfs_solver
import controller as control  # Import the game controller
import utils

pygame.init()

WIDTH, HEIGHT = 1280, 720
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 70
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 50, 50)
BUTTON_PRESSED_COLOR = (255, 75, 75)
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 50)

# Load the video
video_path = "resources/background.mp4"
cap = cv2.VideoCapture(video_path)


# Convert video to Pygame surface
# Convert video to Pygame surface with slow motion
def get_video_frame():
    global cap
    pygame.time.wait(50)  # Increase value for slower motion (e.g., 100 for even slower)
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if it ends
        ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert color format
    frame = cv2.resize(frame, (WIDTH, HEIGHT))  # Resize to fit screen
    frame = pygame.surfarray.make_surface(
        frame.swapaxes(0, 1)
    )  # Convert to pygame Surface
    return frame


class MenuButton(utils.Button):
    def __init__(self, text, pos, callback):
        super().__init__(
            text,
            pos,
            (BUTTON_WIDTH, BUTTON_HEIGHT),
            callback,
            colors={
                "normal": BUTTON_COLOR,
                "hover": BUTTON_HOVER_COLOR,
                "pressed": BUTTON_PRESSED_COLOR,
                "text": WHITE,
            },
        )


def start_game():
    pygame.quit()
    g.main()


def show_help():
    print("Help not implemented.")


def show_high_score():
    print("High score not implemented.")


def show_more_games():
    print("More games not implemented.")


def start_ai_game():
    pygame.quit()  # Quit menu
    g.run_ai_mode()  # Start AI mode


buttons = [
    MenuButton("Jogar", (WIDTH // 2 - BUTTON_WIDTH // 2, 250), start_game),
    MenuButton("Jogar (IA)", (WIDTH // 2 - BUTTON_WIDTH // 2, 350), start_ai_game),
    MenuButton("Ajuda", (WIDTH // 2 - BUTTON_WIDTH // 2, 450), show_help),
    MenuButton(
        "Pontuação Máx.", (WIDTH // 2 - BUTTON_WIDTH // 2, 550), show_high_score
    ),
    MenuButton("Mais Jogos", (WIDTH // 2 - BUTTON_WIDTH // 2, 650), show_more_games),
]


def menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Baker's Dozen")

    while True:
        frame_surface = get_video_frame()  # Get video frame
        screen.blit(frame_surface, (0, 0))  # Draw video as background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()  # Release video
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.check_click(event)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    menu()
