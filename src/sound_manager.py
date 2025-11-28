import os
import pygame

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SOUNDS_PATH = os.path.join(PROJECT_ROOT, "sounds")

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 1.0

    def load_sound(self, name: str, file_path: str):
        """Carrega um efeito sonoro."""
        path = os.path.join(SOUNDS_PATH, file_path)
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound

    def play_sound(self, name: str, volume=1.0):
        """Toca um efeito sonoro carregado."""
        if name in self.sounds:
            snd = self.sounds[name]
            snd.set_volume(volume)
            snd.play()
        else:
            print(f"[SoundManager] Som '{name}' não encontrado!")

    def play_music(self, file_path: str, volume=1.0, loop=True):
        """Toca música de fundo."""
        path = os.path.join(SOUNDS_PATH, file_path)
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, vol: float):
        pygame.mixer.music.set_volume(vol)
