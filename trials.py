#!/usr/bin/env python3
"""Capstone trials for criteria 6, 7 and 8 (criteria.md). 3 trials each; prints real output.

    python trials.py            # before/after an improvement: run again and compare

Drives the Flask test client, so it needs no server. Writes its own log to a
scratch file so criterion 6 can count records exactly.
"""
import json, os, re, sys, tempfile
LOG = os.path.join(tempfile.mkdtemp(), "runs.jsonl")
os.environ["FITFINDR_LOG"] = LOG
import config  # noqa: F401
import serve
from agent import run_agent
from utils.data_loader import get_example_wardrobe

c = serve.app.test_client()
def post(body, client=None):
    h = {"Content-Type": "application/json"}
    if client: h["X-Client"] = client
    r = c.post("/ask", data=json.dumps(body), headers=h)
    return r
def records():
    if not os.path.exists(LOG): return []
    return [json.loads(l) for l in open(LOG, encoding="utf-8") if l.strip()]

def crit6(t):
    before = len(records())
    calls = [({"query": "vintage graphic tee under $30"}, "form"), ({"query": "baggy jeans"}, "form"),
             ({"query": "black leather jacket under $80"}, "form"), ({"query": "cropped hoodie"}, "form"),
             ({"query": "denim jacket under $60"}, "webmcp"), ({"query": "vintage graphic tee under $30"}, "webmcp"),
             ({"query": "baggy jeans"}, "webmcp"), ({"query": ""}, None), ({"nope": 1}, "webmcp"), ({"query": "neon spacesuit under $1"}, None)]
    want = []
    for body, cl in calls:
        post(body, cl); want.append(cl or "other")
    new = records()[before:]
    got = [r["client"] for r in new]
    ok = len(new) == 10 and got == want
    print(f"  trial {t}: records {len(new)}/10, clients match: {got == want}  -> {'PASS' if ok else 'FAIL'}")
    return ok

def crit7(t):
    cases = {"empty": post({"query": ""}), "whitespace": post({"query": "   "}),
             "number": post({"query": 5}), "list body": post([1, 2]),
             "5000 chars": post({"query": "vintage tee " * 417})}
    passed = 0
    for name, r in cases.items():
        is_json = r.is_json and isinstance(r.get_json(), dict) and bool(r.get_json().get("error"))
        ok = 400 <= r.status_code < 500 and is_json
        passed += ok
        print(f"  trial {t}: {name:11s} http={r.status_code} json_error={is_json} -> {'PASS' if ok else 'FAIL'}")
    print(f"  trial {t}: {passed}/5")
    return passed == 5

def crit8(t):
    ok_all = True
    for q, cap in [("vintage graphic tee under $30", 30), ("black leather jacket under $80", 80), ("denim jacket under $60", 60)]:
        r = post({"query": q}, "webmcp"); b = r.get_json() or {}
        direct = run_agent(q, get_example_wardrobe())
        item = b.get("selected_item") or {}
        same_id = item.get("id") == (direct.get("selected_item") or {}).get("id")
        present = bool(b.get("outfit_suggestion")) and bool(b.get("fit_card")) and not b.get("error")
        under = isinstance(item.get("price"), (int, float)) and item["price"] <= cap
        same_text = b.get("fit_card") == direct.get("fit_card") and b.get("outfit_suggestion") == direct.get("outfit_suggestion")
        ok = r.status_code == 200 and same_id and present and under
        ok_all &= ok
        print(f"  trial {t}: {q!r}: http={r.status_code} item_id_match={same_id} present={present} price<=ceiling={under} text_identical={same_text} -> {'PASS' if ok else 'FAIL'}")
    return ok_all

if __name__ == "__main__":
    for name, fn in (("6 every call logged", crit6), ("7 bad input fails properly", crit7), ("8 parity with run_agent", crit8)):
        print(f"\nCriterion {name}")
        res = [fn(t) for t in (1, 2, 3)]
        print(f"  => {sum(res)}/3 trials pass")
