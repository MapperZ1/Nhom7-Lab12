"""
Configuration, Theme Colors, and Font Helpers for Robo-Logic: Boss Battle.
"""

import os
import sys
import pygame

if not pygame.font.get_init():
    pygame.font.init()


def get_resource_path(relative_path: str) -> str:
    """Resolves bundled read-only asset paths for both source and PyInstaller --onefile."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_app_dir() -> str:
    """Resolves writable app directory (beside .exe when frozen, project root otherwise)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Screen configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
FPS = 60

# Dark Cyber Palette (Main Menu & Docs)
COLOR_BG = (22, 27, 34)
COLOR_WORLD_BG = (15, 18, 24)
COLOR_PANEL_BG = (28, 33, 44)
COLOR_PANEL_BORDER = (48, 54, 69)
COLOR_CARD_BG = (35, 41, 55)

COLOR_TEXT_PRIMARY = (240, 246, 252)
COLOR_TEXT_SECONDARY = (139, 148, 158)
COLOR_TEXT_MUTED = (90, 99, 110)
COLOR_TEXT_ACCENT = (88, 166, 255)

COLOR_ACCENT_BLUE = (56, 139, 253)
COLOR_ACCENT_GREEN = (46, 160, 67)
COLOR_ACCENT_ORANGE = (219, 109, 40)
COLOR_ACCENT_PURPLE = (163, 113, 247)
COLOR_ACCENT_CYAN = (57, 211, 239)
COLOR_ACCENT_YELLOW = (240, 180, 41)
COLOR_ACCENT_RED = (248, 81, 73)


def get_ui_font(size, bold=False):
    """Returns a reliable system font with full Vietnamese diacritics support."""
    try:
        return pygame.font.SysFont("segoeui,arial,tahoma", size, bold=bold)
    except Exception:
        return pygame.font.SysFont(None, size, bold=bold)


def get_code_font(size, bold=False):
    """Returns a reliable monospace font for code & logs."""
    try:
        return pygame.font.SysFont("consolas,couriernew", size, bold=bold)
    except Exception:
        return pygame.font.SysFont(None, size, bold=bold)
