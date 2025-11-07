import streamlit as st
import pandas as pd
from datetime import date

def show_transaction_table(con, df, base_ccy):
    st.subheader("🧾 Transactions")

    if df.empty:
        st.info("No transactions available.")
        return

    # Ensure proper datatypes
    df["tdate"] = pd.to_datetime(df["tdate"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df = df.sort_values(["tdate", "id"], na_position="last")

    # Session state for inline edit
    editing_id = st.session_state.get("editing_id")

    # Header row
    header = st.columns([1.2, 1.5, 3.0, 1.3, 0.8, 0.8])
    header[0].markdown("**Date**")
    header[1].markdown("**Category**")
    header[2].markdown("**Description**")
    header[3].markdown(f"**Amount ({base_ccy})**")
    header[4].markdown("**Edit**")
    header[5].markdown("**Delete**")

    for _, row in df.iterrows():
        cols = st.columns([1.2, 1.5, 3.0, 1.3, 0.8, 0.8])

        tdate_display = (
            pd.to_datetime(row["tdate"]).date()
            if pd.notna(row["tdate"])
            else "—"
        )
        cols[0].write(tdate_display)
        cols[1].write(row["category"] or "")
        cols[2].write(row["description"] or "")
        cols[3].write(f"{float(row['amount']):,.2f} {row['currency'] or base_ccy}")

        # Edit button
        if cols[4].button("✏️", key=f"edit_{row['id']}"):
            st.session_state["editing_id"] = int(row["id"])
            st.rerun()

        # Delete button
        if cols[5].button("❌", key=f"del_{row['id']}"):
            cur = con.cursor()
            cur.execute("DELETE FROM txns WHERE id = ?", (row["id"],))
            con.commit()
            st.session_state.pop("editing_id", None)
            st.cache_data.clear()
            st.success(f"Deleted transaction #{row['id']}.")
            st.rerun()

        # Inline edit form
        if editing_id == row["id"]:
            with st.form(f"edit_form_{row['id']}"):
                c1, c2, c3 = st.columns([1.2, 2.5, 1.3])

                e_date = c1.date_input(
                    "Date",
                    value=tdate_display if isinstance(tdate_display, date) else date.today(),
                    key=f"e_date_{row['id']}",
                )
                e_cat = c1.text_input(
                    "Category", value=row["category"] or "", key=f"e_cat_{row['id']}"
                )
                e_desc = c2.text_input(
                    "Description", value=row["description"] or "", key=f"e_desc_{row['id']}"
                )
                e_amt = c2.number_input(
                    "Amount (+ income, – expense)",
                    value=float(row["amount"]) if pd.notna(row["amount"]) else 0.0,
                    step=0.01,
                    format="%.2f",
                    key=f"e_amt_{row['id']}",
                )
                e_ccy = c3.text_input(
                    "Currency",
                    value=(row["currency"] or base_ccy),
                    key=f"e_ccy_{row['id']}",
                ).upper().strip()

                save, cancel = st.columns(2)
                if save.form_submit_button("💾 Save"):
                    cur = con.cursor()
                    cur.execute(
                        """
                        UPDATE txns
                        SET tdate=?, category=?, description=?, amount=?, currency=?
                        WHERE id=?
                        """,
                        (
                            pd.Timestamp(e_date).date(),
                            e_cat.strip(),
                            e_desc.strip(),
                            float(e_amt),
                            e_ccy,
                            int(row["id"]),
                        ),
                    )
                    con.commit()
                    st.session_state.pop("editing_id", None)
                    st.cache_data.clear()
                    st.success("Transaction updated.")
                    st.rerun()

                if cancel.form_submit_button("Cancel"):
                    st.session_state.pop("editing_id", None)
                    st.rerun()