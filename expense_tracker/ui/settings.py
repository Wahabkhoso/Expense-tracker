"""
settings.py
Settings screen: user profile info, currency selection, theme
preference, and notification toggle.
"""

import customtkinter as ctk

from ui import theme
from ui.widgets import SectionCard, PrimaryButton, show_toast
from services.auth_service import update_settings

CURRENCIES = ["PKR", "USD", "EUR", "GBP", "INR", "AED", "SAR"]


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrapper, text="Settings", font=theme.font(22, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 18))

        # ---- Profile Card ----
        profile_card = SectionCard(wrapper, title="User Profile")
        profile_card.pack(fill="x", pady=(0, 16))
        profile_inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_inner.pack(fill="x", padx=18, pady=(0, 18))

        self.name_label = ctk.CTkLabel(profile_inner, text="", font=theme.font(16, "bold"),
                                        text_color=theme.TEXT_PRIMARY)
        self.name_label.pack(anchor="w")
        self.email_label = ctk.CTkLabel(profile_inner, text="", font=theme.font(12),
                                         text_color=theme.TEXT_SECONDARY)
        self.email_label.pack(anchor="w", pady=(2, 0))

        # ---- Preferences Card ----
        prefs_card = SectionCard(wrapper, title="Preferences")
        prefs_card.pack(fill="x", pady=(0, 16))
        prefs_inner = ctk.CTkFrame(prefs_card, fg_color="transparent")
        prefs_inner.pack(fill="x", padx=18, pady=(0, 18))

        ctk.CTkLabel(prefs_inner, text="Currency", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.currency_var = ctk.StringVar()
        ctk.CTkOptionMenu(prefs_inner, variable=self.currency_var, values=CURRENCIES, width=160,
                          height=38, fg_color=theme.BG_DARK, button_color=theme.ACCENT
                          ).grid(row=1, column=0, sticky="w", pady=(4, 16))

        ctk.CTkLabel(prefs_inner, text="Theme", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=(24, 0))
        self.theme_var = ctk.StringVar()
        ctk.CTkOptionMenu(prefs_inner, variable=self.theme_var, values=["dark", "light"], width=160,
                          height=38, fg_color=theme.BG_DARK, button_color=theme.ACCENT
                          ).grid(row=1, column=1, sticky="w", padx=(24, 0), pady=(4, 16))

        self.notifications_var = ctk.BooleanVar()
        ctk.CTkCheckBox(prefs_inner, text="Enable notifications", variable=self.notifications_var,
                         font=theme.font(12), fg_color=theme.ACCENT
                         ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

        PrimaryButton(prefs_card, "Save Preferences", command=self._save, width=180
                      ).pack(anchor="w", padx=18, pady=(0, 18))

        note = ctk.CTkLabel(wrapper, text="Note: theme switching requires an app restart to fully apply.",
                             font=theme.font(11), text_color=theme.TEXT_MUTED)
        note.pack(anchor="w")

    def refresh(self):
        user = self.app.current_user
        self.name_label.configure(text=user.full_name)
        self.email_label.configure(text=user.email)
        self.currency_var.set(user.currency)
        self.theme_var.set(user.theme)
        self.notifications_var.set(user.notifications_enabled)

    def _save(self):
        user = update_settings(
            self.app.current_user.id,
            currency=self.currency_var.get(),
            theme=self.theme_var.get(),
            notifications_enabled=self.notifications_var.get(),
        )
        self.app.current_user = user
        show_toast(self.app.content_area, "Settings saved successfully!", "success")
