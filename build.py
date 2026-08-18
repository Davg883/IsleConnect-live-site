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

ROOT = os.path.dirname(os.path.abspath(__file__))

NAV = [
    ("explore.html",       "Explore Ryde"),
    ("ryde-140.html",      "Ryde 140"),
    ("wartime-trail.html", "Wartime Trail"),
    ("for-partners.html",  "For Partners"),
    ("about.html",         "About"),
]

FOOTER_COLS = [
    ("Explore Ryde", [
        ("ryde/royal-victoria-arcade.html", "Royal Victoria Arcade"),
        ("ryde/puckpool-battery.html",      "Puckpool Battery"),
        ("explore.html",                    "All stories"),
    ]),
    ("Collections", [
        ("ryde-140.html",      "Ryde 140"),
        ("wartime-trail.html", "Wartime Trail"),
    ]),
    ("For partners", [
        ("partners/venues.html",        "Venues & businesses"),
        ("partners/creators.html",      "Authors & creators"),
        ("partners/organisations.html", "Organisations"),
    ]),
    ("IsleConnect", [
        ("about.html",         "About"),
        ("contact.html",       "Contact"),
        ("privacy.html",       "Privacy"),
        ("accessibility.html", "Accessibility"),
        ("terms.html",         "Terms"),
    ]),
]

TRUST_BODY = ("We use source-linked local knowledge and work with the people who know "
              "the story or place. AI helps us create richer experiences faster, but "
              "people remain responsible for what gets published.")


def rel(path, depth):
    return ("../" * depth) + path


def head(title, description, depth):
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
<meta name="theme-color" content="#16243D">
<link rel="icon" href="{rel('favicon.ico', depth)}" sizes="48x48">
<link rel="icon" type="image/png" href="{rel('assets/img/favicon-32.png', depth)}" sizes="32x32">
<link rel="apple-touch-icon" href="{rel('assets/img/apple-touch-icon.png', depth)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel('assets/css/isleconnect.css', depth)}">
</head>
<body>

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


def thread():
    """The story thread — an engraved route line that draws itself as you
    scroll. Used between sections to say 'stories connect places' without
    writing it down."""
    dots = "".join('<circle cx="%d" cy="%d" r="3.4"/>' % (x, y) for x, y in THREAD_DOTS)
    return f"""      <svg class="thread" viewBox="0 0 1200 100" preserveAspectRatio="none"
           role="presentation" aria-hidden="true" focusable="false">
        <path d="{THREAD_PATH}"/>{dots}
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


def placeband(*names):
    """Place typography — location names set large enough to read as landscape."""
    spans = "".join('<span class="placename">%s</span>' % n for n in names)
    return f"""  <div class="placeband" aria-hidden="true">
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


def video_block(slug, poster, label, note, depth, variant="720"):
    """variant: '720' for grid/summary contexts, '' for the full 1080p file
    on a dedicated story page where the video is the whole point."""
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
"""


def write(path, html):
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
}

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
                "Explore the stories, places and people that shaped Ryde — and discover where to go next.", d)
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
            <a class="btn btn--ghost-light" href="for-partners.html">For local partners</a>
          </div>
          {marks('recon', 'source')}
        </div>
      </div>
    </div>
  </section>

  <!-- ============ 2 · TWO FLAGSHIP EXPERIENCES ============ -->
  <section class="band band--ivory" aria-labelledby="flagship-h">
    <div class="wrap">
      <div class="band__head">
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
{thread()}  </div>

  <!-- ============ 3 · HOW IT WORKS ============ -->
  <section class="band band--navy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="band__head band__head--centre">
        <span class="eyebrow">How IsleConnect works</span>
        <h2 id="how-h">Discover. Experience. Go.</h2>
      </div>
      <div class="grid grid--3 steps">
        <div class="step"><span class="step__num" aria-hidden="true">1</span><h3>Discover</h3><p>Find a story connected to where you are.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">2</span><h3>Experience</h3><p>Watch, listen or explore the story on your phone.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">3</span><h3>Go</h3><p>Visit the next place, venue or story nearby.</p></div>
      </div>
      <p class="band__close">The digital experience is there to help you discover more of the real place.</p>
    </div>
  </section>

  <!-- ============ 4 · EXPLORE RYDE — editorial grid, not a card row ============ -->
  <section class="band band--ivory" aria-labelledby="nodes-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Explore Ryde</span>
        <h2 id="nodes-h">A growing network of stories</h2>
        <p class="lede">Two are live. The rest are being built with the people who know them.</p>
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
    </div>
  </section>

{placeband('Ryde', 'Appley', 'Puckpool', 'Seaview')}
  <!-- ============ 5 · THE TWO COLLECTIONS ============ -->
  <section class="band band--ivory-deep" aria-labelledby="coll-h">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Collections</span>
        <h2 id="coll-h">Stories that belong together</h2>
        <p class="lede">Individual stories are useful. Curated collections are what turn a visit into a route.</p>
      </div>
{thread()}
      <div class="grid grid--2">
        <div class="audience">
          <span class="eyebrow">Ryde 140</span>
          <h3>A town explored across the centuries</h3>
          <p>A growing collection exploring Ryde's buildings, people and stories across the centuries.</p>
          <a class="link-arrow" href="ryde-140.html">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <span class="eyebrow">Ryde to Seaview</span>
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.</p>
          <a class="link-arrow" href="wartime-trail.html">Follow the route</a>
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
        <a class="btn btn--primary" href="for-partners.html">Become a Ryde partner</a>
      </div>
    </div>
  </section>

  <!-- ============ 7 · TRUST ============ -->
  <section class="band band--ivory" style="padding-top:0">
    <div class="wrap">
{trust_panel()}    </div>
  </section>

  <!-- ============ 8 · BEYOND RYDE ============ -->
  <section class="band band--ivory-deep" aria-labelledby="beyond-h">
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
                "Stories, places and people across Ryde and the coast to Seaview.", d)
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
          <a class="link-arrow" href="ryde-140.html">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.</p>
          <a class="link-arrow" href="wartime-trail.html">Follow the route</a>
        </div>
      </div>
    </div>
  </section>

  <section class="band band--navy">
    <div class="wrap">
      <div class="band__head band__head--centre">
        <span class="eyebrow">How IsleConnect works</span>
        <h2>Discover. Experience. Go.</h2>
      </div>
      <div class="grid grid--3 steps">
        <div class="step"><span class="step__num" aria-hidden="true">1</span><h3>Discover</h3><p>Find a story connected to where you are.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">2</span><h3>Experience</h3><p>Watch, listen or explore the story on your phone.</p></div>
        <div class="step"><span class="step__num" aria-hidden="true">3</span><h3>Go</h3><p>Visit the next place, venue or story nearby.</p></div>
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
                "A growing collection exploring Ryde's buildings, people and stories across the centuries.", d)
    html += header("ryde-140.html", d, over=True)
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
      <p class="notice" style="margin-top:var(--space-lg)"><b>Wording check needed.</b> This page deliberately avoids stating what the "140" refers to. Confirm the anniversary and the precise framing before launch — see BUILD-SPEC.md §9.</p>
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
                "A self-guided journey through the places that defended, supplied and lived through the Island's wartime years.", d)
    html += header("wartime-trail.html", d, over=True)
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
      <p class="notice" style="margin-top:var(--space-lg)"><b>Canonical numbering.</b> The Puckpool film states "Stop 7 of 9", so nine stops is the master system — the website, QR codes, films and printed material must all use it. Five stops are not yet named here, and the distance and walking time above are estimates. Confirm the full list before launch.</p>
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
      </div>
{thread()}      <ol class="route">
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
          <a class="btn btn--primary" href="partners/venues.html">Become a partner</a>
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

    html = head(f'{s["title"]} — IsleConnect', s["line"], d)
    html += header(s["collection_href"], d, over=True)
    transcript = "\n".join(f"          <p>{line}</p>" for line in s.get("transcript", []))
    transcript_block = ""
    if transcript:
        transcript_block = f"""      <details class="transcript">
        <summary>Read the transcript</summary>
        <div class="transcript__body">
{transcript}
        </div>
      </details>
"""

    nearby_block = ""
    if s.get("nearby"):
        nb = s["nearby"]
        nearby_block = f"""    <section class="exp-section">
      <span class="eyebrow">Nearby</span>
      <h2>While you are here</h2>
      <div class="nearby">
        <div>
          <span class="nearby__kind">{nb['kind']}</span>
          <h3>{nb['name']}</h3>
          <p>{nb['line']}</p>
        </div>
        <a class="btn btn--ghost-dark" href="{rel('contact.html', d)}">Get directions</a>
      </div>
      <p class="notice" style="margin-top:var(--space-md)"><b>Confirm before launch.</b> {nb['name']} appears as a local retail partner on the film's end card. Publish this block only if the agreement is in place — and wire "Get directions" to a real map link.</p>
    </section>

"""

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

    <section class="exp-section">
      <h2 class="visually-hidden">The experience</h2>
{video_block(s['video'], s['poster'], s['video_label'], s['video_note'], d, variant='')}{transcript_block}    </section>

    <section class="exp-section" id="story">
      <span class="eyebrow">The story</span>
      <h2>What happened here</h2>
      <div class="measure">
{story}
      </div>
    </section>

    <section class="exp-section">
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

    <section class="exp-section">
      <span class="eyebrow">Behind the story</span>
      <h2>Who made this</h2>
      <div class="contributor">
        <div class="media media--1x1">
          <span class="media__spec"><b>portrait-{slug}</b>800 × 800</span>
        </div>
        <div>
          <p>Short biography of the contributor or partner organisation. Two or three sentences — enough to establish who they are and why they know this.</p>
          <p class="notice"><b>Copy and portrait needed.</b></p>
        </div>
      </div>
    </section>

    <section class="exp-section">
      <span class="eyebrow">Sources</span>
      <h2>Where this comes from</h2>
      <ul class="sources">
{sources}
      </ul>
    </section>
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
    html = head(f"{title} — IsleConnect", line, d)
    html += header(coll_href, d)
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


def build_partners():
    d = 0
    html = head("For Partners — IsleConnect",
                "Be part of the journey. IsleConnect helps visitors discover the story around them.", d)
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
          <span class="eyebrow">For partners</span>
          <h1>Be part of the journey.</h1>
          <p class="hero__sub">IsleConnect helps visitors discover the story around them — and gives nearby businesses and attractions a natural place in that journey.</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="contact.html">Become a Ryde partner</a>
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
    </div>
  </section>

  <section class="band band--ivory-deep">
    <div class="wrap">
      <div class="band__head">
        <h2>Which one sounds like you?</h2>
      </div>
      <div class="grid grid--3">
        <div class="audience">
          <h3>Venues &amp; businesses</h3>
          <p>An attraction, a venue, a shop or a caf&eacute; near a story or on a route.</p>
          <a class="link-arrow" href="partners/venues.html">For venues</a>
        </div>
        <div class="audience">
          <h3>Authors &amp; creators</h3>
          <p>A book, a body of research, a collection or an archive rooted in real places.</p>
          <a class="link-arrow" href="partners/creators.html">For creators</a>
        </div>
        <div class="audience">
          <h3>Organisations</h3>
          <p>A council, a trust, a museum or a community group holding local knowledge.</p>
          <a class="link-arrow" href="partners/organisations.html">For organisations</a>
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
        <p>Tell us what you run or what you hold. We'll tell you honestly whether we think there's a story in it.</p>
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
      <div class="stats">
        <div class="stat"><b>327</b><span>people discovered this story</span></div>
        <div class="stat"><b>94</b><span>continued to another stop</span></div>
        <div class="stat"><b>36</b><span>requested directions to a nearby venue</span></div>
      </div>
      <p class="notice" style="margin-top:var(--space-lg)"><b>Illustrative figures.</b> These are an example of the reporting shape, not results. Replace with real numbers once the Ryde pilot has run — or remove this block entirely until then.</p>
    </div>
  </section>

"""
    html = head(f"{title} — IsleConnect", sub, d)
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
      <div class="measure"><p>{intro}</p></div>
      <div class="grid grid--3" style="margin-top:var(--space-xl)">
{pts}      </div>
      <div class="btn-row" style="margin-top:var(--space-lg)">
        <a class="btn btn--primary" href="{rel('contact.html', d)}">Start a conversation</a>
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
          <a class="link-arrow" href="{rel('ryde-140.html', d)}">Explore Ryde 140</a>
        </div>
        <div class="audience">
          <h3>Ryde to Seaview Wartime Trail</h3>
          <p>A self-guided route through the Island's wartime coastline.</p>
          <a class="link-arrow" href="{rel('wartime-trail.html', d)}">Follow the route</a>
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
          <a class="btn btn--primary" href="{rel('contact.html', d)}">Start a conversation</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"partners/{key}.html", html)


def build_about():
    d = 0
    html = head("About — IsleConnect",
                "IsleConnect brings Ryde's stories to life — helping people discover the history, places and businesses around them.", d)
    html += header("about.html", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">About</span>
        <h1>We put stories back where they happened.</h1>
      </div>
      <div class="measure">
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
        <span class="eyebrow">Who we work with</span>
        <h2>Historians, venues, authors and the people who keep local knowledge</h2>
      </div>
      <p class="notice"><b>Copy needed.</b> Three or four sentences on the team and background. Do not name partners you have not agreed in writing.</p>
    </div>
  </section>

  <section class="closer">
    <div class="closer__inner">
      <div class="wrap">
        <h2>Start with one story.</h2>
        <p>Two are live now. More are being built with the people who know them.</p>
        <div class="btn-row btn-row--centre">
          <a class="btn btn--primary" href="explore.html">Explore the stories</a>
          <a class="btn btn--ghost-light" href="for-partners.html">Become a Ryde partner</a>
        </div>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write("about.html", html)


def build_contact():
    d = 0
    html = head("Contact — IsleConnect", "Tell us about your venue, story or records.", d)
    html += header("", d)
    html += """
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head">
        <span class="eyebrow">Contact</span>
        <h1>Start a conversation</h1>
        <p class="lede">Three questions. That is deliberately all — we would rather talk than read a form.</p>
      </div>

      <form class="form" method="post" action="#" novalidate>
        <div class="field">
          <label for="name">Your name</label>
          <input id="name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" name="email" type="email" autocomplete="email" required>
        </div>
        <div class="field">
          <label for="kind">What do you run or hold?</label>
          <select id="kind" name="kind">
            <option>A venue or business in or near Ryde</option>
            <option>A book or body of writing</option>
            <option>Records, photographs or local knowledge</option>
            <option>A council, trust or community organisation</option>
            <option>Something else</option>
          </select>
        </div>
        <div class="field">
          <label for="about">Tell us about it</label>
          <span class="hint">A few sentences is plenty.</span>
          <textarea id="about" name="about"></textarea>
        </div>
        <div>
          <button class="btn btn--primary" type="submit">Send</button>
        </div>
        <p class="notice"><b>Not wired up.</b> Connect this to your form handler or inbox before launch, and add the privacy line required by UK GDPR.</p>
      </form>
    </div>
  </section>
"""
    html += footer(d)
    write("contact.html", html)


def build_stub(slug, title, body):
    d = 0
    html = head(f"{title} — IsleConnect", title, d)
    html += header("", d)
    html += f"""
  <section class="band band--ivory" style="padding-top:calc(var(--header-h) + var(--band-y))">
    <div class="wrap">
      <div class="band__head"><h1>{title}</h1></div>
      <div class="measure">
        <p>{body}</p>
        <p class="notice"><b>Content needed before launch.</b> This page must be written and reviewed — it is a legal requirement, not a nice-to-have.</p>
      </div>
    </div>
  </section>
"""
    html += footer(d)
    write(f"{slug}.html", html)


# ============================================================ run

if __name__ == "__main__":
    build_index()
    build_explore()
    build_ryde140()
    build_wartime()
    for slug in STORIES:
        build_story(slug)
    for slug in SOON:
        build_soon(slug)
    build_partners()
    for key in PARTNER_PAGES:
        build_partner_page(key)
    build_about()
    build_contact()
    build_stub("privacy", "Privacy",
               "How IsleConnect collects, uses and stores personal data, written to meet UK GDPR.")
    build_stub("accessibility", "Accessibility",
               "How IsleConnect works for people with access needs, what we have tested, and what we know is not yet good enough. This matters more than usual for a product used outdoors, on phones, on uneven ground.")
    build_stub("terms", "Terms",
               "The terms under which IsleConnect content and services are provided.")
    print("\nDone.")
