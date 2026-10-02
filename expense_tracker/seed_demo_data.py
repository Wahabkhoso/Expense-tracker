"""
seed_demo_data.py
Run this once to populate ExpensePro with realistic demo data
(transactions across the last 3 months + budgets for the current month)
so the app looks populated and professional for screenshots/demo videos.

Usage:
    python seed_demo_data.py
"""

from datetime import date, timedelta
import random

from services.auth_service import register_user, login_user, AuthError
from services.transaction_service import add_transaction
from services.budget_service import set_budget

DEMO_EMAIL = "demo@expensepro.com"
DEMO_PASSWORD = "demo12345"
DEMO_NAME = "Ahmed Khan"

# ---- Get or create the demo user ----
try:
    user = login_user(DEMO_EMAIL, DEMO_PASSWORD)
    print(f"Using existing demo account: {user.email}")
except AuthError:
    user = register_user(DEMO_NAME, DEMO_EMAIL, DEMO_PASSWORD, DEMO_PASSWORD)
    print(f"Created new demo account: {user.email}")

PAYMENT_METHODS = ["Cash", "Bank", "Credit Card", "Debit Card", "Mobile Wallet"]

# ---- Recurring monthly income ----
INCOME_ITEMS = [
    ("Monthly Salary", 150000, "Salary", "Bank"),
    ("Freelance Project", 25000, "Business", "Bank"),
]

# ---- Realistic expense entries (title, amount, category, payment method) ----
EXPENSE_ITEMS = [
    ("Grocery shopping - Imtiaz", 8500, "Food", "Cash"),
    ("Grocery shopping - Al-Fatah", 6200, "Food", "Debit Card"),
    ("Dinner at restaurant", 3200, "Food", "Credit Card"),
    ("Uber rides", 2400, "Transport", "Mobile Wallet"),
    ("Petrol", 5000, "Transport", "Cash"),
    ("Careem to office", 1800, "Transport", "Mobile Wallet"),
    ("New shoes", 4500, "Shopping", "Credit Card"),
    ("Clothing - winter collection", 7800, "Shopping", "Credit Card"),
    ("Electricity bill", 9500, "Bills", "Bank"),
    ("Internet bill (PTCL)", 3500, "Bills", "Bank"),
    ("Mobile top-up", 1000, "Bills", "Mobile Wallet"),
    ("Online course - Udemy", 3200, "Education", "Credit Card"),
    ("Books", 2100, "Education", "Cash"),
    ("Doctor's visit", 3000, "Healthcare", "Cash"),
    ("Pharmacy - medicines", 1500, "Healthcare", "Cash"),
    ("Netflix subscription", 1200, "Entertainment", "Credit Card"),
    ("Movie tickets", 2000, "Entertainment", "Debit Card"),
    ("House rent", 45000, "Rent", "Bank"),
    ("Gift for friend's wedding", 5000, "Other", "Cash"),
]

random.seed(42)  # reproducible demo data
today = date.today()
added_count = 0

# ---- Populate the last 3 months ----
for month_offset in range(3):
    month_date = today.replace(day=1) - timedelta(days=month_offset * 30)
    year, month = month_date.year, month_date.month

    # Income - added on the 1st of each month
    for title, amount, category, method in INCOME_ITEMS:
        tx_date = date(year, month, 1).isoformat()
        add_transaction(user.id, "Income", title, amount, category, tx_date, method,
                         "Demo data")
        added_count += 1

    # Expenses - spread across random days in the month
    for title, amount, category, method in EXPENSE_ITEMS:
        day = random.randint(1, 27)
        # slight randomization so amounts look natural across months
        varied_amount = round(amount * random.uniform(0.85, 1.15), -2)
        tx_date = date(year, month, day).isoformat()
        add_transaction(user.id, "Expense", title, varied_amount, category, tx_date, method,
                         "")
        added_count += 1

print(f"Added {added_count} demo transactions across the last 3 months.")

# ---- Set budgets for the current month ----
budgets = [
    ("Food", 25000),
    ("Transport", 10000),
    ("Shopping", 15000),
    ("Bills", 15000),
    ("Entertainment", 5000),
]
for category, amount in budgets:
    set_budget(user.id, category, amount, today.month, today.year)

print(f"Set {len(budgets)} budgets for {today.strftime('%B %Y')}.")
print()
print("=" * 50)
print(f"Login with:  {DEMO_EMAIL}  /  {DEMO_PASSWORD}")
print("=" * 50)