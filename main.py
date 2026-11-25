"""
Main Entry Point for Robo-Logic: Boss Battle - Group 7.
Coding Boss Battle Arena featuring:
- 6 Boss Battles with Vietnamese Contest Problem Statements & Sample Tests.
- File Import System (.py & .cpp) with drag-and-drop, external reload, and white-theme font size 14 UI.
- RPG Combat: One-Shot Kill on 1st-try AC (-1000 HP), Half-HP Cut on 2nd-try AC (-500 HP), Boss Counter-Attack on WA/TLE/RE (-200 HP).
"""

import sys
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_WORLD_BG,
    get_ui_font, get_code_font
)
from src.audio import audio
from src.save_manager import save_manager
from src.ui.screens import MainMenuScreen, TutorialDocsScreen
from src.ui.boss_screen import BossBattleScreen


class RoboLogicGame:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(280, 25)
        pygame.display.set_caption("Robo-Logic: Boss Battle - Group 7")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Global Screen State: "MENU", "DSA_BOSS", "TUTORIAL_DOCS"
        self.screen_state = "MENU"

        # Screens
        self.menu_screen = MainMenuScreen(
            on_boss=self._start_boss_battle,
            on_docs=self._open_docs,
            on_toggle_sound=self._toggle_sound,
            on_quit=self._quit_game
        )
        self.docs_screen = TutorialDocsScreen(on_back=self._back_to_menu)
        self.boss_screen = BossBattleScreen(on_back_to_menu=self._back_to_menu)

    def _start_boss_battle(self):
        self.screen_state = "DSA_BOSS"
        self.boss_screen.switch_stage(self.boss_screen.current_stage)
        audio.play_click()

    def _open_docs(self):
        self.screen_state = "TUTORIAL_DOCS"
        audio.play_click()

    def _back_to_menu(self):
        self.screen_state = "MENU"
        audio.play_click()

    def _toggle_sound(self):
        return audio.toggle_mute()

    def _quit_game(self):
        self.running = False

    def run(self):
        while self.running:
            time_ms = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if self.screen_state == "MENU":
                    self.menu_screen.handle_event(event)
                elif self.screen_state == "TUTORIAL_DOCS":
                    self.docs_screen.handle_event(event)
                elif self.screen_state == "DSA_BOSS":
                    self.boss_screen.handle_event(event)

            if self.screen_state == "MENU":
                self.menu_screen.draw(self.screen, time_ms)
            elif self.screen_state == "TUTORIAL_DOCS":
                self.docs_screen.draw(self.screen, time_ms)
            elif self.screen_state == "DSA_BOSS":
                self.boss_screen.render(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    game = RoboLogicGame()
    game.run()
