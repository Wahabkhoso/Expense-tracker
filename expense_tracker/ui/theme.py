"""
theme.py
Central color palette, fonts, and spacing constants so every screen
shares one consistent, professional dark financial-dashboard look.
"""

import customtkinter as ctk

# ---- Colors ----
BG_DARK = "#161622"
SIDEBAR_BG = "#1c1c2b"
CARD_BG = "#20202f"
CARD_BG_HOVER = "#262638"
BORDER_COLOR = "#33334a"

TEXT_PRIMARY = "#f2f2f7"
TEXT_SECONDARY = "#9a9ab0"
TEXT_MUTED = "#6d6d85"

INCOME_GREEN = "#2ecc71"
EXPENSE_RED = "#e74c3c"
BALANCE_BLUE = "#3498db"
WARNING_ORANGE = "#f39c12"

ACCENT = "#6c5ce7"
ACCENT_HOVER = "#5b4bd1"

SIDEBAR_ACTIVE = "#2a2a40"

FONT_FAMILY = "Segoe UI"


def font(size=13, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def setup_appearance():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
