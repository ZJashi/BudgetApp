import streamlit as st
import pandas as pd
import altair as alt

def show_dashboard(df, base_ccy):
    if df.empty:
        st.info("No data for selected month.")
        return

    # --- Clean and normalize ---
    df["tdate"] = pd.to_datetime(df["tdate"], errors="coerce")
    df["amount_base"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    # --- Compute KPIs ---
    income = df.loc[df["amount_base"] > 0, "amount_base"].sum()
    expense = -df.loc[df["amount_base"] < 0, "amount_base"].sum()
    net = income - expense

    k1, k2, k3 = st.columns(3)
    k1.metric(f"Income ({base_ccy})", f"{income:,.2f}")
    k2.metric(f"Expenses ({base_ccy})", f"{expense:,.2f}")
    k3.metric(f"Net ({base_ccy})", f"{net:,.2f}")

    st.divider()

    # --- Category Breakdown ---
    st.subheader("📊 Category Breakdown")

    if "category" in df.columns and not df["category"].isna().all():
        cat_agg = (
            df.groupby("category", dropna=False)["amount_base"]
            .sum()
            .reset_index()
            .sort_values("amount_base", ascending=False)
        )

        cat_agg["color"] = cat_agg["amount_base"].apply(
            lambda x: "Income" if x > 0 else "Expense"
        )

        chart = (
            alt.Chart(cat_agg)
            .mark_bar()
            .encode(
                x=alt.X("category:N", sort="-y", title="Category"),
                y=alt.Y("amount_base:Q", title=f"Amount ({base_ccy})"),
                color=alt.Color(
                    "color:N",
                    scale=alt.Scale(domain=["Income", "Expense"], range=["green", "red"]),
                    legend=None,
                ),
                tooltip=["category", "amount_base"],
            )
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.caption("No category data available.")

    # --- Daily Trend ---
    st.subheader("📈 Daily Trend")

    if "tdate" in df.columns and not df["tdate"].isna().all():
        daily = df.groupby("tdate", dropna=False)["amount_base"].sum().reset_index()
        daily["cumulative"] = daily["amount_base"].cumsum()

        # Ensure numeric and drop invalid
        daily = daily.dropna(subset=["amount_base", "cumulative"])
        daily["amount_base"] = daily["amount_base"].astype(float)
        daily["cumulative"] = daily["cumulative"].astype(float)

        # Transform to long format safely
        melted = daily.melt(id_vars=["tdate"], value_vars=["amount_base", "cumulative"])

        line_chart = (
            alt.Chart(melted)
            .mark_line(point=True)
            .encode(
                x=alt.X("tdate:T", title="Date"),
                y=alt.Y("value:Q", title=f"Amount ({base_ccy})"),
                color=alt.Color(
                    "variable:N",
                    title="Metric",
                    scale=alt.Scale(range=["#0072B2", "#E69F00"]),
                ),
                tooltip=["tdate", "variable", "value"],
            )
        )

        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.caption("No daily data available.")
