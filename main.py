# main.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from menu import run_menu
from game import run_game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    while True:
        run_menu(screen, clock)
        final_score = run_game(screen, clock)
        # Aquí podrías mostrar una pantalla de game over con el puntaje
        print(f"Game Over — Puntaje final: {final_score}")

if __name__ == "__main__":
    main()