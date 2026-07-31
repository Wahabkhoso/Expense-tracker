"""
auth_service.py
Handles user registration, login, and password security.
Passwords are never stored in plain text - PBKDF2-HMAC-SHA256 with a
per-user random salt is used for hashing.
"""

import hashlib
import os
import re
from datetime import datetime

from database.database import db
from models.user import User


class AuthError(Exception):
    """Raised for any authentication / registration failure."""
    pass


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()


def _generate_salt() -> str:
    return os.urandom(16).hex()


def register_user(full_name: str, email: str, password: str, confirm_password: str) -> User:
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()

    if not full_name:
        raise AuthError("Full name is required.")
    if not email or not EMAIL_REGEX.match(email):
        raise AuthError("Please enter a valid email address.")
    if not password or len(password) < 6:
        raise AuthError("Password must be at least 6 characters long.")
    if password != confirm_password:
        raise AuthError("Passwords do not match.")

    existing = db.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        raise AuthError("An account with this email already exists.")

    salt = _generate_salt()
    password_hash = _hash_password(password, salt)
    created_at = datetime.now().isoformat()

    user_id = db.execute(
        """INSERT INTO users (full_name, email, password_hash, salt, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (full_name, email, password_hash, salt, created_at),
    )
    row = db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    return User.from_row(row)


def login_user(email: str, password: str) -> User:
    email = (email or "").strip().lower()
    if not email or not password:
        raise AuthError("Please enter both email and password.")

    row = db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if not row:
        raise AuthError("Invalid email or password.")

    computed_hash = _hash_password(password, row["salt"])
    if computed_hash != row["password_hash"]:
        raise AuthError("Invalid email or password.")

    return User.from_row(row)


def update_settings(user_id: int, currency: str = None, theme: str = None,
                     notifications_enabled: bool = None) -> User:
    fields = []
    params = []
    if currency is not None:
        fields.append("currency = ?")
        params.append(currency)
    if theme is not None:
        fields.append("theme = ?")
        params.append(theme)
    if notifications_enabled is not None:
        fields.append("notifications_enabled = ?")
        params.append(1 if notifications_enabled else 0)

    if fields:
        params.append(user_id)
        db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(params))

    row = db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    return User.from_row(row)
