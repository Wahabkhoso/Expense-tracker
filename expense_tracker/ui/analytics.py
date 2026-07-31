"""
analytics.py
Dedicated analytics dashboard: date-range selector, key metric cards,
and five charts driven entirely by services/analytics_service.py.
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui import theme
from ui.widgets import SummaryCard, SectionCard, SecondaryButton
from services import analytics_service
from charts import chart_generator

PRESETS = ["This Week", "This Month", "Last Month", "This Year", "Custom Range"]


class AnalyticsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self.canvases = []
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=28, pady=24)

        top_row = ctk.CTkFrame(scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(top_row, text="Analytics", font=theme.font(22, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")

        # ---- Date range selector ----
        range_row = ctk.CTkFrame(scroll, fg_color="transparent")
        range_row.pack(fill="x", pady=(14, 16))
        self.preset_var = ctk.StringVar(value="This Month")
        ctk.CTkOptionMenu(range_row, variable=self.preset_var, values=PRESETS,
                          command=lambda v: self._on_preset_change(), width=160, height=36,
                          fg_color=theme.CARD_BG, button_color=theme.ACCENT).pack(side="left", padx=(0, 10))
        self.custom_start = ctk.CTkEntry(range_row, placeholder_text="Start (YYYY-MM-DD)",
                                          width=150, height=36, fg_color=theme.CARD_BG)
        self.custom_end = ctk.CTkEntry(range_row, placeholder_text="End (YYYY-MM-DD)",
                                        width=150, height=36, fg_color=theme.CARD_BG)
        SecondaryButton(range_row, "Apply", command=self.refresh, width=90, height=36).pack(side="left", padx=10)

        # ---- Metric cards ----
        cards_row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_row1.pack(fill="x", pady=(0, 12))
        for i in range(3):
            cards_row1.grid_columnconfigure(i, weight=1, uniform="a")
        self.income_card = SummaryCard(cards_row1, "Total Income", "Rs. 0", theme.INCOME_GREEN, "📈")
        self.expense_card = SummaryCard(cards_row1, "Total Expenses", "Rs. 0", theme.EXPENSE_RED, "📉")
        self.savings_card = SummaryCard(cards_row1, "Total Savings", "Rs. 0", theme.BALANCE_BLUE, "🏦")
        self.income_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.expense_card.grid(row=0, column=1, sticky="nsew", padx=8)
        self.savings_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        cards_row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_row2.pack(fill="x", pady=(0, 20))
        for i in range(3):
            cards_row2.grid_columnconfigure(i, weight=1, uniform="b")
        self.avg_expense_card = SummaryCard(cards_row2, "Average Daily Expense", "Rs. 0", theme.WARNING_ORANGE, "📊")
        self.highest_card = SummaryCard(cards_row2, "Highest Expense", "Rs. 0", theme.EXPENSE_RED, "⚡")
        self.top_category_card = SummaryCard(cards_row2, "Top Spending Category", "N/A", theme.ACCENT, "🏷")
        self.avg_expense_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.highest_card.grid(row=0, column=1, sticky="nsew", padx=8)
        self.top_category_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # ---- Charts ----
        row_a = ctk.CTkFrame(scroll, fg_color="transparent")
        row_a.pack(fill="x", pady=(0, 16))
        row_a.grid_columnconfigure(0, weight=1)
        row_a.grid_columnconfigure(1, weight=1)
        self.trend_card = SectionCard(row_a)
        self.trend_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.trend_holder = ctk.CTkFrame(self.trend_card, fg_color="transparent")
        self.trend_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self.income_expense_card = SectionCard(row_a)
        self.income_expense_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.income_expense_holder = ctk.CTkFrame(self.income_expense_card, fg_color="transparent")
        self.income_expense_holder.pack(fill="both", expand=True, padx=10, pady=10)

        row_b = ctk.CTkFrame(scroll, fg_color="transparent")
        row_b.pack(fill="x", pady=(0, 16))
        row_b.grid_columnconfigure(0, weight=1)
        row_b.grid_columnconfigure(1, weight=1)
        self.category_card = SectionCard(row_b)
        self.category_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.category_holder = ctk.CTkFrame(self.category_card, fg_color="transparent")
        self.category_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self.payment_card = SectionCard(row_b)
        self.payment_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.payment_holder = ctk.CTkFrame(self.payment_card, fg_color="transparent")
        self.payment_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self.daily_card = SectionCard(scroll)
        self.daily_card.pack(fill="x", pady=(0, 20))
        self.daily_holder = ctk.CTkFrame(self.daily_card, fg_color="transparent")
        self.daily_holder.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_preset_change(self):
        if self.preset_var.get() == "Custom Range":
            self.custom_start.pack(side="left", padx=(0, 6))
            self.custom_end.pack(side="left", padx=(0, 6))
        else:
            self.custom_start.pack_forget()
            self.custom_end.pack_forget()
        self.refresh()

    def refresh(self):
        user_id = self.app.current_user.id
        currency = "Rs. "
        start_date, end_date = analytics_service.get_date_range(
            self.preset_var.get(), self.custom_start.get() or None, self.custom_end.get() or None
        )

        summary = analytics_service.get_summary(user_id, start_date, end_date)
        self.income_card.update_value(f"{currency}{summary['total_income']:,.0f}")
        self.expense_card.update_value(f"{currency}{summary['total_expenses']:,.0f}")
        self.savings_card.update_value(f"{currency}{summary['total_savings']:,.0f}")

        avg_expense = analytics_service.get_average_daily_expense(user_id, start_date, end_date)
        self.avg_expense_card.update_value(f"{currency}{avg_expense:,.0f}")

        highest = analytics_service.get_highest_expense(user_id, start_date, end_date)
        self.highest_card.update_value(f"{currency}{highest['amount']:,.0f}")

        top_cat = analytics_service.get_top_spending_category(user_id, start_date, end_date)
        self.top_category_card.update_value(top_cat["category"])

        self._render_charts(user_id, start_date, end_date)

    def _render_charts(self, user_id, start_date, end_date):
        for canvas in self.canvases:
            canvas.get_tk_widget().destroy()
        self.canvases.clear()

        def embed(fig, holder):
            canvas = FigureCanvasTkAgg(fig, master=holder)
            canvas.draw_idle()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvases.append(canvas)

        trend = analytics_service.get_monthly_expense_trend(user_id, 6)
        embed(chart_generator.create_line_trend_chart(trend, "Monthly Expense Trend"), self.trend_holder)

        monthly = analytics_service.get_monthly_income_vs_expense(user_id, 6)
        embed(chart_generator.create_income_vs_expense_chart(monthly), self.income_expense_holder)

        categories = analytics_service.get_category_wise_expenses(user_id, start_date, end_date)
        embed(chart_generator.create_category_pie_chart(categories), self.category_holder)

        payment_data = analytics_service.get_payment_method_analysis(user_id, start_date, end_date)
        embed(chart_generator.create_bar_chart(payment_data, "Payment Method Analysis",
                                                 theme.BALANCE_BLUE), self.payment_holder)

        daily = analytics_service.get_daily_spending_trend(user_id, start_date, end_date)
        embed(chart_generator.create_line_trend_chart(daily, "Daily Spending Trend",
                                                         theme.WARNING_ORANGE, figsize=(12, 3)),
              self.daily_holder)
