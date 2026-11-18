# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is a thrifting agent. You type what you want in plain language ("a vintage graphic tee under $30, size M"), and it searches a file of 40 secondhand listings, picks the best match, suggests outfits that combine it with pieces from your wardrobe, and writes a short caption you could post. If nothing in the listings matches, it stops early and tells you which part of the query to loosen instead of making something up.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the listings file by price and size, scores what's left by keyword overlap with the description, and returns the matches best first. Does not call the model.
- **Inputs:** `description` (str), `size` (str | None, default None), `max_price` (float | None, default None, inclusive).
  Size match: the listing's size is split into tokens on anything that isn't a letter or digit (`"S/M"` -> `s`, `m`; `"US 8"` -> `us`, `8`), and the query size must equal one token, case-insensitively. So `M` matches `M`, `S/M`, `M/L` but not `XL` or `US 8`; `S` does not match `US 7`.
- **Returns:** A `list[dict]` of at most `config.SEARCH_RESULT_LIMIT` (10) listing dicts, best match first. Each dict is a full listing record with `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), `platform` (str).
- **When it has nothing:** An empty list `[]` — never `None`, never an exception. That includes a description with no usable keywords.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits that combine the found item with pieces the user already owns, naming those pieces.
- **Inputs:** `new_item` (dict — one listing dict as returned by `search_listings`), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts; may be empty).
- **Returns:** A non-empty `str` of outfit suggestions. With a non-empty wardrobe it names specific wardrobe pieces by their `name`.
- **When it has nothing:** With an empty wardrobe (`{"items": []}`), it still returns a non-empty `str`: general styling advice for the item. It never raises and never returns `""`.

### `create_fit_card`

- **What it does:** Asks the model for a short, postable caption about the find that mentions the item, its price, and its platform.
- **Inputs:** `outfit` (str — the output of `suggest_outfit`), `new_item` (dict — the listing dict).
- **Returns:** A `str` of two to four sentences — the caption.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a descriptive `str` ("Can't write a fit card without an outfit suggestion.") without calling the model. It never raises on that input.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names what the user could change (drop the size, raise the price ceiling, use fewer or more general keywords) and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise, put the first result in `session["selected_item"]` and go to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** regex — a price ceiling from `under/below/less than/max/up to $N` (or a bare `$N`), a size from `size X` or `in a/an X`; whatever is left is the keyword description.

**What moves through the session:** `query` -> `parsed` (description, size, max_price) -> `search_results` -> `selected_item` -> `outfit_suggestion` -> `fit_card`. Each tool's input is read back out of the session, not passed from the previous call's local variable. `error` is set only when the run stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   **Outfit 1: Effortless Grunge**
Pair the graphic tee with your Baggy straight-leg jeans and Black combat boots. Cinc the jeans with the Brown leather belt, and layer the Vintage black denim jacket on top. Finish the look with the Black crossbody bag for an easy, everyday streetwear vibe.

**Outfit 2: Streetwear Contrast**
Tuck the graphic tee into your Wide-leg khaki trousers, accented by the Brown leather belt. Throw the Black cropped zip hoodie over your shoulders or wear it unzipped, and step into the Chunky white sneakers. Grab the Black crossbody bag to complete this relaxed, edgy combination.

  Fit card: Finally found the ultimate 2003 tour bootleg tee on Depop and I am obsessed. It was only $24, and the black-on-black graphic gives off such a effortless, beat-up grunge vibe. Can’t wait to style this with baggy denim and beat-up combat boots for an easy everyday fit.
```

**Empty search (the branch)**

```
$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing matched 'designer ballgown', size XXS, under $5. Try to drop the size or try a nearby one; raise the price ceiling; use fewer or more general keywords (e.g. 'tee' instead of a brand name).

0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(x['title'],x['price']) for x in search_listings('graphic tee', max_price=30)][:3])"
[('Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('Y2K Baby Tee — Butterfly Print', 18.0), ('Vintage Band Tee — Faded Grey', 19.0)]
```

```
$ python -c "from tools import suggest_outfit, search_listings; from utils.data_loader import get_empty_wardrobe; print(suggest_outfit(search_listings('graphic tee',max_price=30)[0], get_empty_wardrobe()))"
Channel the Y2K grunge vibe with two easy looks:

**Look 1 (Casual Edge):** Pair the tee with baggy, light-wash denim or distressed cargo pants. Add a well-worn leather belt and chunky skate sneakers (like vintage Vans or chunky trainers) for an effortless streetwear aesthetic.

**Look 2 (Layered Streetwear):** Wear it layered over a long-sleeve black mesh top or striped tee. Combine with a pleated plaid mini skirt or relaxed black trousers, and finish the outfit with platform boots and a silver chain necklace to lean into the authentic concert-bootleg look.
```

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card, search_listings; item=search_listings('graphic tee',max_price=30)[0]; [print(i+1, create_fit_card('Pair with baggy dark-wash jeans and white sneakers.', item)) for i in range(3)]"
1 Stoked to finally score this 2003 tour bootleg tee after hunting for the ultimate grunge streetwear vibe. I managed to snag it on Depop for just $24, and the black fade is already *so* perfectly broken in. Can't wait to style it with some baggy dark-wash denim and crisp white sneakers.
2 Found this absolute gem on Depop and I'm honestly obsessed. For just $24, this 2003 tour bootleg tee brings the ultimate grunge streetwear vibe. Can’t wait to style it with some baggy dark-wash jeans and beat-up white sneakers.
3 Scored this 2003 tour bootleg tee on Depop for just $24 and I'm honestly obsessed. The faded black grunge vibe is unmatched, especially with baggy dark-wash jeans and fresh white sneakers. Streetwear gold for real.
```

Note: with the cache on (the default), the same three calls returned one identical caption three times; `AI201_CACHE=0` gives three different ones. Temperature is already 0.9, so the cache was the cause.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave Claude the unit 3 page and my repo and asked it to build search_listings from the spec I wrote in the Tool Inventory. The starter warned that a plain substring test lets "s" match "us 9", so I wanted to see how it handled sizes.
- *What came back:* it split each listing's size into whole tokens ("S/M" becomes s and m, "US 8" becomes us and 8) and only counts a match if my size equals one token. Which is why `M` matches `S/M` and `M/L` but not `XL`, and why `S` doesn't match `US 7`. It also returned an empty list, not None, when nothing matched.
- *What I changed:* I didn't change the code. I checked it against the data instead of trusting it: size S only returned S and S/M listings (no shoes), and size 8 only returned the US 8 sneakers. I copied the size rule into my Tool Inventory so the spec matches the code.
- *What I learned:* what counts as a size match is a design decision, and it has to be written in the spec. A substring test would have returned shoes for a small top, and I wouldn't have noticed until I tested criterion 5 in unit 4.

**Moment 2**

- *What I asked for:* I ran create_fit_card three times on the same item to see if the captions would differ, like Milestone 4 says.
- *What came back:* three word-for-word identical captions. TEMPERATURE was already 0.9, so it wasn't the temperature, which left the cache.
- *What I changed:* I turned the cache off with `AI201_CACHE=0` and ran it again, and got three different captions. The cache was handing back the answer it already had. I left the code alone and added a note to my Sample Run so I remember to turn the cache off when I test in unit 4.
- *What I learned:* a bug can come from a setting and not from my code. It also matters for criterion 4: if I tested the fit card with the cache on, I'd be measuring the cache and not the model, and I'd think the card never varied.

**Unit 4**

**Moment 3**

- *What I asked for:* I asked Claude to move `search_listings` onto MCP and to write a scorer for my five criteria, because `run_eval.py` leaves PASS/FAIL blank and so verdicts can become moreso from the wording of my criteria.
- *What came back:* two things. first, the tool registered in `mcp_server.py`, w/ a description written for someone who can't see my code: it names the types (`description` is a string, `max_price` is a float in whole US dollars, inclusive), says how size matching works, and says it returns an empty list and never null when nothing matches. Second, `score_eval.py`, which wraps `suggest_outfit` and `create_fit_card` to record the item id each one actually received and then checks each criterion I made.
- *What I changed:* I didn't change the scorer's rules to make anything pass. The scorer marked the slip-dress card "30 bucks" as a FAIL for the price check, bc criterion 4 says a dollar amount, and I kept it as a FAIL even though a person would call "30 bucks" fine. That miss is the pretty much the whole basis of my diagnosis and my improvement. I also checked the MCP move by comparing `call_tool(...)` with the direct call on three queries (a normal one, the impossible one, & one w/ no filters) and they matched, including the empty list.
- *What I learned:* a tool description is a contract, not a comment, and thus an empty case is part of it. Additionally, a scorer is only as good as how you rewrite/word the check: my sentence counter uses a simple regex and could miscount a caption with "..." or an abbreviation, so I trust the price and platform checks more than the sentence count.

**Moment 4**

- *What I asked for:* after the before run I asked Claude why the slip-dress fit card said "30 bucks" and what the smallest fix was. My instructions stated: only make one change, measure it, and make it part of the retrospective report.
- *What came back:* the cause was in the prompt I made. It said to mention the price once but I never stated how to write it, so the model picked its own wording. The suggested fix was one added line telling the model to write the price exactly like `$30`, never as words like "bucks".
- *What I changed:* only that line in `create_fit_card` in `tools.py`. Before I trusted/approved it, I measured it two ways: the full after run (criterion 4 went from 4/5 to 5/5) and a separate check of 10 fit cards, 2 per item, with the cache off and the outfit text held fixed so only the prompt could vary (9/10 before, 10/10 after; the earlier failure was the same slip dress with "30 bucks").
- *What I learned:* a better result after a change isn't proof. One miss in five could have been luck, and I only have three small samples pointing the same way, so I believe that "it looks like it helped" and not definite w my assertation that "it worked". Holding the outfit text fixed in the 10-card check mattered too, bc otherwise I couldn't tell whether the prompt or the outfit changed the result.


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

Five criteria, five tries each, cache off. Produced by `score_eval.py` (it reuses `run_eval.py::run_once` and applies my criteria mechanically; `run_eval.py` alone leaves PASS/FAIL blank). What a "try" is: criteria 1 and 2 are one query run five times; criteria 3 and 4 are five different items, one run each (try i = item i); criterion 5 is five search queries with a price ceiling and a size, run through the MCP tool. Full output: `results/scored_2026-11-15_1849_before.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item found is the item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card reads like a post | 4 of 5 | PASS | PASS | PASS | FAIL | PASS | MET (4/5), openings distinct |
| 5. Search respects price ceiling and size | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 4's opening-words check: every card started differently (`scored this 2003 tour bootleg`, `scored this vintage champion track`, `still obsessed with how clean`, `found my dream dress on`, `found my new favorite outerwear`), so the criterion's second condition held.

**Real output from one try** — the one that failed (criterion 4, try 4). Produced by `tools.py::create_fit_card`, called from `agent.py::run_agent`:

```
query: silk slip dress in midi length under $40
parsed: {'description': 'silk slip dress in midi length', 'size': None, 'max_price': 40.0}
error: None
selected_item: 90s Silk Slip Dress — Floral, Midi Length
fit_card: Found my dream dress on Depop for just 30 bucks and I am never taking it off. This ivory floral silk midi is giving the ultimate 90s cottagecore romance, but I’m obsessed with throwing an oversized grey crewneck right over it to make it grunge. Such a good little vintage score.
```

And one passing try for criterion 3 (`agent.py::run_agent`, with `suggest_outfit` and `create_fit_card` wrapped to record the item id they received): `selected/outfit/card/results[0] = ('lst_006', 'lst_006', 'lst_006', 'lst_006')` for `'vintage graphic tee under $30'`.

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET | 5 of 5 tries returned a non-empty outfit and a non-empty fit card with no error. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | 5 of 5 tries set `session["error"]`, left `outfit_suggestion` and `fit_card` as `None`, never called `suggest_outfit`, and the message named the size, price and keywords from the query. |
| 3 | The item search found is the one the next tools get | 5 of 5 | MET | For all 5 items the id in `selected_item`, the id `suggest_outfit` received, the id `create_fit_card` received and `search_results[0]` were identical. |
| 4 | The fit card reads like a real post | 4 of 5 | MET (4/5, at the line) | 4 of 5 cards had 2–4 sentences, a `$` price and the platform name, and all 5 openings were different. Item 4 failed: it wrote "30 bucks". Read plainly, "30 bucks" is not a dollar amount in the sense I wrote, so I counted it as a FAIL and it sits exactly on the target. |
| 5 | Search never shows items over my price or in the wrong size | 5 of 5 | MET | 0 violations across 5 queries (1 to 4 results each). |

**Diagnoses**

- **Criterion 4, the one miss (model's output).** The card for the silk slip dress wrote "30 bucks" instead of "$30". `create_fit_card` worked and the tool returned the right item; the prompt told the model to "mention the price" but never said how to write it, so the model chose its own wording. A second check of fit cards only (10 cards, 2 per item, cache off, fixed outfit text) failed once, again on the slip dress with "30 bucks", so it was the prompt and not one unlucky draw. It is one problem on one tool, not a pattern across tools.
- **No misses elsewhere, but my targets were soft in places.** Criterion 1 passed 5 of 5 against a target of 4, so I would tighten it to 5 of 5. Criteria 2, 3 and 5 are deterministic code with no model in the path, so they could only fail if the code was wrong; passing them says the code is right but doesn't say much about my targets. Criterion 5 also passed with result lists of only 1 to 4 items, so it would pass on an empty list too.
- **Something my criteria don't measure.** Search is an any-keyword match, so it returns loosely related items under the real match: `'silk slip dress in midi length'` also returned the Y2K Baby Tee and a silk button-down, and `'graphic tee'` returned cargo pants low in the list. Criterion 5 and the 'first result' choice hide this, because the best match is ranked first. If I added a criterion, it would be about the first result being the right category.

---

## Loop Trace

Produced by `python app.py ask '...' --trace` (`agent.py::run_agent` calling `trace.step`). The MCP call is step 2.

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query (regex)
      in:  'vintage graphic tee under $30'
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
[3] suggest_outfit
      in:  new_item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), wardrobe_items=10
      out: **Outfit 1: Effortless Grunge** Pair the graphic tee with your Baggy straight-leg jeans and Black combat boots…
[4] create_fit_card
      in:  new_item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), outfit=605 chars
      out: Scored this 2003 tour bootleg graphic tee on depop for $24 and it honestly might be my new favorite streetwear…
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query (regex)
      in:  'designer ballgown size XXS under $5'
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
[3] branch: search came back empty
      →    stopping, suggest_outfit and create_fit_card are not called
```

The empty path is visibly shorter: three steps, stopping at the branch, with no `suggest_outfit` or `create_fit_card`.

**The three failure modes, triggered on purpose**

1. **Empty search** — the trace above. Message: *Nothing matched 'designer ballgown', size XXS, under $5. Try to drop the size or try a nearby one; raise the price ceiling; use fewer or more general keywords (e.g. 'tee' instead of a brand name).*
2. **Empty wardrobe** — `python app.py ask 'leather belt' --empty-wardrobe` returned general styling advice ("This versatile brown braided belt adds subtle texture… Outfit Idea 1 (Casual Daytime)…") and a normal fit card. No crash and not an empty string.
3. **Model unavailable** — I changed the first character of the key in `.env` and ran a query I hadn't asked before, `'crochet halter top size S'`. The trace stopped at step 3 and the agent said: *The model couldn't be reached, so I couldn't write the outfit or the fit card. Check that GEMINI_API_KEY in your .env is correct and that you're online, then run the same query again.* I put the key back afterwards. The handlers (`ModelUnavailable`, `QuotaGuard` and `MCPError`) are in `agent.py::run_agent`.

**On the MCP move:** `search_listings` is now registered in `mcp_server.py` with a description that names the types, the units (whole US dollars, inclusive) and the empty case, and `run_agent` calls it with `mcp_client.call_tool("search_listings", ...)` instead of calling `tools.py` directly. The return value did not change: I compared `call_tool(...)` with the direct call on three queries (a normal one, the impossible one and one with no filters) and the lists were equal, including the empty list `[]`. The only difference I noticed is that every call starts a server process, so it is slower per call, and I added an `MCPError` handler so a dead server produces a message rather than a stack trace.

---

## The Improvement

**What I changed:** one line in the `create_fit_card` prompt in `tools.py`. It now says to write the price as a dollar figure exactly like `$30` (digits with a dollar sign), never as words like "bucks". Nothing else changed.

**Which failure it was meant to fix:** criterion 4, try 4, where the card wrote "30 bucks" and failed the price check. The diagnosis was that the prompt never said how to write the price.

### Run Log — After

Full output: `results/scored_2026-11-15_1852_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item found is the item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card reads like a post | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5), openings distinct |
| 5. Search respects price ceiling and size | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:** It looks like it helped, but the evidence is small. Criterion 4 went from 4 of 5 to 5 of 5, and in the 10-card fit-card-only check the pass count went from 9 of 10 to 10 of 10, with the one earlier failure being the "30 bucks" card. That is three small samples pointing the same way, and the mechanism (the prompt now states the format) fits, but one miss in five could easily have been luck, so I wouldn't call it proven. The other four criteria stayed at 5 of 5, so nothing else got worse.

---

## What's Still Broken

- **Criterion 4's margin.** It only passed after the prompt change, and the model can still write the price differently or run to five sentences. If I had more time I'd run 20 cards before and after to get a real rate.
- **Search precision.** The any-keyword match returns loosely related items below the real match, and none of my five criteria measures it. I stopped there because the unit allowed one improvement and the diagnosis pointed at the fit card. Next I'd require more than one keyword to match, or add a criterion about the first result.
- **Criteria 1 and 5 targets.** Criterion 1 passed 5 of 5 against 4 of 5, and criterion 5 passes on short lists. I left them as written, because changing a target after seeing the results would hide what the first test showed.
- **MCP.** Only `search_listings` is on MCP, as the unit asks. The server process restarts on every call.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

## Capstone

**What This Extends**

FitFindr, my unit 3–4 agent: parse a query, search 40 listings (over MCP), write an outfit, write a fit card. New this unit: a one-page web front end served from `serve.py`, a single WebMCP tool (`find_fit`) registered on that page so a browser agent can call FitFindr, and structured logging around every `/ask` request.

**The Shape**

Shape C, extend one capability. The capability is "a browser agent can call FitFindr as a tool." The page registers one WebMCP tool, `find_fit`, whose `execute` calls the existing `POST /ask` and returns the item, outfit and fit card (or the `session.error` message). The page also has a plain form that hits the same endpoint, so it works in any browser without WebMCP. Logging and the run path are required alongside, as for every shape.

Out of scope, decided before building:
- No second tool, and no moving `suggest_outfit` or `create_fit_card` onto MCP. Search stays the only MCP tool.
- No change to the agent loop, the search matching, or the prompts. `run_agent()` is untouched.
- No UI polish, auth, accounts, or non-Chrome WebMCP support. The page exists to carry the tool.

**Running It**

Path B: local, started with `python serve.py`, with a committed run record in `logs/runs.jsonl`. Full steps, environment and the WebMCP browser flag are at the top of [RUNNING.md](RUNNING.md). I followed RUNNING.md from a fresh clone before writing this (see Instrumentation for what it caught). Path A is configured (`render.yaml`: `gunicorn serve:app --bind 0.0.0.0:$PORT --timeout 180`) but I have not deployed it yet.

**Instrumentation**

`runlog.py` appends one JSON line per `POST /ask` to `logs/runs.jsonl`, called from `serve.py::_handle_ask`. Rejected and crashed requests are logged too. Fields on every record:

| Field | Meaning |
|---|---|
| `timestamp`, `run_id` | UTC time, and 8 hex chars to quote a record |
| `client` | `form`, `webmcp` or `other` (from an `X-Client` header the page sets), so a person and an agent can be told apart |
| `level`, `status`, `http_status` | INFO/WARNING/ERROR; `ok`, `no_results`, `bad_request`, `model_unavailable`, `quota_guard`, `mcp_error`, `crash` |
| `input` | the query |
| `output` | chosen item id/title, outfit and fit-card length, and `error` text. The full generated text is not logged |
| `duration_ms`, `wait_ms` | whole request, and the part of it spent queued behind another request |
| `model_calls`, `cache_hits`, `prompt_tokens`, `output_tokens` | what this request spent, taken from `generate.py`'s counters |

Real output from `python measure_cost.py` (10 real runs with the cache off, then three failure probes). The first ten lines are successful runs, the last three are failed ones: an empty query (400), a query that matches nothing (200 with a `no_results` message), and a JSON body that is a list instead of an object (500).

```json
{"timestamp": "2026-11-18T21:29:21.279841+00:00", "run_id": "ac30ff8c", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "vintage graphic tee under $30"}, "output": {"item_id": "lst_006", "item_title": "Graphic Tee — 2003 Tour Bootleg Style", "outfit_chars": 599, "fit_card_chars": 214, "error": null}, "duration_ms": 3434, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 552, "output_tokens": 178}
{"timestamp": "2026-11-18T21:29:24.326701+00:00", "run_id": "f6355ddd", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "baggy jeans"}, "output": {"item_id": "lst_031", "item_title": "Baggy Carpenter Jeans — Dark Wash", "outfit_chars": 561, "fit_card_chars": 246, "error": null}, "duration_ms": 3045, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 560, "output_tokens": 188}
{"timestamp": "2026-11-18T21:29:28.340404+00:00", "run_id": "86d0ddba", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "black leather jacket under $80"}, "output": {"item_id": "lst_022", "item_title": "90s Leather Bomber — Black", "outfit_chars": 509, "fit_card_chars": 222, "error": null}, "duration_ms": 4011, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 541, "output_tokens": 174}
{"timestamp": "2026-11-18T21:29:31.618673+00:00", "run_id": "e5ba0b79", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "cropped hoodie"}, "output": {"item_id": "lst_015", "item_title": "Vintage Graphic Hoodie — Faded Black", "outfit_chars": 484, "fit_card_chars": 228, "error": null}, "duration_ms": 3276, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 512, "output_tokens": 152}
{"timestamp": "2026-11-18T21:29:34.205355+00:00", "run_id": "51e6ee35", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "denim jacket under $60"}, "output": {"item_id": "lst_007", "item_title": "Denim Jacket — Light Wash, Cropped", "outfit_chars": 451, "fit_card_chars": 250, "error": null}, "duration_ms": 2584, "wait_ms": 1, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 500, "output_tokens": 150}
{"timestamp": "2026-11-18T21:29:37.741692+00:00", "run_id": "dd0e9958", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "vintage graphic tee under $30"}, "output": {"item_id": "lst_006", "item_title": "Graphic Tee — 2003 Tour Bootleg Style", "outfit_chars": 584, "fit_card_chars": 279, "error": null}, "duration_ms": 3534, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 545, "output_tokens": 187}
{"timestamp": "2026-11-18T21:29:41.426690+00:00", "run_id": "289013af", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "baggy jeans"}, "output": {"item_id": "lst_031", "item_title": "Baggy Carpenter Jeans — Dark Wash", "outfit_chars": 563, "fit_card_chars": 289, "error": null}, "duration_ms": 3682, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 551, "output_tokens": 192}
{"timestamp": "2026-11-18T21:30:21.158970+00:00", "run_id": "6d1b72cc", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "black leather jacket under $80"}, "output": {"item_id": "lst_022", "item_title": "90s Leather Bomber — Black", "outfit_chars": 526, "fit_card_chars": 220, "error": null}, "duration_ms": 39729, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 545, "output_tokens": 181}
{"timestamp": "2026-11-18T21:30:26.587805+00:00", "run_id": "2be41aad", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "cropped hoodie"}, "output": {"item_id": "lst_015", "item_title": "Vintage Graphic Hoodie — Faded Black", "outfit_chars": 576, "fit_card_chars": 228, "error": null}, "duration_ms": 5424, "wait_ms": 1, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 531, "output_tokens": 169}
{"timestamp": "2026-11-18T21:30:31.705558+00:00", "run_id": "c4a57d89", "client": "other", "level": "INFO", "status": "ok", "http_status": 200, "input": {"query": "denim jacket under $60"}, "output": {"item_id": "lst_007", "item_title": "Denim Jacket — Light Wash, Cropped", "outfit_chars": 560, "fit_card_chars": 243, "error": null}, "duration_ms": 5116, "wait_ms": 0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 522, "output_tokens": 175}
{"timestamp": "2026-11-18T21:30:31.706686+00:00", "run_id": "5a4ecbd6", "client": "other", "level": "WARNING", "status": "bad_request", "http_status": 400, "input": {"query": ""}, "output": {"error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}"}, "duration_ms": 0, "wait_ms": 0, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
{"timestamp": "2026-11-18T21:30:32.098084+00:00", "run_id": "a22b5af3", "client": "other", "level": "WARNING", "status": "no_results", "http_status": 200, "input": {"query": "neon spacesuit under $1"}, "output": {"item_id": null, "item_title": null, "outfit_chars": 0, "fit_card_chars": 0, "error": "Nothing matched 'neon spacesuit', under $1. Try to raise the price ceiling; use fewer or more general keywords (e.g. 'tee' instead of a brand name)."}, "duration_ms": 391, "wait_ms": 0, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
{"timestamp": "2026-11-18T21:30:32.099082+00:00", "run_id": "1813218e", "client": "other", "level": "ERROR", "status": "crash", "http_status": 500, "input": {"query": ""}, "output": {"error": "AttributeError: 'list' object has no attribute 'get'"}, "duration_ms": 0, "wait_ms": 0, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
```

What I noticed in the log:
- Run 8 took 39.7 s against 2-5 s for the others, with the same two model calls and about the same tokens. The tokens say it was not a bigger request, so the time went somewhere else; I have not diagnosed it. It matters for deployment: gunicorn's default 30 s worker timeout would have killed that request, which is why `render.yaml` sets `--timeout 180`.
- The last record is a real bug found by logging the failure path: `serve.py` assumes the body is a JSON object, so `[1, 2]` raises `AttributeError` and Flask returns an HTML 500. I left it unfixed because it belongs to the test half.
- Writing RUNNING.md and following it from a fresh clone: see the note under What It Costs for the run that was missing.

**What It Costs**

Measured with `python measure_cost.py`: 10 real runs, cache off (`AI201_CACHE=0`), five queries twice, each through the instrumented `/ask`. Numbers are averaged from the log records above, not from a pricing page.

| Per successful run | Mean |
|---|---|
| Model calls | 2.0 (`suggest_outfit`, `create_fit_card`; search is local) |
| Prompt tokens | 536 |
| Output tokens | 175 |
| Total tokens | 710 |
| Duration | median 3.6 s, mean 7.4 s (min 2.6 s, max 39.7 s) |

The mean is dragged up by one 39.7 s run, so the median is the honest "typical". Runs that find nothing cost 0 tokens and about 0.4 s.

For a hundred people a day, one run each: 100 x 710 = 71,000 tokens a day (about 53,600 in and 17,500 out), 200 model calls, and about 100 x 3.6 s = 6 minutes of compute, one request at a time. I have not put a dollar figure on it: the course runs on Gemini's free tier, which bills $0, and I have not read this model's paid prices. The dollar figure is 53,600 x (input price) + 17,500 x (output price) per day; `measure_cost.py` computes it if `PRICE_IN_PER_M` and `PRICE_OUT_PER_M` are set.

**Run Log and Verdicts**

_(Milestones 5–6)_

**The Improvement**

_(Milestone 6)_

**What's Still Broken**

_(Milestone 7)_

**How I Used AI**

_(Milestone 7)_

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
