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


# 2 · prohibited content against every generated page on disk
B.guard(pages)


# 3 · every story and partner record is in a known state
for sid, st in B.REG["stories"].items():
    if st.get("status") not in {"draft", "research", "review", "approved",
                                "published", "archived", "blocked"}:
        fail("3 states", f"{sid}: unknown status {st.get('status')!r}")


# 4 · nothing non-published produced a page
for sid, st in B.REG["stories"].items():
    if st.get("status") in B.PUBLISHABLE:
        continue
    candidate = st["slug"] + ".html"
    if candidate in pages and candidate.replace(".html", "") not in B.SOON_SLUGS:
        fail("4 states", f"{sid} is {st['status']} but produced {candidate}")
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
    for url in re.findall(r'(?:href|src)="([^"#][^"]*)"', body):
        if url.startswith(("http", "mailto:", "#", "data:")):
            continue
        target = os.path.normpath(os.path.join(ROOT, d, url.split("#")[0]))
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
    if "<video" in body and "transcript" not in body.lower():
        warn("9 video", f"{page}: video present with no transcript on the page")


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
print("""
  This proves the repository is internally consistent. It does NOT prove:

    · hello@isleconnect.co.uk exists, is monitored, and passes SPF/DKIM/DMARC
    · the legal pages have been read and approved by a person
    · the six retired URLs have been checked for traffic, indexing and QR codes

  Those are release gates and no script can check them. RELEASE-GATES.md has
  the checklist. Do not merge to main until it is complete.
""")
