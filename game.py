# game.py
import pygame, sys, random
import settings as S
from src.entities     import Player, Enemy, PowerUp
from src.wave_manager import WaveManager
from src.terrain      import draw_terrain


# ── HUD helpers ──────────────────────────────────────────────────────────────

def _pu_bar(surface, font, label, timer, max_t, color, y):
    bx, bw, bh = 20, 170, 14
    pct = timer / max_t
    pygame.draw.rect(surface, S.C_BORDER, (bx, y, bw, bh), border_radius=4)
    pygame.draw.rect(surface, color,      (bx, y, int(bw*pct), bh), border_radius=4)
    pygame.draw.rect(surface, (200,200,200),(bx, y, bw, bh), 1, border_radius=4)
    t = font.render(f"{label}  {timer//60}s", True, S.C_UI_TEXT)
    surface.blit(t, (bx + bw + 8, y - 1))


def _overlay(surface, alpha=130):
    ov = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    surface.blit(ov, (0, 0))


def _draw_pause(surface, font_big, font_small, level_name):
    _overlay(surface, 120)
    t1 = font_big.render("PAUSA", True, S.C_HIGHLIGHT)
    t2 = font_small.render("Pulsa ESC para continuar", True, (220, 220, 200))
    surface.blit(t1, t1.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 - 30)))
    surface.blit(t2, t2.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 + 22)))


def _draw_level_banner(surface, font_big, font_med, level_cfg, alpha):
    """Banner de transición de nivel."""
    _overlay(surface, min(160, alpha * 2))
    col_a = (*S.C_ACCENT[:3], 255)
    t1 = font_big.render(f"Nivel {S._current_level}", True, S.C_HIGHLIGHT)
    t2 = font_med.render(level_cfg["name"],           True, (220, 220, 200))
    surface.blit(t1, t1.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 - 35)))
    surface.blit(t2, t2.get_rect(center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2 + 15)))


def _draw_game_over(surface, font_big, font_med, font_small, score, wave, level):
    _overlay(surface, 160)
    lines = [
        (font_big,   "GAME OVER",                  (180,  40,  40), -90),
        (font_med,   f"Nivel {level} · Oleada {wave}", S.C_HIGHLIGHT, -28),
        (font_med,   f"Puntuación: {score}",        S.C_HIGHLIGHT,   28),
        (font_small, "Click o ESC para volver",     (200, 200, 180),  88),
    ]
    cx = S.SCREEN_WIDTH // 2
    cy = S.SCREEN_HEIGHT // 2
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

    # Exponemos el nivel actual en settings para que _draw_level_banner lo use
    S._current_level = wm.level

    paused        = False
    game_over     = False
    hit_timer     = 0

    level_banner_timer = 0   # frames que muestra el banner de nuevo nivel

    # Caché del fondo (se redibuja solo cuando cambia el nivel)
    bg_surface  = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    _redraw_bg(bg_surface, wm.level_cfg)
    last_level  = wm.level

    while True:
        # ── Eventos ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_over:
                        return player.score
                    paused = not paused
                    try:
                        if paused: pygame.mixer.music.pause()
                        else:      pygame.mixer.music.unpause()
                    except Exception:
                        pass

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    return player.score
                if not paused:
                    player.shoot(*event.pos, arrows)

        # ── Lógica ───────────────────────────────────────────────────────
        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            arrows.update()
            powerups.update()

            wave_done, level_changed = wm.update(enemies, player)
            S._current_level = wm.level

            if level_changed:
                level_banner_timer = 180   # 3 segundos de banner
                _redraw_bg(bg_surface, wm.level_cfg)
                last_level = wm.level

            # Flechas vs enemigos
            _resolve_arrow_hits(player, enemies, arrows, powerups)

            # Power-ups recogidos
            for pu in pygame.sprite.spritecollide(player, powerups, True):
                player.activate_powerup(pu.kind)

            # Enemigos vs jugador
            if hit_timer == 0:
                if pygame.sprite.spritecollide(player, enemies, False):
                    player.take_hit()
                    if not player.shielded:
                        hit_timer = 90
                    if player.hp <= 0:
                        game_over = True

            if hit_timer > 0:
                hit_timer -= 1

            if level_banner_timer > 0:
                level_banner_timer -= 1

        # ── Dibujo ───────────────────────────────────────────────────────
        screen.blit(bg_surface, (0, 0))

        powerups.draw(screen)
        enemies.draw(screen)
        arrows.draw(screen)

        # Jugador (parpadea si invencible por golpe, aura si escudo activo)
        if player.shielded:
            _draw_shield_aura(screen, player)
        if hit_timer == 0 or (hit_timer // 8) % 2 == 0:
            player_g.draw(screen)

        # HUD
        _draw_hud(screen, font_hud, font_med, player, wm)

        # Anuncio de nueva oleada
        if wm.pause_timer > 0:
            secs = (S.WAVE_PAUSE - wm.pause_timer) // 60 + 1
            msg  = font_med.render(f"Oleada {wm.wave + 1} en {secs}s...",
                                   True, S.C_HIGHLIGHT)
            screen.blit(msg, msg.get_rect(
                center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2)))

        # Banner de cambio de nivel
        if level_banner_timer > 0:
            _draw_level_banner(screen, font_big, font_med,
                               wm.level_cfg, level_banner_timer)

        # Overlays de estado
        if paused:
            _draw_pause(screen, font_big, font_small, wm.level_cfg["name"])
        if game_over:
            _draw_game_over(screen, font_big, font_med, font_small,
                            player.score, wm.wave, wm.level)

        pygame.display.flip()
        clock.tick(S.FPS)


# ── Funciones auxiliares ──────────────────────────────────────────────────────

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
    pct    = player.pu_shield / S.PU_SHIELD_DURATION
    radius = 20 + int(4 * pct)
    aura   = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
    pygame.draw.circle(aura, (*S.C_PU_SHIELD, 80), (radius+2, radius+2), radius)
    pygame.draw.circle(aura, (*S.C_PU_SHIELD, 180), (radius+2, radius+2), radius, 2)
    screen.blit(aura, (cx - radius - 2, cy - radius - 2))


def _draw_hud(screen, font_hud, font_med, player, wm):
    # Corazones
    for i in range(S.PLAYER_HP):
        col = (180, 40, 40) if i < player.hp else (80, 60, 50)
        pts = [
            (22 + i*24, 26), (29 + i*24, 19),
            (36 + i*24, 26), (29 + i*24, 34),
        ]
        pygame.draw.polygon(screen, col, pts)
        if i < player.hp:
            pygame.draw.polygon(screen, (220, 80, 80), pts, 1)

    # Oleada y nivel
    wt = font_hud.render(f"Nivel {wm.level}  ·  Oleada {wm.wave}", True, S.C_UI_TEXT)
    screen.blit(wt, wt.get_rect(center=(S.SCREEN_WIDTH//2, 16)))

    # Puntos
    st = font_hud.render(f"{player.score} pts", True, S.C_UI_TEXT)
    screen.blit(st, (S.SCREEN_WIDTH - st.get_width() - 20, 10))

    # Combo
    if player.combo > 1:
        ct = font_med.render(f"x{player.combo} COMBO", True, S.C_HIGHLIGHT)
        screen.blit(ct, ct.get_rect(
            center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT - 28)))

    # Barras de power-up
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
        if random.random() < S.PU_DROP_CHANCE:
            powerups.add(PowerUp(*enemy.rect.center))
        enemy.kill()