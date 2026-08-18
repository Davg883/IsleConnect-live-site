# IsleConnect — Measurement

**Version 1.0 · 18 August 2026**

The commercial engine. A venue conversation is won with *"94 people continued to another stop"*, not with a description of the idea. This is how that number gets produced.

Built into `assets/js/isleconnect.js`. No library, no third party, no tag manager.

---

## 1. Off by default, and genuinely off

The layer instruments every page but **sends nothing** until an endpoint is configured:

```python
# build.py
EVENTS_ENDPOINT = ""      # empty = inert
```

Set it to a collector URL, rebuild, and every page gets `<meta name="ic-events" content="…">`. Until then:

- no network request is made
- **no storage is written** — not a cookie, not a `sessionStorage` key
- events accumulate in `window.IsleConnect.events` so the instrumentation can be checked in a browser console

Add `?ic-debug=1` to any URL to log events as they fire.

That default is deliberate. Privacy copy is still a stub, and analytics storage needs a lawful basis under UK GDPR/PECR before it starts. **Write the privacy section before setting the endpoint** — not after.

## 2. What it never collects

No names, emails, addresses, IP addresses or device fingerprints. No cross-site identifier. No cookie of any kind.

The only identifier is a random `sessionStorage` value the browser discards when the tab closes — enough to distinguish *one visitor opened three stories* from *three visitors opened one each*, and useless for anything beyond that. It is written **only** when sending is switched on.

`navigator.doNotTrack` and Global Privacy Control are honoured before anything else runs.

## 3. The vocabulary — thirteen events, fixed

Carried over unchanged from the Vectis ONE concept so the website, the trail app and any future backend report in the same words. A fourteenth event is a deliberate decision, not a convenience — the layer silently drops anything not on this list.

| Event | Fires when | Wired |
|---|---|---|
| `page_opened` | any page loads | automatic |
| `story_started` | a visitor presses play | automatic, `.video video` |
| `story_completed` | the film reaches the end | automatic |
| `stop_selected` | a trail stop or onward story is clicked | automatic, `.route a` · `.onward a` · `.feature__stops a` |
| `trail_selected` | a collection is opened | `data-ic-event` |
| `nearby_places_viewed` | the Nearby block is actually seen | automatic, 40% visible |
| `worked_example_viewed` | the partner stat row is seen | automatic, 40% visible |
| `directions_clicked` | **Get directions** is pressed | `data-ic-event` |
| `sponsor_enquiry` | a partner CTA is pressed | `data-ic-event` |
| `map_opened` · `offer_opened` · `menu_clicked` · `booking_clicked` | — | reserved; no such control exists yet |

The last four are in the vocabulary but fire nowhere. That is correct: the contract is defined once, and controls adopt it as they get built, via `data-ic-event="…"`.

## 4. Context comes from the page

`build.py` writes the context onto `<body>`, and the layer walks up the tree to find it:

```html
<body data-ic-page="story" data-ic-story="puckpool-battery"
      data-ic-trail="wartime-trail" data-ic-stop="7">
```

So an event arrives already knowing which story, trail and stop number it belongs to:

```json
{
  "type": "story_started",
  "page": "story",
  "storyId": "puckpool-battery",
  "trailId": "wartime-trail",
  "stopId": "7",
  "sessionStoryCount": 2,
  "timestamp": "2026-08-18T18:32:30.500Z"
}
```

`sessionStoryCount` is the one that matters commercially. `2` means this visitor continued to a second story — the behaviour the whole network exists to produce.

## 5. The three numbers to report first

From `BUILD-SPEC.md` §8, now actually derivable:

| Number | Derived from |
|---|---|
| People who opened a story | count of `story_started` |
| People who continued to a second story | `story_started` where `sessionStoryCount >= 2` |
| People who requested directions to a nearby venue | count of `directions_clicked` |

That is exactly the shape shown on `partners/venues.html`. Ship the measurement and the sales pitch writes itself.

> ⚠️ **`directions_clicked` is not yet honest.** The button still points at `contact.html` because no map link has been agreed for The Dell Cafe. The event fires on a real click and the intent is real, but until the href is wired to an actual map the number counts *interest in directions*, not directions given. Fix the href before quoting it to a venue. `BUILD-SPEC.md` §8 item 5.

## 6. Adding an event to a new control

```html
<a href="…" data-ic-event="offer_opened">See today's offer</a>
```

Nothing else. The layer picks it up by delegation, so controls added after page load work too.

## 7. Verified

Checked in a browser against the built site: `page_opened`, `story_started` (with full story/trail/stop context), `stop_selected`, `trail_selected` and `directions_clicked` all fire correctly, and no storage is written while the endpoint is empty.

`nearby_places_viewed` and `worked_example_viewed` are visibility-triggered and could not be exercised in that environment — `IntersectionObserver` callbacks are not delivered to a browser pane that is not compositing, which also stopped the pre-existing story-thread animation from running. **Confirm those two by hand on a real device**, alongside the phone test in `BUILD-SPEC.md` §8 item 14.

---

## Related

- `EXPERIENCE-MANIFEST.md` §2 — measurement is component 9 of a complete story
- `BUILD-SPEC.md` §8 — the three numbers, and the pre-launch list
- `partners/venues.html` — the reporting shape a venue is shown
