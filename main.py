# main.py
import pygame
import settings as S
from menu import run_menu
from game import run_game

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    pygame.display.set_caption(S.TITLE)
    clock = pygame.time.Clock()

    # Música de fondo (opcional — pon music.ogg en assets/sounds/)
    try:
        pygame.mixer.music.load("assets/sounds/music.ogg")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    while True:
        run_menu(screen, clock)
        run_game(screen, clock)

if __name__ == "__main__":
    main()