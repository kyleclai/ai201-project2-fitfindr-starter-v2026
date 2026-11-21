#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Two routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

Instrumented in the capstone: every /ask writes one JSON line via runlog.py
(see its docstring for the fields), including rejected and crashed requests.
GET / serves static/index.html, which also registers the WebMCP tool.
"""

import os
import sys
import threading
import time

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

from flask import Flask, g, jsonify, request, send_from_directory

import generate
import runlog
from agent import run_agent
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make

_one_at_a_time = threading.Lock()

# A request is one item described in a sentence. The run log keeps the first
# 500 characters of the input, so anything longer is refused up front.
MAX_QUERY_CHARS = 500


@app.get("/")
def index():
    """The one-page front end. It also registers the WebMCP tool (static/index.html)."""
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    """
    Run the agent on one query.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.
    """
    started = time.perf_counter()
    client = request.headers.get("X-Client", "other")
    client = client if client in ("form", "webmcp") else "other"
    g.query = ""  # _handle_ask fills this in as soon as it knows the query
    try:
        return _handle_ask(started, client)
    except Exception as exc:  # noqa: BLE001 — log it with the input that caused it, then re-raise
        runlog.write(client=client, status="crash", http_status=500, query=g.query,
                     output={"error": f"{type(exc).__name__}: {exc}"},
                     duration_ms=(time.perf_counter() - started) * 1000, wait_ms=0)
        raise


def _handle_ask(started: float, client: str):
    payload = request.get_json(silent=True)
    query = ""

    def reject(message: str, status: int = 400):
        runlog.write(client=client, status="bad_request", http_status=status, query=query,
                     output={"error": message},
                     duration_ms=(time.perf_counter() - started) * 1000, wait_ms=0)
        return jsonify({"error": message}), status

    # Check the shape before reading anything out of it: a list, a number or a
    # string body used to reach payload.get() and crash with an HTML 500.
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return reject("The request body must be a JSON object, e.g. "
                      '{"query": "vintage graphic tee under $30"}')
    raw_query = payload.get("query") or ""
    if not isinstance(raw_query, str):
        return reject("'query' must be a string, e.g. "
                      '{"query": "vintage graphic tee under $30"}')
    query = raw_query.strip()
    g.query = query
    if len(query) > MAX_QUERY_CHARS:
        query = query[:MAX_QUERY_CHARS]  # keep the log record small
        return reject(f"'query' is too long (limit {MAX_QUERY_CHARS} characters). "
                      "Describe one item, e.g. 'vintage graphic tee under $30'.")

    if not query:
        # 400 rather than a stack trace: the caller can act on this one.
        return reject("Send JSON with a 'query' field, e.g. "
                      '{"query": "vintage graphic tee under $30"}')

    wardrobe = payload.get("wardrobe")
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    # A queued request should look like a queued request. Without this the
    # second caller just sits there, and "slow" and "waiting its turn" are
    # indistinguishable from the outside. This note prints nothing else and
    # counts nothing; the timing lives in the run log (wait_ms).
    if _one_at_a_time.locked():
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    failure = None
    session = None
    with _one_at_a_time:
        wait_ms = (time.perf_counter() - started) * 1000
        # Only one agent run is in flight at a time, so the change in the
        # module-level counters across this block is exactly this request's.
        calls0, hits0, tok0 = generate.call_count(), generate.cache_hit_count(), generate.token_counts()
        try:
            session = run_agent(query, wardrobe)
        except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
            failure = f"{type(exc).__name__}: {exc}"
        tok1 = generate.token_counts()
        calls1, hits1 = generate.call_count(), generate.cache_hit_count()

    status = runlog.classify(session, failure)
    http_status = 500 if failure is not None else 200
    runlog.write(
        client=client, status=status, http_status=http_status, query=query,
        output=runlog.summarize_output(session, failure),
        duration_ms=(time.perf_counter() - started) * 1000, wait_ms=wait_ms,
        model_calls=calls1 - calls0, cache_hits=hits1 - hits0,
        prompt_tokens=tok1["prompt"] - tok0["prompt"],
        output_tokens=tok1["output"] - tok0["output"],
    )

    # Outside the lock: building a response is not work the next caller should
    # be waiting on.
    if failure is not None:
        return jsonify({"error": failure}), 500

    return jsonify(session)


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5000"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
