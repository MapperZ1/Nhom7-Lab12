"""
Shared UI Components for Robo-Logic: Boss Battle.
Includes adaptive Button supporting both light (white contest) and dark backgrounds.
"""

import pygame
from src.config import COLOR_TEXT_PRIMARY, get_ui_font
from src.audio import audio


class Button:
    def __init__(self, rect, text, bg_color, text_color=COLOR_TEXT_PRIMARY, font=None, on_click=None, tooltip=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font or get_ui_font(13, bold=True)
        self.on_click = on_click
        self.tooltip = tooltip
        self.is_hovered = False
        self.is_disabled = False

    def handle_event(self, event):
        if self.is_disabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio.play_click()
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface):
        luma = 0.299 * self.bg_color[0] + 0.587 * self.bg_color[1] + 0.114 * self.bg_color[2]
        is_light_bg = luma > 165

        if self.is_disabled:
            draw_bg = (226, 232, 240) if is_light_bg else (50, 55, 65)
            text_col = (148, 163, 184) if is_light_bg else (110, 120, 130)
            border_col = (203, 213, 225) if is_light_bg else (70, 75, 85)
        elif self.is_hovered:
            if is_light_bg:
                draw_bg = tuple(max(0, c - 18) for c in self.bg_color)
                text_col = self.text_color
                border_col = (100, 116, 139)
            else:
                draw_bg = tuple(min(255, c + 25) for c in self.bg_color)
                text_col = (255, 255, 255)
                border_col = (220, 235, 255)
        else:
            draw_bg = self.bg_color
            text_col = self.text_color
            border_col = (180, 192, 210) if is_light_bg else tuple(max(0, c - 20) for c in self.bg_color)

        pygame.draw.rect(surface, draw_bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, 1, border_radius=6)

        text_surf = self.font.render(self.text, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def render(self, surface):
        self.draw(surface)
