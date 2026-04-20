# game.py
import pygame, sys, random
import settings as S
from src.entities     import Player, Enemy, PowerUp
from src.wave_manager import WaveManager
from src.terrain      import draw_terrain
from src.sounds       import play, set_sfx_volume
from src.walls        import build_walls, draw_walls


# ── Menú de pausa ─────────────────────────────────────────────────────────────

class PauseMenu:
    """
    Menú superpuesto al juego cuando se pulsa ESC.
    Permite ajustar volumen de música y SFX con sliders de teclado/ratón.
    """
    BTN_W, BTN_H = 200, 40
    SLIDER_W     = 200

    def __init__(self):
        self.font_title = pygame.font.Font(None, 48)
        self.font_lbl   = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.active_slider = None   # "music" | "sfx" | None

    # ── dibujo ───────────────────────────────────────────────────────────────
    def draw(self, surface):
        # Overlay oscuro semitransparente
        ov = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

        cx = S.SCREEN_WIDTH  // 2
        cy = S.SCREEN_HEIGHT // 2

        # Panel de fondo
        panel = pygame.Rect(cx - 160, cy - 170, 320, 340)
        pygame.draw.rect(surface, (40, 28, 18),  panel, border_radius=10)
        pygame.draw.rect(surface, (200, 140, 50), panel, 2, border_radius=10)

        # Título
        t = self.font_title.render("PAUSA", True, (200, 140, 50))
        surface.blit(t, t.get_rect(center=(cx, cy - 130)))

        # Separador
        pygame.draw.line(surface, (200, 140, 50),
                         (cx - 120, cy - 100), (cx + 120, cy - 100), 1)

        # Slider música
        self._draw_slider(surface, cx, cy - 60,
                          "Música", S.VOL_MUSIC, "music")

        # Slider SFX
        self._draw_slider(surface, cx, cy + 10,
                          "Efectos", S.VOL_SFX, "sfx")

        # Separador
        pygame.draw.line(surface, (200, 140, 50),
                         (cx - 120, cy + 55), (cx + 120, cy + 55), 1)

        # Botón continuar
        btn_cont = self._btn_rect(cx, cy + 95)
        self._draw_btn(surface, btn_cont, "Continuar")

        # Botón menú principal
        btn_menu = self._btn_rect(cx, cy + 148)
        self._draw_btn(surface, btn_menu, "Menú principal")

        return btn_cont, btn_menu

    def _draw_slider(self, surface, cx, y, label, value, key):
        lbl = self.font_lbl.render(label, True, (220, 200, 170))
        surface.blit(lbl, lbl.get_rect(midright=(cx - 10, y + 10)))

        sx  = cx + 10
        sw  = self.SLIDER_W
        # Pista
        pygame.draw.rect(surface, (80, 60, 40),
                         (sx, y + 4, sw, 12), border_radius=6)
        # Relleno
        fill_w = int(sw * value)
        pygame.draw.rect(surface, (200, 140, 50),
                         (sx, y + 4, fill_w, 12), border_radius=6)
        # Perilla
        knob_x = sx + fill_w
        pygame.draw.circle(surface, (240, 220, 180), (knob_x, y + 10), 9)
        pygame.draw.circle(surface, (200, 140, 50),  (knob_x, y + 10), 9, 2)

        # Porcentaje
        pct = self.font_small.render(f"{int(value*100)}%", True, (200, 200, 180))
        surface.blit(pct, (sx + sw + 10, y + 4))

        # Guardar rect del slider para detectar clics
        setattr(self, f"_slider_rect_{key}",
                pygame.Rect(sx, y, sw, 20))

    def _btn_rect(self, cx, cy):
        return pygame.Rect(cx - self.BTN_W // 2, cy - self.BTN_H // 2,
                           self.BTN_W, self.BTN_H)

    def _draw_btn(self, surface, rect, text):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (200, 140, 50) if hover else (90, 60, 30)
        pygame.draw.rect(surface, color,       rect, border_radius=8)
        pygame.draw.rect(surface, (200,140,50), rect, 2, border_radius=8)
        t = self.font_lbl.render(text, True, (230, 210, 180))
        surface.blit(t, t.get_rect(center=rect.center))

    # ── eventos ──────────────────────────────────────────────────────────────
    def handle_event(self, event):
        """
        Devuelve:
          "resume"    → continuar el juego
          "mainmenu"  → volver al menú principal
          None        → ninguna acción especial
        """
        cx = S.SCREEN_WIDTH  // 2
        cy = S.SCREEN_HEIGHT // 2
        btn_cont = self._btn_rect(cx, cy + 95)
        btn_menu = self._btn_rect(cx, cy + 148)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if btn_cont.collidepoint(pos): return "resume"
            if btn_menu.collidepoint(pos): return "mainmenu"
            for key in ("music", "sfx"):
                r = getattr(self, f"_slider_rect_{key}", None)
                if r and r.collidepoint(pos):
                    self.active_slider = key

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active_slider = None

        if event.type == pygame.MOUSEMOTION and self.active_slider:
            self._update_slider_from_mouse(event.pos)

        return None

    def _update_slider_from_mouse(self, pos):
        key = self.active_slider
        r   = getattr(self, f"_slider_rect_{key}", None)
        if r is None:
            return
        value = max(0.0, min(1.0, (pos[0] - r.left) / r.width))
        if key == "music":
            S.VOL_MUSIC = value
            pygame.mixer.music.set_volume(value)
        else:
            S.VOL_SFX = value
            set_sfx_volume(value)


# ── HUD helpers ───────────────────────────────────────────────────────────────

def _pu_bar(surface, font, label, timer, max_t, color, y):
    bx, bw, bh = 20, 170, 14
    pct = timer / max_t
    pygame.draw.rect(surface, S.C_BORDER,     (bx, y, bw, bh), border_radius=4)
    pygame.draw.rect(surface, color,          (bx, y, int(bw*pct), bh), border_radius=4)
    pygame.draw.rect(surface, (200, 200, 200),(bx, y, bw, bh), 1, border_radius=4)
    t = font.render(f"{label}  {timer//60}s", True, S.C_UI_TEXT)
    surface.blit(t, (bx + bw + 8, y - 1))


def _overlay(surface, alpha=130):
    ov = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    surface.blit(ov, (0, 0))


def _draw_level_banner(surface, font_big, font_med, level_cfg):
    _overlay(surface, 150)
    t1 = font_big.render(f"Nivel {S._current_level}", True, S.C_HIGHLIGHT)
    t2 = font_med.render(level_cfg["name"],           True, (220, 220, 200))
    surface.blit(t1, t1.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 - 35)))
    surface.blit(t2, t2.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 + 15)))


def _draw_game_over(surface, font_big, font_med, font_small, score, wave, level):
    _overlay(surface, 160)
    lines = [
        (font_big,   "GAME OVER",                        (180,  40,  40), -90),
        (font_med,   f"Nivel {level}  ·  Oleada {wave}", S.C_HIGHLIGHT,   -28),
        (font_med,   f"Puntuación: {score}",             S.C_HIGHLIGHT,    28),
        (font_small, "Click o ESC para volver",          (200, 200, 180),   88),
    ]
    cx, cy = S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2
    for fnt, txt, col, dy in lines:
        t = fnt.render(txt, True, col)
        surface.blit(t, t.get_rect(center=(cx, cy + dy)))


# ── Loop principal ────────────────────────────────────────────────────────────

def run_game(screen, clock):
    font_big   = pygame.font.Font(None, 62)
    font_med   = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)
    font_hud   = pygame.font.Font(None, 27)

    player   = Player()
    player_g = pygame.sprite.GroupSingle(player)
    enemies  = pygame.sprite.Group()
    arrows   = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    wm = WaveManager()
    wm.start_wave(1, enemies)
    S._current_level = wm.level

    pause_menu         = PauseMenu()
    paused             = False
    game_over          = False
    hit_timer          = 0
    level_banner_timer = 0

    # Muros del nivel actual
    wall_rects = build_walls() if S.LEVELS[wm.level].get("HAS_WALLS") else []

    # Caché del fondo
    bg_surface = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    _redraw_bg(bg_surface, wm.level_cfg)
    last_level = wm.level

    while True:
        # ── Eventos ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if paused:
                action = pause_menu.handle_event(event)
                if action == "resume":
                    paused = False
                    try: pygame.mixer.music.unpause()
                    except Exception: pass
                elif action == "mainmenu":
                    return player.score
                continue   # bloquea el resto de eventos mientras está pausado

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_over:
                        return player.score
                    paused = True
                    try: pygame.mixer.music.pause()
                    except Exception: pass

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    return player.score
                arrows_before = len(arrows)
                player.shoot(*event.pos, arrows)
                if len(arrows) > arrows_before:
                    play("shoot")

        # ── Lógica ───────────────────────────────────────────────────────
        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)

            # Colisión jugador con muros
            _push_out_of_walls(player.rect, wall_rects)

            arrows.update()
            powerups.update()

            # Matar flechas que choquen con muros
            for arrow in list(arrows):
                for wr in wall_rects:
                    if wr.colliderect(arrow.rect):
                        arrow.kill()
                        break

            wave_done, level_changed = wm.update(enemies, player)
            S._current_level = wm.level

            if level_changed:
                level_banner_timer = 180
                wall_rects = (build_walls()
                              if S.LEVELS[wm.level].get("HAS_WALLS")
                              else [])
                _redraw_bg(bg_surface, wm.level_cfg)
                last_level = wm.level

            # Empujar enemigos fuera de muros
            for enemy in enemies:
                _push_out_of_walls(enemy.rect, wall_rects)

            # Colisiones flechas vs enemigos
            _resolve_arrow_hits(player, enemies, arrows, powerups)

            # Power-ups recogidos
            for pu in pygame.sprite.spritecollide(player, powerups, True):
                player.activate_powerup(pu.kind)
                play("powerup")

            # Enemigos vs jugador
            if hit_timer == 0:
                if pygame.sprite.spritecollide(player, enemies, False):
                    player.take_hit()
                    if not player.shielded:
                        hit_timer = 90
                    if player.hp <= 0:
                        game_over = True

            if hit_timer          > 0: hit_timer          -= 1
            if level_banner_timer > 0: level_banner_timer -= 1

        # ── Dibujo ───────────────────────────────────────────────────────
        screen.blit(bg_surface, (0, 0))

        # Muros sobre el suelo
        if wall_rects:
            draw_walls(screen, wall_rects)

        powerups.draw(screen)
        enemies.draw(screen)
        arrows.draw(screen)

        if player.shielded:
            _draw_shield_aura(screen, player)
        if hit_timer == 0 or (hit_timer // 8) % 2 == 0:
            player_g.draw(screen)

        _draw_hud(screen, font_hud, font_med, player, wm)

        if wm.pause_timer > 0:
            secs = (S.WAVE_PAUSE - wm.pause_timer) // 60 + 1
            msg  = font_med.render(f"Oleada {wm.wave + 1} en {secs}s...",
                                   True, S.C_HIGHLIGHT)
            screen.blit(msg, msg.get_rect(
                center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2)))

        if level_banner_timer > 0:
            _draw_level_banner(screen, font_big, font_med, wm.level_cfg)

        if game_over:
            _draw_game_over(screen, font_big, font_med, font_small,
                            player.score, wm.wave, wm.level)

        if paused:
            pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(S.FPS)


# ── Auxiliares ────────────────────────────────────────────────────────────────

def _push_out_of_walls(rect, wall_rects):
    """Empuja un rect fuera de los muros resolviendo el eje de menor penetración."""
    for wr in wall_rects:
        if not wr.colliderect(rect):
            continue
        # Calcular solapamiento en cada eje
        overlap_left  = rect.right  - wr.left
        overlap_right = wr.right    - rect.left
        overlap_top   = rect.bottom - wr.top
        overlap_bot   = wr.bottom   - rect.top

        min_x = min(overlap_left, overlap_right)
        min_y = min(overlap_top,  overlap_bot)

        if min_x < min_y:
            if overlap_left < overlap_right:
                rect.right = wr.left
            else:
                rect.left  = wr.right
        else:
            if overlap_top < overlap_bot:
                rect.bottom = wr.top
            else:
                rect.top    = wr.bottom


def _redraw_bg(surface, level_cfg):
    draw_terrain(
        surface,
        level_cfg["TERRAIN"],
        level_cfg["C_BG"],
        level_cfg["C_GRID"],
        level_cfg["C_BORDER"],
        level_cfg["C_ACCENT"],
    )


def _draw_shield_aura(screen, player):
    cx, cy = player.rect.center
    radius = 20
    aura   = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
    pygame.draw.circle(aura, (*S.C_PU_SHIELD,  70), (radius+2, radius+2), radius)
    pygame.draw.circle(aura, (*S.C_PU_SHIELD, 200), (radius+2, radius+2), radius, 2)
    screen.blit(aura, (cx - radius - 2, cy - radius - 2))


def _draw_hud(screen, font_hud, font_med, player, wm):
    # Corazones
    for i in range(S.PLAYER_HP):
        col = (180, 40, 40) if i < player.hp else (80, 60, 50)
        pts = [(22+i*24,26),(29+i*24,19),(36+i*24,26),(29+i*24,34)]
        pygame.draw.polygon(screen, col, pts)
        if i < player.hp:
            pygame.draw.polygon(screen, (220, 80, 80), pts, 1)

    wt = font_hud.render(f"Nivel {wm.level}  ·  Oleada {wm.wave}", True, S.C_UI_TEXT)
    screen.blit(wt, wt.get_rect(center=(S.SCREEN_WIDTH//2, 16)))

    st = font_hud.render(f"{player.score} pts", True, S.C_UI_TEXT)
    screen.blit(st, (S.SCREEN_WIDTH - st.get_width() - 20, 10))

    if player.combo > 1:
        ct = font_med.render(f"x{player.combo} COMBO", True, S.C_HIGHLIGHT)
        screen.blit(ct, ct.get_rect(
            center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT - 28)))

    bar_y = 48
    if player.pu_pierce > 0:
        _pu_bar(screen, font_hud, "Penetrante",
                player.pu_pierce, S.PU_PIERCE_DURATION, S.C_PU_PIERCE, bar_y)
        bar_y += 26
    if player.pu_triple > 0:
        _pu_bar(screen, font_hud, "Triple",
                player.pu_triple, S.PU_TRIPLE_DURATION, S.C_PU_TRIPLE, bar_y)
        bar_y += 26
    if player.pu_shield > 0:
        _pu_bar(screen, font_hud, "Escudo",
                player.pu_shield, S.PU_SHIELD_DURATION, S.C_PU_SHIELD, bar_y)


def _resolve_arrow_hits(player, enemies, arrows, powerups):
    for arrow in list(arrows):
        if not arrow.alive():
            continue
        if arrow.pierce:
            for enemy in list(enemies):
                if (arrow.rect.colliderect(enemy.rect)
                        and id(enemy) not in arrow.hit_set):
                    arrow.hit_set.add(id(enemy))
                    _damage_enemy(enemy, player, powerups)
        else:
            collided = pygame.sprite.spritecollide(arrow, enemies, False)
            if collided:
                arrow.kill()
                for enemy in collided:
                    _damage_enemy(enemy, player, powerups)


def _damage_enemy(enemy, player, powerups):
    enemy.hp -= 1
    if enemy.hp <= 0:
        player.score += 10 * player.combo
        play("enemy_die")
        if random.random() < S.PU_DROP_CHANCE:
            powerups.add(PowerUp(*enemy.rect.center))
        enemy.kill()