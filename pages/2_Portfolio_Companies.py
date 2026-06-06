import streamlit as st

from src.data_loader import load_portfolio
from src.metrics import add_monitoring_flags
from src.ui import apply_theme, page_header, sidebar_filters

st.set_page_config(page_title="Portfolio Companies", layout="wide")
apply_theme()
df = sidebar_filters(add_monitoring_flags(load_portfolio()), "companies")

page_header("Portfolio Companies", "Search, filter, and inspect the portfolio company database.")

search = st.text_input("Search company", placeholder="Start typing a company name...")
if search:
    df = df[df["company_name"].str.contains(search, case=False, na=False)]

st.dataframe(
    df[
        [
            "company_name", "fund", "sector", "geography", "status", "entry_date",
            "entry_ev", "current_ev", "revenue", "ebitda", "revenue_growth",
            "ebitda_margin", "net_debt_ebitda", "ownership_percentage",
            "valuation_multiple", "monitoring_status", "last_updated",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    height=620,
    column_config={
        "company_name": "Company",
        "fund": "Fund",
        "sector": "Sector",
        "geography": "Geography",
        "status": "Investment status",
        "entry_date": st.column_config.DateColumn("Entry date", format="MMM YYYY"),
        "entry_ev": st.column_config.NumberColumn("Entry EV", format="€ %.0fM"),
        "current_ev": st.column_config.NumberColumn("Current EV", format="€ %.0fM"),
        "revenue": st.column_config.NumberColumn("Revenue", format="€ %.0fM"),
        "ebitda": st.column_config.NumberColumn("EBITDA", format="€ %.0fM"),
        "revenue_growth": st.column_config.ProgressColumn("Revenue growth", format="%.1f%%", min_value=-20, max_value=30),
        "ebitda_margin": st.column_config.NumberColumn("EBITDA margin", format="%.1f%%"),
        "net_debt_ebitda": st.column_config.NumberColumn("Net debt / EBITDA", format="%.1fx"),
        "ownership_percentage": st.column_config.NumberColumn("Ownership", format="%.1f%%"),
        "valuation_multiple": st.column_config.NumberColumn("Valuation multiple", format="%.1fx"),
        "monitoring_status": "Monitoring",
        "last_updated": st.column_config.DateColumn("Last updated", format="DD MMM YYYY"),
    },
)
st.download_button(
    "Download filtered company data",
    df.to_csv(index=False).encode("utf-8"),
    file_name="portfolio_companies_filtered.csv",
    mime="text/csv",
)
