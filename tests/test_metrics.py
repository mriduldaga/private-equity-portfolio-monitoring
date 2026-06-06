from src.data_loader import load_fund_metadata, load_portfolio, load_quarterly_financials
from src.metrics import add_monitoring_flags, issue_summary, portfolio_kpis
from src.report_export import build_excel_report


def test_sample_data_covers_all_funds():
    portfolio = load_portfolio()

    assert len(portfolio) == 32
    assert set(portfolio["fund"]) == {"FASO", "FASA", "FAPEP", "FAGT"}
    assert len(load_quarterly_financials()) == 32
    assert len(load_fund_metadata()) == 4


def test_monitoring_rules_create_actionable_exceptions():
    monitored = add_monitoring_flags(load_portfolio())
    issues = issue_summary(monitored)

    assert monitored["issue_count"].sum() > 0
    assert monitored["stale_data"].any()
    assert monitored["high_leverage"].any()
    assert issues["companies"].sum() == monitored["issue_count"].sum()


def test_portfolio_kpis_and_excel_export():
    monitored = add_monitoring_flags(load_portfolio())
    kpis = portfolio_kpis(monitored)
    report = build_excel_report(monitored)

    assert kpis["portfolio_value"] > 0
    assert kpis["assets"] == len(monitored)
    assert 0 <= kpis["completeness"] <= 100
    assert report.startswith(b"PK")
