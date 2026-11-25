"""
BossBattleScreen - White-Theme Boss Battle Arena with File Import.
Features:
- Pure White background (#FFFFFF) and font size 14 throughout for high readability.
- 6 Boss Stages with Vietnamese Contest Problem Statements & Sample Tests.
- File Import System (Browse dialog via tkinter + Drag & Drop via pygame.DROPFILE + Reload):
  * Supports both Python 3 (.py) and C++ 17 (.cpp/.cc/.cxx).
  * Read-only code preview with line numbers and scroll support.
- Dual-Tab layout:
  * Tab 1 (F1): Boss Arena & Vietnamese Problem Statement + Sample Tests.
  * Tab 2 (F2): Import File, Code Preview, Sample Test Run & Boss Combat Submission Console.
"""

import os
import math
import random
import pygame
from typing import Callable, Dict, Any, List, Optional, Tuple

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, get_ui_font, get_code_font, get_resource_path
from src.dsa_problems import DSA_BOSS_PROBLEMS, get_boss_problem
from src.dsa_judge import dsa_judge, DSAVerdict, DSASubmissionReport
from src.ui.terminal import BashTestTerminal
from src.ui.components import Button
from src.save_manager import save_manager
from src.audio import audio


# Light / White Contest Theme Palette (High Contrast)
LIGHT_BG = (255, 255, 255)
LIGHT_HEADER_BG = (241, 245, 249)
LIGHT_CARD_BG = (255, 255, 255)
LIGHT_ARENA_BG = (248, 250, 252)
LIGHT_BORDER = (203, 213, 225)
LIGHT_TEXT_PRIMARY = (15, 23, 42)
LIGHT_TEXT_SECONDARY = (51, 65, 85)
LIGHT_TEXT_MUTED = (100, 116, 139)

LIGHT_BLUE = (29, 78, 216)
LIGHT_GREEN = (21, 128, 61)
LIGHT_ORANGE = (194, 65, 12)
LIGHT_RED = (185, 28, 28)
LIGHT_CYAN = (14, 116, 144)
LIGHT_PURPLE = (109, 40, 217)
LIGHT_GOLD = (161, 98, 7)


class FloatingCombatText:
    def __init__(self, text: str, x: int, y: int, color: tuple, size: int = 16, is_big: bool = False):
        self.text = text
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.font = get_ui_font(size, bold=True)
        self.alpha = 255.0
        self.vy = -1.3 if not is_big else -1.6
        self.life = 75
        self.is_big = is_big

    def update(self) -> bool:
        self.y += self.vy
        self.life -= 1
        if self.life < 30:
            self.alpha = max(0.0, self.alpha - 8.5)
        return self.life > 0

    def render(self, surface: pygame.Surface):
        if self.alpha <= 0:
            return
        surf = self.font.render(self.text, True, self.color)
        if self.alpha < 255:
            surf.set_alpha(int(self.alpha))
        shadow = self.font.render(self.text, True, (226, 232, 240))
        if self.alpha < 255:
            shadow.set_alpha(int(self.alpha * 0.8))
        surface.blit(shadow, (int(self.x) + 1, int(self.y) + 1))
        surface.blit(surf, (int(self.x), int(self.y)))


class BossBattleScreen:
    def __init__(self, on_back_to_menu: Callable[[], None]):
        self.on_back_to_menu = on_back_to_menu

        # Active Main Tab: "PROBLEM" or "IMPORT"
        self.active_tab = "PROBLEM"

        # Imported file state per stage:
        # {stage_num: {"path": str, "filename": str, "code": str, "language": "python"|"cpp"}}
        self.imported_files: Dict[int, Optional[Dict[str, str]]] = {i: None for i in range(1, 7)}

        # Current Boss & Stage
        self.current_stage = 1
        self.boss_data = get_boss_problem(self.current_stage)

        # Health & Combat State
        self.boss_max_hp = 1000
        self.boss_target_hp = 1000
        self.boss_display_hp = 1000.0

        self.player_max_hp = 1000
        self.player_target_hp = 1000
        self.player_display_hp = 1000.0

        # Attempt counters per stage
        self.attempts: Dict[int, int] = {i: 0 for i in range(1, 7)}

        # Floating combat particles & visual feedback
        self.floating_texts: List[FloatingCombatText] = []
        self.shake_frames = 0
        self.flash_alpha = 0

        # Sub-tab inside Problem Tab: "DESC" or "SAMPLES"
        self.problem_sub_tab = "DESC"
        self.last_report: Optional[DSASubmissionReport] = None

        # Scroll offsets
        self.problem_scroll_y = 0
        self.preview_scroll_row = 0

        # Fonts (Font size 14 for easy reading as requested)
        self.font_nav = get_ui_font(13, bold=True)
        self.font_stage_tab = get_ui_font(12, bold=True)
        self.font_boss_title = get_ui_font(19, bold=True)
        self.font_h2 = get_ui_font(15, bold=True)
        self.font_hp = get_ui_font(14, bold=True)
        self.font_body = get_ui_font(14)
        self.font_body_bold = get_ui_font(14, bold=True)
        self.font_code_mono = get_code_font(14)
        self.font_btn_action = get_ui_font(13, bold=True)

        # -------------------------------------------------------------
        # TOP NAVIGATION BAR CONTROLS (y=0..46)
        # -------------------------------------------------------------
        self.btn_tab_problem = Button(
            (10, 7, 210, 32),
            "1. PROBLEM & ARENA (F1)", LIGHT_BLUE, text_color=(255, 255, 255),
            font=self.font_nav, on_click=lambda: self.switch_main_tab("PROBLEM")
        )
        self.btn_tab_import = Button(
            (226, 7, 240, 32),
            "2. IMPORT & JUDGE (F2)", (226, 232, 240), text_color=LIGHT_TEXT_PRIMARY,
            font=self.font_nav, on_click=lambda: self.switch_main_tab("IMPORT")
        )

        # Stage Navigation Buttons (Stage 1 -> Stage 6)
        self.stage_buttons: List[Button] = []
        stg_w = 100
        start_stg_x = 478
        for i in range(1, 7):
            b = Button(
                (start_stg_x + (i - 1) * (stg_w + 6), 7, stg_w, 32),
                f"Stage {i}",
                LIGHT_BLUE if i == self.current_stage else (226, 232, 240),
                text_color=(255, 255, 255) if i == self.current_stage else LIGHT_TEXT_PRIMARY,
                font=self.font_stage_tab,
                on_click=lambda s=i: self.switch_stage(s)
            )
            self.stage_buttons.append(b)

        self.btn_back = Button(
            (SCREEN_WIDTH - 88, 7, 78, 32),
            "Menu", (226, 232, 240), text_color=LIGHT_RED,
            font=self.font_nav, on_click=self.on_back_to_menu
        )

        # -------------------------------------------------------------
        # TAB 1 (PROBLEM) CONTROLS
        # -------------------------------------------------------------
        self.btn_sub_desc = Button(
            (22, 258, 215, 32),
            "PROBLEM STATEMENT", LIGHT_BLUE, text_color=(255, 255, 255),
            font=self.font_nav, on_click=lambda: self._set_problem_sub_tab("DESC")
        )
        self.btn_sub_samples = Button(
            (245, 258, 245, 32),
            "SAMPLE TESTS", (226, 232, 240), text_color=LIGHT_TEXT_PRIMARY,
            font=self.font_nav, on_click=lambda: self._set_problem_sub_tab("SAMPLES")
        )
        self.btn_reset_battle = Button(
            (1056, 66, 120, 32),
            "Reset Battle", (226, 232, 240), text_color=LIGHT_TEXT_PRIMARY,
            font=self.font_nav, on_click=self.reset_current_battle
        )
        self.btn_go_to_import = Button(
            (SCREEN_WIDTH - 365, 258, 342, 32),
            "GO TO FILE IMPORT & JUDGE -> (F2)", LIGHT_GREEN, text_color=(255, 255, 255),
            font=self.font_nav, on_click=lambda: self.switch_main_tab("IMPORT")
        )

        # -------------------------------------------------------------
        # TAB 2 (FILE IMPORT & RUNNER) CONTROLS
        # -------------------------------------------------------------
        self.btn_browse_file = Button(
            (24, 122, 225, 34),
            "Browse File (.py/.cpp) [F3]", LIGHT_BLUE, text_color=(255, 255, 255),
            font=self.font_btn_action, on_click=self.open_file_dialog
        )
        self.btn_reload_file = Button(
            (257, 122, 150, 34),
            "Reload File [F4]", (226, 232, 240), text_color=LIGHT_TEXT_PRIMARY,
            font=self.font_btn_action, on_click=self.reload_imported_file
        )
        self.btn_run_sample_top = Button(
            (415, 122, 185, 34),
            "Run Sample [F6]", LIGHT_CYAN, text_color=(255, 255, 255),
            font=self.font_btn_action, on_click=self.run_sample_test
        )
        self.btn_submit_top = Button(
            (608, 122, 225, 34),
            "Submit - Attack Boss [F5]", LIGHT_GREEN, text_color=(255, 255, 255),
            font=self.font_btn_action, on_click=self.submit_solution
        )
        self.btn_reset_tab2 = Button(
            (841, 122, 125, 34),
            "Reset Battle", (226, 232, 240), text_color=LIGHT_TEXT_PRIMARY,
            font=self.font_btn_action, on_click=self.reset_current_battle
        )

        # Bottom Runner Console (Light / White Theme, Size 14)
        term_rect = (10, 442, SCREEN_WIDTH - 20, 268)
        self.terminal = BashTestTerminal(
            term_rect,
            on_run_sample=self.run_sample_test,
            on_submit=self.submit_solution,
            hostname="arena",
            username="player",
            theme="light"
        )

        # Load Main Character robot sprite & Final Boss custom portrait (Einstein)
        self.player_sprite: Optional[pygame.Surface] = None
        self.boss_portraits: Dict[str, pygame.Surface] = {}
        self._load_boss_portraits()

        self._update_stage_button_labels()

    def _load_boss_portraits(self):
        """Loads main robot sprite and custom boss portrait images from assets/ folder."""
        # 1. Main Character Pixel Robot
        robot_path = get_resource_path(os.path.join("assets", "player_robot.png"))
        if os.path.isfile(robot_path):
            try:
                raw_bot = pygame.image.load(robot_path).convert_alpha()
                self.player_sprite = pygame.transform.scale(raw_bot, (94, 120))
            except Exception as e:
                print(f"[BossBattleScreen] Could not load player_robot.png: {e}")

        # 2. Final Boss Portrait (Einstein)
        final_boss_path = get_resource_path(os.path.join("assets", "boss_final.jpg"))
        if os.path.isfile(final_boss_path):
            try:
                raw_img = pygame.image.load(final_boss_path)
                w, h = raw_img.get_size()
                crop_y = int(h * 0.12)
                crop_h = int(h * 0.76)
                cropped = raw_img.subsurface(pygame.Rect(0, crop_y, w, crop_h))
                scaled = pygame.transform.smoothscale(cropped, (98, 132))
                self.boss_portraits["einstein"] = scaled
            except Exception as e:
                print(f"[BossBattleScreen] Could not load boss portrait: {e}")

    def switch_main_tab(self, tab: str):
        """Switches between 'PROBLEM' and 'IMPORT' tabs."""
        self.active_tab = tab
        if tab == "PROBLEM":
            self.btn_tab_problem.bg_color = LIGHT_BLUE
            self.btn_tab_problem.text_color = (255, 255, 255)
            self.btn_tab_import.bg_color = (226, 232, 240)
            self.btn_tab_import.text_color = LIGHT_TEXT_PRIMARY
        else:
            self.btn_tab_import.bg_color = LIGHT_BLUE
            self.btn_tab_import.text_color = (255, 255, 255)
            self.btn_tab_problem.bg_color = (226, 232, 240)
            self.btn_tab_problem.text_color = LIGHT_TEXT_PRIMARY
        audio.play_click()

    def _set_problem_sub_tab(self, sub: str):
        self.problem_sub_tab = sub
        self.problem_scroll_y = 0
        if sub == "DESC":
            self.btn_sub_desc.bg_color = LIGHT_BLUE
            self.btn_sub_desc.text_color = (255, 255, 255)
            self.btn_sub_samples.bg_color = (226, 232, 240)
            self.btn_sub_samples.text_color = LIGHT_TEXT_PRIMARY
        else:
            self.btn_sub_samples.bg_color = LIGHT_BLUE
            self.btn_sub_samples.text_color = (255, 255, 255)
            self.btn_sub_desc.bg_color = (226, 232, 240)
            self.btn_sub_desc.text_color = LIGHT_TEXT_PRIMARY
        audio.play_click()

    def switch_stage(self, stage: int):
        """Switches to a different boss stage."""
        self.current_stage = stage
        self.boss_data = get_boss_problem(stage)
        self.boss_max_hp = self.boss_data["max_hp"]
        self.boss_target_hp = self.boss_max_hp
        self.boss_display_hp = float(self.boss_max_hp)

        self.player_max_hp = 1000
        self.player_target_hp = 1000
        self.player_display_hp = 1000.0

        self.floating_texts.clear()
        self.last_report = None
        self.problem_scroll_y = 0
        self.preview_scroll_row = 0
        self._set_problem_sub_tab("DESC")

        # Terminal announce
        self.terminal.log_separator()
        self.terminal.log_info(f">>> SWITCHED TO STAGE {stage}: {self.boss_data.get('problem_code', '')} — {self.boss_data['boss_name']} <<<")
        imp = self.imported_files.get(stage)
        if imp:
            self.terminal.log_info(f"Loaded file: {imp['filename']} ({imp['language'].upper()})")
        else:
            self.terminal.log_info(f"No solution file loaded yet. Import a .py or .cpp file for Stage {stage}.")
        self.terminal.log_separator()

        self._update_stage_button_labels()
        audio.play_click()

    def _update_stage_button_labels(self):
        for i, b in enumerate(self.stage_buttons, 1):
            is_slain = save_manager.is_boss_slain(i)
            is_one_shot = save_manager.is_boss_one_shot(i)
            tag = " [1-SHOT]" if is_one_shot else (" [V]" if is_slain else "")
            b.text = f"Stage {i}{tag}"
            if i == self.current_stage:
                b.bg_color = LIGHT_BLUE
                b.text_color = (255, 255, 255)
            elif is_slain:
                b.bg_color = (220, 252, 231)
                b.text_color = LIGHT_GREEN
            else:
                b.bg_color = (226, 232, 240)
                b.text_color = LIGHT_TEXT_PRIMARY

    def reset_current_battle(self):
        """Restores full HP for boss and player to retry fight."""
        self.boss_target_hp = self.boss_max_hp
        self.boss_display_hp = float(self.boss_max_hp)
        self.player_target_hp = self.player_max_hp
        self.player_display_hp = float(self.player_max_hp)
        self.floating_texts.clear()
        self.shake_frames = 0
        self.flash_alpha = 0
        self.terminal.log_info(f"[RESET] Restored 1000 HP for both Boss and Knight on Stage {self.current_stage}.")
        audio.play_click()

    # -----------------------------------------------------------------
    # FILE IMPORT LOGIC
    # -----------------------------------------------------------------
    def open_file_dialog(self):
        """Opens native OS file picker to select a .py or .cpp solution file."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            try:
                root.attributes("-topmost", True)
            except Exception:
                pass
            file_path = filedialog.askopenfilename(
                title=f"Select solution file for Stage {self.current_stage} (.py or .cpp)",
                filetypes=[
                    ("Solution Files (Python / C++)", "*.py *.cpp *.cc *.cxx"),
                    ("Python Script (*.py)", "*.py"),
                    ("C++ Source (*.cpp, *.cc)", "*.cpp *.cc *.cxx"),
                    ("All Files", "*.*")
                ]
            )
            root.destroy()
            pygame.event.clear()
            if file_path:
                self.import_solution_file(file_path)
        except Exception as e:
            self.terminal.log_fail(f"[FILE DIALOG ERROR]: {e}")
            audio.play_error()

    def import_solution_file(self, file_path: str) -> bool:
        """Reads an external .py or .cpp file and attaches it to the current stage."""
        if not file_path or not os.path.isfile(file_path):
            self.terminal.log_fail(f"[IMPORT ERROR]: File not found '{file_path}'.")
            audio.play_error()
            return False

        ext = os.path.splitext(file_path)[1].lower()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                code_content = f.read()
        except Exception as e:
            self.terminal.log_fail(f"[FILE READ ERROR]: {e}")
            audio.play_error()
            return False

        if ext in (".cpp", ".cc", ".cxx", ".c++"):
            lang = "cpp"
        elif ext == ".py":
            lang = "python"
        else:
            lang = "cpp" if ("#include" in code_content or "int main" in code_content) else "python"

        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(abs_path)
        self.imported_files[self.current_stage] = {
            "path": abs_path,
            "filename": filename,
            "code": code_content,
            "language": lang
        }
        self.preview_scroll_row = 0

        lang_label = "C++ 17" if lang == "cpp" else "Python 3"
        line_count = len(code_content.splitlines())
        self.terminal.log_separator()
        self.terminal.log_pass(f"[IMPORT SUCCESS] File: {filename} | Language: {lang_label} | {line_count} lines")
        self.terminal.log_info(f"Path: {abs_path}")
        self.terminal.log_info("Click [Run Sample (F6)] to test safely or [Submit - Attack Boss (F5)].")
        audio.play_switch()
        return True

    def reload_imported_file(self):
        """Re-reads the imported file from disk (useful when editing externally)."""
        imp = self.imported_files.get(self.current_stage)
        if not imp:
            self.terminal.log_fail("[INFO]: No file loaded yet to reload. Please browse a file first!")
            audio.play_error()
            return
        self.import_solution_file(imp["path"])

    def _get_current_imported(self) -> Optional[Dict[str, str]]:
        return self.imported_files.get(self.current_stage)

    # -----------------------------------------------------------------
    # TEST RUN & BOSS COMBAT SUBMISSION
    # -----------------------------------------------------------------
    def run_sample_test(self):
        """Executes imported file against sample test cases without boss counter-attack."""
        imp = self._get_current_imported()
        if not imp:
            self.terminal.log_fail("[NO FILE]: Please browse or drag & drop a .py / .cpp file first!")
            audio.play_error()
            return

        code = imp["code"]
        lang = imp["language"]
        fname = imp["filename"]
        cmd = f"g++ -O2 -std=c++17 {fname} && ./a.out --sample" if lang == "cpp" else f"python3 {fname} --sample"
        self.terminal.log_command(cmd)
        self.terminal.log_info(f"=== RUNNING SAMPLE TESTS [{lang.upper()}] — Stage {self.current_stage}: {self.boss_data.get('problem_code', '')} ===")

        report = dsa_judge.evaluate(code, self.boss_data, attempt_count=self.attempts[self.current_stage], is_sample_run=True, language=lang)
        self.last_report = report

        for tr in report.test_results:
            if tr.verdict == DSAVerdict.AC:
                self.terminal.log_pass(f"  [PASS] Sample {tr.test_idx}: Output matched ({tr.elapsed_ms:.1f}ms)")
            else:
                self.terminal.log_fail(f"  [FAIL] Sample {tr.test_idx}: {tr.verdict.value} ({tr.elapsed_ms:.1f}ms)")
                if tr.error_msg:
                    self.terminal.log_fail(f"         Error: {tr.error_msg}")
                else:
                    self.terminal.log_fail(f"         Input:    {tr.input_data}")
                    self.terminal.log_fail(f"         Output:   {tr.actual}")
                    self.terminal.log_fail(f"         Expected: {tr.expected}")

        if report.verdict == DSAVerdict.AC:
            audio.play_switch()
            self.terminal.log_pass(f">>> PASSED {report.passed_count}/{report.total_count} SAMPLE TESTS! Ready to click [Submit - Attack Boss (F5)]. <<<")
        else:
            audio.play_error()
            self.terminal.log_fail(f">>> SAMPLE TEST FAILED [{report.verdict.value}]. Fix your file and click [Reload File (F4)]. <<<")

    def submit_solution(self):
        """Submits imported file against hidden test cases to deal combat damage to Boss."""
        if self.boss_target_hp <= 0:
            self.terminal.log_info("This Boss is already defeated! Switch stages or click [Reset Battle].")
            return

        imp = self._get_current_imported()
        if not imp:
            self.terminal.log_fail("[NO FILE]: Please browse or drag & drop a .py / .cpp file before submitting!")
            audio.play_error()
            return

        code = imp["code"]
        lang = imp["language"]
        fname = imp["filename"]
        self.attempts[self.current_stage] += 1
        current_attempt = self.attempts[self.current_stage]

        cmd = f"g++ -O2 -std=c++17 {fname} && ./a.out --judge" if lang == "cpp" else f"python3 {fname} --judge"
        self.terminal.log_command(f"{cmd} (Attempt {current_attempt})")
        self.terminal.log_info(f"Judging '{fname}' [{lang.upper()}] against hidden test suite...")

        report = dsa_judge.evaluate(code, self.boss_data, attempt_count=current_attempt, is_sample_run=False, language=lang)
        self.last_report = report

        for tr in report.test_results:
            if tr.verdict == DSAVerdict.AC:
                self.terminal.log_pass(f"  [PASS] Hidden Test {tr.test_idx}: OK ({tr.elapsed_ms:.1f}ms)")
            else:
                self.terminal.log_fail(f"  [FAIL] Hidden Test {tr.test_idx}: {tr.verdict.value} ({tr.elapsed_ms:.1f}ms)")
                if tr.error_msg:
                    self.terminal.log_fail(f"         Error: {tr.error_msg}")
                else:
                    self.terminal.log_fail(f"         Output: {tr.actual} | Expected: {tr.expected}")

        # Combat damage handling
        if report.damage_to_boss > 0:
            self.boss_target_hp = max(0, self.boss_target_hp - report.damage_to_boss)

            if report.is_one_shot:
                self.shake_frames = 20
                self.flash_alpha = 150
                audio.play_win()
                self.floating_texts.append(FloatingCombatText("-1000 ONE-SHOT CRITICAL!", 790, 95, LIGHT_GOLD, size=20, is_big=True))
                self.floating_texts.append(FloatingCombatText("CRITICAL FINISH!", 815, 128, LIGHT_ORANGE, size=15))
                self.terminal.log_combat(">>> ONE-SHOT KILL! 1st-try AC (-1000 HP)! <<<", is_one_shot=True)
                self.terminal.log_combat(f">>> STAGE {self.current_stage} BOSS DEFEATED! <<<", is_one_shot=True)
                save_manager.record_boss_defeat(self.current_stage, is_one_shot=True, attempts=current_attempt)

            elif report.is_half_hp:
                self.shake_frames = 12
                audio.play_step()
                self.floating_texts.append(FloatingCombatText("-500 HALF-HP SLASH!", 790, 100, LIGHT_ORANGE, size=16, is_big=True))
                self.terminal.log_combat(">>> HALF-HP SLASH! 2nd-try AC (-500 HP Boss)! <<<")
                self.terminal.log_combat(f"Boss HP remaining: {self.boss_target_hp}/{self.boss_max_hp}")
                if self.boss_target_hp <= 0:
                    audio.play_win()
                    save_manager.record_boss_defeat(self.current_stage, is_one_shot=False, attempts=current_attempt)

            else:
                self.shake_frames = 8
                audio.play_step()
                self.floating_texts.append(FloatingCombatText(f"-{report.damage_to_boss} DAMAGE!", 805, 105, LIGHT_GREEN, size=15))
                self.terminal.log_combat(f"Hit dealt {report.damage_to_boss} damage! Boss HP: {self.boss_target_hp}/{self.boss_max_hp}")
                if self.boss_target_hp <= 0:
                    audio.play_win()
                    save_manager.record_boss_defeat(self.current_stage, is_one_shot=False, attempts=current_attempt)

            self._update_stage_button_labels()

        if report.damage_to_player > 0:
            self.player_target_hp = max(0, self.player_target_hp - report.damage_to_player)
            self.shake_frames = 10
            audio.play_error()
            self.floating_texts.append(FloatingCombatText(f"-{report.damage_to_player} BOSS COUNTER!", 600, 120, LIGHT_RED, size=15))
            self.terminal.log_fail(f">>> BOSS COUNTER-ATTACK! Boss dealt -{report.damage_to_player} HP to Knight! <<<")
            self.terminal.log_fail(f"Knight HP remaining: {self.player_target_hp}/{self.player_max_hp} HP")

    # -----------------------------------------------------------------
    # EVENT HANDLING
    # -----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        # Drag & drop support for .py / .cpp files anywhere in window
        if event.type == pygame.DROPFILE:
            if self.import_solution_file(event.file):
                self.switch_main_tab("IMPORT")
            return

        # Top Global Navigation Bar
        if self.btn_tab_problem.handle_event(event):
            return
        if self.btn_tab_import.handle_event(event):
            return
        if self.btn_back.handle_event(event):
            return

        for b in self.stage_buttons:
            if b.handle_event(event):
                return

        # Global Hotkeys
        if event.type == pygame.KEYDOWN:
            ctrl_pressed = (event.mod & pygame.KMOD_CTRL) or (event.mod & pygame.KMOD_META)
            if event.key == pygame.K_F1:
                self.switch_main_tab("PROBLEM")
                return
            elif event.key == pygame.K_F2:
                self.switch_main_tab("IMPORT")
                return
            elif event.key == pygame.K_F3:
                self.switch_main_tab("IMPORT")
                self.open_file_dialog()
                return
            elif event.key == pygame.K_F4:
                self.reload_imported_file()
                return
            elif event.key == pygame.K_F5 or (ctrl_pressed and event.key == pygame.K_o):
                self.submit_solution()
                return
            elif event.key == pygame.K_F6 or (ctrl_pressed and event.key == pygame.K_r):
                self.run_sample_test()
                return
            elif event.key == pygame.K_ESCAPE:
                self.on_back_to_menu()
                return

        # Tab-specific events
        if self.active_tab == "PROBLEM":
            if self.btn_sub_desc.handle_event(event):
                return
            if self.btn_sub_samples.handle_event(event):
                return
            if self.btn_reset_battle.handle_event(event):
                return
            if self.btn_go_to_import.handle_event(event):
                return

            # Mouse wheel scroll on problem description area
            if event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] >= 250:
                if event.button == 4:
                    self.problem_scroll_y = min(0, self.problem_scroll_y + 26)
                    return
                elif event.button == 5:
                    self.problem_scroll_y = max(-450, self.problem_scroll_y - 26)
                    return
            elif event.type == pygame.MOUSEWHEEL:
                self.problem_scroll_y = max(-450, min(0, self.problem_scroll_y + event.y * 26))
                return

        elif self.active_tab == "IMPORT":
            if self.btn_browse_file.handle_event(event):
                return
            if self.btn_reload_file.handle_event(event):
                return
            if self.btn_run_sample_top.handle_event(event):
                return
            if self.btn_submit_top.handle_event(event):
                return
            if self.btn_reset_tab2.handle_event(event):
                return
            if self.terminal.handle_event(event):
                return

            # Scroll code preview box (y: 178..434)
            preview_rect = pygame.Rect(10, 178, SCREEN_WIDTH - 20, 256)
            if event.type == pygame.MOUSEBUTTONDOWN and preview_rect.collidepoint(event.pos):
                imp = self._get_current_imported()
                total_lines = len(imp["code"].splitlines()) if imp else 0
                if event.button == 4:
                    self.preview_scroll_row = max(0, self.preview_scroll_row - 3)
                    return
                elif event.button == 5:
                    max_scr = max(0, total_lines - 10)
                    self.preview_scroll_row = min(max_scr, self.preview_scroll_row + 3)
                    return

    def update(self):
        if abs(self.boss_display_hp - self.boss_target_hp) > 0.5:
            self.boss_display_hp += (self.boss_target_hp - self.boss_display_hp) * 0.12
        else:
            self.boss_display_hp = float(self.boss_target_hp)

        if abs(self.player_display_hp - self.player_target_hp) > 0.5:
            self.player_display_hp += (self.player_target_hp - self.player_display_hp) * 0.12
        else:
            self.player_display_hp = float(self.player_target_hp)

        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        if self.shake_frames > 0:
            self.shake_frames -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 10)

    # -----------------------------------------------------------------
    # RENDERING (WHITE THEME, FONT SIZE 14)
    # -----------------------------------------------------------------
    def render(self, surface: pygame.Surface):
        self.update()

        shake_ox = random.randint(-4, 4) if self.shake_frames > 0 else 0
        shake_oy = random.randint(-4, 4) if self.shake_frames > 0 else 0

        # Pure White Contest Background
        surface.fill(LIGHT_BG)

        # 1. TOP NAVIGATION BAR
        top_bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 46)
        pygame.draw.rect(surface, LIGHT_HEADER_BG, top_bar_rect)
        pygame.draw.line(surface, LIGHT_BORDER, (0, 46), (SCREEN_WIDTH, 46), 1)

        self.btn_tab_problem.draw(surface)
        self.btn_tab_import.draw(surface)
        for b in self.stage_buttons:
            b.draw(surface)
        self.btn_back.draw(surface)

        # 2. ACTIVE TAB
        if self.active_tab == "PROBLEM":
            self._render_tab_problem(surface, shake_ox, shake_oy)
        else:
            self._render_tab_import(surface, shake_ox, shake_oy)

        # 3. Flash overlay on One-Shot Critical
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((254, 240, 138, int(self.flash_alpha)))
            surface.blit(flash_surf, (0, 0))

    def _render_tab_problem(self, surface: pygame.Surface, shake_ox: int, shake_oy: int):
        """Tab 1: Boss Arena (top) & Scrollable White Problem Sheet at Font Size 14 (bottom)."""
        # 1. Upper Arena Card (10, 54, 1180, 188)
        arena_rect = pygame.Rect(10 + shake_ox, 54 + shake_oy, SCREEN_WIDTH - 20, 188)
        pygame.draw.rect(surface, LIGHT_ARENA_BG, arena_rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_BORDER, arena_rect, 1, border_radius=8)

        # Boss Title & Subtitle
        stg_lbl = f"STAGE {self.current_stage}: {self.boss_data['boss_name']}  ({self.boss_data.get('problem_code', '')})"
        stg_surf = self.font_boss_title.render(stg_lbl, True, self.boss_data["theme_color"])
        ch_surf = self.font_body_bold.render(self.boss_data.get("boss_title", ""), True, LIGHT_TEXT_SECONDARY)

        surface.blit(stg_surf, (arena_rect.x + 20, arena_rect.y + 12))
        surface.blit(ch_surf, (arena_rect.x + 20, arena_rect.y + 40))

        # Boss HP Bar
        hp_x = arena_rect.x + 20
        hp_y = arena_rect.y + 68
        hp_w = 380
        hp_h = 24
        pygame.draw.rect(surface, (226, 232, 240), (hp_x, hp_y, hp_w, hp_h), border_radius=5)
        boss_ratio = max(0.0, min(1.0, self.boss_display_hp / self.boss_max_hp))
        boss_fill_w = int(hp_w * boss_ratio)
        hp_color = LIGHT_RED if boss_ratio < 0.3 else (LIGHT_ORANGE if boss_ratio < 0.6 else (202, 138, 4))
        if boss_fill_w > 0:
            pygame.draw.rect(surface, hp_color, (hp_x, hp_y, boss_fill_w, hp_h), border_radius=5)
        pygame.draw.rect(surface, (148, 163, 184), (hp_x, hp_y, hp_w, hp_h), 1, border_radius=5)

        hp_text = f"BOSS HP: {int(self.boss_display_hp)} / {self.boss_max_hp}"
        hp_surf = self.font_hp.render(hp_text, True, (255, 255, 255) if boss_ratio > 0.35 else LIGHT_TEXT_PRIMARY)
        surface.blit(hp_surf, (hp_x + 12, hp_y + 3))

        # Player HP Bar
        p_hp_x = arena_rect.x + 20
        p_hp_y = arena_rect.y + 100
        p_hp_w = 380
        p_hp_h = 22
        pygame.draw.rect(surface, (226, 232, 240), (p_hp_x, p_hp_y, p_hp_w, p_hp_h), border_radius=5)
        p_ratio = max(0.0, min(1.0, self.player_display_hp / self.player_max_hp))
        p_fill_w = int(p_hp_w * p_ratio)
        if p_fill_w > 0:
            pygame.draw.rect(surface, LIGHT_GREEN if p_ratio > 0.4 else LIGHT_RED, (p_hp_x, p_hp_y, p_fill_w, p_hp_h), border_radius=5)
        pygame.draw.rect(surface, (148, 163, 184), (p_hp_x, p_hp_y, p_hp_w, p_hp_h), 1, border_radius=5)

        p_hp_text = f"KNIGHT HP: {int(self.player_display_hp)} / {self.player_max_hp}"
        p_hp_surf = self.font_hp.render(p_hp_text, True, (255, 255, 255) if p_ratio > 0.35 else LIGHT_TEXT_PRIMARY)
        surface.blit(p_hp_surf, (p_hp_x + 12, p_hp_y + 2))

        # Attempt & Combat Rule Summary (Font 14)
        imp = self._get_current_imported()
        imp_txt = f"Loaded: {imp['filename']}" if imp else "No file loaded (.py / .cpp)"
        att_str = f"Attempts: {self.attempts[self.current_stage]}  |  {imp_txt}  |  1st-try AC: One-Shot (-1000 HP)"
        att_surf = self.font_body.render(att_str, True, LIGHT_TEXT_SECONDARY)
        surface.blit(att_surf, (arena_rect.x + 20, arena_rect.y + 134))

        rule_str = "2nd-try AC: Half-HP Cut (-500 HP)  |  Wrong (WA / TLE / RE): Boss Counter -200 HP"
        rule_surf = self.font_body.render(rule_str, True, LIGHT_TEXT_MUTED)
        surface.blit(rule_surf, (arena_rect.x + 20, arena_rect.y + 158))

        # Reset button
        self.btn_reset_battle.draw(surface)

        # Sprites
        boss_alive = self.boss_target_hp > 0
        self._render_player_sprite(surface, arena_rect.x + 650, arena_rect.y + 128)
        self._render_boss_sprite(surface, arena_rect.x + 930, arena_rect.y + 120, self.boss_data["boss_shape"], self.boss_data["theme_color"], boss_alive)

        # Defeated Banner
        if not boss_alive:
            banner_rect = pygame.Rect(arena_rect.x + 630, arena_rect.y + 12, 340, 42)
            pygame.draw.rect(surface, (254, 249, 195), banner_rect, border_radius=6)
            pygame.draw.rect(surface, LIGHT_GOLD, banner_rect, 2, border_radius=6)
            vic_txt = "ONE-SHOT CRITICAL VICTORY!" if save_manager.is_boss_one_shot(self.current_stage) else "BOSS DEFEATED!"
            vic_surf = self.font_h2.render(vic_txt, True, LIGHT_GOLD)
            surface.blit(vic_surf, (banner_rect.centerx - vic_surf.get_width() // 2, banner_rect.centery - vic_surf.get_height() // 2))

        for ft in self.floating_texts:
            ft.render(surface)

        # 2. Lower Problem Statement Card (10, 250, 1180, 460)
        prob_rect = pygame.Rect(10, 250, SCREEN_WIDTH - 20, 460)
        pygame.draw.rect(surface, LIGHT_CARD_BG, prob_rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_BORDER, prob_rect, 1, border_radius=8)

        # Sub-tab bar
        self.btn_sub_desc.draw(surface)
        self.btn_sub_samples.draw(surface)
        self.btn_go_to_import.draw(surface)
        pygame.draw.line(surface, LIGHT_BORDER, (prob_rect.x + 12, 298), (prob_rect.right - 12, 298), 1)

        # Scrollable Content Area (Font size 14)
        content_rect = pygame.Rect(24, 306, prob_rect.width - 48, prob_rect.height - 64)
        prev_clip = surface.get_clip()
        surface.set_clip(content_rect)

        if self.problem_sub_tab == "DESC":
            self._render_full_desc(surface, content_rect)
        else:
            self._render_full_samples(surface, content_rect)

        surface.set_clip(prev_clip)

        # Subtle scroll hint at bottom right
        scroll_hint = self.font_stage_tab.render("(Scroll mouse wheel to read more)", True, LIGHT_TEXT_MUTED)
        surface.blit(scroll_hint, (prob_rect.right - scroll_hint.get_width() - 20, prob_rect.bottom - 20))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wraps a line of text cleanly so font size 14 never overflows horizontally."""
        if not text:
            return [""]
        if font.size(text)[0] <= max_width:
            return [text]
        words = text.split(" ")
        lines = []
        curr = ""
        for w in words:
            cand = f"{curr} {w}".strip() if curr else w
            if font.size(cand)[0] <= max_width:
                curr = cand
            else:
                if curr:
                    lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)
        return lines

    def _render_full_desc(self, surface: pygame.Surface, rect: pygame.Rect):
        y = rect.y + self.problem_scroll_y
        line_h = 22

        header_str = f"{self.boss_data.get('contest_name', 'THỬ THÁCH LẬP TRÌNH')}  —  {self.boss_data.get('problem_code', '')}"
        surface.blit(self.font_h2.render(header_str, True, LIGHT_BLUE), (rect.x, y))
        y += 26

        meta_str = f"Dạng bài: {self.boss_data['topic']}  |  Giới hạn: {self.boss_data.get('time_limit', '1.0s')}  |  Bộ nhớ: {self.boss_data.get('memory_limit', '256 MB')}"
        for wrapped in self._wrap_text(meta_str, self.font_body_bold, rect.width):
            surface.blit(self.font_body_bold.render(wrapped, True, LIGHT_CYAN), (rect.x, y))
            y += line_h

        y += 6
        for raw_line in self.boss_data["description"].splitlines():
            if raw_line.startswith("["):
                col = LIGHT_ORANGE
                font = self.font_body_bold
                y += 4
            else:
                col = LIGHT_TEXT_PRIMARY
                font = self.font_body

            for wrapped in self._wrap_text(raw_line, font, rect.width):
                surface.blit(font.render(wrapped, True, col), (rect.x, y))
                y += line_h

    def _render_full_samples(self, surface: pygame.Surface, rect: pygame.Rect):
        y = rect.y + self.problem_scroll_y
        samples = self.boss_data.get("sample_tests", [])
        for i, sample in enumerate(samples, 1):
            s_title = self.font_h2.render(f"VÍ DỤ {i}:", True, LIGHT_BLUE)
            surface.blit(s_title, (rect.x, y))
            y += 24

            stdin_display = sample.get("stdin", str(sample.get("input", ""))).replace("\n", "  |  ")
            inp_str = f"Dữ liệu vào (stdin):   {stdin_display}"
            for wrapped in self._wrap_text(inp_str, self.font_code_mono, rect.width - 16):
                surface.blit(self.font_code_mono.render(wrapped, True, LIGHT_TEXT_PRIMARY), (rect.x + 12, y))
                y += 22

            exp_display = sample.get("expected_stdout", str(sample.get("expected", ""))).replace("\n", " ")
            out_str = f"Kết quả ra (stdout):   {exp_display}"
            for wrapped in self._wrap_text(out_str, self.font_code_mono, rect.width - 16):
                surface.blit(self.font_code_mono.render(wrapped, True, LIGHT_GREEN), (rect.x + 12, y))
                y += 22

            if "explanation" in sample:
                exp_str = f"Giải thích: {sample['explanation']}"
                for wrapped in self._wrap_text(exp_str, self.font_body, rect.width - 16):
                    surface.blit(self.font_body.render(wrapped, True, LIGHT_TEXT_SECONDARY), (rect.x + 12, y))
                    y += 22
            y += 12

    def _render_tab_import(self, surface: pygame.Surface, shake_ox: int, shake_oy: int):
        """Tab 2: File Import Control Card, Read-Only Code Preview (Font 14), and Runner Console."""
        # 1. Top File Import Control Card (10, 54, 1180, 116)
        ctrl_rect = pygame.Rect(10 + shake_ox, 54 + shake_oy, SCREEN_WIDTH - 20, 116)
        pygame.draw.rect(surface, LIGHT_CARD_BG, ctrl_rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_BORDER, ctrl_rect, 1, border_radius=8)

        imp = self._get_current_imported()
        if imp:
            lang_lbl = "C++ 17" if imp["language"] == "cpp" else "Python 3"
            line_cnt = len(imp["code"].splitlines())
            file_info = f"Loaded File (Stage {self.current_stage}): {imp['filename']}   |   Language: {lang_lbl}   |   {line_cnt} lines"
            info_col = LIGHT_GREEN
            path_str = f"Path: {imp['path']}"
        else:
            file_info = f"No solution file loaded for Stage {self.current_stage} ({self.boss_data.get('problem_code', '')})"
            info_col = LIGHT_ORANGE
            path_str = "Click [Browse File (.py/.cpp) [F3]] or drag & drop a file directly into this window!"

        surface.blit(self.font_h2.render(file_info, True, info_col), (ctrl_rect.x + 14, ctrl_rect.y + 10))
        path_surf = self.font_body.render(path_str, True, LIGHT_TEXT_SECONDARY)
        if path_surf.get_width() > 740:
            path_str_short = "..." + path_str[-78:]
            path_surf = self.font_body.render(path_str_short, True, LIGHT_TEXT_SECONDARY)
        surface.blit(path_surf, (ctrl_rect.x + 14, ctrl_rect.y + 36))

        # Mini Combat Status on Top-Right of Control Card
        status_box = pygame.Rect(ctrl_rect.right - 395, ctrl_rect.y + 10, 382, 48)
        pygame.draw.rect(surface, LIGHT_ARENA_BG, status_box, border_radius=6)
        pygame.draw.rect(surface, LIGHT_BORDER, status_box, 1, border_radius=6)
        boss_hp_s = f"Boss HP: {int(self.boss_display_hp)}/{self.boss_max_hp}"
        hero_hp_s = f"Knight HP: {int(self.player_display_hp)}/{self.player_max_hp}"
        surface.blit(self.font_body_bold.render(boss_hp_s, True, LIGHT_RED if self.boss_target_hp > 0 else LIGHT_GREEN), (status_box.x + 12, status_box.y + 5))
        surface.blit(self.font_body_bold.render(hero_hp_s, True, LIGHT_BLUE), (status_box.x + 195, status_box.y + 5))
        att_mini = f"Attempts: {self.attempts[self.current_stage]}  |  Status: {'DEFEATED' if self.boss_target_hp <= 0 else 'IN BATTLE'}"
        surface.blit(self.font_stage_tab.render(att_mini, True, LIGHT_TEXT_MUTED), (status_box.x + 12, status_box.y + 27))

        # Action Buttons
        self.btn_browse_file.draw(surface)
        self.btn_reload_file.draw(surface)
        self.btn_run_sample_top.draw(surface)
        self.btn_submit_top.draw(surface)
        self.btn_reset_tab2.draw(surface)

        # 2. Middle Read-Only Code Preview Card (10, 178, 1180, 256)
        prev_rect = pygame.Rect(10, 178, SCREEN_WIDTH - 20, 256)
        pygame.draw.rect(surface, LIGHT_CARD_BG, prev_rect, border_radius=6)
        pygame.draw.rect(surface, LIGHT_BORDER, prev_rect, 1, border_radius=6)

        hdr_rect = pygame.Rect(prev_rect.x, prev_rect.y, prev_rect.width, 30)
        pygame.draw.rect(surface, LIGHT_HEADER_BG, hdr_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.line(surface, LIGHT_BORDER, (prev_rect.x, prev_rect.y + 30), (prev_rect.right, prev_rect.y + 30), 1)

        hdr_title = "IMPORTED SOURCE PREVIEW (Font 14 - Read-only)"
        surface.blit(self.font_body_bold.render(hdr_title, True, LIGHT_TEXT_PRIMARY), (prev_rect.x + 12, prev_rect.y + 5))
        hint_r = "Drag & drop .py / .cpp file or scroll mouse wheel"
        hint_surf = self.font_stage_tab.render(hint_r, True, LIGHT_TEXT_MUTED)
        surface.blit(hint_surf, (prev_rect.right - hint_surf.get_width() - 12, prev_rect.y + 7))

        code_area = pygame.Rect(prev_rect.x + 2, prev_rect.y + 31, prev_rect.width - 4, prev_rect.height - 33)
        prev_clip = surface.get_clip()
        surface.set_clip(code_area)

        if imp:
            gutter_w = 50
            pygame.draw.rect(surface, LIGHT_ARENA_BG, (code_area.x, code_area.y, gutter_w, code_area.height))
            pygame.draw.line(surface, LIGHT_BORDER, (code_area.x + gutter_w, code_area.y), (code_area.x + gutter_w, code_area.bottom), 1)

            lines = imp["code"].splitlines()
            line_h = 21
            vis_count = max(1, code_area.height // line_h)
            for i in range(vis_count + 1):
                idx = self.preview_scroll_row + i
                if idx >= len(lines):
                    break
                dy = code_area.y + 4 + i * line_h
                num_surf = self.font_code_mono.render(f"{idx + 1:>3}", True, LIGHT_TEXT_MUTED)
                surface.blit(num_surf, (code_area.x + 8, dy))
                code_surf = self.font_code_mono.render(lines[idx], True, LIGHT_TEXT_PRIMARY)
                surface.blit(code_surf, (code_area.x + gutter_w + 12, dy))
        else:
            guide_lines = [
                ("HOW TO IMPORT & SUBMIT YOUR SOLUTION FILE:", LIGHT_BLUE, True),
                (f"1. Write your solution for Stage {self.current_stage} in an external editor (VS Code, PyCharm, Dev-C++, Notepad...).", LIGHT_TEXT_PRIMARY, False),
                ("2. Save as .py (Python 3: def solve(...) or stdin/stdout) or .cpp (C++ 17: cin/cout).", LIGHT_TEXT_PRIMARY, False),
                ("3. Click [Browse File (.py/.cpp) [F3]] above or DRAG & DROP your file directly onto this window.", LIGHT_TEXT_PRIMARY, False),
                ("4. After saving edits externally (Ctrl+S), click [Reload File [F4]] then [Submit - Attack Boss [F5]]!", LIGHT_GREEN, True),
            ]
            gy = code_area.y + 22
            for txt, col, is_b in guide_lines:
                fnt = self.font_body_bold if is_b else self.font_body
                for wline in self._wrap_text(txt, fnt, code_area.width - 48):
                    surface.blit(fnt.render(wline, True, col), (code_area.x + 24, gy))
                    gy += 24
                gy += 4

        surface.set_clip(prev_clip)

        # 3. Bottom Runner Console (Light Theme, Font 14)
        self.terminal.render(surface)

        # Floating combat texts visible on Tab 2 too
        for ft in self.floating_texts:
            ft.render(surface)

    # -----------------------------------------------------------------
    # VECTOR SPRITES (HIGH CONTRAST FOR LIGHT BACKGROUND)
    # -----------------------------------------------------------------
    def _render_player_sprite(self, surface: pygame.Surface, cx: int, cy: int):
        """Draws the Main Character Robot sprite floating above a soft shadow."""
        t = pygame.time.get_ticks() / 280.0
        bounce = int(math.sin(t) * 4)

        # Ground shadow
        pygame.draw.ellipse(surface, (203, 213, 225), (cx - 32, cy + 36, 64, 14))

        if self.player_sprite is not None:
            rect = self.player_sprite.get_rect(center=(cx, cy - 16 + bounce))
            surface.blit(self.player_sprite, rect)
        else:
            px, py = cx, cy + bounce
            pygame.draw.rect(surface, (37, 99, 235), (px - 26, py - 35, 52, 48), border_radius=6)
            pygame.draw.rect(surface, (15, 23, 42), (px - 26, py - 35, 52, 48), 2, border_radius=6)

    def _render_boss_sprite(self, surface: pygame.Surface, cx: int, cy: int, shape: str, theme_color: tuple, alive: bool):
        """Renders distinctive vector shapes for each Boss with crisp outlines for white background."""
        t = pygame.time.get_ticks() / 320.0
        float_y = int(math.sin(t) * 5)
        bx = cx
        by = cy + float_y

        # Ground shadow
        pygame.draw.ellipse(surface, (203, 213, 225), (cx - 46, cy + 32, 92, 16))

        outline_col = (15, 23, 42)
        if not alive:
            theme_color = (148, 163, 184)

        if shape == "slime":
            pts = [
                (bx - 46, by + 30), (bx - 50, by), (bx - 32, by - 40),
                (bx + 32, by - 40), (bx + 50, by), (bx + 46, by + 30)
            ]
            pygame.draw.polygon(surface, theme_color, pts)
            pygame.draw.polygon(surface, outline_col, pts, 2)
            pygame.draw.ellipse(surface, (219, 234, 254), (bx - 30, by - 30, 22, 12))
            if alive:
                pygame.draw.circle(surface, (255, 255, 255), (bx - 14, by - 2), 7)
                pygame.draw.circle(surface, (255, 255, 255), (bx + 14, by - 2), 7)
                pygame.draw.circle(surface, (15, 23, 42), (bx - 12, by - 2), 4)
                pygame.draw.circle(surface, (15, 23, 42), (bx + 12, by - 2), 4)

        elif shape == "golem":
            pygame.draw.rect(surface, theme_color, (bx - 44, by - 44, 88, 75), border_radius=6)
            pygame.draw.rect(surface, outline_col, (bx - 44, by - 44, 88, 75), 2, border_radius=6)
            pygame.draw.rect(surface, (71, 85, 105), (bx - 58, by - 30, 16, 45), border_radius=3)
            pygame.draw.rect(surface, (71, 85, 105), (bx + 42, by - 30, 16, 45), border_radius=3)
            if alive:
                pygame.draw.circle(surface, (251, 146, 60), (bx, by + 8), 12)
                pygame.draw.line(surface, (254, 240, 138), (bx - 22, by - 18), (bx - 8, by - 16), 4)
                pygame.draw.line(surface, (254, 240, 138), (bx + 8, by - 16), (bx + 22, by - 18), 4)

        elif shape == "serpent":
            for seg in range(4):
                sox = int(math.sin(t + seg) * 10)
                pygame.draw.circle(surface, theme_color, (bx + sox - seg * 10, by + 30 - seg * 16), 26 - seg * 3)
                pygame.draw.circle(surface, outline_col, (bx + sox - seg * 10, by + 30 - seg * 16), 26 - seg * 3, 2)
            pygame.draw.circle(surface, theme_color, (bx + 16, by - 24), 16)
            pygame.draw.circle(surface, outline_col, (bx + 16, by - 24), 16, 2)
            if alive:
                pygame.draw.circle(surface, (224, 242, 254), (bx + 22, by - 26), 6)

        elif shape == "dragon":
            pts = [(bx - 55, by + 25), (bx, by - 55), (bx + 55, by + 25), (bx, by + 12)]
            pygame.draw.polygon(surface, theme_color, pts)
            pygame.draw.polygon(surface, outline_col, pts, 2)
            pygame.draw.line(surface, (217, 119, 6), (bx - 18, by - 36), (bx - 38, by - 65), 6)
            pygame.draw.line(surface, (217, 119, 6), (bx + 18, by - 36), (bx + 38, by - 65), 6)
            if alive:
                pygame.draw.circle(surface, (254, 240, 138), (bx - 14, by - 12), 6)
                pygame.draw.circle(surface, (254, 240, 138), (bx + 14, by - 12), 6)

        elif shape == "phantom":
            pygame.draw.ellipse(surface, theme_color, (bx - 42, by - 50, 84, 90))
            pygame.draw.ellipse(surface, outline_col, (bx - 42, by - 50, 84, 90), 2)
            pygame.draw.ellipse(surface, (30, 27, 75), (bx - 32, by - 38, 64, 60))
            if alive:
                pygame.draw.circle(surface, (216, 180, 254), (bx - 12, by - 16), 6)
                pygame.draw.circle(surface, (216, 180, 254), (bx + 12, by - 16), 6)

        elif shape == "einstein" and "einstein" in self.boss_portraits:
            portrait = self.boss_portraits["einstein"]
            pw, ph = portrait.get_size()
            frame_rect = pygame.Rect(bx - pw // 2 - 4, by - ph // 2 - 12, pw + 8, ph + 8)
            # Shadow & Golden Boss Frame
            pygame.draw.rect(surface, (254, 243, 199) if alive else (226, 232, 240), frame_rect, border_radius=6)
            surface.blit(portrait, (bx - pw // 2, by - ph // 2 - 8))
            border_col = (180, 115, 10) if alive else (148, 163, 184)
            pygame.draw.rect(surface, border_col, frame_rect, 3, border_radius=6)
            if not alive:
                # Dimmed overlay + defeated cross when slain
                dim = pygame.Surface((pw, ph), pygame.SRCALPHA)
                dim.fill((255, 255, 255, 135))
                surface.blit(dim, (bx - pw // 2, by - ph // 2 - 8))
                pygame.draw.line(surface, (185, 28, 28), (frame_rect.left + 8, frame_rect.top + 8), (frame_rect.right - 8, frame_rect.bottom - 8), 4)
                pygame.draw.line(surface, (185, 28, 28), (frame_rect.right - 8, frame_rect.top + 8), (frame_rect.left + 8, frame_rect.bottom - 8), 4)

        else:
            # DP Overlord fallback vector sprite
            pygame.draw.rect(surface, theme_color, (bx - 48, by - 30, 96, 68), border_radius=6)
            pygame.draw.rect(surface, outline_col, (bx - 48, by - 30, 96, 68), 2, border_radius=6)
            crown_pts = [
                (bx - 42, by - 30), (bx - 30, by - 60), (bx, by - 42),
                (bx + 30, by - 60), (bx + 42, by - 30)
            ]
            pygame.draw.polygon(surface, (234, 179, 8), crown_pts)
            pygame.draw.polygon(surface, outline_col, crown_pts, 2)
            if alive:
                pygame.draw.circle(surface, (254, 249, 195), (bx - 16, by - 6), 7)
                pygame.draw.circle(surface, (254, 249, 195), (bx + 16, by - 6), 7)
