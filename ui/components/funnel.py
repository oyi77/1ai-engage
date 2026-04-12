import pandas as pd
import streamlit as st
import os

from scripts.config import LEADS_FILE


def render_funnel(df=None):
    st.header("📊 Funnel")

    if df is None:
        if not os.path.exists(LEADS_FILE) or os.path.getsize(LEADS_FILE) == 0:
            st.info("No leads found.")
            return
        df = pd.read_csv(LEADS_FILE)

    if df.empty:
        st.info("No leads found.")
        return

    if "status" in df.columns:
        counts = df["status"].value_counts().to_dict()
    else:
        counts = {}

    key_stages = [
        "new",
        "enriched",
        "draft_ready",
        "reviewed",
        "contacted",
        "replied",
        "meeting_booked",
        "won",
    ]

    cols = st.columns(len(key_stages))
    for col, stage in zip(cols, key_stages):
        count = counts.get(stage, 0)
        col.metric(label=stage.replace("_", " ").title(), value=count)

    st.subheader("All Statuses Overview")
    if counts:
        chart_data = pd.DataFrame(
            list(counts.items()), columns=["Status", "Count"]
        ).set_index("Status")
        st.bar_chart(chart_data)
    else:
        st.info("No status data available.")
