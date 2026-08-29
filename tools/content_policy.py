#!/usr/bin/env python3
"""
The single content policy, shared by the build guard and live verification.

Standard library only, so `tools/verify-live.py` can import it without pulling
in the registry or PyYAML.

Two rules live here:

  BANNED_PHRASES        internal drafting language that must never ship
  MISLEADING_CLAIMS     claims about partnerships and products that must not
                        appear unless an approved record backs them

What gets scanned matters as much as what is scanned for:

  · HTML comments ARE scanned. A comment is served to the browser and is
    visible in View Source — an internal note there is still published.
  · Attribute VALUES are scanned; attribute NAMES are not. `placeholder="…"`
    is a legitimate form attribute, so the name must not trip a phrase check
    while the value it holds still does.
  · <script> and <style> bodies are not scanned. Minified CSS and JSON-LD
    produce noise, and neither is prose a visitor reads.
  · Anything inside an element carrying `data-public-note` is exempt. The
    exemption is structural and greppable rather than a string allow-list.
"""

import re

PUBLIC_NOTE_ATTR = "data-public-note"

# Internal drafting language. Matched on word boundaries, so "placeholder" as
# an attribute name cannot trip "Placeholder" as a phrase.
BANNED_PHRASES = [
    "Copy needed",
    "Copy and portrait needed",
    "To be confirmed",
    "Not wired up",
    "Content needed before launch",
    "Wording check needed",
    "Replace with real numbers",
    "Confirm before launch",
    "Check before launch",
    "before launch",
    "Placeholder",
    "TODO",
    "FIXME",
    "Lorem ipsum",
    "Illustrative figures",
    "UNCONFIRMED",
    # Internal document names. If one is cited on a public page, the page is
    # quoting a working note rather than telling a visitor something.
    "BUILD-SPEC",
    "ASSET-MANIFEST",
    "DESIGN-LANGUAGE",
    "TRAIL-STOPS",
    "MEASUREMENT.md",
    "EXPERIENCE-MANIFEST",
    "site-todo",
]

# Narrow editorial rule. The word "experience" is ordinary English and is not
# banned; what is banned is claiming a relationship or a live product that no
# approved record supports. This is the failure that put "in development with
# the farm" on the public site.
MISLEADING_CLAIMS = [
    r"in development with\b",
    r"in partnership with\b",
    r"\bpartnered with\b",
    r"\bofficial partner\b",
    r"\bour partners? at\b",
    r"\bin association with\b",
    r"\bsponsored by\b",
    r"\bnow live\b",
    r"\bbook (?:now|today)\b",
]

# An f-string that never got formatted. Both the bare token and the call or
# subscript forms — `{title}` leaks just as readily as `{fn()}`.
TEMPLATE_LEAKS = [
    r"\{[A-Za-z_][A-Za-z0-9_]*\}",
    r"\{[A-Za-z_][A-Za-z0-9_]*(?:\(\)|\[)[^}]*\}",
]

_PUBLIC_NOTE_RE = re.compile(
    r"<(\w+)[^>]*\b" + PUBLIC_NOTE_ATTR + r"\b[^>]*>.*?</\1>", re.S)
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
_ATTR_RE = re.compile(r"""[\w:.-]+\s*=\s*(?:"([^"]*)"|'([^']*)')""")
_TAG_RE = re.compile(r"<[^>]+>")


def surfaces(html):
    """Return (prose, attribute_values) — everything a visitor can reach.

    `prose` keeps HTML comments deliberately: they ship to the browser.
    """
    text = _PUBLIC_NOTE_RE.sub(" ", html)
    text = _SCRIPT_STYLE_RE.sub(" ", text)

    attrs = " \n".join(
        (m.group(1) if m.group(1) is not None else m.group(2))
        for m in _ATTR_RE.finditer(text))

    # Comments survive: unwrap them so their content is scanned as prose,
    # then drop the remaining tags so attribute names are not scanned here.
    prose = re.sub(r"<!--(.*?)-->", r" \1 ", text, flags=re.S)
    prose = _TAG_RE.sub(" ", prose)
    return prose, attrs


def scan(html, label=""):
    """Return a list of human-readable problems found in one page."""
    prose, attrs = surfaces(html)
    where = f"{label}  →  " if label else ""
    problems = []

    for surface, name in ((prose, "text"), (attrs, "attribute")):
        for phrase in BANNED_PHRASES:
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", surface):
                problems.append(f"{where}internal language in {name}: {phrase!r}")
        for pattern in MISLEADING_CLAIMS:
            m = re.search(pattern, surface, re.I)
            if m:
                problems.append(
                    f"{where}unsupported claim in {name}: {m.group(0)!r} — "
                    f"an approved record must back this, or it must not be said")
        for pattern in TEMPLATE_LEAKS:
            for leak in re.findall(pattern, surface):
                problems.append(f"{where}unrendered template {leak!r}")

    # Deterministic and free of the duplicates the two leak patterns produce.
    return sorted(set(problems))
