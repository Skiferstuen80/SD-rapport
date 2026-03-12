#!/usr/bin/env python3
"""
HMS-Rapport Generator

Generates HMS reports (month, quarter, or year) for Aage Haverstad AS
by fetching data from SmartDok and building a .docx document.

Usage:
  python -m hms_report --type quarter --quarter Q4 --year 2025
  python -m hms_report --type month --year 2026 --month 2
  python -m hms_report --type year --year 2025
  python -m hms_report -q Q4 -y 2025 -c hms_report/config-Q4-2025.json
"""

import argparse
import base64
import json
import sys
import time
from pathlib import Path

# Allow importing smartdok_client from parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hms_report.config import (
    MONTH_NUMBER_TO_NAME,
    create_default_config,
    get_period_label,
    get_report_type_label,
)
from hms_report.fetch_data import fetch_all_report_data
from hms_report.charts import generate_all_charts
from hms_report.build_document import build_document


def _make_filename(config: dict) -> str:
    report_type = config.get("reportType", "quarter")
    year = config["year"]

    if report_type == "month":
        month = config.get("month", 1)
        month_name = MONTH_NUMBER_TO_NAME[month]
        return f"HMS-Maanedsrapport-{month_name}-{year}.docx"
    elif report_type == "year":
        return f"HMS-Aarsrapport-{year}.docx"
    else:
        quarter = config.get("quarter", "Q4")
        return f"HMS-Kvartalsrapport-{quarter}-{year}.docx"


def main() -> None:
    parser = argparse.ArgumentParser(description="HMS-Rapport Generator")
    parser.add_argument("--type", "-t", default="quarter",
                        choices=["month", "quarter", "year"],
                        help="Rapporttype (default: quarter)")
    parser.add_argument("--quarter", "-q", default="Q4",
                        choices=["Q1", "Q2", "Q3", "Q4"],
                        help="Kvartal (kun for --type quarter)")
    parser.add_argument("--year", "-y", type=int, default=2025)
    parser.add_argument("--month", "-m", type=int, choices=range(1, 13),
                        metavar="1-12",
                        help="Maaned (kun for --type month)")
    parser.add_argument("--config", "-c", help="Sti til JSON-konfigurasjonsfil")
    parser.add_argument("--output-json", action="store_true",
                        help="Skriv JSON med base64-encoded docx til stdout")
    args = parser.parse_args()

    # Validate month argument
    if args.type == "month" and args.month is None:
        parser.error("--month kreves for --type month")

    # Load or create config
    if args.config:
        config = json.loads(Path(args.config).read_text())
        # Ensure reportType is set for older config files
        if "reportType" not in config:
            config["reportType"] = "quarter"
        if "periodLabel" not in config:
            config["periodLabel"] = get_period_label(
                config["reportType"], config["year"],
                month=config.get("month"), quarter=config.get("quarter"),
            )
        if not args.output_json:
            print(f"Lastet konfig fra {args.config}")
    else:
        config = create_default_config(
            quarter=args.quarter,
            year=args.year,
            report_type=args.type,
            month=args.month,
        )

        if not args.output_json:
            print(f"Bruker standardkonfig for {config['periodLabel']}")
            scripts_dir = Path(__file__).resolve().parent
            config_name = f"config-{args.type}"
            if args.type == "quarter":
                config_name += f"-{args.quarter}"
            elif args.type == "month":
                config_name += f"-{args.year}-{args.month:02d}"
            config_name += f"-{args.year}.json"
            default_path = scripts_dir / config_name
            default_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
            print(f"Standardkonfig skrevet til {default_path}")
            print("Rediger denne filen og kjoer med --config for aa fylle inn manuelle felt.\n")

    type_label = get_report_type_label(config.get("reportType", "quarter"))

    # When outputting JSON, redirect all print() to stderr so stdout stays clean
    if args.output_json:
        import builtins
        _real_stdout = sys.stdout
        sys.stdout = sys.stderr

    if not args.output_json:
        print("=" * 60)
        print(f"  HMS-{type_label} {config['periodLabel']}")
        print("  Aage Haverstad AS")
        print("=" * 60)

    start_time = time.time()

    # Step 1: Fetch all data
    data = fetch_all_report_data(config)

    # Step 2: Generate charts
    charts = generate_all_charts(data)

    # Step 3: Build document
    doc_bytes = build_document(data, charts)

    filename = _make_filename(config)

    if args.output_json:
        # Restore real stdout for JSON output
        sys.stdout = _real_stdout
        result = {
            "filename": filename,
            "docx_base64": base64.b64encode(doc_bytes).decode("ascii"),
        }
        sys.stdout.buffer.write(json.dumps(result).encode("utf-8"))
    else:
        # Write to file
        output_dir = Path(__file__).resolve().parent.parent / "output"
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / filename
        output_path.write_bytes(doc_bytes)

        elapsed = time.time() - start_time

        print("\n" + "=" * 60)
        print(f"  Rapport generert: {output_path}")
        print(f"  Tid brukt: {elapsed:.1f} sekunder")
        print("=" * 60)


if __name__ == "__main__":
    main()
