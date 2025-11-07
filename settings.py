import pandas as pd

# === FX Rates ===
def load_rates(con):
    """Return DataFrame of FX rates."""
    return pd.read_sql_query("SELECT * FROM fx_rates ORDER BY currency", con)


def save_rate(con, currency, rate):
    """Insert or update FX rate."""
    cur = con.cursor()
    cur.execute("""
        INSERT INTO fx_rates (currency, rate_to_base)
        VALUES (?, ?)
        ON CONFLICT(currency) DO UPDATE SET rate_to_base = excluded.rate_to_base;
    """, (currency, rate))
    con.commit()


# === Settings ===
def load_settings(con):
    """Return DataFrame of all settings."""
    return pd.read_sql_query("SELECT * FROM settings", con)


def save_setting(con, key, value):
    """Insert or update a setting."""
    cur = con.cursor()
    cur.execute("""
        INSERT INTO settings (k, v)
        VALUES (?, ?)
        ON CONFLICT(k) DO UPDATE SET v = excluded.v;
    """, (key, value))
    con.commit()


# --- Alias for backward compatibility with old code ---
set_setting = save_setting


# === Base Currency ===
def get_base_currency(con):
    """
    Return the base currency (used for conversions and display).
    If not set, default to 'USD'.
    """
    cur = con.cursor()
    cur.execute("SELECT v FROM settings WHERE k = 'base_currency'")
    row = cur.fetchone()
    return row[0] if row else "USD"


def set_base_currency(con, currency):
    """Set or update the base currency."""
    save_setting(con, "base_currency", currency)
