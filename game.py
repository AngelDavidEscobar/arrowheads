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
    SLIDER_W = 100

    def __init__(self):
        self.font_title = pygame.font.Font(None, 48)
        self.font_lbl   = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.active_slider = None

    def draw(self, surface):
        ov = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        surface.blit(ov,(0,0))

        cx = S.SCREEN_WIDTH  // 2
        cy = S.SCREEN_HEIGHT // 2

        panel = pygame.Rect(cx-150, cy-170, 300, 340)
        pygame.draw.rect(surface,(40,28,18),  panel, border_radius=10)
        pygame.draw.rect(surface,(200,140,50),panel, 2, border_radius=10)

        t = self.font_title.render("PAUSA", True, (200,140,50))
        surface.blit(t, t.get_rect(center=(cx, cy-132)))
        pygame.draw.line(surface,(200,140,50),(cx-110,cy-103),(cx+110,cy-103),1)

        self._draw_slider(surface, cx, cy-62, "Música",  S.VOL_MUSIC, "music")
        self._draw_slider(surface, cx, cy+2,  "Efectos", S.VOL_SFX,   "sfx")

        pygame.draw.line(surface,(200,140,50),(cx-110,cy+52),(cx+110,cy+52),1)

        btn_cont = self._btn_rect(cx, cy+95)
        btn_menu = self._btn_rect(cx, cy+148)
        self._draw_btn(surface, btn_cont, "Continuar")
        self._draw_btn(surface, btn_menu, "Menú principal")
        return btn_cont, btn_menu

    def _draw_slider(self, surface, cx, y, label, value, key):
        lbl = self.font_lbl.render(label, True, (220,200,170))
        surface.blit(lbl, lbl.get_rect(midright=(cx-8, y+10)))
        sx, sw = cx+8, self.SLIDER_W
        pygame.draw.rect(surface,(80,60,40),(sx,y+4,sw,12),border_radius=6)
        fw = int(sw*value)
        pygame.draw.rect(surface,(200,140,50),(sx,y+4,fw,12),border_radius=6)
        kx = sx+fw
        pygame.draw.circle(surface,(240,220,180),(kx,y+10),8)
        pygame.draw.circle(surface,(200,140, 50),(kx,y+10),8,2)
        pct = self.font_small.render(f"{int(value*100)}%",True,(200,200,180))
        surface.blit(pct,(sx+sw+8,y+4))
        setattr(self, f"_sr_{key}", pygame.Rect(sx,y,sw,20))

    def _btn_rect(self, cx, cy):
        return pygame.Rect(cx-90, cy-20, 180, 40)

    def _draw_btn(self, surface, rect, text):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface,(200,140,50) if hover else (90,60,30),
                         rect, border_radius=8)
        pygame.draw.rect(surface,(200,140,50),rect,2,border_radius=8)
        t = self.font_lbl.render(text, True, (230,210,180))
        surface.blit(t, t.get_rect(center=rect.center))

    def handle_event(self, event):
        cx = S.SCREEN_WIDTH  // 2
        cy = S.SCREEN_HEIGHT // 2
        btn_cont = self._btn_rect(cx, cy+95)
        btn_menu = self._btn_rect(cx, cy+148)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            pos = event.pos
            if btn_cont.collidepoint(pos): return "resume"
            if btn_menu.collidepoint(pos): return "mainmenu"
            for key in ("music","sfx"):
                r = getattr(self, f"_sr_{key}", None)
                if r and r.collidepoint(pos):
                    self.active_slider = key
        if event.type == pygame.MOUSEBUTTONUP and event.button==1:
            self.active_slider = None
        if event.type == pygame.MOUSEMOTION and self.active_slider:
            self._slide(event.pos)
        return None

    def _slide(self, pos):
        key = self.active_slider
        r   = getattr(self, f"_sr_{key}", None)
        if not r: return
        v = max(0.0, min(1.0,(pos[0]-r.left)/r.width))
        if key=="music":
            S.VOL_MUSIC=v; pygame.mixer.music.set_volume(v)
        else:
            S.VOL_SFX=v; set_sfx_volume(v)


# ── HUD helpers ───────────────────────────────────────────────────────────────

def _pu_bar(surface, font, label, timer, max_t, color, y):
    bx,bw,bh = 20,170,14
    pct = timer/max_t
    pygame.draw.rect(surface, S.C_BORDER,    (bx,y,bw,bh),border_radius=4)
    pygame.draw.rect(surface, color,         (bx,y,int(bw*pct),bh),border_radius=4)
    pygame.draw.rect(surface,(200,200,200),  (bx,y,bw,bh),1,border_radius=4)
    t = font.render(f"{label}  {timer//60}s", True, S.C_UI_TEXT)
    surface.blit(t,(bx+bw+8,y-1))


def _overlay(surface, alpha=130):
    ov = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0,0,0,alpha))
    surface.blit(ov,(0,0))


def _draw_level_banner(surface, font_big, font_med, level_cfg, countdown):
    _overlay(surface, 160)
    cx, cy = S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2
    t1 = font_big.render(f"Nivel {S._current_level}", True, S.C_HIGHLIGHT)
    t2 = font_med.render(level_cfg["name"],           True, (220,220,200))
    secs = countdown // 60 + 1
    t3 = font_med.render(f"Preparándose en {secs}s...", True, (180,180,160))
    surface.blit(t1, t1.get_rect(center=(cx, cy-50)))
    surface.blit(t2, t2.get_rect(center=(cx, cy+5)))
    surface.blit(t3, t3.get_rect(center=(cx, cy+50)))


def _draw_game_over(surface, font_big, font_med, font_small, score, wave, level):
    _overlay(surface, 180)
    lines = [
        (font_big,   "GAME OVER",                       (200,40,40),   -90),
        (font_med,   f"Nivel {level}  ·  Oleada {wave}",S.C_HIGHLIGHT, -28),
        (font_med,   f"Puntuación: {score}",            S.C_HIGHLIGHT,   28),
        (font_small, "Click o ESC para volver",         (200,200,180),   88),
    ]
    cx, cy = S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2
    for fnt,txt,col,dy in lines:
        t = fnt.render(txt, True, col)
        surface.blit(t, t.get_rect(center=(cx, cy+dy)))


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

    wall_type  = S.LEVELS[wm.level].get("WALL_TYPE","cross")
    wall_rects = build_walls(wall_type) if S.LEVELS[wm.level].get("HAS_WALLS") else []

    bg_surface = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    _redraw_bg(bg_surface, wm.level_cfg)

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
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_over: return player.score
                    paused = True
                    try: pygame.mixer.music.pause()
                    except Exception: pass
                if event.key == pygame.K_SPACE and not game_over:
                    player.try_dash(pygame.key.get_pressed())

            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                if game_over: return player.score
                before = len(arrows)
                player.shoot(*event.pos, arrows)
                if len(arrows) > before:
                    play("shoot")

        # ── Lógica ───────────────────────────────────────────────────────
        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            _push_out_of_walls(player.rect, wall_rects)

            arrows.update()
            powerups.update()

            for arrow in list(arrows):
                for wr in wall_rects:
                    if wr.colliderect(arrow.rect):
                        arrow.kill(); break

            wave_done, level_changed, in_level_pause = wm.update(enemies, player)
            S._current_level = wm.level

            if level_changed:
                level_banner_timer = wm.level_cfg.get("LEVEL_PAUSE", 600)
                wall_type  = S.LEVELS[wm.level].get("WALL_TYPE","cross")
                wall_rects = (build_walls(wall_type)
                              if S.LEVELS[wm.level].get("HAS_WALLS") else [])
                _redraw_bg(bg_surface, wm.level_cfg)

            if level_banner_timer > 0:
                level_banner_timer -= 1

            for enemy in enemies:
                _push_out_of_walls(enemy.rect, wall_rects)

            _resolve_arrow_hits(player, enemies, arrows, powerups)

            for pu in pygame.sprite.spritecollide(player, powerups, True):
                player.activate_powerup(pu.kind)
                play("powerup")

            if hit_timer == 0 and not player.dashing:
                if pygame.sprite.spritecollide(player, enemies, False):
                    player.take_hit()
                    if not player.shielded:
                        hit_timer = 90
                    if player.hp <= 0:
                        game_over = True

            if hit_timer > 0: hit_timer -= 1

        # ── Dibujo ───────────────────────────────────────────────────────
        screen.blit(bg_surface,(0,0))

        if wall_rects:
            wt = S.LEVELS[wm.level].get("WALL_TYPE","cross")
            draw_walls(screen, wall_rects, wt)

        powerups.draw(screen)
        enemies.draw(screen)
        arrows.draw(screen)

        if player.shielded:   _draw_shield_aura(screen, player)
        if player.dashing:    _draw_dash_trail(screen, player)
        if hit_timer==0 or (hit_timer//8)%2==0:
            player_g.draw(screen)

        _draw_dash_indicator(screen, font_hud, player)
        _draw_hud(screen, font_hud, font_med, player, wm)

        # Cuenta regresiva entre oleadas (solo si no es pausa de nivel)
        if wm.pause_timer > 0 and not wm.in_level_pause:
            secs = (wm.level_cfg.get("WAVE_PAUSE",300) - wm.pause_timer)//60 + 1
            msg  = font_med.render(f"Oleada {wm.wave+1} en {secs}s...",
                                   True, S.C_HIGHLIGHT)
            screen.blit(msg, msg.get_rect(
                center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2)))

        # Banner de cambio de nivel
        if level_banner_timer > 0:
            _draw_level_banner(screen, font_big, font_med,
                               wm.level_cfg, level_banner_timer)

        if game_over:
            _draw_game_over(screen, font_big, font_med, font_small,
                            player.score, wm.wave, wm.level)
        if paused:
            pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(S.FPS)


# ── Auxiliares ────────────────────────────────────────────────────────────────

def _push_out_of_walls(rect, wall_rects):
    for wr in wall_rects:
        if not wr.colliderect(rect): continue
        ol = rect.right  - wr.left
        or_= wr.right    - rect.left
        ot = rect.bottom - wr.top
        ob = wr.bottom   - rect.top
        if min(ol,or_) < min(ot,ob):
            if ol < or_: rect.right = wr.left
            else:        rect.left  = wr.right
        else:
            if ot < ob:  rect.bottom = wr.top
            else:        rect.top    = wr.bottom


def _redraw_bg(surface, level_cfg):
    draw_terrain(surface, level_cfg["TERRAIN"],
                 level_cfg["C_BG"], level_cfg["C_GRID"],
                 level_cfg["C_BORDER"], level_cfg["C_ACCENT"])


def _draw_shield_aura(screen, player):
    cx,cy = player.rect.center; r=20
    aura = pygame.Surface((r*2+4,r*2+4),pygame.SRCALPHA)
    pygame.draw.circle(aura,(*S.C_PU_SHIELD, 70),(r+2,r+2),r)
    pygame.draw.circle(aura,(*S.C_PU_SHIELD,200),(r+2,r+2),r,2)
    screen.blit(aura,(cx-r-2,cy-r-2))


def _draw_dash_trail(screen, player):
    cx,cy = player.rect.center
    trail = pygame.Surface((20,20),pygame.SRCALPHA)
    alpha = int(180*(player.dash_frames/S.DASH_FRAMES))
    pygame.draw.circle(trail,(255,255,220,alpha),(10,10),8)
    ox = int(-player.dash_dx*14); oy = int(-player.dash_dy*14)
    screen.blit(trail,(cx+ox-10,cy+oy-10))


def _draw_dash_indicator(screen, font, player):
    x,y = 20, S.SCREEN_HEIGHT-36
    if player.dash_cooldown == 0:
        t = font.render("DASH listo", True, (220,220,100))
        screen.blit(t,(x,y))
    else:
        pct = 1.0 - player.dash_cooldown/S.DASH_COOLDOWN
        t   = font.render(f"DASH  {player.dash_cooldown//60+1}s",
                          True, (130,130,80))
        screen.blit(t,(x,y))
        pygame.draw.rect(screen,(60,55,40),  (x,y+16,80,6),border_radius=3)
        pygame.draw.rect(screen,(200,180,60),(x,y+16,int(80*pct),6),border_radius=3)


def _draw_hud(screen, font_hud, font_med, player, wm):
    for i in range(S.PLAYER_HP):
        col = (180,40,40) if i<player.hp else (80,60,50)
        pts = [(22+i*24,26),(29+i*24,19),(36+i*24,26),(29+i*24,34)]
        pygame.draw.polygon(screen,col,pts)
        if i<player.hp:
            pygame.draw.polygon(screen,(220,80,80),pts,1)

    wt = font_hud.render(f"Nivel {wm.level}  ·  Oleada {wm.wave}",
                         True, S.C_UI_TEXT)
    screen.blit(wt, wt.get_rect(center=(S.SCREEN_WIDTH//2,16)))

    st = font_hud.render(f"{player.score} pts", True, S.C_UI_TEXT)
    screen.blit(st,(S.SCREEN_WIDTH-st.get_width()-20,10))

    if player.combo > 1:
        ct = font_med.render(f"x{player.combo} COMBO", True, S.C_HIGHLIGHT)
        screen.blit(ct, ct.get_rect(
            center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT-28)))

    bar_y = 48
    if player.pu_pierce > 0:
        _pu_bar(screen,font_hud,"Penetración",
                player.pu_pierce,S.PU_PIERCE_DURATION,S.C_PU_PIERCE,bar_y)
        bar_y += 26
    if player.pu_triple > 0:
        _pu_bar(screen,font_hud,"Triple",
                player.pu_triple,S.PU_TRIPLE_DURATION,S.C_PU_TRIPLE,bar_y)
        bar_y += 26
    if player.pu_shield > 0:
        _pu_bar(screen,font_hud,"Escudo",
                player.pu_shield,S.PU_SHIELD_DURATION,S.C_PU_SHIELD,bar_y)


def _resolve_arrow_hits(player, enemies, arrows, powerups):
    for arrow in list(arrows):
        if not arrow.alive(): continue
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