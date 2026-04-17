# src/terrain.py
"""Dibuja el suelo según el tipo de terreno del nivel activo."""
import pygame
import random
import settings as S

# Semilla fija para que el patrón no cambie cada frame
_plains_details  = []
_forest_details  = []
_details_ready   = False

def _build_details():
    global _plains_details, _forest_details, _details_ready
    rng = random.Random(42)

    # Llanura: manchas de hierba seca
    _plains_details = [
        (rng.randint(20, S.SCREEN_WIDTH - 20),
         rng.randint(20, S.SCREEN_HEIGHT - 20),
         rng.randint(2, 5))
        for _ in range(120)
    ]

    # Bosque: piedras y raíces
    _forest_details = [
        (rng.randint(20, S.SCREEN_WIDTH - 20),
         rng.randint(20, S.SCREEN_HEIGHT - 20),
         rng.choice(["rock", "root"]))
        for _ in range(80)
    ]
    _details_ready = True


def draw_terrain(surface, terrain_type, c_bg, c_grid, c_border, c_accent):
    global _details_ready
    if not _details_ready:
        _build_details()

    surface.fill(c_bg)

    if terrain_type == "plains":
        _draw_plains(surface, c_bg, c_grid, c_border, c_accent)
    elif terrain_type == "forest":
        _draw_forest(surface, c_bg, c_grid, c_border, c_accent)

    # Borde medieval (igual en todos los niveles, color adaptado)
    pygame.draw.rect(surface, c_border,
                     (0, 0, S.SCREEN_WIDTH, S.SCREEN_HEIGHT), 18)
    pygame.draw.rect(surface, c_accent,
                     (10, 10, S.SCREEN_WIDTH - 20, S.SCREEN_HEIGHT - 20), 1)


def _draw_plains(surface, c_bg, c_grid, c_border, c_accent):
    # Rejilla fina de tierra
    for x in range(0, S.SCREEN_WIDTH, 32):
        pygame.draw.line(surface, c_grid, (x, 0), (x, S.SCREEN_HEIGHT), 1)
    for y in range(0, S.SCREEN_HEIGHT, 32):
        pygame.draw.line(surface, c_grid, (0, y), (S.SCREEN_WIDTH, y), 1)

    # Manchas de hierba seca
    darker = tuple(max(0, c - 18) for c in c_bg)
    for (x, y, r) in _plains_details:
        pygame.draw.circle(surface, darker, (x, y), r)


def _draw_forest(surface, c_bg, c_grid, c_border, c_accent):
    # Patrón de losas de piedra
    tile = 40
    stone_light = tuple(min(255, c + 15) for c in c_bg)
    stone_dark  = tuple(max(0,   c - 10) for c in c_bg)

    for row in range(S.SCREEN_HEIGHT // tile + 1):
        for col in range(S.SCREEN_WIDTH // tile + 1):
            offset = (tile // 2) if row % 2 == 0 else 0
            x = col * tile - offset
            y = row * tile
            color = stone_light if (row + col) % 2 == 0 else stone_dark
            pygame.draw.rect(surface, color, (x, y, tile - 1, tile - 1))

    # Grilla de juntas
    for x in range(0, S.SCREEN_WIDTH, tile):
        pygame.draw.line(surface, c_border, (x, 0), (x, S.SCREEN_HEIGHT), 1)
    for y in range(0, S.SCREEN_HEIGHT, tile):
        pygame.draw.line(surface, c_border, (0, y), (S.SCREEN_WIDTH, y), 1)

    # Piedras y raíces decorativas
    for (x, y, kind) in _forest_details:
        if kind == "rock":
            pygame.draw.ellipse(surface, stone_dark, (x - 5, y - 3, 10, 6))
            pygame.draw.ellipse(surface, stone_light, (x - 4, y - 2, 5, 3))
        else:
            pygame.draw.line(surface, stone_dark, (x, y), (x + 8, y + 4), 1)
            pygame.draw.line(surface, stone_dark, (x + 4, y), (x + 4, y + 6), 1)