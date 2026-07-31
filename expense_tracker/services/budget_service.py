"""
budget_service.py
Business logic for creating and tracking category budgets, including
spend-vs-budget status calculation used by the Budgets screen.
"""

from typing import List, Dict
from database.database import db
from models.budget import Budget


class BudgetValidationError(Exception):
    pass


def set_budget(user_id: int, category: str, amount, month: int, year: int) -> int:
    if not category:
        raise BudgetValidationError("Please select a category.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise BudgetValidationError("Budget amount must be a valid number.")
    if amount < 0:
        raise BudgetValidationError("Budget amount cannot be negative.")

    existing = db.fetch_one(
        "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND month = ? AND year = ?",
        (user_id, category, month, year),
    )
    if existing:
        db.execute("UPDATE budgets SET amount = ? WHERE id = ?", (amount, existing["id"]))
        return existing["id"]
    else:
        return db.execute(
            "INSERT INTO budgets (user_id, category, amount, month, year) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, amount, month, year),
        )


def delete_budget(budget_id: int, user_id: int) -> None:
    db.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user_id))


def get_budgets_for_month(user_id: int, month: int, year: int) -> List[Budget]:
    rows = db.fetch_all(
        "SELECT * FROM budgets WHERE user_id = ? AND month = ? AND year = ? ORDER BY category",
        (user_id, month, year),
    )
    return [Budget.from_row(r) for r in rows]


def get_budget_status(user_id: int, month: int, year: int) -> List[Dict]:
    """Returns a list of dicts: category, budget, spent, remaining, status."""
    budgets = get_budgets_for_month(user_id, month, year)
    results = []
    month_str = f"{year:04d}-{month:02d}"

    for b in budgets:
        row = db.fetch_one(
            """SELECT COALESCE(SUM(amount), 0) as spent FROM transactions
               WHERE user_id = ? AND type = 'Expense' AND category = ?
               AND substr(date, 1, 7) = ?""",
            (user_id, b.category, month_str),
        )
        spent = row["spent"] if row else 0.0
        remaining = b.amount - spent

        if b.amount == 0:
            status = "No Budget"
        elif spent >= b.amount:
            status = "Budget Exceeded"
        elif spent >= b.amount * 0.8:
            status = "Near Limit"
        else:
            status = "Under Budget"

        results.append({
            "id": b.id,
            "category": b.category,
            "budget": b.amount,
            "spent": spent,
            "remaining": remaining,
            "status": status,
            "percent": min(100, (spent / b.amount * 100) if b.amount > 0 else 0),
        })

    return results
