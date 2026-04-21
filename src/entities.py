# src/entities.py
import pygame, math, random
import settings as S


# ── Flecha ────────────────────────────────────────────────────────────────────

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, pierce=False):
        super().__init__()
        self.pierce  = pierce
        self.hit_set = set()
        color = S.C_PU_PIERCE if pierce else S.C_ARROW
        surf  = pygame.Surface((16, 5), pygame.SRCALPHA)
        pygame.draw.rect(surf,    color, (0, 2, 13, 2))
        pygame.draw.polygon(surf, color, [(11, 0), (16, 2), (11, 5)])
        angle      = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(surf, angle)
        self.rect  = self.image.get_rect(center=(x, y))
        self.dx, self.dy = dx, dy

    def update(self):
        self.rect.x += self.dx * S.ARROW_SPEED
        self.rect.y += self.dy * S.ARROW_SPEED
        if not pygame.Rect(-20, -20,
                           S.SCREEN_WIDTH + 40,
                           S.SCREEN_HEIGHT + 40).colliderect(self.rect):
            self.kill()


# ── Power-up ──────────────────────────────────────────────────────────────────

class PowerUp(pygame.sprite.Sprite):
    TYPES = ["pierce", "triple", "shield"]

    def __init__(self, x, y, kind=None):
        super().__init__()
        self.kind = kind or random.choice(self.TYPES)
        color = {"pierce": S.C_PU_PIERCE,
                 "triple": S.C_PU_TRIPLE,
                 "shield": S.C_PU_SHIELD}[self.kind]
        label = {"pierce": "P", "triple": "T", "shield": "E"}[self.kind]

        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pts = [(12,1),(23,12),(12,23),(1,12)]
        pygame.draw.polygon(self.image, color, pts)
        pygame.draw.polygon(self.image, S.C_BORDER, pts, 2)
        font = pygame.font.Font(None, 17)
        lbl  = font.render(label, True, (255,255,255))
        self.image.blit(lbl, lbl.get_rect(center=(12,12)))
        self.rect     = self.image.get_rect(center=(x, y))
        self.lifetime = 8 * 60

    def update(self):
        self.lifetime -= 1
        alpha = 255 if self.lifetime > 120 or (self.lifetime//10)%2==0 else 80
        self.image.set_alpha(alpha)
        if self.lifetime <= 0:
            self.kill()


# ── Jugador ───────────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.circle(surf, S.C_PLAYER,   (13, 7),  5)
        pygame.draw.rect(surf,   S.C_PLAYER,   (9, 12, 8, 11))
        pygame.draw.arc(surf,    S.C_HIGHLIGHT,
                        pygame.Rect(17, 5, 7, 14), 0, math.pi, 2)
        self.image      = surf
        self.base_image = surf.copy()
        self.rect       = self.image.get_rect(
            center=(S.SCREEN_WIDTH//2, S.SCREEN_HEIGHT//2))

        self.hp          = S.PLAYER_HP
        self.score       = 0
        self.cooldown    = 0
        self.combo       = 1
        self.combo_timer = 0
        self.pu_pierce   = 0
        self.pu_triple   = 0
        self.pu_shield   = 0
        self.dash_frames   = 0
        self.dash_cooldown = 0
        self.dash_dx       = 0.0
        self.dash_dy       = 0.0

    @property
    def shielded(self): return self.pu_shield > 0
    @property
    def dashing(self):  return self.dash_frames > 0

    def activate_powerup(self, kind):
        if   kind == "pierce": self.pu_pierce = S.PU_PIERCE_DURATION
        elif kind == "triple": self.pu_triple = S.PU_TRIPLE_DURATION
        elif kind == "shield": self.pu_shield = S.PU_SHIELD_DURATION

    def take_hit(self):
        if self.shielded or self.dashing: return
        self.hp         -= 1
        self.combo       = 1
        self.combo_timer = 0

    def try_dash(self, keys):
        if self.dash_cooldown > 0 or self.dash_frames > 0: return
        dx = dy = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx == 0 and dy == 0: dy = -1.0
        length = math.hypot(dx, dy)
        self.dash_dx     = dx / length
        self.dash_dy     = dy / length
        self.dash_frames   = S.DASH_FRAMES
        self.dash_cooldown = S.DASH_COOLDOWN

    def update(self, keys):
        if not self.dashing:
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
            if dx and dy: dx *= 0.707; dy *= 0.707
            self.rect.x += int(dx * S.PLAYER_SPEED)
            self.rect.y += int(dy * S.PLAYER_SPEED)
        else:
            self.rect.x += int(self.dash_dx * S.DASH_SPEED)
            self.rect.y += int(self.dash_dy * S.DASH_SPEED)
            self.dash_frames -= 1

        self.rect.x = max(32, min(S.SCREEN_WIDTH  - 32, self.rect.x))
        self.rect.y = max(32, min(S.SCREEN_HEIGHT - 32, self.rect.y))

        for attr in ("cooldown","pu_pierce","pu_triple","pu_shield","dash_cooldown"):
            v = getattr(self, attr)
            if v > 0: setattr(self, attr, v-1)

        self.combo_timer += 1
        if self.combo_timer >= 300 and self.combo < 4:
            self.combo += 1; self.combo_timer = 0

    def shoot(self, tx, ty, group):
        if self.cooldown > 0: return
        cx, cy = self.rect.center
        dist   = math.hypot(tx-cx, ty-cy)
        if dist == 0: return
        dx, dy = (tx-cx)/dist, (ty-cy)/dist
        pierce = self.pu_pierce > 0
        if self.pu_triple > 0:
            for off in (-15, 0, 15):
                a = math.atan2(dy, dx) + math.radians(off)
                group.add(Arrow(cx, cy, math.cos(a), math.sin(a), pierce))
        else:
            group.add(Arrow(cx, cy, dx, dy, pierce))
        self.cooldown = S.FIRE_COOLDOWN


# ── Sprites de bestias ────────────────────────────────────────────────────────

def _draw_beast(variant):
    """Niveles 1 y 2 — tamaño 28px"""
    SIZE = 28
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    if variant == 0:
        BODY=(110,55,30); DARK=(70,30,10); EYE=(220,60,60)
        pygame.draw.ellipse(surf, BODY, (4,12,20,14))
        pygame.draw.ellipse(surf, BODY, (7,4,14,13))
        pygame.draw.ellipse(surf, DARK, (9,11,8,6))
        pygame.draw.ellipse(surf, (200,100,60),(10,12,6,4))
        pygame.draw.polygon(surf, BODY, [(8,5),(5,-1),(11,4)])
        pygame.draw.polygon(surf, BODY, [(18,5),(23,-1),(17,4)])
        pygame.draw.circle(surf, EYE, (10,8), 2)
        pygame.draw.circle(surf, EYE, (17,8), 2)
        pygame.draw.circle(surf,(255,200,200),(10,7),1)
        pygame.draw.circle(surf,(255,200,200),(17,7),1)
        pygame.draw.polygon(surf,(230,220,210),[(11,15),(10,19),(13,15)])
        pygame.draw.polygon(surf,(230,220,210),[(16,15),(17,19),(14,15)])
        for px in (6,11,16,21):
            pygame.draw.rect(surf, DARK, (px,24,3,5))

    elif variant == 1:
        BODY=(80,20,20); HORN=(180,140,30); EYE=(255,200,0)
        pygame.draw.ellipse(surf, BODY, (3,11,22,16))
        pygame.draw.ellipse(surf, BODY, (6,3,16,14))
        pygame.draw.polygon(surf, HORN, [(8,4),(4,-3),(10,3)])
        pygame.draw.polygon(surf, HORN, [(20,4),(24,-3),(18,3)])
        pygame.draw.circle(surf, EYE, (10,9), 3)
        pygame.draw.circle(surf, EYE, (18,9), 3)
        pygame.draw.circle(surf,(255,255,180),(10,8),1)
        pygame.draw.circle(surf,(255,255,180),(18,8),1)
        pygame.draw.line(surf,(200,50,50),(10,14),(18,14),2)
        pygame.draw.polygon(surf,(230,220,210),[(11,14),(9,19),(13,14)])
        pygame.draw.polygon(surf,(230,220,210),[(17,14),(19,19),(15,14)])
        for px in (5,10,16,21):
            pygame.draw.rect(surf,(60,10,10),(px,25,4,5))

    else:
        BODY=(40,10,60); WING=(60,20,80); EYE=(255,80,0)
        pygame.draw.polygon(surf, WING, [(14,10),(0,2),(5,18)])
        pygame.draw.polygon(surf, WING, [(14,10),(28,2),(23,18)])
        pygame.draw.ellipse(surf, BODY, (5,9,18,16))
        pygame.draw.ellipse(surf, BODY, (7,1,14,13))
        pygame.draw.polygon(surf,(180,60,220),[(9,2),(6,-3),(11,1)])
        pygame.draw.polygon(surf,(180,60,220),[(19,2),(22,-3),(17,1)])
        pygame.draw.circle(surf, EYE, (10,7), 3)
        pygame.draw.circle(surf, EYE, (18,7), 3)
        pygame.draw.circle(surf,(255,220,100),(10,6),1)
        pygame.draw.circle(surf,(255,220,100),(18,6),1)
        pygame.draw.arc(surf,(255,80,0),pygame.Rect(9,10,10,6),math.pi,2*math.pi,2)
        for px in (6,11,16,21):
            pygame.draw.rect(surf,(30,5,50),(px,23,3,5))
            pygame.draw.line(surf,(200,100,255),(px+1,27),(px,29),1)

    return surf


def _draw_snow_beast(variant):
    """
    Criaturas de las Montañas Nevadas — tamaño 44px (más grandes).
    variant 0 = oso de las nieves
    variant 1 = trol de hielo
    variant 2 = yeti
    """
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    if variant == 0:
        # ── Oso de las nieves ────────────────────────────────────────────
        FUR   = (230, 235, 245)   # blanco azulado
        DARK  = (140, 150, 170)
        NOSE  = ( 80,  60,  80)
        EYE   = ( 20,  20,  80)

        # cuerpo grande
        pygame.draw.ellipse(surf, FUR,  (4,  18, 36, 24))
        pygame.draw.ellipse(surf, DARK, (4,  18, 36, 24), 2)
        # cabeza
        pygame.draw.ellipse(surf, FUR,  (9,  4,  26, 20))
        pygame.draw.ellipse(surf, DARK, (9,  4,  26, 20), 2)
        # orejas redondas
        pygame.draw.circle(surf, FUR,  (11, 5),  5)
        pygame.draw.circle(surf, DARK, (11, 5),  5, 1)
        pygame.draw.circle(surf, FUR,  (33, 5),  5)
        pygame.draw.circle(surf, DARK, (33, 5),  5, 1)
        pygame.draw.circle(surf, (200,180,200),(11,5),2)
        pygame.draw.circle(surf, (200,180,200),(33,5),2)
        # hocico
        pygame.draw.ellipse(surf, DARK, (15, 14, 14, 9))
        pygame.draw.circle(surf, NOSE,  (22, 16), 3)
        # ojos
        pygame.draw.circle(surf, EYE,  (15, 10), 3)
        pygame.draw.circle(surf, EYE,  (29, 10), 3)
        pygame.draw.circle(surf,(200,220,255),(15,9),1)
        pygame.draw.circle(surf,(200,220,255),(29,9),1)
        # garras
        for px in (5, 14, 26, 35):
            pygame.draw.rect(surf, DARK, (px, 40, 5, 5), border_radius=2)
            pygame.draw.line(surf, (100,110,130),(px+2,40),(px+2,44),1)

    elif variant == 1:
        # ── Trol de hielo ────────────────────────────────────────────────
        SKIN  = ( 90, 140, 180)   # azul hielo
        DARK  = ( 50,  80, 120)
        ICE   = (180, 220, 255)
        EYE   = (255, 255,  50)   # ojos amarillos

        # cuerpo robusto
        pygame.draw.rect(surf, SKIN, (6, 16, 32, 26), border_radius=6)
        pygame.draw.rect(surf, DARK, (6, 16, 32, 26), 2, border_radius=6)
        # cabeza cuadrada
        pygame.draw.rect(surf, SKIN, (8,  2, 28, 18), border_radius=4)
        pygame.draw.rect(surf, DARK, (8,  2, 28, 18), 2, border_radius=4)
        # cristales de hielo en la cabeza
        pygame.draw.polygon(surf, ICE, [(14, 2),(11,-4),(17, 2)])
        pygame.draw.polygon(surf, ICE, [(22, 2),(19,-5),(25, 2)])
        pygame.draw.polygon(surf, ICE, [(30, 2),(27,-4),(33, 2)])
        # ojos
        pygame.draw.rect(surf, EYE,  (12, 7,  6, 6), border_radius=2)
        pygame.draw.rect(surf, EYE,  (26, 7,  6, 6), border_radius=2)
        pygame.draw.rect(surf, DARK, (12, 7,  6, 6), 1, border_radius=2)
        pygame.draw.rect(surf, DARK, (26, 7,  6, 6), 1, border_radius=2)
        # boca gruñendo
        pygame.draw.line(surf, DARK, (14,17),(30,17), 2)
        for tx in (16,20,24,28):
            pygame.draw.line(surf, ICE, (tx,17),(tx-1,21), 2)
        # brazos
        pygame.draw.rect(surf, SKIN, (0, 18, 8, 16), border_radius=3)
        pygame.draw.rect(surf, SKIN, (36,18, 8, 16), border_radius=3)
        pygame.draw.rect(surf, DARK, (0, 18, 8, 16), 1, border_radius=3)
        pygame.draw.rect(surf, DARK, (36,18, 8, 16), 1, border_radius=3)
        # puños con garras de hielo
        for px in (1, 37):
            pygame.draw.polygon(surf, ICE, [(px,34),(px+2,30),(px+4,34)])
            pygame.draw.polygon(surf, ICE, [(px+3,34),(px+5,30),(px+7,34)])
        # piernas
        for px in (10, 26):
            pygame.draw.rect(surf, DARK, (px,40,8,5), border_radius=2)

    else:
        # ── Yeti ─────────────────────────────────────────────────────────
        FUR   = (245, 248, 255)   # blanco puro peludo
        SHADE = (180, 190, 210)
        EYE   = (220,  40,  40)   # ojos rojos furiosos
        CLAW  = (160, 170, 190)

        # pelaje exterior (silueta irregular)
        for ox, oy, r in [(22,22,18),(10,18,10),(34,18,10),
                          (14,30,9),(30,30,9),(22,10,12)]:
            pygame.draw.circle(surf, FUR,   (ox,oy), r)
            pygame.draw.circle(surf, SHADE, (ox,oy), r, 1)
        # cara
        pygame.draw.ellipse(surf, FUR,   (10, 6, 24, 20))
        pygame.draw.ellipse(surf, SHADE, (10, 6, 24, 20), 2)
        # ojos furiosos
        pygame.draw.circle(surf, EYE,  (16, 13), 4)
        pygame.draw.circle(surf, EYE,  (28, 13), 4)
        pygame.draw.circle(surf,(255,180,180),(16,12),2)
        pygame.draw.circle(surf,(255,180,180),(28,12),2)
        # cejas enfadadas
        pygame.draw.line(surf, SHADE, (12,9),(20,11), 2)
        pygame.draw.line(surf, SHADE, (32,9),(24,11), 2)
        # boca con colmillos
        pygame.draw.arc(surf, SHADE,
                        pygame.Rect(14,17,16,8), math.pi, 2*math.pi, 2)
        pygame.draw.polygon(surf, (240,240,255), [(17,17),(15,22),(19,17)])
        pygame.draw.polygon(surf, (240,240,255), [(27,17),(29,22),(25,17)])
        # garras inferiores
        for px in (8, 16, 24, 32):
            pygame.draw.rect(surf, CLAW, (px,38,4,7), border_radius=2)
            pygame.draw.line(surf, SHADE, (px+2,38),(px+2,44),1)

    return surf


class Enemy(pygame.sprite.Sprite):
    SPAWN_MARGIN   = 30
    _VARIANT_CYCLE = [0,0,1,1,2,0,1,2]

    def __init__(self, wave, level_cfg):
        super().__init__()
        level_num = S._current_level
        variant   = self._VARIANT_CYCLE[wave % len(self._VARIANT_CYCLE)]

        if level_num == 3:
            self.image = _draw_snow_beast(variant)
        else:
            self.image = _draw_beast(variant)

        self.rect = self.image.get_rect()

        side = random.randint(0,3)
        m    = self.SPAWN_MARGIN
        W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
        if   side==0: cx,cy = random.randint(0,W), -m
        elif side==1: cx,cy = W+m, random.randint(0,H)
        elif side==2: cx,cy = random.randint(0,W), H+m
        else:         cx,cy = -m, random.randint(0,H)
        self.rect.center = (cx,cy)

        spd_mult   = level_cfg.get("ENEMY_SPD_MULT", 1.0)
        self.hp    = S.enemy_hp_for_wave(wave)
        self.speed = (S.ENEMY_SPD_BASE + wave * 0.08) * spd_mult
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

    def update(self, target):
        cx, cy = target.rect.center
        size   = self.rect.width // 2
        ex, ey = self.float_x + size, self.float_y + size
        dist   = math.hypot(cx-ex, cy-ey)
        if dist:
            self.float_x += (cx-ex)/dist * self.speed
            self.float_y += (cy-ey)/dist * self.speed
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)