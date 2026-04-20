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


# ── Power-up pickup ───────────────────────────────────────────────────────────

class PowerUp(pygame.sprite.Sprite):
    TYPES = ["pierce", "triple", "shield"]

    def __init__(self, x, y, kind=None):
        super().__init__()
        self.kind = kind or random.choice(self.TYPES)
        color = {
            "pierce": S.C_PU_PIERCE,
            "triple": S.C_PU_TRIPLE,
            "shield": S.C_PU_SHIELD,
        }[self.kind]
        label = {"pierce": "P", "triple": "T", "shield": "E"}[self.kind]

        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pts = [(12, 1), (23, 12), (12, 23), (1, 12)]
        pygame.draw.polygon(self.image, color, pts)
        pygame.draw.polygon(self.image, S.C_BORDER, pts, 2)
        font = pygame.font.Font(None, 17)
        lbl  = font.render(label, True, (255, 255, 255))
        self.image.blit(lbl, lbl.get_rect(center=(12, 12)))

        self.rect     = self.image.get_rect(center=(x, y))
        self.lifetime = 8 * 60

    def update(self):
        self.lifetime -= 1
        alpha = 255 if self.lifetime > 120 or (self.lifetime // 10) % 2 == 0 else 80
        self.image.set_alpha(alpha)
        if self.lifetime <= 0:
            self.kill()


# ── Jugador ───────────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((26, 26), pygame.SRCALPHA)
        # Cuerpo
        pygame.draw.circle(surf, S.C_PLAYER, (13, 7), 5)
        pygame.draw.rect(surf,   S.C_PLAYER, (9, 12, 8, 11))
        # Arco
        pygame.draw.arc(surf, S.C_HIGHLIGHT,
                        pygame.Rect(17, 5, 7, 14), 0, math.pi, 2)
        self.image      = surf
        self.base_image = surf.copy()
        self.rect       = self.image.get_rect(
            center=(S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2))

        self.hp          = S.PLAYER_HP
        self.score       = 0
        self.cooldown    = 0
        self.combo       = 1
        self.combo_timer = 0

        self.pu_pierce = 0
        self.pu_triple = 0
        self.pu_shield = 0

    def activate_powerup(self, kind):
        if kind == "pierce": self.pu_pierce = S.PU_PIERCE_DURATION
        elif kind == "triple": self.pu_triple = S.PU_TRIPLE_DURATION
        elif kind == "shield": self.pu_shield = S.PU_SHIELD_DURATION

    @property
    def shielded(self):
        return self.pu_shield > 0

    def take_hit(self):
        if self.shielded:
            return
        self.hp         -= 1
        self.combo       = 1
        self.combo_timer = 0

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx and dy:
            dx *= 0.707; dy *= 0.707

        self.rect.x = max(32, min(S.SCREEN_WIDTH  - 32,
                                  self.rect.x + int(dx * S.PLAYER_SPEED)))
        self.rect.y = max(32, min(S.SCREEN_HEIGHT - 32,
                                  self.rect.y + int(dy * S.PLAYER_SPEED)))

        for attr in ("cooldown", "pu_pierce", "pu_triple", "pu_shield"):
            v = getattr(self, attr)
            if v > 0:
                setattr(self, attr, v - 1)

        self.combo_timer += 1
        if self.combo_timer >= 300 and self.combo < 4:
            self.combo      += 1
            self.combo_timer = 0

    def shoot(self, tx, ty, group):
        if self.cooldown > 0:
            return
        cx, cy = self.rect.center
        dist   = math.hypot(tx - cx, ty - cy)
        if dist == 0:
            return
        dx, dy = (tx - cx) / dist, (ty - cy) / dist
        pierce = self.pu_pierce > 0

        if self.pu_triple > 0:
            for off in (-15, 0, 15):
                a = math.atan2(dy, dx) + math.radians(off)
                group.add(Arrow(cx, cy, math.cos(a), math.sin(a), pierce))
        else:
            group.add(Arrow(cx, cy, dx, dy, pierce))

        self.cooldown = S.FIRE_COOLDOWN


# ── Bestia enemiga ────────────────────────────────────────────────────────────

def _draw_beast(variant):
    """
    Dibuja una bestia de 28x28 px en una Surface con alpha.
    variant 0 = lobo  /  variant 1 = bestia cornuda  /  variant 2 = demonio
    """
    SIZE   = 28
    surf   = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    if variant == 0:
        # ── Lobo ──────────────────────────────────────────────
        BODY  = (110,  55,  30)   # marrón pelaje
        DARK  = ( 70,  30,  10)
        EYE   = (220,  60,  60)   # ojos rojos

        # cuerpo ovalado
        pygame.draw.ellipse(surf, BODY,  (4, 12, 20, 14))
        # cabeza
        pygame.draw.ellipse(surf, BODY,  (7,  4, 14, 13))
        # hocico
        pygame.draw.ellipse(surf, DARK,  (9, 11,  8,  6))
        pygame.draw.ellipse(surf, (200, 100, 60), (10, 12, 6, 4))
        # orejas puntiagudas
        pygame.draw.polygon(surf, BODY,  [(8, 5), (5, -1), (11, 4)])
        pygame.draw.polygon(surf, BODY,  [(18, 5), (23, -1), (17, 4)])
        # ojos
        pygame.draw.circle(surf, EYE, (10, 8), 2)
        pygame.draw.circle(surf, EYE, (17, 8), 2)
        pygame.draw.circle(surf, (255,200,200), (10, 7), 1)
        pygame.draw.circle(surf, (255,200,200), (17, 7), 1)
        # colmillos
        pygame.draw.polygon(surf, (230, 220, 210),
                            [(11, 15), (10, 19), (13, 15)])
        pygame.draw.polygon(surf, (230, 220, 210),
                            [(16, 15), (17, 19), (14, 15)])
        # patas
        for px in (6, 11, 16, 21):
            pygame.draw.rect(surf, DARK, (px, 24, 3, 5))

    elif variant == 1:
        # ── Bestia cornuda ────────────────────────────────────
        BODY  = ( 80,  20,  20)   # rojo oscuro
        HORN  = (180, 140,  30)   # cuernos dorados
        EYE   = (255, 200,   0)   # ojos amarillos

        # cuerpo
        pygame.draw.ellipse(surf, BODY, (3, 11, 22, 16))
        # cabeza
        pygame.draw.ellipse(surf, BODY, (6,  3, 16, 14))
        # cuernos
        pygame.draw.polygon(surf, HORN, [(8,  4), (4, -3), (10, 3)])
        pygame.draw.polygon(surf, HORN, [(20, 4), (24, -3), (18, 3)])
        # ojos brillantes
        pygame.draw.circle(surf, EYE, (10, 9), 3)
        pygame.draw.circle(surf, EYE, (18, 9), 3)
        pygame.draw.circle(surf, (255, 255, 180), (10, 8), 1)
        pygame.draw.circle(surf, (255, 255, 180), (18, 8), 1)
        # boca con colmillos
        pygame.draw.line(surf, (200, 50, 50), (10, 14), (18, 14), 2)
        pygame.draw.polygon(surf, (230, 220, 210),
                            [(11, 14), (9,  19), (13, 14)])
        pygame.draw.polygon(surf, (230, 220, 210),
                            [(17, 14), (19, 19), (15, 14)])
        # patas robustas
        for px in (5, 10, 16, 21):
            pygame.draw.rect(surf, (60, 10, 10), (px, 25, 4, 5))

    else:
        # ── Demonio ───────────────────────────────────────────
        BODY  = ( 40,  10,  60)   # morado oscuro
        WING  = ( 60,  20,  80)
        EYE   = (255,  80,   0)   # ojos naranja fuego

        # alas (triángulos detrás del cuerpo)
        pygame.draw.polygon(surf, WING,
                            [(14, 10), (0, 2), (5, 18)])
        pygame.draw.polygon(surf, WING,
                            [(14, 10), (28, 2), (23, 18)])
        # cuerpo
        pygame.draw.ellipse(surf, BODY, (5, 9, 18, 16))
        # cabeza
        pygame.draw.ellipse(surf, BODY, (7, 1, 14, 13))
        # cuernos pequeños
        pygame.draw.polygon(surf, (180, 60, 220), [(9, 2), (6, -3), (11, 1)])
        pygame.draw.polygon(surf, (180, 60, 220), [(19, 2), (22, -3), (17, 1)])
        # ojos de fuego
        pygame.draw.circle(surf, EYE, (10, 7), 3)
        pygame.draw.circle(surf, EYE, (18, 7), 3)
        pygame.draw.circle(surf, (255, 220, 100), (10, 6), 1)
        pygame.draw.circle(surf, (255, 220, 100), (18, 6), 1)
        # boca
        pygame.draw.arc(surf, (255, 80, 0),
                        pygame.Rect(9, 10, 10, 6), math.pi, 2*math.pi, 2)
        # garras
        for px in (6, 11, 16, 21):
            pygame.draw.rect(surf, (30, 5, 50), (px, 23, 3, 5))
            pygame.draw.line(surf, (200, 100, 255),
                             (px+1, 27), (px, 29), 1)

    return surf


class Enemy(pygame.sprite.Sprite):
    SPAWN_MARGIN = 30
    # Qué variante de bestia aparece según la oleada
    _VARIANT_CYCLE = [0, 0, 1, 1, 2, 0, 1, 2]

    def __init__(self, wave, level_cfg):
        super().__init__()
        variant    = self._VARIANT_CYCLE[wave % len(self._VARIANT_CYCLE)]
        self.image = _draw_beast(variant)
        self.rect  = self.image.get_rect()

        # Spawn en los bordes
        side = random.randint(0, 3)
        m    = self.SPAWN_MARGIN
        W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
        if side == 0:   cx, cy = random.randint(0, W), -m
        elif side == 1: cx, cy = W + m, random.randint(0, H)
        elif side == 2: cx, cy = random.randint(0, W), H + m
        else:           cx, cy = -m, random.randint(0, H)
        self.rect.center = (cx, cy)

        bonus_hp  = level_cfg.get("ENEMY_HP_BONUS", 0)
        spd_mult  = level_cfg.get("ENEMY_SPD_MULT", 1.0)
        self.hp   = S.ENEMY_HP_BASE + wave + bonus_hp
        self.speed = (S.ENEMY_SPD_BASE + wave * 0.12) * spd_mult
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

    def update(self, target):
        cx, cy = target.rect.center
        ex, ey = self.float_x + 14, self.float_y + 14
        dist   = math.hypot(cx - ex, cy - ey)
        if dist:
            self.float_x += (cx - ex) / dist * self.speed
            self.float_y += (cy - ey) / dist * self.speed
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)