# settings.py

SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 640
FPS           = 60
TITLE         = "Arrowheads"

LEVELS = {
    1: {
        "name":           "Las Llanuras",
        "wave_start":     1,
        "wave_end":       5,
        "C_BG":           (210, 180, 140),
        "C_BORDER":       ( 90,  60,  30),
        "C_GRID":         (180, 150, 110),
        "C_ACCENT":       (200, 140,  50),
        "TERRAIN":        "plains",
        "ENEMY_SPD_MULT": 1.0,
        "HAS_WALLS":      False,
        "WAVE_PAUSE":     300,   # 5 segundos entre oleadas
        "LEVEL_PAUSE":    0,     # sin pausa de nivel (es el primero)
    },
    2: {
        "name":           "El Bosque Oscuro",
        "wave_start":     6,
        "wave_end":       10,
        "C_BG":           ( 45,  65,  40),
        "C_BORDER":       ( 20,  35,  20),
        "C_GRID":         ( 55,  78,  50),
        "C_ACCENT":       ( 90, 160,  70),
        "TERRAIN":        "forest",
        "ENEMY_SPD_MULT": 0.8,
        "HAS_WALLS":      True,
        "WAVE_PAUSE":     300,
        "LEVEL_PAUSE":    600,   # 10 segundos al entrar al nivel
    },
    3: {
        "name":           "Montañas Nevadas",
        "wave_start":     11,
        "wave_end":       999,
        "C_BG":           (220, 230, 240),
        "C_BORDER":       ( 80,  90, 110),
        "C_GRID":         (200, 210, 225),
        "C_ACCENT":       (140, 180, 220),
        "TERRAIN":        "snow",
        "ENEMY_SPD_MULT": 1,
        "HAS_WALLS":      True,
        "WALL_TYPE":      "rocks",
        "WAVE_PAUSE":     300,
        "LEVEL_PAUSE":    600,
    },
}

LEVEL_TRANSITION_WAVE = 5

# Paleta base
C_BG        = (210, 180, 140)
C_BORDER    = ( 90,  60,  30)
C_GRID      = (180, 150, 110)
C_ACCENT    = (200, 140,  50)
C_PLAYER    = ( 60,  40,  20)
C_ENEMY     = (139,  28,  28)
C_ARROW     = ( 80,  50,  20)
C_UI_TEXT   = (230, 220, 200)
C_UI_BG     = (100,  80,  60)
C_HIGHLIGHT = (200, 140,  50)

C_PU_PIERCE = ( 70, 130, 180)
C_PU_TRIPLE = (180,  80, 180)
C_PU_SHIELD = (220, 190,  40)

PLAYER_SPEED  = 3
PLAYER_HP     = 5
ARROW_SPEED   = 9
FIRE_COOLDOWN = 18

DASH_SPEED    = 18
DASH_FRAMES   = 8
DASH_COOLDOWN = 90

PU_PIERCE_DURATION = 10 * 60
PU_TRIPLE_DURATION = 10 * 60
PU_SHIELD_DURATION = 10 * 60
PU_DROP_CHANCE     = 0.28

ENEMY_SPD_BASE = 1.4

def enemy_hp_for_wave(wave):
    if wave <= 3:  return 1
    if wave <= 7:  return 2
    if wave <= 10: return 3
    return 6   # nivel 3 — aguantan 6 golpes

def enemy_count_for_wave(wave):
    if wave <= 10:
        return 4 + wave * 2
    # Nivel 3: muchos menos enemigos pero más resistentes
    return 3 + (wave - 10) * 1

VOL_MUSIC = 1.0
VOL_SFX   = 1.0
_current_level = 1