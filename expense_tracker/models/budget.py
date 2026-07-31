"""
budget.py
Data model representing a monthly category budget.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Budget:
    id: Optional[int]
    user_id: int
    category: str
    amount: float
    month: int
    year: int

    @staticmethod
    def from_row(row: dict) -> "Budget":
        return Budget(
            id=row["id"],
            user_id=row["user_id"],
            category=row["category"],
            amount=row["amount"],
            month=row["month"],
            year=row["year"],
        )
