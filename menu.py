# menu.py
import pygame, sys
import settings as S
from src.sounds import set_sfx_volume


def run_menu(screen, clock):
    font_big   = pygame.font.Font(None, 72)
    font_med   = pygame.font.Font(None, 38)
    font_small = pygame.font.Font(None, 26)
    tick       = 0
    state      = "main"   # "main" | "instructions" | "settings"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and state != "main":
                    state = "main"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                if state == "instructions":
                    state = "main"; continue
                if state == "settings":
                    state = "main"; continue

                btn_play, btn_instr, btn_cfg = _draw_main(
                    screen, font_big, font_med, font_small, tick)
                if btn_play.collidepoint(pos):
                    return
                if btn_instr.collidepoint(pos):
                    state = "instructions"
                if btn_cfg.collidepoint(pos):
                    state = "settings"

            if state == "settings":
                _handle_settings_event(event)

        if state == "main":
            _draw_main(screen, font_big, font_med, font_small, tick)
        elif state == "instructions":
            _draw_instructions(screen, font_med, font_small)
        elif state == "settings":
            _draw_settings(screen, font_med, font_small)

        pygame.display.flip()
        clock.tick(S.FPS)
        tick += 1


# ── Slider helper ─────────────────────────────────────────────────────────────

_active_slider = None   # "music" | "sfx" | None

def _handle_settings_event(event):
    global _active_slider
    cx = S.SCREEN_WIDTH  // 2
    cy = S.SCREEN_HEIGHT // 2
    SW = 160   # ancho del slider

    sliders = {
        "music": pygame.Rect(cx + 20, cy - 42, SW, 20),
        "sfx":   pygame.Rect(cx + 20, cy + 18, SW, 20),
    }

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for key, r in sliders.items():
            if r.collidepoint(event.pos):
                _active_slider = key
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        _active_slider = None
    if event.type == pygame.MOUSEMOTION and _active_slider:
        r = sliders[_active_slider]
        v = max(0.0, min(1.0, (event.pos[0] - r.left) / r.width))
        if _active_slider == "music":
            S.VOL_MUSIC = v
            pygame.mixer.music.set_volume(v)
        else:
            S.VOL_SFX = v
            set_sfx_volume(v)


# ── Pantallas ─────────────────────────────────────────────────────────────────

def _draw_main(surface, font_big, font_med, font_small, tick):
    surface.fill((210, 180, 140))
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    b    = 18

    pygame.draw.rect(surface,(90,60,30),(b,b,W-b*2,H-b*2),4)
    pygame.draw.rect(surface,(90,60,30),(b+8,b+8,W-b*2-16,H-b*2-16),1)

    t = font_big.render("ARROWHEADS", True, (50,30,10))
    surface.blit(t, t.get_rect(center=(W//2, 195)))
    s = font_med.render("Hunt or be hunted", True, (90,60,30))
    surface.blit(s, s.get_rect(center=(W//2, 255)))

    for x in (130, 478):
        col = (200,140,50) if (tick//25)%2==0 else (90,60,30)
        pygame.draw.line(surface, col, (x,190),(x+28,195),3)
        pygame.draw.polygon(surface, col, [(x+26,190),(x+34,195),(x+26,200)])

    btn_play  = pygame.Rect(W//2-100, 320, 200, 52)
    btn_instr = pygame.Rect(W//2-100, 390, 200, 46)
    btn_cfg   = pygame.Rect(W//2-100, 450, 200, 46)

    _btn(surface, btn_play,  font_med,   "JUGAR")
    _btn(surface, btn_instr, font_small, "INSTRUCCIONES")
    _btn(surface, btn_cfg,   font_small, "AJUSTES")

    ver = font_small.render("v1.0", True, (140,110,80))
    surface.blit(ver, (W-46, H-30))

    return btn_play, btn_instr, btn_cfg


def _btn(surface, rect, font, text):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surface, (200,140,50) if hover else (90,60,30),
                     rect, border_radius=8)
    pygame.draw.rect(surface, (90,60,30), rect, 2, border_radius=8)
    lbl = font.render(text, True, (230,210,180))
    surface.blit(lbl, lbl.get_rect(center=rect.center))


def _draw_instructions(surface, font_med, font_small):
    surface.fill((30, 20, 12))
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    pygame.draw.rect(surface,(200,140,50),(18,18,W-36,H-36),2,border_radius=10)

    t = font_med.render("INSTRUCCIONES", True, (200,140,50))
    surface.blit(t, t.get_rect(center=(W//2, 52)))
    pygame.draw.line(surface,(200,140,50),(W//2-140,74),(W//2+140,74),1)

    lines = [
        ("CONTROLES",                          (200,140, 50), True),
        ("WASD / Flechas  —  Mover",           (220,200,170), False),
        ("Click izquierdo  —  Disparar",       (220,200,170), False),
        ("Espacio  —  Dash",                   (220,200,170), False),
        ("ESC  —  Pausar",                     (220,200,170), False),
        ("",None,False),
        ("POWER-UPS  (10 segundos)",           (200,140, 50), True),
        ("P  Azul   — Penetración",            ( 70,130,180), False),
        ("T  Morado — Triple flecha",          (180, 80,180), False),
        ("E  Dorado — Escudo",                 (200,170, 40), False),
        ("",None,False),
        ("DIFICULTAD",                         (200,140, 50), True),
        ("Oleadas 1-3   →  1 golpe",           (220,200,170), False),
        ("Oleadas 4-7   →  2 golpes",          (220,200,170), False),
        ("Oleadas 8-10  →  3 golpes",          (220,200,170), False),
        ("Oleada  11+   →  6 golpes",          (180,160,220), False),
        ("",None,False),
        ("Nivel 2  →  oleada 6  (Bosque)",     (130,180,130), False),
        ("Nivel 3  →  oleada 11 (Montañas)",   (180,210,255), False),
        ("",None,False),
        ("Click para volver",                  (140,130,110), False),
    ]
    y = 90
    for text, color, bold in lines:
        if not text:
            y += 10; continue
        fnt = font_med if bold else font_small
        t   = fnt.render(text, True, color)
        surface.blit(t, (46, y))
        y += 28 if bold else 22


def _draw_settings(surface, font_med, font_small):
    surface.fill((30, 20, 12))
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    cx, cy = W//2, H//2
    pygame.draw.rect(surface,(200,140,50),(18,18,W-36,H-36),2,border_radius=10)

    t = font_med.render("AJUSTES", True, (200,140,50))
    surface.blit(t, t.get_rect(center=(W//2, 52)))
    pygame.draw.line(surface,(200,140,50),(W//2-100,74),(W//2+100,74),1)

    SW = 160
    _draw_menu_slider(surface, font_small, cx, cy-40,
                      "Música",  S.VOL_MUSIC, SW)
    _draw_menu_slider(surface, font_small, cx, cy+20,
                      "Efectos", S.VOL_SFX,   SW)

    note = font_small.render("Click para volver", True, (140,130,110))
    surface.blit(note, note.get_rect(center=(W//2, H-50)))


def _draw_menu_slider(surface, font, cx, y, label, value, sw):
    lbl = font.render(label, True, (220,200,170))
    surface.blit(lbl, lbl.get_rect(midright=(cx-12, y+10)))

    sx = cx + 20
    pygame.draw.rect(surface,(80,60,40),(sx,y+4,sw,12),border_radius=6)
    fw = int(sw * value)
    pygame.draw.rect(surface,(200,140,50),(sx,y+4,fw,12),border_radius=6)
    kx = sx + fw
    pygame.draw.circle(surface,(240,220,180),(kx,y+10),8)
    pygame.draw.circle(surface,(200,140, 50),(kx,y+10),8,2)
    pct = font.render(f"{int(value*100)}%", True, (200,200,180))
    surface.blit(pct,(sx+sw+10, y+4))