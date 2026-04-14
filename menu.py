# menu.py
import pygame, sys
from settings import *

def draw_title(surface, font_big, font_small, tick):
    surface.fill(C_BG)

    # Marco decorativo medieval
    border = 20
    pygame.draw.rect(surface, C_BORDER,
                     (border, border,
                      SCREEN_WIDTH - border*2,
                      SCREEN_HEIGHT - border*2), 4)
    # líneas interiores
    pygame.draw.rect(surface, C_BORDER,
                     (border+8, border+8,
                      SCREEN_WIDTH - (border+8)*2,
                      SCREEN_HEIGHT - (border+8)*2), 1)

    # Título
    title = font_big.render("ARROWHEADS", True, C_UI_TEXT)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 160)))

    sub = font_small.render("Hunt or be hunted", True, C_BORDER)
    surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 210)))

    # Decoración: flechas simples
    for i, x in enumerate([130, 380]):
        color = C_HIGHLIGHT if (tick // 30) % 2 == 0 else C_BORDER
        pygame.draw.line(surface, color, (x, 157), (x+30, 162), 3)
        pygame.draw.polygon(surface, color,
                            [(x+28,157),(x+36,162),(x+28,167)])

    # Botón "Jugar"
    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 80, 300, 160, 48)
    hover    = btn_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surface, C_HIGHLIGHT if hover else C_BORDER, btn_rect, border_radius=6)
    pygame.draw.rect(surface, C_BORDER, btn_rect, 2, border_radius=6)
    label = font_small.render("JUGAR", True, C_BG)
    surface.blit(label, label.get_rect(center=btn_rect.center))

    # Controles
    hints = [
        "WASD / flechas — mover",
        "Click izquierdo  — disparar",
        "Sobrevive las oleadas",
    ]
    for i, h in enumerate(hints):
        t = font_small.render(h, True, C_BORDER)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 390 + i*22)))

    return btn_rect


def run_menu(screen, clock):
    try:
        font_big   = pygame.font.Font(None, 52)
        font_small = pygame.font.Font(None, 28)
    except:
        font_big   = pygame.font.SysFont("serif", 48)
        font_small = pygame.font.SysFont("serif", 26)

    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn = draw_title(screen, font_big, font_small, tick)
                if btn.collidepoint(event.pos):
                    return   # sale del menú → inicia juego

        btn = draw_title(screen, font_big, font_small, tick)
        pygame.display.flip()
        clock.tick(FPS)
        tick += 1