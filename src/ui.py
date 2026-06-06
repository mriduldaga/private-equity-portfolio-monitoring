import plotly.express as px
import streamlit as st


NAVY = "#10263f"
BLUE = "#2f65a7"
GOLD = "#b89a5d"
PALE = "#eef3f7"


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f7f9fb; }
        [data-testid="stSidebar"] { background: #10263f; }
        [data-testid="stSidebar"] * { color: #f4f7fa !important; }
        [data-testid="stMetric"] {
            background: white; border: 1px solid #e2e8ee; border-radius: 8px;
            padding: 18px 20px; box-shadow: 0 1px 2px rgba(16,38,63,.04);
        }
        [data-testid="stMetricLabel"] { color: #66788a; }
        h1, h2, h3, h4 { color: #10263f; letter-spacing: -.02em; }
        .page-kicker { color:#b89a5d; font-weight:700; font-size:.78rem; letter-spacing:.14em; }
        .page-subtitle { color:#66788a; margin-top:-10px; margin-bottom:20px; }
        .watch-row {
            background:white; border:1px solid #e2e8ee; border-left:4px solid #b89a5d;
            border-radius:6px; padding:12px 14px; margin-bottom:8px;
            display:flex; justify-content:space-between; align-items:center;
        }
        .watch-row span, .watch-row small { color:#66788a; }
        .badge { padding:3px 8px; border-radius:10px; font-size:.72rem; font-weight:700; }
        .critical { background:#fde8e7; color:#a63a35; }
        .watchlist { background:#fff3da; color:#8a641e; }
        .on-track { background:#e3f3ea; color:#327452; }
        .report-box {background:white;border:1px solid #e2e8ee;border-radius:8px;padding:24px;}
        div[data-testid="stDataFrame"] { background: white; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, period: str = "Q1 2026") -> None:
    st.markdown(f'<div class="page-kicker">{period} · PORTFOLIO MONITORING</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def format_currency(value: float) -> str:
    if value >= 1000:
        return f"€{value / 1000:.2f}bn"
    return f"€{value:,.0f}m"


def status_badge(status: str) -> str:
    css_class = status.lower().replace(" ", "-")
    return f'<span class="badge {css_class}">{status}</span>'


def exposure_chart(df, category: str, title: str):
    grouped = df.groupby(category, as_index=False)["current_ev"].sum()
    fig = px.bar(
        grouped.sort_values("current_ev"),
        x="current_ev",
        y=category,
        orientation="h",
        title=title,
        labels={"current_ev": "Current enterprise value (€m)", category: ""},
        color=category,
        color_discrete_sequence=[NAVY, BLUE, GOLD, "#7994ad", "#b7c4cf"],
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10), height=330)
    return fig


def sidebar_filters(df, key: str):
    with st.sidebar:
        st.markdown("### FIVE ARROWS")
        st.caption("Portfolio Monitoring")
        st.caption("NAVIGATION")
        st.page_link("app.py", label="Command Center")
        st.page_link("pages/1_Fund_Overview.py", label="Fund Overview")
        st.page_link("pages/2_Portfolio_Companies.py", label="Portfolio Companies")
        st.page_link("pages/3_Performance_Monitoring.py", label="Performance Monitoring")
        st.page_link("pages/4_Data_Completeness.py", label="Data Completeness")
        st.page_link("pages/5_Investor_Report.py", label="Investor Report")
        st.divider()
        funds = st.multiselect("Fund", sorted(df["fund"].unique()), default=sorted(df["fund"].unique()), key=f"{key}_fund")
        sectors = st.multiselect("Sector", sorted(df["sector"].unique()), default=sorted(df["sector"].unique()), key=f"{key}_sector")
        geographies = st.multiselect("Geography", sorted(df["geography"].unique()), default=sorted(df["geography"].unique()), key=f"{key}_geo")
        st.divider()
        st.caption("Fictional data · For demonstration only")
    return df[df["fund"].isin(funds) & df["sector"].isin(sectors) & df["geography"].isin(geographies)]
