import os
import pandas as pd
import streamlit as st
from datetime import date

from db import get_con
from utils import first_of_month_from
from transactions import load_txns, delete_month_data
from settings import get_base_currency
from ui.sidebar import sidebar_controls
from ui.charts import show_dashboard
from ui.table import show_transaction_table

# ---------- Page Setup ----------
st.set_page_config(page_title="Personal Budget", layout="wide")

# ---------- Database & Sidebar ----------
con = get_con()
sidebar_controls(con)

# ---------- Load Transactions ----------
df = load_txns(con)
df["tdate"] = pd.to_datetime(df["tdate"], errors="coerce")

if df.empty:
    st.info("No transactions yet. Add one from the sidebar or import a CSV.")
    st.stop()

base_ccy = get_base_currency(con)

# ---------- Filters ----------
st.header("📅 Filters")

c1, c2 = st.columns(2)
max_d = df["tdate"].max() if df["tdate"].notna().any() else pd.Timestamp.today()
selected_month = c1.date_input("Month", value=first_of_month_from(max_d))
cats = ["(All)"] + sorted(df["category"].dropna().astype(str).unique().tolist())
selected_cat = c2.selectbox("Category", cats)

c3, c4 = st.columns(2)
currs = ["(All)"] + sorted(df["currency"].dropna().astype(str).unique().tolist())
selected_ccy = c3.selectbox("Currency", currs)
days = ["(All)"] + [d.date() for d in pd.date_range(selected_month, periods=31, freq="D")]
selected_day = c4.selectbox("Day (optional)", days)

# ---------- Apply Filters ----------
mask = (df["tdate"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M"))
if selected_cat != "(All)":
    mask &= (df["category"] == selected_cat)
if selected_ccy != "(All)":
    mask &= (df["currency"] == selected_ccy)
if selected_day != "(All)":
    mask &= (df["tdate"].dt.date == selected_day)

mdf = df.loc[mask].copy()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧾 Transactions", "⚙️ Settings"])

with tab1:
    show_dashboard(mdf, base_ccy)

with tab2:
    show_transaction_table(con, mdf, base_ccy)

with tab3:
    st.subheader("⚙️ Settings")
    st.write("Delete monthly data manually (does not run automatically).")

    if st.button("🧨 Delete all transactions for selected month"):
        delete_month_data(con, selected_month)
