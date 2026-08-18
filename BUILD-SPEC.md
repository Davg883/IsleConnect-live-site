# IsleConnect V1 — Build Specification

**Version 3.0 · 18 August 2026 · STRATEGY FROZEN**
Built around the two products that exist: **Ryde 140** and the **Ryde to Seaview Wartime Trail**.

From this version, changes should be execution quality, not strategy.

**Companion documents.** `EXPERIENCE-MANIFEST.md` — the production standard a story must meet to go live. `ASSET-MANIFEST.md` — the files. `TRAIL-STOPS.md` — the canonical nine-stop route record. `DESIGN-LANGUAGE.md` — the five behaviours that make the site identifiable with the logo hidden.
`MEASUREMENT.md` — the anonymous behavioural event layer.

---

## 1. Decisions log — settled, do not reopen

| # | Decision | Applied |
|---|---|---|
| 1 | **The lighthouse becomes the IsleConnect trust mark.** Vectis ONE stays as the underlying technical name. | Mark sits beside the wordmark in header and footer. Extracted from the Puckpool intro; **replace with the vector original.** |
| 2 | **Ryde 140 is a programme name, not a date range.** The site never states what "140" refers to. | *"A growing collection exploring Ryde's buildings, people and stories across the centuries."* This lets 1836–1856 arcade content sit naturally without implying it belongs to an 1887 event. |
| 3 | **Nine stops is the canonical trail system**, taken from the film's "Stop 7 of 9". | Puckpool is fixed at Stop 7. Unconfirmed stops read *"Stop number to be confirmed"* rather than being invented. Website, QR codes, films and print must all use this system. |
| 4 | **One trail name: "Ryde to Seaview Wartime Trail."** "Wartime Coast" is retired. | Used in the H1, page title, meta, and every reference. Nav shows "Wartime Trail" as a length-driven abbreviation of the same name — not an alternative one. |
| 5 | **The Dell Cafe becomes the first story→business demonstration.** | A `Nearby` module on the Puckpool page, carrying a visible confirm-before-launch notice. |
| 6 | **Hero says "Ryde", not "the town."** | *"Explore the stories, places and people that shaped Ryde — then discover where to go next."* Reinforces location for visitors arriving from search or a QR code. |

### Positioning

> **IsleConnect brings Ryde's stories to life — helping people discover the history, places and businesses around them.**
>
> **Ryde is where we are proving the model. The same approach can later bring books, attractions and destinations to life.**

### The two products

| | Ryde 140 | Ryde to Seaview Wartime Trail |
|---|---|---|
| **Shape** | Place exploration | Journey exploration |
| **Sells as** | "Bring your history and people to life" | "Commission a connected journey" |
| **Lead asset** | Royal Victoria Arcade, c.1837 | Puckpool Battery, Stop 7 of 9 |

### Language

Visitor-facing: **stories** and **trails**. "Experience" stays internal and commercial.

---

## 2. Design tokens

`:root` in `assets/css/isleconnect.css`.

```
--navy       #16243D    --ivory       #F4EFE7    --gold   #C89B3C
--navy-deep  #0F1A2D    --ivory-deep  #EDE5D9    --teal   #1F7A80
--navy-soft  #23375A    --white       #FFFFFF    --sage   #4E9E7E
```

> ⚠️ Sampled by eye from the deck PDF. Replace with true values from the master slides.

Playfair Display + Lato via Google Fonts with full system fallbacks. Fluid `clamp()` scale. **Self-host before launch.**

---

## 3. Pages — 19 files

| File | Purpose | Nav |
|---|---|---|
| `index.html` | Homepage, eight bands | — |
| `explore.html` | All story nodes | ✓ Explore Ryde |
| `ryde-140.html` | Collection page | ✓ Ryde 140 |
| `wartime-trail.html` | Route page, canonical stop numbering | ✓ Wartime Trail |
| `ryde/royal-victoria-arcade.html` | **Live** — video, transcript, sources | — |
| `ryde/puckpool-battery.html` | **Live** — video, transcript, Nearby, sources | — |
| `ryde/appley-tower.html` · `ryde-pier` · `union-street` · `seaview` | In development, with contribution prompt | — |
| `for-partners.html` | Landing, branches three ways | ✓ For Partners |
| `partners/venues.html` | Venues — includes the measurement example | — |
| `partners/creators.html` · `organisations.html` | Other two routes | — |
| `about.html` · `contact.html` | | ✓ About |
| `privacy` · `accessibility` · `terms` | Stubs — **required before launch** | footer |

Nav is five items. Contact sits in the mobile menu, footer and every CTA.

`build.py` generates all 19. Edit there, run `python3 build.py`.

---

## 4. Homepage bands — frozen order

| # | Band | Answers |
|---|---|---|
| 1 | Hero — *Bring Ryde to life* | Where am I? |
| 2 | Two flagship films | What can I actually do? |
| 3 | Discover. Experience. Go. | How does it work? |
| 4 | Explore Ryde — six nodes | Is there more? |
| 5 | Collections | How do they connect? |
| 6 | For local venues | What's in it for my business? |
| 7 | Trust | Why believe it? |
| 8 | Beyond Ryde | What else could this be? |

Visitor question first, commercial question second. Band 3 closes on *"The digital experience is there to help you discover more of the real place."*

Bands 2 and 5 both cover the collections deliberately: **band 2 shows the product**, **band 5 shows the curation**.

**Band 8 names categories only.** No partner names until there is a publishable agreement.

---

## 5. Components

| Class | Component |
|---|---|
| `.brand__mark` | Lighthouse trust mark, 34px header / 30px footer |
| `.video` / `.video__caption` | Player with the evidence label in the caption bar |
| `.features` / `.feature` | Two-up flagship blocks |
| `.nodes` / `.node--soon` | Story grid, quieter "in development" state |
| `.route` | Numbered trail stops |
| `.nearby` | **Story → nearby business.** The commercial behaviour to measure. Also reused as the contribution prompt on in-development pages. |
| `.transcript` | Collapsible transcript under each video |
| `.stats` | Illustrative partner reporting — clearly labelled as an example |
| `.benefit` · `.beyond` | Partner benefits; future categories (quietest component on the site) |

---

## 6. Performance and playback

- **Video is `preload="none"`** — nothing downloads until a visitor presses play. Posters carry the pages.
- **Two encodes per film.** Homepage feature blocks serve the **720p** files (smaller display, summary context); dedicated story pages serve **1080p**, where the video is the whole point. Puckpool came in at 54 MB and 19.7 Mbps; it is now 5.5 MB / 3.1 MB.
- `playsinline` set — iOS plays in place rather than hijacking fullscreen.
- All images carry explicit `width`/`height` (no layout shift), `decoding="async"`, `fetchpriority="high"` on heroes and `loading="lazy"` below the fold.
- **Transcripts are on the page**, not just burned into the video. Outdoors, in wind, people read.

**Remaining performance work:** self-host fonts, serve WebP with JPG fallback, and add `<track>` WebVTT caption files. The transcript text is already accurate — the VTT needs timing, which should be cut against the actual edit rather than estimated.

---

## 7. Accessibility

Skip link · semantic landmarks · gold `:focus-visible` outlines · `aria-current` on the active nav item · mobile nav with `aria-expanded`, Escape-to-close and focus return · `prefers-reduced-motion` respected · contrast passes WCAG AA (ivory/navy ≈ 12.5:1, gold on navy ≈ 6.2:1) · video controls native and keyboard-operable · transcripts on both films.

**Still to do:** real alt text on supplied imagery, `<track>` caption files, and a written accessibility statement.

---

## 8. Before launch

**Blocking:**

1. Replace the extracted PNG mark with the vector original — and regenerate `favicon.ico`, `favicon-32.png` and `apple-touch-icon.png` from it
2. Write Privacy — legal requirement
3. Wire the contact form; add the GDPR consent line
4. Confirm the remaining five trail stops
5. Confirm or remove the The Dell Cafe block, and wire "Get directions" to a real map link
6. Confirm or remove the illustrative stats on `partners/venues.html`
7. Remove every remaining `.notice` block

**Recommended:**

8. Self-host fonts · 9. True brand hex values · 10. Contributor bios and portraits · 11. Accessibility statement · 12. WebVTT captions · 13. WebP conversion
14. **Test standing at Puckpool, on a phone, on 4G.** That is the actual use case, and no desktop test substitutes for it.

**Analytics — built, and off by default.** The thirteen-event layer from the Vectis ONE concept is now wired into every page and sends nothing until `EVENTS_ENDPOINT` is set in `build.py`. See `MEASUREMENT.md`. Report these three first, because they are the venue proposition in plain numbers:

- people who opened a story
- people who continued to a second story
- people who requested directions to a nearby venue

That is exactly the shape shown on `partners/venues.html`. Ship the measurement and the sales pitch writes itself.

---

## 9. Still open

1. **The vector logo file** — the header currently uses a 136px PNG extracted from the Puckpool intro frame. Good enough to look right; not good enough to ship.
2. **Five unnamed trail stops** — the numbering system is now canonical, the content is not. Tracked in `TRAIL-STOPS.md`, which also holds the eight-field record every stop needs.
3. **The Dell Cafe agreement** — is it publishable? The first real story → business demonstration, and the first directions number is worth more commercially than another film.
4. **Contributor bios and portraits** for both live stories.
5. **Hosting and domain.**
