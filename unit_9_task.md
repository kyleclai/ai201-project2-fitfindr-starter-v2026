# Unit 9 — Capstone: Show What You Know

> Tracker for the capstone. Tick boxes and add rows to the **Update Log** as work lands.
> Status: **In progress (M1–M3 done; M4 criteria are YOURS to write next)** · System: FitFindr · Shape: **C — WebMCP front door** · Path: A (Render) with Path B fallback

Both halves (build + test) are due this unit, in the **same repo** as the system being extended. 60 pts: 30 build, 30 test.
Missing your own criteria costs nothing; an honest standard, honest runs, and real diagnoses are what's graded.

## Hard rules
- Extend, don't restart. "Rewrite", "from scratch", "new project" = wrong plan.
- Same repo. Never delete/recreate it or rewrite history.
- **Commit `criteria.md` before any results**, and name both commits in their messages (e.g. `add capstone criteria`, `add capstone first results`).
- At least **8 new commits** this unit; at least 3 in Milestone 2 alone.
- Everything pasted as text. No screenshots, no video.
- README: add one `## Capstone` heading at the end; section names are **bold labels** on their own line, not `###` headings.
- Don't ask a model to write the criteria. Ask it only whether each could be checked by someone who can't ask you what you meant.

## Shapes (pick one; all still need run path + log)
- **A. Deploy and instrument** — operational layer is the whole job.
- **B. Harden against failure** — timeouts, retries, empty/missing input, rate limits; criteria are about the bad path.
- **C. Extend one capability** — ONE new retrieval strategy / tool / label / endpoint, plus evidence it works.

## Run paths (worth the same)
- **Path A, hosted:** URL + platform + the command/config that deployed it. Free host = 512 MB, sleeps after ~15 min (cold start ~1 min; say warm vs any request in latency criteria). Copy logs into README the same session.
- **Path B, local with logs:** one documented start command in `RUNNING.md`, tested from a clean checkout; committed run record (structured log pasted as text); Python version, pinned deps, model files + size.

## Required
- [x] One system extended; say which and what's new
- [x] One shape declared + one sentence on what's out of scope
- [x] Run path that isn't the editor (`RUNNING.md`)
- [x] Structured logging: timestamp, input, output, duration (+ system-specific fields); failures logged too; ≥10 entries pasted in README (+ ≥1 failed run)
- [x] Measured cost per run (10 runs, average, method written down)
- [x] 5 criteria, written first, no template, ≥3 about the extension, ≥1 about the bad path, each with a target and a "why this target"
- [x] 3 trials per criterion
- [x] Verdict (MET/MISSED) + diagnosis (stage + mechanism) per criterion
- [x] One improvement, made and measured, before/after side by side
- [x] Written call on what's left

**Stretch (declare in README before starting):** second measured improvement · latency breakdown by stage · 10× load observation · both run paths with a diff note.

## Milestones

### M1 — Pick system, shape, cut scope (~35 min)
- [x] Choose system (the one I know best)
- [x] Choose shape; write **The Shape** paragraph
- [x] Write 2–3 out-of-scope items
- [x] Size check: ≤ ~90 min of building. Run the "how many separate pieces of work?" check; cut to one
- [x] Commit

### M2 — Build the extension (~90 min)
- [x] Build the one thing; get one path working end to end first
- [x] Original system still works (no regression): `test.py` 10/10, CLI `ask` runs
- [x] ≥3 commits
- [x] If stuck after 1 hr: cut down, and write what was cut in What's Still Broken (n/a: not stuck)
- [x] Commit

### M3 — Run it, make it observable (~75 min)
- [x] Pick path; write `RUNNING.md`
- [x] Fresh clone into a new folder, follow `RUNNING.md` exactly; fix what's missing
- [x] Structured log file (readable back, not `print()`)
- [x] Failures leave records too
- [x] Cost: 10 runs, average; or time it if no spend number
- [x] README **Instrumentation**: ≥10 entries + ≥1 failure; **What It Costs**: number + method
- [x] Both paths: A (Render, https://fitfindr-1vae.onrender.com) deployed and B (local) tested
- [x] Commit

### M4 — Write criteria, unaided (~45 min)
- [x] 5 numbered criteria in `criteria.md`, each: target (number/rate/visible thing) + why that target
- [x] No criterion hinges on "works / reliable / good / fast"
- [x] ≥3 about the extension; ≥1 about a failure path
- [ ] Self-check: (1) how to test from the sentence alone, (2) would two people score it the same, (3) what would have to happen for it to fail?
- [ ] Peer/Claude review (don't rewrite them)
- [x] **Commit with a message naming it, BEFORE any results**

### M5 — Run the test (~50 min)
- [x] Decide what each criterion needs run against it (failures triggered deliberately; latency needs a distribution)
- [x] 3 separate runs, nothing changed in between; save real output (criteria 6, 7, 8, 11 run 3x; 9 and 10 checked live with peers, not counted)
- [x] Run-log table: 5 rows × Run 1/2/3 + verdict
- [x] Paste real output per criterion, naming file + function that produced it
- [x] Commit (message names it as first results)

### M6 — Verdicts, diagnoses, one fix (~70 min)
- [x] MET/MISSED against my own target (target must hold, not "sometimes")
- [x] Each miss: the stage + the mechanism. Look for a shared root cause
- [x] If all met: say whether targets were low; name one to tighten and to what (n/a: there were misses)
- [x] One improvement aimed at a diagnosed cause; re-run all 5 × 3 (criteria 6, 7, 8, 11 re-run; 9 and 10 can't be re-run as trials)
- [x] Before/after tables side by side in README; say if it helped, and any trade
- [x] Criterion revisions only if unmeasurable (never "it was hard"); keep original line, add revision + reason beneath (n/a: no revisions)
- [x] Commit

### M7 — Cost, what's left, submit (~30 min)
- [x] What It Costs: measured per-run, method, hundred-people-a-day arithmetic
- [x] What's Still Broken: per miss, what + why stopped; or tighten-target if all met; plus the one thing to do first and why
- [x] New **How I Used AI** under `## Capstone`: two specific moments (asked / got / changed)
- [ ] Checklist below passes; submit repo URL (checklist passes; resubmit the repo URL)

## README sections under `## Capstone` (bold labels)
- [x] What This Extends
- [x] The Shape
- [x] Running It
- [x] Instrumentation
- [x] What It Costs
- [x] Run Log and Verdicts
- [x] The Improvement
- [x] What's Still Broken
- [x] How I Used AI

## Submission checklist
- [x] `criteria.md` (+ any revisions beneath originals)
- [x] `RUNNING.md`
- [x] `README.md` with all nine sections
- [x] ≥8 new commits; criteria commit precedes results commit; both named
- [ ] Same repo URL as the earlier submission (same repo; resubmit so the grader sees the new commits)

## Run-log format (use for before and after)
```
| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. ... | ... | | | | |
```

---

## Lecture notes (AI201 L9 slides)
- Grade is in the testing, not the building. "Cut it until it's one thing." Any "rewrite" in the plan = wrong plan.
- **Instrument BEFORE you deploy** — can't add a log line to a run that already happened. Minimum fields: timestamp · input · output · duration. Structured, not `print()`. Log failures. Think INFO vs ERROR levels.
- Models add questions classic monitoring misses: what did it say, was it good, what did it cost.
- Render free tier: 512 MB RAM (fine for an API client), sleeps after ~15 idle min (~1 min wake), **no persistent disk** (commit anything you keep).
- Latency criterion trap: say **warm vs any request** in the criterion. Catching a cold start is a real, diagnosable miss; moving the number afterwards is not allowed.
- Criteria: ≥3 about the extension, ≥1 about a wrong/bad path, commit `criteria.md` BEFORE running anything, name both commits.
- Rate limiting reference: flask-limiter (Provenance Guard used it).
- **Week 10 Demo Day:** standup (2 min: what I built + show it running / a criterion with its number / what the test found, name a miss / the improvement + what's still broken). Testing round: a peer starts my project from `RUNNING.md` alone, no asking, and uses it (ordinary then unexpected). Project must be running and RUNNING.md filled out.
- **Final project due Sunday.** Also: end-of-course survey email; fast-track Spring 2027 seat.

## Shape candidate: C — WebMCP front door (decision pending)
Idea: smallest possible WebMCP. Serve one HTML page from `serve.py` at `/` (a form that POSTs to `/ask`) and register ONE tool, `find_fit`, in it so a browser agent can call FitFindr. Deploy on Render (Path A). Page works without WebMCP (feature-detect `document.modelContext`).
Out of scope (draft): second tool; MCP-server rewrite or moving `suggest_outfit`/`create_fit_card` onto MCP; polished UI/design; auth; non-Chrome support; touching search ranking.
Open risks: WebMCP is an origin trial (Chrome 149+) / flag `chrome://flags/#enable-webmcp-testing`; API shape still changing; peers need that flag in the testing round, so RUNNING.md must say so and the plain form must work without it.

## Decision record
| Date | Decision | Why |
|---|---|---|
| 2026-11-16 | System: FitFindr (project 2) | See comparison below; confirmed by user |

### Candidate comparison
| Project | Fit | Notes |
|---|---|---|
| 1 Unofficial Guide (RAG) | Strong | API-only + small ONNX embedder; criterion 1 still missed; BM25 already pinned → clean Shape C (hybrid search). Chroma store + corpus make hosting heavier. |
| **2 FitFindr (agent)** | **Strongest** | Only Gemini + Flask/gunicorn/mcp deps → fits Path A's 512 MB; `trace.py`, `serve.py`, `RUNNING.md` already exist; many bad paths (LLM empty/rate-limit, MCP server restarts per call, no-match search). Known open issues give real criteria. |
| 3 TakeMeter (classifier) | Weak | torch/transformers → Path B only; no serving or logging; README unfinished. |
| 4 Provenance Guard | Medium | Already has `audit.jsonl` and rate limiting, but torch + GPT-2 → Path B; its open problems are signal redesign, too big for one unit. |

## Update Log
| Date | Milestone | What changed | Commit |
|---|---|---|---|
| 2026-11-16 | — | Created this tracker | — |
| 2026-11-16 | Pre-M1 | Baseline check: `python test.py` 10/10 pass; `app.py ask 'vintage graphic tee under $30'` runs all 4 stages (parse → search via MCP → outfit → fit card). Note: responses are cached ("0 model calls, 2 from cache") — cost/latency measurements must bypass the cache. | — |
| 2026-11-18 | Pre-M1 | Added `architecture.excalidraw` (entry points, agent loop, MCP boundary, LLM path/cache, trace, failure path) | — |
| 2026-11-18 | M1 | README `## Capstone` skeleton: What This Extends, The Shape, out-of-scope | see git log |
| 2026-11-18 | Pre-M1 | Read L9 slides into tracker; researched WebMCP; drafted Shape C candidate | — |
| 2026-11-18 | M2 | `static/index.html` (form + WebMCP `find_fit` registration, feature-detects `document.modelContext` then `navigator.modelContext`); `GET /` in `serve.py`. Page JS checked against a jsdom stub, NOT real Chrome. | see git log |
| 2026-11-18 | M3 | `runlog.py` JSONL log on every `/ask`; `measure_cost.py`; `RUNNING.md` capstone section; `render.yaml`; README Running It / Instrumentation / What It Costs. Clean-clone run failed first on macOS port 5000 (AirPlay) → documented `PORT=5001`. Measured: 710 tokens, 2 model calls, median 3.6 s (one 39.7 s outlier, undiagnosed) per run. Found: non-object JSON body → HTML 500. | see git log |

## Rubric audit (2026-11-21, against the scored first submission: 25/60)

| # | Item | Pts | Now |
|---|---|---|---|
| 1 | Required evidence, ≥8 commits, How I Used AI | 4 | Done: 20+ capstone commits, How I Used AI written |
| 2–4 | Criteria carry targets, testable, reasons | 15 | Done (criteria 6–11 in criteria.md) |
| 5 | Criteria about the extension | 3 | Done (6–11); 9 and 10 only informally measured |
| 6–7 | README describes it, runs observable | 8 | Done, plus hosted RUNLOG records |
| 8 | Runs actually happened | 5 | Done: trials.py, before/after files, criteria committed first |
| 9 | Verdicts right | 6 | Done; 9 "not verified", 10 "likely met, not counted" stated plainly |
| 10 | Every miss diagnosed | 7 | 7, 11, multi-item and the 39.7 s outlier (rate-limit pacing) diagnosed |
| 11 | Improvement follows diagnosis, measured | 6 | Done (criterion 7: 2/5 → 5/5) |
| 12 | Cost and what's left | 6 | Done |
| 13 | Second measured improvement (stretch) | 2 | Done (criterion 11: 3/5 → 5/5) |
| 14 | Latency breakdown (stretch) | 1 | Partial: per-step timings from one hosted run; not declared as a stretch |
| 15 | Load observation (stretch) | 1 | Not done |
| 16 | Both run paths (stretch) | 1 | Path A deployed on Render, Path B tested locally |

Status 2026-11-21: complete. Criterion 7 fix confirmed on the live Render site (`{"query": 5}` returns a 400 JSON error). Open and stated in the README: criteria 9 and 10 not counted, no model has chosen `find_fit` on its own, no load test.
