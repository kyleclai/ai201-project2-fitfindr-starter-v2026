"""
Structured run log for FitFindr's HTTP server.

One JSON object per line (JSONL) appended to logs/runs.jsonl. Every request to
POST /ask writes exactly one record, including rejected and crashed ones — a
failure that leaves no record is one you never find.

Fields (all present on every record):
    timestamp        UTC, ISO 8601
    run_id           8 hex chars, so a record can be quoted in a bug report
    client           "form" | "webmcp" | "other"  (X-Client header from the page)
    level            INFO | WARNING | ERROR
    status           ok | no_results | bad_request | model_unavailable |
                     quota_guard | mcp_error | crash
    http_status      what the caller got
    input            {"query": "..."}  (first 500 chars)
    output           {"item_id", "item_title", "outfit_chars", "fit_card_chars",
                      "error"}  — small on purpose; the full text is not logged
    duration_ms      whole request, including time spent waiting for the lock
    wait_ms          the part of duration_ms spent queued behind another request
    model_calls      real model calls this request made (cache hits excluded)
    cache_hits       model answers served from .cache instead
    prompt_tokens / output_tokens
                     tokens the service reported for this request

Each record is also printed to stdout prefixed `RUNLOG ` so a host's log viewer
(e.g. Render's Logs tab) shows it. Logging must never break a request: write()
swallows its own errors.
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import config

LOG_PATH = Path(os.getenv("FITFINDR_LOG", config.ROOT / "logs" / "runs.jsonl"))
_write_lock = threading.Lock()

# Fragments of the messages run_agent() puts in session["error"]. The agent
# is not changed for the capstone, so the kind of failure is read back from
# its message.
_ERROR_KINDS = (
    ("model couldn't be reached", "model_unavailable"),
    ("request budget", "quota_guard"),
    ("over MCP", "mcp_error"),
)

_LEVELS = {
    "ok": "INFO",
    "no_results": "WARNING",
    "bad_request": "WARNING",
}


def classify(session: dict | None, failure: str | None) -> str:
    """Name what happened to one /ask run."""
    if failure is not None:
        return "crash"
    if session is None or not session.get("error"):
        return "ok"
    message = session["error"]
    for fragment, kind in _ERROR_KINDS:
        if fragment in message:
            return kind
    return "no_results"


def summarize_output(session: dict | None, failure: str | None) -> dict:
    """The small, loggable shape of a result."""
    if failure is not None:
        return {"error": failure}
    item = (session or {}).get("selected_item") or {}
    return {
        "item_id": item.get("id"),
        "item_title": item.get("title"),
        "outfit_chars": len((session or {}).get("outfit_suggestion") or ""),
        "fit_card_chars": len((session or {}).get("fit_card") or ""),
        "error": (session or {}).get("error"),
    }


def write(*, client, status, http_status, query, output, duration_ms, wait_ms,
          model_calls=0, cache_hits=0, prompt_tokens=0, output_tokens=0) -> dict:
    """Append one record. Returns it (handy in tests). Never raises."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": uuid.uuid4().hex[:8],
        "client": client,
        "level": _LEVELS.get(status, "ERROR"),
        "status": status,
        "http_status": http_status,
        "input": {"query": (query or "")[:500]},
        "output": output,
        "duration_ms": round(duration_ms),
        "wait_ms": round(wait_ms),
        "model_calls": model_calls,
        "cache_hits": cache_hits,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
    }
    line = json.dumps(record, ensure_ascii=False)
    try:
        with _write_lock:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except Exception:  # noqa: BLE001 — a log problem must not fail the request
        pass
    # Also to stdout: a host's log viewer shows what the process prints, and on a
    # free instance the file above is wiped when it sleeps.
    try:
        print("RUNLOG " + line, flush=True)
    except Exception:  # noqa: BLE001
        pass
    return record
