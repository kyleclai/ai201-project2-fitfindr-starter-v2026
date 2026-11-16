# Unit 3 progress tracker — FitFindr

Check items off as they're done. Due: **Sunday, Oct 4th 11:59PM PDT** (per the unit page).

## Setup
- [x] Repo cloned, `.venv` created, `requirements.txt` installed
- [x] `.env` created from `.env.example`
- [ ] **YOU:** paste your real `GEMINI_API_KEY` into `.env` (never commit it), then `python test.py` should pass
- [ ] **YOU:** push to your fork and submit the fork URL in the Course Portal

## Milestone 1 — Read the data, run the starter (~30 min)
- [x] `python app.py fields` / `listings --full -n 6` read
- [x] Wardrobe shape noted (empty wardrobe = `{"items": []}`)
- [x] Starter run with `ask`
- [x] Commit #1

Fields: `id, title, description, category, style_tags, size, condition, price, colors, brand (often null), platform`

## Milestone 2 — Spec the tools (~40 min)
- [x] Tool Inventory in README (inputs w/ types, return, empty case) for all 3 tools
- [x] Branch rule written as a rule
- [x] Commit #2

## Milestone 3 — Acceptance criteria (~40 min)
- [x] `criteria.md` criteria 3, 4, 5 written (state / fit card / own choice)
- [x] A "why this target" under all five
- [x] Commit #3

## Milestone 4 — Build the tools (~85 min)
- [x] `search_listings` (returns `[]` on no match)
- [x] `suggest_outfit` (handles empty wardrobe)
- [x] `create_fit_card` (varies across runs; not cached/temp 0)
- [ ] Each tested from terminal; output pasted in README Sample Run
- [x] Commit #4

## Milestone 5 — Loop and state (~60 min)
- [x] `agent.py::run_agent` fills session after every call and reads from it
- [x] Empty search stops before `suggest_outfit`, `fit_card` stays `None`, message names what to change
- [x] Happy path verified: `selected_item` is what reached `suggest_outfit`
- [x] Commit #5

## Milestone 6 — Write-up and submit (~30 min)
- [ ] README: What This Does, Planning Loop, Sample Run, How I Used AI
- [ ] Final check: `criteria.md` + README sections + 4+ new commits
- [ ] Push; submit fork URL

## Still open (needs your API key)
- [x] (done) Add key to `.env`, then run the three per-tool terminal tests and one full `ask` with the real model; paste the output into README **Sample Run** (search test and the empty-search run are already real output; model outputs aren't pasted yet)
- [x] (drafted, edit to match what you remember) Write **How I Used AI** (two real moments — see README)
- [ ] Read criteria.md 3-5 and make sure you'd defend them (the unit says criteria should be yours)

## Notes / findings
- Happy-path state check was done with the two model tools mocked: `selected_item` id == id received by `suggest_outfit` == id received by `create_fit_card` for 5/5 queries. Not yet confirmed with the live model.
- Size matching is whole-token (`S/M` -> s, m) so `S` doesn't match `US 7`.
