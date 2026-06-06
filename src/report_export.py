from io import BytesIO

import pandas as pd

from src.metrics import issue_summary, quarterly_snapshot


def build_excel_report(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book
        header = workbook.add_format({"bold": True, "font_color": "white", "bg_color": "#10263F", "border": 0})
        title = workbook.add_format({"bold": True, "font_size": 18, "font_color": "#10263F"})
        percent = workbook.add_format({"num_format": "0.0%"})
        money = workbook.add_format({"num_format": '€0.0"m"'})

        snapshot = quarterly_snapshot(df)
        snapshot.to_excel(writer, sheet_name="Fund Snapshot", index=False, startrow=3)
        sheet = writer.sheets["Fund Snapshot"]
        sheet.write("A1", "Quarterly Fund Snapshot · Q1 2026", title)
        sheet.set_column("A:A", 14)
        sheet.set_column("B:B", 18, money)
        sheet.set_column("C:G", 20)

        export_columns = [
            "company_name", "fund", "sector", "geography", "status", "current_ev",
            "revenue_growth", "ebitda_margin", "net_debt_ebitda", "valuation_multiple",
            "monitoring_status", "primary_issue", "last_updated", "data_completeness",
        ]
        df[export_columns].to_excel(writer, sheet_name="Portfolio Companies", index=False)
        company_sheet = writer.sheets["Portfolio Companies"]
        company_sheet.set_column("A:E", 19)
        company_sheet.set_column("F:N", 21)

        issues = issue_summary(df)
        issues.to_excel(writer, sheet_name="Monitoring Exceptions", index=False)
        writer.sheets["Monitoring Exceptions"].set_column("A:A", 38)

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(1, worksheet.dim_rowmax), worksheet.dim_colmax)
            for col, value in enumerate(worksheet.table.get("columns", [])):
                worksheet.write(0, col, value, header)
    return output.getvalue()
