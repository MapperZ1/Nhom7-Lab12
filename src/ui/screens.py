"""
Screens for Robo-Logic: Boss Battle.
100% English UI without academic course mentions.
"""

import os
import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_WORLD_BG, COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_GREEN, COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_PURPLE, COLOR_ACCENT_YELLOW, COLOR_ACCENT_RED, COLOR_ACCENT_CYAN,
    get_ui_font, get_code_font, get_resource_path
)
from src.ui.components import Button
from src.audio import audio


class MainMenuScreen:
    def __init__(self, on_boss, on_docs, on_toggle_sound, on_quit):
        self.on_boss = on_boss
        self.on_docs = on_docs
        self.on_toggle_sound = on_toggle_sound
        self.on_quit = on_quit

        self.font_logo = get_ui_font(38, bold=True)
        self.font_subtitle = get_ui_font(14, bold=True)
        self.font_tagline = get_ui_font(13)
        self.font_btn_main = get_ui_font(14, bold=True)
        self.font_btn = get_ui_font(13, bold=True)
        self.font_footer = get_ui_font(12)

        cx = SCREEN_WIDTH // 2
        btn_w = 400
        start_y = 280
        gap = 12

        self.btn_boss = Button(
            (cx - btn_w // 2, start_y, btn_w, 46),
            "ENTER BOSS BATTLE ARENA", COLOR_ACCENT_GREEN,
            font=self.font_btn_main, on_click=self.on_boss
        )
        self.btn_docs = Button(
            (cx - btn_w // 2, start_y + 46 + gap, btn_w, 42),
            "GUIDE & DOCUMENTATION", COLOR_ACCENT_BLUE,
            font=self.font_btn, on_click=self.on_docs
        )
        self.btn_sound = Button(
            (cx - btn_w // 2, start_y + 46 + gap + 42 + gap, btn_w, 42),
            "SOUND: ON", (40, 48, 62),
            font=self.font_btn, on_click=self._toggle_audio
        )
        self.btn_quit = Button(
            (cx - btn_w // 2, start_y + 46 + gap + 2 * (42 + gap), btn_w, 42),
            "QUIT GAME", (55, 35, 40),
            font=self.font_btn, on_click=self.on_quit
        )

        self.buttons = [
            self.btn_boss, self.btn_docs, self.btn_sound, self.btn_quit
        ]

        # Load Main Character pixel-art robot sprite
        self.hero_sprite = None
        robot_path = get_resource_path(os.path.join("assets", "player_robot.png"))
        if os.path.isfile(robot_path):
            try:
                raw_bot = pygame.image.load(robot_path).convert_alpha()
                self.hero_sprite = pygame.transform.scale(raw_bot, (86, 110))
            except Exception as e:
                print(f"[MainMenuScreen] Could not load player_robot.png: {e}")

    def _toggle_audio(self):
        is_on = self.on_toggle_sound()
        self.btn_sound.text = "SOUND: ON" if is_on else "SOUND: OFF"

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface, time_ms):
        surface.fill(COLOR_WORLD_BG)

        offset = int((time_ms * 0.02) % 40)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(surface, (20, 26, 36), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(surface, (20, 26, 36), (0, (y + offset) % SCREEN_HEIGHT), (SCREEN_WIDTH, (y + offset) % SCREEN_HEIGHT))

        cx = SCREEN_WIDTH // 2
        bob = math.sin(time_ms * 0.004) * 7
        bot_x = cx
        bot_y = 104 + bob

        # Shadow
        shadow_surf = pygame.Surface((84, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 90), (0, 0, 84, 24))
        surface.blit(shadow_surf, (bot_x - 42, 148))

        if self.hero_sprite is not None:
            rect = self.hero_sprite.get_rect(center=(bot_x, int(bot_y)))
            surface.blit(self.hero_sprite, rect)
        else:
            # Fallback vector robot
            pygame.draw.circle(surface, (235, 242, 255), (bot_x, int(bot_y)), 22)
            pygame.draw.circle(surface, (40, 50, 70), (bot_x, int(bot_y)), 22, 2)

        # Titles
        title_surf = self.font_logo.render("ROBO-LOGIC: BOSS BATTLE", True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surf, title_surf.get_rect(center=(cx, 192)))

        sub_surf = self.font_subtitle.render("CODING ARENA & BOSS CHALLENGE - GROUP 7", True, COLOR_ACCENT_CYAN)
        surface.blit(sub_surf, sub_surf.get_rect(center=(cx, 228)))

        tag_surf = self.font_tagline.render("Write Python 3 or C++ 17 Solutions Externally & Import to Battle Bosses", True, COLOR_TEXT_SECONDARY)
        surface.blit(tag_surf, tag_surf.get_rect(center=(cx, 254)))

        for btn in self.buttons:
            btn.draw(surface)

        footer_text = "Project by Group 7 | Support Python 3 & C++ 17 File Import | 6 Boss Stages"
        foot_surf = self.font_footer.render(footer_text, True, COLOR_TEXT_MUTED)
        surface.blit(foot_surf, foot_surf.get_rect(center=(cx, SCREEN_HEIGHT - 22)))


class TutorialDocsScreen:
    """
    Documentation & Guide Screen in English.
    """
    def __init__(self, on_back):
        self.on_back = on_back
        self.active_tab = 0

        self.font_tab = get_ui_font(12, bold=True)
        self.font_h1 = get_ui_font(16, bold=True)
        self.font_h2 = get_ui_font(15, bold=True)
        self.font_body = get_ui_font(14)
        self.font_code = get_code_font(14)

        self.tabs = [
            "1. Overview",
            "2. 6 Arena Bosses",
            "3. Combat Rules",
            "4. File Import & Judge"
        ]

        self.btn_back = Button(
            (28, 18, 96, 36), "Back", (45, 52, 68),
            font=self.font_tab, on_click=self.on_back
        )

        self.tab_buttons = []
        tab_start_x = 140
        tab_w = 240
        tab_h = 36
        for i, tab_name in enumerate(self.tabs):
            bx = tab_start_x + i * (tab_w + 10)
            btn = Button(
                (bx, 18, tab_w, tab_h), tab_name, (35, 42, 56),
                font=self.font_tab,
                on_click=lambda idx=i: self._set_tab(idx)
            )
            self.tab_buttons.append(btn)

        self.scroll_y = 0

    def _set_tab(self, idx):
        self.active_tab = idx
        self.scroll_y = 0
        audio.play_click()

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return True

        for btn in self.tab_buttons:
            if btn.handle_event(event):
                return True

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(-350, min(0, self.scroll_y + event.y * 30))
            return True

        return False

    def draw(self, surface, time_ms):
        surface.fill(COLOR_BG)

        top_bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
        pygame.draw.rect(surface, (20, 24, 34), top_bar_rect)
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (0, 70), (SCREEN_WIDTH, 70), 2)

        self.btn_back.draw(surface)

        for i, btn in enumerate(self.tab_buttons):
            btn.bg_color = COLOR_ACCENT_BLUE if self.active_tab == i else (35, 42, 56)
            btn.draw(surface)

        content_rect = pygame.Rect(32, 86, SCREEN_WIDTH - 64, SCREEN_HEIGHT - 106)
        pygame.draw.rect(surface, (25, 30, 42), content_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, content_rect, 1, border_radius=10)

        content_surf = pygame.Surface((content_rect.width - 24, content_rect.height - 24))
        content_surf.fill((25, 30, 42))

        if self.active_tab == 0:
            self._draw_tab_overview(content_surf)
        elif self.active_tab == 1:
            self._draw_tab_bosses(content_surf)
        elif self.active_tab == 2:
            self._draw_tab_combat(content_surf)
        elif self.active_tab == 3:
            self._draw_tab_import(content_surf)

        surface.blit(content_surf, (content_rect.x + 12, content_rect.y + 12))

    def _draw_tab_overview(self, surf):
        y = 12 + self.scroll_y

        title = self.font_h1.render("OVERVIEW: ROBO-LOGIC BOSS BATTLE ARENA", True, COLOR_ACCENT_CYAN)
        surf.blit(title, (20, y))
        y += 32

        paragraphs = [
            ("1. Core Gameplay Concept:", COLOR_ACCENT_YELLOW),
            ("- Robo-Logic: Boss Battle is a competitive coding RPG where you battle 6 unique Bosses by solving coding problems.", COLOR_TEXT_PRIMARY),
            ("- Write your solution in Python 3 (.py) or C++ 17 (.cpp) using your favorite external IDE (VS Code, PyCharm, Dev-C++, etc.).", COLOR_TEXT_PRIMARY),
            ("- Import your solution file directly into the game to run sample tests and defeat the Boss!", COLOR_TEXT_PRIMARY),
            ("", None),
            ("2. Two-Tab Contest Layout (1200 x 720):", COLOR_ACCENT_YELLOW),
            ("- Tab 1 (F1 - Problem & Arena): Clean white reading sheet (font size 14) with Vietnamese contest problem statements and sample tests.", COLOR_TEXT_PRIMARY),
            ("- Tab 2 (F2 - Import & Judge): Browse or drag & drop .py/.cpp files, inspect read-only preview, run samples (F6), and submit (F5).", COLOR_TEXT_PRIMARY),
            ("", None),
            ("3. Victory Objective:", COLOR_ACCENT_YELLOW),
            ("- Pass all hidden test cases on your 1st submission to trigger a 1-SHOT KILL (-1000 HP)!", COLOR_ACCENT_GREEN)
        ]

        for text, col in paragraphs:
            if not text:
                y += 10
                continue
            if text.startswith(("1.", "2.", "3.")):
                h_surf = self.font_h2.render(text, True, col if col else COLOR_TEXT_PRIMARY)
                surf.blit(h_surf, (20, y))
                y += 26
            else:
                b_surf = self.font_body.render(text, True, col if col else COLOR_TEXT_PRIMARY)
                surf.blit(b_surf, (20, y))
                y += 22

    def _draw_tab_bosses(self, surf):
        y = 12 + self.scroll_y

        title = self.font_h1.render("6 ARENA BOSS STAGES", True, COLOR_ACCENT_GREEN)
        surf.blit(title, (20, y))
        y += 28

        bosses = [
            ("Stage 1: TWOSUM (Slime)", COLOR_ACCENT_CYAN, [
                "  - Task: Find two distinct indices i, j such that nums[i] + nums[j] == target.",
                "  - Target: def solve(nums, target) -> [i, j] or Standard I/O (stdin/stdout)."
            ]),
            ("Stage 2: BRACKETS (Golem)", COLOR_ACCENT_ORANGE, [
                "  - Task: Validate balanced parentheses string containing (), [], {}.",
                "  - Target: def solve(s) -> bool or print YES/NO."
            ]),
            ("Stage 3: HEAPK (Serpent)", COLOR_ACCENT_CYAN, [
                "  - Task: Find the K-th largest element in an unsorted integer array.",
                "  - Target: def solve(nums, k) -> int or Standard I/O."
            ]),
            ("Stage 4: WOODCUT (Fire Dragon)", COLOR_ACCENT_RED, [
                "  - Task: Find the maximum sawblade height H to harvest at least M meters of wood.",
                "  - Target: def solve(trees, m) -> int or Standard I/O."
            ]),
            ("Stage 5: MAZE (Phantom)", COLOR_ACCENT_PURPLE, [
                "  - Task: Find minimum steps from (0, 0) to (R-1, C-1) in a grid maze.",
                "  - Target: def solve(grid) -> int or Standard I/O."
            ]),
            ("Stage 6: KNAPSACK (Professor Einstein - Final Boss)", COLOR_ACCENT_YELLOW, [
                "  - Task: Maximize total item value without exceeding bag capacity C.",
                "  - Target: def solve(weights, values, capacity) -> int or Standard I/O."
            ])
        ]

        for b_name, col, lines in bosses:
            surf.blit(self.font_h2.render(b_name, True, col), (20, y))
            y += 24
            for line in lines:
                surf.blit(self.font_body.render(line, True, COLOR_TEXT_PRIMARY), (24, y))
                y += 20
            y += 8

    def _draw_tab_combat(self, surf):
        y = 12 + self.scroll_y

        title = self.font_h1.render("RPG BOSS COMBAT & DAMAGE RULES", True, COLOR_ACCENT_YELLOW)
        surf.blit(title, (20, y))
        y += 28

        sections = [
            ("1. One-Shot Critical Kill (-1000 HP):", COLOR_ACCENT_YELLOW, [
                "- When your submission gets Accepted (AC) on the 1st attempt:",
                "- Your Knight unleashes a critical strike dealing 1000 DAMAGE!",
                "- Boss HP drops straight to 0, earning the [1-SHOT] victory badge."
            ]),
            ("2. Half-HP Slash (-500 HP):", COLOR_ACCENT_ORANGE, [
                "- When your submission gets Accepted (AC) on the 2nd attempt:",
                "- Deals 500 DAMAGE (exactly 50% of Boss Max HP)!"
            ]),
            ("3. Subsequent Attempts:", COLOR_ACCENT_GREEN, [
                "- From the 3rd attempt onward, each AC deals 500 damage to finish off the Boss."
            ]),
            ("4. Boss Counter-Attack on Failure (WA / TLE / RE):", COLOR_ACCENT_RED, [
                "- Wrong Answer (WA): Output does not match expected answer.",
                "- Time Limit Exceeded (TLE): Execution exceeds time limit (>2.0s).",
                "- Runtime / Compilation Error (RE): Syntax or runtime crash.",
                "- Every failed submission triggers a Boss counter-attack (-200 HP to your Knight)!"
            ])
        ]

        for heading, col, lines in sections:
            surf.blit(self.font_h2.render(heading, True, col), (20, y))
            y += 24
            for line in lines:
                surf.blit(self.font_body.render(line, True, COLOR_TEXT_PRIMARY), (32, y))
                y += 21
            y += 10

    def _draw_tab_import(self, surf):
        y = 12 + self.scroll_y

        title = self.font_h1.render("FILE IMPORT & JUDGE GUIDE (.PY / .CPP)", True, COLOR_ACCENT_CYAN)
        surf.blit(title, (20, y))
        y += 28

        sections = [
            ("1. How to Import Your Solution File:", COLOR_ACCENT_YELLOW, [
                "- Step 1: Write your code in Python (.py) or C++ 17 (.cpp) using VS Code, PyCharm, Dev-C++, etc.",
                "- Step 2: Switch to Tab 2 (F2) and click [Browse File (.py/.cpp) [F3]] to select your file.",
                "- Pro Tip: You can also DRAG & DROP any .py or .cpp file directly onto the game window!"
            ]),
            ("2. Supported Code Formats:", COLOR_ACCENT_GREEN, [
                "- C++ (.cpp): Standard int main() reading from cin and printing to cout (compiled with g++ -std=c++17).",
                "- Python (.py): Supports BOTH function style def solve(...) AND standard script input()/print()."
            ]),
            ("3. Global Hotkeys:", COLOR_ACCENT_CYAN, [
                "- F1 / F2: Switch between Tab 1 (Problem & Arena) and Tab 2 (Import & Judge).",
                "- F3: Open file picker dialog.",
                "- F4: Reload file from disk after saving edits (Ctrl+S) in your external editor.",
                "- F6 (or Ctrl+R): Run sample tests safely (no Boss counter damage).",
                "- F5 (or Ctrl+O): Submit file against hidden tests to attack Boss!"
            ])
        ]

        for heading, col, lines in sections:
            surf.blit(self.font_h2.render(heading, True, col), (20, y))
            y += 24
            for line in lines:
                surf.blit(self.font_body.render(line, True, COLOR_TEXT_PRIMARY), (32, y))
                y += 22
            y += 10
