import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import add_monitoring_flags, portfolio_kpis, quarterly_snapshot
from src.report_export import build_excel_report
from src.ui import apply_theme, exposure_chart, format_currency, page_header, sidebar_filters

st.set_page_config(page_title="Investor Report", layout="wide")
apply_theme()
df = sidebar_filters(add_monitoring_flags(load_portfolio()), "report")
kpis = portfolio_kpis(df)

page_header("Investor Report", "Quarterly fund snapshot prepared for investor reporting workflows.")

st.markdown("### Q1 2026 portfolio snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio value", format_currency(kpis["portfolio_value"]))
c2.metric("Portfolio companies", kpis["assets"])
c3.metric("Revenue growth", f'{kpis["avg_growth"]:.1f}%')
c4.metric("Data completeness", f'{kpis["completeness"]:.0f}%')

left, right = st.columns(2)
with left:
    st.plotly_chart(exposure_chart(df, "sector", "Sector breakdown"), use_container_width=True)
with right:
    st.plotly_chart(exposure_chart(df, "geography", "Geographic breakdown"), use_container_width=True)

top, watch = st.columns(2)
with top:
    st.markdown("#### Top performers")
    performers = df.nlargest(5, "revenue_growth")[["company_name", "fund", "revenue_growth", "ebitda_margin"]]
    st.dataframe(
        performers,
        hide_index=True,
        use_container_width=True,
        column_config={
            "company_name": "Company",
            "fund": "Fund",
            "revenue_growth": st.column_config.NumberColumn("Revenue growth", format="%.1f%%"),
            "ebitda_margin": st.column_config.NumberColumn("EBITDA margin", format="%.1f%%"),
        },
    )
with watch:
    st.markdown("#### Watchlist companies")
    watchlist = df[df["issue_count"] > 0].nlargest(5, "issue_count")[["company_name", "monitoring_status", "primary_issue"]]
    st.dataframe(watchlist, hide_index=True, use_container_width=True)

st.markdown("### Fund snapshot")
st.dataframe(quarterly_snapshot(df), hide_index=True, use_container_width=True)

report = build_excel_report(df)
st.download_button(
    "Export investor report to Excel",
    report,
    file_name="five_arrows_q1_2026_investor_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)
