import { NextResponse } from "next/server";

const BASE_URL = process.env.SMARTDOK_BASE_URL || "https://api.smartdok.no";

async function getSessionToken(): Promise<string> {
  const apiToken = process.env.SMARTDOK_API_TOKEN;
  if (!apiToken) {
    throw new Error("SMARTDOK_API_TOKEN is not configured");
  }

  const res = await fetch(`${BASE_URL}/Authorize/ApiToken`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Token: apiToken }),
  });

  if (!res.ok) {
    throw new Error(`Auth failed: ${res.status} ${res.statusText}`);
  }

  const token = await res.text();
  // The API returns the session token as a quoted string
  return token.replace(/"/g, "");
}

function getPreviousWeekRange(): { start: Date; end: Date; lastUpdatedSince: string } {
  const now = new Date();
  // Find Monday of current week
  const currentDay = now.getDay(); // 0=Sun, 1=Mon, ...
  const daysSinceMonday = currentDay === 0 ? 6 : currentDay - 1;

  const thisMonday = new Date(now);
  thisMonday.setDate(now.getDate() - daysSinceMonday);
  thisMonday.setHours(0, 0, 0, 0);

  // Previous week: Monday to Sunday
  const prevMonday = new Date(thisMonday);
  prevMonday.setDate(thisMonday.getDate() - 7);

  const prevSunday = new Date(thisMonday);
  prevSunday.setDate(thisMonday.getDate() - 1);
  prevSunday.setHours(23, 59, 59, 999);

  return {
    start: prevMonday,
    end: prevSunday,
    lastUpdatedSince: prevMonday.toISOString(),
  };
}

interface RueSummary {
  Id: number;
  EventId: number;
  Title: string;
  Status: string;
  Severity: string;
  SubmitDate: string;
  EventTime: string | null;
  DeadlineDateTime: string | null;
  ProjectId: number;
  SubProjectId: number | null;
}

interface RueSummaryResponse {
  Items: RueSummary[];
  Count: number;
  Offset: number;
  TotalCount: number;
}

export async function GET() {
  try {
    const sessionToken = await getSessionToken();
    const { start, end, lastUpdatedSince } = getPreviousWeekRange();

    // Fetch all pages
    const allItems: RueSummary[] = [];
    let offset = 0;
    const count = 100;

    while (true) {
      const url = `${BASE_URL}/rue/summaries?LastUpdatedSince=${encodeURIComponent(lastUpdatedSince)}&Offset=${offset}&Count=${count}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status} ${res.statusText}`);
      }

      const data: RueSummaryResponse = await res.json();
      allItems.push(...data.Items);

      if (allItems.length >= data.TotalCount) break;
      offset += count;
    }

    // Filter by EventTime within previous week (Monday–Sunday)
    const filtered = allItems.filter((item) => {
      if (!item.EventTime) return false;
      const eventDate = new Date(item.EventTime);
      return eventDate >= start && eventDate <= end;
    });

    // Sort by EventTime descending
    filtered.sort((a, b) => {
      const dateA = new Date(a.EventTime!).getTime();
      const dateB = new Date(b.EventTime!).getTime();
      return dateB - dateA;
    });

    return NextResponse.json({
      items: filtered,
      weekStart: start.toISOString().split("T")[0],
      weekEnd: end.toISOString().split("T")[0],
      totalFetched: allItems.length,
      totalFiltered: filtered.length,
    });
  } catch (error) {
    console.error("RUE fetch error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
