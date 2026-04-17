# src/entities.py
import pygame, math, random
import settings as S

# ── Flecha ───────────────────────────────────────────────────────────────────

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
                           S.SCREEN_WIDTH+40,
                           S.SCREEN_HEIGHT+40).colliderect(self.rect):
            self.kill()


# ── Power-up pickup ──────────────────────────────────────────────────────────

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


# ── Jugador ──────────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.circle(surf, S.C_PLAYER, (13, 7), 5)
        pygame.draw.rect(surf,   S.C_PLAYER, (9, 12, 8, 11))
        pygame.draw.arc(surf, S.C_HIGHLIGHT,
                        pygame.Rect(17, 5, 7, 14), 0, math.pi, 2)
        self.image      = surf
        self.base_image = surf.copy()
        self.rect       = self.image.get_rect(
            center=(S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2))

        self.hp        = S.PLAYER_HP
        self.score     = 0
        self.cooldown  = 0
        self.combo     = 1
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
            return          # invencible
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


# ── Enemigo ──────────────────────────────────────────────────────────────────

class Enemy(pygame.sprite.Sprite):
    SPAWN_MARGIN = 30

    def __init__(self, wave, level_cfg):
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(self.image, S.C_ENEMY, (11, 8), 6)
        pygame.draw.rect(self.image,   S.C_ENEMY, (6, 14, 10, 8))
        self.rect = self.image.get_rect()

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
        dist   = math.hypot(cx - self.float_x - 11,
                            cy - self.float_y - 11)
        if dist:
            self.float_x += (cx - self.float_x - 11) / dist * self.speed
            self.float_y += (cy - self.float_y - 11) / dist * self.speed
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)