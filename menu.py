import pygame
import cv2
import sys
import game as g
import controller as control
import utils

WIDTH, HEIGHT = 1280, 720
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 70
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 50, 50)
BUTTON_PRESSED_COLOR = (255, 75, 75)
WHITE = (255, 255, 255)


def get_video_frame(cap):
    pygame.time.wait(50)
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return frame


def show_highscores(screen):
    import json

    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    def time_in_seconds(score):
        try:
            return int(score["time"].replace("s", ""))
        except:
            return float("inf")

    scores.sort(key=time_in_seconds)
    top_scores = scores[:3]

    font_title = pygame.font.Font(None, 80)
    font_entry = pygame.font.Font(None, 50)
    font_back = pygame.font.Font(None, 36)

    screen.fill((0, 128, 0))

    title_text = font_title.render("Melhores Pontuações", True, (255, 255, 255))
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 120)))

    medals = ["1st - ", "2nd - ", "3rd -"]
    if top_scores:
        for i, entry in enumerate(top_scores):
            name = entry.get("name", "Anônimo")
            time = entry.get("time", "??s")
            text = f"{medals[i]} {name:<15} - {time}"
            entry_surface = font_entry.render(text, True, (255, 255, 255))
            screen.blit(entry_surface, (WIDTH // 2 - 200, 220 + i * 80))
    else:
        no_scores = font_entry.render("Nenhuma pontuação salva!", True, (255, 255, 255))
        screen.blit(no_scores, no_scores.get_rect(center=(WIDTH // 2, 300)))

    back_text = font_back.render("Pressione [ESC] para voltar", True, (200, 200, 200))
    screen.blit(back_text, back_text.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False


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


def select_board_mode(screen):
    """New screen after clicking 'Jogar' with board mode options."""
    font = pygame.font.Font(None, 60)
    small_btn = MenuButton("Mini Board (4 cartas)", (WIDTH // 2 - 150, 300), lambda: "small")
    big_btn = MenuButton("Big Board (52 cartas)", (WIDTH // 2 - 150, 400), lambda: "big")
    buttons = [small_btn, big_btn]

    selecting = True
    while selecting:
        screen.fill((0, 100, 0))
        label = font.render("Escolha o tipo de jogo", True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=(WIDTH // 2, 150)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                if button.check_click(event):
                    return f"START_GAME_{button.callback()}"

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()


def menu():
    if not pygame.get_init():
        pygame.init()

    font = pygame.font.Font(None, 50)
    video_path = "resources/background.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file")
        pygame.quit()
        return

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Baker's Dozen")

    # Button callbacks
    def start_game():
        return select_board_mode(screen)

    def show_help():
        print("Help not implemented.")
        return None

    def show_high_score():
        show_highscores(screen)
        return None

    def quit_game():
        return "QUIT"

    buttons = [
        MenuButton("Jogar", (WIDTH // 2 - BUTTON_WIDTH // 2, 250), start_game),
        MenuButton("Ajuda", (WIDTH // 2 - BUTTON_WIDTH // 2, 350), show_help),
        MenuButton("Pontuação Máx.", (WIDTH // 2 - BUTTON_WIDTH // 2, 450), show_high_score),
        MenuButton("Sair", (WIDTH // 2 - BUTTON_WIDTH // 2, 550), quit_game),
    ]

    running = True
    action = None

    while running:
        frame_surface = get_video_frame(cap)
        screen.blit(frame_surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                action = "QUIT"
                break

            for button in buttons:
                if button.check_click(event):
                    result = button.callback()
                    if result and result.startswith("START_GAME"):
                        mode = result.split("_")[-1]
                        action = f"START_GAME_{mode}"
                        running = False
                    elif result == "QUIT":
                        running = False
                        action = "QUIT"

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

    cap.release()
    return action


if __name__ == "__main__":
    try:
        action = menu()
        if action and action.startswith("START_GAME"):
            mode = action.split("_")[-1]
            g.main(board_mode=mode)
    except Exception as e:
        print("Menu crashed:", e)
    finally:
        pygame.quit()
        sys.exit(0)
