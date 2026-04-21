# src/wave_manager.py
import settings as S
from src.entities import Enemy


class WaveManager:
    def __init__(self):
        self.wave         = 0
        self.pause_timer  = 0
        self.level_timer  = 0   # cuenta regresiva de pausa entre niveles
        self.in_level_pause = False
        self.spawning     = False
        self.spawn_queue  = []
        self.spawn_timer  = 0
        self.level        = 1
        self.level_cfg    = S.LEVELS[1]

    def _get_level_for_wave(self, wave_num):
        for lvl, cfg in S.LEVELS.items():
            if cfg["wave_start"] <= wave_num <= cfg["wave_end"]:
                return lvl, cfg
        last = max(S.LEVELS.keys())
        return last, S.LEVELS[last]

    def start_wave(self, wave_num, group):
        self.wave      = wave_num
        new_lvl, cfg   = self._get_level_for_wave(wave_num)
        level_changed  = new_lvl != self.level
        self.level     = new_lvl
        self.level_cfg = cfg

        count            = S.enemy_count_for_wave(wave_num)
        self.spawn_queue = [Enemy(wave_num, cfg) for _ in range(count)]
        self.spawning    = True
        self.spawn_timer = 0
        return level_changed

    def update(self, group, player):
        """
        Devuelve (wave_done, level_changed, in_level_pause).
        in_level_pause = True mientras se está mostrando la cuenta regresiva
        entre niveles (10s).
        """
        # ── Pausa entre niveles (10s) ─────────────────────────────────
        if self.in_level_pause:
            self.level_timer -= 1
            if self.level_timer <= 0:
                self.in_level_pause = False
                self.start_wave(self.wave, group)
            return False, False, True

        # ── Spawn ─────────────────────────────────────────────────────
        if self.spawning:
            self.spawn_timer += 1
            if self.spawn_timer % 28 == 0 and self.spawn_queue:
                group.add(self.spawn_queue.pop(0))
            if not self.spawn_queue:
                self.spawning = False

        for e in group:
            e.update(player)

        # ── Fin de oleada ─────────────────────────────────────────────
        if not self.spawning and len(group) == 0:
            self.pause_timer += 1
            wave_pause = self.level_cfg.get("WAVE_PAUSE", 300)

            if self.pause_timer >= wave_pause:
                self.pause_timer = 0
                next_wave        = self.wave + 1
                new_lvl, cfg     = self._get_level_for_wave(next_wave)
                level_changed    = new_lvl != self.level

                if level_changed:
                    # Guarda la oleada pendiente y activa pausa de nivel
                    self.wave         = next_wave
                    self.level        = new_lvl
                    self.level_cfg    = cfg
                    self.level_timer  = cfg.get("LEVEL_PAUSE", 600)
                    self.in_level_pause = True
                    return True, True, False
                else:
                    changed = self.start_wave(next_wave, group)
                    return True, changed, False

        return False, False, False