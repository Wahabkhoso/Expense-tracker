"""
analytics_service.py
All numerical analysis is performed here using Pandas. UI code must never
compute analytics directly - it should only call these functions.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List

import pandas as pd

from database.database import db


def _load_dataframe(user_id: int) -> pd.DataFrame:
    rows = db.fetch_all("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
    if not rows:
        return pd.DataFrame(columns=[
            "id", "user_id", "type", "title", "amount", "category",
            "date", "payment_method", "description", "created_at",
        ])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df


def get_date_range(preset: str, custom_start: str = None, custom_end: str = None
                    ) -> Tuple[Optional[str], Optional[str]]:
    """Returns (start_date, end_date) as ISO strings for a given preset."""
    today = datetime.now().date()

    if preset == "This Week":
        start = today - timedelta(days=today.weekday())
        return start.isoformat(), today.isoformat()
    elif preset == "This Month":
        start = today.replace(day=1)
        return start.isoformat(), today.isoformat()
    elif preset == "Last Month":
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return last_month_start.isoformat(), last_month_end.isoformat()
    elif preset == "This Year":
        start = today.replace(month=1, day=1)
        return start.isoformat(), today.isoformat()
    elif preset == "Custom Range":
        return custom_start, custom_end
    return None, None


def _filter_by_range(df: pd.DataFrame, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    if df.empty:
        return df
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]
    return df


def get_summary(user_id: int, start_date: str = None, end_date: str = None) -> Dict:
    """Total income, expenses, savings, savings rate for the (optionally filtered) period."""
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)

    total_income = df.loc[df["type"] == "Income", "amount"].sum() if not df.empty else 0.0
    total_expenses = df.loc[df["type"] == "Expense", "amount"].sum() if not df.empty else 0.0
    total_savings = total_income - total_expenses
    savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0.0

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "total_savings": float(total_savings),
        "savings_rate": float(savings_rate),
    }


def get_average_daily_expense(user_id: int, start_date: str = None, end_date: str = None) -> float:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return 0.0
    days = expenses["date"].dt.date.nunique()
    return float(expenses["amount"].sum() / days) if days > 0 else 0.0


def get_highest_expense(user_id: int, start_date: str = None, end_date: str = None) -> Dict:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return {"title": "N/A", "amount": 0.0, "category": "N/A", "date": "N/A"}
    row = expenses.loc[expenses["amount"].idxmax()]
    return {
        "title": row["title"],
        "amount": float(row["amount"]),
        "category": row["category"],
        "date": row["date"].strftime("%Y-%m-%d"),
    }


def get_top_spending_category(user_id: int, start_date: str = None, end_date: str = None) -> Dict:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return {"category": "N/A", "amount": 0.0}
    grouped = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
    return {"category": grouped.index[0], "amount": float(grouped.iloc[0])}


def get_category_wise_expenses(user_id: int, start_date: str = None, end_date: str = None
                                ) -> Dict[str, float]:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return {}
    grouped = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
    return grouped.to_dict()


def get_payment_method_analysis(user_id: int, start_date: str = None, end_date: str = None
                                 ) -> Dict[str, float]:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return {}
    grouped = expenses.groupby("payment_method")["amount"].sum().sort_values(ascending=False)
    return grouped.to_dict()


def get_monthly_income_vs_expense(user_id: int, num_months: int = 6) -> Dict[str, Dict[str, float]]:
    """Returns {'2026-01': {'income': X, 'expense': Y}, ...} for the last num_months."""
    df = _load_dataframe(user_id)
    result = {}
    today = datetime.now().date()

    months = []
    year, month = today.year, today.month
    for _ in range(num_months):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    months.reverse()

    if df.empty:
        for y, m in months:
            key = f"{y:04d}-{m:02d}"
            result[key] = {"income": 0.0, "expense": 0.0}
        return result

    df["year_month"] = df["date"].dt.strftime("%Y-%m")

    for y, m in months:
        key = f"{y:04d}-{m:02d}"
        month_df = df[df["year_month"] == key]
        income = month_df.loc[month_df["type"] == "Income", "amount"].sum()
        expense = month_df.loc[month_df["type"] == "Expense", "amount"].sum()
        result[key] = {"income": float(income), "expense": float(expense)}

    return result


def get_monthly_expense_trend(user_id: int, num_months: int = 6) -> Dict[str, float]:
    data = get_monthly_income_vs_expense(user_id, num_months)
    return {k: v["expense"] for k, v in data.items()}


def get_daily_spending_trend(user_id: int, start_date: str = None, end_date: str = None
                              ) -> Dict[str, float]:
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return {}
    grouped = expenses.groupby(expenses["date"].dt.strftime("%Y-%m-%d"))["amount"].sum()
    return grouped.sort_index().to_dict()


def get_transactions_dataframe(user_id: int, start_date: str = None, end_date: str = None
                                ) -> pd.DataFrame:
    """Exposed for reports (CSV/Excel/PDF) to consume a clean, filtered DataFrame."""
    df = _filter_by_range(_load_dataframe(user_id), start_date, end_date)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df
