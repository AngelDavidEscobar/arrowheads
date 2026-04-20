# main.py
import pygame
import settings as S
from src.sounds import load_sounds
from menu import run_menu
from game import run_game

def main():
    pygame.init()

    # Parámetros explícitos — resuelve la mayoría de problemas de audio
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)

    screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    pygame.display.set_caption(S.TITLE)
    clock = pygame.time.Clock()

    # Efectos de sonido
    load_sounds()

    # Música de fondo
    try:
        pygame.mixer.music.load("assets/sounds/music.ogg")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1, start=0)   # arranca en el segundo 0
        print("[Audio] Música cargada y reproduciendo ")
    except Exception as e:
        print(f"[Audio] No se pudo cargar music.ogg: {e}")

    while True:
        run_menu(screen, clock)
        run_game(screen, clock)

if __name__ == "__main__":
    main()