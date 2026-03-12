"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";

interface Metrics {
  rueMonth: number;
  rueYear: number;
  rueWeek: number;
  rueOpen: number;
  rueClosed: number;
  qdMonth: number;
  qdYear: number;
  sjaMonth: number;
  sjaYear: number;
}

interface RecentRue {
  eventId: number;
  title: string;
  severity: string;
  status: string;
  date: string;
}

interface MonthlyTrend {
  month: string;
  count: number;
}

interface DashboardData {
  updatedAt: string;
  year: number;
  month: number;
  metrics: Metrics;
  recentRue: RecentRue[];
  monthlyTrend: MonthlyTrend[];
  error?: string;
}

const monthNames = [
  "", "Januar", "Februar", "Mars", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Desember",
];

const severityColor: Record<string, string> = {
  High: "#ef4444",
  Medium: "#f59e0b",
  Low: "#22c55e",
};

const statusLabel: Record<string, string> = {
  Close: "Lukket",
  Open: "Åpen",
  New: "Ny",
  Discarded: "Forkastet",
  Unprocessed: "Ubehandlet",
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString("nb-NO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function msUntilNext0700(): number {
  const now = new Date();
  const next = new Date(now);
  next.setHours(7, 0, 0, 0);
  if (now >= next) next.setDate(next.getDate() + 1);
  return next.getTime() - now.getTime();
}

export default function DashboardPage() {
  const params = useParams();
  const token = params.token as string;
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`/api/dashboard?token=${encodeURIComponent(token)}`);
      const json = await res.json();
      if (!res.ok || json.error) {
        setError(json.error || `Feil: ${res.status}`);
        return;
      }
      setData(json);
      setError(null);
    } catch {
      setError("Kunne ikke hente data");
    }
  }, [token]);

  useEffect(() => {
    fetchData();

    // Refresh every hour
    const hourly = setInterval(fetchData, 60 * 60 * 1000);

    // Schedule refresh at 07:00
    const timeout = setTimeout(() => {
      fetchData();
      // Then every 24h
      const daily = setInterval(fetchData, 24 * 60 * 60 * 1000);
      return () => clearInterval(daily);
    }, msUntilNext0700());

    return () => {
      clearInterval(hourly);
      clearTimeout(timeout);
    };
  }, [fetchData]);

  if (error) {
    return (
      <div style={styles.container}>
        <p style={{ color: "#ef4444", fontSize: "2rem", textAlign: "center" }}>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={styles.container}>
        <p style={{ color: "#94a3b8", fontSize: "2rem", textAlign: "center" }}>Laster...</p>
      </div>
    );
  }

  const m = data.metrics;
  const maxTrend = Math.max(...data.monthlyTrend.map((t) => t.count), 1);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <img src="/logo.svg" alt="Åge Haverstad AS" style={{ height: "60px" }} />
          <h1 style={styles.title}>HMS-oversikt</h1>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={styles.period}>{monthNames[data.month]} {data.year}</p>
          <p style={styles.updated}>Oppdatert: {formatTime(data.updatedAt)}</p>
        </div>
      </div>

      {/* Metric cards */}
      <div style={styles.cardsRow}>
        <MetricCard label="RUH denne måned" value={m.rueMonth} color="#3b82f6" />
        <MetricCard label="RUH forrige uke" value={m.rueWeek} color="#6366f1" />
        <MetricCard label="Kvalitetsavvik" value={m.qdMonth} color="#f59e0b" />
        <MetricCard label="SJA denne måned" value={m.sjaMonth} color="#22c55e" />
      </div>

      {/* Year totals + status */}
      <div style={styles.cardsRow}>
        <MetricCard label={`RUH ${data.year}`} value={m.rueYear} color="#1e40af" />
        <MetricCard label="Åpne RUH" value={m.rueOpen} color="#ef4444" />
        <MetricCard label="Lukkede RUH" value={m.rueClosed} color="#16a34a" />
        <MetricCard label={`Kvalitetsavvik ${data.year}`} value={m.qdYear} color="#d97706" />
        <MetricCard label={`SJA ${data.year}`} value={m.sjaYear} color="#059669" />
      </div>

      {/* Bottom row: trend + recent events */}
      <div style={styles.bottomRow}>
        {/* Monthly trend chart */}
        <div style={styles.chartCard}>
          <h2 style={styles.sectionTitle}>RUH per måned {data.year}</h2>
          <div style={styles.barChart}>
            {data.monthlyTrend.map((t) => (
              <div key={t.month} style={styles.barCol}>
                <span style={styles.barValue}>{t.count}</span>
                <div
                  style={{
                    ...styles.bar,
                    height: `${Math.max((t.count / maxTrend) * 100, 4)}%`,
                  }}
                />
                <span style={styles.barLabel}>{t.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent events */}
        <div style={styles.tableCard}>
          <h2 style={styles.sectionTitle}>Siste hendelser</h2>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>#</th>
                <th style={{ ...styles.th, textAlign: "left" }}>Tittel</th>
                <th style={styles.th}>Alv.</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Dato</th>
              </tr>
            </thead>
            <tbody>
              {data.recentRue.map((r) => (
                <tr key={r.eventId}>
                  <td style={styles.td}>{r.eventId}</td>
                  <td style={{ ...styles.td, textAlign: "left", maxWidth: "400px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {r.title}
                  </td>
                  <td style={{ ...styles.td, color: severityColor[r.severity] || "#94a3b8", fontWeight: 700 }}>
                    {r.severity}
                  </td>
                  <td style={styles.td}>{statusLabel[r.status] || r.status}</td>
                  <td style={styles.td}>{r.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ ...styles.card, borderTop: `4px solid ${color}` }}>
      <p style={styles.cardValue}>{value}</p>
      <p style={styles.cardLabel}>{label}</p>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#0f172a",
    color: "#f1f5f9",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
    padding: "2rem 2.5rem",
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  title: {
    fontSize: "2.5rem",
    fontWeight: 700,
    margin: 0,
    color: "#f8fafc",
  },
  period: {
    fontSize: "1.5rem",
    fontWeight: 600,
    margin: 0,
    color: "#e2e8f0",
  },
  updated: {
    fontSize: "0.9rem",
    color: "#64748b",
    margin: "0.25rem 0 0",
  },
  cardsRow: {
    display: "flex",
    gap: "1rem",
  },
  card: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "1.25rem 1.5rem",
    textAlign: "center" as const,
  },
  cardValue: {
    fontSize: "3rem",
    fontWeight: 800,
    margin: 0,
    color: "#f8fafc",
    lineHeight: 1.1,
  },
  cardLabel: {
    fontSize: "0.95rem",
    color: "#94a3b8",
    margin: "0.5rem 0 0",
  },
  bottomRow: {
    display: "flex",
    gap: "1.5rem",
    flex: 1,
    minHeight: 0,
  },
  chartCard: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "1.5rem",
    display: "flex",
    flexDirection: "column" as const,
  },
  tableCard: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "1.5rem",
    overflow: "auto",
  },
  sectionTitle: {
    fontSize: "1.1rem",
    fontWeight: 600,
    margin: "0 0 1rem",
    color: "#cbd5e1",
  },
  barChart: {
    display: "flex",
    alignItems: "flex-end",
    gap: "0.5rem",
    flex: 1,
    minHeight: "150px",
  },
  barCol: {
    flex: 1,
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "0.3rem",
    height: "100%",
    justifyContent: "flex-end",
  },
  barValue: {
    fontSize: "0.85rem",
    fontWeight: 600,
    color: "#94a3b8",
  },
  bar: {
    width: "100%",
    maxWidth: "48px",
    backgroundColor: "#3b82f6",
    borderRadius: "4px 4px 0 0",
    transition: "height 0.5s ease",
  },
  barLabel: {
    fontSize: "0.8rem",
    color: "#64748b",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    fontSize: "1rem",
  },
  th: {
    padding: "0.6rem 0.75rem",
    borderBottom: "2px solid #334155",
    color: "#94a3b8",
    fontWeight: 600,
    textAlign: "center" as const,
    fontSize: "0.9rem",
  },
  td: {
    padding: "0.6rem 0.75rem",
    borderBottom: "1px solid #1e293b",
    textAlign: "center" as const,
    color: "#e2e8f0",
  },
};
