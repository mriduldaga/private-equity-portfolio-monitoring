from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@st.cache_data
def load_portfolio() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "portfolio_companies.csv")
    for column in ["entry_date", "last_updated"]:
        df[column] = pd.to_datetime(df[column])
    return df


@st.cache_data
def load_quarterly_financials() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "quarterly_financials.csv")
    df["quarter_end"] = pd.to_datetime(df["quarter_end"])
    return df


@st.cache_data
def load_fund_metadata() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "fund_metadata.csv")
