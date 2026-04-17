# src/wave_manager.py
import random
from src.entities import Enemy
import settings as S

class WaveManager:
    def __init__(self):
        self.wave        = 0
        self.pause_timer = 0
        self.spawning    = False
        self.spawn_queue = []
        self.spawn_timer = 0
        self.level       = 1
        self.level_cfg   = S.LEVELS[1]

    def _get_level_for_wave(self, wave_num):
        for lvl, cfg in S.LEVELS.items():
            if cfg["wave_start"] <= wave_num <= cfg["wave_end"]:
                return lvl, cfg
        return max(S.LEVELS.keys()), S.LEVELS[max(S.LEVELS.keys())]

    def start_wave(self, wave_num, group):
        self.wave      = wave_num
        new_lvl, cfg   = self._get_level_for_wave(wave_num)
        level_changed  = new_lvl != self.level
        self.level     = new_lvl
        self.level_cfg = cfg

        count            = 4 + wave_num * 2
        self.spawn_queue = [Enemy(wave_num, cfg) for _ in range(count)]
        self.spawning    = True
        self.spawn_timer = 0
        return level_changed

    def update(self, group, player):
        if self.spawning:
            self.spawn_timer += 1
            if self.spawn_timer % 28 == 0 and self.spawn_queue:
                group.add(self.spawn_queue.pop(0))
            if not self.spawn_queue:
                self.spawning = False

        for e in group:
            e.update(player)

        if not self.spawning and len(group) == 0:
            self.pause_timer += 1
            if self.pause_timer >= S.WAVE_PAUSE:
                self.pause_timer = 0
                changed = self.start_wave(self.wave + 1, group)
                return True, changed
        return False, False