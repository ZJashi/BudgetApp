import streamlit as st
import pandas as pd
from datetime import date
from settings import get_base_currency, set_setting, load_rates
from transactions import insert_txn

def sidebar_controls(con):
    st.sidebar.header("💰 Add Transaction")

    rates_df = load_rates(con)
    base_ccy = get_base_currency(con)
    known_ccys = sorted(rates_df["currency"].unique().tolist()) if not rates_df.empty else [base_ccy]
    if base_ccy not in known_ccys:
        known_ccys = [base_ccy] + known_ccys

    with st.sidebar.form("add_txn"):
        d = st.date_input("Date", value=date.today())
        cat = st.text_input("Category", placeholder="e.g., Rent, Groceries")
        desc = st.text_input("Description", placeholder="Optional")
        amt = st.number_input("Amount (+ income, – expense)", step=0.01, format="%.2f")
        ccy_choice = st.selectbox("Currency", options=known_ccys + ["(Other…)"])
        ccy = st.text_input("Other currency", placeholder="USD").upper().strip() if ccy_choice == "(Other…)" else ccy_choice

        if st.form_submit_button("Save"):
            if not ccy:
                st.sidebar.error("Please specify a currency.")
            else:
                insert_txn(con, d, cat, desc, amt, ccy)
                st.sidebar.success("Saved!")
                st.cache_data.clear()

    # ---------- Currencies ----------
    st.sidebar.divider()
    st.sidebar.subheader("💱 Currencies & Rates")
    with st.sidebar.form("fx_settings"):
        base_input = st.text_input("Base currency", value=base_ccy).upper().strip()
        if st.form_submit_button("Save base currency"):
            set_setting(con, "base_currency", base_input)
            con.execute("""
                INSERT INTO fx_rates(currency, rate_to_base)
                SELECT ?, 1.0
                WHERE NOT EXISTS (SELECT 1 FROM fx_rates WHERE currency = ?)
            """, [base_input, base_input])
            con.execute("UPDATE fx_rates SET rate_to_base = 1.0 WHERE currency = ?", [base_input])
            st.success(f"Base currency set to {base_input}")
            st.cache_data.clear()
            st.rerun()

    with st.sidebar.form("add_rate"):
        rate_df = load_rates(con)
        rate_ccy = st.selectbox("Currency", options=sorted(rate_df["currency"].unique().tolist()))
        rate_val = st.number_input("Rate → base", step=0.0001, format="%.6f", min_value=0.0)
        if st.form_submit_button("Save rate"):
            if rate_val <= 0:
                st.sidebar.error("Rate must be > 0")
            else:
                con.execute("""
                    INSERT INTO fx_rates(currency, rate_to_base) VALUES (?, ?)
                    ON CONFLICT (currency) DO UPDATE SET rate_to_base = excluded.rate_to_base
                """, [rate_ccy, float(rate_val)])
                st.sidebar.success(f"Saved: 1 {rate_ccy} = {rate_val:.4f} {base_input}")
                st.cache_data.clear()

    st.sidebar.dataframe(load_rates(con), use_container_width=True, height=200)

