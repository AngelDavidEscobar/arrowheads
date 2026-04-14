# settings.py
import pygame

# Pantalla
SCREEN_WIDTH  = 512
SCREEN_HEIGHT = 512
FPS           = 60
TITLE         = "Arrowheads"

# Paleta sepia / medieval
C_BG         = (210, 180, 140)   # arena
C_BORDER     = ( 90,  60,  30)   # marrón oscuro
C_PLAYER     = ( 60,  40,  20)   # silueta cazador
C_ENEMY      = (139,  28,  28)   # rojo sangre apagado
C_ARROW      = ( 80,  50,  20)   # madera
C_UI_TEXT    = ( 50,  30,  10)
C_UI_BG      = (180, 150, 110)
C_HIGHLIGHT  = (200, 140,  50)

# Jugador
PLAYER_SPEED  = 3
PLAYER_HP     = 5
ARROW_SPEED   = 8
FIRE_COOLDOWN = 20   # frames entre disparos

# Oleadas
WAVE_PAUSE    = 180  # frames de pausa entre oleadas
ENEMY_HP_BASE = 2
ENEMY_SPD_BASE = 1.5