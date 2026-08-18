# Ryde to Seaview Wartime Trail — canonical route record

**Version 0.1 · 18 August 2026 · FOUR OF NINE KNOWN**

The master source for website, films, QR codes and print. Nothing about the trail should be numbered anywhere until it is numbered here.

**Nine stops is canonical**, taken from the film's *"Stop 7 of 9"*. Puckpool is fixed at Stop 7. Everything else below is either confirmed or explicitly open — no stop number is invented to fill a row.

> **This is the biggest strategic content task on the project**, above everything except the vector logo and `puckpool-now.jpg`. Until the nine are locked, the trail is visually real and structurally incomplete: no route map, no distance, no walking time, no QR sequence, no production order, no venue conversations, no transport discussion, no printable trail material. All of those unlock the day this table is finished.

---

## Master table

| # | Public name | Location | Status | Then/Now | Media | Nearby |
|---|---|---|---|---|---|---|
| 1 | **unnamed** | — | — | — | — | — |
| 2 | **unnamed** | — | — | — | — | — |
| ? | Ryde Pier | Ryde Esplanade / pier head | not started | none | none | Esplanade venues |
| ? | Appley Tower | Appley Park, Ryde | not started | none | none | Appley beach kiosks |
| 3 | **unnamed** | — | — | — | — | — |
| 4 | **unnamed** | — | — | — | — | — |
| 5 | **unnamed** | — | — | — | — | — |
| **7** | **Puckpool Battery** | Puckpool Park, off Puckpool Hill | **live** | **missing — Priority 1** | 1080p + 720p + WebM | **The Dell Cafe — permission unresolved** |
| ? | Seaview | Seaview village | not started | none | none | Seaview venues |

Four public names exist. Three of them have no stop number. **Five stops have no name at all.**

**Ordering inference, not a decision:** the route runs west to east, so Ryde Pier and Appley Tower fall below 7, and Seaview falls above it. That constrains the puzzle; it does not solve it. Do not publish a number on that basis.

---

## Per-stop record

Every stop gets these eight fields. A stop is "locked" when all eight are answered — including *none* as an honest answer.

```text
Stop number
Public name
Exact location            postcode / what3words / GPS
Story hook                one line, body position + direction to look
Evidence / source status  fact · reconstruction · archive · oral history · interpretation
Then/Now availability      pair exists / plate needed / not possible
Media status              none · scripted · shot · edited · published
Nearby place or business  the onward action, and whether it is agreed
```

---

## Stop 7 — Puckpool Battery *(the worked example)*

| Field | Value |
|---|---|
| **Stop number** | 7 of 9 — **confirmed**, from the film |
| **Public name** | Puckpool Battery |
| **Exact location** | Puckpool Park, off Puckpool Hill, Ryde — GPS to be captured on site, not looked up |
| **Story hook** | *Stand where the guns watched the Solent.* |
| **Evidence status** | Source-backed reconstruction — Victorian battery re-armed with high-angle AA weaponry in the 1940 crisis |
| **Then/Now** | **Plate needed.** Film is reconstruction throughout. One tripod position, one visit, one still — see `EXPERIENCE-MANIFEST.md` §4 |
| **Media** | Published — 1080p / 720p MP4, 720p WebM, poster. Transcript on page; WebVTT outstanding |
| **Nearby** | **The Dell Cafe.** Module built, confirm-before-launch notice showing. **Unresolved.** |

### Why The Dell Cafe is worth resolving this week

If the permission is genuine it is worth more than another piece of content, because it is the first real demonstration of the actual IsleConnect mechanism — **story → nearby** — rather than a description of it.

The Puckpool page then says something very simple:

> **Nearby** — Continue your walk at The Dell Cafe · `Directions`

And then it gets measured. **That first real directions number matters more commercially than another film.** It is the number a venue conversation starts from.

---

## Leads from the earlier concept build

Material recovered from the previous Next.js prototype (`isleconnect/public/media`). **None of this is confirmed and none of it is published as fact.** It is recorded here because it is the only existing evidence of how the route was being numbered and named before the current system was frozen.

### A numbering conflict, not a correction

The signage mockup now shown on `for-partners.html` reads:

> **YOU ARE NEAR STOP 5** — Puckpool Pay Office: The Shrapnel Incident

That contradicts the canonical system in two ways at once, and the contradiction is informative:

- **It says Stop 5, and the film says Stop 7.** The film is the source of the canonical numbering, so the film wins. The mockup is treated as earlier draft artwork and captioned as such on the page.
- **It says "Puckpool Pay Office", which is not "Puckpool Battery".** These may be two different places on the same site. If so, the Pay Office is a **candidate name for one of the five unnamed stops** — and "The Shrapnel Incident" is a story hook that someone, at some point, had a source for.

**Action:** ask whoever produced the signage artwork where the Stop 5 numbering and the Pay Office name came from. That single question may resolve two of the nine slots.

### The Dell Cafe may itself be a wartime site

`dell-cafe-ww2.png` in the old build is a black-and-white reconstruction of a low pavilion-style building captioned **"HMS MEDINA — PORT DEPOT NO. 3"**, with blast-taped windows, sandbags and a despatch rider's motorcycle. The filename ties it to The Dell Cafe — the venue already built into the Puckpool page's `Nearby` block.

If that is evidenced, the commercial mechanism and the story become the same thing: the nearby venue *is* a stop. That would be the strongest possible demonstration of story → nearby.

**It is not published.** HMS Medina and a numbered port depot are checkable claims, and nothing goes on the site under a reconstruction mark without a source behind it. Verify first, then decide whether The Dell Cafe is a venue, a stop, or both.

---

## Stops 1–6, 8, 9 — the working brief

For whoever names them:

- The film is the primary source. If it names or shows stops, those names win.
- A stop must be **standable** — somewhere a visitor can physically be, on the walking route, with something to look at.
- A stop needs a story that survives Rule 3: something can be said about it with a status attached.
- Proximity to a venue is a tiebreak, not a criterion. The trail is not a shopping route.
- Five names, then eight fields each. That is the whole task.

Once locked, this file drives: the route page numbering, QR sequence, production order, distance and walking time (currently estimates, flagged as such on the route page), and the printed trail.

---

## Related

- `EXPERIENCE-MANIFEST.md` — what must exist before any of these go live
- `ASSET-MANIFEST.md` — the files
- `BUILD-SPEC.md` §1.3 — the numbering decision
