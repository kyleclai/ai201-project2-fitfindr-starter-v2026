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
- *What came back:* it split each listing's size into whole tokens ("S/M" becomes s and m, "US 8" becomes us and 8) and only counts a match if my size equals one token. It returned an empty list, not None, when nothing matched.
- *What I changed:* I didn't change the code, but I tested it myself instead of trusting it. Size S only returned S and S/M listings (no shoes), and size 8 only returned the US 8 sneakers. I also copied the size rule into my Tool Inventory so the spec matches the code.

**Moment 2**

- *What I asked for:* I ran create_fit_card three times on the same item to see if the captions would differ, like Milestone 4 says.
- *What came back:* three word-for-word identical captions, even though TEMPERATURE was already 0.9. So it wasn't the temperature.
- *What I changed:* I turned the cache off with `AI201_CACHE=0` and ran it again, and got three different captions. The cache was handing back the answer it already had. I left the code alone and added a note to my Sample Run so I remember to turn the cache off when I test in unit 4.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
