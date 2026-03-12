"""Configuration and constants for HMS reports (month, quarter, year)."""

from __future__ import annotations

import calendar
from typing import Any, Literal

Quarter = Literal["Q1", "Q2", "Q3", "Q4"]
ReportType = Literal["month", "quarter", "year"]

QUARTER_DATES: dict[str, Any] = {
    "Q1": lambda y: {"start": f"{y}-01-01", "end": f"{y}-03-31"},
    "Q2": lambda y: {"start": f"{y}-04-01", "end": f"{y}-06-30"},
    "Q3": lambda y: {"start": f"{y}-07-01", "end": f"{y}-09-30"},
    "Q4": lambda y: {"start": f"{y}-10-01", "end": f"{y}-12-31"},
}

QUARTER_MONTHS: dict[str, list[str]] = {
    "Q1": ["Januar", "Februar", "Mars"],
    "Q2": ["April", "Mai", "Juni"],
    "Q3": ["Juli", "August", "September"],
    "Q4": ["Oktober", "November", "Desember"],
}

MONTH_NUMBER_TO_NAME: dict[int, str] = {
    1: "Januar", 2: "Februar", 3: "Mars", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

ALL_MONTHS = [
    "Januar", "Februar", "Mars", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Desember",
]


def get_date_range(quarter: Quarter, year: int) -> dict[str, str]:
    return QUARTER_DATES[quarter](year)


def get_date_range_for_type(
    report_type: ReportType,
    year: int,
    month: int | None = None,
    quarter: Quarter | None = None,
) -> dict[str, str]:
    """Return start/end date strings for any report type."""
    if report_type == "month":
        if month is None:
            raise ValueError("month kreves for rapporttype 'month'")
        last_day = calendar.monthrange(year, month)[1]
        return {"start": f"{year}-{month:02d}-01", "end": f"{year}-{month:02d}-{last_day}"}
    elif report_type == "quarter":
        if quarter is None:
            raise ValueError("quarter kreves for rapporttype 'quarter'")
        return QUARTER_DATES[quarter](year)
    else:  # year
        return {"start": f"{year}-01-01", "end": f"{year}-12-31"}


def get_months_for_type(
    report_type: ReportType,
    year: int,
    month: int | None = None,
    quarter: Quarter | None = None,
) -> list[str]:
    """Return list of Norwegian month names for the report period."""
    if report_type == "month":
        return [MONTH_NUMBER_TO_NAME[month]]
    elif report_type == "quarter":
        return QUARTER_MONTHS[quarter]
    else:  # year
        return list(ALL_MONTHS)


def get_period_label(
    report_type: ReportType,
    year: int,
    month: int | None = None,
    quarter: Quarter | None = None,
) -> str:
    """Human-readable period label for titles and filenames."""
    if report_type == "month":
        return f"{MONTH_NUMBER_TO_NAME[month]} {year}"
    elif report_type == "quarter":
        return f"{quarter} {year}"
    else:
        return str(year)


def get_report_title(report_type: ReportType) -> str:
    """Return the report title based on type."""
    titles = {
        "month": "HMS-MAANEDSRAPPORT",
        "quarter": "HMS-KVARTALSRAPPORT",
        "year": "HMS-AARSRAPPORT",
    }
    return titles[report_type]


def get_report_type_label(report_type: ReportType) -> str:
    """Norwegian label for the report type."""
    labels = {
        "month": "Maanedsrapport",
        "quarter": "Kvartalsrapport",
        "year": "Aarsrapport",
    }
    return labels[report_type]


def create_default_config(
    quarter: Quarter = "Q4",
    year: int = 2025,
    report_type: ReportType = "quarter",
    month: int | None = None,
) -> dict:
    date_range = get_date_range_for_type(report_type, year, month=month, quarter=quarter)
    return {
        "reportType": report_type,
        "quarter": quarter,
        "year": year,
        "month": month,
        "dateRange": date_range,
        "periodLabel": get_period_label(report_type, year, month=month, quarter=quarter),
        "utarbeidetAv": "[Fyll inn navn]",
        "manual": {
            "kortStatus": "[Fyll inn kort status for perioden]",
            "sykefravær": [
                {
                    "month": m,
                    "sykmeldinger": 0,
                    "egenmeldinger": 0,
                    "fraværProsent": 0,
                    "antallAnsatte": 0,
                }
                for m in ALL_MONTHS
            ],
            "nøkkelaktiviteter": {
                "vernerunder": {"antall": 0, "kommentar": ""},
                "hmsMøte": {"gjennomført": False, "kommentar": ""},
                "risikovurdering": {"gjennomført": False, "kommentar": ""},
            },
            "tiltakNesteKvartal": ["[Fyll inn tiltak]"],
        },
    }
