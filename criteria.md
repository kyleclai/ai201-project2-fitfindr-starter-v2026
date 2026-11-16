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
i picked 4 of 5 and not 5 of 5 because my search is just a keyword match on 40 listings, so if i type "tee shirt" or "sneaks" it can miss something a person would call a match. two of the three steps also call the model over the network, so one rate-limit or timeout in five tries could happen. i didn't go lower since the query has to match a listing, so if it fails there it's my loop or tool being broken, not the data.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
this path never touches the model or the network. it's a filter that returns `[]` and one `if` in `run_agent`, so nothing changes from run to run. if it misses even once the branch is wrong, so 5 of 5 is the only honest target. "naming what to change" means the message has to mention the size, price ceiling, or keywords that were actually in the query.

---

## 3. The item search found is the same one the next tools get

for 5 different queries that each match something, the `id` in `session["selected_item"]` is the same `id` that `suggest_outfit` got, the same one `create_fit_card` got, and the same as `session["search_results"][0]` — 5 of 5 queries. i check it by wrapping both tools so they record what they were called with.

**Why this target:**
i'm counting exact id matches instead of reading the output, because a state bug looks like a tool bug. a fit card about the wrong jacket still reads fine. it's 5 of 5 because it's just dict reads and writes with no model involved, so one mismatch means my loop passed the wrong value. i use `id` instead of comparing the whole dict so a harmless copy doesn't fail, but a different item always does.

---

## 4. The fit card reads like a real post even though the words change

for 5 different items, each fit card is 2–4 sentences, has the price as a dollar amount, and names the platform. at least 4 of the 5 cards pass all three checks, and no two of the 5 cards start with the same first five words.

**Why this target:**
the words are different every run (temperature is 0.9), so i'm not testing the wording. i'm checking for the three things i'd be annoyed to see missing: no price, no platform, or a caption that turns into a paragraph. i picked 4 of 5 because the model might write "eighteen bucks" instead of "$18", or run to five sentences, and that's just how the tool works. the opening-words check has no wiggle room because five items starting the same way means my prompt is making a template, which is exactly what a fit card shouldn't be.

---

## 5. Search never shows items over my price or in the wrong size

across 5 queries that each have a price ceiling and a size, every listing `search_listings` returns is at or under the ceiling and has the size i asked for as one of its size tokens. zero violations, in 5 of 5 queries.

**Why this target:**
i care about this one because a thrift search that shows a $55 item for "under $30", or shoes when i asked for a small top, looks broken and makes me stop trusting the rest. it's plain code with no model, so the target is zero violations and not a percentage. the filter either compares right or it doesn't. the size part is the likeliest to break (`"s" in "us 9"` is true with a plain substring test), which is why i check size and not just price.

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
