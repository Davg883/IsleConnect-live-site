#!/usr/bin/env python3
"""
Write build-info.json — deployment identity only.

Standard library only, no dependencies, no site rebuild. Run as the deploy
build command so the served site can report which commit it is.

    python3 tools/build-info.py
"""

import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def commit():
    for var in ("VERCEL_GIT_COMMIT_SHA", "GITHUB_SHA", "CF_PAGES_COMMIT_SHA"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:                                         # noqa: BLE001
        return "unknown"


def environment():
    # Vercel sets "production" or "preview". Anything else is treated as
    # preview, so a preview can never claim to be production.
    env = (os.environ.get("VERCEL_ENV")
           or os.environ.get("IC_ENVIRONMENT") or "").lower()
    return env if env in ("production", "preview", "development") else "preview"


def published_story_count():
    """Counted from the registry without importing yaml — one line per record."""
    import glob
    import re
    n = 0
    for path in glob.glob(os.path.join(ROOT, "content", "stories", "*.yaml")):
        text = open(path, encoding="utf-8").read()
        if re.search(r"^status:\s*published\s*$", text, re.M):
            n += 1
    return n


info = {
    "commit": commit(),
    "builtAt": datetime.datetime.now(datetime.timezone.utc)
               .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "environment": environment(),
    "publishedStories": published_story_count(),
}

out = os.path.join(ROOT, "build-info.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)
    f.write("\n")

print(json.dumps(info))
sys.exit(0)
