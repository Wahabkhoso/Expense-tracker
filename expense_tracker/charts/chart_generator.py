"""
chart_generator.py
Reusable Matplotlib chart-building functions. Each function returns a
matplotlib.figure.Figure that the UI layer embeds using FigureCanvasTkAgg.
No chart here ever uses hardcoded/static data - callers must supply
real data retrieved from analytics_service.
"""

import matplotlib
matplotlib.use("Agg")  # backend is swapped by the UI layer via FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ---- Theme constants (kept in sync with ui/theme.py) ----
BG_COLOR = "#1e1e2d"
CARD_COLOR = "#252537"
TEXT_COLOR = "#e4e4ef"
GRID_COLOR = "#3a3a4d"
INCOME_COLOR = "#2ecc71"
EXPENSE_COLOR = "#e74c3c"
BALANCE_COLOR = "#3498db"
WARNING_COLOR = "#f39c12"

CATEGORY_PALETTE = [
    "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#95a5a6", "#f1c40f",
]


def _style_axes(ax, fig):
    fig.patch.set_facecolor(CARD_COLOR)
    ax.set_facecolor(CARD_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.5)


def create_income_vs_expense_chart(monthly_data: dict, figsize=(6, 3.4)) -> Figure:
    """monthly_data: {'2026-01': {'income': X, 'expense': Y}, ...}"""
    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)

    months = list(monthly_data.keys())
    labels = [m[5:] + "/" + m[2:4] for m in months]
    income_vals = [monthly_data[m]["income"] for m in months]
    expense_vals = [monthly_data[m]["expense"] for m in months]

    import numpy as np
    x = np.arange(len(months))
    width = 0.35

    ax.bar(x - width / 2, income_vals, width, label="Income", color=INCOME_COLOR)
    ax.bar(x + width / 2, expense_vals, width, label="Expenses", color=EXPENSE_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Monthly Income vs Expense", fontsize=10, fontweight="bold")
    legend = ax.legend(facecolor=CARD_COLOR, edgecolor=GRID_COLOR, fontsize=8)
    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)

    _style_axes(ax, fig)
    fig.tight_layout()
    return fig


def create_category_pie_chart(category_data: dict, figsize=(5, 3.4)) -> Figure:
    """category_data: {'Food': 1500.0, 'Transport': 300.0, ...}"""
    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor(CARD_COLOR)

    if not category_data:
        ax.text(0.5, 0.5, "No expense data yet", ha="center", va="center",
                 color=TEXT_COLOR, fontsize=10)
        ax.axis("off")
        return fig

    labels = list(category_data.keys())
    values = list(category_data.values())
    colors = [CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i in range(len(labels))]

    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%", startangle=90, colors=colors,
        pctdistance=0.8, wedgeprops={"width": 0.4, "edgecolor": CARD_COLOR},
    )
    for at in autotexts:
        at.set_color(TEXT_COLOR)
        at.set_fontsize(8)

    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5),
              fontsize=7, facecolor=CARD_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR)
    ax.set_title("Expense by Category", fontsize=10, fontweight="bold", color=TEXT_COLOR)
    fig.tight_layout()
    return fig


def create_line_trend_chart(series_data: dict, title: str, color=EXPENSE_COLOR,
                             figsize=(6, 3.2)) -> Figure:
    """series_data: {'2026-01': 500.0, ...} ordered dict of label -> value"""
    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)

    if not series_data:
        fig.patch.set_facecolor(CARD_COLOR)
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                 color=TEXT_COLOR, fontsize=10)
        ax.axis("off")
        return fig

    labels = list(series_data.keys())
    values = list(series_data.values())

    ax.plot(labels, values, marker="o", color=color, linewidth=2, markersize=4)
    ax.fill_between(range(len(labels)), values, color=color, alpha=0.15)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)

    _style_axes(ax, fig)
    fig.tight_layout()
    return fig


def create_bar_chart(data: dict, title: str, color=BALANCE_COLOR, figsize=(6, 3.2)) -> Figure:
    """Generic horizontal bar chart, e.g. for payment method analysis."""
    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)

    if not data:
        fig.patch.set_facecolor(CARD_COLOR)
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                 color=TEXT_COLOR, fontsize=10)
        ax.axis("off")
        return fig

    labels = list(data.keys())
    values = list(data.values())

    ax.barh(labels, values, color=color)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.invert_yaxis()

    _style_axes(ax, fig)
    fig.tight_layout()
    return fig
