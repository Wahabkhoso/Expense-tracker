"""
main.py
Entry point for the ExpensePro desktop application.
Manages transitions between Login -> Register -> Main App Shell.
"""

import sys
import traceback
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from ui import theme
from ui.login import LoginScreen
from ui.register import RegisterScreen
from ui.app_shell import AppShell


class ExpenseProApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        theme.setup_appearance()

        self.title("ExpensePro - Expense Tracker & Analytics")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=theme.BG_DARK)

        self.current_user = None
        self.active_widget = None

        self.show_login()

    def _clear(self):
        if self.active_widget is not None:
            self.active_widget.destroy()
            self.active_widget = None

    def show_login(self):
        self._clear()
        screen = LoginScreen(self, on_login_success=self.on_login_success,
                              on_go_register=self.show_register)
        screen.pack(fill="both", expand=True)
        self.active_widget = screen

    def show_register(self):
        self._clear()
        screen = RegisterScreen(self, on_register_success=self.on_login_success,
                                 on_go_login=self.show_login)
        screen.pack(fill="both", expand=True)
        self.active_widget = screen

    def on_login_success(self, user):
        self.current_user = user
        self._clear()
        shell = AppShell(self, current_user=user, on_logout=self.on_logout)
        shell.pack(fill="both", expand=True)
        self.active_widget = shell

    def on_logout(self):
        self.current_user = None
        self.show_login()


def main():
    app = ExpenseProApp()

    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global safety net so the app never crashes with a raw traceback."""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(error_msg, file=sys.stderr)
        try:
            messagebox.showerror(
                "Unexpected Error",
                "Something went wrong. The error has been logged.\n\n"
                f"{exc_value}"
            )
        except Exception:
            pass

    tk.Tk.report_callback_exception = handle_exception
    app.mainloop()


if __name__ == "__main__":
    main()
