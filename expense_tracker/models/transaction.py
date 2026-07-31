"""
transaction.py
Data model representing a single income/expense transaction.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    id: Optional[int]
    user_id: int
    type: str  # "Income" or "Expense"
    title: str
    amount: float
    category: str
    date: str  # ISO format YYYY-MM-DD
    payment_method: str
    description: str = ""
    created_at: str = ""

    @staticmethod
    def from_row(row: dict) -> "Transaction":
        return Transaction(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            title=row["title"],
            amount=row["amount"],
            category=row["category"],
            date=row["date"],
            payment_method=row["payment_method"],
            description=row.get("description") or "",
            created_at=row.get("created_at", ""),
        )
