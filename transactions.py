import pandas as pd
import streamlit as st

def insert_txn(con, tdate, category, description, amount, currency):
    """Insert a new transaction (append, never overwrite)."""
    tdate = pd.to_datetime(tdate).date()
    category = category.strip() if category else None
    description = description.strip() if description else None
    amount = float(amount) if amount else 0.0
    currency = currency.strip().upper() if currency else None

    cur = con.cursor()
    cur.execute("""
        INSERT INTO txns (tdate, category, description, amount, currency)
        VALUES (?, ?, ?, ?, ?)
    """, (tdate, category, description, amount, currency))
    con.commit()
    st.cache_data.clear()  # ensure dashboard refreshes


def get_all_txns(con):
    """Fetch all transactions ordered by date (newest first)."""
    try:
        df = pd.read_sql_query("SELECT * FROM txns ORDER BY tdate DESC", con)
        df["tdate"] = pd.to_datetime(df["tdate"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "tdate", "category", "description", "amount", "currency"])


# Backward-compatible alias
load_txns = get_all_txns


def delete_txn(con, txn_id):
    """Delete a single transaction by ID."""
    cur = con.cursor()
    cur.execute("DELETE FROM txns WHERE id = ?", (txn_id,))
    con.commit()
    st.cache_data.clear()


def delete_month_data(con, month_date):
    """Delete all transactions for the month of the given date."""
    month_date = pd.to_datetime(month_date, errors="coerce")
    if pd.isna(month_date):
        return

    year, month = month_date.year, month_date.month

    cur = con.cursor()
    cur.execute("""
        DELETE FROM txns
        WHERE strftime('%Y', tdate) = ? AND strftime('%m', tdate) = ?
    """, (str(year), f"{month:02d}"))
    con.commit()

    st.success(f"Deleted all transactions for {month_date.strftime('%B %Y')}.")
    st.cache_data.clear()
