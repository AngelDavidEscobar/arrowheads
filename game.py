# game.py
import pygame, sys
from settings import *
from src.entities   import Player
from src.wave_manager import WaveManager

def run_game(screen, clock):
    try:
        font = pygame.font.Font(None, 30)
    except:
        font = pygame.font.SysFont("serif", 28)

    player   = Player()
    player_g = pygame.sprite.GroupSingle(player)
    enemies  = pygame.sprite.Group()
    arrows   = pygame.sprite.Group()
    wm       = WaveManager()
    wm.start_wave(1, enemies)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot(*event.pos, arrows)

        keys = pygame.key.get_pressed()
        player.update(keys)
        arrows.update()
        wm.update(enemies, player)

        # Colisiones: flechas vs enemigos
        hits = pygame.sprite.groupcollide(enemies, arrows, False, True)
        for enemy, _ in hits.items():
            enemy.hp -= 1
            if enemy.hp <= 0:
                player.score += 10
                enemy.kill()

        # Colisiones: enemigos vs jugador
        if pygame.sprite.spritecollide(player, enemies, False):
            player.hp -= 1
            if player.hp <= 0:
                return player.score   # game over

        # Dibujo
        screen.fill(C_BG)

        # Rejilla de suelo (efecto de tierra)
        for x in range(0, SCREEN_WIDTH, 32):
            pygame.draw.line(screen, C_UI_BG, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(screen, C_UI_BG, (0, y), (SCREEN_WIDTH, y), 1)

        # Borde
        pygame.draw.rect(screen, C_BORDER, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 16)

        enemies.draw(screen)
        arrows.draw(screen)
        player_g.draw(screen)

        # HUD
        hp_txt = font.render(f"❤ {player.hp}   Oleada {wm.wave}   Pts {player.score}", True, C_UI_TEXT)
        screen.blit(hp_txt, (20, 12))

        if wm.pause_timer > 0:
            msg = font.render(f"Oleada {wm.wave + 1} en {(WAVE_PAUSE - wm.pause_timer)//60 + 1}s...", True, C_HIGHLIGHT)
            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

        pygame.display.flip()
        clock.tick(FPS)