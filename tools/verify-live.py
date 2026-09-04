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
    3  access blocked — a protected deployment answered with its login flow
       and no bypass secret was configured. Nothing about the site was tested.

Protected previews
    A Vercel preview with Deployment Protection enabled answers every request
    with a 302 to vercel.com/sso-api before any of our configuration is
    reached. That is not a content failure and must never be reported as one.

    Set VERCEL_AUTOMATION_BYPASS_SECRET and the verifier sends it as the
    x-vercel-protection-bypass header on every request. The secret is never
    placed in a URL, never logged, and never printed: a query-string token
    would land in server logs, browser history and any error message that
    echoes the URL.
"""

import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_policy                                         # noqa: E402

# One policy, shared with the build guard, so a phrase blocked before a deploy
# is the same phrase blocked after it.
BANNED = content_policy.BANNED_PHRASES

# /build-info.json is deliberately NOT in this list. It is required only when a
# specific commit has to be confirmed — with --expect, or unless build identity
# has been switched off deliberately. See the identity step in main().
MUST_EXIST = [
    "/", "/explore.html", "/journeys.html", "/how-we-work.html",
    "/work-with-us.html", "/about.html", "/contact.html",
    "/privacy.html", "/accessibility.html", "/terms.html",
    "/ryde-140.html", "/wartime-trail.html",
    "/ryde/royal-victoria-arcade.html", "/ryde/puckpool-battery.html",
    "/robots.txt", "/sitemap.xml",
]

# Retired. Each must either be gone, or redirect to its recorded destination.
# It must never still serve the old page. See the redirect map in DEPLOY.md.
RETIRED = {
    "/explore/darker-side-of-wight.html": "/explore.html",
    "/explore/bembridge-fort.html":       "/explore.html",
    "/for-venues.html":                   "/partners/venues.html",
    "/for-creators.html":                 "/partners/creators.html",
    "/for-partners.html":                 "/work-with-us.html",
}

# Withdrawn, not moved. These must answer 404 or 410 and must NEVER redirect:
# a redirect tells a visitor and a search engine that the thing still exists
# somewhere in the programme, which is the claim being withdrawn.
GONE = {
    "/explore/the-garlic-farm.html":
        "described a partnership that was never agreed — withdrawn outright, "
        "not redirected, because redirecting to Explore implies it remains "
        "part of the programme",
    "/review/town-hall-rebox.html":
        "review material must never be public, redirect or otherwise",
}

# Text that proves an old page is still being served rather than redirected.
STALE_MARKERS = ["in development with the farm", "Darker Side of Wight",
                 "Bembridge Fort", "Bring your story to life"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


BYPASS_ENV = "VERCEL_AUTOMATION_BYPASS_SECRET"
BYPASS_HEADER = "x-vercel-protection-bypass"


def bypass_secret():
    """The protection-bypass secret, or None. Read at call time so a test can
    set it, and stripped so a trailing newline from a secret store cannot
    produce an invalid header value."""
    return (os.environ.get(BYPASS_ENV) or "").strip() or None


def request_headers():
    h = {"User-Agent": "isleconnect-verify/3"}
    secret = bypass_secret()
    if secret:
        # Header, never a query parameter: a token in the URL is written to
        # server logs, browser history, and any message that echoes the URL.
        h[BYPASS_HEADER] = secret
    return h


def redact(text):
    """Never let the secret reach stdout, an exception message, or CI logs."""
    secret = bypass_secret()
    if secret and text:
        return text.replace(secret, "***redacted***")
    return text


def is_protection_challenge(status, headers):
    """A protected deployment answers with a redirect into Vercel's SSO flow.
    That says nothing about the site's content."""
    if status not in (301, 302, 303, 307, 308):
        return False
    location = headers.get("Location", "") or ""
    return "vercel.com/sso-api" in location or "/.well-known/vercel/sso" in location


def fetch(url, follow=True):
    opener = (urllib.request.build_opener() if follow
              else urllib.request.build_opener(NoRedirect))
    req = urllib.request.Request(url, headers=request_headers())
    try:
        with opener.open(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except Exception as e:                                    # noqa: BLE001
        return None, redact(str(e)), {}


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
    ap.add_argument("--no-build-identity", action="store_true",
                    default=os.environ.get("IC_NO_BUILD_IDENTITY", "") not in ("", "0"),
                    help="build identity is switched off deliberately (no "
                         "buildCommand); skip the commit check and verify "
                         "content only")
    args = ap.parse_args()

    if args.no_build_identity and args.expect:
        print("--expect and --no-build-identity are contradictory: a commit "
              "cannot be confirmed without build identity.", file=sys.stderr)
        return 1

    base = args.base.rstrip("/")
    expect = args.expect
    if expect.upper() == "HEAD":
        expect = local_head() or ""

    print(f"Verifying {base}")
    if bypass_secret():
        print(f"  sending {BYPASS_HEADER} (secret from ${BYPASS_ENV})")

    # ---- 0 · can we reach the site at all? -------------------------------
    # A protected deployment answers everything with its login redirect. That
    # is an access problem, not a content problem, and reporting it as exit 1
    # would send someone hunting for a bug in a site nobody has seen.
    probe_status, _probe_body, probe_headers = fetch(base + "/", follow=False)
    if is_protection_challenge(probe_status, probe_headers):
        print(f"\nACCESS BLOCKED — {base} answered {probe_status} into Vercel's "
              f"login flow.")
        if bypass_secret():
            print(f"A {BYPASS_HEADER} header was sent but did not satisfy the "
                  f"deployment. Check that ${BYPASS_ENV} matches the value in "
                  f"Project Settings → Deployment Protection → Protection "
                  f"Bypass for Automation, and that it has been regenerated "
                  f"into this environment since it last changed.")
        else:
            print(f"No bypass secret is configured. Set ${BYPASS_ENV} to the "
                  f"value from Project Settings → Deployment Protection → "
                  f"Protection Bypass for Automation, or verify against an "
                  f"unprotected deployment such as production.")
        print("\nNothing about the site was tested. This is not a content "
              "failure.")
        return 3

    # ---- 1 · which commit is actually live -------------------------------
    # Exit 2 means "the deployment has not arrived". It must never be reported
    # as exit 1, which means "the content that IS deployed is wrong". Confusing
    # the two is exactly what this step exists to prevent.
    required = list(MUST_EXIST)
    deadline = time.time() + max(args.wait, 0)
    deployed = None

    if args.no_build_identity:
        print("  build identity disabled by request — verifying content only.")
    else:
        # Identity is served, so it is required to be present and correct.
        required = required + ["/build-info.json"]
        while True:
            status, body, _ = fetch(base + "/build-info.json")
            if status == 200:
                try:
                    import json
                    info = json.loads(body)
                    deployed = info.get("commit")
                    built = info.get("builtAt")
                    env = info.get("environment")
                except Exception:                             # noqa: BLE001
                    deployed, built, env = None, None, None
                if deployed:
                    print(f"  deployed commit {deployed[:12]}  built {built}"
                          f"  environment {env}")
                    if not expect or deployed.startswith(expect[:12]):
                        break
                    if time.time() >= deadline:
                        print(f"\nTIMED OUT — {base} is still serving "
                              f"{deployed[:12]}, expected {expect[:12]}.")
                        print("The deployment has not arrived yet. This is not "
                              "a content failure; re-run when it completes.")
                        return 2
                    print(f"  waiting for {expect[:12]} …")
                    time.sleep(args.interval)
                    continue
                if expect:
                    print("\nTIMED OUT — /build-info.json is being served but "
                          "carries no commit, so the deployed revision cannot "
                          f"be confirmed against {expect[:12]}.")
                    return 2
                break
            if status == 404:
                if time.time() < deadline and (expect or args.wait):
                    print("  /build-info.json not there yet, waiting …")
                    time.sleep(args.interval)
                    continue
                if expect:
                    print(f"\nTIMED OUT — {base}/build-info.json is still 404 "
                          f"after {args.wait}s, so the deployment serving "
                          f"{expect[:12]} has not arrived.")
                    print("If build identity is switched off deliberately, "
                          "re-run with --no-build-identity instead.")
                    return 2
                print("\n/build-info.json is absent and no commit was expected.")
                print("If that is deliberate, re-run with --no-build-identity "
                      "to verify content only. Treating it as a failure here, "
                      "because an unannounced missing identity file usually "
                      "means the build command did not run.")
                return 1
            if time.time() >= deadline:
                print(f"\nCould not read /build-info.json ({status}). The "
                      f"deployment cannot be identified.")
                return 2
            time.sleep(args.interval)

    fails, checked = [], 0

    # ---- 2 · pages that must exist and be clean --------------------------
    print()
    for path in required:
        status, body, _ = fetch(base + path)
        checked += 1
        if status != 200:
            fails.append(f"{path} returned {status}")
            print(f"  {status}  {path}")
            continue
        # Same policy and the same scanning surfaces as the build guard:
        # comments and attribute values included.
        for problem in content_policy.scan(body, path):
            fails.append(problem)
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
            if destination.rstrip("/") in location.rstrip("/"):
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

    # ---- 3b · withdrawn: gone outright, and never redirected ------------
    print()
    for path, why in GONE.items():
        status, body, headers = fetch(base + path, follow=False)
        checked += 1
        location = headers.get("Location", "")
        if status in (404, 410):
            print(f"  {status}  {path}   (withdrawn)")
        elif status in (301, 302, 307, 308):
            fails.append(f"{path} redirects to {location}, but it must be gone: {why}")
            print(f"  {status}  {path} -> {location}   <-- must not redirect")
        elif status == 200:
            fails.append(f"{path} is still being served, and it must be gone: {why}")
            print(f"  200  {path}   <-- still live")
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
