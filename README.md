# IsleConnect — V1 site

Static site. No build step, no framework, no dependencies.

## Run it

Open `index.html` in a browser.

For a local server (better for video):

```bash
python3 -m http.server 8000
```

Then visit http://localhost:8000

## What this version is

Re-centred on the two things that exist today:

- **Ryde 140** — Royal Victoria Arcade, evidence-led reconstruction c.1837
- **Wartime Trail** — Ryde to Seaview, Puckpool Battery

Both videos are in the build and play on the homepage. Garlic Farm, Peter J. Murray and other use cases are demoted to a *Beyond Ryde* band that names categories, not partners.

## Files

```
index.html                  homepage, eight bands
explore.html                all story nodes
ryde-140.html               collection page
wartime-trail.html          route page with numbered stops
ryde/*.html                 six story pages (2 live, 4 coming soon)
for-partners.html           partner landing
partners/*.html             venues / creators / organisations
about.html  contact.html
privacy / accessibility / terms    stubs — content required

assets/css/isleconnect.css  design system, tokens in :root
assets/js/isleconnect.js    sticky header + mobile nav
assets/video/               two flagship films, 1080p + 720p
assets/img/                 posters pulled from those films

build.py                    regenerates all 19 pages
BUILD-SPEC.md               designer/developer reference
DESIGN-LANGUAGE.md          the five visual behaviours that make it IsleConnect
ASSET-MANIFEST.md           the files — what's in, what's still needed
EXPERIENCE-MANIFEST.md      what must exist for a story to go live
TRAIL-STOPS.md              canonical nine-stop route record
MEASUREMENT.md              the anonymous event layer, and how to switch it on
```

## Editing

Header, footer, copy and page structure all live in `build.py`. Edit there, then:

```bash
python3 build.py
```

## The design language

Five behaviours make the site identifiable with the logo hidden: Then/Now, the story thread, evidence marks, place typography, and go-somewhere-next. See `DESIGN-LANGUAGE.md`.

The one to try first: open the homepage and press and hold **Hold to see 1837** on the hero.

## Producing a new story

`ASSET-MANIFEST.md` is the files. `EXPERIENCE-MANIFEST.md` is the standard: three production rules
(matched Then/Now pair, one onward action, a status on every claim), the nine components of a story
unit, and the film package that ships with each one.

## Before launch

See `BUILD-SPEC.md` §8 — five blocking items, seven recommended, six open questions.
