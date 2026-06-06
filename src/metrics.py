from datetime import date

import numpy as np
import pandas as pd


AS_OF_DATE = pd.Timestamp("2026-03-31")
REQUIRED_FIELDS = [
    "revenue",
    "ebitda",
    "revenue_growth",
    "ebitda_margin",
    "net_debt",
    "valuation_multiple",
]


def add_monitoring_flags(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["days_since_update"] = (AS_OF_DATE - result["last_updated"]).dt.days
    result["missing_financials"] = result[REQUIRED_FIELDS].isna().any(axis=1)
    result["revenue_decline"] = result["revenue_growth"] < -10
    result["margin_compression"] = result["margin_change"] < -3
    result["high_leverage"] = result["net_debt_ebitda"] > 5
    result["multiple_contraction"] = result["multiple_change"] < -1
    result["stale_data"] = result["days_since_update"] > 90
    flag_columns = [
        "missing_financials",
        "revenue_decline",
        "margin_compression",
        "high_leverage",
        "multiple_contraction",
        "stale_data",
    ]
    result["issue_count"] = result[flag_columns].sum(axis=1)
    result["monitoring_status"] = np.select(
        [result["issue_count"] >= 3, result["issue_count"] >= 1],
        ["Critical", "Watchlist"],
        default="On track",
    )
    issue_names = {
        "missing_financials": "Missing quarterly financials",
        "revenue_decline": "Revenue decline >10%",
        "margin_compression": "EBITDA margin compression",
        "high_leverage": "High leverage",
        "multiple_contraction": "Valuation multiple contraction",
        "stale_data": "Data not updated in 90 days",
    }
    result["primary_issue"] = result.apply(
        lambda row: next(
            (label for column, label in issue_names.items() if row[column]),
            "No exceptions",
        ),
        axis=1,
    )
    result["data_completeness"] = 100 * (1 - result[REQUIRED_FIELDS].isna().sum(axis=1) / len(REQUIRED_FIELDS))
    return result


def portfolio_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return dict(
            portfolio_value=0,
            value_change=0,
            assets=0,
            watchlist=0,
            avg_growth=0,
            growth_delta=0,
            completeness=0,
            stale=0,
        )
    return {
        "portfolio_value": df["current_ev"].sum(),
        "value_change": (df["current_ev"].sum() / df["entry_ev"].sum() - 1) * 100,
        "assets": len(df),
        "watchlist": int((df["issue_count"] > 0).sum()),
        "avg_growth": df["revenue_growth"].mean(),
        "growth_delta": (df["revenue_growth"] - df["revenue_growth_plan"]).mean(),
        "completeness": df["data_completeness"].mean(),
        "stale": int(df["stale_data"].sum()),
    }


def issue_summary(df: pd.DataFrame) -> pd.DataFrame:
    issues = {
        "Missing quarterly financials": "missing_financials",
        "Revenue decline >10%": "revenue_decline",
        "EBITDA margin compression": "margin_compression",
        "High leverage": "high_leverage",
        "Valuation multiple contraction": "multiple_contraction",
        "Data not updated in 90 days": "stale_data",
    }
    return pd.DataFrame(
        [{"issue": label, "companies": int(df[column].sum())} for label, column in issues.items()]
    ).sort_values("companies", ascending=False)


def quarterly_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("fund", as_index=False)
        .agg(
            portfolio_value=("current_ev", "sum"),
            assets=("company_name", "count"),
            avg_revenue_growth=("revenue_growth", "mean"),
            avg_ebitda_margin=("ebitda_margin", "mean"),
            watchlist_assets=("issue_count", lambda x: int((x > 0).sum())),
            data_completeness=("data_completeness", "mean"),
        )
    )
