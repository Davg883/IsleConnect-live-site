#!/usr/bin/env python3
"""
Write build-info.json — deployment identity only.

This is the ONLY implementation. build.py calls this script rather than
carrying a second copy with its own defaults; a duplicate implementation with
opposite defaults is how a preview deployment came to be able to describe
itself as production.

No site rebuild: the HTML that ships is the HTML reviewed in the pull request.

    python3 tools/build-info.py
"""

import datetime
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml
except ImportError:                                           # pragma: no cover
    raise SystemExit(
        "\ntools/build-info.py needs PyYAML to count published stories.\n"
        "The count is parsed from the records, never pattern-matched out of\n"
        "the file text, so a malformed record fails loudly instead of being\n"
        "quietly counted wrong.\n\n"
        "    pip install -r requirements.txt\n")


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
    """Preview is the safe default. Production is never inferred — the platform
    has to state it, so nothing can accidentally claim to be live."""
    env = (os.environ.get("VERCEL_ENV")
           or os.environ.get("IC_ENVIRONMENT") or "").strip().lower()
    if env in ("production", "preview", "development"):
        return env
    return "preview"


def published_story_count():
    """Parsed from the records. A regex over the file text would miss a record
    whose status carries a trailing comment, and would happily count one that
    does not parse at all."""
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "stories", "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            rec = yaml.safe_load(f)
        if not isinstance(rec, dict):
            raise SystemExit(
                f"\ntools/build-info.py: {os.path.relpath(path, ROOT)} is empty "
                f"or is not a single record. Fix the record before deploying.\n")
        if rec.get("status") == "published":
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
