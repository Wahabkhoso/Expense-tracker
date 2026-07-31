"""
add_transaction.py
Form screen for creating a new transaction (and reused for editing,
via edit_transaction_id). Performs client-side validation before
calling the transaction_service, which re-validates server-side.
"""

from datetime import date

import customtkinter as ctk

from ui import theme
from ui.widgets import SectionCard, PrimaryButton, SecondaryButton, show_toast
from services import transaction_service
from services.transaction_service import ValidationError

PAYMENT_METHODS = ["Cash", "Bank", "Credit Card", "Debit Card", "Mobile Wallet"]


class AddTransactionScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self.edit_transaction_id = None
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=28, pady=24)

        self.header_label = ctk.CTkLabel(wrapper, text="Add Transaction", font=theme.font(22, "bold"),
                                          text_color=theme.TEXT_PRIMARY, anchor="w")
        self.header_label.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(wrapper, text="Record a new income or expense entry", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(0, 18))

        card = SectionCard(wrapper)
        card.pack(fill="both", expand=True)
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=26)

        # ---- Transaction Type ----
        ctk.CTkLabel(form, text="Transaction Type", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.type_var = ctk.StringVar(value="Expense")
        type_row = ctk.CTkFrame(form, fg_color="transparent")
        type_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))
        ctk.CTkRadioButton(type_row, text="Income", variable=self.type_var, value="Income",
                           fg_color=theme.INCOME_GREEN, command=self._on_type_change).pack(side="left", padx=(0, 24))
        ctk.CTkRadioButton(type_row, text="Expense", variable=self.type_var, value="Expense",
                           fg_color=theme.EXPENSE_RED, command=self._on_type_change).pack(side="left")

        # ---- Title / Amount ----
        self.title_entry = self._labeled_entry(form, "Title", row=2, col=0, placeholder="e.g. Grocery shopping")
        self.amount_entry = self._labeled_entry(form, "Amount", row=2, col=1, placeholder="e.g. 2500")

        # ---- Category / Date ----
        ctk.CTkLabel(form, text="Category", font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                     anchor="w").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(form, variable=self.category_var,
                                                 values=transaction_service.get_categories_by_type("Expense"),
                                                 width=280, height=38, fg_color=theme.BG_DARK,
                                                 button_color=theme.ACCENT, button_hover_color=theme.ACCENT_HOVER)
        self.category_menu.grid(row=5, column=0, sticky="w", pady=(0, 16))

        self.date_entry = self._labeled_entry(form, "Date (YYYY-MM-DD)", row=4, col=1,
                                               placeholder=date.today().isoformat())
        self.date_entry.insert(0, date.today().isoformat())

        # ---- Payment Method ----
        ctk.CTkLabel(form, text="Payment Method", font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                     anchor="w").grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.payment_var = ctk.StringVar(value=PAYMENT_METHODS[0])
        self.payment_menu = ctk.CTkOptionMenu(form, variable=self.payment_var, values=PAYMENT_METHODS,
                                               width=280, height=38, fg_color=theme.BG_DARK,
                                               button_color=theme.ACCENT, button_hover_color=theme.ACCENT_HOVER)
        self.payment_menu.grid(row=7, column=0, sticky="w", pady=(0, 16))

        # ---- Description ----
        ctk.CTkLabel(form, text="Description (optional)", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY, anchor="w").grid(row=8, column=0, columnspan=2,
                                                                         sticky="w", pady=(0, 4))
        self.description_text = ctk.CTkTextbox(form, height=70, width=580, fg_color=theme.BG_DARK)
        self.description_text.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.error_label = ctk.CTkLabel(form, text="", font=theme.font(11), text_color=theme.EXPENSE_RED)
        self.error_label.grid(row=10, column=0, columnspan=2, sticky="w", pady=(4, 10))

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=11, column=0, columnspan=2, sticky="w")
        self.submit_btn = PrimaryButton(btn_row, "Add Transaction", command=self._submit, width=180)
        self.submit_btn.pack(side="left", padx=(0, 10))
        SecondaryButton(btn_row, "Clear Form", command=self._clear_form, width=140).pack(side="left")

    def _labeled_entry(self, parent, label, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                     anchor="w").grid(row=row, column=col, sticky="w", padx=(0 if col == 0 else 20, 0), pady=(0, 4))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=280, height=38, fg_color=theme.BG_DARK)
        entry.grid(row=row + 1, column=col, sticky="w", padx=(0 if col == 0 else 20, 0), pady=(0, 16))
        return entry

    def _on_type_change(self):
        cats = transaction_service.get_categories_by_type(self.type_var.get())
        self.category_menu.configure(values=cats)
        if cats:
            self.category_var.set(cats[0])

    def _clear_form(self):
        self.title_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())
        self.description_text.delete("1.0", "end")
        self.type_var.set("Expense")
        self._on_type_change()
        self.payment_var.set(PAYMENT_METHODS[0])
        self.error_label.configure(text="")
        self.edit_transaction_id = None
        self.header_label.configure(text="Add Transaction")
        self.submit_btn.configure(text="Add Transaction")

    def load_for_edit(self, transaction):
        self.edit_transaction_id = transaction.id
        self.header_label.configure(text="Edit Transaction")
        self.submit_btn.configure(text="Save Changes")
        self.type_var.set(transaction.type)
        self._on_type_change()
        self.category_var.set(transaction.category)
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, transaction.title)
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(transaction.amount))
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, transaction.date)
        self.payment_var.set(transaction.payment_method)
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", transaction.description)

    def _submit(self):
        user_id = self.app.current_user.id
        try:
            if self.edit_transaction_id:
                transaction_service.update_transaction(
                    self.edit_transaction_id, user_id, self.type_var.get(),
                    self.title_entry.get(), self.amount_entry.get(), self.category_var.get(),
                    self.date_entry.get(), self.payment_var.get(),
                    self.description_text.get("1.0", "end").strip(),
                )
                msg = "Transaction updated successfully!"
            else:
                transaction_service.add_transaction(
                    user_id, self.type_var.get(), self.title_entry.get(), self.amount_entry.get(),
                    self.category_var.get(), self.date_entry.get(), self.payment_var.get(),
                    self.description_text.get("1.0", "end").strip(),
                )
                msg = "Transaction added successfully!"

            self.error_label.configure(text="")
            self._clear_form()
            self.app.refresh_all_screens()
            show_toast(self.app.content_area, msg, "success")
            self.app.navigate("Dashboard")
        except ValidationError as e:
            self.error_label.configure(text=str(e))
