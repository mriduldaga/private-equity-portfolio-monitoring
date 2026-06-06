import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import add_monitoring_flags, portfolio_kpis
from src.ui import (
    apply_theme,
    exposure_chart,
    format_currency,
    page_header,
    status_badge,
)

st.set_page_config(
    page_title="Five Arrows Portfolio Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

portfolio = add_monitoring_flags(load_portfolio())

with st.sidebar:
    st.markdown("### FIVE ARROWS")
    st.caption("Portfolio Monitoring")
    selected_funds = st.multiselect(
        "Fund",
        sorted(portfolio["fund"].unique()),
        default=sorted(portfolio["fund"].unique()),
    )
    st.divider()
    st.caption("NAVIGATION")
    st.page_link("app.py", label="Command Center")
    st.page_link("pages/1_Fund_Overview.py", label="Fund Overview")
    st.page_link("pages/2_Portfolio_Companies.py", label="Portfolio Companies")
    st.page_link("pages/3_Performance_Monitoring.py", label="Performance Monitoring")
    st.page_link("pages/4_Data_Completeness.py", label="Data Completeness")
    st.page_link("pages/5_Investor_Report.py", label="Investor Report")
    st.divider()
    st.caption("Fictional data · For demonstration only")

filtered = portfolio[portfolio["fund"].isin(selected_funds)]
kpis = portfolio_kpis(filtered)

page_header(
    "Portfolio Command Center",
    "Private equity portfolio monitoring, operating performance, and investor reporting.",
    "Q1 2026",
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio value", format_currency(kpis["portfolio_value"]), f'{kpis["value_change"]:+.1f}% vs entry')
c2.metric("Active assets", f'{kpis["assets"]}', f'{kpis["watchlist"]} on watchlist')
c3.metric("Average revenue growth", f'{kpis["avg_growth"]:.1f}%', f'{kpis["growth_delta"]:+.1f}pp vs plan')
c4.metric("Data completeness", f'{kpis["completeness"]:.0f}%', f'{kpis["stale"]} stale updates')

st.markdown("### Executive view")
left, right = st.columns([1.45, 1])
with left:
    st.plotly_chart(exposure_chart(filtered, "sector", "Sector exposure"), use_container_width=True)
with right:
    st.markdown("#### Attention required")
    watchlist = filtered[filtered["issue_count"] > 0].sort_values(
        ["issue_count", "current_ev"], ascending=[False, False]
    ).head(6)
    if watchlist.empty:
        st.success("No monitoring exceptions in the selected portfolio.")
    else:
        for _, row in watchlist.iterrows():
            st.markdown(
                f"""
                <div class="watch-row">
                    <div><b>{row['company_name']}</b><br><span>{row['fund']} · {row['sector']}</span></div>
                    <div>{status_badge(row['monitoring_status'])}<br><small>{row['primary_issue']}</small></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("### Fund summary")
fund_summary = (
    filtered.groupby("fund", as_index=False)
    .agg(
        portfolio_value=("current_ev", "sum"),
        assets=("company_name", "count"),
        revenue_growth=("revenue_growth", "mean"),
        ebitda_margin=("ebitda_margin", "mean"),
        exceptions=("issue_count", "sum"),
    )
)
st.dataframe(
    fund_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "fund": "Fund",
        "portfolio_value": st.column_config.NumberColumn("Portfolio value", format="€ %.0fM"),
        "assets": "Assets",
        "revenue_growth": st.column_config.NumberColumn("Avg. growth", format="%.1f%%"),
        "ebitda_margin": st.column_config.NumberColumn("Avg. EBITDA margin", format="%.1f%%"),
        "exceptions": "Open exceptions",
    },
)
