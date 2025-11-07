import sqlite3
import os
from pathlib import Path

DB_PATH = Path("/Users/zurajashi/Desktop/BudgetApp")


def get_con()

    # Make sure folder exists
    DB_PATH.parent.mkdir(exist_ok=True)

    #Connect to a file
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()


    # Create Tables
    cur.execute(
    '''
        CREATE TABLE IF NOT EXISTS txns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tdate TEXT,
            category TEXT, 
            description TEXT, 
            amount REAL, 
            currency TEXT
        );
    ''')


    cur.execute(
    '''
        CREATE TABLE IF NOT EXISTS settings(
            k TEXT PRIMARY KEY,  
            v TEXT
        );    
    ''')


    cur.execute(
    '''
        CREATE TABLE IF NOT EXISTS fx_rates(]
            currency TEXT PRIMARY KEY, 
            rate_to_base REAL
        );
    ''')

    con.commit()
    return con
