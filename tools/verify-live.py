#!/usr/bin/env python3
"""
IsleConnect — post-deployment verification.

Runs against the live domain, never the local build. It first confirms which
commit is actually deployed, so it can tell three different things apart:

    the new deploy failed
    the new deploy has not arrived yet
    the new deploy is fine

Usage
    python3 tools/verify-live.py
    python3 tools/verify-live.py --expect HEAD           # wait for local HEAD
    python3 tools/verify-live.py --expect <sha> --wait 600
    python3 tools/verify-live.py --base https://isleconnect-git-branch.vercel.app

Exit codes
    0  verified
    1  a real failure — content is wrong, or a retired page still serves
    2  timed out waiting for the expected commit (deploy not arrived)
"""

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

BANNED = [
    "Copy needed", "Not wired up", "Content needed before launch",
    "Wording check needed", "Confirm before launch", "Illustrative figures",
    "TODO", "FIXME", "Lorem ipsum", "BUILD-SPEC", "ASSET-MANIFEST",
]

MUST_EXIST = [
    "/", "/explore.html", "/journeys.html", "/how-we-work.html",
    "/for-partners.html", "/about.html", "/contact.html",
    "/privacy.html", "/accessibility.html", "/terms.html",
    "/ryde-140.html", "/wartime-trail.html",
    "/ryde/royal-victoria-arcade.html", "/ryde/puckpool-battery.html",
    "/robots.txt", "/sitemap.xml", "/build-info.json",
]

# Retired. Each must either be gone, or redirect to its recorded destination.
# It must never still serve the old page. See the redirect map in DEPLOY.md.
RETIRED = {
    "/explore/the-garlic-farm.html":      "/explore.html",
    "/explore/darker-side-of-wight.html": "/explore.html",
    "/explore/bembridge-fort.html":       "/explore.html",
    "/for-venues.html":                   "/partners/venues.html",
    "/for-creators.html":                 "/partners/creators.html",
    "/work-with-us.html":                 "/for-partners.html",
    # Review material must never be public, redirect or otherwise.
    "/review/town-hall-rebox.html":       None,
}

# Text that proves an old page is still being served rather than redirected.
STALE_MARKERS = ["in development with the farm", "Darker Side of Wight",
                 "Bembridge Fort", "Bring your story to life"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, follow=True):
    opener = (urllib.request.build_opener() if follow
              else urllib.request.build_opener(NoRedirect))
    req = urllib.request.Request(url, headers={"User-Agent": "isleconnect-verify/2"})
    try:
        with opener.open(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except Exception as e:                                    # noqa: BLE001
        return None, str(e), {}


def local_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:                                         # noqa: BLE001
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get(
        "IC_BASE_URL", "https://www.isleconnect.co.uk"))
    ap.add_argument("--expect", default=os.environ.get("IC_EXPECT_COMMIT", ""),
                    help="commit SHA the deployment must be serving, or HEAD")
    ap.add_argument("--wait", type=int, default=int(os.environ.get("IC_WAIT", "300")),
                    help="seconds to wait for that commit (default 300)")
    ap.add_argument("--interval", type=int, default=15)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    expect = args.expect
    if expect.upper() == "HEAD":
        expect = local_head() or ""

    print(f"Verifying {base}")

    # ---- 1 · which commit is actually live -------------------------------
    deadline = time.time() + max(args.wait, 0)
    deployed = None
    while True:
        status, body, _ = fetch(base + "/build-info.json")
        if status == 200:
            try:
                import json
                info = json.loads(body)
                deployed = info.get("commit")
                built = info.get("builtAt")
            except Exception:                                 # noqa: BLE001
                deployed, built = None, None
            if deployed:
                print(f"  deployed commit {deployed[:12]}  built {built}")
                if not expect or deployed.startswith(expect[:12]):
                    break
                if time.time() >= deadline:
                    print(f"\nTIMED OUT — {base} is still serving "
                          f"{deployed[:12]}, expected {expect[:12]}.")
                    print("The deployment has not arrived yet. This is not a "
                          "content failure; re-run when the deploy completes.")
                    return 2
                print(f"  waiting for {expect[:12]} …")
                time.sleep(args.interval)
                continue
            break
        if status == 404:
            if expect and time.time() < deadline:
                print("  /build-info.json not there yet, waiting …")
                time.sleep(args.interval)
                continue
            print("  /build-info.json absent — the deployed build predates "
                  "build identity. Continuing with content checks only.")
            break
        if time.time() >= deadline:
            print(f"\nCould not read /build-info.json ({status}). Aborting.")
            return 2
        time.sleep(args.interval)

    fails, checked = [], 0

    # ---- 2 · pages that must exist and be clean --------------------------
    print()
    for path in MUST_EXIST:
        status, body, _ = fetch(base + path)
        checked += 1
        if status != 200:
            fails.append(f"{path} returned {status}")
            print(f"  {status}  {path}")
            continue
        visible = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for phrase in BANNED:
            if phrase in visible:
                fails.append(f"{path} still contains {phrase!r}")
        if "<form" in body and 'action="#"' in body:
            fails.append(f"{path} serves a form posting to '#'")
        print(f"  200  {path}")

    # ---- 3 · retired pages: gone, or redirected — never still serving ----
    print()
    for path, destination in RETIRED.items():
        status, body, headers = fetch(base + path, follow=False)
        checked += 1
        location = headers.get("Location", "")
        if status in (301, 302, 307, 308):
            if destination is None:
                fails.append(f"{path} redirects but review material must be gone")
                print(f"  {status}  {path} -> {location}   <-- must not exist")
            elif destination.rstrip("/") in location.rstrip("/"):
                print(f"  {status}  {path} -> {location}")
            else:
                fails.append(f"{path} redirects to {location}, expected {destination}")
                print(f"  {status}  {path} -> {location}   <-- wrong destination")
        elif status in (404, 410):
            print(f"  {status}  {path}   (gone)")
        elif status == 200:
            if any(m in body for m in STALE_MARKERS):
                fails.append(f"{path} is STILL SERVING THE OLD PAGE — "
                             f"the deploy did not remove it")
                print(f"  200  {path}   <-- old content still live")
            else:
                fails.append(f"{path} returns 200; expected a redirect or 404")
                print(f"  200  {path}   <-- should be gone or redirected")
        else:
            fails.append(f"{path} returned {status}")

    print()
    if fails:
        for f in fails:
            print("FAIL  " + f)
        print(f"\nLIVE VERIFICATION FAILED — {len(fails)} issue(s) "
              f"across {checked} checks against {base}.")
        return 1

    print(f"LIVE VERIFICATION PASSED — {checked} checks against {base}"
          + (f" at commit {deployed[:12]}." if deployed else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
