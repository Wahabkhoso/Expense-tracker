"""
register.py
Registration screen for new users.
"""

import customtkinter as ctk
from ui import theme
from ui.widgets import PrimaryButton, show_toast
from services.auth_service import register_user, AuthError


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, on_register_success, on_go_login):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.on_register_success = on_register_success
        self.on_go_login = on_go_login
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=theme.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=theme.BORDER_COLOR, width=440)
        container.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(padx=48, pady=40)

        ctk.CTkLabel(inner, text="Create Account", font=theme.font(24, "bold"),
                     text_color=theme.ACCENT).pack(pady=(0, 2))
        ctk.CTkLabel(inner, text="Start tracking your finances with ExpensePro",
                     font=theme.font(12), text_color=theme.TEXT_SECONDARY).pack(pady=(0, 20))

        def labeled_entry(label_text, show=None, placeholder=""):
            ctk.CTkLabel(inner, text=label_text, font=theme.font(12),
                         text_color=theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
            entry = ctk.CTkEntry(inner, placeholder_text=placeholder, show=show,
                                  height=38, width=320)
            entry.pack(pady=(4, 12))
            return entry

        self.name_entry = labeled_entry("Full Name", placeholder="John Doe")
        self.email_entry = labeled_entry("Email", placeholder="you@example.com")
        self.password_entry = labeled_entry("Password", show="•", placeholder="At least 6 characters")
        self.confirm_entry = labeled_entry("Confirm Password", show="•", placeholder="Re-enter password")
        self.confirm_entry.bind("<Return>", lambda e: self._handle_register())

        self.error_label = ctk.CTkLabel(inner, text="", font=theme.font(11),
                                         text_color=theme.EXPENSE_RED, wraplength=320)
        self.error_label.pack(pady=(0, 8))

        PrimaryButton(inner, "Create Account", command=self._handle_register, width=320).pack(pady=(4, 12))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="Already have an account?", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        link = ctk.CTkLabel(row, text="Sign In", font=theme.font(12, "bold"),
                             text_color=theme.ACCENT, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self.on_go_login())

    def _handle_register(self):
        try:
            user = register_user(
                self.name_entry.get(), self.email_entry.get(),
                self.password_entry.get(), self.confirm_entry.get(),
            )
            self.error_label.configure(text="")
            self.on_register_success(user)
        except AuthError as e:
            self.error_label.configure(text=str(e))
