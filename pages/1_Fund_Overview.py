import plotly.express as px
import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import add_monitoring_flags, portfolio_kpis
from src.ui import apply_theme, exposure_chart, format_currency, page_header, sidebar_filters

st.set_page_config(page_title="Fund Overview", layout="wide")
apply_theme()
df = sidebar_filters(add_monitoring_flags(load_portfolio()), "overview")
kpis = portfolio_kpis(df)

page_header("Fund Overview", "Fund-level valuation, exposure, and operating performance.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Portfolio value", format_currency(kpis["portfolio_value"]))
c2.metric("Assets", kpis["assets"])
c3.metric("Average revenue growth", f'{kpis["avg_growth"]:.1f}%')
c4.metric("Average EBITDA margin", f'{df["ebitda_margin"].mean():.1f}%' if not df.empty else "0.0%")
c5.metric("Underperforming", kpis["watchlist"])

left, right = st.columns(2)
with left:
    st.plotly_chart(exposure_chart(df, "sector", "Sector exposure"), use_container_width=True)
with right:
    st.plotly_chart(exposure_chart(df, "geography", "Geographic exposure"), use_container_width=True)

left, right = st.columns([1.4, 1])
with left:
    top = df.nlargest(10, "current_ev").sort_values("current_ev")
    fig = px.bar(
        top,
        x="current_ev",
        y="company_name",
        orientation="h",
        color="fund",
        title="Top 10 companies by valuation",
        labels={"current_ev": "Current enterprise value (€m)", "company_name": ""},
        color_discrete_sequence=["#10263f", "#2f65a7", "#b89a5d", "#7994ad"],
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=410)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Fund performance")
    summary = (
        df.groupby("fund", as_index=False)
        .agg(
            value=("current_ev", "sum"),
            growth=("revenue_growth", "mean"),
            margin=("ebitda_margin", "mean"),
            assets=("company_name", "count"),
        )
    )
    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True,
        column_config={
            "fund": "Fund",
            "value": st.column_config.NumberColumn("Value", format="€ %.0fM"),
            "growth": st.column_config.ProgressColumn("Revenue growth", format="%.1f%%", min_value=-15, max_value=30),
            "margin": st.column_config.NumberColumn("EBITDA margin", format="%.1f%%"),
            "assets": "Assets",
        },
    )
