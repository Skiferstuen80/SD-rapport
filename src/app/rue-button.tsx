"use client";

import { useState } from "react";

interface RueItem {
  Id: number;
  EventId: number;
  Title: string;
  Status: string;
  Severity: string;
  EventTime: string;
  SubmitDate: string;
}

interface RueResponse {
  items: RueItem[];
  weekStart: string;
  weekEnd: string;
  totalFetched: number;
  totalFiltered: number;
  error?: string;
}

const severityColor: Record<string, string> = {
  High: "#dc2626",
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

export default function RueButton() {
  const [data, setData] = useState<RueResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFetch() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/rue");
      const json: RueResponse = await res.json();
      if (!res.ok || json.error) {
        setError(json.error || `Feil: ${res.status}`);
        setData(null);
      } else {
        setData(json);
      }
    } catch {
      setError("Kunne ikke koble til serveren");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: "2rem" }}>
      <button
        onClick={handleFetch}
        disabled={loading}
        style={{
          padding: "0.6rem 1.2rem",
          fontSize: "1rem",
          backgroundColor: loading ? "#94a3b8" : "#2563eb",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Henter..." : "Hent RUH forrige uke"}
      </button>

      {error && (
        <p style={{ color: "#dc2626", marginTop: "1rem" }}>{error}</p>
      )}

      {data && (
        <div style={{ marginTop: "1.5rem" }}>
          <p style={{ color: "#666", marginBottom: "0.5rem" }}>
            Uke {data.weekStart} – {data.weekEnd} ({data.totalFiltered} hendelser)
          </p>

          {data.items.length === 0 ? (
            <p>Ingen RUH-hendelser forrige uke.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  fontSize: "0.9rem",
                }}
              >
                <thead>
                  <tr
                    style={{
                      borderBottom: "2px solid #e2e8f0",
                      textAlign: "left",
                    }}
                  >
                    <th style={{ padding: "0.5rem" }}>#</th>
                    <th style={{ padding: "0.5rem" }}>Tittel</th>
                    <th style={{ padding: "0.5rem" }}>Alvorlighet</th>
                    <th style={{ padding: "0.5rem" }}>Status</th>
                    <th style={{ padding: "0.5rem" }}>Hendelsestid</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr
                      key={item.Id}
                      style={{ borderBottom: "1px solid #e2e8f0" }}
                    >
                      <td style={{ padding: "0.5rem" }}>{item.EventId}</td>
                      <td style={{ padding: "0.5rem" }}>{item.Title}</td>
                      <td style={{ padding: "0.5rem" }}>
                        <span
                          style={{
                            color: severityColor[item.Severity] || "#666",
                            fontWeight: 600,
                          }}
                        >
                          {item.Severity}
                        </span>
                      </td>
                      <td style={{ padding: "0.5rem" }}>
                        {statusLabel[item.Status] || item.Status}
                      </td>
                      <td style={{ padding: "0.5rem" }}>
                        {new Date(item.EventTime).toLocaleString("nb-NO", {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
