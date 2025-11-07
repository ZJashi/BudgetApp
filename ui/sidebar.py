import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from settings import get_base_currency, set_setting, load_rates


DB_PATH = "/Users/zurajashi/Desktop/BudgetApp/budget.sqlite"


def sidebar_controls(con):
    """Sidebar for adding transactions and managing currencies (SQLite-safe)."""

    st.sidebar.header("💰 Add Transaction")

    # ---------- Load base currency and FX rates ----------
    rates_df = load_rates(con)
    base_ccy = get_base_currency(con)
    known_ccys = (
        sorted(rates_df["currency"].unique().tolist()) if not rates_df.empty else [base_ccy]
    )
    if base_ccy not in known_ccys:
        known_ccys = [base_ccy] + known_ccys

    # ---------- Add Transaction ----------
    with st.sidebar.form("add_txn"):
        d = st.date_input("Date", value=date.today())
        cat = st.text_input("Category", placeholder="e.g., Rent, Groceries, Salary")
        desc = st.text_input("Description", placeholder="Optional")

        c1, c2 = st.columns([1, 1])
        with c1:
            amt = st.number_input("Amount (+ income, – expense)", step=0.01, format="%.2f")
        with c2:
            ccy_choice = st.selectbox("Currency", options=known_ccys + ["(Other…)"], index=0)
            ccy = (
                st.text_input("Other currency", placeholder="USD").upper().strip()
                if ccy_choice == "(Other…)"
                else ccy_choice
            )

        add = st.form_submit_button("Save")

        if add:
            if not ccy:
                st.sidebar.error("Please specify a currency.")
            else:
                # ---------- Use a fresh connection to guarantee write ----------
                with sqlite3.connect(DB_PATH) as db:
                    db.execute(
                        """
                        INSERT INTO txns (tdate, category, description, amount, currency)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        [pd.Timestamp(d).date(), cat.strip(), desc.strip(), float(amt), ccy],
                    )
                    db.execute(
                        """
                        INSERT INTO fx_rates (currency, rate_to_base)
                        SELECT ?, 0.0
                        WHERE NOT EXISTS (SELECT 1 FROM fx_rates WHERE currency = ?)
                        """,
                        [ccy, ccy],
                    )
                    db.commit()

                st.sidebar.success("✅ Transaction saved!")
                st.cache_data.clear()
                st.rerun()

    # ---------- Divider ----------
    st.sidebar.divider()
    st.sidebar.subheader("💱 Currencies & Rates")

    # ---------- Base currency ----------
    with st.sidebar.form("fx_settings"):
        base_input = st.text_input(
            "Base currency (reporting)", value=base_ccy
        ).upper().strip()
        if st.form_submit_button("Save base currency") and base_input:
            with sqlite3.connect(DB_PATH) as db:
                set_setting(db, "base_currency", base_input)
                db.execute(
                    """
                    INSERT INTO fx_rates (currency, rate_to_base)
                    SELECT ?, 1.0
                    WHERE NOT EXISTS (SELECT 1 FROM fx_rates WHERE currency = ?)
                    """,
                    [base_input, base_input],
                )
                db.execute(
                    "UPDATE fx_rates SET rate_to_base = 1.0 WHERE currency = ?",
                    [base_input],
                )
                db.commit()
            st.success(f"✅ Base currency set to {base_input}")
            st.cache_data.clear()
            st.rerun()

    # ---------- Add or update FX rate ----------
    with st.sidebar.form("add_rate"):
        st.caption("Set rate to **base** (amount × rate_to_base → base).")
        rate_df = load_rates(con)
        rate_ccy = st.selectbox("Currency", options=sorted(rate_df["currency"].unique().tolist()))
        rate_val = st.number_input("Rate → base", step=0.0001, format="%.6f", min_value=0.0)

        if st.form_submit_button("Save rate"):
            if rate_ccy == base_ccy:
                st.sidebar.info("Base currency is always 1.0")
            elif rate_val <= 0:
                st.sidebar.error("Rate must be > 0")
            else:
                with sqlite3.connect(DB_PATH) as db:
                    db.execute(
                        """
                        INSERT INTO fx_rates (currency, rate_to_base)
                        VALUES (?, ?)
                        ON CONFLICT (currency)
                        DO UPDATE SET rate_to_base = excluded.rate_to_base
                        """,
                        [rate_ccy, float(rate_val)],
                    )
                    db.commit()
                st.sidebar.success(f"✅ Saved: 1 {rate_ccy} = {rate_val:.6f} {base_input}")
                st.cache_data.clear()
                st.rerun()

    # ---------- Display FX table ----------
    st.sidebar.dataframe(
        load_rates(con).sort_values("currency"),
        use_container_width=True,
        height=220,
    )



