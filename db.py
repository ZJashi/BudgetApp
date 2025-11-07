import sqlite3
import os
from pathlib import Path

DB_PATH = Path("/Users/zurajashi/Desktop/BudgetApp/budget.sqlite")

def get_con():

    # Make sure the folder exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to a fixed database file, not :memory:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = con.cursor()

    # Create tables once
    cur.execute("""
        CREATE TABLE IF NOT EXISTS txns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tdate TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            currency TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            k TEXT PRIMARY KEY,
            v TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fx_rates(
            currency TEXT PRIMARY KEY,
            rate_to_base REAL
        );
    """)
    con.commit()
    return con
