#!/usr/bin/env python3
"""
Tests for the protection-bypass behaviour of tools/verify-live.py.

Standard library only, no test framework, so it runs anywhere the verifier
runs.  Every case is served by a local HTTP server — nothing touches a real
deployment.

    python3 tools/test_verify_live.py
"""

import http.server
import importlib.util
import io
import os
import socket
import sys
import threading
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = "s3cret-bypass-value-do-not-log"

# verify-live.py has a hyphen, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location(
    "verify_live", os.path.join(HERE, "verify-live.py"))
verify_live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify_live)

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


@contextlib.contextmanager
def env(**kw):
    """Set environment variables for the duration of a block."""
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def server(handler_cls):
    port = free_port()
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler_cls)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()


class RecordingHandler(http.server.BaseHTTPRequestHandler):
    """Records every request it receives. Header names are lowercased because
    HTTP header names are case-insensitive and urllib sends them capitalised
    ('X-Vercel-Protection-Bypass'), which a case-sensitive lookup would miss."""
    seen = []          # list of {"headers": {lowercased}, "line": request line}

    def do_GET(self):
        RecordingHandler.seen.append({
            "headers": {k.lower(): v for k, v in self.headers.items()},
            "line": self.requestline,
        })
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html>ok</html>")

    def log_message(self, *a):
        pass


class ProtectedHandler(http.server.BaseHTTPRequestHandler):
    """Mimics Vercel Deployment Protection: everything 302s into the SSO flow
    unless the bypass header carries the right secret."""
    def do_GET(self):
        if self.headers.get(verify_live.BYPASS_HEADER) == SECRET:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html>real content</html>")
            return
        self.send_response(302)
        self.send_header("Location",
                         "https://vercel.com/sso-api?url=%2F&nonce=abc")
        self.send_header("x-robots-tag", "noindex")
        self.end_headers()

    def log_message(self, *a):
        pass


# ---------------------------------------------------------------- the tests

def test_header_sent_when_secret_set():
    RecordingHandler.seen = []
    with env(VERCEL_AUTOMATION_BYPASS_SECRET=SECRET), server(RecordingHandler) as base:
        verify_live.fetch(base + "/")
    sent = RecordingHandler.seen[-1]["headers"] if RecordingHandler.seen else {}
    check("bypass header is sent when the secret is set",
          sent.get(verify_live.BYPASS_HEADER) == SECRET,
          f"got {sent.get(verify_live.BYPASS_HEADER)!r}")


def test_header_absent_when_no_secret():
    RecordingHandler.seen = []
    with env(VERCEL_AUTOMATION_BYPASS_SECRET=None), server(RecordingHandler) as base:
        verify_live.fetch(base + "/")
    sent = RecordingHandler.seen[-1]["headers"] if RecordingHandler.seen else {}
    check("no bypass header when no secret is configured",
          verify_live.BYPASS_HEADER not in sent)


def test_secret_never_in_url():
    """The whole point of using a header: a token in the request target ends up
    in server logs, browser history and any message that echoes the URL."""
    RecordingHandler.seen = []
    with env(VERCEL_AUTOMATION_BYPASS_SECRET=SECRET), server(RecordingHandler) as base:
        verify_live.fetch(base + "/explore.html")
    lines = [r["line"] for r in RecordingHandler.seen]
    check("secret never appears in the request target",
          lines and all(SECRET not in line for line in lines),
          "; ".join(lines))


def test_secret_redacted_from_messages():
    with env(VERCEL_AUTOMATION_BYPASS_SECRET=SECRET):
        msg = verify_live.redact(f"connection failed for {SECRET} at host")
    check("secret is redacted from error text",
          SECRET not in msg and "***redacted***" in msg, msg)


def test_whitespace_stripped():
    with env(VERCEL_AUTOMATION_BYPASS_SECRET=f"  {SECRET}\n"):
        check("secret is stripped of surrounding whitespace",
              verify_live.bypass_secret() == SECRET)


def test_blank_secret_treated_as_absent():
    with env(VERCEL_AUTOMATION_BYPASS_SECRET="   "):
        check("blank secret is treated as absent",
              verify_live.bypass_secret() is None)


def test_protection_challenge_detected():
    ok = verify_live.is_protection_challenge(
        302, {"Location": "https://vercel.com/sso-api?url=%2F"})
    not_ours = verify_live.is_protection_challenge(
        307, {"Location": "/explore.html"})
    plain = verify_live.is_protection_challenge(404, {})
    check("SSO redirect is recognised as a protection challenge", ok)
    check("an ordinary site redirect is not a protection challenge", not not_ours)
    check("a 404 is not a protection challenge", not plain)


def run_main(base, **envkw):
    """Run main() against base, capturing stdout, and return (exit, output)."""
    argv = sys.argv
    out = io.StringIO()
    sys.argv = ["verify-live.py", "--base", base, "--no-build-identity"]
    try:
        with env(**envkw), contextlib.redirect_stdout(out):
            code = verify_live.main()
    finally:
        sys.argv = argv
    return code, out.getvalue()


def test_protected_without_secret_exits_3():
    with server(ProtectedHandler) as base:
        code, out = run_main(base, VERCEL_AUTOMATION_BYPASS_SECRET=None)
    check("protected preview without a secret exits 3, not 1", code == 3,
          f"exit {code}")
    check("access-blocked output says nothing was tested",
          "ACCESS BLOCKED" in out and "not a content failure" in out)


def test_protected_with_secret_gets_through():
    """With the right secret the protection layer is passed. The run then
    fails on content (this fake serves the same stub for every path), which is
    the point: it reached the site and judged it, rather than exiting 3."""
    with server(ProtectedHandler) as base:
        code, out = run_main(base, VERCEL_AUTOMATION_BYPASS_SECRET=SECRET)
    check("with the secret, the run is no longer access-blocked",
          code != 3 and "ACCESS BLOCKED" not in out, f"exit {code}")
    check("the secret is never printed in the output", SECRET not in out)


def test_unprotected_behaviour_unchanged():
    """An ordinary deployment with no secret configured behaves exactly as
    before: it proceeds to content checks rather than exiting 3."""
    with server(RecordingHandler) as base:
        code, out = run_main(base, VERCEL_AUTOMATION_BYPASS_SECRET=None)
    check("unprotected verification is unaffected by this change",
          code != 3 and "ACCESS BLOCKED" not in out, f"exit {code}")


if __name__ == "__main__":
    print("verify-live protection-bypass tests\n")
    for fn in (test_header_sent_when_secret_set,
               test_header_absent_when_no_secret,
               test_secret_never_in_url,
               test_secret_redacted_from_messages,
               test_whitespace_stripped,
               test_blank_secret_treated_as_absent,
               test_protection_challenge_detected,
               test_protected_without_secret_exits_3,
               test_protected_with_secret_gets_through,
               test_unprotected_behaviour_unchanged):
        fn()

    print()
    if FAILURES:
        for f in FAILURES:
            print("FAILED  " + f)
        print(f"\n{len(FAILURES)} test(s) failed.")
        sys.exit(1)
    print("All tests passed.")
