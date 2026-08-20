"""
Phase 4 — Longitudinal Analysis Engine
========================================
Compares a patient's current report against all their past reports.
Computes per-parameter trends: improving / worsening / stable.
Generates trajectory-aware risk scores.

This is the second major novelty of the research paper —
most health AI tools analyse one report in isolation.
This one reasons across time.
"""

import json
import os
from datetime import datetime


# How much change (%) counts as meaningful vs noise
IMPROVEMENT_THRESHOLD = 5.0   # % change toward normal
WORSENING_THRESHOLD   = 5.0   # % change away from normal


def classify_trend(values_over_time: list[float], normal_min: float, normal_max: float) -> str:
    """
    Given a list of values ordered oldest → newest,
    classify the trend as 'improving', 'worsening', or 'stable'.

    Logic:
    - Compute how far each value is from the normal midpoint
    - Compare first half average vs second half average
    - If moving toward midpoint → improving
    - If moving away → worsening
    - Otherwise → stable
    """
    if len(values_over_time) < 2:
        return "insufficient_data"

    midpoint = (normal_min + normal_max) / 2

    def distance_from_normal(v):
        if normal_min <= v <= normal_max:
            return 0.0
        return min(abs(v - normal_min), abs(v - normal_max))

    distances = [distance_from_normal(v) for v in values_over_time]

    # Compare first half vs second half average distance from normal
    mid      = len(distances) // 2
    first_avg = sum(distances[:mid]) / max(len(distances[:mid]), 1)
    last_avg  = sum(distances[mid:]) / max(len(distances[mid:]), 1)

    if first_avg == 0 and last_avg == 0:
        return "stable_normal"

    if first_avg == 0:
        return "worsening"

    pct_change = ((last_avg - first_avg) / first_avg) * 100

    if pct_change < -IMPROVEMENT_THRESHOLD:
        return "improving"
    elif pct_change > WORSENING_THRESHOLD:
        return "worsening"
    else:
        return "stable"


def get_trend_label(trend: str) -> dict:
    """Return display label + color for a trend string."""
    return {
        "improving":         {"label": "Improving",         "color": "green"},
        "worsening":         {"label": "Worsening",         "color": "red"},
        "stable":            {"label": "Stable",            "color": "amber"},
        "stable_normal":     {"label": "Consistently Normal","color": "green"},
        "insufficient_data": {"label": "Only 1 report",     "color": "gray"},
    }.get(trend, {"label": trend, "color": "gray"})


def compute_longitudinal(all_results: list[dict]) -> dict:
    """
    Main function. Takes a list of result dicts (oldest first),
    each containing 'raw_values' and 'uploaded_at'.

    Returns:
    {
      "total_reports": int,
      "date_range": { "from": str, "to": str },
      "parameters": {
        "hemoglobin": {
          "values": [10.5, 11.2, 11.8],
          "dates":  ["Jan 2024", "Mar 2024", "Jun 2024"],
          "trend":  "improving",
          "trend_label": "Improving",
          "trend_color": "green",
          "latest": 11.8,
          "change_from_first": +1.3,
          "change_pct": +12.4
        },
        ...
      },
      "overall_trend": "improving" | "worsening" | "stable",
      "scores_over_time": [33, 45, 58],
      "risk_trajectory": "decreasing" | "increasing" | "stable"
    }
    """
    if not all_results:
        return {"total_reports": 0}

    # Load normal ranges for trend context
    ranges_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "normal_ranges.json"
    )
    try:
        with open(ranges_path) as f:
            ranges = json.load(f)
    except Exception:
        ranges = {}

    # Collect values per parameter across all reports
    param_history  = {}   # key → list of (date, value)
    scores         = []
    dates          = []

    for result in all_results:
        raw_vals = result.get("raw_values", {})
        if isinstance(raw_vals, str):
            try:
                raw_vals = json.loads(raw_vals)
            except Exception:
                raw_vals = {}

        date_str = result.get("uploaded_at", "")
        try:
            dt       = datetime.fromisoformat(str(date_str).replace(" ", "T"))
            date_fmt = dt.strftime("%b %Y")
        except Exception:
            date_fmt = str(date_str)[:10]

        dates.append(date_fmt)
        score = result.get("health_score") or 0
        scores.append(score)

        for key, value in raw_vals.items():
            if key not in param_history:
                param_history[key] = []
            param_history[key].append({"date": date_fmt, "value": float(value)})

    # Compute trend per parameter
    parameters = {}
    for key, history in param_history.items():
        ref    = ranges.get(key, {})
        n_min  = ref.get("min", 0)
        n_max  = ref.get("max", 999)
        vals   = [h["value"] for h in history]
        hdates = [h["date"]  for h in history]

        trend       = classify_trend(vals, n_min, n_max)
        trend_info  = get_trend_label(trend)
        first_val   = vals[0]  if vals else 0
        latest_val  = vals[-1] if vals else 0
        change      = round(latest_val - first_val, 2)
        change_pct  = round((change / first_val * 100) if first_val != 0 else 0, 1)

        parameters[key] = {
            "display_name":       ref.get("display_name", key),
            "unit":               ref.get("unit", ""),
            "values":             vals,
            "dates":              hdates,
            "trend":              trend,
            "trend_label":        trend_info["label"],
            "trend_color":        trend_info["color"],
            "latest":             latest_val,
            "first":              first_val,
            "change_from_first":  change,
            "change_pct":         change_pct,
            "normal_min":         n_min,
            "normal_max":         n_max,
        }

    # Overall trend from health scores
    if len(scores) >= 2:
        score_change = scores[-1] - scores[0]
        if score_change > 5:
            overall_trend = "improving"
        elif score_change < -5:
            overall_trend = "worsening"
        else:
            overall_trend = "stable"
    else:
        overall_trend = "insufficient_data"

    return {
        "total_reports":    len(all_results),
        "date_range":       {
            "from": dates[0]  if dates else "",
            "to":   dates[-1] if dates else ""
        },
        "report_dates":     dates,
        "parameters":       parameters,
        "scores_over_time": scores,
        "overall_trend":    overall_trend,
        "risk_trajectory":  "decreasing" if overall_trend == "improving"
                            else "increasing" if overall_trend == "worsening"
                            else "stable"
    }


def get_longitudinal_rag_context(longitudinal_data: dict) -> str:
    """
    Build a text summary of longitudinal trends for injection into RAG prompt.
    This is what makes the chatbot temporally aware.
    """
    if not longitudinal_data or longitudinal_data.get("total_reports", 0) < 2:
        return ""

    lines   = [f"PATIENT HISTORY ({longitudinal_data['total_reports']} reports):"]
    params  = longitudinal_data.get("parameters", {})

    worsening  = [k for k, v in params.items() if v["trend"] == "worsening"]
    improving  = [k for k, v in params.items() if v["trend"] == "improving"]

    if worsening:
        names = ", ".join(params[k]["display_name"] for k in worsening[:4])
        lines.append(f"Worsening over time: {names}")

    if improving:
        names = ", ".join(params[k]["display_name"] for k in improving[:4])
        lines.append(f"Improving over time: {names}")

    scores = longitudinal_data.get("scores_over_time", [])
    if len(scores) >= 2:
        lines.append(f"Health score trend: {scores[0]} → {scores[-1]}/100")

    return "\n".join(lines)