"""Generate charts (PNG buffers) for the HMS quarterly report."""

from __future__ import annotations

import io
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Color palettes
PIE_COLORS = [
    "#2563EB", "#DC2626", "#16A34A", "#F59E0B",
    "#8B5CF6", "#EC4899", "#06B6D4", "#F97316",
    "#6366F1", "#84CC16", "#14B8A6", "#A855F7",
]
BAR_COLOR = "#F5A623"
LINE_COLOR = "#DC2626"


def _fig_to_bytes(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_pie_chart(title: str, data: dict[str, int]) -> bytes:
    if not data:
        data = {"Ingen data": 1}

    labels = list(data.keys())
    values = list(data.values())
    colors = PIE_COLORS[: len(labels)]

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        colors=colors,
        autopct=lambda pct: f"{int(round(pct * sum(values) / 100))}" if pct > 5 else "",
        startangle=90,
        textprops={"fontsize": 7, "color": "white", "weight": "bold"},
    )
    ax.set_title(title, fontsize=9, fontweight="bold", color="#1f2937")
    ax.legend(
        labels, loc="lower center", bbox_to_anchor=(0.5, -0.15),
        fontsize=6, ncol=2, frameon=False,
    )
    fig.tight_layout()
    return _fig_to_bytes(fig)


def render_horizontal_bar_chart(title: str, data: dict[str, int]) -> bytes:
    if not data:
        data = {"Ingen data": 0}

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(labels, values, color=BAR_COLOR)
    ax.set_title(title, fontsize=13, fontweight="bold", color="#1f2937")
    ax.set_xlabel("Antall")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    fig.tight_layout()
    return _fig_to_bytes(fig)


def render_line_chart(title: str, months: list[dict]) -> bytes:
    labels = [m["label"] for m in months]
    values = [m["count"] for m in months]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(labels, values, color=LINE_COLOR, marker="o", linewidth=2, markersize=6)
    ax.fill_between(labels, values, alpha=0.15, color=LINE_COLOR)
    ax.set_title(title, fontsize=13, fontweight="bold", color="#1f2937")
    ax.set_ylabel("Antall")
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    fig.tight_layout()
    return _fig_to_bytes(fig)


def generate_all_charts(data: dict) -> dict[str, bytes]:
    print("\nGenererer diagrammer...")

    charts = {
        "rueEventType": render_pie_chart("Type hendelse", data["rue"]["byEventType"]),
        "rueEventInvolved": render_pie_chart("Hendelsen omfattet", data["rue"]["byEventInvolved"]),
        "rueCauseOfEvent": render_pie_chart("Aarsak til hendelsen", data["rue"]["byCauseOfEvent"]),
        "rueEventInvolvedBar": render_horizontal_bar_chart(
            "Hendelsene omfattet", data["rue"]["byEventInvolved"]
        ),
        "rueMonthlyFrequency": render_line_chart(
            "Rapporteringsfrekvens per maaned", data["rue"]["byMonth"]
        ),
        "qdConcerning": render_pie_chart("Angaar", data["qd"]["byConcerning"]),
        "qdRelatesTo": render_pie_chart("I forhold til", data["qd"]["byRelatesTo"]),
        "qdCause": render_pie_chart("Aarsak", data["qd"]["byCause"]),
    }

    print("  8 diagrammer generert")
    return charts
