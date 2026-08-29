# IsleConnect — deployment

The live site is `https://www.isleconnect.co.uk`, served from this repository.
Nothing reaches the public until it is committed and pushed here.

---

## Release gates

`RELEASE-GATES.md` lists what preflight cannot prove — the mailbox, the legal
pages, and the retired-URL checks. **All of it must be ticked before merging
to `main`.** A green preflight is not a release decision.

## Build identity and determinism

`build-info.json` carries the commit, build time, environment and published
story count. Because it contains a timestamp it is **gitignored, not
committed** — otherwise every rebuild would show as drift and the
committed-output check would be meaningless.

It is generated at deploy time. `vercel.json` sets:

```
buildCommand: python3 tools/build-info.py
outputDirectory: .
```

Vercel installs `requirements.txt` itself, before the build command runs — the
deploy log shows `Installing dependencies … + pyyaml`. **Do not add a `pip
install` to the build command.** That environment is managed by `uv`, so pip
refuses to write to it (PEP 668, `externally-managed-environment`) and the
deploy fails. Declaring the dependency in `requirements.txt` is the whole job.

`tools/build-info.py` is the **only** implementation of `build-info.json`.
`build.py` calls this script rather than carrying its own copy: two
implementations with different defaults is precisely how a preview deployment
could come to describe itself as production.

It writes the identity file and nothing else — **it does not rebuild the
site**. That is deliberate:

- the HTML that ships is exactly the HTML reviewed in the pull request, not a
  rebuild that might differ from it
- `VERCEL_ENV` decides the `environment` field, and anything unrecognised falls
  back to `preview`. Production is never inferred — the platform has to state
  it, so a preview cannot claim to be live.
- `publishedStories` is parsed from the YAML records. It is not pattern-matched
  out of the file text, which would miss a record whose status carries a
  trailing comment and would happily count one that does not parse at all.

Parsing needs PyYAML, which is why it is in `requirements.txt`. A malformed
record now fails the deploy instead of silently producing a wrong count.

The committed HTML staying authoritative is what the `checks.yml` drift test
enforces: if the records and the committed pages disagree, CI fails on the
branch, before anything deploys. That test reports newly generated but
uncommitted pages as well as changed and deleted ones — a new page that was
never committed would otherwise deploy while CI stayed green.

> **Fallback.** If the build step fails on the preview for any reason, remove
> `buildCommand` and `outputDirectory` from `vercel.json`. The site serves the
> committed HTML exactly as before and `/build-info.json` is simply absent.
> Verification then has to be told that this is deliberate:
>
> ```
> python3 tools/verify-live.py --no-build-identity
> ```
>
> Without that flag a missing `/build-info.json` is treated as a failure,
> because an unannounced missing identity file almost always means the build
> command did not run.

## Once, before the first run

```bash
pip install -r requirements.txt      # PyYAML, to read content/
```

## The gate — never push straight to `main`

Vercel is connected to this repository, so a push to `main` changes the live
site. Work on a branch, review the Vercel preview, then merge.

```bash
git switch -c remediation/structured-publishing

python3 tools/preflight.py                 # must exit 0
python3 -m http.server 8000                # look at it locally

git add -A && git commit -m "..." && git push -u origin HEAD
# open the PR, review the Vercel preview deployment, then merge

# after the production deploy completes:
python3 tools/verify-live.py --expect HEAD --wait 600
```

`--expect HEAD` makes the live check wait for *your* commit to be the one
being served, so it can tell "the deploy failed" from "the deploy has not
arrived yet". Without it the check races Vercel and fails a good build.

### Two workflows, deliberately separate

`.github/workflows/checks.yml` — runs on every push and pull request. Registry
validation, publication-state gates, prohibited content, link resolution, video
controls, and a check that the committed HTML still matches the records.
Everything operates on the checked-out branch; nothing touches the live domain,
so nothing here can race a deployment.

`.github/workflows/verify-production.yml` — **not** run on push. It fires on
`deployment_status` once a production deployment reports success, or manually
via *Run workflow*. It confirms the deployed commit first, then checks content.

> **What CI can and cannot prevent.** Vercel deploys from the branch as soon as
> it is pushed. A failing check is a red cross **after** the site has changed.
> It catches the mistake; only `preflight.py` run locally before you push, and
> merging through a PR rather than pushing to `main`, actually prevent it.

### What preflight checks

| # | Check |
|---|---|
| 1 | Production build succeeds — registry validation and content guard included |
| 2 | No prohibited phrase on any generated page |
| 3 | Every story and partner record is in a known state |
| 4 | Every record produced exactly what its status permits — `published` a full page, `research` the reduced "in development" page, everything else nothing at all — and `review/` does not exist in the tree |
| 5 | Privacy, Accessibility and Terms contain real content, not stubs |
| 6 | A contact address is configured and appears on the site |
| 7 | The contact form is either genuinely connected or not rendered at all |
| 8 | Every internal link and asset resolves |
| 9 | Every video has controls and a poster, and no autoplay with sound |
| 10 | The mechanical editorial rules from `CLAUDE.md`: five navigation items in order, Vectis ONE once per page and unlinked, AI claimed once on the homepage outside provenance captions, and the operator never confused with ISLE CONNECT LTD |

### What verify-live checks

Runs against the **live domain**, not the local build.

1. Reads `/build-info.json` and reports which commit is actually deployed.
   With `--expect`, it waits (bounded) for that commit before judging anything.
2. Every page that should exist returns 200 and carries no prohibited phrase.
3. Every retired URL is either gone or redirects to its recorded destination —
   and is never still serving the old page. A stale page answering 200 is
   exactly how the last two releases went unnoticed.

Exit codes: `0` verified · `1` a real failure · `2` the deployment has not
arrived yet · `3` access blocked. Those are different things and the script
says which.

### Verifying a protected preview

A Vercel preview with Deployment Protection enabled answers **every** request
with a 302 into `vercel.com/sso-api` before any of this repository's
configuration is reached. A browser session gets through because it carries a
Vercel login cookie; a standalone script does not inherit that.

Untreated, this looks like a site-wide failure. It is not — nothing about the
site was tested. The verifier detects the SSO redirect and exits **3**, with a
message saying so.

To verify a protected preview from a terminal or CI, set the automation bypass
secret from *Project Settings → Deployment Protection → Protection Bypass for
Automation*:

```powershell
$env:VERCEL_AUTOMATION_BYPASS_SECRET = "<value from Vercel>"
py tools/verify-live.py --base https://<preview-host> --no-build-identity
```

The verifier sends it as the `x-vercel-protection-bypass` header on every
request. It is **never** put in a URL: a token in a query string is written to
server logs, browser history, and any error message that echoes the URL. The
value is redacted from the script's own output.

In CI the value comes from the `VERCEL_AUTOMATION_BYPASS_SECRET` repository
secret. It is not needed for production, which is unprotected — with no secret
set, no header is sent and behaviour is unchanged.

`python3 tools/test_verify_live.py` covers this: that the header is sent only
when configured, that the secret never reaches a URL or the output, that a
protected preview exits 3 rather than 1, and that ordinary unprotected
verification is unaffected. It runs in `checks.yml` on every push.

> **Note:** it needs outbound network access. It runs in CI and on your machine.
> An environment without outbound access cannot run it at all; verify from a
> machine or a CI runner that can reach the public internet.

---

## Steps 10–15, by hand

10. Push to `main`.
11. Open the production domain and look at it — not the local preview.
12. `python3 tools/verify-live.py`.
13. Send one controlled test to `david@isleconnect.co.uk`.
14. Confirm it arrives (check Gmail **and** Outlook, and the spam folder) and
    that nothing sensitive is written to any log.
15. Record the version and date below.

| Date | Version | Notes |
|---|---|---|
| | | |

---

## Retired pages — delete these from the repository

These were live and should not have been. They are the pre-Ryde build, and
`the-garlic-farm.html` publicly described a partnership as *"in development
with the farm"* — exactly what the site's own rules forbid.

```
explore/bembridge-fort.html
explore/darker-side-of-wight.html
explore/the-garlic-farm.html
for-venues.html
for-creators.html
work-with-us.html
```

Already staged for deletion in this change. `verify-live.py` will fail while any
of them still answers 200, so a partial deploy cannot pass silently.

### Redirect map — decision recorded

`vercel.json` carries these. Renamed service pages redirect to their new
homes; retired project pages land on Explore rather than 404, because a
printed QR code or a shared link may still point at one.

| Retired URL | Destination | Why |
|---|---|---|
| `/for-venues.html` | `/partners/venues.html` | Renamed, same purpose — 301 |
| `/for-creators.html` | `/partners/creators.html` | Renamed, same purpose — 301 |
| `/work-with-us.html` | `/for-partners.html` | Renamed, same purpose — 301 |
| `/explore/the-garlic-farm.html` | **none — must 404** | Described a partnership that was never agreed. Withdrawn, not moved. |
| `/explore/darker-side-of-wight.html` | `/explore.html` **(307)** | Retired project page. Temporary until traffic, indexing and QR destinations are checked. |
| `/explore/bembridge-fort.html` | `/explore.html` **(307)** | Same |
| `/review/*` | none — must 404 | Review material is never public |

The three renamed service pages use permanent redirects (301) because they are
straightforward renames.

The two remaining project pages use **temporary redirects (307)** deliberately:
a 301 is cached aggressively by browsers and intermediaries and is painful to
reverse. Once traffic, indexing and any printed QR destinations have been
checked, change `"permanent": false` to `true`, or remove the redirect so the
URL is gone.

**The Garlic Farm page is different, and deliberately so.** It has no redirect
at all. Redirecting it to Explore would tell a visitor — and a search engine
choosing a canonical URL — that the page still belongs somewhere in the
programme. It does not: it made a claim about a partnership that was never
agreed, and the honest response is withdrawal rather than relocation. A 307
would additionally have kept the old URL in the search index, since a temporary
redirect tells Google to retain the original.

> **Why 404 and not 410.** 410 is the more precise status, but `vercel.json`
> cannot express it. Its `redirects` property only emits redirect codes; the
> legacy `routes` property can set an arbitrary status but cannot be combined
> with `redirects`, `headers`, `cleanUrls` or `trailingSlash`, all of which
> this config uses. The remaining route would be a serverless function, which
> means adding a runtime to a deliberately static site for one dead URL.
> Google treats 404 and 410 almost identically for removal — 410 is marginally
> faster — so the cost is a few days of crawl latency, recovered by the Search
> Console removal recorded in `RELEASE-GATES.md` §3b.

`verify-live.py` enforces the distinction: retired URLs may redirect or be
gone, but a **withdrawn** URL must answer 404 or 410 and must never redirect.
`tools/preflight.py` step 11 additionally fails the build if a retired page
reappears in the tree or the sitemap, or if any page links to a withdrawn one.

**Before merging, check** whether any of the six were shared, indexed, or
printed on a QR code. If one carries real traffic, that changes its destination.
Record the outcome in `RELEASE-GATES.md`.

---

## Email

Creating the mailbox is not the whole job:

- inbox monitored, and forwarding works if used
- replies send **from** the IsleConnect domain
- SPF, DKIM and DMARC all configured and passing
- a test message reaches both Gmail and Outlook without landing in spam
- retention and deletion practice matches what `privacy.html` says

---

## Publication states

| State | Production domain |
|---|---|
| `draft` | Excluded |
| `research` | Excluded — the public "in development" page is a separate thing |
| `review` | Excluded. Private preview only |
| `approved` | Excluded until a publication decision |
| `published` | Included |
| `archived` | Only where intentionally retained |
| `blocked` | Excluded |

`review` is deliberately not "publish with noindex". `noindex` asks a search
engine not to list a page; it does not stop anyone with the URL from opening it.
Rights-pending media does not go on a public URL. The Town Hall record is
`blocked` and produces no page at all — a 404 there is the correct state until a
protected preview deployment exists.

---

## Town Hall publishing sequence

When the five gates in `content/stories/town-hall-rebox.yaml` clear:

1. Set `status: approved` and clear `blockedBy`.
2. Final factual, rights and accessibility check.
3. Set `status: published`.
4. `python3 build.py` — the page, the collection entry, the sitemap entry and
   the live story count all follow from the record.
5. Add the featured-story band to the homepage.
6. Add it as the organisational case study on the partner pages.
7. Generate the QR destination and verify it against the production URL.
8. Add captions, transcript, poster and social image.
9. Record the version above.

The live count is computed:

```python
LIVE_COUNT = len([s for s in REG["stories"].values() if s["status"] == "published"])
```

It is never typed by hand again.
