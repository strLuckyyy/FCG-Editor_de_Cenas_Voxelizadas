import os
import pygame
from typing import Any, cast

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SOUNDS_PATH = os.path.join(PROJECT_ROOT, "sounds")

class SoundManager:#   audio quality, bits, stereo, buffer size
    def __init__(self, freq=44100, size=-16, channels=2, buffer=512):
        pygame.mixer.init(frequency=freq, size=size, channels=channels, buffer=buffer)
        self.default_volume = 0.5
        self.music_volume = 1.0
        self.sounds = {}

    def _full_path(self, file_path: str) -> str:
        return os.path.join(SOUNDS_PATH, file_path)

    # ------------------- Sound Effect Management ------------------- #

    def load_sound(self, name: str, file_path: str):
        """Loads a sound effect and stores it by name."""
        if name in self.sounds:
            return self.sounds[name]

        path = self._full_path(file_path)

        if not os.path.exists(path):
            print(f"[SoundManager] ERRO: Arquivo não encontrado: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(cast(Any, path))
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"[SoundManager] Falha ao carregar '{file_path}': {e}")
            return None

    def play_sound(self, name: str, volume=None):
        sound = self.sounds.get(name)
        if sound is None:
            print(f"[SoundManager] Som '{name}' não carregado!")
            return

        volume = volume if volume is not None else self.default_volume
        sound.set_volume(volume)
        sound.play()

    # ------------------- Music Management ------------------- #

    def play_music(self, file_path: str, volume=1.0, loop=True):
        path = self._full_path(file_path)

        if not os.path.exists(path):
            print(f"[SoundManager] Música não encontrada: {path}")
            return

        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        
    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, vol: float):
        pygame.mixer.music.set_volume(vol)