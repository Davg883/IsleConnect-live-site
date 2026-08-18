# IsleConnect V1 — Asset Manifest

**Version 4.0 · 18 August 2026** — strategy frozen. Both films are in the build.

**This document is the files.** What must exist for a story to *go live* — the rules, the story unit, the package spec — now lives in `EXPERIENCE-MANIFEST.md`. The trail's nine stops live in `TRAIL-STOPS.md`.

> `puckpool-now.jpg` is an asset. **Puckpool = story + evidence + contributor + media + Stop 7 + nearby action + measurement** is the experience.

---

## What is already in

Both flagship videos are supplied, encoded for web, and live in the build. Nothing is blocking the homepage.

| File | Source | Size | Notes |
|---|---|---|---|
| `assets/video/victoria-arcade.mp4` | *Victoria arcade old to new Final.mp4* | 3.5 MB | 1080p, H.264, faststart. 20s. |
| `assets/video/victoria-arcade-720.mp4` | same | 1.2 MB | 720p variant for slow connections. |
| `assets/video/puckpool-battery.mp4` | *Puckpool Guns with intro.mp4* | 5.5 MB | 1080p, H.264, faststart. 22s. Re-encoded from 54 MB. |
| `assets/video/puckpool-battery-720.mp4` | same | 3.1 MB | 720p variant. |

WebM/VP9 versions sit alongside the MP4s (`victoria-arcade-720.webm`, `puckpool-battery-720.webm`) so playback works on Chromium builds without an H.264 decoder. MP4 is listed first so Safari and iOS still get it.

Posters pulled from those videos:

| File | Frame | Used for |
|---|---|---|
| `card-ryde140.jpg` | Arcade, c.1837 reconstruction @ 5.0s | Homepage flagship poster, Ryde 140 hero, OG image |
| `card-wartime.jpg` | AA crew scanning the sky @ 18.6s | Homepage flagship poster, Wartime Trail hero |
| `card-explore-ryde.jpg` | Present-day arcade @ 15.0s, cropped | For Partners hero, closing band |
| `hero-01.jpg` | Arcade reconstruction @ 6.5s, cropped | Homepage hero |
| `exp-victoria-arcade-hero.jpg` | = `card-ryde140` | Story page hero |
| `exp-puckpool-hero.jpg` | = `card-wartime` | Story page hero |

Then/Now pair — the homepage hero press-and-hold:

| File | Frame |
|---|---|
| `arcade-now.jpg` | Present-day façade @ 16.6s, cropped |
| `arcade-then.jpg` | c.1837 reconstruction @ 4.2s, same crop |

Both cut from the same locked-off camera in the film and cropped identically, so they register.

Also produced:

| File | Notes |
|---|---|
| `assets/img/isleconnect-mark.png` | 136 × 136 circle-masked lighthouse, cut from the Puckpool intro at 0.7s. **Placeholder for the vector.** |
| `favicon.ico` | Tab icon. 48/32/16 px, transparent corners, generated from the mark with a contrast lift so the tower survives at 16px. |
| `assets/img/favicon-32.png` | 32 px PNG for browsers that prefer it to the `.ico`. |
| `assets/img/apple-touch-icon.png` | 180 × 180 iOS home-screen icon, laid on navy — iOS composites transparency onto white otherwise. |

> **All three are derived from the placeholder PNG and inherit its ceiling.** At 16px the lighthouse is a suggestion rather than a shape. **Regenerate the whole set from the vector** the moment it arrives — a favicon is the one place where a 136px source is most obviously a 136px source.

> **Note on cropping.** `hero-01` and `card-explore-ryde` are cropped top and bottom to remove the videos' burned-in overlay labels, which clashed with the site header at full bleed. The card posters keep their labels deliberately — *"Evidence-led AI reconstruction · c.1837"* on screen is good product language and worth showing.

**Both encodes are wired in.** Homepage feature blocks serve the 720p files (smaller display, summary context); the dedicated story pages serve 1080p, where the film is the whole point.

---

## Priority 1 — what would most improve the site now

| ID | Ratio | Min size | Direction |
|---|---|---|---|
| **Logo vector** | — | SVG or AI | **Highest priority.** The header mark is currently a 136px PNG cut from the Puckpool intro frame and circle-masked. It reads correctly at 34px but will not survive a retina display or a print application. Supply the original vector. |
| **`puckpool-now.jpg`** | 16:9 | 1920 × 1080 | **Second, and cheap for the value.** A present-day still of the Puckpool emplacement from the same camera position as the film, so the wartime trail gets the Then/Now hold-to-reveal the Arcade already has. One visit, one tripod position. **Capture the viewpoint record** — `EXPERIENCE-MANIFEST.md` §4 — not just the frame. |
| `hero-01` (replacement) | ~3:1 wide crop | 2400 × 800 | See the hero brief below. |
| `portrait-royal-victoria-arcade` | 1:1 | 800 × 800 | Environmental portrait, on site. Brief in `EXPERIENCE-MANIFEST.md` §5. |
| `portrait-puckpool-battery` | 1:1 | 800 × 800 | Same, for the wartime trail. |

Once **both** flagship stories do Then/Now, visitors read it as an IsleConnect behaviour rather than a clever Arcade effect. That is why `puckpool-now.jpg` outranks new content.

### The hero brief

The current hero is a cropped video frame. It is elegant, and it reinforces heritage more than discovery.

The replacement should be **person + recognisable Ryde place + movement**. Someone walking up Union Street with the Arcade visible; visitors on the Esplanade with the town behind them. Not an empty architectural photograph — the site already carries the historic imagery, so the hero can do the human job: *this is something people go out and explore.*

It sits under a heavy navy scrim from the bottom — the **top two-thirds carries the image**.

---

## Crop set

Responsive cards, social and future feeds need more than one crop per story. Established now as naming, even where only the first is produced:

| Name | Ratio | Min size | Use |
|---|---|---|---|
| `storyname-16x9` | 16:9 | 1600 × 900 | Cards, posters, OG image |
| `storyname-4x5` | 4:5 | 1080 × 1350 | Mobile cards, social, feeds |
| `storyname-1x1` | 1:1 | 1080 × 1080 | Avatars, dense grids, map pins |

Not all three are needed immediately. The 4:5 is the one most likely to be wanted later and least likely to be recoverable — **frame with headroom to allow it.**

---

## Priority 2 — the next story nodes

Four "Coming soon" pages exist and are honest about their state. Each needs the full package in `EXPERIENCE-MANIFEST.md` §3 before it can go live:

| Node | Collection | Needs |
|---|---|---|
| Appley Tower | Wartime Trail | `card-appley-tower.jpg` + media |
| Ryde Pier | Wartime Trail | `card-ryde-pier.jpg` + media |
| Union Street | Ryde 140 | `card-union-street.jpg` + media |
| Seaview | Wartime Trail | `card-seaview.jpg` + media |

Posters 1600 × 900. Media 1920 × 1080 MP4 (H.264) or MP3, with a poster frame, a Then/Now pair, timed captions and a transcript.

**Five trail stops are still unnamed** — see `TRAIL-STOPS.md`. That is the single biggest content gap on the project, and it blocks the route map, distances, QR sequence, production order and print material.

---

## Moved to future pipeline

Not needed for V1. Do not commission.

`card-darker-side` · `card-garlic-farm` · MiniVox / Mokee Joe · Peter J. Murray material · Garlic Farm material · other destination and attraction imagery · partner logos · testimonial portraits

These return when there is an actual collaboration or agreed concept to publish. The homepage's *Beyond Ryde* band names the categories — books, attractions, other destinations — without naming any partner. That is deliberate and protects credibility.

---

## Copy still needed

Marked inline in the build with a `Copy needed` notice:

- **Contributor biographies and portraits** — for both live story pages.
- **About page, section 3** — who we work with. Three or four sentences.
- **Privacy, Accessibility and Terms** — all three are stubs. Privacy is a UK GDPR requirement and cannot ship empty.
- **Contact form handler** — not wired to anything. Connect it and add the GDPR consent line.

## Captions

Both films carry an on-page transcript, taken from their burned-in captions. The text is accurate. What is missing is timed `<track>` WebVTT files — cut those against the actual edit rather than estimating from frame sampling.

**From now on `captions.vtt` is standard film output**, not a post-production extra. See `EXPERIENCE-MANIFEST.md` §3.

## Settled — no longer open

- **Ryde 140** is a programme name. The site never states what "140" refers to, so 1836–1856 arcade content sits naturally.
- **Trail name** is *Ryde to Seaview Wartime Trail*, everywhere. "Wartime Coast" retired.
- **Stop numbering** is nine, from the film. Puckpool is Stop 7.
- **The lighthouse** is the IsleConnect trust mark.
- **Then/Now, onward action and claim status** are production rules, not options — `EXPERIENCE-MANIFEST.md` §1.

## Still to confirm

- **The five unnamed trail stops** — biggest content gap. `TRAIL-STOPS.md`.
- **The Dell Cafe** — is the partnership publishable? The `Nearby` block is built and flagged. Resolve early: it is the first real story → business demonstration, and the first directions number is worth more commercially than another film.
- **Distance and walking time** for Ryde → Seaview — route page figures are estimates, flagged as such. Unlocked by the five names.
- **Illustrative stats** on `partners/venues.html` — replace with real pilot numbers or remove.
