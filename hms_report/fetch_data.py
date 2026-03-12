"""Fetch and aggregate all data needed for the HMS report."""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Allow importing smartdok_client from parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartdok_client import (
    get_forms,
    get_projects,
    get_qd_list_v2,
    get_rue_detail,
    get_rue_summaries,
    get_sja_overview,
    get_users,
)

from .config import ALL_MONTHS, MONTH_NUMBER_TO_NAME, get_months_for_type
from .translations import translate_classification, translate_rue_status


# ---- Helpers ----

def _in_range(date_str: str, start: str, end: str) -> bool:
    d = date_str[:10]
    return start <= d <= end


def _month_key(date_str: str) -> str:
    return date_str[:7]  # "YYYY-MM"


def _split_classification(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _inc(m: dict[str, int], key: str) -> None:
    m[key] = m.get(key, 0) + 1


def _init_monthly(config: dict) -> list[dict]:
    """Initialize monthly count entries for the report period."""
    report_type = config.get("reportType", "quarter")
    month_names = get_months_for_type(
        report_type,
        config["year"],
        month=config.get("month"),
        quarter=config.get("quarter"),
    )
    start_month = int(config["dateRange"]["start"][5:7])
    return [
        {"month": f"{config['year']}-{start_month + i:02d}", "label": label, "count": 0}
        for i, label in enumerate(month_names)
    ]


def _prev_month(config: dict) -> dict:
    """Get month entry for the month before the report period starts."""
    start_month = int(config["dateRange"]["start"][5:7])
    prev = start_month - 1
    if prev < 1:
        return {
            "month": f"{config['year'] - 1}-12",
            "label": MONTH_NUMBER_TO_NAME[12],
            "count": 0,
        }
    return {
        "month": f"{config['year']}-{prev:02d}",
        "label": MONTH_NUMBER_TO_NAME[prev],
        "count": 0,
    }


def _format_project(project_map: dict, project_id: int) -> str:
    p = project_map.get(project_id)
    if not p:
        return f"Prosjekt {project_id}"
    return f"{p['number']} {p['name']}" if p["number"] else p["name"]


# ---- RUE classification extraction from detail ----

def _extract_classification(detail: dict, cls_type: str) -> str:
    for group in detail.get("Values", []):
        if group.get("Type") == cls_type and group.get("Values"):
            return translate_classification(cls_type, group["Values"][0]["Name"])
    return ""


# ---- Data fetchers ----

def _fetch_reference_data() -> tuple[dict[int, dict], int]:
    print("  Henter prosjekter og brukere...")
    projects = get_projects()
    users = get_users()

    project_map: dict[int, dict] = {}
    for p in projects:
        project_map[p["Id"]] = {
            "name": p["ProjectName"].strip(),
            "number": (p.get("ProjectNumber") or "").strip(),
        }

    active = sum(1 for u in users if not u.get("IsEnded") and not u.get("IsDeleted"))
    print(f"  {len(projects)} prosjekter, {active} aktive ansatte")
    return project_map, active


def _fetch_rue_data(config: dict, project_map: dict) -> dict:
    start, end = config["dateRange"]["start"], config["dateRange"]["end"]

    print("  Henter RUE-oversikter...")
    all_summaries = get_rue_summaries()
    filtered = [r for r in all_summaries if _in_range(r["SubmitDate"], start, end)]
    print(f"  Fant {len(filtered)} RUE i perioden (av {len(all_summaries)} totalt)")

    # Fetch details with concurrency
    print(f"  Henter {len(filtered)} RUE-detaljer (5 parallelle)...")
    details: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(get_rue_detail, r["Id"]): r["Id"] for r in filtered}
        for future in as_completed(futures):
            rid = futures[future]
            details[rid] = future.result()

    by_status: dict[str, int] = {}
    by_event_type: dict[str, int] = {}
    by_event_involved: dict[str, int] = {}
    by_cause: dict[str, int] = {}

    prev = _prev_month(config)
    period_months = _init_monthly(config)
    by_month = [prev] + period_months
    rows: list[dict] = []

    # Count previous month
    prev_start = prev["month"] + "-01"
    prev_end = prev["month"] + "-31"
    for s in all_summaries:
        if _in_range(s["SubmitDate"], prev_start, prev_end):
            prev["count"] += 1

    for summary in filtered:
        detail = details[summary["Id"]]

        _inc(by_status, translate_rue_status(summary["Status"]))

        et = _extract_classification(detail, "EventType")
        ei = _extract_classification(detail, "EventInvolved")
        ce = _extract_classification(detail, "CauseOfEvent")
        if et:
            _inc(by_event_type, et)
        if ei:
            _inc(by_event_involved, ei)
        if ce:
            _inc(by_cause, ce)

        mk = _month_key(summary["SubmitDate"])
        for m in by_month:
            if m["month"] == mk:
                m["count"] += 1
                break

        rows.append({
            "id": summary["Id"],
            "eventId": summary["EventId"],
            "title": summary["Title"],
            "status": translate_rue_status(summary["Status"]),
            "severity": summary.get("Severity", ""),
            "submitDate": summary["SubmitDate"],
            "eventTime": summary.get("EventTime"),
            "projectName": _format_project(project_map, summary["ProjectId"]),
            "eventType": et,
            "eventInvolved": ei,
            "causeOfEvent": ce,
        })

    rows.sort(key=lambda r: r["submitDate"], reverse=True)

    return {
        "total": len(filtered),
        "byStatus": by_status,
        "byEventType": by_event_type,
        "byEventInvolved": by_event_involved,
        "byCauseOfEvent": by_cause,
        "byMonth": by_month,
        "rows": rows,
    }


def _fetch_qd_data(config: dict, project_map: dict) -> dict:
    start, end = config["dateRange"]["start"], config["dateRange"]["end"]

    print("  Henter QD v2-liste...")
    all_qd = get_qd_list_v2()
    filtered = [q for q in all_qd if _in_range(q["SubmitDate"], start, end)]
    print(f"  Fant {len(filtered)} QD i perioden (av {len(all_qd)} totalt)")

    by_status: dict[str, int] = {}
    by_concerning: dict[str, int] = {}
    by_relates_to: dict[str, int] = {}
    by_cause: dict[str, int] = {}
    by_month = _init_monthly(config)
    rows: list[dict] = []

    for qd in filtered:
        _inc(by_status, qd["Status"])
        for v in _split_classification(qd.get("Concerning")):
            _inc(by_concerning, v)
        for v in _split_classification(qd.get("RelatesTo")):
            _inc(by_relates_to, v)
        for v in _split_classification(qd.get("Cause")):
            _inc(by_cause, v)

        mk = _month_key(qd["SubmitDate"])
        for m in by_month:
            if m["month"] == mk:
                m["count"] += 1
                break

        rows.append({
            "id": qd["Id"],
            "eventId": qd["EventId"],
            "title": qd["Title"],
            "status": qd["Status"],
            "submitDate": qd["SubmitDate"],
            "eventTime": qd.get("EventTime"),
            "projectName": _format_project(project_map, qd["ProjectId"]),
            "concerning": qd.get("Concerning", ""),
            "relatesTo": qd.get("RelatesTo", ""),
            "cause": qd.get("Cause", ""),
        })

    rows.sort(key=lambda r: r["submitDate"], reverse=True)

    return {
        "total": len(filtered),
        "byStatus": by_status,
        "byConcerning": by_concerning,
        "byRelatesTo": by_relates_to,
        "byCause": by_cause,
        "byMonth": by_month,
        "rows": rows,
    }


def _fetch_sja_data(config: dict) -> dict:
    start, end = config["dateRange"]["start"], config["dateRange"]["end"]

    print("  Henter SJA-oversikt...")
    sja_list = get_sja_overview(start, end)
    print(f"  Raa SJA fra API: {len(sja_list)}")

    # API ignores date filter — must filter client-side
    filtered = [
        s for s in sja_list
        if s.get("SubmittedDate") and _in_range(s["SubmittedDate"], start, end)
    ]
    print(f"  Fant {len(filtered)} SJA i perioden (etter datofiltrering)")

    by_month = _init_monthly(config)
    for sja in filtered:
        mk = _month_key(sja["SubmittedDate"])
        for m in by_month:
            if m["month"] == mk:
                m["count"] += 1
                break

    return {"total": len(filtered), "byMonth": by_month}


def _fetch_vernerunde_data(config: dict) -> dict:
    start, end = config["dateRange"]["start"], config["dateRange"]["end"]

    print("  Henter Forms for Vernerunde...")
    forms = get_forms(start, end)
    vernerunder = [f for f in forms if "vernerunde" in f.get("DefFormName", "").lower()]
    print(f"  Fant {len(vernerunder)} Vernerunder (av {len(forms)} totalt)")

    by_month = _init_monthly(config)
    for form in vernerunder:
        mk = _month_key(form["FilledOutDate"])
        for m in by_month:
            if m["month"] == mk:
                m["count"] += 1
                break

    return {"total": len(vernerunder), "byMonth": by_month}


def _build_monthly_summary(
    config: dict,
    all_rue: list[dict],
    all_qd: list[dict],
    all_sja: list[dict],
    all_forms: list[dict],
    active_employees: int,
) -> list[dict]:
    year = config["year"]
    rows = []

    for i, month_name in enumerate(ALL_MONTHS):
        month_num = i + 1
        month_key = f"{year}-{month_num:02d}"
        month_start = f"{month_key}-01"
        month_end = f"{month_key}-31"

        ruh = sum(1 for r in all_rue if _in_range(r["SubmitDate"], month_start, month_end))
        qa = sum(1 for q in all_qd if _in_range(q["SubmitDate"], month_start, month_end))
        sja = sum(
            1 for s in all_sja
            if s.get("SubmittedDate") and _in_range(s["SubmittedDate"], month_start, month_end)
        )
        vr = sum(
            1 for f in all_forms
            if "vernerunde" in f.get("DefFormName", "").lower()
            and _in_range(f["FilledOutDate"], month_start, month_end)
        )

        sf = config["manual"]["sykefravær"][i]
        n_employees = sf.get("antallAnsatte") or active_employees
        ruh_freq = f"{ruh / n_employees:.2f}" if n_employees > 0 else "0.00"

        rows.append({
            "month": month_name,
            "ruh": ruh,
            "ruhFrequency": ruh_freq,
            "sja": sja,
            "vernerunder": vr,
            "kvalitetsavvik": qa,
            "sykefraværProsent": sf.get("fraværProsent", 0),
            "antallAnsatte": n_employees,
        })

    return rows


# ---- Main orchestrator ----

def fetch_all_report_data(config: dict) -> dict:
    period_label = config.get("periodLabel", f"{config.get('quarter', '')} {config['year']}")
    print(f"\nHenter data for {period_label}...")
    print(f"Periode: {config['dateRange']['start']} -> {config['dateRange']['end']}\n")

    # Step 1: Reference data
    print("Steg 1: Referansedata")
    project_map, active_employees = _fetch_reference_data()

    # Step 2: Event data
    print("\nSteg 2: Hendelsesdata")
    rue = _fetch_rue_data(config, project_map)
    qd = _fetch_qd_data(config, project_map)
    sja = _fetch_sja_data(config)
    vernerunder = _fetch_vernerunde_data(config)

    # Step 3: Full-year data for monthly summary (section 8)
    print("\nSteg 3: Henter helarsdata for maanedsoversikt...")
    full_year_start = f"{config['year']}-01-01"
    full_year_end = f"{config['year']}-12-31"

    all_rue = get_rue_summaries()
    all_qd = get_qd_list_v2()
    all_sja = get_sja_overview(full_year_start, full_year_end)
    all_forms = get_forms(full_year_start, full_year_end)

    fy_rue = [r for r in all_rue if _in_range(r["SubmitDate"], full_year_start, full_year_end)]
    fy_qd = [q for q in all_qd if _in_range(q["SubmitDate"], full_year_start, full_year_end)]
    print(f"  Helaar: {len(fy_rue)} RUE, {len(fy_qd)} QD, {len(all_sja)} SJA (raa), {len(all_forms)} forms")

    # Step 4: Build monthly summary
    print("\nSteg 4: Bygger maanedsoversikt (12 maaneder)")
    monthly = _build_monthly_summary(config, fy_rue, fy_qd, all_sja, all_forms, active_employees)

    print(f"\nDatahenting fullfoert!")
    print(f"  RUH: {rue['total']}, QD: {qd['total']}, SJA: {sja['total']}, Vernerunder: {vernerunder['total']}")

    return {
        "config": config,
        "rue": rue,
        "qd": qd,
        "sja": sja,
        "vernerunder": vernerunder,
        "monthlySummary": monthly,
        "activeEmployees": active_employees,
        "projectMap": project_map,
    }
