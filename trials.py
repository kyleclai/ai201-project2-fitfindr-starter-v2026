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

def crit11(t):
    """Force each failure kind; the log record must name it and keep the query."""
    import agent, tools
    from generate import ModelUnavailable, QuotaGuard
    from mcp_client import MCPError
    q = "vintage graphic tee under $30"
    def forced(label, want, patch):
        before = len(records())
        undo = patch()
        try:
            post({"query": q}, "webmcp")
        finally:
            undo()
        new = records()[before:]
        rec = new[-1] if new else {}
        ok = len(new) == 1 and rec.get("status") == want and rec.get("input", {}).get("query") == q
        print(f"  trial {t}: {label:18s} want={want} got={rec.get('status')} query_kept={rec.get('input', {}).get('query') == q} -> {'PASS' if ok else 'FAIL'}")
        return ok
    def raising(module, name, exc):
        def patch():
            orig = getattr(module, name)
            def boom(*a, **k): raise exc
            setattr(module, name, boom)
            return lambda: setattr(module, name, orig)
        return patch
    results = [
        forced("model unreachable", "model_unavailable", raising(tools, "generate", ModelUnavailable("x"))),
        forced("budget hit", "quota_guard", raising(tools, "generate", QuotaGuard("x"))),
        forced("MCP down", "mcp_error", raising(agent, "call_tool", MCPError("x"))),
        forced("crash in handler", "crash", raising(serve.runlog, "classify", RuntimeError("x"))),
    ]
    # Fifth check: same failure, different wording. The status must not depend on it.
    sess = {"error": "Totally different wording than before.", "error_kind": "model_unavailable"}
    got = serve.runlog.classify(sess, None)
    ok5 = got == "model_unavailable"
    print(f"  trial {t}: reworded message  want=model_unavailable got={got} -> {'PASS' if ok5 else 'FAIL'}")
    results.append(ok5)
    print(f"  trial {t}: {sum(results)}/5")
    return all(results)

if __name__ == "__main__":
    for name, fn in (("6 every call logged", crit6), ("7 bad input fails properly", crit7), ("8 parity with run_agent", crit8), ("11 failure kinds logged accurately", crit11)):
        print(f"\nCriterion {name}")
        res = [fn(t) for t in (1, 2, 3)]
        print(f"  => {sum(res)}/3 trials pass")
