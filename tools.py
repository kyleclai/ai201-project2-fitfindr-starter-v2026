"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "in", "on", "of", "to", "with",
    "i", "me", "my", "want", "looking", "find", "need", "some", "something",
    "under", "below", "size", "that", "is", "it", "any",
}


def _tokens(text: str) -> list[str]:
    """Lowercase alphanumeric tokens, with a trailing plural 's' removed."""
    out = []
    for t in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


def _size_matches(listing_size: str, wanted: str) -> bool:
    """
    True when `wanted` is one whole token of the listing's size.

    "S/M" -> {s, m}, "US 8" -> {us, 8}, "XL (oversized)" -> {xl, oversized}.
    Whole-token equality, so "s" does not match "us 9" and "l" does not match "xl".
    """
    have = set(re.findall(r"[a-z0-9]+", (listing_size or "").lower()))
    want = re.findall(r"[a-z0-9]+", (wanted or "").lower())
    return bool(want) and all(w in have for w in want)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    keywords = {t for t in _tokens(description) if t not in _STOPWORDS}
    if not keywords:
        return []

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size and not _size_matches(listing["size"], size):
            continue

        title = set(_tokens(listing["title"]))
        tags = set(t for tag in listing["style_tags"] for t in _tokens(tag))
        other = set(
            _tokens(listing["description"]) + _tokens(listing["category"])
            + [t for c in listing["colors"] for t in _tokens(c)]
            + _tokens(listing["brand"] or "")
        )
        score = sum(3 * (k in title) + 2 * (k in tags) + (k in other) for k in keywords)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item = _describe_item(new_item)
    owned = (wardrobe or {}).get("items") or []

    if not owned:
        prompt = (
            f"Someone is thinking about buying this secondhand item:\n{item}\n\n"
            "They haven't told us what they own. Give general styling advice: "
            "one or two outfit ideas, naming the kinds of pieces that would go "
            "with it. Keep it under 120 words."
        )
    else:
        pieces = "\n".join(
            f"- {w['name']} ({w.get('category', '')}; "
            f"{', '.join(w.get('colors', []))}; {w.get('notes', '')})"
            for w in owned
        )
        prompt = (
            f"Someone is thinking about buying this secondhand item:\n{item}\n\n"
            f"Here is what they already own:\n{pieces}\n\n"
            "Suggest one or two outfits that combine the new item with pieces "
            "from that list. Name the owned pieces exactly as listed. Keep it "
            "under 120 words."
        )

    text = (generate(prompt, temperature=config.TEMPERATURE) or "").strip()
    return text or "Pair it with simple basics in a neutral color and let it be the statement piece."


def _describe_item(item: dict) -> str:
    brand = item.get("brand") or "no brand listed"
    return (
        f"{item['title']} — {item['category']}, size {item['size']}, "
        f"{item['condition']} condition, ${item['price']:.0f} on {item['platform']}. "
        f"Colors: {', '.join(item['colors'])}. Style: {', '.join(item['style_tags'])}. "
        f"Brand: {brand}."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "Can't write a fit card without an outfit suggestion."

    prompt = (
        "Write a short social-media caption (2 to 4 sentences) for someone "
        "showing off a thrift find. It should sound like a real post, not a "
        "product description. Mention the item, its price, and the platform "
        "once each, and be specific about the vibe. Write the price as a dollar "
        f"figure exactly like ${new_item['price']:.0f} (digits with a dollar sign), "
        "never as words like 'bucks'. Don't use a hashtag wall.\n\n"
        f"Item: {_describe_item(new_item)}\n"
        f"Outfit idea: {outfit.strip()}"
    )
    text = (generate(prompt, temperature=config.TEMPERATURE) or "").strip()
    return text or f"Found {new_item['title']} for ${new_item['price']:.0f} on {new_item['platform']}."
