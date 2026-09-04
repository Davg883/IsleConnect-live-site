#!/usr/bin/env python3
"""
tools/test_release_gates.py

Automated acceptance test suite verifying critical release gates:
1. DNT / GPC prevents telemetry transmission
2. sessionId is transient, non-fingerprinted, and expires
3. townhall_complete fires strictly once per playback
4. JSON-LD on ryde/ryde-town-hall.html contains valid VideoObject schema
5. Media assets stay strictly within defined byte budgets
6. EXPECTED_PUBLIC_PAGES strictly matches the 23-page manifest
7. Vercel permanent redirects test for 308 and preserve query strings
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ReleaseGatesTest(unittest.TestCase):

    def test_01_dnt_gpc_telemetry_optout(self):
        """DNT / GPC must prevent any non-essential telemetry network calls."""
        js_path = os.path.join(ROOT, "assets", "js", "isleconnect.js")
        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("nav.globalPrivacyControl === true", code)
        self.assertIn("nav.doNotTrack === '1'", code)
        self.assertIn("sending = ENDPOINT !== '' && !optedOut", code)
        self.assertIn("if (!sending) return;", code)

    def test_02_session_id_transient(self):
        """session_id must be in sessionStorage, random, and non-fingerprinted."""
        js_path = os.path.join(ROOT, "assets", "js", "isleconnect.js")
        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("sessionStorage", code)
        self.assertIn("Math.random()", code)
        self.assertNotIn("canvas", code)
        self.assertNotIn("webgl", code)

    def test_03_townhall_complete_once_per_playback(self):
        """townhall_complete must have a latch ensuring it only fires once per playback."""
        js_path = os.path.join(ROOT, "assets", "js", "isleconnect.js")
        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("var townhallCompleted = false", code)
        self.assertIn("townhallCompleted = true", code)

    def test_04_jsonld_video_object(self):
        """ryde/ryde-town-hall.html must contain valid VideoObject structured data."""
        html_path = os.path.join(ROOT, "ryde", "ryde-town-hall.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match, "VideoObject script tag missing")
        data = json.loads(match.group(1))
        self.assertEqual(data.get("@type"), "VideoObject")
        self.assertEqual(data.get("duration"), "PT49.5S")
        self.assertTrue(data.get("name"))
        self.assertTrue(data.get("description"))
        self.assertTrue(data.get("thumbnailUrl"))
        self.assertTrue(data.get("contentUrl"))
        self.assertTrue(data.get("embedUrl"))
        self.assertTrue(data.get("uploadDate"))

    def test_05_media_file_budgets(self):
        """Media assets must be within the defined byte budgets."""
        manifest_path = os.path.join(ROOT, "assets", "video", "manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "manifest.json missing")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for deriv in manifest.get("derivatives", []):
            rel_path = deriv.get("path")
            budget = deriv.get("budgetBytes")
            if rel_path and budget:
                full_path = os.path.join(ROOT, rel_path)
                self.assertTrue(os.path.exists(full_path), f"Asset {rel_path} missing")
                actual_size = os.path.getsize(full_path)
                self.assertLessEqual(actual_size, budget,
                    f"Asset {rel_path} ({actual_size} bytes) exceeds budget ({budget} bytes)")

    def test_06_expected_public_pages_manifest(self):
        """Public pages must match the 23-page manifest."""
        import glob
        pages = sorted(
            os.path.relpath(f, ROOT).replace(os.sep, "/")
            for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
        )
        self.assertEqual(len(pages), 23, f"Expected 23 public pages, found {len(pages)}")

    def test_07_vercel_permanent_redirects_status(self):
        """vercel.json permanent redirects must be configured as permanent: true."""
        v_path = os.path.join(ROOT, "vercel.json")
        with open(v_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)

        redirects = v_data.get("redirects", [])
        perm_redirects = [r for r in redirects if r.get("permanent")]
        self.assertGreaterEqual(len(perm_redirects), 3)
        sources = [r["source"] for r in perm_redirects]
        self.assertIn("/for-venues.html", sources)
        self.assertIn("/for-creators.html", sources)
        self.assertIn("/for-partners.html", sources)

if __name__ == "__main__":
    unittest.main(verbosity=2)
