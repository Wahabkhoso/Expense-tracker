"""
widgets.py
Reusable, styled UI components shared across screens: summary cards,
a simple scrollable table, confirmation dialogs, and toast messages.
"""

import customtkinter as ctk
from ui import theme


class SummaryCard(ctk.CTkFrame):
    """A rounded metric card used on Dashboard / Analytics screens."""

    def __init__(self, master, title: str, value: str, accent_color: str, icon: str = "●", **kwargs):
        super().__init__(master, fg_color=theme.CARD_BG, corner_radius=14,
                          border_width=1, border_color=theme.BORDER_COLOR, **kwargs)

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(16, 4))

        icon_label = ctk.CTkLabel(top_row, text=icon, font=theme.font(20), text_color=accent_color)
        icon_label.pack(side="left")

        self.title_label = ctk.CTkLabel(self, text=title, font=theme.font(12),
                                         text_color=theme.TEXT_SECONDARY, anchor="w")
        self.title_label.pack(fill="x", padx=18, pady=(2, 0))

        self.value_label = ctk.CTkLabel(self, text=value, font=theme.font(22, "bold"),
                                         text_color=theme.TEXT_PRIMARY, anchor="w")
        self.value_label.pack(fill="x", padx=18, pady=(2, 16))

    def update_value(self, value: str):
        self.value_label.configure(text=value)


class SectionCard(ctk.CTkFrame):
    """A generic rounded content container with an optional header."""

    def __init__(self, master, title: str = None, **kwargs):
        super().__init__(master, fg_color=theme.CARD_BG, corner_radius=14,
                          border_width=1, border_color=theme.BORDER_COLOR, **kwargs)
        if title:
            header = ctk.CTkLabel(self, text=title, font=theme.font(15, "bold"),
                                   text_color=theme.TEXT_PRIMARY, anchor="w")
            header.pack(fill="x", padx=18, pady=(16, 8))


class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        defaults = dict(
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            font=theme.font(13, "bold"), corner_radius=8, height=38,
        )
        defaults.update(kwargs)
        super().__init__(master, text=text, command=command, **defaults)


class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        defaults = dict(
            fg_color="transparent", hover_color=theme.CARD_BG_HOVER,
            border_width=1, border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY, font=theme.font(13),
            corner_radius=8, height=38,
        )
        defaults.update(kwargs)
        super().__init__(master, text=text, command=command, **defaults)


class DangerButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        defaults = dict(
            fg_color=theme.EXPENSE_RED, hover_color="#c0392b",
            font=theme.font(12, "bold"), corner_radius=6, height=30,
        )
        defaults.update(kwargs)
        super().__init__(master, text=text, command=command, **defaults)


def show_toast(parent, message: str, kind: str = "success"):
    """Small temporary notification banner at the top of the current screen."""
    color = {
        "success": theme.INCOME_GREEN,
        "error": theme.EXPENSE_RED,
        "warning": theme.WARNING_ORANGE,
        "info": theme.BALANCE_BLUE,
    }.get(kind, theme.BALANCE_BLUE)

    toast = ctk.CTkFrame(parent, fg_color=color, corner_radius=8, height=40)
    toast.place(relx=0.5, rely=0.02, anchor="n")
    label = ctk.CTkLabel(toast, text=message, font=theme.font(12, "bold"), text_color="#111111")
    label.pack(padx=16, pady=8)
    parent.after(2600, toast.destroy)


def confirm_dialog(parent, title: str, message: str, on_confirm):
    """A modal Yes/No confirmation dialog."""
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("380x180")
    dialog.configure(fg_color=theme.CARD_BG)
    dialog.grab_set()
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text=title, font=theme.font(15, "bold"),
                 text_color=theme.TEXT_PRIMARY).pack(pady=(20, 6))
    ctk.CTkLabel(dialog, text=message, font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                 wraplength=320, justify="center").pack(pady=(0, 16))

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=6)

    def _confirm():
        dialog.destroy()
        on_confirm()

    DangerButton(btn_frame, "Delete", command=_confirm, width=110).pack(side="left", padx=6)
    SecondaryButton(btn_frame, "Cancel", command=dialog.destroy, width=110).pack(side="left", padx=6)


def status_badge(master, text: str, kind: str = "info"):
    color_map = {
        "income": (theme.INCOME_GREEN, "#0d2818"),
        "expense": (theme.EXPENSE_RED, "#2c1414"),
        "under": (theme.INCOME_GREEN, "#0d2818"),
        "near": (theme.WARNING_ORANGE, "#2c2412"),
        "exceeded": (theme.EXPENSE_RED, "#2c1414"),
        "info": (theme.BALANCE_BLUE, "#0d1f2c"),
    }
    fg, bg = color_map.get(kind, (theme.BALANCE_BLUE, "#0d1f2c"))
    badge = ctk.CTkLabel(master, text=text, font=theme.font(11, "bold"), text_color=fg,
                          fg_color=bg, corner_radius=6, padx=10, pady=3)
    return badge
