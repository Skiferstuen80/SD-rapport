"""
Vercel Python Serverless Function for HMS report generation.

POST /api/hms-report
Body: { "reportType": "quarter"|"month"|"year", "year": 2025, "quarter?": "Q4", "month?": 3 }
Returns: .docx file as binary download
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hms_report.config import create_default_config, MONTH_NUMBER_TO_NAME
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


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length else {}

            report_type = body.get("reportType", "quarter")
            year = int(body.get("year", 2025))
            quarter = body.get("quarter", "Q4")
            month = body.get("month")
            if month is not None:
                month = int(month)

            config = create_default_config(
                quarter=quarter,
                year=year,
                report_type=report_type,
                month=month,
            )

            data = fetch_all_report_data(config)
            charts = generate_all_charts(data)
            doc_bytes = build_document(data, charts)
            filename = _make_filename(config)

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(doc_bytes)))
            self.end_headers()
            self.wfile.write(doc_bytes)

        except Exception as e:
            error_body = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
