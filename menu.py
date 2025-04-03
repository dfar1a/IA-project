import pygame
import cv2
import sys
import game as g
import bfsSolver as bfs_solver
import controller as control  # Import the game controller
import utils

WIDTH, HEIGHT = 1280, 720
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 70
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 50, 50)
BUTTON_PRESSED_COLOR = (255, 75, 75)
WHITE = (255, 255, 255)


def get_video_frame(cap):
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
            effects={
                "gradient": True,
                "shadow": True,
                "hover_animation": True,
                "rounded_corners": 10,
            },
        )


def menu():
    # Initialize pygame here if it's not already initialized
    if not pygame.get_init():
        pygame.init()

    # Create font after pygame is initialized
    font = pygame.font.Font(None, 50)

    # Create the video capture object
    video_path = "resources/background.mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        pygame.quit()
        return

    # Set up the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Baker's Dozen")

    # Create buttons with fresh callbacks
    def start_game():
        return "START_GAME"

    def show_help():
        print("Help not implemented.")
        return None

    def show_high_score():
        print("High score not implemented.")
        return None

    def quit_game():
        return "QUIT"

    buttons = [
        MenuButton("Jogar", (WIDTH // 2 - BUTTON_WIDTH // 2, 250), start_game),
        MenuButton("Ajuda", (WIDTH // 2 - BUTTON_WIDTH // 2, 350), show_help),
        MenuButton(
            "Pontuação Máx.", (WIDTH // 2 - BUTTON_WIDTH // 2, 450), show_high_score
        ),
        MenuButton("Sair", (WIDTH // 2 - BUTTON_WIDTH // 2, 550), quit_game),
    ]

    running = True
    action = None

    # Main menu loop
    while running:
        frame_surface = get_video_frame(cap)  # Get video frame
        screen.blit(frame_surface, (0, 0))  # Draw video as background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                action = "QUIT"
                break

            # Check buttons
            for button in buttons:
                if button.check_click(event):
                    result = button.callback()
                    if result == "START_GAME":
                        running = False
                        action = "START_GAME"
                    elif result == "QUIT":
                        running = False
                        action = "QUIT"

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

    # Clean up resources
    cap.release()  # Release video

    # Return the action to take
    return action


if __name__ == "__main__":
    action = menu()
    if action == "START_GAME":
        g.main()
    pygame.quit()
    sys.exit()
