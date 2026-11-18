#!/usr/bin/env python3
"""
Measure what one FitFindr run costs, from the run log rather than a price list.

    python measure_cost.py            10 real runs (cache OFF), then 3 failure probes

It drives the same Flask app `gunicorn serve:app` serves (via Flask's test
client), so every request goes through the instrumented /ask and lands in
logs/runs.jsonl. The averages printed here are computed from those records.

Cost here is tokens and seconds, as reported/measured. To turn tokens into
dollars, pass this model's current per-million-token prices from the pricing
page you're billed under:

    PRICE_IN_PER_M=0.10 PRICE_OUT_PER_M=0.40 python measure_cost.py

(Those numbers are examples, not the real prices; the free tier bills $0.)
"""
import json
import os
import statistics
import sys

os.environ["AI201_CACHE"] = "0"   # five tries of one input must be real answers

import runlog  # noqa: E402
import serve   # noqa: E402

QUERIES = [
    "vintage graphic tee under $30",
    "baggy jeans",
    "black leather jacket under $80",
    "cropped hoodie",
    "denim jacket under $60",
] * 2


def read_records(skip: int) -> list[dict]:
    with runlog.LOG_PATH.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh.read().splitlines()[skip:]]


def main() -> int:
    skip = sum(1 for _ in runlog.LOG_PATH.open()) if runlog.LOG_PATH.exists() else 0
    client = serve.app.test_client()

    print(f"10 real runs, cache off, logging to {runlog.LOG_PATH}")
    for i, q in enumerate(QUERIES, 1):
        r = client.post("/ask", json={"query": q}, headers={"X-Client": "other"})
        print(f"  {i:2d}. {r.status_code}  {q}", file=sys.stderr)

    print("3 failure probes (empty query, no match, non-object body)", file=sys.stderr)
    client.post("/ask", json={})
    client.post("/ask", json={"query": "neon spacesuit under $1"})
    client.post("/ask", data="[1, 2]", content_type="application/json")

    recs = read_records(skip)
    ok = [r for r in recs if r["status"] == "ok"]
    if not ok:
        print("No successful runs to average. Check the log:", runlog.LOG_PATH)
        return 1

    def mean(key):
        return statistics.mean(r[key] for r in ok)

    pin, pout = mean("prompt_tokens"), mean("output_tokens")
    print(f"\nsuccessful runs: {len(ok)} of {len(QUERIES)}")
    print(f"mean model calls / run:   {mean('model_calls'):.1f}")
    print(f"mean prompt tokens / run: {pin:.0f}")
    print(f"mean output tokens / run: {pout:.0f}")
    print(f"mean total tokens / run:  {pin + pout:.0f}")
    print(f"median duration / run:    {statistics.median(r['duration_ms'] for r in ok) / 1000:.2f} s")
    print(f"mean duration / run:      {mean('duration_ms') / 1000:.2f} s "
          f"(min {min(r['duration_ms'] for r in ok) / 1000:.2f}, "
          f"max {max(r['duration_ms'] for r in ok) / 1000:.2f})")
    try:
        cin, cout = float(os.environ["PRICE_IN_PER_M"]), float(os.environ["PRICE_OUT_PER_M"])
        cost = pin * cin / 1e6 + pout * cout / 1e6
        print(f"cost / run at ${cin}/M in, ${cout}/M out: ${cost:.6f}")
    except (KeyError, ValueError):
        print("cost in dollars: not computed (set PRICE_IN_PER_M and PRICE_OUT_PER_M)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
