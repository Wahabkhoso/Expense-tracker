"""
dashboard.py
Main dashboard screen: greeting, four summary cards, monthly
income-vs-expense chart, category donut chart, and recent transactions.
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui import theme
from ui.widgets import SummaryCard, SectionCard, SecondaryButton
from services import analytics_service, transaction_service
from charts import chart_generator


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self.canvases = []
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=28, pady=24)
        self.scroll = scroll

        # ---- Greeting ----
        self.greeting_label = ctk.CTkLabel(scroll, text="", font=theme.font(24, "bold"),
                                            text_color=theme.TEXT_PRIMARY, anchor="w")
        self.greeting_label.pack(fill="x")
        ctk.CTkLabel(scroll, text="Here's your financial overview", font=theme.font(13),
                     text_color=theme.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(0, 20))

        # ---- Summary Cards ----
        cards_row = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_row.grid_columnconfigure(i, weight=1, uniform="cards")

        self.balance_card = SummaryCard(cards_row, "Total Balance", "Rs. 0", theme.BALANCE_BLUE, "💰")
        self.income_card = SummaryCard(cards_row, "Total Income", "Rs. 0", theme.INCOME_GREEN, "📈")
        self.expense_card = SummaryCard(cards_row, "Total Expenses", "Rs. 0", theme.EXPENSE_RED, "📉")
        self.savings_card = SummaryCard(cards_row, "Savings Rate", "0%", theme.WARNING_ORANGE, "🏦")

        self.balance_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.income_card.grid(row=0, column=1, sticky="nsew", padx=8)
        self.expense_card.grid(row=0, column=2, sticky="nsew", padx=8)
        self.savings_card.grid(row=0, column=3, sticky="nsew", padx=(8, 0))

        # ---- Charts Row ----
        charts_row = ctk.CTkFrame(scroll, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 20))
        charts_row.grid_columnconfigure(0, weight=3)
        charts_row.grid_columnconfigure(1, weight=2)

        self.bar_chart_card = SectionCard(charts_row)
        self.bar_chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.bar_chart_holder = ctk.CTkFrame(self.bar_chart_card, fg_color="transparent")
        self.bar_chart_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self.pie_chart_card = SectionCard(charts_row)
        self.pie_chart_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.pie_chart_holder = ctk.CTkFrame(self.pie_chart_card, fg_color="transparent")
        self.pie_chart_holder.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- Recent Transactions ----
        self.recent_card = SectionCard(scroll, title="Recent Transactions")
        self.recent_card.pack(fill="x", pady=(0, 20))

        header_row = ctk.CTkFrame(self.recent_card, fg_color="transparent")
        header_row.pack(fill="x", padx=18)
        for text, w in [("Date", 90), ("Title", 200), ("Category", 130), ("Type", 90), ("Amount", 120)]:
            ctk.CTkLabel(header_row, text=text, font=theme.font(11, "bold"),
                         text_color=theme.TEXT_SECONDARY, width=w, anchor="w").pack(side="left")

        self.recent_rows_frame = ctk.CTkFrame(self.recent_card, fg_color="transparent")
        self.recent_rows_frame.pack(fill="x", padx=18, pady=(6, 10))

        SecondaryButton(self.recent_card, "View All Transactions",
                         command=lambda: self.app.navigate("Transactions")
                         ).pack(anchor="e", padx=18, pady=(0, 16))

    def refresh(self):
        user = self.app.current_user
        self.greeting_label.configure(text=f"Good {self._time_of_day()}, {user.full_name.split()[0]}")

        summary = analytics_service.get_summary(user.id)
        currency = user.currency + " " if user.currency != "PKR" else "Rs. "
        self.balance_card.update_value(f"{currency}{summary['total_savings']:,.0f}")
        self.income_card.update_value(f"{currency}{summary['total_income']:,.0f}")
        self.expense_card.update_value(f"{currency}{summary['total_expenses']:,.0f}")
        self.savings_card.update_value(f"{summary['savings_rate']:.1f}%")

        self._render_charts(user.id)
        self._render_recent_transactions(user.id, currency)

    def _time_of_day(self):
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            return "Morning"
        elif hour < 17:
            return "Afternoon"
        return "Evening"

    def _render_charts(self, user_id):
        for canvas in self.canvases:
            canvas.get_tk_widget().destroy()
        self.canvases.clear()

        monthly_data = analytics_service.get_monthly_income_vs_expense(user_id, 6)
        fig1 = chart_generator.create_income_vs_expense_chart(monthly_data)
        canvas1 = FigureCanvasTkAgg(fig1, master=self.bar_chart_holder)
        canvas1.draw_idle()
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        self.canvases.append(canvas1)

        category_data = analytics_service.get_category_wise_expenses(user_id)
        fig2 = chart_generator.create_category_pie_chart(category_data)
        canvas2 = FigureCanvasTkAgg(fig2, master=self.pie_chart_holder)
        canvas2.draw_idle()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        self.canvases.append(canvas2)

    def _render_recent_transactions(self, user_id, currency):
        for widget in self.recent_rows_frame.winfo_children():
            widget.destroy()

        transactions = transaction_service.get_recent_transactions(user_id, 8)
        if not transactions:
            ctk.CTkLabel(self.recent_rows_frame, text="No transactions yet. Add your first one!",
                         font=theme.font(12), text_color=theme.TEXT_MUTED).pack(anchor="w", pady=10)
            return

        for tx in transactions:
            row = ctk.CTkFrame(self.recent_rows_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=tx.date, font=theme.font(11), text_color=theme.TEXT_SECONDARY,
                         width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=tx.title, font=theme.font(12), text_color=theme.TEXT_PRIMARY,
                         width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=tx.category, font=theme.font(11), text_color=theme.TEXT_SECONDARY,
                         width=130, anchor="w").pack(side="left")
            color = theme.INCOME_GREEN if tx.type == "Income" else theme.EXPENSE_RED
            ctk.CTkLabel(row, text=tx.type, font=theme.font(11, "bold"), text_color=color,
                         width=90, anchor="w").pack(side="left")
            sign = "+" if tx.type == "Income" else "-"
            ctk.CTkLabel(row, text=f"{sign}{currency}{tx.amount:,.0f}", font=theme.font(12, "bold"),
                         text_color=color, width=120, anchor="w").pack(side="left")
