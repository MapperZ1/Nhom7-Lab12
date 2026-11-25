"""
BashTestTerminal - Output Log & Test Runner Panel for File Import Judging.
Full English UI with clean white/light mode styling and font size 14.
"""

import pygame
from typing import List, Tuple, Optional, Callable
from src.config import get_code_font, get_ui_font
from src.ui.components import Button


class TerminalLine:
    def __init__(self, text: str, color: tuple = (25, 35, 50), is_bold: bool = False):
        self.text = text
        self.color = color
        self.is_bold = is_bold


class BashTestTerminal:
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        on_run_sample: Optional[Callable[[], None]] = None,
        on_submit: Optional[Callable[[], None]] = None,
        hostname: str = "arena",
        username: str = "player",
        theme: str = "light"
    ):
        self.rect = pygame.Rect(rect)
        self.on_run_sample = on_run_sample
        self.on_submit = on_submit
        self.hostname = hostname
        self.username = username
        self.theme = theme

        # Fonts: Size 14 for clear readability
        self.font_term = get_code_font(14)
        self.font_term_bold = get_code_font(14, bold=True)
        self.font_header = get_ui_font(14, bold=True)
        self.font_btn = get_ui_font(12, bold=True)

        # Output buffer
        self.lines: List[TerminalLine] = []
        self.scroll_y = 0
        self.line_height = 22
        self.max_buffer_lines = 400

        # Header dimensions
        self.header_height = 34

        if self.theme == "light":
            self.bg_col = (255, 255, 255)
            self.border_col = (203, 213, 225)
            self.header_bg = (241, 245, 249)
            self.header_text_col = (15, 23, 42)
            self.col_info = (30, 41, 59)
            self.col_cmd = (29, 78, 216)
            self.col_pass = (21, 128, 61)
            self.col_fail = (185, 28, 28)
            self.col_combat = (180, 83, 9)
            self.col_oneshot = (161, 98, 7)
            self.col_sep = (203, 213, 225)
            btn_clear_bg = (226, 232, 240)
            btn_clear_txt = (30, 41, 59)
        else:
            self.bg_col = (15, 18, 25)
            self.border_col = (45, 55, 75)
            self.header_bg = (25, 32, 45)
            self.header_text_col = (220, 230, 242)
            self.col_info = (230, 238, 248)
            self.col_cmd = (57, 211, 239)
            self.col_pass = (46, 210, 100)
            self.col_fail = (255, 90, 90)
            self.col_combat = (245, 158, 11)
            self.col_oneshot = (250, 204, 21)
            self.col_sep = (65, 80, 105)
            btn_clear_bg = (50, 60, 78)
            btn_clear_txt = (240, 246, 252)

        btn_y = self.rect.y + 4
        btn_h = 26
        self.btn_run_sample = Button(
            (self.rect.right - 350, btn_y, 130, btn_h),
            "Run Sample (F6)", (14, 116, 144), text_color=(255, 255, 255),
            font=self.font_btn, on_click=self.on_run_sample
        )
        self.btn_submit = Button(
            (self.rect.right - 214, btn_y, 134, btn_h),
            "Submit (F5)", (21, 128, 61), text_color=(255, 255, 255),
            font=self.font_btn, on_click=self.on_submit
        )
        self.btn_clear = Button(
            (self.rect.right - 74, btn_y, 66, btn_h),
            "Clear", btn_clear_bg, text_color=btn_clear_txt,
            font=self.font_btn, on_click=self.clear
        )

        self.log_info("Test Runner ready (Python 3 & C++ 17). Browse or drop a .py / .cpp file to start.")
        self.log_info("Click [Run Sample] to test safely or [Submit] to attack the Boss.")
        self.log_separator()

    def clear(self):
        self.lines.clear()
        self.scroll_y = 0
        self.log_info("Console cleared. Ready for next run.")

    def _add_wrapped_line(self, text: str, color: tuple, is_bold: bool = False):
        max_w = max(200, self.rect.width - 28)
        font = self.font_term_bold if is_bold else self.font_term
        for raw_line in text.splitlines() or [""]:
            if font.size(raw_line)[0] <= max_w:
                self.lines.append(TerminalLine(raw_line, color, is_bold))
            else:
                words = raw_line.split(" ")
                curr = ""
                for w in words:
                    cand = f"{curr} {w}".strip() if curr else w
                    if font.size(cand)[0] <= max_w:
                        curr = cand
                    else:
                        if curr:
                            self.lines.append(TerminalLine(curr, color, is_bold))
                        while font.size(w)[0] > max_w and len(w) > 10:
                            cut = len(w) // 2
                            while cut > 1 and font.size(w[:cut])[0] > max_w:
                                cut -= 2
                            self.lines.append(TerminalLine(w[:cut], color, is_bold))
                            w = w[cut:]
                        curr = w
                if curr:
                    self.lines.append(TerminalLine(curr, color, is_bold))
        self._auto_scroll_bottom()

    def log_command(self, cmd_str: str):
        prompt = f"{self.username}@{self.hostname}:~$ {cmd_str}"
        self._add_wrapped_line(prompt, self.col_cmd, is_bold=True)

    def log_info(self, text: str):
        self._add_wrapped_line(text, self.col_info, is_bold=False)

    def log_pass(self, text: str):
        self._add_wrapped_line(text, self.col_pass, is_bold=True)

    def log_fail(self, text: str):
        self._add_wrapped_line(text, self.col_fail, is_bold=True)

    def log_combat(self, text: str, is_one_shot: bool = False):
        col = self.col_oneshot if is_one_shot else self.col_combat
        self._add_wrapped_line(text, col, is_bold=True)

    def log_separator(self):
        self.lines.append(TerminalLine("-" * 92, self.col_sep))
        self._auto_scroll_bottom()

    def _auto_scroll_bottom(self):
        if len(self.lines) > self.max_buffer_lines:
            self.lines = self.lines[-self.max_buffer_lines:]
        vis_lines = self._visible_lines_count()
        if len(self.lines) > vis_lines:
            self.scroll_y = len(self.lines) - vis_lines
        else:
            self.scroll_y = 0

    def _visible_lines_count(self) -> int:
        content_h = self.rect.height - self.header_height - 10
        return max(1, content_h // self.line_height)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.btn_run_sample.handle_event(event):
            return True
        if self.btn_submit.handle_event(event):
            return True
        if self.btn_clear.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - 2)
                return True
            elif event.button == 5:
                max_scroll = max(0, len(self.lines) - self._visible_lines_count())
                self.scroll_y = min(max_scroll, self.scroll_y + 2)
                return True

        return False

    def render(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.border_col, self.rect, 1, border_radius=6)

        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height)
        pygame.draw.rect(surface, self.header_bg, header_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.line(surface, self.border_col, (self.rect.x, self.rect.y + self.header_height), (self.rect.right, self.rect.y + self.header_height), 1)

        title_str = "TEST RUNNER & COMBAT CONSOLE"
        title_surf = self.font_header.render(title_str, True, self.header_text_col)
        surface.blit(title_surf, (self.rect.x + 12, self.rect.y + 7))

        self.btn_run_sample.draw(surface)
        self.btn_submit.draw(surface)
        self.btn_clear.draw(surface)

        content_y = self.rect.y + self.header_height + 6
        content_h = self.rect.height - self.header_height - 10
        vis_lines = self._visible_lines_count()

        prev_clip = surface.get_clip()
        term_clip = pygame.Rect(self.rect.x + 4, content_y, self.rect.width - 8, content_h)
        surface.set_clip(term_clip)

        for i in range(vis_lines + 1):
            line_idx = self.scroll_y + i
            if line_idx >= len(self.lines):
                break

            line_data = self.lines[line_idx]
            font = self.font_term_bold if line_data.is_bold else self.font_term
            text_surf = font.render(line_data.text, True, line_data.color)
            draw_y = content_y + i * self.line_height
            surface.blit(text_surf, (self.rect.x + 12, draw_y))

        surface.set_clip(prev_clip)
