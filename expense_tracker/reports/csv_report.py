"""
csv_report.py
Exports transaction data to CSV using Pandas.
"""

import pandas as pd
from services.analytics_service import get_transactions_dataframe


def export_transactions_csv(user_id: int, filepath: str, start_date: str = None,
                             end_date: str = None) -> None:
    df = get_transactions_dataframe(user_id, start_date, end_date)
    columns = ["id", "date", "title", "category", "type", "payment_method", "amount", "description"]
    if df.empty:
        df = pd.DataFrame(columns=columns)
    else:
        df = df[columns]
    df.to_csv(filepath, index=False)
