# src/wave_manager.py
import random
from src.entities import Enemy
from settings import WAVE_PAUSE

class WaveManager:
    def __init__(self):
        self.wave       = 0
        self.enemies    = []
        self.pause_timer = 0
        self.spawning   = False
        self.spawn_queue = []
        self.spawn_timer = 0

    def start_wave(self, wave_num, group):
        self.wave = wave_num
        count     = 4 + wave_num * 2
        self.spawn_queue = [Enemy(wave_num) for _ in range(count)]
        self.spawning    = True
        self.spawn_timer = 0

    def update(self, group, player):
        if self.spawning:
            self.spawn_timer += 1
            if self.spawn_timer % 30 == 0 and self.spawn_queue:
                e = self.spawn_queue.pop(0)
                group.add(e)
            if not self.spawn_queue:
                self.spawning = False

        for e in group:
            e.update(player)

        # Si todos los enemigos murieron → pausa → nueva oleada
        if not self.spawning and len(group) == 0:
            self.pause_timer += 1
            if self.pause_timer >= WAVE_PAUSE:
                self.pause_timer = 0
                self.start_wave(self.wave + 1, group)
                return True   # nueva oleada iniciada
        return False