# settings.py

# Pantalla
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 640
FPS           = 60
TITLE         = "Arrowheads"

# ── Niveles ──────────────────────────────────────────────────────────────────
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
        "ENEMY_HP_BONUS": 0,
        "HAS_WALLS":      False,
    },
    2: {
        "name":           "El Bosque Oscuro",
        "wave_start":     6,
        "wave_end":       999,
        "C_BG":           ( 45,  65,  40),
        "C_BORDER":       ( 20,  35,  20),
        "C_GRID":         ( 55,  78,  50),
        "C_ACCENT":       ( 90, 160,  70),
        "TERRAIN":        "forest",
        "ENEMY_SPD_MULT": 1.1,    # antes 1.3 → más justo
        "ENEMY_HP_BONUS": 1,
        "HAS_WALLS":      True,   # activa la cruz de muros
    },
}

LEVEL_TRANSITION_WAVE = 5

# Paleta base (se sobreescribe en runtime)
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

# Power-up colores
C_PU_PIERCE = ( 70, 130, 180)
C_PU_TRIPLE = (180,  80, 180)
C_PU_SHIELD = (220, 190,  40)

# Jugador
PLAYER_SPEED  = 3
PLAYER_HP     = 5
ARROW_SPEED   = 9
FIRE_COOLDOWN = 18

# Power-ups (10 segundos)
PU_PIERCE_DURATION = 10 * 60
PU_TRIPLE_DURATION = 10 * 60
PU_SHIELD_DURATION = 10 * 60
PU_DROP_CHANCE     = 0.28

# Oleadas
WAVE_PAUSE     = 180
ENEMY_HP_BASE  = 2
ENEMY_SPD_BASE = 1.4

# Volúmenes (modificables desde el menú de pausa)
VOL_MUSIC  = 1.0
VOL_SFX    = 1.0

# Variable de nivel actual (se escribe en runtime desde game.py)
_current_level = 1