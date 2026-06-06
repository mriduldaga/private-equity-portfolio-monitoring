import plotly.express as px
import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import add_monitoring_flags, issue_summary
from src.ui import apply_theme, page_header, sidebar_filters

st.set_page_config(page_title="Performance Monitoring", layout="wide")
apply_theme()
df = sidebar_filters(add_monitoring_flags(load_portfolio()), "monitoring")
exceptions = df[df["issue_count"] > 0].copy()

page_header("Performance Monitoring", "Exception-based monitoring across operating performance, leverage, valuation, and reporting.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Companies flagged", len(exceptions), f'{len(df) - len(exceptions)} on track')
c2.metric("Critical assets", int((df["monitoring_status"] == "Critical").sum()))
c3.metric("High leverage", int(df["high_leverage"].sum()), ">5.0x net debt / EBITDA")
c4.metric("Stale updates", int(df["stale_data"].sum()), ">90 days")

left, right = st.columns([1, 1.5])
with left:
    issues = issue_summary(df)
    fig = px.bar(
        issues.sort_values("companies"),
        x="companies",
        y="issue",
        orientation="h",
        title="Open monitoring exceptions",
        color="companies",
        color_continuous_scale=["#b7c4cf", "#b89a5d", "#a63a35"],
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10), height=390)
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.scatter(
        df,
        x="revenue_growth",
        y="ebitda_margin",
        size="current_ev",
        color="monitoring_status",
        hover_name="company_name",
        hover_data=["fund", "net_debt_ebitda"],
        title="Growth and profitability",
        labels={"revenue_growth": "Revenue growth (%)", "ebitda_margin": "EBITDA margin (%)"},
        color_discrete_map={"Critical": "#a63a35", "Watchlist": "#b89a5d", "On track": "#2f65a7"},
    )
    fig.add_vline(x=-10, line_dash="dash", line_color="#a63a35")
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=390)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Exception register")
st.dataframe(
    exceptions.sort_values(["issue_count", "current_ev"], ascending=[False, False])[
        [
            "company_name", "fund", "monitoring_status", "primary_issue", "issue_count",
            "revenue_growth", "margin_change", "net_debt_ebitda", "multiple_change",
            "days_since_update",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "company_name": "Company",
        "fund": "Fund",
        "monitoring_status": "Status",
        "primary_issue": "Primary issue",
        "issue_count": "Exceptions",
        "revenue_growth": st.column_config.NumberColumn("Revenue growth", format="%.1f%%"),
        "margin_change": st.column_config.NumberColumn("Margin change", format="%.1fpp"),
        "net_debt_ebitda": st.column_config.NumberColumn("Leverage", format="%.1fx"),
        "multiple_change": st.column_config.NumberColumn("Multiple change", format="%.1fx"),
        "days_since_update": "Days since update",
    },
)
