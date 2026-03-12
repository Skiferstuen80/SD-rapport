"use client";

import { useState } from "react";

type ReportType = "month" | "quarter" | "year";

const MONTHS = [
  "Januar", "Februar", "Mars", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Desember",
];

const YEARS = [2024, 2025, 2026];
const QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

export default function HmsReportPanel() {
  const [reportType, setReportType] = useState<ReportType>("quarter");
  const [year, setYear] = useState(2025);
  const [quarter, setQuarter] = useState("Q4");
  const [month, setMonth] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);

    try {
      const body: Record<string, string | number> = { reportType, year };
      if (reportType === "quarter") body.quarter = quarter;
      if (reportType === "month") body.month = month;

      const res = await fetch("/api/hms-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.error || `Feil: ${res.status}`);
      }

      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      let filename = "HMS-Rapport.docx";
      if (disposition) {
        const match = disposition.match(/filename="(.+?)"/);
        if (match) filename = match[1];
      }

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ukjent feil");
    } finally {
      setLoading(false);
    }
  }

  const btnBase: React.CSSProperties = {
    padding: "0.5rem 1rem",
    fontSize: "0.9rem",
    border: "2px solid #2563eb",
    borderRadius: "6px",
    cursor: "pointer",
    transition: "all 0.15s",
  };

  const btnActive: React.CSSProperties = {
    ...btnBase,
    backgroundColor: "#2563eb",
    color: "#fff",
  };

  const btnInactive: React.CSSProperties = {
    ...btnBase,
    backgroundColor: "#fff",
    color: "#2563eb",
  };

  const selectStyle: React.CSSProperties = {
    padding: "0.5rem",
    fontSize: "0.9rem",
    borderRadius: "6px",
    border: "1px solid #cbd5e1",
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2 style={{ marginBottom: "1rem", fontSize: "1.2rem" }}>HMS-rapport</h2>

      {/* Report type selector */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {(["month", "quarter", "year"] as ReportType[]).map((t) => {
          const labels: Record<ReportType, string> = {
            month: "Måned",
            quarter: "Kvartal",
            year: "År",
          };
          return (
            <button
              key={t}
              onClick={() => setReportType(t)}
              style={reportType === t ? btnActive : btnInactive}
            >
              {labels[t]}
            </button>
          );
        })}
      </div>

      {/* Period selectors */}
      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginBottom: "1rem" }}>
        <label>
          År:{" "}
          <select value={year} onChange={(e) => setYear(Number(e.target.value))} style={selectStyle}>
            {YEARS.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>

        {reportType === "quarter" && (
          <label>
            Kvartal:{" "}
            <select value={quarter} onChange={(e) => setQuarter(e.target.value)} style={selectStyle}>
              {QUARTERS.map((q) => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
          </label>
        )}

        {reportType === "month" && (
          <label>
            Måned:{" "}
            <select value={month} onChange={(e) => setMonth(Number(e.target.value))} style={selectStyle}>
              {MONTHS.map((m, i) => (
                <option key={i + 1} value={i + 1}>{m}</option>
              ))}
            </select>
          </label>
        )}
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={loading}
        style={{
          padding: "0.6rem 1.5rem",
          fontSize: "1rem",
          backgroundColor: loading ? "#94a3b8" : "#16a34a",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Genererer rapport..." : "Generer rapport"}
      </button>

      {error && (
        <p style={{ color: "#dc2626", marginTop: "1rem" }}>{error}</p>
      )}
    </div>
  );
}
