"""
user.py
Data model representing a user record.
"""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    full_name: str
    email: str
    currency: str = "PKR"
    theme: str = "dark"
    notifications_enabled: bool = True

    @staticmethod
    def from_row(row: dict) -> "User":
        return User(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            currency=row.get("currency", "PKR"),
            theme=row.get("theme", "dark"),
            notifications_enabled=bool(row.get("notifications_enabled", 1)),
        )
