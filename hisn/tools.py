"""The three read-only triage tools and their schemas."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hisn.retrieval import search_runbooks

DATA_DIR = Path(__file__).parent / "data"


def _load_assets() -> dict[str, dict]:
    """Map normalised host name to asset fields (accepts a mapping or a list)."""
    raw = json.loads((DATA_DIR / "assets.json").read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "assets" in raw:
        raw = raw["assets"]
    if isinstance(raw, dict):
        pairs = raw.items()
    else:
        pairs = [(a.get("host") or a.get("hostname") or a.get("name"), a) for a in raw]
    return {name.strip().lower(): dict(fields) for name, fields in pairs}


def lookup_asset(host: str) -> dict:
    """Look up a host's owner, criticality and environment."""
    asset = _load_assets().get(host.strip().lower())
    if asset is None:
        return {"host": host, "known": False}
    return {**asset, "known": True}


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def related_alerts(rule_id: str, agent: str, around: str, window_minutes: int = 60) -> dict:
    """Count alerts with the same rule and agent in the window ending at `around`."""
    if not 1 <= window_minutes <= 1440:
        raise ValueError("window_minutes must be between 1 and 1440")
    end = _parse_time(around)
    start = end - timedelta(minutes=window_minutes)
    ids = []
    with (DATA_DIR / "alerts.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            alert = json.loads(line)
            if (
                str(alert["rule"]["id"]) == str(rule_id)
                and alert["agent"]["name"].lower() == agent.lower()
                and start <= _parse_time(alert["timestamp"]) <= end
            ):
                ids.append(alert["id"])
    return {"count": len(ids), "alert_ids": ids}


TOOLS: dict = {
    "lookup_asset": lookup_asset,
    "search_runbooks": search_runbooks,
    "related_alerts": related_alerts,
}


def _schema(name: str, description: str, properties: dict, required: list) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


_STRING = {"type": "string"}
_INTEGER = {"type": "integer"}

TOOL_SCHEMAS: list = [
    _schema(
        "lookup_asset",
        "Look up a host's owner, criticality and environment.",
        {"host": _STRING},
        ["host"],
    ),
    _schema(
        "search_runbooks",
        "Search the incident runbooks and return the best matches.",
        {"query": _STRING, "k": _INTEGER},
        ["query"],
    ),
    _schema(
        "related_alerts",
        "Count alerts with the same rule and agent in the minutes before a time.",
        {"rule_id": _STRING, "agent": _STRING, "around": _STRING, "window_minutes": _INTEGER},
        ["rule_id", "agent", "around"],
    ),
]
