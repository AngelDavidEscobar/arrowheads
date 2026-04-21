# src/walls.py
import pygame
import settings as S

WALL_THICK = 22
WALL_LEN   = 180

C_WALL_FACE  = ( 38,  52,  35)
C_WALL_TOP   = ( 55,  75,  50)
C_WALL_SHADE = ( 25,  35,  22)

C_ROCK_FACE  = (150, 155, 165)
C_ROCK_TOP   = (190, 195, 205)
C_ROCK_SHADE = ( 90,  95, 105)


def build_walls(wall_type="cross"):
    cx = S.SCREEN_WIDTH  // 2
    cy = S.SCREEN_HEIGHT // 2
    t  = WALL_THICK
    h  = WALL_LEN // 2

    if wall_type == "rocks":
        # Montañas nevadas: 4 rocas en esquinas interiores + 1 central pequeña
        rock_size = 38
        rs = rock_size
        rects = [
            pygame.Rect(cx - 220, cy - 200, rs, rs),
            pygame.Rect(cx + 182, cy - 200, rs, rs),
            pygame.Rect(cx - 220, cy + 162, rs, rs),
            pygame.Rect(cx + 182, cy + 162, rs, rs),
            pygame.Rect(cx -  rs//2, cy - rs//2, rs, rs),  # centro
        ]
    else:
        # Bosque oscuro: cruz clásica
        rects = [
            pygame.Rect(cx - h, cy - t//2, WALL_LEN, t),
            pygame.Rect(cx - t//2, cy - h, t, WALL_LEN),
        ]
    return rects


def draw_walls(surface, wall_rects, wall_type="cross"):
    if wall_type == "rocks":
        for r in wall_rects:
            _draw_rock(surface, r)
    else:
        for r in wall_rects:
            _draw_forest_wall(surface, r)


def _draw_forest_wall(surface, r):
    shadow = r.move(3, 3)
    pygame.draw.rect(surface, C_WALL_SHADE, shadow, border_radius=3)
    pygame.draw.rect(surface, C_WALL_FACE,  r,      border_radius=3)
    pygame.draw.rect(surface, C_WALL_TOP,   r, 2,   border_radius=3)
    step = 10
    if r.width > r.height:
        for x in range(r.left+step, r.right, step):
            pygame.draw.line(surface, C_WALL_SHADE, (x,r.top+2),(x,r.bottom-2),1)
    else:
        for y in range(r.top+step, r.bottom, step):
            pygame.draw.line(surface, C_WALL_SHADE, (r.left+2,y),(r.right-2,y),1)


def _draw_rock(surface, r):
    # Sombra
    shadow = r.move(4, 4)
    pygame.draw.ellipse(surface, C_ROCK_SHADE, shadow)
    # Roca base
    pygame.draw.ellipse(surface, C_ROCK_FACE, r)
    # Borde
    pygame.draw.ellipse(surface, C_ROCK_SHADE, r, 2)
    # Brillo de nieve en la cima
    snow_r = pygame.Rect(r.x + r.w//4, r.y, r.w//2, r.h//3)
    pygame.draw.ellipse(surface, (240,245,255), snow_r)
    # Grietas
    cx, cy = r.centerx, r.centery
    pygame.draw.line(surface, C_ROCK_SHADE,
                     (cx-6, cy-4), (cx+2, cy+8), 1)
    pygame.draw.line(surface, C_ROCK_SHADE,
                     (cx+4, cy-6), (cx+8, cy+4), 1)