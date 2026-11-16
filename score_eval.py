#!/usr/bin/env python3
"""
Scores my five criteria (criteria.md) with five tries each.

    python score_eval.py --label before
    python score_eval.py --label after

Why this exists next to run_eval.py: run_eval.py leaves PASS/FAIL blank. This
script applies the criteria exactly as I worded them, mechanically, so the
verdict doesn't depend on my mood. It reuses run_eval.run_once (same agent, same
trace capture, cache off) and wraps the two model tools to record which item id
each one actually received, which is what criterion 3 needs.

Try definitions:
  1  one query, run 5 times
  2  one impossible query, run 5 times
  3  5 different queries, one run each (try i = item i)
  4  the fit cards from those same 5 runs
  5  5 search queries with a price ceiling and a size, through the MCP tool
"""
import argparse
import datetime as dt
import re

import config
import agent
import scenarios as sc
import run_eval

seen = {}
_real_outfit, _real_card = agent.suggest_outfit, agent.create_fit_card


def _outfit(item, wardrobe):
    seen["outfit"] = item["id"]
    return _real_outfit(item, wardrobe)


def _card(outfit, item):
    seen["card"] = item["id"]
    return _real_card(outfit, item)


agent.suggest_outfit, agent.create_fit_card = _outfit, _card


def run(scenario):
    seen.clear()
    rec = run_eval.run_once(scenario)
    return rec, dict(seen)


def c1(rec, _):
    s = rec["session"]
    ok = (not rec["crashed"] and s and not s["error"] and bool(s["outfit_suggestion"])
          and bool((s["fit_card"] or "").strip()))
    return ok, "fit card %d chars" % len((s or {}).get("fit_card") or "") if ok else \
        (rec["crashed"] or (s or {}).get("error") or "no fit card")


def c2(rec, seen_):
    s = rec["session"]
    if rec["crashed"] or not s:
        return False, rec["crashed"]
    msg = s["error"] or ""
    p = s["parsed"]
    names = [w for w in re.findall(r"[a-z]+", p["description"].lower())]
    mentions = (p["size"] and p["size"].lower() in msg.lower()) or \
        ("$" in msg and p["max_price"] is not None) or any(w in msg.lower() for w in names)
    ok = (bool(msg) and s["outfit_suggestion"] is None and s["fit_card"] is None
          and "outfit" not in seen_ and "card" not in seen_ and bool(mentions))
    return ok, "stopped early, tools 2+3 not called" if ok else f"error={msg!r} seen={seen_}"


def c3(rec, seen_):
    s = rec["session"]
    if rec["crashed"] or not s or s["error"]:
        return False, rec["crashed"] or (s or {}).get("error")
    sel = s["selected_item"]["id"]
    ids = (sel, seen_.get("outfit"), seen_.get("card"), s["search_results"][0]["id"])
    return len(set(ids)) == 1, f"selected/outfit/card/results[0] = {ids}"


def sentences(text):
    return [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]


def c4(rec, _):
    s = rec["session"]
    card = (s or {}).get("fit_card") or ""
    if not card:
        return False, "no fit card produced"
    item = s["selected_item"]
    n = len(sentences(card))
    price = re.search(r"\$\s?%d(\.00?)?\b" % round(item["price"]), card) is not None
    plat = item["platform"].lower() in card.lower()
    ok = 2 <= n <= 4 and price and plat
    return ok, f"sentences={n} price_in_card={price} platform_in_card={plat}"


def openings(cards):
    firsts = [" ".join(re.findall(r"\w+", c.lower())[:5]) for c in cards if c]
    return len(set(firsts)) == len(firsts), firsts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    args = ap.parse_args()
    config.CACHE_ENABLED = False

    by = {S["name"]: S for S in sc.SCENARIOS}
    matching, impossible = by["matching query completes"], by["impossible query stops early"]
    items = [S for S in sc.SCENARIOS if S["name"].startswith("item ")]

    rows, detail, cards = {}, [], []

    def record(num, i, ok, note, extra=""):
        rows.setdefault(num, []).append(ok)
        detail.append(f"- Criterion {num}, try {i}: **{'PASS' if ok else 'FAIL'}** — {note}{extra}")

    outputs = []
    for i in range(1, 6):
        rec, sn = run(matching)
        ok, note = c1(rec, sn); record(1, i, ok, note)
        outputs.append(("1", i, rec))
        print(f"C1 try {i}: {'PASS' if ok else 'FAIL'} {note}", flush=True)
    for i in range(1, 6):
        rec, sn = run(impossible)
        ok, note = c2(rec, sn); record(2, i, ok, note)
        outputs.append(("2", i, rec))
        print(f"C2 try {i}: {'PASS' if ok else 'FAIL'} {note}", flush=True)
    for i, S in enumerate(items, 1):
        rec, sn = run(S)
        ok3, n3 = c3(rec, sn); record(3, i, ok3, n3, f"  (query: {S['query']!r})")
        ok4, n4 = c4(rec, sn); record(4, i, ok4, n4)
        cards.append(((rec["session"] or {}).get("fit_card") or ""))
        outputs.append((f"3/4 item {i}", i, rec))
        print(f"C3 item {i}: {'PASS' if ok3 else 'FAIL'} {n3}\nC4 item {i}: {'PASS' if ok4 else 'FAIL'} {n4}", flush=True)
    distinct, firsts = openings(cards)

    from mcp_client import call_tool
    for i, q in enumerate(sc.SEARCH_CHECKS, 1):
        p = agent.parse_query(q)
        res = call_tool("search_listings", {"description": p["description"], "size": p["size"],
                                            "max_price": p["max_price"]})
        want = p["size"].lower()
        bad = [r["title"] for r in res
               if r["price"] > p["max_price"] or want not in re.findall(r"[a-z0-9]+", r["size"].lower())]
        record(5, i, not bad, f"{q!r}: {len(res)} results, violations={bad}")
        print(f"C5 try {i}: {'PASS' if not bad else 'FAIL'} {q!r} {len(res)} results {bad}", flush=True)

    targets = {1: ("1. Full three-tool run returns a fit card", 4),
               2: ("2. Impossible query stops before tool 2", 5),
               3: ("3. Item found is the item passed on", 5),
               4: ("4. Fit card reads like a post", 4),
               5: ("5. Search respects price ceiling and size", 5)}
    lines = [f"# Run log — {args.label}", "",
             f"- Produced by: `score_eval.py` (reuses `run_eval.py::run_once`), loop `agent.py::run_agent`",
             f"- Cache off, temperature {config.TEMPERATURE}, {dt.datetime.now():%Y-%m-%d %H:%M}", "",
             "| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |",
             "|---|---|---|---|---|---|---|---|"]
    for n, (name, need) in targets.items():
        r = rows[n]
        passes = sum(r)
        met = passes >= need
        if n == 4:
            met = met and distinct
        verdict = f"{'MET' if met else 'MISSED'} ({passes}/5)" + ("" if n != 4 else f", openings {'distinct' if distinct else 'NOT distinct'}")
        lines.append(f"| {name} | {need} of 5 | " + " | ".join("PASS" if x else "FAIL" for x in r) + f" | {verdict} |")
    lines += ["", f"Criterion 4 opening check (first five words of each card): {firsts} -> "
              f"{'all distinct' if distinct else 'DUPLICATES'}", "", "## Per-try detail", ""] + detail
    lines += ["", "## Real output", ""]
    for label, i, rec in outputs:
        s = rec["session"] or {}
        lines += [f"### Criterion {label}, try {i}", "", "```",
                  f"query: {s.get('query')}", f"parsed: {s.get('parsed')}",
                  f"error: {s.get('error')}",
                  f"selected_item: {(s.get('selected_item') or {}).get('title')}",
                  f"fit_card: {s.get('fit_card')}", "```", ""]
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"scored_{dt.datetime.now():%Y-%m-%d_%H%M}_{args.label}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print("\n" + "\n".join(lines[:14]))
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
