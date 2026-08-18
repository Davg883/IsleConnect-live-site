# IsleConnect — Experience Manifest

**Version 1.0 · 18 August 2026**

The Asset Manifest lists files. This lists **what must exist for a story to go live**.

`puckpool-now.jpg` is an asset.
**Puckpool = story + evidence + contributor + media + Stop 7 + nearby action + measurement** is the experience.

That distinction matters the moment someone other than the founder produces a territory. This document is the one they are given.

---

## 1. The three production rules

Locked. These are part of the content brief, not optional extras.

### Rule 1 — Every story ships a matched Then/Now pair

Shot or rendered from **one camera position**: *today* and *then*. Identically framed and cropped so the two plates register exactly.

Without the pair, a story cannot use the site's signature interaction, and Then/Now stops being an IsleConnect behaviour and goes back to being a clever Arcade effect. See §4 for the capture record.

> **Standing exception:** Puckpool is live without one. The film is reconstruction throughout. `puckpool-now.jpg` is the highest-value outstanding asset on the site after the vector logo, precisely because it closes this exception on the flagship wartime story.

### Rule 2 — Every story ends with one clear onward action

Next story, location, venue or route. **The site never ends in a dead end.**

One primary action, not a list. Built as `.onward` on story pages and `.nearby` where a real business relationship exists.

### Rule 3 — Every claim carries a status

Nothing on the site asserts without saying what kind of assertion it is.

| Status | Meaning | Mark |
|---|---|---|
| **Fact** | Documented, citable, verifiable | `SOURCE CHECKED` |
| **Source-backed reconstruction** | Built from evidence, rendered as an interpretation of it | `RECONSTRUCTION` |
| **Archive** | Reproduced original material | `ARCHIVE` |
| **Oral history** | Testimony, recorded and attributed | `ORAL HISTORY` |
| **Location** | This happened on this spot | `ON THIS SPOT` |
| **Interpretation** | Reasoned inference beyond what the sources state | *no mark yet* |
| **Fiction** | Story set in a real place, not a claim about it | *no mark yet* |

The arcade film already does this on screen — *"Evidence-led AI reconstruction · c.1837"* — and it is the strongest trust signal on the site.

> **Gap, not a task.** The last two rows have no visual mark because no interpretive or fictional content is published yet. When it arrives — the books strand is the likely first — the marks get designed then. **Do not publish interpretation or fiction under a mark that means something else.** The moment one mark is decorative, all of them stop meaning anything.

---

## 2. The story unit

A complete IsleConnect story is nine components. This is the product unit — everything else is packaging.

| # | Component | Live when |
|---|---|---|
| 1 | **Place** | Named, located, and reachable on foot |
| 2 | **Verified story** | Written, checked, and status-marked per Rule 3 |
| 3 | **Matched Then/Now pair** | Both plates registered from one viewpoint (Rule 1) |
| 4 | **Media** | Full package per §3 |
| 5 | **Contributor** | Named human, portrait, one-line credential (§5) |
| 6 | **Evidence** | `sources.md` — what was used, what was inferred |
| 7 | **Route position** | Stop number, or explicitly *to be confirmed* — never invented |
| 8 | **Next action** | One onward move (Rule 2) |
| 9 | **Measurement** | The three events below, firing |

**Measurement, per story:**

- opened the story
- continued to a second story
- requested directions to a nearby venue

Those three are the venue proposition in plain numbers. A story that publishes without them is unmeasurable and therefore commercially silent.

---

## 3. The film package

Every film ships as this set. Treat it as one unit — not a video with extras attached.

```text
video-1080.mp4
video-720.mp4
video-720.webm
poster.jpg
then.jpg
now.jpg
captions.vtt
transcript.txt
sources.md
rights.md
metadata.json
```

**Timed captions are standard output, not post-production.** WebVTT is cut against the actual edit, by whoever holds the timeline. Estimating timings from frame sampling afterwards costs more and reads worse.

**Crop set.** Responsive cards, social and future feeds need more than one crop. Establish the naming now even where only the first is produced:

| Name | Ratio | Min size | Use |
|---|---|---|---|
| `storyname-16x9` | 16:9 | 1600 × 900 | Cards, posters, OG image |
| `storyname-4x5` | 4:5 | 1080 × 1350 | **Mobile cards, social, feeds** |
| `storyname-1x1` | 1:1 | 1080 × 1080 | Avatars, dense grids, map pins |

The 4:5 is the one most likely to be wanted and least likely to be recoverable later — frame with headroom to allow it.

### `metadata.json`

Overly structured for two stories. By story 30 it is the reason the catalogue is still usable.

```json
{
  "id": "puckpool-battery",
  "title": "Puckpool Battery",
  "collection": "Ryde to Seaview Wartime Trail",
  "stop": 7,
  "stops_total": 9,
  "coordinates": { "lat": null, "lon": null, "captured": false },
  "period": { "from": 1863, "to": 1945, "primary": 1940 },
  "contributor": { "name": null, "role": null, "portrait": null },
  "status": "source-backed-reconstruction",
  "then_now": { "then": null, "now": null, "viewpoint_record": null },
  "onward": { "type": "venue", "target": "the-dell-cafe", "confirmed": false },
  "publication": "live",
  "updated": "2026-08-18"
}
```

`null` means *not captured yet* and is honest. **Never fill a coordinate from memory or an online estimate** — it comes from the capture record in §4 or it stays null.

---

## 4. The matched viewpoint record

"Same camera position" is not a reproducible instruction. Record all of it, at capture:

| Field | Why |
|---|---|
| **GPS position** | The return visit, and the map pin |
| **Camera height** | The single most commonly missed variable |
| **Focal length** (and equivalent) | Perspective compression must match, not just angle |
| **Bearing** | Which way the camera faced |
| **Pitch** | Up/down tilt — small errors are very visible in a hold-to-reveal |
| **Time and date** | Light and shadow direction on the return |
| **Reference still** | The frame to match against, in the field |

Store as `viewpoint.json` alongside the pair. This becomes more valuable the more people produce content — it is what lets someone re-shoot a plate in three years without the original crew.

---

## 5. Contributor portraits

These are not staff profile photographs. The portrait answers one question visually: **who knows this story?**

- Historian or venue person **standing where the story happened**
- Local contributor **with their archive material**
- Someone **physically pointing something out**
- Environmental framing with enough setting that the location is recognisable

That does the work of *Human checked* without another line of copy. A headshot against a wall does not.

1:1, 800 × 800 minimum. Also frame for the 4:5 crop.

---

## 6. Go-live checklist

A story publishes when all nine rows of §2 are true. Anything short of that publishes as **in development**, honestly labelled, with a contribution prompt — as the four unbuilt nodes do now.

The one thing never to do: fill a gap by inventing content that looks like the verified kind.

---

## Related

- `ASSET-MANIFEST.md` — the files, and what is still missing
- `TRAIL-STOPS.md` — the canonical nine-stop route record
- `DESIGN-LANGUAGE.md` — the five behaviours these rules protect
- `BUILD-SPEC.md` — decisions log and pre-launch list
