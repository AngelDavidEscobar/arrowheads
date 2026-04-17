# menu.py
import pygame, sys
import settings as S


def run_menu(screen, clock):
    font_big   = pygame.font.Font(None, 62)
    font_med   = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)
    tick = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn = _draw(screen, font_big, font_med, font_small, tick)
                if btn.collidepoint(event.pos):
                    return

        _draw(screen, font_big, font_med, font_small, tick)
        pygame.display.flip()
        clock.tick(S.FPS)
        tick += 1


def _draw(surface, font_big, font_med, font_small, tick):
    surface.fill((210, 180, 140))
    b = 18
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT

    # Marco doble
    pygame.draw.rect(surface, (90, 60, 30),  (b,   b,   W-b*2,    H-b*2),    4)
    pygame.draw.rect(surface, (90, 60, 30),  (b+8, b+8, W-b*2-16, H-b*2-16), 1)

    # Título
    t = font_big.render("ARROWHEADS", True, (50, 30, 10))
    surface.blit(t, t.get_rect(center=(W//2, 170)))
    s = font_med.render("Hunt or be hunted", True, (90, 60, 30))
    surface.blit(s, s.get_rect(center=(W//2, 222)))

    # Flechas animadas
    for x in (150, 460):
        col = (200, 140, 50) if (tick // 25) % 2 == 0 else (90, 60, 30)
        pygame.draw.line(surface, col, (x, 167), (x+28, 172), 3)
        pygame.draw.polygon(surface, col, [(x+26,167),(x+34,172),(x+26,177)])

    # Botón JUGAR
    btn = pygame.Rect(W//2 - 90, 305, 180, 52)
    hover = btn.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surface, (200,140,50) if hover else (90,60,30),
                     btn, border_radius=8)
    pygame.draw.rect(surface, (90, 60, 30), btn, 2, border_radius=8)
    lbl = font_med.render("JUGAR", True, (210, 180, 140))
    surface.blit(lbl, lbl.get_rect(center=btn.center))

    # Cuadro power-ups
    px, py, pw, ph = W//2 - 170, 378, 340, 125
    pygame.draw.rect(surface, (180,150,110), (px,py,pw,ph), border_radius=6)
    pygame.draw.rect(surface, (90, 60, 30),  (px,py,pw,ph), 1, border_radius=6)

    pu_info = [
        ("Power-ups  (10 segundos cada uno)", (50,  30,  10)),
        ("Azul    P  —  Flechas penetrantes", (70, 130, 180)),
        ("Morado  T  —  Triple flecha",       (180, 80, 180)),
        ("Dorado  E  —  Escudo  (inmunidad)", (200,170,  40)),
    ]
    for i, (txt, col) in enumerate(pu_info):
        t = font_small.render(txt, True, col)
        surface.blit(t, t.get_rect(center=(W//2, py + 20 + i*28)))

    # Controles
    controls = ["WASD / flechas — mover", "Click — disparar",
                "ESC — pausa", "Nivel 2 se desbloquea en oleada 6"]
    for i, h in enumerate(controls):
        t = font_small.render(h, True, (90, 60, 30))
        surface.blit(t, t.get_rect(center=(W//2, 526 + i*22)))

    return btn