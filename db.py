import sqlite3
from pathlib import Path
import streamlit as st

# Path to your persistent SQLite database
DB_PATH = Path("/Users/zurajashi/Desktop/BudgetApp/budget.sqlite")

@st.cache_resource
def get_con():
    # Ensure parent directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to a fixed on-disk database
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = con.cursor()

    # Create necessary tables if they don't exist
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS txns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tdate TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            currency TEXT
        );

        CREATE TABLE IF NOT EXISTS fx_rates (
            currency TEXT PRIMARY KEY,
            rate_to_base REAL
        );

        CREATE TABLE IF NOT EXISTS settings (
            k TEXT PRIMARY KEY,
            v TEXT
        );
    """)
    con.commit()
    return con

