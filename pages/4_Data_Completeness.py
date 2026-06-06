import plotly.express as px
import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import REQUIRED_FIELDS, add_monitoring_flags
from src.ui import apply_theme, page_header, sidebar_filters

st.set_page_config(page_title="Data Completeness", layout="wide")
apply_theme()
df = sidebar_filters(add_monitoring_flags(load_portfolio()), "completeness")

page_header("Data Completeness", "Quarterly reporting readiness and database maintenance tracker.")

overall = df["data_completeness"].mean() if not df.empty else 0
complete = int((df["data_completeness"] == 100).sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Completeness score", f"{overall:.0f}%")
c2.metric("Complete company records", complete, f"of {len(df)}")
c3.metric("Missing financial packs", int(df["missing_financials"].sum()))
c4.metric("Updates >90 days old", int(df["stale_data"].sum()))

missing = (
    df[REQUIRED_FIELDS].isna().sum().rename_axis("field").reset_index(name="missing_records")
)
left, right = st.columns([1, 1.5])
with left:
    fig = px.bar(
        missing.sort_values("missing_records"),
        x="missing_records",
        y="field",
        orientation="h",
        title="Missing data by field",
        color_discrete_sequence=["#b89a5d"],
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=340)
    st.plotly_chart(fig, use_container_width=True)
with right:
    fund_quality = df.groupby("fund", as_index=False).agg(
        data_completeness=("data_completeness", "mean"),
        avg_days_since_update=("days_since_update", "mean"),
        stale_records=("stale_data", "sum"),
    )
    st.markdown("#### Reporting readiness by fund")
    st.dataframe(
        fund_quality,
        use_container_width=True,
        hide_index=True,
        column_config={
            "fund": "Fund",
            "data_completeness": st.column_config.ProgressColumn("Completeness", format="%.0f%%", min_value=0, max_value=100),
            "avg_days_since_update": st.column_config.NumberColumn("Avg. days since update", format="%.0f"),
            "stale_records": "Stale records",
        },
    )

st.markdown("### Records requiring follow-up")
follow_up = df[(df["data_completeness"] < 100) | df["stale_data"]]
st.dataframe(
    follow_up[["company_name", "fund", "data_completeness", "last_updated", "days_since_update", "primary_issue"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "company_name": "Company",
        "fund": "Fund",
        "data_completeness": st.column_config.ProgressColumn("Completeness", format="%.0f%%", min_value=0, max_value=100),
        "last_updated": st.column_config.DateColumn("Last updated", format="DD MMM YYYY"),
        "days_since_update": "Days since update",
        "primary_issue": "Primary issue",
    },
)
