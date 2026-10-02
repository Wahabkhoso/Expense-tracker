"""
app_shell.py
The main authenticated application window: persistent sidebar
navigation plus a swappable content area for each screen.
"""

import customtkinter as ctk

from ui import theme
from ui.dashboard import DashboardScreen
from ui.transactions import TransactionsScreen
from ui.add_transaction import AddTransactionScreen
from ui.analytics import AnalyticsScreen
from ui.budgets import BudgetsScreen
from ui.reports import ReportsScreen
from ui.settings import SettingsScreen

NAV_ITEMS = [
    ("Dashboard", "🏠"),
    ("Transactions", "📋"),
    ("Add Transaction", "➕"),
    ("Analytics", "📊"),
    ("Budgets", "🎯"),
    ("Reports", "🧾"),
    ("Settings", "⚙"),
]


class AppShell(ctk.CTkFrame):
    def __init__(self, master, current_user, on_logout):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.current_user = current_user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.active_screen_name = "Dashboard"

        self._build_sidebar()
        self._build_content_area()
        self._build_screens()
        self.navigate("Dashboard")

    # ---------- Sidebar ----------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=theme.SIDEBAR_BG, width=230, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(26, 30), padx=20)
        ctk.CTkLabel(logo_frame, text="💳 ExpensePro", font=theme.font(19, "bold"),
                     text_color=theme.ACCENT).pack(anchor="w")

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=14)

        for name, icon in NAV_ITEMS:
            btn = ctk.CTkButton(
                nav_frame, text=f"  {icon}   {name}", anchor="w", height=42,
                font=theme.font(13), corner_radius=8,
                fg_color="transparent", hover_color=theme.CARD_BG_HOVER,
                text_color=theme.TEXT_SECONDARY,
                command=lambda n=name: self.navigate(n),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[name] = btn

        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=24)

        ctk.CTkLabel(bottom_frame, text=self.current_user.full_name, font=theme.font(12, "bold"),
                     text_color=theme.TEXT_PRIMARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(bottom_frame, text=self.current_user.email, font=theme.font(10),
                     text_color=theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 10))
        ctk.CTkButton(bottom_frame, text="Logout", height=34, font=theme.font(12),
                      fg_color=theme.EXPENSE_RED, hover_color="#c0392b",
                      command=self.on_logout).pack(fill="x")

    # ---------- Content area ----------
    def _build_content_area(self):
        self.content_area = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _build_screens(self):
        self.screens = {
            "Dashboard": DashboardScreen(self.content_area, self),
            "Transactions": TransactionsScreen(self.content_area, self),
            "Add Transaction": AddTransactionScreen(self.content_area, self),
            "Analytics": AnalyticsScreen(self.content_area, self),
            "Budgets": BudgetsScreen(self.content_area, self),
            "Reports": ReportsScreen(self.content_area, self),
            "Settings": SettingsScreen(self.content_area, self),
        }
        for screen in self.screens.values():
            screen.grid(row=0, column=0, sticky="nsew")

    def navigate(self, screen_name: str):
        self.active_screen_name = screen_name
        for name, btn in self.nav_buttons.items():
            if name == screen_name:
                btn.configure(fg_color=theme.SIDEBAR_ACTIVE, text_color=theme.TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=theme.TEXT_SECONDARY)

        screen = self.screens[screen_name]
        screen.tkraise()
        # Force the screen switch to render immediately, then load the
        # (potentially heavier) data/charts a moment later. This avoids
        # the whole app freezing for a beat on every navigation click.
        self.update_idletasks()
        if hasattr(screen, "refresh"):
            self.after(30, screen.refresh)

    def refresh_all_screens(self):
        """Called after any CRUD operation so every screen shows live data."""
        for screen in self.screens.values():
            if hasattr(screen, "refresh"):
                screen.refresh()