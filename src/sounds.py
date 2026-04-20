# src/sounds.py
import pygame
import os

_sounds = {}

def load_sounds():
    files = {
        "shoot":     "assets/sounds/shoot.ogg",
        "enemy_die": "assets/sounds/enemy_die.ogg",
        "powerup":   "assets/sounds/powerup.ogg",
    }
    for name, path in files.items():
        if not os.path.exists(path):
            print(f"[Audio] FALTA: {path}")
            continue
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(1.0)
            _sounds[name] = snd
            print(f"[Audio] OK: {path}")
        except Exception as e:
            print(f"[Audio] Error {path}: {e}")


def play(name):
    if name in _sounds:
        _sounds[name].play()


def set_sfx_volume(vol):
    """Ajusta el volumen de todos los efectos de sonido. vol entre 0.0 y 1.0"""
    import settings as S
    S.VOL_SFX = vol
    for snd in _sounds.values():
        snd.set_volume(vol)