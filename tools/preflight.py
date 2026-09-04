#!/usr/bin/env python3
"""
IsleConnect — pre-deployment gate.

Steps 1-9 of the deployment sequence. Run before pushing. Exits non-zero on
any failure, so CI blocks the deploy rather than warning about it.

    python3 tools/preflight.py
"""

import os
import re
import subprocess
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIL = []
WARN = []


def fail(step, msg):
    FAIL.append(f"[{step}] {msg}")


def warn(step, msg):
    WARN.append(f"[{step}] {msg}")


# 1 · production build (also runs registry validation and the content guard)
r = subprocess.run([sys.executable, "build.py"], cwd=ROOT,
                   capture_output=True, text=True)
if r.returncode != 0:
    fail("1 build", "build.py failed:\n" + (r.stdout or "") + (r.stderr or ""))
    print("\n".join(FAIL))
    sys.exit(1)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "build ok")

sys.path.insert(0, ROOT)
import build as B  # noqa: E402  (import after a successful build)

# Inspect what is actually on disk — that is what gets deployed, and it will
# include anything left behind by an earlier build.
pages = sorted(
    os.path.relpath(f, ROOT).replace(os.sep, "/")
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
)

EXPECTED_PUBLIC_PAGES = [
    "about.html",
    "accessibility.html",
    "consultancy.html",
    "contact.html",
    "explore.html",
    "how-we-work.html",
    "index.html",
    "journeys.html",
    "partners/creators.html",
    "partners/organisations.html",
    "partners/venues.html",
    "privacy.html",
    "ryde-140.html",
    "ryde/appley-tower.html",
    "ryde/puckpool-battery.html",
    "ryde/royal-victoria-arcade.html",
    "ryde/ryde-pier.html",
    "ryde/ryde-town-hall.html",
    "ryde/seaview.html",
    "ryde/union-street.html",
    "terms.html",
    "wartime-trail.html",
    "work-with-us.html",
]

if pages != EXPECTED_PUBLIC_PAGES:
    missing_pages = set(EXPECTED_PUBLIC_PAGES) - set(pages)
    extra_pages = set(pages) - set(EXPECTED_PUBLIC_PAGES)
    if missing_pages:
        fail("2 manifest", f"Missing expected public pages: {sorted(missing_pages)}")
    if extra_pages:
        fail("2 manifest", f"Unexpected public pages found on disk: {sorted(extra_pages)}")


# 2 · prohibited content against every generated page on disk
B.guard(pages)


# 3 · every story and partner record is in a known state
for sid, st in B.REG["stories"].items():
    if st.get("status") not in B.STATUSES:
        fail("3 states", f"{sid}: unknown status {st.get('status')!r}")


# 4 · what is on disk matches what each record's status permits
# Permission comes from the status, not from membership of any list:
#   published → a full story page   research → the reduced page   else → none
for sid, st in B.REG["stories"].items():
    candidate = st["slug"] + ".html"
    on_disk = candidate in pages
    status = st.get("status")
    if status in B.RENDERABLE:
        if not on_disk:
            fail("4 states", f"{sid} is {status} and should have produced "
                             f"{candidate}, which is missing")
        elif status in B.RENDER_REDUCED:
            body = open(os.path.join(ROOT, candidate), encoding="utf-8").read()
            if 'page="story-in-development"' not in body:
                fail("4 states", f"{sid} is {status} but {candidate} is not the "
                                 f"reduced 'in development' page")
    elif on_disk:
        fail("4 states", f"{sid} is {status} but produced {candidate}")

if glob.glob(os.path.join(ROOT, "review", "*.html")):
    fail("4 states", "review/ exists in the production tree — review material "
                     "must never reach the public domain, noindex or not")


# 5 · legal pages carry real content
for slug, needle in (("privacy.html", "lawful basis"),
                     ("accessibility.html", "not good enough yet"),
                     ("terms.html", "Historical interpretation")):
    path = os.path.join(ROOT, slug)
    if not os.path.exists(path):
        fail("5 legal", f"{slug} missing")
        continue
    body = open(path, encoding="utf-8").read()
    if needle.lower() not in body.lower():
        fail("5 legal", f"{slug} does not contain approved content ({needle!r})")
    if len(re.sub(r"<[^>]+>", "", body)) < 1200:
        fail("5 legal", f"{slug} is too short to be a real notice")


# 6 · contact address is configured
if not B.SITE.get("contact_email"):
    fail("6 email", "SITE['contact_email'] is empty")
else:
    hits = [p for p in pages if B.SITE["contact_email"] in
            open(os.path.join(ROOT, p), encoding="utf-8").read()]
    if not hits:
        fail("6 email", "contact address appears on no page")
    else:
        warn("6 email", f"confirm {B.SITE['contact_email']} is monitored and that "
                        f"SPF, DKIM and DMARC pass — preflight cannot test delivery")


# 7 · the form is either genuinely connected or not rendered
contact = open(os.path.join(ROOT, "contact.html"), encoding="utf-8").read()
has_form = "<form" in contact
if has_form and not B.SITE.get("form_endpoint"):
    fail("7 form", "contact.html renders a form but SITE['form_endpoint'] is empty")
if B.SITE.get("form_endpoint") and not has_form:
    warn("7 form", "form_endpoint is set but no form is rendered")
if 'action="#"' in contact:
    fail("7 form", "contact form posts to '#'")


# 8 · every internal link and asset resolves
missing = set()
for page in pages:
    d = os.path.dirname(page)
    body = open(os.path.join(ROOT, page), encoding="utf-8").read()
    for url in re.findall(r'(?:href|src)="([^"]*)"', body):
        url = url.strip()
        # In-page, or not a repository path at all. A protocol-relative URL
        # (//fonts.example/x.css) is external too — it is not a local file, and
        # a startswith("http") test misses it.
        if (not url or url.startswith("#") or url.startswith("//")
                or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", url)):
            continue
        # A fragment and a query string both address the same file on disk.
        path_part = url.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        base = ROOT if path_part.startswith("/") else os.path.join(ROOT, d)
        target = os.path.normpath(os.path.join(base, path_part.lstrip("/")))
        if os.path.isdir(target):                 # a directory link resolves
            target = os.path.join(target, "index.html")   # through its index
        if not os.path.exists(target):
            missing.add(f"{page} → {url}")
for m in sorted(missing):
    fail("8 links", m)


# 9 · every video has controls, a poster and a transcript on the page
for page in pages:
    body = open(os.path.join(ROOT, page), encoding="utf-8").read()
    for tag in re.findall(r"<video[^>]*>", body):
        if "controls" not in tag:
            fail("9 video", f"{page}: <video> without controls")
        if "poster=" not in tag:
            fail("9 video", f"{page}: <video> without a poster")
        if "autoplay" in tag and "muted" not in tag:
            fail("9 video", f"{page}: autoplay without muted")
    # accessibility.html states that every film has a written transcript on the
    # same page. That is a promise to a visitor, so an unmet one fails the
    # build rather than warning about it.
    if "<video" in body and 'class="transcript"' not in body:
        fail("9 video", f"{page}: <video> with no transcript on the page — "
                        f"accessibility.html promises one beside every film")


# 10 · the standing editorial rules that are mechanically checkable
# CLAUDE.md lists rules that "must not break". The ones a script can actually
# test are tested here rather than trusted to memory.

# Navigation is five items, in this order.
EXPECTED_NAV = ["Explore", "Journeys", "Work With Us", "How We Work", "About"]
actual_nav = [label for _href, label in B.NAV]
if actual_nav != EXPECTED_NAV:
    fail("10 rules", f"navigation is {actual_nav}, expected {EXPECTED_NAV}")

# Vectis ONE appears exactly once per page, and is never a link.
for page in pages:
    body = open(os.path.join(ROOT, page), encoding="utf-8").read()
    n = body.count("Vectis ONE")
    if n != 1:
        fail("10 rules", f"{page}: 'Vectis ONE' appears {n} times, expected once")
    for anchor in re.findall(r"<a\b[^>]*>.*?</a>", body, re.S):
        if "Vectis ONE" in anchor:
            fail("10 rules", f"{page}: 'Vectis ONE' is inside a link; it must be unlinked")

# AI is claimed once on the homepage, in the trust panel, in a sentence whose
# subject is human responsibility.
#
# Provenance captions are exempt and are stripped first. "Evidence-led AI
# reconstruction" on a film is a required disclosure — the site's own rule is
# that a reconstruction is labelled wherever it appears — not a claim about the
# product. Counting it would set the labelling rule against the marketing rule
# and force one of them to be broken.
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
home_text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", home, flags=re.S | re.I)
home_text = re.sub(r'<(?:p|span|div)\s+class="[^"]*(?:video__caption|townhall-feature__provenance|method-panel__badge)[^"]*">.*?</(?:p|span|div)>', " ", home_text, flags=re.S)
home_text = re.sub(r"<[^>]+>", " ", home_text)
ai_hits = re.findall(r"(?<![A-Za-z])AI(?![A-Za-z])", home_text)
if len(ai_hits) != 1:
    fail("10 rules", f"homepage claims AI {len(ai_hits)} times outside provenance "
                     f"captions, expected once (in the trust panel, in a sentence "
                     f"whose subject is human responsibility)")

# The operator is named unambiguously, and never as the unrelated company.
for page in pages:
    body = open(os.path.join(ROOT, page), encoding="utf-8").read()
    if re.search(r"ISLE\s+CONNECT\s+LTD", body, re.I) and "not connected" not in body.lower():
        fail("10 rules", f"{page}: names ISLE CONNECT LTD without disclaiming it")


# 11 · a retired or withdrawn URL never comes back
# The sitemap is generated from the pages actually written, so a retired page
# can only reappear if someone recreates it or hand-links it. Both are caught
# here rather than discovered in a search index months later.
RETIRED_PATHS = [
    "explore/the-garlic-farm.html",
    "explore/darker-side-of-wight.html",
    "explore/bembridge-fort.html",
    "for-venues.html",
    "for-creators.html",
    "for-partners.html",
]
# Withdrawn outright rather than redirected: the page made a claim that was
# never agreed, so it must not exist, be linked, or be advertised to crawlers.
WITHDRAWN_PATHS = ["explore/the-garlic-farm.html"]

sitemap = ""
sitemap_path = os.path.join(ROOT, "sitemap.xml")
if os.path.exists(sitemap_path):
    sitemap = open(sitemap_path, encoding="utf-8").read()

for retired in RETIRED_PATHS:
    if os.path.exists(os.path.join(ROOT, retired)):
        fail("11 retired", f"{retired} exists again in the production tree")
    if retired in sitemap:
        fail("11 retired", f"{retired} is advertised in sitemap.xml")

for page in pages:
    body = open(os.path.join(ROOT, page), encoding="utf-8").read()
    for withdrawn in WITHDRAWN_PATHS:
        leaf = withdrawn.rsplit("/", 1)[-1]
        if re.search(r'(?:href|src)="[^"]*' + re.escape(leaf) + r'"', body):
            fail("11 retired", f"{page} links to withdrawn page {withdrawn}")


# ------------------------------------------------------------------ report
print()
for w in WARN:
    print("WARN  " + w)
if FAIL:
    print()
    for f_ in FAIL:
        print("FAIL  " + f_)
    print(f"\nPREFLIGHT FAILED — {len(FAIL)} blocking issue(s). Do not deploy.")
    sys.exit(1)

print(f"\nPREFLIGHT PASSED — {len(pages)} public pages, "
      f"{B.LIVE_COUNT} published stories, {len(WARN)} warning(s).")
print(f"""
  This proves the repository is internally consistent. It does NOT prove:

    · {B.SITE['contact_email']} exists, is monitored, and passes SPF/DKIM/DMARC
    · the legal pages have been read and approved by a person
    · the six retired URLs have been checked for traffic, indexing and QR codes

  Those are release gates and no script can check them. RELEASE-GATES.md has
  the checklist. Do not merge to main until it is complete.
""")
