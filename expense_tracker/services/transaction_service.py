"""
transaction_service.py
Business logic and validation for creating, reading, updating,
and deleting transactions. All SQL is parameterized.
"""

from datetime import datetime
from typing import Optional, List

from database.database import db
from models.transaction import Transaction

VALID_TYPES = {"Income", "Expense"}
VALID_PAYMENT_METHODS = {"Cash", "Bank", "Credit Card", "Debit Card", "Mobile Wallet"}


class ValidationError(Exception):
    pass


def _validate(type_: str, title: str, amount, category: str, date_str: str,
              payment_method: str):
    if type_ not in VALID_TYPES:
        raise ValidationError("Transaction type must be Income or Expense.")
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValidationError("Amount must be a valid number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if not category or not category.strip():
        raise ValidationError("Please select a category.")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValidationError("Date must be a valid date in YYYY-MM-DD format.")
    if payment_method not in VALID_PAYMENT_METHODS:
        raise ValidationError("Please select a valid payment method.")
    return amount


def add_transaction(user_id: int, type_: str, title: str, amount, category: str,
                     date_str: str, payment_method: str, description: str = "") -> int:
    amount = _validate(type_, title, amount, category, date_str, payment_method)
    created_at = datetime.now().isoformat()
    return db.execute(
        """INSERT INTO transactions
           (user_id, type, title, amount, category, date, payment_method, description, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, type_, title.strip(), amount, category, date_str, payment_method,
         (description or "").strip(), created_at),
    )


def update_transaction(transaction_id: int, user_id: int, type_: str, title: str, amount,
                        category: str, date_str: str, payment_method: str,
                        description: str = "") -> None:
    amount = _validate(type_, title, amount, category, date_str, payment_method)
    existing = db.fetch_one(
        "SELECT id FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)
    )
    if not existing:
        raise ValidationError("Transaction not found.")
    db.execute(
        """UPDATE transactions SET type = ?, title = ?, amount = ?, category = ?,
           date = ?, payment_method = ?, description = ? WHERE id = ? AND user_id = ?""",
        (type_, title.strip(), amount, category, date_str, payment_method,
         (description or "").strip(), transaction_id, user_id),
    )


def delete_transaction(transaction_id: int, user_id: int) -> None:
    db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)
    )


def get_transaction(transaction_id: int, user_id: int) -> Optional[Transaction]:
    row = db.fetch_one(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)
    )
    return Transaction.from_row(row) if row else None


def get_all_transactions(user_id: int) -> List[Transaction]:
    rows = db.fetch_all(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC", (user_id,)
    )
    return [Transaction.from_row(r) for r in rows]


def search_transactions(user_id: int, keyword: str = "", type_filter: str = "All",
                         category_filter: str = "All", start_date: str = None,
                         end_date: str = None) -> List[Transaction]:
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if keyword:
        query += " AND (title LIKE ? OR description LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like])

    if type_filter and type_filter != "All":
        query += " AND type = ?"
        params.append(type_filter)

    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC, id DESC"
    rows = db.fetch_all(query, tuple(params))
    return [Transaction.from_row(r) for r in rows]


def get_recent_transactions(user_id: int, limit: int = 8) -> List[Transaction]:
    rows = db.fetch_all(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit),
    )
    return [Transaction.from_row(r) for r in rows]


def get_all_categories() -> List[str]:
    rows = db.fetch_all("SELECT name FROM categories ORDER BY name ASC")
    return [r["name"] for r in rows]


def get_categories_by_type(type_: str) -> List[str]:
    db_type = "income" if type_ == "Income" else "expense"
    rows = db.fetch_all("SELECT name FROM categories WHERE type = ? ORDER BY name ASC", (db_type,))
    return [r["name"] for r in rows]
