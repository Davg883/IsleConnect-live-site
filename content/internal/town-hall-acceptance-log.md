# Town Hall / Re:Box — architectural acceptance log

**Never rendered.** The build reads `content/stories`, `content/collections` and
`content/partners`. It does not read this directory.

## What this is for

Town Hall is the first story to be published *through* the registry rather than
alongside it. Publishing it is therefore a test of a claim: that IsleConnect has
a publishing engine, and not a well-documented manual process.

Fill this in **while** publishing, not afterwards. The value is in what actually
happened, including the steps that felt too small to write down — those are
exactly the ones that quietly accumulate into an hour of work per story.

The publishing sequence is in `DEPLOY.md` under *Town Hall publishing sequence*.

## The distinction that matters

Not every manual step is a defect.

- **Editorial judgement** — a person deciding what deserves the homepage, how a
  story is framed, whether an image reads well. This should stay manual. Making
  it automatic would be worse, not better.
- **Mechanical synchronisation** — the same fact restated in a second place
  because nothing propagates it. Every instance is a future inconsistency, and
  it is the class of problem the registry exists to remove.

When a row is manual, say which of the two it is. That is the column that
decides whether anything needs building.

## The log

| Output | Automatic or manual | Should become automated? | Notes |
|---|---|---|---|
| Story page | | | |
| Collection listing | | | |
| Homepage feature | | | |
| Sitemap | | | |
| Social metadata | | | |
| QR destination | | | |
| Partner case study | | | |
| Live story count | | | |
| Journey membership | | | |
| Transcript | | | |

Two rows were added to the seven originally proposed: the live story count and
journey membership are both claimed to be record-driven today, so the log should
either confirm that or catch it being untrue.

## What the build does today

Recorded on 29 August 2026 at `85161c2`, so the log can be checked against a
prediction rather than a memory. If reality differs from this table, that
difference is itself a finding.

| Output | Expected today | Basis |
|---|---|---|
| Story page | **Automatic** | Rendering is driven by `status`; `published` produces the full page |
| Collection listing | **Automatic** | From the record's `collections:` field |
| Sitemap | **Automatic** | Generated from the pages actually written |
| Live story count | **Automatic** | `LIVE_COUNT` computed from the registry, never typed |
| Journey membership | **Automatic** | Same `collections:` field as the listing |
| Transcript | **Automatic** | `video_block()` emits it wherever the film appears |
| Homepage feature | **Manual** | `DEPLOY.md` step 5 — plausibly editorial judgement |
| Partner case study | **Manual** | `DEPLOY.md` step 6 |
| Social metadata | **Partly automatic, and wrong** | See below |
| QR destination | **Manual** | Nothing in `build.py` generates one |

### The social metadata defect

`og:title` and `og:description` are correctly per-page. **`og:image` is not.**
It is hardcoded to `assets/img/card-ryde140.jpg` in `head()`, so every one of
the 21 pages advertises the Ryde 140 card when shared — the wartime story, the
partner pages, the legal notices, all of them.

Records already carry a `media.poster` for stories that have one. The fix is to
use it where present and fall back to a site-wide default otherwise. It is small
and self-contained; it changes the head of every page, which is why it was not
folded into the release this log was written alongside.

Town Hall will make this visible: its share card will show Ryde 140 artwork for
a Re:Box story unless the fix lands first.

### QR destinations

There is no QR generation of any kind — `build.py` mentions QR only in the alt
text of a photograph. Destinations are decided and encoded by hand.

This matters more than it looks. A printed QR code cannot be corrected after it
is on a wall, so the destination URL is the one output where a mistake is
permanent. A record-driven destination, validated by preflight against the pages
actually built, would make it impossible to print a code pointing at a URL that
does not exist.

## After publication

For every row marked manual and mechanical, decide one of:

1. **Move it into the build** — it derives from a record and nothing else.
2. **Add a preflight check** — a person still decides, but the build refuses to
   ship an inconsistent result.
3. **Leave it, and say why** — genuine editorial judgement.

Record the decision here. A row left blank is a row that will be rediscovered
from scratch at the next story.

Completed by ____________________ on ____________
