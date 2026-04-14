# src/entities.py
import pygame, math
from settings import *

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = pygame.Surface((14, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, C_ARROW, (0, 1, 12, 2))
        pygame.draw.polygon(self.image, C_ARROW,
                            [(10, 0), (14, 2), (10, 4)])
        angle = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect  = self.image.get_rect(center=(x, y))
        self.dx, self.dy = dx, dy

    def update(self):
        self.rect.x += self.dx * ARROW_SPEED
        self.rect.y += self.dy * ARROW_SPEED
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Silueta de cazador (círculo cabeza + cuerpo)
        pygame.draw.circle(self.image, C_PLAYER, (12, 7), 5)
        pygame.draw.rect(self.image,   C_PLAYER, (8, 12, 8, 10))
        # arco
        pygame.draw.arc(self.image, C_HIGHLIGHT,
                        pygame.Rect(16, 6, 6, 12), 0, math.pi, 2)
        self.rect   = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.hp     = PLAYER_HP
        self.score  = 0
        self.cooldown = 0

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx and dy:
            dx *= 0.707; dy *= 0.707
        self.rect.x = max(32, min(SCREEN_WIDTH  - 32, self.rect.x + dx * PLAYER_SPEED))
        self.rect.y = max(32, min(SCREEN_HEIGHT - 32, self.rect.y + dy * PLAYER_SPEED))
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self, target_x, target_y, group):
        if self.cooldown > 0:
            return
        cx, cy = self.rect.center
        dist = math.hypot(target_x - cx, target_y - cy)
        if dist == 0:
            return
        dx = (target_x - cx) / dist
        dy = (target_y - cy) / dist
        group.add(Arrow(cx, cy, dx, dy))
        self.cooldown = FIRE_COOLDOWN


class Enemy(pygame.sprite.Sprite):
    SPAWN_POINTS = [
        (0, 0), (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH, 0),
        (0, SCREEN_HEIGHT//2),         (SCREEN_WIDTH, SCREEN_HEIGHT//2),
        (0, SCREEN_HEIGHT), (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT),
    ]

    def __init__(self, wave):
        super().__init__()
        import random
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, C_ENEMY, (10, 8), 5)
        pygame.draw.rect(self.image,   C_ENEMY, (6, 13, 8, 7))
        self.rect  = self.image.get_rect()
        sx, sy     = random.choice(self.SPAWN_POINTS)
        self.rect.center = (
            sx + random.randint(-20, 20),
            sy + random.randint(-20, 20)
        )
        self.hp    = ENEMY_HP_BASE + wave
        self.speed = ENEMY_SPD_BASE + wave * 0.15
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

    def update(self, target):
        cx, cy = target.rect.center
        dist   = math.hypot(cx - self.float_x - 10, cy - self.float_y - 10)
        if dist:
            self.float_x += (cx - self.float_x - 10) / dist * self.speed
            self.float_y += (cy - self.float_y - 10) / dist * self.speed
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)