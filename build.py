#!/usr/bin/env python3
"""
IsleConnect V1 — page generator.

Re-centred on the two things that exist today:
  · Ryde 140          — Royal Victoria Arcade reconstruction
  · Wartime Trail     — Ryde to Seaview, Puckpool Battery

Shared chrome (head/header/footer) lives here once. Run:  python3 build.py
Writes every page including index.html.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Where anonymous behavioural events are posted. Empty means the measurement
# layer stays inert: it instruments every page and buffers events in the
# browser for inspection, but sends nothing and writes no storage. Set this
# to a real collector URL to switch it on — and write the privacy copy first.
# See MEASUREMENT.md.
EVENTS_ENDPOINT = ""

# ============================================================ site configuration

SITE = {
    "operator":       "David Grannum, trading as IsleConnect",
    "operator_short": "IsleConnect",
    "domain":         "isleconnect.co.uk",
    "base_url":       "https://www.isleconnect.co.uk",
    "contact_email":  "david@isleconnect.co.uk",
    # Connected diagnostic endpoint
    "form_endpoint":  "https://formspree.io/f/xvgowwzn",
    # The date a person actually read and approved the three legal notices.
    # Not a build date and not a placeholder — if the notices change, this
    # moves only when someone has read them again.
    "legal_reviewed": "29 August 2026",
}

# ============================================================ content registry
# One record per story, collection and partner. The renderer reads only these
# directories. Editorial notes live in `internal:` — a field nothing renders.

try:
    import yaml
except ImportError:                                          # pragma: no cover
    raise SystemExit(
        "\nThis build needs PyYAML to read content/.\n"
        "    pip install pyyaml        (or: py -m pip install pyyaml on Windows)\n")
import glob as _glob

CONTENT = os.path.join(ROOT, "content")

# What may appear on the production domain, and in what form. Publication
# permission comes from the record's status and from nothing else — never from
# membership of a dictionary in this file.
#
#   published   a complete public story page
#   research    the reduced public "in development" page, and nothing more
#   everything else — draft, review, approved, blocked, archived — no page
#
# `review` is deliberately not "publish with noindex": noindex is a request to
# search engines, not access control, and a page with rights-pending media must
# not sit on a public URL at all.
STATUSES = {"draft", "research", "review", "approved",
            "published", "archived", "blocked"}
PUBLISHABLE = {"published"}
RENDER_FULL = {"published"}
RENDER_REDUCED = {"research"}
RENDERABLE = RENDER_FULL | RENDER_REDUCED

# Total public pages: 21 base + ryde/ryde-town-hall.html + consultancy.html = 23
EXPECTED_PUBLIC_PAGES = 23

REQUIRED_STORY = ["id", "slug", "title", "line", "status", "collections"]


def load_registry():
    """Read content/. A duplicate id or slug is an error, never a silent
    overwrite — the record that lost would vanish without a trace."""
    reg = {"stories": {}, "collections": {}, "partners": {}}
    errs = []
    for kind, key in (("stories", "id"), ("collections", "id"), ("partners", "partnerId")):
        seen_slugs = {}
        for path in sorted(_glob.glob(os.path.join(CONTENT, kind, "*.yaml"))):
            where = os.path.relpath(path, ROOT)
            try:
                rec = yaml.safe_load(open(path, encoding="utf-8"))
            except yaml.YAMLError as e:                       # noqa: PERF203
                errs.append(f"{where}: is not valid YAML — {e}")
                continue
            if rec is None:
                errs.append(f"{where}: is empty — every record file must "
                            f"contain one record, or be deleted")
                continue
            if not isinstance(rec, dict):
                errs.append(f"{where}: must be a mapping, got {type(rec).__name__}")
                continue
            if not rec.get(key):
                errs.append(f"{where}: missing the required '{key}' field, so "
                            f"the record cannot be identified")
                continue

            rec["_path"] = where
            ident = rec[key]
            if ident in reg[kind]:
                errs.append(f"{where}: duplicate {key} {ident!r}, already declared "
                            f"in {reg[kind][ident]['_path']}")
                continue
            slug = rec.get("slug")
            if slug:
                if slug in seen_slugs:
                    errs.append(f"{where}: duplicate slug {slug!r}, already used "
                                f"by {seen_slugs[slug]}")
                    continue
                seen_slugs[slug] = where
            reg[kind][ident] = rec

    if errs:
        print("\nBUILD FAILED — content registry could not be loaded:\n")
        for e in errs:
            print("   " + e)
        print()
        raise SystemExit(1)
    return reg


def validate_registry(reg):
    """Structural gates. Phrase scanning is the safety net; this is the rule."""
    errs = []

    for sid, st in reg["stories"].items():
        for field in REQUIRED_STORY:
            if not st.get(field):
                errs.append(f"{st['_path']}: missing required field '{field}'")
        if st.get("status") not in STATUSES:
            errs.append(f"{st['_path']}: unknown status {st.get('status')!r}")

        for cid in st.get("collections") or []:
            if cid not in reg["collections"]:
                errs.append(f"{st['_path']}: unknown collection {cid!r}")

        # A published story must actually be cleared.
        if st.get("status") == "published":
            g = st.get("governance") or {}
            if g.get("rightsRecord") != "complete":
                errs.append(f"{st['_path']}: published but rightsRecord is "
                            f"{g.get('rightsRecord')!r} — rights-pending material "
                            f"cannot enter production")
            media = st.get("media") or {}
            if not media.get("video"):
                errs.append(f"{st['_path']}: published with no media")
            # Stated explicitly, every time. An absent `rights` key is not
            # consent — it is a record nobody has completed.
            if media.get("rights") != "cleared":
                errs.append(f"{st['_path']}: published but media rights are "
                            f"{media.get('rights')!r} — every published story "
                            f"needs media.rights: cleared, stated explicitly")

        # A source-checked mark is a claim; it needs the record behind it.
        marks_ = st.get("marks") or []
        if "source" in marks_ and (st.get("governance") or {}).get("editorialReview") != "complete":
            errs.append(f"{st['_path']}: carries the 'source checked' mark without "
                        f"a completed editorial review")

        # A nearby partner must exist and be approved, or the block is omitted.
        np_ = st.get("nearby")
        if np_ and np_ not in reg["partners"]:
            errs.append(f"{st['_path']}: unknown partner {np_!r}")

    for pid, pt in reg["partners"].items():
        ap = pt.get("approval") or {}
        for flag in ("inclusionApproved", "nameApproved"):
            if flag not in ap:
                errs.append(f"{pt['_path']}: approval.{flag} must be stated explicitly")
        if ap.get("inclusionApproved"):
            if not ap.get("approvedBy"):
                errs.append(f"{pt['_path']}: inclusionApproved without approvedBy")
            if not ap.get("approvedAt"):
                errs.append(f"{pt['_path']}: inclusionApproved without approvedAt")
            if not ap.get("nameApproved"):
                errs.append(f"{pt['_path']}: included but the public name is not approved")
            if not (pt.get("location") or {}).get("directionsUrl"):
                errs.append(f"{pt['_path']}: approved for inclusion but no directionsUrl")
        offer = pt.get("offer") or {}
        if offer.get("active") and not offer.get("expiresAt"):
            errs.append(f"{pt['_path']}: an active offer needs an expiry date")

    if errs:
        print("\nBUILD FAILED — content registry did not validate:\n")
        for e in errs:
            print("   " + e)
        print()
        raise SystemExit(1)
    return reg


REG = validate_registry(load_registry())

PUBLISHED = {sid: st for sid, st in REG["stories"].items()
             if st.get("status") in PUBLISHABLE}

# Never typed by hand again.
LIVE_COUNT = len(PUBLISHED)
LIVE_COUNT_WORD = {0: "No stories are", 1: "One story is", 2: "Two are",
                   3: "Three stories are"}.get(LIVE_COUNT, f"{LIVE_COUNT} stories are")


# Records are addressed by their declared `slug` field. id and slug are
# different things and are not assumed to be interchangeable.
BY_SLUG = {st["slug"]: st for st in REG["stories"].values()}

# The renderers address a story by a short key ("puckpool-battery"); the record
# declares a full page slug ("ryde/puckpool-battery"). Derive the mapping from
# the declared slug rather than from the id, which is a separate field that is
# only incidentally similar. validate_render_sources() proves the two sets
# agree, so a divergence is an error rather than a silently missing block.
RENDER_KEY_TO_SLUG = {}
for _st in REG["stories"].values():
    RENDER_KEY_TO_SLUG.setdefault(_st["slug"].rsplit("/", 1)[-1], _st["slug"])


def page_slug_for(render_key):
    """The declared slug of the record a renderer key belongs to."""
    return RENDER_KEY_TO_SLUG.get(render_key, render_key)


def story_record(page_slug):
    """The registry record that owns a rendered page, resolved by the record's
    declared `slug` — never by assuming the id and the slug are the same."""
    return BY_SLUG.get(page_slug)


def partner_for(page_slug):
    """Return an approved partner record, or None. An unapproved partner is
    not a warning on the page — the block simply does not exist."""
    st = story_record(page_slug) or {}
    pid = st.get("nearby")
    if not pid:
        return None
    pt = REG["partners"].get(pid) or {}
    ap = pt.get("approval") or {}
    if not (ap.get("inclusionApproved") and ap.get("nameApproved")):
        return None
    if not (pt.get("location") or {}).get("directionsUrl"):
        return None
    return pt


# ------------------------------------------------------------ content guard
# Safety net beneath the structural rules: catches an internal phrase that
# reaches a page by some route the schema does not cover.
#
# The policy itself lives in tools/content_policy.py so that the build guard
# and tools/verify-live.py enforce one list rather than two that drift apart.
# A banned phrase is permitted only inside an element that declares itself
# intentional public copy: <span data-public-note>To be confirmed</span>.

sys.path.insert(0, os.path.join(ROOT, "tools"))
import content_policy as _policy                              # noqa: E402

BANNED = _policy.BANNED_PHRASES
PUBLIC_NOTE_ATTR = _policy.PUBLIC_NOTE_ATTR


def guard(paths):
    problems = []
    for path in paths:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue
        problems += _policy.scan(open(full, encoding="utf-8").read(), path)
    if problems:
        print("\nBUILD FAILED — internal language found on public pages:\n")
        for pr in problems:
            print("   " + pr)
        print("\nMove the note into content/internal/ or a record's `internal:` field.\n")
        raise SystemExit(1)
    print("Content guard passed: %d public pages clean." % len(paths))


# Collections do not get top-level slots. Two fit; ten would not.
NAV = [
    ("explore.html",      "Explore"),
    ("journeys.html",     "Journeys"),
    ("for-partners.html", "Work With Us"),
    ("how-we-work.html",  "How We Work"),
    ("about.html",        "About"),
]

FOOTER_COLS = [
    ("Explore Ryde", [
        ("ryde/royal-victoria-arcade.html", "Royal Victoria Arcade"),
        ("ryde/puckpool-battery.html",      "Puckpool Battery"),
        ("ryde/ryde-town-hall.html",        "Ryde Town Hall"),
        ("explore.html",                    "All stories"),
    ]),
    ("Journeys", [
        ("ryde-140.html",      "Ryde through time"),
        ("wartime-trail.html", "Ryde to Seaview Wartime Trail"),
        ("journeys.html",      "All journeys"),
    ]),
    ("Work with us", [
        ("partners/venues.html",        "Venues & businesses"),
        ("partners/organisations.html", "Community organisations"),
        ("consultancy.html",            "Consultancy & pilots"),
        ("for-partners.html",           "Overview"),
    ]),
    ("IsleConnect", [
        ("about.html",         "About"),
        ("how-we-work.html",   "How we work"),
        ("contact.html",       "Contact"),
        ("privacy.html",       "Privacy"),
        ("accessibility.html", "Accessibility"),
        ("terms.html",         "Terms"),
    ]),
]

TRUST_BODY = ("We use source-linked local knowledge and work with the people who know "
              "the story or place. AI helps us research and build these stories faster, but "
              "people remain responsible for what gets published.")


def rel(path, depth):
    return ("../" * depth) + path


def head(title, description, depth, page="page", story=None, trail=None, stop=None):
    """page/story/trail/stop become data-ic-* attributes on <body>, which is
    where the measurement layer reads its context from. See MEASUREMENT.md."""
    events = (f'\n<meta name="ic-events" content="{EVENTS_ENDPOINT}">'
              if EVENTS_ENDPOINT else "")
    attrs = f' data-ic-page="{page}"'
    if story:
        attrs += f' data-ic-story="{story}"'
    if trail:
        attrs += f' data-ic-trail="{trail}"'
    if stop:
        attrs += f' data-ic-stop="{stop}"'
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:image" content="{rel('assets/img/card-ryde140.jpg', depth)}">
<meta name="theme-color" content="#16243D">{events}
<link rel="icon" href="{rel('favicon.ico', depth)}" sizes="48x48">
<link rel="icon" type="image/png" href="{rel('assets/img/favicon-32.png', depth)}" sizes="32x32">
<link rel="apple-touch-icon" href="{rel('assets/img/apple-touch-icon.png', depth)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel('assets/css/isleconnect.css', depth)}">
</head>
<body{attrs}>

<a class="skip-link" href="#main">Skip to content</a>
"""


def header(current, depth, over=False):
    cls = "site-header site-header--over" if over else "site-header site-header--solid"
    CUR = ' aria-current="page"'
    links = "\n      ".join(
        '<a href="%s"%s>%s</a>' % (rel(h, depth), CUR if h == current else "", label)
        for h, label in NAV)
    mobile = "\n  ".join(
        '<a href="%s">%s</a>' % (rel(h, depth), label) for h, label in NAV)
    return f"""
<header class="{cls}">
  <div class="site-header__inner">
    <a class="brand" href="{rel('index.html', depth)}"><img class="brand__mark" src="{rel('assets/img/isleconnect-mark.png', depth)}" width="34" height="34" alt=""><span>Isle<b>Connect</b></span></a>
    <nav class="nav" aria-label="Main">
      {links}
    </nav>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav">Menu</button>
  </div>
</header>

<div class="mobile-nav" id="mobile-nav">
  {mobile}
  <a href="{rel('contact.html', depth)}">Contact</a>
</div>

<main id="main">
"""


def footer(depth):
    cols = ""
    for heading, items in FOOTER_COLS:
        lis = "\n          ".join(
            '<li><a href="%s">%s</a></li>' % (rel(h, depth), label) for h, label in items)
        cols += f"""      <div>
        <h4>{heading}</h4>
        <ul>
          {lis}
        </ul>
      </div>
"""
    return f"""
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-cols">
{cols}    </div>

    <div class="footer-bar">
      <a class="brand" href="{rel('index.html', depth)}"><img class="brand__mark" src="{rel('assets/img/isleconnect-mark.png', depth)}" width="30" height="30" alt=""><span>Isle<b>Connect</b></span></a>
      <span class="powered">Powered by Vectis ONE</span>
      <span>&copy; 2026 IsleConnect</span>
    </div>
  </div>
</footer>

<script src="{rel('assets/js/isleconnect.js', depth)}"></script>
</body>
</html>
"""


def trust_panel():
    return f"""      <div class="trust">
        <span class="eyebrow">Why you can trust it</span>
        <h2>Real stories. Real places. Human checked.</h2>
        <p>{TRUST_BODY}</p>
        <ul class="ticks">
          <li>Sources checked</li>
          <li>Human reviewed</li>
          <li>Rights respected</li>
        </ul>
      </div>
"""



# ---------------------------------------------------------------- design language

THREAD_PATH = ("M0,72 C140,72 190,26 320,26 C450,26 500,74 640,74 "
               "C780,74 830,22 980,22 C1090,22 1140,52 1200,52")
THREAD_DOTS = [(320, 26), (640, 74), (980, 22)]


# Segments of one continuous route line. Each starts at the height the
# previous one finished at, so a reader following the page down the homepage
# sees a single engraved trace crossing every band rather than four separate
# ornaments. Entry/exit heights are the first and last y in each path.
#
#   a  72 → 52     b  52 → 26     c  26 → 70     d  70 → 44     e  44 → 62
#
# Segments are only chained on the homepage. Elsewhere a single 'a' is still
# a section rule, which is what it was designed as.
THREAD_SEGMENTS = {
    "a": (THREAD_PATH, THREAD_DOTS),
    "b": ("M0,52 C150,52 200,80 340,80 C470,80 520,30 660,30 "
          "C800,30 850,64 1000,64 C1100,64 1150,26 1200,26",
          [(340, 80), (660, 30), (1000, 64)]),
    "c": ("M0,26 C130,26 180,58 320,58 C450,58 500,24 640,24 "
          "C790,24 840,72 990,72 C1090,72 1150,70 1200,70",
          [(320, 58), (640, 24), (990, 72)]),
    "d": ("M0,70 C140,70 190,34 330,34 C460,34 510,76 650,76 "
          "C790,76 840,30 980,30 C1080,30 1140,44 1200,44",
          [(330, 34), (650, 76), (980, 30)]),
    "e": ("M0,44 C160,44 210,74 350,74 C480,74 530,28 670,28 "
          "C810,28 860,58 1010,58 C1110,58 1160,62 1200,62",
          [(350, 74), (670, 28), (1010, 58)]),
}


def thread(seg="a"):
    """The story thread — an engraved route line that draws itself as you
    scroll. Used between sections to say 'stories connect places' without
    writing it down."""
    path, dot_list = THREAD_SEGMENTS[seg]
    dots = "".join('<circle cx="%d" cy="%d" r="3.4"/>' % (x, y) for x, y in dot_list)
    return f"""      <svg class="thread" viewBox="0 0 1200 100" preserveAspectRatio="none"
           role="presentation" aria-hidden="true" focusable="false">
        <path d="{path}"/>{dots}
      </svg>
"""


MARK_KINDS = {
    "source":  "Source checked",
    "recon":   "Reconstruction",
    "archive": "Archive",
    "spot":    "On this spot",
    "oral":    "Oral history",
}


def marks(*kinds):
    """Evidence marks — provenance as part of the visual language rather than
    bureaucratic metadata."""
    items = "".join(
        '<li class="mark mark--%s">%s</li>' % ("oral" if k == "oral" else k, MARK_KINDS[k])
        for k in kinds)
    return '<ul class="marks">%s</ul>' % items


def placeband(*names, route=False):
    """Place typography — location names set large enough to read as landscape.

    route=True hangs each name off the story thread, so the four places read
    as stops on the same line the rest of the page has been following."""
    spans = "".join('<span class="placename">%s</span>' % n for n in names)
    cls = "placeband placeband--route" if route else "placeband"
    return f"""  <div class="{cls}" aria-hidden="true">
    <div class="placeband__names">{spans}</div>
  </div>
"""


def thennow(then_img, now_img, alt_now, depth, hold, back, extra_class="", inner=""):
    """Then/Now — press and hold to reveal the historic plate.
    The control is a real button so keyboard users get the same interaction."""
    return f"""      <div class="thennow {extra_class}">
        <div class="thennow__plate thennow__plate--now">
          <img src="{rel('assets/img/' + now_img, depth)}" alt="{alt_now}" fetchpriority="high" decoding="async">
        </div>
        <div class="thennow__plate thennow__plate--then">
          <img src="{rel('assets/img/' + then_img, depth)}" alt="" decoding="async">
        </div>
        <div class="thennow__sweep" aria-hidden="true"></div>
{inner}        <button class="thennow__hold" type="button" aria-pressed="false"
                data-hold="{hold}" data-back="{back}"><span>{hold}</span></button>
      </div>
"""


def routestrip(depth):
    """Nine numbered slots, drawn as a strip. Only the stops we can evidence
    carry a name; the rest are visibly empty sockets rather than invented
    places. The gap is the point — it shows a visitor (and a venue) that the
    route is a real system with known and unknown positions, not a vague walk.

    Named stops whose number is not yet confirmed cannot be placed on a
    numbered strip, so they are listed underneath instead."""
    placed = {st["n"]: st for st in TRAIL_STOPS if st["n"]}
    unplaced = [st for st in TRAIL_STOPS if not st["n"]]

    pips = ""
    for n in range(1, TRAIL_TOTAL + 1):
        st = placed.get(n)
        if st:
            pips += f"""          <li class="routestrip__stop is-known">
            <span class="routestrip__n">{n}</span>
            <a href="{rel('ryde/' + st['slug'] + '.html', depth)}">{st['title']}</a>
          </li>
"""
        else:
            pips += f"""          <li class="routestrip__stop">
            <span class="routestrip__n">{n}</span>
            <span class="routestrip__tbc" data-public-note>To be confirmed<span class="visually-hidden">, stop {n}</span></span>
          </li>
"""

    names = " &nbsp;·&nbsp; ".join(
        f'<a href="{rel("ryde/" + st["slug"] + ".html", depth)}">{st["title"]}</a>'
        for st in unplaced)
    tail = ""
    if names:
        tail = f"""      <p class="routestrip__note"><b>Named, not yet numbered:</b> {names}. Their positions are confirmed on the ground before they are published as stop numbers.</p>
"""

    return f"""      <div class="routestrip">
        <ol class="routestrip__list" aria-label="The nine stops on the Ryde to Seaview Wartime Trail">
{pips}        </ol>
      </div>
{tail}"""


# accessibility.html promises a written transcript on the same page as every
# film. A film appears on more than one page — the homepage and its collection
# page as well as its own story page — so the promise only holds if the
# transcript travels with the film. Keyed by video slug and emitted by
# video_block itself, it holds by construction rather than by remembering.
# Populated below, once STORIES exists.
VIDEO_TRANSCRIPTS = {}


def transcript_details(video_slug, indent="        "):
    lines = VIDEO_TRANSCRIPTS.get(video_slug) or []
    if not lines:
        return ""
    body = "\n".join(f"{indent}    <p>{line}</p>" for line in lines)
    return (f"""{indent}<details class="transcript">
{indent}  <summary>Read the transcript</summary>
{indent}  <div class="transcript__body">
{body}
{indent}  </div>
{indent}</details>
""")


def video_block(slug, poster, label, note, depth, variant="720"):
    """variant: '720' for grid/summary contexts, '' for the full 1080p file
    on a dedicated story page where the video is the whole point.

    The transcript is part of the film, not part of the page that happens to
    embed it, so it is emitted here on every page the film appears."""
    src = slug + ("-720" if variant == "720" else "") + ".mp4"
    return f"""        <div class="video">
          <video controls preload="none" poster="{rel('assets/img/' + poster, depth)}"
                 width="1920" height="1080" playsinline>
            <source src="{rel('assets/video/' + src, depth)}" type="video/mp4">
            <source src="{rel('assets/video/' + slug + '-720.webm', depth)}" type="video/webm">
            Your browser cannot play this video.
          </video>
          <p class="video__caption"><b>{label}</b><span>{note}</span></p>
        </div>
""" + transcript_details(slug)


PUBLIC_PAGES = []


def write(path, html):
    PUBLIC_PAGES.append(path)
    full = os.path.join(ROOT, path)
    d = os.path.dirname(full)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)


# ============================================================ content

NODES = [
    {"slug": "royal-victoria-arcade", "title": "Royal Victoria Arcade",
     "line": "Stand in Union Street. See the Arcade as Ryde saw it in 1837.",
     "meta": "Ryde 140 · Live", "live": True},
    {"slug": "ryde-town-hall", "title": "Ryde Town Hall",
     "line": "A familiar corner seen across nearly two centuries.",
     "meta": "Ryde 140 · Live", "live": True},
    {"slug": "puckpool-battery", "title": "Puckpool Battery",
     "line": "Stand where the guns watched the Solent.",
     "meta": "Wartime Trail · Live", "live": True},
    {"slug": "appley-tower", "title": "Appley Tower",
     "line": "You've walked past Appley Tower. Now find out what you've been looking at.",
     "meta": "Wartime Trail · Coming soon", "live": False},
    {"slug": "ryde-pier", "title": "Ryde Pier",
     "line": "Walk out half a mile, then look back at the town.",
     "meta": "Wartime Trail · Coming soon", "live": False},
    {"slug": "union-street", "title": "Union Street",
     "line": "You walk it every week. Look up once.",
     "meta": "Ryde 140 · Coming soon", "live": False},
    {"slug": "seaview", "title": "Seaview",
     "line": "The coast keeps going. So does the story.",
     "meta": "Wartime Trail · Coming soon", "live": False},
]

# Canonical stop numbering. The Puckpool film states "Stop 7 of 9", so the
# master system is nine stops. Only the stops we can evidence are named; the
# rest are placeholders until the route is confirmed. Do not invent names —
# the QR codes, films and printed material must all agree with this list.
TRAIL_TOTAL = 9

TRAIL_STOPS = [
    {"n": None, "slug": "ryde-pier", "title": "Ryde Pier",
     "line": "Walk out half a mile, then look back at the town.", "state": "soon"},
    {"n": None, "slug": "appley-tower", "title": "Appley Tower",
     "line": "You've walked past Appley Tower. Now find out what you've been looking at.", "state": "soon"},
    {"n": 7, "slug": "puckpool-battery", "title": "Puckpool Battery",
     "line": "The Sea-Face Guard. Victorian guns stripped away and replaced, in the "
             "crisis of 1940, by fast-firing high-angle anti-aircraft weaponry.",
     "state": "live"},
    {"n": None, "slug": "seaview", "title": "Seaview",
     "line": "The coast keeps going. So does the story.", "state": "soon"},
]

STORIES = {
    "royal-victoria-arcade": {
        "collection": "Ryde 140",
        "collection_href": "ryde-140.html",
        "title": "Royal Victoria Arcade",
        "line": "Stand in Union Street. See the Arcade as Ryde saw it in 1837.",
        "video": "victoria-arcade",
        "poster": "exp-victoria-arcade-hero.jpg",
        "video_label": "Evidence-led AI reconstruction · c.1837",
        "video_note": "20 seconds · sound on",
        "story": [
            "The Royal Victoria Arcade opened on 1 July 1836, named for Princess Victoria — before she became Queen. Ryde was already building in her name.",
            "The front you walk past today is not the front that opened. The arcade originally had three grand entrance arches. In 1856 they were replaced by the broad entrance we recognise now.",
            "The reconstruction in the film shows the c.1837 frontage, built from a contemporary 1837 engraving together with surviving building materials, brick sources and architectural details. It is an interpretation, and it is labelled as one on screen.",
        ],
        "visit": [
            ("Where", "Union Street, Ryde"),
            ("Getting there", "Central Ryde, a few minutes' walk up from the Esplanade."),
            ("Opening", "Check the arcade's own opening hours before travelling."),
            ("Accessibility", "Step-free entrance from Union Street."),
            ("Time needed", "10 minutes to watch and look; longer if you go in."),
        ],
        "sources": [
            ("Contemporary 1837 engraving", "Primary visual source for the original frontage."),
            ("Surviving building materials", "Brick sources and architectural details recorded on site."),
            ("Documented 1856 alteration", "The record of the entrance change."),
        ],
        "next": ["puckpool-battery", "union-street"],
        "transcript": [
            "Before Victoria became Queen… Ryde was already building in her name.",
            "Opened in 1836 and named for Princess Victoria,",
            "Ryde's Royal Victoria Arcade originally had three grand entrance arches.",
            "In 1856, they were replaced by the broad entrance we recognise today.",
            "Evidence-led interpretation of the Royal Victoria Arcade, c.1837 — based on a "
            "contemporary 1837 engraving and surviving building materials, brick sources "
            "and architectural details.",
        ],
        "nearby": None,
        "marks": ("recon", "archive", "source"),
    },
    "puckpool-battery": {
        "collection": "Wartime Trail",
        "collection_href": "wartime-trail.html",
        "title": "Puckpool Battery",
        "line": "Stand where the guns watched the Solent.",
        "video": "puckpool-battery",
        "poster": "exp-puckpool-hero.jpg",
        "video_label": "The Sea-Face Guard · Puckpool Point",
        "video_note": "22 seconds · sound on",
        "story": [
            "Puckpool was built to hold the sea face — to cover the approach to Spithead from a low point on the shore.",
            "The 1892 Armstrong protected barbettes mounted here were the only examples of their kind ever deployed in Great Britain.",
            "Then the threat changed. The massive, slow-firing Victorian guns that once guarded Spithead were stripped away, replaced in the crisis of 1940 by fast-firing, high-angle anti-aircraft weaponry — and the crews stopped watching the water and started scanning the skies for the Luftwaffe.",
        ],
        "visit": [
            ("Where", "Puckpool Point, between Ryde and Seaview"),
            ("Getting there", "On the coastal path from Appley. Parking at Puckpool Park."),
            ("Opening", "Open park land. Daylight recommended."),
            ("Accessibility", "Surfaced coastal path; the battery earthworks are uneven."),
            ("Time needed", "20 minutes here; about two hours for the full walk from Ryde."),
        ],
        "sources": [
            ("Armstrong barbette records", "1892 emplacement type and deployment."),
            ("Wartime defence records", "The 1940 conversion to anti-aircraft weaponry."),
            ("Site survey", "Photography and measurements taken on site."),
        ],
        "next": ["royal-victoria-arcade", "appley-tower"],
        "transcript": [
            "As technology advanced, the old fortress adapted.",
            "The massive, slow-firing Victorian guns that once guarded Spithead were stripped away…",
            "…replaced in the crisis of 1940 by fast-firing, high-angle anti-aircraft weaponry…",
            "…to scan the skies for the Luftwaffe.",
            "Did you know: the 1892 Armstrong protected barbettes mounted here were the only "
            "examples of their kind ever deployed in Great Britain.",
        ],
        # Story → nearby business. This is the commercial behaviour to measure.
        # UNCONFIRMED: The Dell Cafe appears as "local retail partner" on the film's
        # end card. Remove this block if the agreement is not in place.
        "marks": ("spot", "archive", "source"),
        "nearby": {
            "kind": "Café",
            "name": "The Dell Cafe",
            "line": "Continue your walk with food and refreshments nearby.",
        },
    },
    "ryde-town-hall": {
        "collection": "Ryde 140",
        "collection_href": "ryde-140.html",
        "title": "Ryde Town Hall: Past, Present and Future",
        "line": "A familiar corner seen across nearly two centuries.",
        "video": "town-hall",
        "poster": "card-town-hall.jpg",
        "video_label": "Ryde Town Hall",
        "video_note": "Evidence-led AI reconstruction & concept visualisation",
        "story": [
            "Follow Ryde Town Hall from its opening in 1831, through civic expansion, celebration and community life, into closure — and a future that has not yet been written.",
            "Opening in 1831 with its grand neoclassical columned frontage on Lind Street, Ryde Town Hall served as the civic beating heart of the town for generations.",
            "In 1867–69, the hall expanded with an imposing clock tower and municipal chambers. By 1887, it stood at the centre of Queen Victoria's Golden Jubilee festivities.",
            "Through decades of dances, concerts and public meetings, the hall was where Ryde gathered. Following closure in the early 21st century, the building fell quiet.",
            "Today, community initiatives and imaginative stewardship are asking what this familiar corner could become. The future visualised here is a conceptual interpretation to spark local conversation.",
        ],
        "visit": [
            ("Where", "Lind Street, Ryde"),
            ("Getting there", "Central Ryde, opposite Lind Street car park and moments from Union Street."),
            ("Viewing", "Exterior visible from Lind Street and Victoria Street. Interior closed."),
            ("Accessibility", "Paved level town-centre pavements surrounding the site."),
            ("Time needed", "10 minutes to take in the architecture, film and historic timeline."),
        ],
        "sources": [
            ("Civic Architectural Records 1831–1869", "Architectural plans and municipal committee records for the original hall and Victorian expansion."),
            ("Ryde Jubilee & Civic Archive (1887)", "Photographs and press accounts of civic gatherings and celebrations."),
            ("Contemporary Site Survey & Photography", "Current photographic record of Lind Street, facade condition and architectural masonry."),
            ("Concept Visualisation Note", "Future gathering scene is an evidence-led concept visualisation to encourage discussion; no approved planning scheme is implied."),
        ],
        "next": ["royal-victoria-arcade", "puckpool-battery"],
        "transcript": [
            "A familiar corner seen across nearly two centuries.",
            "Ryde Town Hall opened in 1831, created to give the expanding seaside resort a proud civic identity.",
            "In the late 1860s, the hall was enlarged, crowned by its landmark clock tower.",
            "By 1887, Ryde celebrated the Queen's Golden Jubilee under these neoclassical columns.",
            "For over a century, music, dances, debates and town meetings filled its rooms.",
            "In recent decades, the doors closed, and the building waited.",
            "Today, we look back through evidence and photographs — and ask what this corner might become for the next generation.",
            "Visualisation of future civic gathering is an evidence-led conceptual interpretation; no approved scheme implied.",
        ],
        "nearby": None,
        "marks": ("recon", "archive", "source"),
    },
}

# The transcript belongs to the film, keyed by video slug, so video_block can
# emit it on every page the film appears — not only its own story page.
VIDEO_TRANSCRIPTS.update({
    s["video"]: (s.get("transcript") or [])
    for s in STORIES.values() if s.get("video")
})

SOON = {
    "appley-tower": ("Wartime Trail", "wartime-trail.html", "Appley Tower",
                     "You've walked past Appley Tower. Now find out what you've been looking at."),
    "ryde-pier": ("Wartime Trail", "wartime-trail.html", "Ryde Pier",
                  "Walk out half a mile, then look back at the town."),
    "union-street": ("Ryde 140", "ryde-140.html", "Union Street",
                     "You walk it every week. Look up once."),
    "seaview": ("Wartime Trail", "wartime-trail.html", "Seaview",
                "The coast keeps going. So does the story."),
}


def node_card(n, depth):
    cls = "node" if n["live"] else "node node--soon"
    if n["live"]:
        title = f'<a href="{rel("ryde/" + n["slug"] + ".html", depth)}">{n["title"]}</a>'
    else:
        title = f'<a href="{rel("ryde/" + n["slug"] + ".html", depth)}">{n["title"]}</a>'
    return f"""        <article class="{cls}">
          <h3>{title}</h3>
          <p>{n['line']}</p>
          <p class="node__meta">{n['meta']}</p>
        </article>
"""


# ============================================================ pages

def build_index():
    d = 0
    html = head("IsleConnect — Bring Ryde to life",
                "Explore the stories, places and people that shaped Ryde — and discover where to go next.", d,
                page="home")
    html += header("", d, over=True)

    nodes = "".join(node_card(n, d) for n in NODES)

    html += f"""
  <!-- ============ 1 · HERO — then/now, the signature interaction ============ -->
  <section class="hero">
    <div class="hero__media">
{thennow('arcade-then.jpg', 'arcade-now.jpg',
         'The Royal Victoria Arcade on Union Street, Ryde, today',
         d, 'Hold to see 1837', 'Release for today')}    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <div class="hero__content">
          <h1>Bring Ryde to life.</h1>
          <p class="hero__sub">Explore the stories, places and people that shaped Ryde — then discover where to go next.</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="explore.html">Explore the stories</a>
            <a class="btn btn--ghost-light" href="for-partners.html">Work with us</a>
          </div>
          {marks('recon', 'source')}
        </div>
      </div>
    </div>
  </section>

  <!-- ============ 1b · NEW STORY FEATURE — RYDE TOWN HALL ============ -->
  <section class="band band--ivory" style="padding-top:var(--space-xl); padding-bottom:var(--space-md)">
    <div class="wrap">
      <div class="feature-spotlight">
        <div class="feature-spotlight__media">
          <div class="video-poster-card">
            <img src="assets/img/card-town-hall.jpg" alt="Ryde Town Hall past, present and future" width="1600" height="900" loading="lazy">
            <a href="ryde/ryde-town-hall.html#watch" class="video-poster-card__play" aria-label="Watch the 50-second Ryde Town Hall film" data-ic-event="townhall_play">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
            </a>
          </div>
        </div>
        <div class="feature-spotlight__body">
          <span class="eyebrow">New from Ryde 140</span>
          <h2>Ryde Town Hall: Past, Present and Future</h2>
          <p class="lede">A familiar corner seen across nearly two centuries.</p>
          <p>Follow Ryde Town Hall from its opening in 1831, through civic expansion, celebration and community life, into closure — and a future that has not yet been written.</p>
          <p class="townhall-feature__provenance"><small>The film combines a present-day photographic record with clearly labelled AI-assisted historical interpretation and a future concept visualisation.</small></p>
          <div class="btn-row">
            <a class="btn btn--primary" href="ryde/ryde-town-hall.html#watch" data-ic-event="townhall_play">Watch the 50-second film</a>
            <a class="btn btn--ghost-dark" href="ryde/ryde-town-hall.html">Explore the story and sources</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ 2 · TWO FLAGSHIP EXPERIENCES ============ -->
  <section class="band band--ivory" aria-labelledby="flagship-h">
    <div class="wrap">
{thread('a')}      <div class="band__head">
        <span class="eyebrow">See it working</span>
        <h2 id="flagship-h">Two ways to discover Ryde</h2>
      </div>

      <div class="features">

        <article class="feature">
{video_block('victoria-arcade', 'card-ryde140.jpg', 'Royal Victoria Arcade', 'Evidence-led AI reconstruction · c.1837', d)}          <div class="feature__body">
            <span class="eyebrow">Ryde 140</span>
            <h3>See the town differently.</h3>
            <p class="feature__lead">Step back into Ryde's past through evidence-led reconstructions, archive stories and the people who shaped the town.</p>
            <p class="feature__stops">Royal Victoria Arcade · Union Street · seafront · people · buildings · forgotten stories</p>
            <div class="btn-row">
              <a class="btn btn--primary" href="ryde-140.html">Explore Ryde 140</a>
            </div>
          </div>
        </article>

        <article class="feature">
{video_block('puckpool-battery', 'card-wartime.jpg', 'Puckpool Battery', 'The Sea-Face Guard · Stop 7', d)}          <div class="feature__body">
            <span class="eyebrow">Ryde to Seaview</span>
            <h3>Follow the coast through wartime.</h3>
            <p class="feature__lead">Walk from Ryde towards Seaview and discover how this familiar coastline became part of Britain's wartime defences.</p>
            <p class="feature__stops">Ryde Pier → Appley → Puckpool → Seaview</p>
            <div class="btn-row">
              <a class="btn btn--primary" href="wartime-trail.html">Explore the wartime trail</a>
            </div>
          </div>
        </article>

      </div>
    </div>
  </section>

  <div class="wrap">
{thread('b')}  </div>

  <!-- ============ 3 · HOW IT WORKS ============ -->
  <section class="band band--navy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="band__head band__head--centre">
        <span class="eyebrow">How IsleConnect works</span>
        <h2 id="how-h">Discover. Experience. Go.</h2>
        <p class="assure"><b>No app to download.</b> Scan a code or open a link — it runs in the browser you already have.</p>
      </div>
      <div class="grid grid--3 steps">
        <div class="step"><span class="step__num" aria-hidden="true">1</span><h3>Discover</h3><p>Find a story connected to where you are.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">2</span><h3>Experience</h3><p>Watch, listen or explore the story on your phone.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">3</span><h3>Go</h3><p>Find the next story, place to visit, or somewhere local to stop.</p></div>
      </div>
      <p class="band__close">The digital experience is there to help you discover more of the real place.</p>
{thread('c')}    </div>
  </section>

  <!-- ============ 4 · EXPLORE RYDE — editorial grid, not a card row ============ -->
  <section class="band band--ivory" aria-labelledby="nodes-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Explore Ryde</span>
        <h2 id="nodes-h">A growing network of stories</h2>
        <p class="lede">{LIVE_COUNT_WORD} live. The rest are being built with the people who know them.</p>
      </div>

      <div class="stories">

        <article class="story story--lead">
          <div class="story__media">
            <img src="assets/img/card-ryde140.jpg" width="1600" height="900" loading="lazy" decoding="async"
                 alt="The Royal Victoria Arcade as reconstructed for c.1837">
          </div>
          <span class="card__cat">Ryde 140</span>
          <h3><a href="ryde/royal-victoria-arcade.html">Royal Victoria Arcade</a></h3>
          <p>Stand in Union Street. See the Arcade as Ryde saw it in 1837.</p>
          {marks('recon', 'archive')}
        </article>

        <article class="story story--sub">
          <div class="story__media">
            <img src="assets/img/card-town-hall.jpg" width="1600" height="900" loading="lazy" decoding="async"
                 alt="Ryde Town Hall past, present and future">
          </div>
          <span class="card__cat">Ryde 140</span>
          <h3><a href="ryde/ryde-town-hall.html">Ryde Town Hall</a></h3>
          <p>A familiar corner seen across nearly two centuries.</p>
          {marks('recon', 'archive')}
        </article>

        <article class="story story--sub">
          <div class="story__media">
            <img src="assets/img/card-wartime.jpg" width="1600" height="900" loading="lazy" decoding="async"
                 alt="An anti-aircraft crew at Puckpool Battery">
          </div>
          <span class="card__cat">Wartime Trail · Stop 7</span>
          <h3><a href="ryde/puckpool-battery.html">Puckpool Battery</a></h3>
          <p>Stand where the guns watched the Solent.</p>
          {marks('spot', 'source')}
        </article>

        <article class="story story--frag">
          <p class="story__state">In development</p>
          <h3><a href="ryde/appley-tower.html">Appley Tower</a></h3>
          <p>You've walked past Appley Tower. Now find out what you've been looking at.</p>
        </article>

        <article class="story story--frag">
          <p class="story__state">In development</p>
          <h3><a href="ryde/ryde-pier.html">Ryde Pier</a></h3>
          <p>Walk out half a mile, then look back at the town.</p>
        </article>

        <article class="story story--frag">
          <p class="story__state">In development</p>
          <h3><a href="ryde/union-street.html">Union Street</a></h3>
          <p>You walk it every week. Look up once.</p>
        </article>

        <article class="story story--frag">
          <p class="story__state">In development</p>
          <h3><a href="ryde/seaview.html">Seaview</a></h3>
          <p>The coast keeps going. So does the story.</p>
        </article>

      </div>

      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--ghost-dark" href="explore.html">See all stories</a>
      </div>
{thread('d')}    </div>
  </section>

{placeband('Ryde', 'Appley', 'Puckpool', 'Seaview', route=True)}
  <!-- ============ 5 · THE TWO COLLECTIONS ============ -->
  <section class="band band--ivory-deep" aria-labelledby="coll-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Collections</span>
        <h2 id="coll-h">Stories that belong together</h2>
        <p class="lede">One story makes you stop. A trail gives you somewhere to go next.</p>
      </div>
{thread('e')}
      <div class="grid grid--2">
        <div class="audience">
          <span class="eyebrow">Ryde 140</span>
          <h3>A town explored across the centuries</h3>
          <p>A growing collection exploring Ryde's buildings, people and stories across the centuries.</p>
          <a class="link-arrow" href="ryde-140.html" data-ic-event="trail_selected" data-ic-trail="ryde-140">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <span class="eyebrow">Ryde to Seaview</span>
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.</p>
          <a class="link-arrow" href="wartime-trail.html" data-ic-event="trail_selected" data-ic-trail="wartime-trail">Follow the route</a>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ BRIDGE · WHAT COULD ISLECONNECT HELP YOU CHANGE? ============ -->
  <section class="band band--navy" aria-labelledby="change-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Consultancy &amp; Pilots</span>
        <h2 id="change-h">What could IsleConnect help you change?</h2>
        <p class="lede">Some organisations already have a story. Others have a visibility, visitor or engagement problem and are unsure where to begin.</p>
      </div>
      <div class="grid grid--2" style="margin-bottom:var(--space-lg); gap:var(--space-lg)">
        <div>
          <p>IsleConnect provides focused consultancy and small, measurable pilots for:</p>
          <ul class="ticks ticks--on-dark">
            <li><b>Independent businesses</b> seeking more discovery and customer action</li>
            <li><b>Attractions</b> wanting a stronger before, during and after-visit experience</li>
            <li><b>Community organisations</b> holding stories, archives or local knowledge</li>
            <li><b>Places</b> looking to connect several venues into one useful journey</li>
          </ul>
        </div>
        <div class="bridge-card">
          <h3 style="color:var(--ivory)">Start small and measurable</h3>
          <p style="color:var(--ink-on-dark-muted)">You do not need to commission a complete platform. Start with one location, one customer problem or one story worth testing.</p>
          <div class="btn-row" style="margin-top:var(--space-md)">
            <a class="btn btn--primary" href="consultancy.html" data-ic-event="consultancy_view">Explore consultancy and pilots</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ 6 · FOR LOCAL VENUES AND BUSINESSES ============ -->
  <section class="band band--ivory" aria-labelledby="partners-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">For local venues and businesses</span>
        <h2 id="partners-h">Be part of the journey.</h2>
        <p class="lede">IsleConnect helps visitors discover the story around them — and gives nearby businesses and attractions a natural place in that journey.</p>
      </div>
      <div class="grid grid--3">
        <div class="benefit">
          <h3>Be discovered</h3>
          <p>Appear when someone is already exploring nearby.</p>
        </div>
        <div class="benefit">
          <h3>Tell your story</h3>
          <p>Show people what makes your venue or place worth stopping for.</p>
        </div>
        <div class="benefit">
          <h3>See what happens next</h3>
          <p>Understand whether visitors continue, explore or take an action.</p>
        </div>
      </div>
      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--primary" href="for-partners.html">Work with us</a>
      </div>
    </div>
  </section>

  <!-- ============ 7 · TRUST ============ -->
  <section class="band band--ivory" style="padding-top:0">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <!-- ============ 8 · BEYOND RYDE — the quietest band on the page ============ -->
  <section class="band band--ivory-deep beyond-band" aria-labelledby="beyond-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">What's coming next</span>
        <h2 id="beyond-h">Beyond Ryde</h2>
        <p class="lede">The same approach can bring books, attractions and other destinations to life.</p>
      </div>
      <ol class="beyond-list">
        <li>
          <h3>Books &amp; authors</h3>
          <p>Connect stories with the places that inspired them.</p>
        </li>
        <li>
          <h3>Attractions</h3>
          <p>Help visitors discover more before, during and after a visit.</p>
        </li>
        <li>
          <h3>Other towns &amp; destinations</h3>
          <p>Use verified local stories to create connected journeys.</p>
        </li>
      </ol>

      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--ghost-dark" href="contact.html">Interested in working with us?</a>
      </div>
    </div>
  </section>

  <!-- ============ CLOSE ============ -->
  <section class="closer">
    <div class="closer__media" aria-hidden="true">
      <img src="assets/img/card-explore-ryde.jpg" width="1600" height="504" alt="" loading="lazy" decoding="async">
    </div>
    <div class="closer__inner">
      <div class="wrap">
        <h2>Start with one story.</h2>
        <p>Ryde is where we are proving the model. The same approach can later bring books, attractions and destinations to life.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="explore.html">Explore the stories</a>
          <a class="btn btn--ghost-light" href="for-partners.html">Become a Ryde partner</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("index.html", html)


def build_explore():
    d = 0
    nodes = "".join(node_card(n, d) for n in NODES)
    html = head("Explore Ryde — IsleConnect",
                "Stories, places and people across Ryde and the coast to Seaview.", d,
                page="explore")
    html += header("explore.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Explore Ryde</span>
        <h1>Stories connected to real places</h1>
        <p class="lede">Every story starts where it happened and points you at the next one. Two are live now; the rest are being built with the people who know them.</p>
      </div>
      <div class="nodes">
{nodes}      </div>
    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Collections</span>
        <h2>Or follow a whole collection</h2>
      </div>
      <div class="grid grid--2">
        <div class="audience">
          <h3>Ryde 140</h3>
          <p>A growing collection exploring Ryde's buildings, people and stories across the centuries.</p>
          <a class="link-arrow" href="ryde-140.html" data-ic-event="trail_selected" data-ic-trail="ryde-140">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.</p>
          <a class="link-arrow" href="wartime-trail.html" data-ic-event="trail_selected" data-ic-trail="wartime-trail">Follow the route</a>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--navy">
    <div class="wrap">
      <div class="band__head band__head--centre">
        <span class="eyebrow">How IsleConnect works</span>
        <h2>Discover. Experience. Go.</h2>
        <p class="assure"><b>No app to download.</b> Scan a code or open a link — it runs in the browser you already have.</p>
      </div>
      <div class="grid grid--3 steps">
        <div class="step"><span class="step__num" aria-hidden="true">1</span><h3>Discover</h3><p>Find a story connected to where you are.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">2</span><h3>Experience</h3><p>Watch, listen or explore the story on your phone.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">3</span><h3>Go</h3><p>Find the next story, place to visit, or somewhere local to stop.</p></div>
      </div>
      <p class="band__close">The digital experience is there to help you discover more of the real place.</p>
    </div>
  </section>
"""
    html += footer(d)
    write("explore.html", html)


def build_ryde140():
    d = 0
    items = [n for n in NODES if n["meta"].startswith("Ryde 140")]
    cards = "".join(node_card(n, d) for n in items)
    html = head("Ryde 140 — IsleConnect",
                "A growing collection exploring Ryde's buildings, people and stories across the centuries.", d,
                page="collection", trail="ryde-140")
    html += header("journeys.html", d, over=True)
    html += f"""
  <section class="hero hero--short">
    <div class="hero__media" aria-hidden="true">
      <img src="assets/img/card-ryde140.jpg" width="1600" height="900" alt="" fetchpriority="high" decoding="async">
    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <div class="hero__content">
          <span class="eyebrow">Collection</span>
          <h1>Ryde 140</h1>
          <p class="hero__sub">See the town differently.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <p class="lede">A growing collection exploring Ryde's buildings, people and stories across the centuries.</p>
      </div>
      <div class="measure">
        <p>Ryde is full of frontages that are not the frontages people first walked past, streets that changed use twice over, and businesses whose history is longer than their sign suggests. Ryde 140 collects those stories and puts them back where they happened.</p>
        <p>Each one is built from a documented source, checked by someone who knows the subject, and clearly labelled where an image is an interpretation rather than a record.</p>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Watch</span>
        <h2>Royal Victoria Arcade</h2>
        <p class="lede">Ryde's Royal Victoria Arcade opened on 1 July 1836, named for Princess Victoria. The entrance you walk past today is not the one that opened.</p>
      </div>
{video_block('victoria-arcade', 'card-ryde140.jpg', 'Royal Victoria Arcade', 'Evidence-led AI reconstruction · c.1837', d)}      <div class="btn-row" style="margin-top:var(--space-md)">
        <a class="btn btn--primary" href="ryde/royal-victoria-arcade.html">Open the full story</a>
      </div>
    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">In this collection</span>
        <h2>Stories so far</h2>
      </div>
      <div class="nodes">
{cards}      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Know a Ryde story worth telling?</h2>
        <p>We work with venues, businesses, historians and local organisations to put stories back where they happened.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="contact.html">Start a conversation</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("ryde-140.html", html)


def build_wartime():
    d = 0
    stops = ""
    for st in TRAIL_STOPS:
        num = f"Stop {st['n']} of {TRAIL_TOTAL}" if st["n"] else "Stop number to be confirmed"
        state = ("" if st["state"] == "live"
                 else '<span class="route__soon">Story in development</span>')
        marker = st["n"] if st["n"] else "?"
        stops += f"""        <li data-stop="{marker}">
          <p class="node__meta" style="padding-top:0">{num}</p>
          <h3><a href="ryde/{st['slug']}.html">{st['title']}</a></h3>
          <p>{st['line']}</p>
          {state}
        </li>
"""
    html = head("Ryde to Seaview Wartime Trail — IsleConnect",
                "A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.", d,
                page="collection", trail="wartime-trail")
    html += header("journeys.html", d, over=True)
    html += f"""
  <section class="hero hero--short">
    <div class="hero__media" aria-hidden="true">
      <img src="assets/img/card-wartime.jpg" width="1600" height="900" alt="" fetchpriority="high" decoding="async">
    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <div class="hero__content">
          <span class="eyebrow">Collection</span>
          <h1>Ryde to Seaview Wartime Trail</h1>
          <p class="hero__sub">Follow the coast through wartime.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <p class="lede">A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.</p>
      </div>
      <div class="measure">
        <p>Walk from Ryde towards Seaview and the coastline stops being scenery. The pier, the tower, the earthworks at Puckpool — each was part of a defensive line that changed shape as the threat changed.</p>
      </div>
      <ul class="facts" style="margin-top:var(--space-lg)">
        <li><span class="facts__k">Route</span><span class="facts__v">Ryde Pier → Appley → Puckpool → Seaview</span></li>
        <li><span class="facts__k">Stops</span><span class="facts__v">Nine along the route</span></li>
        <li><span class="facts__k">Distance</span><span class="facts__v">About 3 miles along the coast</span></li>
        <li><span class="facts__k">Time</span><span class="facts__v">Around two hours at a walking pace, longer if you stop</span></li>
        <li><span class="facts__k">Terrain</span><span class="facts__v">Surfaced coastal path for most of the route; some uneven ground at the battery</span></li>
        <li><span class="facts__k">Best time</span><span class="facts__v">Daylight, any season. Exposed in a westerly.</span></li>
      </ul>
      <p class="notice notice--public" style="margin-top:var(--space-lg)"><b>This trail is still being built.</b> One stop is finished and published. The rest are in research, and the walking figures above are our best estimate until the full route is walked and timed. We would rather tell you that than publish a number we cannot stand behind.</p>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Watch</span>
        <h2>Puckpool Battery — The Sea-Face Guard</h2>
        <p class="lede">The 1892 Armstrong protected barbettes mounted here were the only examples of their kind ever deployed in Great Britain.</p>
      </div>
{video_block('puckpool-battery', 'card-wartime.jpg', 'Puckpool Battery', 'The Sea-Face Guard · Stop 7', d)}      <div class="btn-row" style="margin-top:var(--space-md)">
        <a class="btn btn--primary" href="ryde/puckpool-battery.html">Open the full story</a>
      </div>
    </div>
  </section>

{placeband('Ryde', 'Appley', 'Puckpool', 'Seaview')}
  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">The route</span>
        <h2>Stops along the way</h2>
        <p class="lede">Nine stops from Ryde to Seaview. Four are named so far.</p>
      </div>
{routestrip(d)}{thread()}      <ol class="route">
{stops}      </ol>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Run a venue on this route?</h2>
        <p>Walkers pass your door already. IsleConnect gives them a reason to stop.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="partners/venues.html" data-ic-event="sponsor_enquiry">Become a partner</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("wartime-trail.html", html)


def build_story(slug):
    d = 1
    s = STORIES[slug]
    story = "\n".join(f"        <p>{p}</p>" for p in s["story"])
    visit = "\n".join(
        f'        <li><span class="facts__k">{k}</span><span class="facts__v">{v}</span></li>'
        for k, v in s["visit"])
    sources = "\n".join(f'        <li><b>{n}</b> — {t}</li>' for n, t in s["sources"])

    nxt = ""
    for ns in s["next"]:
        if ns in STORIES:
            t, l = STORIES[ns]["title"], STORIES[ns]["line"]
            coll = STORIES[ns]["collection"]
            meta = f"{coll} · Live"
        else:
            coll, _, t, l = SOON[ns]
            meta = f"{coll} · Coming soon"
        nxt += f"""        <article class="node">
          <h3><a href="{ns}.html">{t}</a></h3>
          <p>{l}</p>
          <p class="node__meta">{meta}</p>
        </article>
"""

    stop_no = next((st["n"] for st in TRAIL_STOPS if st["slug"] == slug and st["n"]), None)
    html = head(f'{s["title"]} — IsleConnect', s["line"], d,
                page="story", story=slug,
                trail=s["collection_href"].replace(".html", ""),
                stop=stop_no)
    html += header("journeys.html", d, over=True)
    # The transcript is emitted by video_block itself, so it travels with the
    # film to every page that embeds it. Nothing to add here.

    # A partner block exists only when a partner record is approved for
    # inclusion and carries a real directions URL. An unapproved partner is
    # not a warning on the page — the block simply is not built.
    nearby_block = ""
    pt = partner_for(page_slug_for(slug))
    if pt:
        nearby_block = f"""    <section class="exp-section">
      <span class="eyebrow">Nearby</span>
      <h2>While you are here</h2>
      <div class="nearby">
        <div>
          <span class="nearby__kind">{pt['kind']}</span>
          <h3>{pt['publicName']}</h3>
          <p>{pt['copy']['line']}</p>
        </div>
        <a class="btn btn--ghost-dark" href="{pt['location']['directionsUrl']}" rel="noopener" data-ic-event="directions_clicked">Get directions</a>
      </div>
    </section>

"""

    extra_townhall_block = ""
    if slug == "ryde-town-hall":
        extra_townhall_block = f"""    <section class="exp-section">
      <span class="eyebrow">Timeline</span>
      <h2>Nearly two centuries at a glance</h2>
      <div class="timeline">
        <div class="timeline__beat">
          <div class="timeline__year">1831</div>
          <div class="timeline__desc">Ryde Town Hall opens with its grand neoclassical columned frontage on Lind Street, establishing a proud civic identity.</div>
        </div>
        <div class="timeline__beat">
          <div class="timeline__year">1867–69</div>
          <div class="timeline__desc">Municipal expansion adds an imposing clock tower and council chambers as Ryde flourishes as a seaside borough.</div>
        </div>
        <div class="timeline__beat">
          <div class="timeline__year">1887</div>
          <div class="timeline__desc">Civic celebrations for Queen Victoria's Golden Jubilee centre on the Town Hall with community processions and illuminations.</div>
        </div>
        <div class="timeline__beat">
          <div class="timeline__year">Entertainment Era</div>
          <div class="timeline__desc">Decades of dances, concerts, theatrical performances and town meetings establish the hall as Ryde's social beating heart.</div>
        </div>
        <div class="timeline__beat">
          <div class="timeline__year">Closure</div>
          <div class="timeline__desc">Municipal reorganization and rising maintenance costs lead to the hall's closure in the early 21st century. The doors fall quiet.</div>
        </div>
        <div class="timeline__beat">
          <div class="timeline__year">Future Possibility</div>
          <div class="timeline__desc">Community proposals and imaginative stewardship explore new life for the hall as a vibrant cultural and civic space.</div>
        </div>
      </div>
      <p class="notice notice--public" style="margin-top:var(--space-md)">
        <b>FUTURE CONCEPT VISUALISATION — NO APPROVED SCHEME IMPLIED.</b> The gathering depicted in the film's closing sequence is an evidence-led conceptual interpretation designed to stimulate community discussion. It does not represent an approved architectural or planning scheme.
      </p>
    </section>

    <section class="exp-section">
      <span class="eyebrow">Community</span>
      <h2>What could this corner become?</h2>
      <div class="nearby">
        <div>
          <span class="nearby__kind">Have your say</span>
          <h3>A place for community conversation</h3>
          <p>Ryde Town Hall belongs to the town's history and its future. If you have memories, historical photographs, or ideas about how this landmark can serve the community again, we want to hear from you.</p>
        </div>
        <a class="btn btn--primary" href="{rel('contact.html', d)}">Share your thoughts</a>
      </div>
      <div class="nearby" style="margin-top:var(--space-md)">
        <div>
          <span class="nearby__kind">Case Study</span>
          <h3>How this project was created</h3>
          <p>See how IsleConnect combined archival records, on-site photography, and evidence-led visualisation to turn a quiet building into an active community conversation.</p>
        </div>
        <a class="btn btn--ghost-dark" href="{rel('consultancy.html#town-hall-case-study', d)}">Read the case study</a>
      </div>
    </section>
"""

    sources_block = f"""    <section class="exp-section">
      <details class="source-notes" open>
        <summary><h2 style="display:inline;font-size:inherit;margin:0">Sources and interpretation notes</h2></summary>
        <div style="margin-top:var(--space-md)">
          <ul class="sources">
{sources}
          </ul>
        </div>
      </details>
    </section>""" if slug == "ryde-town-hall" else f"""    <section class="exp-section">
      <span class="eyebrow">Sources</span>
      <h2>Where this comes from</h2>
      <ul class="sources">
{sources}
      </ul>
    </section>"""

    html += f"""
  <section class="hero hero--short">
    <div class="hero__media" aria-hidden="true">
      <img src="{rel('assets/img/' + s['poster'], d)}" width="1920" height="1080" alt="" fetchpriority="high" decoding="async">
    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <p class="crumb"><a href="{rel('explore.html', d)}">Explore Ryde</a> &nbsp;/&nbsp; <a href="{rel(s['collection_href'], d)}">{s['collection']}</a></p>
        <div class="hero__content">
          <h1>{s['title']}</h1>
          <p class="hero__sub">{s['line']}</p>
          {marks(*s.get('marks', ('source',)))}
        </div>
      </div>
    </div>
  </section>

  <div class="wrap">

    <section class="exp-section" id="watch">
      <h2 class="visually-hidden">The experience</h2>
{video_block(s['video'], s['poster'], s['video_label'], s['video_note'], d, variant='')}    </section>

    <section class="exp-section" id="story">
      <span class="eyebrow">The story</span>
      <h2>What happened here</h2>
      <div class="measure">
{story}
      </div>
    </section>

{extra_townhall_block}    <section class="exp-section">
      <span class="eyebrow">Visit</span>
      <h2>Practical details</h2>
      <ul class="facts">
{visit}
      </ul>
    </section>

{nearby_block}    <section class="exp-section onward">
      <span class="eyebrow">Go somewhere next</span>
      <p class="onward__lead">You are standing in it. <em>Now walk to the next one.</em></p>
{thread()}      <div class="nodes">
{nxt}      </div>
    </section>

{sources_block}
  </div>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Be part of the journey.</h2>
        <p>IsleConnect helps visitors discover the story around them — and gives nearby businesses and attractions a natural place in that journey.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="{rel('for-partners.html', d)}">Become a Ryde partner</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"ryde/{slug}.html", html)


def build_soon(slug):
    d = 1
    coll, coll_href, title, line = SOON[slug]
    html = head(f"{title} — IsleConnect", line, d,
                page="story-in-development", story=slug,
                trail=coll_href.replace(".html", ""))
    html += header("journeys.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <p class="crumb" style="color:var(--ink-muted)"><a href="{rel('explore.html', d)}" style="color:var(--ink-muted)">Explore Ryde</a> &nbsp;/&nbsp; <a href="{rel(coll_href, d)}" style="color:var(--ink-muted)">{coll}</a></p>
      <div class="band__head">
        <span class="eyebrow">Coming soon</span>
        <h1>{title}</h1>
        <p class="lede">{line}</p>
      </div>
      <div class="measure">
        <p>This story is being built with the people who know it. We publish nothing until the sources are checked and a person has signed it off.</p>
      </div>

      <div class="nearby" style="margin-top:var(--space-xl)">
        <div>
          <span class="nearby__kind">Help us build it</span>
          <h3>Do you have photographs, memories or records connected with {title}?</h3>
          <p>Local knowledge is where every one of these stories starts. If you hold something — a photograph, a document, or a memory worth recording — we would like to hear from you.</p>
        </div>
        <a class="btn btn--primary" href="{rel('contact.html', d)}">Get in touch</a>
      </div>

      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--ghost-dark" href="{rel(coll_href, d)}">Back to {coll}</a>
        <a class="btn btn--ghost-dark" href="{rel('explore.html', d)}">See what's live</a>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"ryde/{slug}.html", html)


def build_journeys():
    d = 0
    html = head("Journeys — IsleConnect",
                "Curated routes and collections across Ryde and the coast to Seaview.", d)
    html += header("journeys.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Journeys</span>
        <h1>Stories that belong together</h1>
        <p class="lede">A single story is worth ten minutes. A journey is worth an afternoon. These are the routes and collections we are building.</p>
      </div>
{thread()}
      <div class="grid grid--2">
        <div class="audience">
          <span class="eyebrow">Collection</span>
          <h3>Ryde through time</h3>
          <p>A growing collection exploring Ryde's buildings, people and stories across the centuries. Published under the programme name <b>Ryde 140</b>.</p>
          <a class="link-arrow" href="ryde-140.html">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <span class="eyebrow">Route</span>
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided walk along the coast, through the places that defended, supplied and lived through the Island's wartime years. One stop published; the route is still being built.</p>
          <a class="link-arrow" href="wartime-trail.html">Follow the route</a>
        </div>
      </div>
    </div>
  </section>

{placeband('Ryde', 'Appley', 'Puckpool', 'Seaview')}
  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">In research</span>
        <h2>What we are working on next</h2>
        <p class="lede">Journeys we are building with the people who know these places. If you hold records, photographs or first-hand knowledge of any of them, we would like to hear from you.</p>
      </div>
      <ol class="beyond-list">
        <li><h3>Union Street</h3><p>The commercial spine of the town, and what is hiding above the shopfronts.</p></li>
        <li><h3>The seafront and the pier</h3><p>How arriving at Ryde has changed, and what that did to the town behind it.</p></li>
        <li><h3>Folklore and the darker side</h3><p>The stories the island tells about itself, mapped to where they are set.</p></li>
      </ol>
      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--primary" href="contact.html">Get in touch</a>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("journeys.html", html)


def build_how_we_work():
    d = 0
    html = head("How we work — IsleConnect",
                "What source-linked and human-checked actually mean, story by story.", d)
    html += header("how-we-work.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">How we work</span>
        <h1>What "human checked" actually means</h1>
        <p class="lede">It is an easy thing to claim and a hard thing to hold to. So here is exactly what we mean by it, and what each label on a story is promising.</p>
      </div>
    </div>
  </section>

  <section class="band band--ivory" style="padding-top:0">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">The marks on every story</span>
        <h2>Five labels, five specific promises</h2>
      </div>
      <ol class="beyond-list">
        <li>
          <h3>{marks('archive')}</h3>
          <p>The material came from a named archive, record office or documented collection, and we can tell you which one. Listed in the story's sources.</p>
        </li>
        <li>
          <h3>{marks('source')}</h3>
          <p>Every factual claim in the story traces to a source we hold. Where two sources disagree, we say so rather than picking the tidier one.</p>
        </li>
        <li>
          <h3>{marks('recon')}</h3>
          <p>An image is an interpretation, not a photograph of the past. It is built from documented evidence — an engraving, surviving fabric, measured detail — and labelled on screen wherever it appears. We never present a reconstruction as a record.</p>
        </li>
        <li>
          <h3>{marks('spot')}</h3>
          <p>The location is exact. You can stand where the story happened, and the practical detail on the page has been checked on the ground.</p>
        </li>
        <li>
          <h3>{marks('oral')}</h3>
          <p>Someone's first-hand account, recorded with their permission and used on terms they agreed.</p>
        </li>
      </ol>
    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Who checks it</span>
        <h2>Four different people can say "yes", and they mean different things</h2>
      </div>
      <ul class="facts">
        <li><span class="facts__k">Editorial</span><span class="facts__v">The story reads clearly, and nothing has been overstated for effect.</span></li>
        <li><span class="facts__k">Local knowledge</span><span class="facts__v">Someone who knows the place confirms it matches what is actually there.</span></li>
        <li><span class="facts__k">Historical</span><span class="facts__v">A specialist confirms the history and the interpretation are defensible.</span></li>
        <li><span class="facts__k">Rights</span><span class="facts__v">The rights-holder has agreed to their material being used, on recorded terms.</span></li>
      </ul>
      <div class="measure" style="margin-top:var(--space-lg)">
        <p>A story is only published when the checks it needs have all been made. Where a story has had editorial and local review but not yet a specialist historical review, we say so on the page rather than implying more scrutiny than it has had.</p>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Where AI fits</span>
        <h2>What the machine does, and what it never does</h2>
      </div>
      <div class="measure">
        <p><b>What it does.</b> It helps us search records faster, draft and redraft, and build visual reconstructions from documented evidence that would otherwise take weeks of illustration.</p>
        <p><b>What it never does.</b> Decide what is true, sign off a story, or publish anything. A person is responsible for every claim on this site, and if something here is wrong that is a person's mistake, not a machine's.</p>
        <p>If you think we have got something wrong, <a href="contact.html">tell us</a>. We would rather be corrected than be confidently mistaken.</p>
      </div>
    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Have something we should know about?</h2>
        <p>Records, photographs, or the kind of knowledge that only comes from paying attention to one place for thirty years.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="contact.html">Get in touch</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("how-we-work.html", html)

def build_partners():
    d = 0
    html = head("Work With Us — IsleConnect",
                "Partnerships, consultancy and place activation across Ryde and the Isle of Wight.", d,
                page="partners")
    html += header("for-partners.html", d, over=True)
    html += f"""
  <section class="hero hero--short">
    <div class="hero__media" aria-hidden="true">
      <img src="assets/img/card-explore-ryde.jpg" width="1600" height="504" alt="" loading="lazy" decoding="async">
    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <div class="hero__content">
          <span class="eyebrow">Work With Us</span>
          <h1>Turn local curiosity into footfall and action.</h1>
          <p class="hero__sub">Whether you run an independent venue, manage a visitor attraction, hold community archives, or want to launch a 30-day footfall pilot — IsleConnect connects stories to real-world outcomes.</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Book a 20-minute mapping call</a>
            <a class="btn btn--ghost-light" href="consultancy.html" data-ic-event="consultancy_view">Explore consultancy &amp; pilots</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="grid grid--3">
        <div class="benefit">
          <h3>Be discovered</h3>
          <p>Appear when someone is already exploring nearby and ready to stop.</p>
        </div>
        <div class="benefit">
          <h3>Tell your story</h3>
          <p>Show people what makes your venue or place worth stopping for — not a generic directory listing.</p>
        </div>
        <div class="benefit">
          <h3>Measure what happens</h3>
          <p>Understand whether visitors continue, explore, ask for directions or take action.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--navy">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Where it meets the street</span>
        <h2>It starts with a card on your counter</h2>
        <p class="lede">No app, no hardware, no screen to maintain. A visitor scans, the story opens in their browser, and the next place on the route is one tap away.</p>
      </div>
      <figure class="figure">
        <img src="assets/img/trail-signage.jpg" width="1122" height="1402" loading="lazy" decoding="async"
             alt="Two IsleConnect QR cards in acrylic holders on a caf&eacute; counter: a stop card reading &quot;You are near Stop 5&quot; with a scan code, and a smaller route reward partner card.">
        <figcaption class="figure__cap"><b>Signage design mockup.</b> The stop number and title shown are indicative artwork from an earlier draft — the canonical nine-stop list is still being confirmed, and no reward scheme is running yet. What is real is the mechanism: a code on a counter, a story in the browser, and a measurable onward journey.</figcaption>
      </figure>
    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Five ways to work together</span>
        <h2>Which path fits your organisation?</h2>
        <p class="lede">Choose the collaboration model that matches your goals, resources and timeline.</p>
      </div>
      <div class="grid grid--3">
        <div class="audience">
          <span class="eyebrow">Local Discovery</span>
          <h3>Venues &amp; businesses</h3>
          <p>An attraction, shop or caf&eacute; near a story or on a walking route seeking visitors.</p>
          <a class="link-arrow" href="partners/venues.html">For venues</a>
        </div>
        <div class="audience">
          <span class="eyebrow">Community</span>
          <h3>Organisations &amp; archives</h3>
          <p>Councils, heritage trusts, or community groups holding local knowledge and archives.</p>
          <a class="link-arrow" href="partners/organisations.html">For organisations</a>
        </div>
        <div class="audience">
          <span class="eyebrow">Creative</span>
          <h3>Authors &amp; creators</h3>
          <p>A book, a body of research, or a collection rooted in Island places and people.</p>
          <a class="link-arrow" href="partners/creators.html">For creators</a>
        </div>
      </div>

      <div class="grid grid--2" style="margin-top:var(--space-lg); gap:var(--space-lg)">
        <div class="bridge-card" style="background:var(--ivory); border:1px solid var(--border)">
          <span class="eyebrow" style="color:var(--navy)">Consultancy &amp; Small Pilots</span>
          <h3 style="color:var(--navy); margin-top:0.3rem">Packaged Strategy Pathways</h3>
          <p style="color:var(--ink)">From a 10-day Local Visibility Review to a 30-Day Story-to-Footfall Pilot or full Connected Place Programme.</p>
          <div class="btn-row" style="margin-top:var(--space-md)">
            <a class="btn btn--primary" href="consultancy.html" data-ic-event="consultancy_view">Explore consultancy</a>
          </div>
        </div>
        <div class="bridge-card" style="background:var(--ivory); border:1px solid var(--border)">
          <span class="eyebrow" style="color:var(--navy)">Free Initial Step</span>
          <h3 style="color:var(--navy); margin-top:0.3rem">20-Minute Mapping Call</h3>
          <p style="color:var(--ink)">A focused diagnostic conversation to map your current visibility gaps and identify quick wins for footfall.</p>
          <div class="btn-row" style="margin-top:var(--space-md)">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Request a mapping call</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Start a conversation.</h2>
        <p>Tell us what you run or what you hold. We'll tell you honestly whether there's a story in it and what practical next steps look like.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="contact.html">Get in touch</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("for-partners.html", html)


PARTNER_PAGES = {
    "venues": ("Venues & businesses", "Give people already exploring nearby a reason to stop.",
               "Walkers on the wartime trail pass your door already. Visitors reading about Union Street are standing outside it. IsleConnect puts your venue into the journey they are already on.",
               [("Be discovered", "Appear at the point someone is nearby and already curious."),
                ("Tell your story", "Your history, your people, your reason to stop — not a directory listing."),
                ("See what happens next", "Understand whether visitors continue, explore or take an action.")]),
    "creators": ("Authors & creators", "Take your story beyond the page and into the places connected to it.",
                 "If your work is rooted in real places, those places can carry it. We connect passages, research and recordings to the exact spots they describe, so a reader can go and stand there.",
                 [("Your work keeps working", "Readers find you at the location, not only in a shop."),
                  ("Rights respected", "Your work is used with permission, on terms you agree, and credited."),
                  ("New readers", "Visitors who came for the place discover the writing.")]),
    "organisations": ("Organisations", "Turn the knowledge you already hold into something the public can use.",
                      "Councils, trusts, museums and community groups often hold the best material on a place and the least capacity to publish it. We work with what you have, and you sign off everything before it goes live.",
                      [("Your records reach people", "Archive material put back where it came from."),
                       ("You keep control", "Nothing publishes without your approval."),
                       ("Evidence of use", "See what the public actually engages with.")]),
}


# One line per page, set large, in the display face. The commercial promise
# for a venue and the credibility claim for an organisation are different
# sentences and belong in different places — but they are the same component.
PARTNER_PROMISE = {
    "venues": "Turn local curiosity into local visits.",
    "organisations": "Built in Ryde. Tested in the real world.",
}

PROMISE_ABOUT = "Built in Ryde. Tested in the real world."


def promise(line):
    return f"""      <p class="promise">{line}</p>
""" if line else ""


def build_partner_page(key):
    d = 1
    title, sub, intro, points = PARTNER_PAGES[key]
    pts = "".join(f"""        <div class="benefit">
          <h3>{h}</h3>
          <p>{p}</p>
        </div>
""" for h, p in points)

    stats_block = ""
    if key == "venues":
        stats_block = f"""  <section class="band band--ivory" style="padding-top:0">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">See what happens next</span>
        <h2>You find out what visitors actually did</h2>
        <p class="lede">Not a dashboard to learn. A short monthly summary of what happened around your venue.</p>
      </div>
      <div class="stats stats--example" role="figure" aria-label="Example monthly summary" data-data-status="illustrative">
        <p class="stats__label">Example monthly summary — Puckpool Battery</p>
        <div class="stat"><b>327</b><span>people discovered this story</span></div>
        <div class="stat"><b>94</b><span>continued to another stop</span></div>
        <div class="stat"><b>36</b><span>requested directions to a nearby venue</span></div>
      </div>
      <p class="stats__note">An example of the report, using made-up numbers. Real figures arrive once your venue is live and people start walking the route.</p>
    </div>
  </section>

"""
    html = head(f"{title} — IsleConnect", sub, d, page=f"partner-{key}")
    html += header("for-partners.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <p class="crumb" style="color:var(--ink-muted)"><a href="{rel('for-partners.html', d)}" style="color:var(--ink-muted)">For partners</a> &nbsp;/&nbsp; {title}</p>
      <div class="band__head">
        <span class="eyebrow">For partners</span>
        <h1>{title}</h1>
        <p class="lede">{sub}</p>
      </div>
{promise(PARTNER_PROMISE.get(key))}      <div class="measure"><p>{intro}</p></div>
      <div class="grid grid--3" style="margin-top:var(--space-xl)">
{pts}      </div>
      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--primary" href="{rel('contact.html', d)}" data-ic-event="sponsor_enquiry">Start a conversation</a>
      </div>
    </div>
  </section>

{stats_block}  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">See it working</span>
        <h2>What we've built so far</h2>
      </div>
      <div class="grid grid--2">
        <div class="audience">
          <h3>Ryde 140</h3>
          <p>Evidence-led reconstructions of the buildings, people and moments that made the town.</p>
          <a class="link-arrow" href="{rel('ryde-140.html', d)}" data-ic-event="trail_selected" data-ic-trail="ryde-140">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided route through the Island's wartime coastline.</p>
          <a class="link-arrow" href="{rel('wartime-trail.html', d)}" data-ic-event="trail_selected" data-ic-trail="wartime-trail">Follow the route</a>
        </div>
      </div>
    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Be part of the journey.</h2>
        <p>Tell us what you run or what you hold. We'll tell you honestly whether we think there's a story in it.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="{rel('contact.html', d)}" data-ic-event="sponsor_enquiry">Start a conversation</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"partners/{key}.html", html)


def build_consultancy():
    d = 0
    html = head("Consultancy &amp; Pilots — IsleConnect",
                "Turn local attention into useful action. Evidence-led place consultancy, 30-day pilots and connected programmes.", d,
                page="consultancy")
    html += header("consultancy.html", d, over=True)
    html += f"""
  <section class="hero hero--short">
    <div class="hero__media" aria-hidden="true">
      <img src="assets/img/card-explore-ryde.jpg" width="1600" height="504" alt="" loading="lazy" decoding="async">
    </div>
    <div class="hero__scrim" aria-hidden="true"></div>
    <div class="hero__inner">
      <div class="wrap">
        <div class="hero__content">
          <span class="eyebrow">Consultancy &amp; Pilots</span>
          <h1>Turn local attention into useful action.</h1>
          <p class="hero__sub">We help destinations, attractions and independent businesses transform overlooked local stories into measurable discovery, footfall and customer visits.</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Book a 20-minute mapping call</a>
            <a class="btn btn--ghost-light" href="#pathways">View our pathways</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--ivory" id="pathways">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">How we work</span>
        <h2>Three practical pathways to action</h2>
        <p class="lede">You do not need to commission a vast digital platform to start seeing results. Begin where your business or place actually feels the friction.</p>
      </div>

      <div class="grid grid--3">
        <div class="benefit" style="display:flex; flex-direction:column; justify-content:space-between">
          <div>
            <span class="eyebrow">Diagnostic</span>
            <h3>1. Local Visibility Review</h3>
            <p>A fast, rigorous assessment of how easily visitors find your venue, story or experience on the ground and across digital search.</p>
            <ul class="ticks" style="margin-top:var(--space-md)">
              <li>Google Maps &amp; local listing discovery audit</li>
              <li>Physical walk-by friction &amp; arrival touchpoints</li>
              <li>Story differentiation assessment</li>
              <li>Actionable 10-day quick-win priority list</li>
            </ul>
          </div>
          <div style="margin-top:var(--space-lg)">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="visibility_review_click">Request my visibility review</a>
          </div>
        </div>

        <div class="benefit" style="display:flex; flex-direction:column; justify-content:space-between">
          <div>
            <span class="eyebrow">Small Pilot</span>
            <h3>2. 30-Day Story-to-Footfall Pilot</h3>
            <p>Prove the model on your doorstep with a controlled, measurable campaign connecting one verified story to customer visits.</p>
            <ul class="ticks" style="margin-top:var(--space-md)">
              <li>One evidence-led story &amp; high-impact short video</li>
              <li>Physical QR signage &amp; counter placement</li>
              <li>Direct onward routing to your venue or offer</li>
              <li>Weekly engagement &amp; onward footfall metrics</li>
            </ul>
          </div>
          <div style="margin-top:var(--space-lg)">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="pilot_enquiry_click">Discuss a 30-day pilot</a>
          </div>
        </div>

        <div class="benefit" style="display:flex; flex-direction:column; justify-content:space-between">
          <div>
            <span class="eyebrow">Strategic</span>
            <h3>3. Connected Place Programme</h3>
            <p>For town partnerships, business improvement districts, heritage trusts and destinations uniting multiple venues into a route.</p>
            <ul class="ticks" style="margin-top:var(--space-md)">
              <li>Curated walking trails linking complementary venues</li>
              <li>Shared visitor circulation &amp; dwell-time expansion</li>
              <li>Stakeholder governance &amp; rights clearance framework</li>
              <li>Comprehensive footfall reporting across all stops</li>
            </ul>
          </div>
          <div style="margin-top:var(--space-lg)">
            <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Map a place-based programme</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ CASE STUDY · RYDE TOWN HALL ============ -->
  <section class="band band--navy" id="town-hall-case-study" aria-labelledby="cs-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Commercial &amp; Civic Case Study</span>
        <h2 id="cs-h">Ryde Town Hall: Turning a Familiar Building into a Public Conversation</h2>
        <p class="lede">How IsleConnect used archival research, on-site photography and evidence-led visualisation to re-engage the community with a quiet landmark.</p>
      </div>

      <div class="grid grid--2" style="gap:var(--space-xl); align-items:start">
        <div>
          <div class="video-poster-card" style="margin-bottom:var(--space-md)">
            <img src="assets/img/card-town-hall.jpg" alt="Ryde Town Hall" width="1600" height="900" loading="lazy">
            <a href="ryde/ryde-town-hall.html#watch" class="video-poster-card__play" aria-label="Watch the Town Hall project film" data-ic-event="townhall_play">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
            </a>
          </div>
          <p class="notice notice--public" style="background:rgba(255,255,255,0.06); border-color:rgba(255,255,255,0.15); color:var(--ivory)">
            <b>FUTURE CONCEPT VISUALISATION — NO APPROVED SCHEME IMPLIED.</b> The civic gathering scene is an evidence-led concept visualisation to stimulate conversation.
          </p>
        </div>

        <div>
          <h3 style="color:var(--ivory)">The Challenge</h3>
          <p style="color:var(--ink-on-dark-muted)">Ryde Town Hall has stood in Lind Street since 1831, serving as council chamber, court and concert hall. Following its closure in the early 2000s, the building became a closed facade. Passers-by saw peeling paint and boarded doors; many forgot what the building had stood for, and newer residents had never set foot inside.</p>

          <h3 style="color:var(--ivory); margin-top:var(--space-md)">The Response</h3>
          <p style="color:var(--ink-on-dark-muted)">Rather than issuing a dense heritage report that few would read, IsleConnect developed a 50-second narrative arc spanning 190 years: from opening day in 1831, through Queen Victoria's 1887 Jubilee celebrations, into closure — ending with a visualised future possibility to prompt public dialogue.</p>

          <h3 style="color:var(--ivory); margin-top:var(--space-md)">Our 7-Point Process</h3>
          <ol class="ticks ticks--on-dark" style="padding-left:1.2rem">
            <li><b>Primary source gathering:</b> 1830s architectural plans and 1880s municipal records.</li>
            <li><b>On-site survey:</b> High-resolution photographic audit of architectural masonry and facade condition.</li>
            <li><b>Rigorous claims validation:</b> Separating verified architectural facts from interpretive elements.</li>
            <li><b>Evidence-led AI production:</b> Historical recreation supervised and checked frame by frame.</li>
            <li><b>Strict disclosure governance:</b> Clear legal labeling distinguishing records from conceptual visions.</li>
            <li><b>Friction-free deployment:</b> Fast mobile web delivery with zero app download friction.</li>
            <li><b>Civic call-to-action:</b> Direct community feedback channel asking "What could this corner become?".</li>
          </ol>

          <div class="btn-row" style="margin-top:var(--space-lg)">
            <a class="btn btn--primary" href="ryde/ryde-town-hall.html" data-ic-event="townhall_play">Watch the project</a>
            <a class="btn btn--ghost-light" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Could your place tell a stronger story?</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ TRUST & RIGOUR ============ -->
  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Why IsleConnect</span>
        <h2>Integrity first. Speed second.</h2>
      </div>
      <div class="grid grid--3">
        <div class="benefit">
          <h3>Human editorial control</h3>
          <p>We believe in artificial intelligence as an accelerator for research and production, never as an unsupervised publisher. Every claim is checked against primary sources.</p>
        </div>
        <div class="benefit">
          <h3>Zero-app friction</h3>
          <p>Visitors do not download apps for a 2-minute experience. Our stories load in under 1 second in any mobile browser via lightweight, accessible web standards.</p>
        </div>
        <div class="benefit">
          <h3>Transparent outcomes</h3>
          <p>We measure genuine public interest: video views, transcript reads, onward footfall and venue visits — without privacy-invasive surveillance or profiling.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Start with a 20-minute mapping call.</h2>
        <p>Whether you have an under-visited landmark, a quiet high-street corner, or an archive waiting for an audience, let's look at the practical options.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="contact.html#mapping-conversation" data-ic-event="enquiry_form_start">Book a mapping call</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("consultancy.html", html)


def build_about():
    d = 0
    html = head("About — IsleConnect",
                "IsleConnect brings Ryde's stories to life — helping people discover the history, places and businesses around them.", d,
                page="about")
    html += header("about.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">About</span>
        <h1>We put stories back where they happened.</h1>
      </div>
{promise(PROMISE_ABOUT)}      <div class="measure">
        <p>IsleConnect brings Ryde's stories to life — helping people discover the history, places and businesses around them.</p>
        <p>A fort with no interpretation is a wall. A frontage on Union Street is a frontage, unless someone tells you it is not the one that opened. The material is almost always already there — in an archive, in an engraving, or in the head of someone who has spent thirty years finding it out. What is usually missing is a way for a visitor to meet it at the moment they are standing in front of the place.</p>
        <p>That is the whole job.</p>
        <p>Ryde is where we are proving the model. The same approach can later bring books, attractions and destinations to life.</p>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Leadership</span>
        <h2>Built from practical business experience</h2>
      </div>
      <div class="measure">
        <p>IsleConnect is founded and directed in Ryde by <b>David Grannum</b>. It brings together over twenty years of building and operating real-world businesses with formal advanced training in artificial intelligence, including the Oxford Artificial Intelligence Programme and professional AI Solution Architect certifications.</p>
        <p>Too much conversation around AI focuses either on speculative hype or automated generic content that ignores local reality. IsleConnect takes the opposite stance: practical, evidence-led systems where machine intelligence accelerates research, data structuring and visual reconstruction, while real people retain absolute authority over what is said and published.</p>
        <p>Every story, partnership and consultancy engagement is built on that foundation: rigorous provenance, respect for local creators, and clear commercial measurement.</p>
      </div>
    </div>
  </section>

  <section class="band band--ivory">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Who we are</span>
        <h2>Historians, artists, venues and the people who keep local knowledge</h2>
      </div>
      <div class="measure">
        <p>We work in close collaboration with historians, artists, venues, authors and community organisations across Ryde and the Isle of Wight. They retain full authority over their knowledge, memories and archive material; IsleConnect provides the platform to turn it into an engaging, accessible public experience.</p>
        <p>Artificial intelligence supports research, visualisation and production, but it does not decide what is published. Sources, rights and interpretations remain subject to human review.</p>
      </div>
    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Start with one story.</h2>
        <p>Three are live now. More are being built with the people who know them.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="explore.html">Explore the stories</a>
          <a class="btn btn--ghost-light" href="for-partners.html">Work with us</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("about.html", html)


def contact_route():
    """Diagnostic mapping conversation form and direct email fallback."""
    e = SITE["contact_email"]
    endpoint = SITE["form_endpoint"] or ""
    return f"""      <div class="grid grid--2" style="gap:var(--space-xl); align-items:start">
        <div>
          <span class="eyebrow" id="mapping-conversation">Diagnostic Conversation</span>
          <h2>Request a 20-minute mapping call</h2>
          <p>If you run a venue, manage an attraction, or hold local records, let's map where your visibility and visitor journey can improve quickly.</p>
          <p>Tell us a little about your business or project. A real person reviews every request and responds within one working day.</p>

          <form class="diagnostic-form" method="post" action="{endpoint}">
            <div class="field">
              <label for="diag-name">Your name *</label>
              <input id="diag-name" name="name" type="text" autocomplete="name" required placeholder="e.g. Jane Smith">
            </div>
            <div class="field">
              <label for="diag-org">Business or organisation *</label>
              <input id="diag-org" name="organisation" type="text" required placeholder="e.g. The Coastal Gallery">
            </div>
            <div class="field">
              <label for="diag-web">Website or social link</label>
              <input id="diag-web" name="website" type="url" placeholder="https://example.co.uk">
            </div>
            <div class="field">
              <label for="diag-loc">Location</label>
              <input id="diag-loc" name="location" type="text" placeholder="e.g. Union Street, Ryde">
            </div>
            <div class="field">
              <label>What would you most like to improve?</label>
              <div class="options-grid">
                <label class="option-label"><input type="checkbox" name="improve[]" value="footfall"> Visits and footfall</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="bookings"> Bookings &amp; enquiries</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="visibility"> Online discovery &amp; maps</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="content"> Story &amp; content consistency</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="visitor-exp"> Visitor on-site experience</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="community"> Community engagement</label>
                <label class="option-label"><input type="checkbox" name="improve[]" value="workflow"> AI &amp; content workflow</label>
              </div>
            </div>
            <div class="field">
              <label for="diag-notes">Tell us briefly about what you run or hold</label>
              <span class="hint">A few sentences is plenty.</span>
              <textarea id="diag-notes" name="notes" rows="4" placeholder="Tell us about your venue, the challenge you face, or the story you would like to tell."></textarea>
            </div>
            <div class="field">
              <label for="diag-email">Your email *</label>
              <input id="diag-email" name="email" type="email" autocomplete="email" required placeholder="jane@example.co.uk">
            </div>
            <div class="field">
              <label for="diag-phone">Phone number (optional)</label>
              <input id="diag-phone" name="phone" type="tel" autocomplete="tel" placeholder="07123 456789">
            </div>
            <div class="field">
              <label class="option-label">
                <input type="checkbox" name="permission" required checked>
                <span>I am happy for IsleConnect to contact me about this enquiry.</span>
              </label>
            </div>
            <p class="hint">We use what you send only to reply and discuss working together. See our <a href="privacy.html">privacy notice</a>.</p>
            <div style="margin-top:var(--space-md)">
              <button class="btn btn--primary" type="submit">Request mapping conversation</button>
            </div>
          </form>

          <div id="enquiry-thank-you" class="thank-you-card" style="display:none">
            <span class="eyebrow" style="color:var(--gold)">Thank you</span>
            <h3 style="color:var(--navy); margin-top:0.2rem">We have received your details</h3>
            <p>David Grannum or a member of the team will review your project and get back to you within one working day.</p>
            <p>If you'd like to book a 20-minute conversation slot directly on our calendar, you can do so below:</p>
            <div class="btn-row" style="margin-top:var(--space-md)">
              <a class="btn btn--primary" href="mailto:{e}?subject=Booking%2020-Minute%20Mapping%20Call" data-ic-event="mapping_call_booked">Confirm mapping call via email</a>
            </div>
          </div>
        </div>

        <div style="padding-top:var(--space-lg)">
          <div class="nearby" style="background:var(--ivory); border:1px solid var(--border)">
            <div>
              <span class="nearby__kind">Direct Contact</span>
              <h3>Email us directly</h3>
              <p>Prefer to write an email without filling in a form? David reads every message and replies personally.</p>
              <p style="margin-top:var(--space-sm); font-size:1.1rem"><b><a href="mailto:{e}">{e}</a></b></p>
            </div>
            <a class="btn btn--ghost-dark" href="mailto:{e}?subject=IsleConnect%20enquiry">Write an email</a>
          </div>

          <div class="measure" style="margin-top:var(--space-xl)">
            <h3>Our commitment</h3>
            <p>We do not use high-pressure sales. We will tell you frankly whether your venue or project is a good fit for IsleConnect, what can be accomplished quickly, and what is best left alone.</p>
            <p>Your details are kept strictly confidential and never sold or shared. See our <a href="privacy.html">privacy notice</a>.</p>
          </div>
        </div>
      </div>
"""

def build_contact():
    d = 0
    html = head("Contact &amp; Mapping Conversation — IsleConnect", "Request a 20-minute mapping conversation or write to us directly.", d, page="contact")
    html += header("", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Start a conversation</span>
        <h1>Turn local curiosity into useful action</h1>
        <p class="lede">Book a diagnostic mapping call or get in touch about partnerships, stories or consultancy.</p>
      </div>

{contact_route()}
    </div>
  </section>
"""
    html += footer(d)
    write("contact.html", html)


LEGAL_INTRO = """      <p class="legal-meta">Operated by {operator} · Last reviewed {reviewed}</p>"""


def legal_page(slug, title, lede, body_html):
    d = 0
    html = head(f"{title} — IsleConnect", lede, d)
    html += header("", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <h1>{title}</h1>
        <p class="lede">{lede}</p>
      </div>
      <p class="legal-meta">Operated by {SITE['operator']} · Last reviewed {SITE['legal_reviewed']}</p>
      <div class="measure legal">
{body_html}
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"{slug}.html", html)


def build_privacy():
    e = SITE["contact_email"]
    legal_page("privacy", "Privacy",
        "How IsleConnect collects, uses and stores personal data.",
        f"""        <h2>Who we are</h2>
        <p>IsleConnect is a visitor-experience project operated by {SITE['operator']}, based on the Isle of Wight. We are the data controller for the personal data described on this page. We are not connected with any similarly named limited company.</p>
        <p>You can reach us at <a href="mailto:{e}">{e}</a>.</p>

        <h2>What we collect</h2>
        <p><b>When you contact us.</b> Your name, email address, what you run or hold, and whatever you choose to write in your message. We use this only to reply to you and to discuss working together.</p>
        <p><b>When you use the site.</b> At present, nothing. No usage or analytics data is sent anywhere, because we have not switched any measurement on: the site carries no advertising trackers, no third-party analytics, and no profiling cookies, and it transmits no record of the pages you open.</p>
        <p>We intend to measure how our stories are used — which stories are opened, whether a visitor continues to a second one, whether directions to a nearby venue are requested. Those would be counts of events, not profiles of people. None of it is happening yet, and we will update this notice before it does rather than afterwards.</p>
        <p>We do not ask for, and have no use for, special category data — health, beliefs, or anything of that kind. Please don't send it to us.</p>

        <h2>Why we are allowed to hold it</h2>
        <p>For enquiries, our lawful basis is legitimate interests: you have contacted us and expect a reply, and answering you is the whole point. Where we send anything beyond a direct reply, we ask for consent first, and you can withdraw it at any time.</p>

        <h2>How long we keep it</h2>
        <p>Enquiries are kept for up to two years from the last contact, then deleted. There is currently no usage measurement to retain.</p>

        <h2>Who else sees it</h2>
        <p>Our email and hosting providers process data on our behalf under contract. We do not sell personal data. We do not pass enquiries to partner venues unless you ask us to.</p>

        <h2>Your rights</h2>
        <p>You can ask us for a copy of what we hold, ask us to correct or delete it, or object to how we use it. Email <a href="mailto:{e}">{e}</a> and we will respond within one month.</p>
        <p>If you are unhappy with how we have handled your data you can complain to the Information Commissioner's Office at <a href="https://ico.org.uk" rel="noopener">ico.org.uk</a>.</p>

        <h2>Cookies</h2>
        <p>This site sets no cookies and writes nothing to your device. If that changes, we will ask you before any non-essential storage is used, and this notice will say so first.</p>

        <h2>Changes</h2>
        <p>If this notice changes we will update the review date at the top of the page.</p>""")


def build_accessibility():
    e = SITE["contact_email"]
    legal_page("accessibility", "Accessibility",
        "What we have built for access, what we have tested, and what is not good enough yet.",
        f"""        <p>IsleConnect is used outdoors, on phones, often on uneven ground and in poor weather. Access is not a compliance exercise for us — it decides whether the thing works at all.</p>

        <h2>What we have built for access</h2>
        <p>This is a description of what we have built and what we have checked. It is not a conformance statement: the site has not been audited against WCAG 2.2, by us or by anyone else, and we do not claim it meets that standard.</p>
        <ul>
          <li>Every page is built to be operated by keyboard alone, with a visible focus outline and a skip link to the main content. We have walked the main routes this way; we have not exhaustively tested every control.</li>
          <li>Text and background colours were chosen against the WCAG 2.2 AA contrast ratios, and we have checked the main text and interface colours. The full palette has not been independently verified.</li>
          <li>Text resizes without breaking the layout, and the page reflows to a single column on small screens.</li>
          <li>Every film has a written transcript on the same page, in a panel you can open — including where the same film also appears on the homepage or a journey page. Our build refuses to publish a page that carries a film without one.</li>
          <li>Nothing moves, flashes or plays automatically. Video starts only when you press play.</li>
          <li>If your device or browser is set to reduce motion, animation is switched off and the content still works.</li>
          <li>Our press-and-hold reveal can also be operated as a simple on/off toggle, because holding a button is not possible with some assistive technology.</li>
          <li>Practical access information — steps, uneven ground, step-free routes — is given for every place we send you to.</li>
        </ul>

        <h2>What is not good enough yet</h2>
        <ul>
          <li>No independent accessibility audit has been carried out. Everything above is our own assessment of our own work.</li>
          <li>Our films have captions burned into the picture rather than selectable caption tracks. Transcripts cover the content, but captions cannot yet be resized or restyled.</li>
          <li>The site has not yet been tested with a screen reader by someone who uses one daily. We would rather say so than imply otherwise.</li>
          <li>We have not tested with speech input, screen magnification, or a switch device.</li>
          <li>Some of the places we write about are genuinely difficult to reach. We describe the access honestly rather than pretending otherwise, but we cannot change the ground.</li>
        </ul>

        <h2>Tell us where it fails</h2>
        <p>If something here does not work for you, please tell us at <a href="mailto:{e}">{e}</a> and say what you were trying to do. We will reply, and we will say plainly whether and when we can fix it.</p>

        <p>This statement describes the site as built and reviewed on {SITE['legal_reviewed']}. It is an honest self-assessment rather than a third-party audit, and we would rather understate what we have verified than claim a standard we have not tested against.</p>""")


def build_terms():
    e = SITE["contact_email"]
    legal_page("terms", "Terms",
        "The terms on which IsleConnect content and services are provided.",
        f"""        <h2>Who provides this site</h2>
        <p>This site is provided by {SITE['operator']}, Isle of Wight. Contact: <a href="mailto:{e}">{e}</a>.</p>

        <h2>Using the site</h2>
        <p>You are welcome to read, watch and share our stories, and to follow our trails. Please don't republish our films or text commercially, or present our work as your own, without asking us first.</p>

        <h2>Historical interpretation</h2>
        <p>Some images on this site are reconstructions — visual interpretations built from documented sources, not photographs of the past. They are labelled as such wherever they appear, and each story lists what it was built from. We work to make them accurate, but an interpretation is not a record, and we will correct anything shown to be wrong.</p>

        <h2>Visiting the places we describe</h2>
        <p>Our stories point at real locations, many of them outdoors and some of them uneven, exposed or on private land. Opening times and access change. Check before you travel, follow signage, and take responsibility for your own safety. We are not liable for anything that happens on a visit.</p>

        <h2>Other people's rights</h2>
        <p>Archive material and creative work belonging to others is used with permission and credited. If you believe we have used something we should not have, tell us at <a href="mailto:{e}">{e}</a> and we will take it down while we look into it.</p>

        <h2>Corrections</h2>
        <p>If you think something here is wrong, please tell us. We would rather be corrected than be confidently mistaken.</p>

        <h2>Liability</h2>
        <p>We provide this site in good faith and take care over it, but we cannot guarantee it will always be available or error-free. Nothing here excludes liability that cannot lawfully be excluded.</p>

        <h2>Law</h2>
        <p>These terms are governed by the law of England and Wales.</p>""")


def build_info():
    """Deployment identity. There is exactly one implementation of this and it
    is tools/build-info.py — the deploy runs it directly as the build command,
    so a local build must not produce a second, differently-defaulted file."""
    import subprocess as _sp
    r = _sp.run([sys.executable, os.path.join(ROOT, "tools", "build-info.py")],
                capture_output=True, text=True)
    if r.returncode != 0:
        print("\nBUILD FAILED — tools/build-info.py exited "
              f"{r.returncode}:\n{r.stdout}{r.stderr}")
        raise SystemExit(1)


def build_sitemap_and_robots():
    """Generated from the pages actually written — a review-state page cannot
    end up in here by accident."""
    base = SITE["base_url"].rstrip("/")
    urls = "".join(
        "  <url><loc>%s/%s</loc></url>\n" % (base, path.replace("index.html", ""))
        for path in sorted(PUBLIC_PAGES))
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + urls + "</urlset>\n")
    PUBLIC_PAGES.remove("sitemap.xml")

    write("robots.txt",
          "User-agent: *\n"
          "Disallow: /review/\n"
          "Allow: /\n\n"
          "Sitemap: %s/sitemap.xml\n" % base)
    PUBLIC_PAGES.remove("robots.txt")



# ------------------------------------------------ registry / renderer parity
# Page bodies still come from STORIES and SOON while the registry governs
# publication. That is two sources of truth for the same story, which is the
# divergence this whole change exists to stop — so until the bodies are
# generated from records, the two must be proven identical on every build.

def validate_render_sources():
    errs = []
    render_keys = set(STORIES) | set(SOON)
    registry_keys = set(RENDER_KEY_TO_SLUG)

    if len(RENDER_KEY_TO_SLUG) != len(REG["stories"]):
        errs.append("two records share the last segment of their slug, so a "
                    "renderer key cannot be resolved unambiguously")

    for key in sorted(render_keys - registry_keys):
        errs.append(f"{key!r} is rendered but has no record in content/stories/")

    # A record only needs a renderer entry if its status lets it render at all.
    # town-hall-rebox is blocked and correctly has none.
    for key in sorted(registry_keys - render_keys):
        status = BY_SLUG[RENDER_KEY_TO_SLUG[key]]["status"]
        if status in RENDERABLE:
            errs.append(f"{key!r} is {status} and should render, but has no "
                        f"renderer entry in STORIES or SOON")

    for key in sorted(render_keys & registry_keys):
        rec = BY_SLUG[RENDER_KEY_TO_SLUG[key]]
        if key in STORIES:
            title, line = STORIES[key]["title"], STORIES[key]["line"]
            href = STORIES[key]["collection_href"]
        else:
            _coll, href, title, line = SOON[key]
        if title != rec["title"]:
            errs.append(f"{key}: renderer title {title!r} != record "
                        f"{rec['title']!r} ({rec['_path']})")
        if line != rec["line"]:
            errs.append(f"{key}: renderer line differs from the record "
                        f"({rec['_path']})")
        # Compare collection identity, not the display string: the renderer is
        # free to use a short label, but it must link to the same collection
        # the record declares.
        rendered_coll = os.path.basename(href).replace(".html", "")
        rec_colls = set(rec.get("collections") or [])
        if rendered_coll not in rec_colls:
            errs.append(f"{key}: renderer links to collection "
                        f"{rendered_coll!r} but the record declares "
                        f"{sorted(rec_colls)} ({rec['_path']})")

    # Publication permission comes from status, never from which dict a key
    # happens to sit in.
    for key in sorted(render_keys & registry_keys):
        status = BY_SLUG[RENDER_KEY_TO_SLUG[key]]["status"]
        if key in STORIES and status not in RENDER_FULL:
            errs.append(f"{key}: has a full story body but status is {status!r} "
                        f"— only {sorted(RENDER_FULL)} may render a full page")
        if key in SOON and status not in RENDER_REDUCED:
            errs.append(f"{key}: is in SOON but status is {status!r} — only "
                        f"{sorted(RENDER_REDUCED)} render the reduced page")

    if errs:
        print("\nBUILD FAILED — the registry and the renderers disagree:\n")
        for e in errs:
            print("   " + e)
        print("\nThe record is authoritative. Correct the renderer to match it.\n")
        raise SystemExit(1)


validate_render_sources()

# ============================================================ run

if __name__ == "__main__":
    print("Registry: %d stories (%d published), %d collections, %d partners"
          % (len(REG["stories"]), LIVE_COUNT,
             len(REG["collections"]), len(REG["partners"])))

    build_index()
    build_explore()
    build_journeys()
    build_how_we_work()
    build_ryde140()
    build_wartime()

    # Driven by status, in slug order. Nothing renders because it appears in a
    # dictionary; it renders because its record says it may.
    for _slug, _st in sorted(BY_SLUG.items()):
        _key = _slug.rsplit("/", 1)[-1]
        if _st["status"] in RENDER_FULL:
            build_story(_key)
        elif _st["status"] in RENDER_REDUCED:
            build_soon(_key)

    build_partners()
    build_consultancy()
    for key in PARTNER_PAGES:
        build_partner_page(key)
    build_about()
    build_contact()
    build_privacy()
    build_accessibility()
    build_terms()
    build_sitemap_and_robots()
    build_info()

    # Nothing outside a renderable state may have produced a page, by any route.
    leaked = sorted(st["slug"] + ".html" for st in REG["stories"].values()
                    if st["status"] not in RENDERABLE
                    and st["slug"] + ".html" in PUBLIC_PAGES)
    if leaked:
        print("\nBUILD FAILED — records that must not publish produced pages:",
              leaked)
        raise SystemExit(1)

    if len(PUBLIC_PAGES) != EXPECTED_PUBLIC_PAGES:
        print(f"\nBUILD FAILED — {len(PUBLIC_PAGES)} public pages, expected "
              f"{EXPECTED_PUBLIC_PAGES}. If this change is intended, update "
              f"EXPECTED_PUBLIC_PAGES and say why in the pull request.")
        for p in sorted(PUBLIC_PAGES):
            print("   " + p)
        raise SystemExit(1)

    guard(PUBLIC_PAGES)
    print("\nDone.")
