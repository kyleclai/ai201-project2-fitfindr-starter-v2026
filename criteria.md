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
I picked 4 of 5 and not 5 of 5 because my search is just a keyword match on 40 listings, so if I type "tee shirt" or "sneaks" it can miss something a person would call a match. Two of the three steps also call the model over the network, so one rate-limit or timeout in five tries could happen. I didn't go lower since the query has to match a listing, so if it fails there it's my loop or tool being broken, not the data.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never touches the model or the network. It's a filter that returns `[]` and one `if` in `run_agent`, so nothing changes from run to run. If it misses even once the branch is wrong, so 5 of 5 is the only honest target. "Naming what to change" means the message has to mention the size, price ceiling, or keywords that were actually in the query.

---

## 3. Item search found is same one the next tools get

For 5 different queries that each match something, the `id` in `session["selected_item"]` is the same `id` that `suggest_outfit` got, the same one `create_fit_card` got, and the same as `session["search_results"][0]` — 5 of 5 queries. I check it by wrapping both tools so they record what they were called with.

**Why this target:**
I'm counting exact id matches instead of reading the output, because a state bug looks like a tool bug. A fit card about the wrong jacket still reads fine. It's 5 of 5 because it's just dict reads and writes with no model involved, so one mismatch means my loop passed the wrong value. I use `id` instead of comparing the whole dict so a harmless copy doesn't fail, but a different item always does.

---

## 4. Fit card reads like a real post even though words change

For 5 different items, each fit card is 2–4 sentences, has the price as a dollar amount, and names the platform. At least 4 of the 5 cards pass all three checks, and no two of the 5 cards start with the same first five words.

**Why this target:**
The words are different every run (temperature is 0.9), so I'm not testing the wording. I'm checking for the three things I'd be annoyed to see missing: no price, no platform, or a caption that turns into a paragraph. I picked 4 of 5 because the model might write "eighteen bucks" instead of "$18", or run to five sentences, and that's just how the tool works. The opening-words check has no wiggle room because five items starting the same way means my prompt is making a template, which is exactly what a fit card shouldn't be.

---

## 5. Search never shows items over my price or in the wrong size

Across 5 queries that each have a price ceiling and a size, every listing `search_listings` returns is at or under the ceiling and has the size I asked for as one of its size tokens. Zero violations, in 5 of 5 queries.

**Why this target:**
I care about this one because a thrift search that shows a $55 item for "under $30", or shoes when I asked for a small top, looks broken and makes me stop trusting the rest. It's plain code with no model, so the target is zero violations and not a percentage. The filter either compares right or it doesn't. The size part is the likeliest to break (`"s" in "us 9"` is true with a plain substring test), which is why I check size and not just price.

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

---

# Capstone criteria

Written in unit 9, **before any capstone trial was run**. These are about the part
I added: the web page, the WebMCP tool `find_fit`, the run log, and the run
path. The unit 3 criteria above still describe the agent underneath.

Latency note: I am not setting a latency criterion. The hosted instance sleeps
after about 15 idle minutes and takes about a minute to wake, so any single
number would have to say "warm" or "cold", and I would only ever use it warm.
The warm median (about 3.6 s over 10 runs) is measured and reported in the README
as a measurement, not as a pass/fail target.

## 6. Every call that reaches FitFindr is logged

Across 10 calls (a mix of form submissions, `find_fit` calls from the WebMCP tool
and deliberately bad ones), `logs/runs.jsonl` gains exactly 10 records, and each
record's `client` field matches how the call was made (`form`, `webmcp`, `other`).
Zero calls missing.

**Why this target:**
The log is how I can prove that a request typed into the WebMCP extension actually reached my project and was not lost somewhere between the browser and the server. If even one call can go missing, I cannot trust the log for any of the other criteria, so the target is zero missing and not a percentage. It is a plain file write, so there is no network luck to allow for.

## 7. Every bad input to the tool fails properly, with a readable error

For 5 bad inputs (an empty query, a whitespace-only query, a number where the query should be a string, a JSON body that is a list instead of an object, and a 5,000-character query), each returns JSON with an `error` message in plain language and a 4xx status, never an HTML error page and never a 500. Each also leaves a log record whose `status` says what went wrong. Target: 5 of 5.

**Why this target:**
When something fails, a stack trace or an HTML page in the log is hard to read and hard to debug. Wrapping each failure into a short human-readable message makes it quick to see what the caller did wrong. These are all inputs I can construct on purpose, so there is no randomness to allow for, and a miss means a branch I did not handle. I already expect the list-body case to miss, which is part of why it is on the list.

## 8. The tool does what the original FitFindr does

For 3 queries, calling `find_fit` through the page returns `ok: true` with an item, an outfit and a fit card, and the result matches what `run_agent()` returns for the same query: same item id, and the item respects the price ceiling in the query. Target: 3 of 3.

**Why this target:**
This is the core of the extension. The tool the website offers has to actually work, and it has to give the same answer as the original FitFindr, otherwise the WebMCP layer is changing the product instead of exposing it. Item choice is deterministic code, so the item id must match exactly. The outfit and fit card text come from the model, so I compare those only for being present and non-empty unless the cache makes them identical.

## 9. RUNNING.md alone is enough to use it and to start it

A reader who has only RUNNING.md can (a) say in one sentence what WebMCP is, from its short explainer, (b) get a result from the hosted URL, and (c) start the project themselves from a clean clone for when the hosted copy is down. Target: 3 of 3 attempts, no questions asked of me.

**Why this target:**
My peers will mostly open the Render site and start trying things, and the Render copy will not stay up forever. RUNNING.md has to carry both jobs: explain the interesting part (WebMCP) in practical terms, and give the steps to run it locally. I tested the clean clone once already and it exposed a real problem (macOS port 5000), so I do not trust it to work without a check.

## 10. The browser setup for WebMCP works from the written steps

On a Chrome profile that has never had the flag set, following only the browser setup steps in RUNNING.md (Chrome version, the `chrome://flags/#enable-webmcp-testing` flag, the Model Context Tool Inspector extension), the page's status line reads "tool find_fit registered", the Inspector lists `find_fit`, and Execute Tool with `{"query": "vintage graphic tee under $30"}` returns `ok: true`. Target: 3 of 3 fresh-profile attempts.

**Why this target:**
WebMCP is experimental, so the browser setup is part of the product, not a side detail: every test of this idea needs it. If the steps are wrong or incomplete, nobody can reach the feature at all. The tool call goes through the Inspector's Execute Tool path, not through its Gemini chat box, because the chat step depends on a Google model that returned 503 for me and is outside my project.
