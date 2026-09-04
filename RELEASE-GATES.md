# Release gates — the things no script can check

`tools/preflight.py` proves the repository is internally consistent. It cannot
prove any of the following. Each needs a person to confirm it, and the date
recorded here, before this reaches production.

## 1 · Mailbox

Four public pages point at `david@isleconnect.co.uk` the moment this merges:
Contact, Privacy, Accessibility and Terms.

- [ ] Mailbox exists
- [ ] Incoming mail confirmed by test
- [ ] Outgoing replies send **from** the IsleConnect domain
- [ ] SPF configured and passing
- [ ] DKIM configured and passing
- [ ] DMARC configured and passing
- [ ] Test delivered to Gmail — not in spam
- [ ] Test delivered to Outlook — not in spam
- [ ] Named person monitoring it: ______________________
- [ ] Retention period decided, and it matches `privacy.html`

Confirmed by ____________________ on ____________

## 2 · Legal pages read and approved

Generated, not approved. Read each against how you actually operate.

`privacy.html` states:

- [ ] Who the data controller is
- [ ] How to contact them
- [ ] What the contact process collects
- [ ] Purpose and lawful basis
- [ ] Which service processes the email
- [ ] Retention periods — matching the mailbox decision above
- [ ] Whether analytics or cookies are used (the measurement layer is inert
      until `EVENTS_ENDPOINT` is set — if you set it, this copy must change first)
- [ ] User rights
- [ ] How to complain, correct or delete

`terms.html` reflects:

- [ ] Historical content may include labelled interpretation
- [ ] Route information can change
- [ ] Visitors remain responsible for their own safety
- [ ] Third-party venues and links are independent
- [ ] IP ownership and permitted reuse
- [ ] No unapproved partnership is implied

`accessibility.html`:

- [ ] The "what is not good enough yet" section is still accurate

- [ ] **Proper legal review obtained before any large public launch**

Confirmed by ____________________ on ____________

## 2b · Accessibility claims

The page describes what has been built and what has been checked. It does not
claim WCAG 2.2 conformance, and it must not until someone has actually tested
against it. Confirm every statement on the page is true of the site as built:

- [ ] Keyboard operation walked on each page type — home, explore, journeys,
      collection, published story, in-development story, partner, legal
- [ ] Visible focus outline on every interactive element
- [ ] Skip link present and working
- [ ] Text and interface colours checked against AA contrast ratios, with the
      figures recorded somewhere they can be re-checked
- [ ] Page reflows to one column, and text resizes to 200% without loss
- [ ] `prefers-reduced-motion` honoured
- [ ] The press-and-hold reveal also works as a plain toggle
- [ ] Every film has a transcript on the same page
- [ ] The limitations list is complete and current — no audit, no screen-reader
      testing, burned-in captions, no speech-input/magnification/switch testing

If a box cannot be ticked, the sentence that claims it comes off the page before
merge. Understating what has been verified is always the safer error.

- [ ] Independent audit scheduled, or a decision recorded not to commission one
      yet, and why

Confirmed by ____________________ on ____________

## 2c · Privacy copy matches behaviour

`privacy.html` currently states that **no** usage or analytics data is
collected, because `EVENTS_ENDPOINT` in `build.py` is empty and the measurement
layer sends nothing.

- [ ] `EVENTS_ENDPOINT` is still empty, and the page still says so
- [ ] No third-party script, font, or embed on any page makes a request that
      would contradict "we transmit no record of the pages you open"
- [ ] If measurement is switched on later: the privacy copy is rewritten and
      approved **before** the endpoint is set, not after, and this gate is
      re-run

Confirmed by ____________________ on ____________

## 3 · Retired URLs

- [ ] Checked whether any of the six were shared publicly
- [ ] Checked search-indexing status
- [ ] Checked whether any appears on a printed QR code
- [ ] Destination confirmed for each (see the map in `DEPLOY.md`)
- [ ] Once traffic is understood, the two remaining project-page redirects
      moved from temporary (307) to permanent (301) — or to gone, if that
      reads better

Confirmed by ____________________ on ____________

### 3b · The Garlic Farm page — withdrawn, not moved

`/explore/the-garlic-farm.html` described a partnership that was never agreed.
It is the one retired URL that does **not** redirect: it answers 404, because
redirecting it to Explore would tell a visitor, and a search engine, that it
is still part of the programme. That is the claim being withdrawn.

Removing it from the site does not remove it from a search index. Google may
keep serving a cached copy of the old page until it recrawls.

- [ ] Confirmed the live URL answers 404 and does not redirect
      (`tools/verify-live.py` checks this on every run)
- [ ] Removal requested via Search Console → **Removals → Temporarily remove
      URL**, for this exact URL. Note that a removal request hides the result
      for about six months; the durable signal is the 404 from the live URL,
      which is why both are needed.
- [ ] Updated `sitemap.xml` submitted
- [ ] Indexing requested for `/`, `/journeys.html`, `/how-we-work.html` and
      the three partner pages
- [ ] Re-checked after two weeks that the cached copy is gone

Removal requested by ____________________ on ____________

Cache confirmed gone by ____________________ on ____________

## 4 · Operator identity

- [ ] `David Grannum, trading as IsleConnect` is correct and current
- [ ] Nothing implies a link to ISLE CONNECT LTD (company 14356207)
- [ ] Advice taken on name and trade-mark risk before national expansion

Confirmed by ____________________ on ____________

## 5 · Enquiry form operational delivery & serverless endpoint

The diagnostic mapping form posts to `/api/enquiry` with direct fallback to `{endpoint}`.
Preflight cannot test live third-party delivery or serverless edge invocation.

- [ ] Formspree upstream target configured (`FORMSPREE_ENDPOINT` or default endpoint `https://formspree.io/f/xvgowwzn`)
- [ ] Test submission delivered end-to-end to `david@isleconnect.co.uk`
- [ ] Confirmation thank-you card displays cleanly upon submission
- [ ] Client-side fallback gracefully offers direct `mailto:david@isleconnect.co.uk` if upstream returns 502/network error
- [ ] Honeypot field (`_hp_company`) silently traps spam without false positives
- [ ] Zero PII (names, emails, phones, notes) logged in edge telemetry or console

Confirmed by ____________________ on ____________

---

Only when every box above is ticked should this merge to `main`.
