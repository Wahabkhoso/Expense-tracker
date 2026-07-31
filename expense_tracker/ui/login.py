"""
login.py
Login screen shown before the user reaches the main application shell.
"""

import customtkinter as ctk
from ui import theme
from ui.widgets import PrimaryButton, SecondaryButton, show_toast
from services.auth_service import login_user, AuthError


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_go_register):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.on_login_success = on_login_success
        self.on_go_register = on_go_register
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=theme.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=theme.BORDER_COLOR, width=420)
        container.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(padx=48, pady=44)

        ctk.CTkLabel(inner, text="ExpensePro", font=theme.font(28, "bold"),
                     text_color=theme.ACCENT).pack(pady=(0, 2))
        ctk.CTkLabel(inner, text="Welcome back! Please sign in to continue.",
                     font=theme.font(12), text_color=theme.TEXT_SECONDARY).pack(pady=(0, 24))

        ctk.CTkLabel(inner, text="Email", font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                     anchor="w").pack(fill="x")
        self.email_entry = ctk.CTkEntry(inner, placeholder_text="you@example.com",
                                         height=40, width=320)
        self.email_entry.pack(pady=(4, 14))

        ctk.CTkLabel(inner, text="Password", font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                     anchor="w").pack(fill="x")
        self.password_entry = ctk.CTkEntry(inner, placeholder_text="••••••••",
                                            show="•", height=40, width=320)
        self.password_entry.pack(pady=(4, 6))
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

        self.error_label = ctk.CTkLabel(inner, text="", font=theme.font(11),
                                         text_color=theme.EXPENSE_RED, wraplength=320)
        self.error_label.pack(pady=(0, 8))

        PrimaryButton(inner, "Sign In", command=self._handle_login, width=320).pack(pady=(8, 12))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="Don't have an account?", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        link = ctk.CTkLabel(row, text="Register", font=theme.font(12, "bold"),
                             text_color=theme.ACCENT, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self.on_go_register())

    def _handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            user = login_user(email, password)
            self.error_label.configure(text="")
            self.on_login_success(user)
        except AuthError as e:
            self.error_label.configure(text=str(e))
