"""
transactions.py
Full transaction management screen: search, type/category filters,
date range filter, table view with edit/delete/view-details actions.
"""

import customtkinter as ctk

from ui import theme
from ui.widgets import SectionCard, PrimaryButton, SecondaryButton, DangerButton, confirm_dialog, show_toast
from services import transaction_service


class TransactionsScreen(ctk.CTkFrame):
    PAGE_SIZE = 12

    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self.page = 0
        self.filtered_transactions = []
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=28, pady=24)

        top_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(top_row, text="Transactions", font=theme.font(22, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(side="left")
        PrimaryButton(top_row, "+ Add Transaction",
                      command=lambda: self.app.navigate("Add Transaction"), width=170
                      ).pack(side="right")

        # ---- Filters ----
        filters_card = SectionCard(wrapper)
        filters_card.pack(fill="x", pady=(16, 16))
        filters_row = ctk.CTkFrame(filters_card, fg_color="transparent")
        filters_row.pack(fill="x", padx=18, pady=16)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(filters_row, placeholder_text="Search transactions...",
                                     textvariable=self.search_var, width=220, height=36,
                                     fg_color=theme.BG_DARK)
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        self.type_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filters_row, variable=self.type_var, values=["All", "Income", "Expense"],
                          command=lambda v: self._apply_filters(), width=110, height=36,
                          fg_color=theme.BG_DARK, button_color=theme.ACCENT).pack(side="left", padx=(0, 10))

        categories = ["All"] + transaction_service.get_all_categories()
        self.category_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filters_row, variable=self.category_var, values=categories,
                          command=lambda v: self._apply_filters(), width=140, height=36,
                          fg_color=theme.BG_DARK, button_color=theme.ACCENT).pack(side="left", padx=(0, 10))

        self.start_date_entry = ctk.CTkEntry(filters_row, placeholder_text="Start (YYYY-MM-DD)",
                                              width=150, height=36, fg_color=theme.BG_DARK)
        self.start_date_entry.pack(side="left", padx=(0, 6))
        self.end_date_entry = ctk.CTkEntry(filters_row, placeholder_text="End (YYYY-MM-DD)",
                                            width=150, height=36, fg_color=theme.BG_DARK)
        self.end_date_entry.pack(side="left", padx=(0, 6))
        SecondaryButton(filters_row, "Filter", command=self._apply_filters, width=80,
                         height=36).pack(side="left")

        # ---- Table ----
        table_card = SectionCard(wrapper)
        table_card.pack(fill="both", expand=True)

        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_DARK)
        header_row.pack(fill="x", padx=16, pady=(16, 0))
        headers = [("ID", 50), ("Date", 90), ("Title", 170), ("Category", 110),
                   ("Type", 80), ("Method", 110), ("Amount", 110), ("Actions", 160)]
        for text, w in headers:
            ctk.CTkLabel(header_row, text=text, font=theme.font(11, "bold"),
                         text_color=theme.TEXT_SECONDARY, width=w, anchor="w").pack(side="left", padx=2, pady=8)

        self.rows_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=16, pady=(4, 8))

        pagination_row = ctk.CTkFrame(table_card, fg_color="transparent")
        pagination_row.pack(fill="x", padx=16, pady=(0, 16))
        SecondaryButton(pagination_row, "◀ Prev", command=self._prev_page, width=90, height=32).pack(side="left")
        self.page_label = ctk.CTkLabel(pagination_row, text="Page 1", font=theme.font(11),
                                        text_color=theme.TEXT_SECONDARY)
        self.page_label.pack(side="left", padx=14)
        SecondaryButton(pagination_row, "Next ▶", command=self._next_page, width=90, height=32).pack(side="left")

    def refresh(self):
        categories = ["All"] + transaction_service.get_all_categories()
        self._apply_filters(categories=categories)

    def _apply_filters(self, categories=None):
        user_id = self.app.current_user.id
        self.filtered_transactions = transaction_service.search_transactions(
            user_id,
            keyword=self.search_var.get().strip(),
            type_filter=self.type_var.get(),
            category_filter=self.category_var.get(),
            start_date=self.start_date_entry.get().strip() or None,
            end_date=self.end_date_entry.get().strip() or None,
        )
        self.page = 0
        self._render_page()

    def _render_page(self):
        for widget in self.rows_scroll.winfo_children():
            widget.destroy()

        currency = "Rs. "
        start = self.page * self.PAGE_SIZE
        page_items = self.filtered_transactions[start:start + self.PAGE_SIZE]
        total_pages = max(1, (len(self.filtered_transactions) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page_label.configure(text=f"Page {self.page + 1} of {total_pages}  ({len(self.filtered_transactions)} results)")

        if not page_items:
            ctk.CTkLabel(self.rows_scroll, text="No transactions found.", font=theme.font(12),
                         text_color=theme.TEXT_MUTED).pack(pady=20)
            return

        for tx in page_items:
            row = ctk.CTkFrame(self.rows_scroll, fg_color=theme.CARD_BG_HOVER, corner_radius=8)
            row.pack(fill="x", pady=3)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=6, pady=6)

            ctk.CTkLabel(inner, text=str(tx.id), font=theme.font(11), width=50,
                         text_color=theme.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(inner, text=tx.date, font=theme.font(11), width=90,
                         text_color=theme.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(inner, text=tx.title, font=theme.font(12), width=170,
                         text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left")
            ctk.CTkLabel(inner, text=tx.category, font=theme.font(11), width=110,
                         text_color=theme.TEXT_SECONDARY, anchor="w").pack(side="left")
            color = theme.INCOME_GREEN if tx.type == "Income" else theme.EXPENSE_RED
            ctk.CTkLabel(inner, text=tx.type, font=theme.font(11, "bold"), width=80,
                         text_color=color, anchor="w").pack(side="left")
            ctk.CTkLabel(inner, text=tx.payment_method, font=theme.font(11), width=110,
                         text_color=theme.TEXT_SECONDARY, anchor="w").pack(side="left")
            sign = "+" if tx.type == "Income" else "-"
            ctk.CTkLabel(inner, text=f"{sign}{currency}{tx.amount:,.0f}", font=theme.font(12, "bold"),
                         width=110, text_color=color, anchor="w").pack(side="left")

            actions = ctk.CTkFrame(inner, fg_color="transparent", width=160)
            actions.pack(side="left")
            ctk.CTkButton(actions, text="Edit", width=55, height=26, font=theme.font(11),
                          fg_color=theme.BALANCE_BLUE, hover_color="#2980b9",
                          command=lambda t=tx: self._edit(t)).pack(side="left", padx=2)
            DangerButton(actions, "Delete", width=60, height=26,
                         command=lambda t=tx: self._delete(t)).pack(side="left", padx=2)

    def _edit(self, transaction):
        self.app.navigate("Add Transaction")
        self.app.screens["Add Transaction"].load_for_edit(transaction)

    def _delete(self, transaction):
        def do_delete():
            transaction_service.delete_transaction(transaction.id, self.app.current_user.id)
            self.app.refresh_all_screens()
            show_toast(self.app.content_area, "Transaction deleted.", "success")

        confirm_dialog(self.app, "Delete Transaction",
                        f"Are you sure you want to delete '{transaction.title}'? This cannot be undone.",
                        do_delete)

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._render_page()

    def _next_page(self):
        total_pages = max(1, (len(self.filtered_transactions) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.page < total_pages - 1:
            self.page += 1
            self._render_page()
