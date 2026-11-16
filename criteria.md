# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 rather than 5 of 5 because search is a plain keyword match against 40 listings, so a phrasing like "tee shirt" or "sneaks" can miss a listing that a person would call a match. Two of the three steps also call a model over the network, so one rate-limit or timeout in five tries is plausible. I didn't go lower because "matches at least one listing" means I only count queries where search has something to find; a miss there would be a loop or tool bug, not a data gap.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never touches the model or the network: it's a filter that returns `[]` and one `if` in `run_agent`. Nothing about it varies run to run, so any miss means the branch is wrong, not that the run was unlucky. 5 of 5 is the only target that is honest for deterministic code. "Naming what to change" is checkable: the message must mention at least one of the size, the price ceiling, or the keywords that was actually in the query.

---

## 3. Something about state

For 5 different queries that each match something, the `id` of `session["selected_item"]` equals the `id` of the `new_item` received by `suggest_outfit`, the `id` received by `create_fit_card`, and the `id` of `session["search_results"][0]` — 5 of 5 queries, checked by wrapping both tools to record the argument they were called with.

**Why this target:**
This is a count of exact id matches, not a read of the output, because state failure looks like a tool problem: a fit card about the wrong jacket still reads fine. It's 5 of 5 because the state is plain dict reads and writes with no model in the path; one mismatch means the loop passed a stale or different value. I used `id` rather than comparing whole dicts so a harmless copy doesn't count as a failure, while a different item always does.

---

## 4. Something about the fit card

For 5 different items, each fit card is 2–4 sentences, contains the item's price written as a dollar amount, and names its platform, and no two of the 5 cards open with the same first five words — at least 4 of the 5 cards must pass all three checks, and the no-shared-opening check must hold across all 5.

**Why this target:**
The words will differ every run (temperature is 0.9), so I'm not testing wording; I'm testing three things I'd be unhappy to see missing: no price, no platform, or a caption that's a paragraph. 4 of 5 rather than 5 of 5 because a model sometimes writes "just $18" as "eighteen bucks" or runs to five sentences, and that's the nature of the tool. The shared-opening check has no slack because five items that open identically means the prompt is producing a template, which is the one failure I said a fit card can't have.

---

## 5. Your choice

Across 5 queries that each include a price ceiling and a size, every listing `search_listings` returns is at or under the ceiling and has the requested size as one of its size tokens — zero violations in 5 of 5 queries.

**Why this target:**
I care about this because a thrift search that returns a $55 item for "under $30", or shoes for a small top, reads as broken and makes the user stop trusting the rest. It's pure code with no model, so the target is zero violations rather than a percentage: the filter either compares correctly or it doesn't. The size tokenizer is the part most likely to fail (`"s" in "us 9"` is true with a plain substring test), which is why the check is on size too, not just price.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
