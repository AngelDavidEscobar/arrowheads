# src/walls.py
"""
Cruz de muros en el centro del escenario para el nivel 2.
Los muros tienen colisión con el jugador, los enemigos y las flechas.
"""
import pygame
import settings as S

# Grosor y largo de cada brazo de la cruz
WALL_THICK = 22
WALL_LEN_H = 180   # largo del brazo horizontal
WALL_LEN_V = 180   # largo del brazo vertical

# Color de los muros (piedra oscura del bosque)
C_WALL_FACE  = ( 38,  52,  35)
C_WALL_TOP   = ( 55,  75,  50)
C_WALL_SHADE = ( 25,  35,  22)


def build_walls():
    """
    Devuelve una lista de pygame.Rect que forman la cruz central.
    Se generan 4 rectángulos: arriba, abajo, izquierda, derecha
    más el bloque central que los une.
    """
    cx = S.SCREEN_WIDTH  // 2
    cy = S.SCREEN_HEIGHT // 2
    t  = WALL_THICK
    half_h = WALL_LEN_H // 2
    half_v = WALL_LEN_V // 2

    rects = [
        # brazo horizontal completo
        pygame.Rect(cx - half_h, cy - t // 2, WALL_LEN_H, t),
        # brazo vertical completo
        pygame.Rect(cx - t // 2, cy - half_v, t, WALL_LEN_V),
    ]
    return rects


def draw_walls(surface, wall_rects):
    """Dibuja los muros con un efecto de profundidad simple."""
    for r in wall_rects:
        # Sombra (desplazada 3px abajo-derecha)
        shadow = r.move(3, 3)
        pygame.draw.rect(surface, C_WALL_SHADE, shadow, border_radius=3)
        # Cara principal
        pygame.draw.rect(surface, C_WALL_FACE, r, border_radius=3)
        # Borde iluminado (borde superior e izquierdo más claro)
        pygame.draw.rect(surface, C_WALL_TOP, r, 2, border_radius=3)
        # Detalle: líneas de piedra horizontales
        step = 10
        if r.width > r.height:
            # muro horizontal → líneas verticales
            for x in range(r.left + step, r.right, step):
                pygame.draw.line(surface, C_WALL_SHADE,
                                 (x, r.top + 2), (x, r.bottom - 2), 1)
        else:
            # muro vertical → líneas horizontales
            for y in range(r.top + step, r.bottom, step):
                pygame.draw.line(surface, C_WALL_SHADE,
                                 (r.left + 2, y), (r.right - 2, y), 1)