"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    # Criteria 3 and 4 each need 5 DIFFERENT items, one run per item (try i = item i).
    {"name": "item 1: graphic tee", "query": "vintage graphic tee under $30",
     "wardrobe": "example", "criterion": 3},
    {"name": "item 2: track jacket", "query": "90s track jacket in size M",
     "wardrobe": "example", "criterion": 3},
    {"name": "item 3: sneakers", "query": "platform sneakers size 8",
     "wardrobe": "example", "criterion": 3},
    {"name": "item 4: slip dress", "query": "silk slip dress in midi length under $40",
     "wardrobe": "example", "criterion": 3},
    {"name": "item 5: denim jacket", "query": "denim jacket under $50",
     "wardrobe": "example", "criterion": 3},
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems


# Criterion 5 is about search_listings alone (no model), so score_eval.py runs
# these five through the MCP tool directly. Each has a price ceiling AND a size.
SEARCH_CHECKS = [
    "top size M under $20",
    "jacket size S under $50",
    "jeans size W30 under $40",
    "tee size L under $25",
    "sneakers size 8 under $50",
]
