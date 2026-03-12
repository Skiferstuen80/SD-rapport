import { NextRequest, NextResponse } from "next/server";

const BASE_URL = process.env.SMARTDOK_BASE_URL || "https://api.smartdok.no";
const DASHBOARD_TOKEN = process.env.DASHBOARD_TOKEN || "";

async function getSessionToken(): Promise<string> {
  const apiToken = process.env.SMARTDOK_API_TOKEN;
  if (!apiToken) throw new Error("SMARTDOK_API_TOKEN is not configured");

  const res = await fetch(`${BASE_URL}/Authorize/ApiToken`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Token: apiToken }),
  });
  if (!res.ok) throw new Error(`Auth failed: ${res.status}`);
  const token = await res.text();
  return token.replace(/"/g, "");
}

async function fetchAllPages(
  sessionToken: string,
  endpoint: string,
  params: Record<string, string> = {}
): Promise<unknown[]> {
  const allItems: unknown[] = [];
  let offset = 0;
  const count = 100;

  while (true) {
    const query = new URLSearchParams({ ...params, count: String(count), offset: String(offset) });
    const res = await fetch(`${BASE_URL}${endpoint}?${query}`, {
      headers: { Authorization: `Bearer ${sessionToken}` },
    });
    if (!res.ok) throw new Error(`API error: ${res.status} on ${endpoint}`);

    const data = await res.json();
    if (!data.Items) return Array.isArray(data) ? data : [data];
    allItems.push(...data.Items);
    if (allItems.length >= data.TotalCount) break;
    offset += count;
  }
  return allItems;
}

interface RueSummary {
  Id: number;
  EventId: number;
  Title: string;
  Status: string;
  Severity: string;
  SubmitDate: string;
  EventTime: string | null;
  ProjectId: number;
}

interface QdSummary {
  Id: number;
  EventId: number;
  Title: string;
  Status: string;
  SubmitDate: string;
}

function inRange(dateStr: string, start: string, end: string): boolean {
  const d = dateStr.slice(0, 10);
  return d >= start && d <= end;
}

export async function GET(request: NextRequest) {
  // Token auth
  const token = request.nextUrl.searchParams.get("token");
  if (!DASHBOARD_TOKEN || token !== DASHBOARD_TOKEN) {
    return NextResponse.json({ error: "Ugyldig token" }, { status: 403 });
  }

  try {
    const sessionToken = await getSessionToken();
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    const monthStart = `${year}-${String(month).padStart(2, "0")}-01`;
    const monthEnd = `${year}-${String(month).padStart(2, "0")}-31`;
    const yearStart = `${year}-01-01`;
    const yearEnd = `${year}-12-31`;

    // Previous week range
    const currentDay = now.getDay();
    const daysSinceMonday = currentDay === 0 ? 6 : currentDay - 1;
    const thisMonday = new Date(now);
    thisMonday.setDate(now.getDate() - daysSinceMonday);
    thisMonday.setHours(0, 0, 0, 0);
    const prevMonday = new Date(thisMonday);
    prevMonday.setDate(thisMonday.getDate() - 7);
    const prevSunday = new Date(thisMonday);
    prevSunday.setDate(thisMonday.getDate() - 1);
    const weekStart = prevMonday.toISOString().slice(0, 10);
    const weekEnd = prevSunday.toISOString().slice(0, 10);

    // Fetch RUE and QD
    const [rueItems, qdItems] = await Promise.all([
      fetchAllPages(sessionToken, "/rue/summaries") as Promise<RueSummary[]>,
      fetchAllPages(sessionToken, "/qd/v2") as Promise<QdSummary[]>,
    ]);

    // SJA — POST endpoint
    const sjaRes = await fetch(`${BASE_URL}/sja/overview`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${sessionToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ fromDate: yearStart, toDate: yearEnd }),
    });
    const sjaData = await sjaRes.json();
    const sjaAll: { SubmittedDate?: string }[] = Array.isArray(sjaData)
      ? sjaData
      : Object.values(sjaData).find(Array.isArray) as { SubmittedDate?: string }[] || [];

    // Filter
    const rueYear = rueItems.filter((r) => inRange(r.SubmitDate, yearStart, yearEnd));
    const rueMonth = rueItems.filter((r) => inRange(r.SubmitDate, monthStart, monthEnd));
    const rueWeek = rueItems.filter((r) => {
      if (!r.EventTime) return false;
      const d = r.EventTime.slice(0, 10);
      return d >= weekStart && d <= weekEnd;
    });

    const qdYear = qdItems.filter((q) => inRange(q.SubmitDate, yearStart, yearEnd));
    const qdMonth = qdItems.filter((q) => inRange(q.SubmitDate, monthStart, monthEnd));

    const sjaYear = sjaAll.filter(
      (s) => s.SubmittedDate && inRange(s.SubmittedDate, yearStart, yearEnd)
    );
    const sjaMonth = sjaAll.filter(
      (s) => s.SubmittedDate && inRange(s.SubmittedDate, monthStart, monthEnd)
    );

    // Open vs closed RUE this year
    const rueOpen = rueYear.filter(
      (r) => r.Status === "Open" || r.Status === "New" || r.Status === "Unprocessed"
    ).length;
    const rueClosed = rueYear.filter((r) => r.Status === "Close").length;

    // Last 5 RUE events
    const recentRue = [...rueYear]
      .sort((a, b) => b.SubmitDate.localeCompare(a.SubmitDate))
      .slice(0, 5)
      .map((r) => ({
        eventId: r.EventId,
        title: r.Title,
        severity: r.Severity,
        status: r.Status,
        date: r.SubmitDate?.slice(0, 10),
      }));

    // Monthly trend (RUE per month this year)
    const monthlyRue: number[] = Array(12).fill(0);
    for (const r of rueYear) {
      const m = parseInt(r.SubmitDate.slice(5, 7), 10) - 1;
      if (m >= 0 && m < 12) monthlyRue[m]++;
    }

    const monthNames = [
      "Jan", "Feb", "Mar", "Apr", "Mai", "Jun",
      "Jul", "Aug", "Sep", "Okt", "Nov", "Des",
    ];

    return NextResponse.json({
      updatedAt: now.toISOString(),
      year,
      month,
      metrics: {
        rueMonth: rueMonth.length,
        rueYear: rueYear.length,
        rueWeek: rueWeek.length,
        rueOpen,
        rueClosed,
        qdMonth: qdMonth.length,
        qdYear: qdYear.length,
        sjaMonth: sjaMonth.length,
        sjaYear: sjaYear.length,
      },
      recentRue,
      monthlyTrend: monthlyRue.slice(0, month).map((count, i) => ({
        month: monthNames[i],
        count,
      })),
    });
  } catch (error) {
    console.error("Dashboard API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Ukjent feil" },
      { status: 500 }
    );
  }
}
