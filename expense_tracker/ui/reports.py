"""
reports.py
Reports screen: choose a report type and date range, then export to
CSV, Excel, or PDF via the reports/ modules.
"""

import os
from tkinter import filedialog

import customtkinter as ctk

from ui import theme
from ui.widgets import SectionCard, PrimaryButton, SecondaryButton, show_toast
from services import analytics_service
from reports import csv_report, excel_report, pdf_report

REPORT_TYPES = ["Complete Financial Summary", "Monthly Expense Report",
                "Monthly Income Report", "Category-wise Expense Report"]
PRESETS = ["This Month", "Last Month", "This Year", "All Time", "Custom Range"]


class ReportsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrapper, text="Reports", font=theme.font(22, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(wrapper, text="Generate and export financial reports", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 18))

        card = SectionCard(wrapper, title="Generate Report")
        card.pack(fill="x", pady=(0, 16))
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=18, pady=(0, 18))

        ctk.CTkLabel(form, text="Report Type", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.report_type_var = ctk.StringVar(value=REPORT_TYPES[0])
        ctk.CTkOptionMenu(form, variable=self.report_type_var, values=REPORT_TYPES, width=260,
                          height=38, fg_color=theme.BG_DARK, button_color=theme.ACCENT
                          ).grid(row=1, column=0, sticky="w", pady=(4, 14))

        ctk.CTkLabel(form, text="Date Range", font=theme.font(12),
                     text_color=theme.TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=(20, 0))
        self.preset_var = ctk.StringVar(value="This Month")
        ctk.CTkOptionMenu(form, variable=self.preset_var, values=PRESETS,
                          command=lambda v: self._toggle_custom(), width=200,
                          height=38, fg_color=theme.BG_DARK, button_color=theme.ACCENT
                          ).grid(row=1, column=1, sticky="w", padx=(20, 0), pady=(4, 14))

        self.custom_start = ctk.CTkEntry(form, placeholder_text="Start (YYYY-MM-DD)", width=150,
                                          height=38, fg_color=theme.BG_DARK)
        self.custom_end = ctk.CTkEntry(form, placeholder_text="End (YYYY-MM-DD)", width=150,
                                        height=38, fg_color=theme.BG_DARK)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 18))
        PrimaryButton(btn_row, "Export to CSV", command=lambda: self._export("csv"), width=150).pack(side="left", padx=(0, 10))
        PrimaryButton(btn_row, "Export to Excel", command=lambda: self._export("excel"), width=150,
                      fg_color=theme.INCOME_GREEN, hover_color="#27ae60").pack(side="left", padx=(0, 10))
        PrimaryButton(btn_row, "Export to PDF", command=lambda: self._export("pdf"), width=150,
                      fg_color=theme.EXPENSE_RED, hover_color="#c0392b").pack(side="left")

        self.status_label = ctk.CTkLabel(wrapper, text="", font=theme.font(12), text_color=theme.TEXT_SECONDARY)
        self.status_label.pack(anchor="w", pady=(4, 0))

        # ---- Live preview card ----
        self.preview_card = SectionCard(wrapper, title="Report Preview")
        self.preview_card.pack(fill="both", expand=True, pady=(16, 0))
        self.preview_frame = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.preview_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    def _toggle_custom(self):
        if self.preset_var.get() == "Custom Range":
            self.custom_start.grid(row=1, column=2, sticky="w", padx=(20, 6), pady=(4, 14))
            self.custom_end.grid(row=1, column=3, sticky="w", pady=(4, 14))
        else:
            self.custom_start.grid_forget()
            self.custom_end.grid_forget()

    def _resolve_range(self):
        preset = self.preset_var.get()
        if preset == "All Time":
            return None, None
        if preset == "Custom Range":
            return self.custom_start.get() or None, self.custom_end.get() or None
        return analytics_service.get_date_range(preset)

    def refresh(self):
        self._render_preview()

    def _render_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        start_date, end_date = self._resolve_range()
        user_id = self.app.current_user.id
        summary = analytics_service.get_summary(user_id, start_date, end_date)

        rows = [
            ("Total Income", f"Rs. {summary['total_income']:,.2f}", theme.INCOME_GREEN),
            ("Total Expenses", f"Rs. {summary['total_expenses']:,.2f}", theme.EXPENSE_RED),
            ("Total Savings", f"Rs. {summary['total_savings']:,.2f}", theme.BALANCE_BLUE),
            ("Savings Rate", f"{summary['savings_rate']:.1f}%", theme.WARNING_ORANGE),
        ]
        for label, value, color in rows:
            row = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, font=theme.font(12), text_color=theme.TEXT_SECONDARY,
                         width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=theme.font(13, "bold"), text_color=color,
                         anchor="w").pack(side="left")

    def _export(self, fmt):
        start_date, end_date = self._resolve_range()
        user_id = self.app.current_user.id
        report_title = self.report_type_var.get()

        ext_map = {"csv": ".csv", "excel": ".xlsx", "pdf": ".pdf"}
        default_name = report_title.replace(" ", "_") + ext_map[fmt]

        filepath = filedialog.asksaveasfilename(
            defaultextension=ext_map[fmt],
            initialfile=default_name,
            filetypes=[(fmt.upper(), f"*{ext_map[fmt]}")],
        )
        if not filepath:
            return

        try:
            if fmt == "csv":
                csv_report.export_transactions_csv(user_id, filepath, start_date, end_date)
            elif fmt == "excel":
                excel_report.export_financial_report(user_id, filepath, start_date, end_date)
            elif fmt == "pdf":
                pdf_report.export_pdf_report(user_id, filepath, report_title, start_date, end_date)

            self.status_label.configure(text=f"Report saved to: {filepath}", text_color=theme.INCOME_GREEN)
            show_toast(self.app.content_area, f"{fmt.upper()} report exported successfully!", "success")
        except Exception as e:
            self.status_label.configure(text=f"Export failed: {e}", text_color=theme.EXPENSE_RED)
            show_toast(self.app.content_area, "Export failed. See status message.", "error")
