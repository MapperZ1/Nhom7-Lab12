"""
Procedural sound manager for Robo-Logic.
Synthesizes retro-modern digital sound effects directly into memory.
Requires no external audio asset files.
"""

import math
import struct
import pygame


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._init_mixer()
        if pygame.mixer.get_init():
            self._generate_all_sounds()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
        except Exception as e:
            print(f"[SoundManager] Mixer init failed: {e}")

    def toggle_mute(self):
        self.enabled = not self.enabled
        return self.enabled

    def _synthesize(self, generator_func, duration=0.15, volume=0.5):
        sample_rate = 44100
        total_samples = int(sample_rate * duration)
        raw = bytearray()

        for i in range(total_samples):
            t = float(i) / sample_rate
            progress = float(i) / total_samples

            if progress < 0.05:
                env = progress / 0.05
            elif progress > 0.8:
                env = (1.0 - progress) / 0.2
            else:
                env = 1.0

            sample_val = generator_func(t, progress)
            clamped = max(-1.0, min(1.0, sample_val * env * volume))
            int_val = int(clamped * 32767.0)
            raw.extend(struct.pack('<hh', int_val, int_val))

        try:
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception as e:
            print(f"[SoundManager] Failed creating sound: {e}")
            return None

    def _generate_all_sounds(self):
        def click_gen(t, p):
            freq = 900.0 - (p * 400.0)
            return math.sin(2.0 * math.pi * freq * t)
        self.sounds["click"] = self._synthesize(click_gen, duration=0.04, volume=0.35)

        def move_gen(t, p):
            freq = 240.0 + (p * 100.0)
            wave1 = math.sin(2.0 * math.pi * freq * t)
            wave2 = 0.3 * (1.0 if (int(t * freq * 2) % 2 == 0) else -1.0)
            return (wave1 + wave2) * 0.7
        self.sounds["move"] = self._synthesize(move_gen, duration=0.10, volume=0.35)

        def switch_gen(t, p):
            f = 350.0 if p < 0.5 else 550.0
            return (1.0 if (int(t * f) % 2 == 0) else -1.0) * 0.5
        self.sounds["switch"] = self._synthesize(switch_gen, duration=0.12, volume=0.4)

        def error_gen(t, p):
            f = 140.0
            buzz = 1.0 if (int(t * f) % 2 == 0) else -1.0
            mod = 1.0 if (int(t * 30.0) % 2 == 0) else 0.2
            return buzz * mod
        self.sounds["error"] = self._synthesize(error_gen, duration=0.30, volume=0.5)

        def win_gen(t, p):
            if p < 0.22:
                f = 523.25
            elif p < 0.44:
                f = 659.25
            elif p < 0.66:
                f = 783.99
            else:
                f = 1046.50
            return 0.7 * math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t)
        self.sounds["win"] = self._synthesize(win_gen, duration=0.65, volume=0.6)

    def play(self, name):
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def play_click(self):
        self.play("click")

    def play_win(self):
        self.play("win")

    def play_error(self):
        self.play("error")

    def play_switch(self):
        self.play("switch")

    def play_step(self):
        self.play("move")


audio = SoundManager()
