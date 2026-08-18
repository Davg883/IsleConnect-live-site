# IsleConnect — Design Language

**Version 1.0 · 18 August 2026**

The test of a design system is whether the product is identifiable with the logo hidden. These five behaviours are the answer — built out of what IsleConnect actually does, not bolted on.

> **Make IsleConnect feel like a beautifully designed modern field guide whose pages occasionally come alive.**
> Editorial rather than corporate. Place-led rather than technology-led. Historic without nostalgia. Digital without looking like software.
>
> **When you touch the site, the place changes.**

---

## 1. Then / Now — the signature interaction

**Built. Live on the homepage hero.**

The hero is the Royal Victoria Arcade as it stands today. Press and hold **Hold to see 1837** and the façade becomes the c.1837 reconstruction — three grand entrance arches, figures in the street. Release and today returns.

This is IsleConnect in one interaction. No explanation of AI, no architecture, no feature grid: the place you are looking at tells you its story.

**How it is built**

- Two plates, identically cropped from the same locked-off camera in the arcade film, so they register exactly. `assets/img/arcade-now.jpg` and `arcade-then.jpg`.
- A gold hairline sweeps across as the past arrives — the same engraved stroke as the story thread, used as a transition rather than a decoration.
- The control is a real `<button>`. Mouse and touch get press-and-hold; keyboard and screen-reader users get click-to-toggle, because you cannot "hold" a button with assistive technology. A click that merely follows a pointer gesture is swallowed so the two models never fight.
- `prefers-reduced-motion` removes the sweep and the pulse, and swaps instantly. The interaction still works.

**To extend it**, every future story needs a matched pair from the same camera position: *today* and *then*. That is now a production requirement, not a nice-to-have — Rule 1 in `EXPERIENCE-MANIFEST.md`, which also specifies the viewpoint record (GPS, camera height, focal length, bearing, pitch, time, reference still) that makes the position reproducible by someone else, years later.

> ⚠️ **Puckpool cannot do this yet.** The film is reconstruction throughout — there is no present-day plate of the emplacement from the same angle. One still, shot from where the camera sits in the film, unlocks Then/Now for the whole wartime trail. It is the cheapest high-value asset on the list.

---

## 2. The story thread

**Built.** `.thread`

A thin engraved line — part cartographic route, part contour, part pencil stroke from an archival drawing — runs between sections, with three small gold stops along it. It draws itself once as it scrolls into view, then stays.

It appears between the flagship films and *How it works*, inside the collections band, above the trail's stop list, and above *Go somewhere next* on every story page.

It says **stories connect places** without writing it down.

Deliberately not a glowing tech line. 1.4px, low-contrast, tactile. If it starts reading as decoration rather than connection, use it less.

---

## 3. Evidence marks

**Built.** `.marks` / `.mark`

Small letterpress-style labels that carry provenance as part of the visual language rather than as bureaucratic metadata:

`RECONSTRUCTION` · `SOURCE CHECKED` · `ARCHIVE` · `ON THIS SPOT` · `ORAL HISTORY`

Each has its own colour drawn from the palette — reconstruction in gold, source-checked in sage, archive in teal, on-this-spot in navy. They sit under the hero on every story page and beside stories in the Explore grid.

This is the trust section doing its work *inside* the content. The arcade film already does it on screen with *"Evidence-led AI reconstruction · c.1837"*; the marks extend that pattern to the whole site.

**Rule:** never apply a mark that isn't true. The moment one is decorative, all of them stop meaning anything.

---

## 4. Place typography

**Built.** `.placename` / `.placeband`

Location names set at 2.4–6.5rem in outlined display serif, running past both edges of the viewport and fading out at the margins — read as landscape rather than as a heading.

`RYDE — APPLEY — PUCKPOOL — SEAVIEW`

Used once on the homepage between the story network and the collections, and once on the trail page above the stops. Sparingly: it is a horizon line, not a headline.

---

## 5. Go somewhere next

**Built.** `.onward`

Story pages no longer end with a generic "related content" block. They end with:

> **You are standing in it.** *Now walk to the next one.*

— a story thread, and then the onward places. The next stop emerges rather than being listed.

---

## Editorial rhythm — breaking the three-card tell

Repeated evenly-spaced three-card rows are the clearest signature of generated design. Two sections were rebuilt to break it:

**Explore Ryde** is now asymmetric. Royal Victoria Arcade is a wide lead tile at 4 of 6 columns; Puckpool sits beside it at 2; the four in-development stories run beneath as catalogue fragments — rules, small type, no images, like entries in an archive index. It reads as a growing collection rather than a product grid.

**Beyond Ryde** is no longer three boxes. It is a typeset editorial list: display-serif category on the left, one line of explanation on the right, separated by hairlines. Less UI, more publication.

---

## Copy — write the picture, not the abstraction

Every story line was rewritten to put the reader somewhere:

| Before | After |
|---|---|
| Discover the guns that guarded the Solent. | **Stand where the guns watched the Solent.** |
| See how the entrance may have appeared in 1837. | **Stand in Union Street. See the Arcade as Ryde saw it in 1837.** |
| A familiar landmark with stories behind it. | **You've walked past Appley Tower. Now find out what you've been looking at.** |
| Where millions of Island journeys have begun. | **Walk out half a mile, then look back at the town.** |
| Buildings, people and stories hidden in plain sight. | **You walk it every week. Look up once.** |
| The wartime route continues east. | **The coast keeps going. So does the story.** |

The rule: the reader should not have to interpret anything. Give them a body position and a direction to look.

---

## Deliberately not doing

- **No mascots or characters.** The characters are the Arcade, the emplacement, the pier, the coastline and the people who lived there. A mascot would weaken that.
- **No movement for its own sake.** The site stays calm, trustworthy and rooted. Every animation here is either revealing evidence or connecting two places.
- **No parallax on the hero.** The hold-to-reveal is the interaction; adding drift on top would dilute it.

---

## Still for a designer

**Typography is the one thing not settled here.** The site currently pairs Playfair Display with Lato — attractive, and deliberately conventional so the custom behaviours carry the identity. The brief for Simon's designer:

- **Display serif** with editorial / nineteenth-century printing character, but not costume-Victorian.
- **Sans** modern, highly legible, neutral enough to make the historic face feel special.
- Target: *archive meets contemporary guide*, not *heritage museum website*.

Swap both in `:root` (`--font-display`, `--font-body`) and everything follows — the scale is fluid and nothing hard-codes a size.

Also for a designer: whether the story thread should be genuinely hand-drawn rather than a bezier curve. A real engraved or pencil stroke, traced and used as an SVG path, would be warmer than the geometric version built here. The mechanism is ready for it — replace `THREAD_PATH` in `build.py`.
