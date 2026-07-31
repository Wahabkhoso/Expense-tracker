"""
budgets.py
Budget management screen: set a monthly budget per category, view
spend progress bars, and surface over-budget warnings.
"""

from datetime import date

import customtkinter as ctk

from ui import theme
from ui.widgets import SectionCard, PrimaryButton, DangerButton, confirm_dialog, show_toast, status_badge
from services import budget_service, transaction_service
from services.budget_service import BudgetValidationError

MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


class BudgetsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        today = date.today()
        self.month = today.month
        self.year = today.year
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=28, pady=24)

        top_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(top_row, text="Budgets", font=theme.font(22, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")

        self.month_label = ctk.CTkLabel(top_row, text="", font=theme.font(13),
                                         text_color=theme.TEXT_SECONDARY)
        self.month_label.pack(side="right", padx=(0, 12))
        ctk.CTkButton(top_row, text="▶", width=32, height=32, command=self._next_month,
                      fg_color=theme.CARD_BG, hover_color=theme.CARD_BG_HOVER).pack(side="right", padx=2)
        ctk.CTkButton(top_row, text="◀", width=32, height=32, command=self._prev_month,
                      fg_color=theme.CARD_BG, hover_color=theme.CARD_BG_HOVER).pack(side="right", padx=2)

        # ---- Set Budget Form ----
        form_card = SectionCard(wrapper, title="Set a Category Budget")
        form_card.pack(fill="x", pady=(16, 16))
        form_row = ctk.CTkFrame(form_card, fg_color="transparent")
        form_row.pack(fill="x", padx=18, pady=(0, 18))

        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(form_row, variable=self.category_var,
                                                values=transaction_service.get_categories_by_type("Expense"),
                                                width=180, height=38, fg_color=theme.BG_DARK,
                                                button_color=theme.ACCENT)
        self.category_menu.pack(side="left", padx=(0, 10))

        self.amount_entry = ctk.CTkEntry(form_row, placeholder_text="Budget amount", width=180,
                                          height=38, fg_color=theme.BG_DARK)
        self.amount_entry.pack(side="left", padx=(0, 10))

        PrimaryButton(form_row, "Set Budget", command=self._set_budget, width=140).pack(side="left")

        self.error_label = ctk.CTkLabel(form_card, text="", font=theme.font(11),
                                         text_color=theme.EXPENSE_RED)
        self.error_label.pack(anchor="w", padx=18, pady=(0, 12))

        # ---- Budget cards list ----
        self.list_scroll = ctk.CTkScrollableFrame(wrapper, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True)

    def refresh(self):
        self.month_label.configure(text=f"{MONTH_NAMES[self.month - 1]} {self.year}")
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        user_id = self.app.current_user.id
        statuses = budget_service.get_budget_status(user_id, self.month, self.year)

        if not statuses:
            ctk.CTkLabel(self.list_scroll, text="No budgets set for this month yet.",
                         font=theme.font(12), text_color=theme.TEXT_MUTED).pack(pady=20)
            return

        for s in statuses:
            card = SectionCard(self.list_scroll)
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=14)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=s["category"], font=theme.font(15, "bold"),
                         text_color=theme.TEXT_PRIMARY).pack(side="left")

            badge_kind = {"Under Budget": "under", "Near Limit": "near",
                          "Budget Exceeded": "exceeded", "No Budget": "info"}[s["status"]]
            status_badge(top, s["status"], badge_kind).pack(side="left", padx=10)

            DangerButton(top, "Remove", width=70, height=26,
                         command=lambda sid=s["id"]: self._delete_budget(sid)).pack(side="right")

            progress = ctk.CTkProgressBar(inner, height=14, corner_radius=6,
                                           progress_color=self._bar_color(s["status"]),
                                           fg_color=theme.BG_DARK)
            progress.set(s["percent"] / 100)
            progress.pack(fill="x", pady=(10, 8))

            details = ctk.CTkFrame(inner, fg_color="transparent")
            details.pack(fill="x")
            ctk.CTkLabel(details, text=f"Budget: Rs. {s['budget']:,.0f}", font=theme.font(11),
                         text_color=theme.TEXT_SECONDARY).pack(side="left", padx=(0, 20))
            ctk.CTkLabel(details, text=f"Spent: Rs. {s['spent']:,.0f}", font=theme.font(11),
                         text_color=theme.EXPENSE_RED).pack(side="left", padx=(0, 20))
            remaining_color = theme.INCOME_GREEN if s["remaining"] >= 0 else theme.EXPENSE_RED
            ctk.CTkLabel(details, text=f"Remaining: Rs. {s['remaining']:,.0f}", font=theme.font(11),
                         text_color=remaining_color).pack(side="left")

            if s["status"] == "Budget Exceeded":
                over = s["spent"] - s["budget"]
                ctk.CTkLabel(inner, text=f"⚠ {s['category']} budget exceeded by Rs. {over:,.0f}.",
                             font=theme.font(11, "bold"), text_color=theme.WARNING_ORANGE
                             ).pack(anchor="w", pady=(8, 0))

    def _bar_color(self, status):
        return {"Under Budget": theme.INCOME_GREEN, "Near Limit": theme.WARNING_ORANGE,
                "Budget Exceeded": theme.EXPENSE_RED, "No Budget": theme.TEXT_MUTED}[status]

    def _set_budget(self):
        try:
            budget_service.set_budget(self.app.current_user.id, self.category_var.get(),
                                       self.amount_entry.get(), self.month, self.year)
            self.error_label.configure(text="")
            self.amount_entry.delete(0, "end")
            self.refresh()
            show_toast(self.app.content_area, "Budget saved successfully!", "success")
        except BudgetValidationError as e:
            self.error_label.configure(text=str(e))

    def _delete_budget(self, budget_id):
        def do_delete():
            budget_service.delete_budget(budget_id, self.app.current_user.id)
            self.refresh()
            show_toast(self.app.content_area, "Budget removed.", "success")
        confirm_dialog(self.app, "Remove Budget", "Are you sure you want to remove this budget?", do_delete)

    def _prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.refresh()

    def _next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.refresh()
