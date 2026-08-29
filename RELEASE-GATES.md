# Release gates — the things no script can check

`tools/preflight.py` proves the repository is internally consistent. It cannot
prove any of the following. Each needs a person to confirm it, and the date
recorded here, before this reaches production.

## 1 · Mailbox

Eight public pages point at `hello@isleconnect.co.uk` the moment this merges.

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

## 3 · Retired URLs

- [ ] Checked whether any of the six were shared publicly
- [ ] Checked search-indexing status
- [ ] Checked whether any appears on a printed QR code
- [ ] Destination confirmed for each (see the map in `DEPLOY.md`)
- [ ] Once traffic is understood, the three project-page redirects moved from
      temporary (307) to permanent (301) — or to 410 if that reads better

Confirmed by ____________________ on ____________

## 4 · Operator identity

- [ ] `David Grannum, trading as IsleConnect` is correct and current
- [ ] Nothing implies a link to ISLE CONNECT LTD (company 14356207)
- [ ] Advice taken on name and trade-mark risk before national expansion

Confirmed by ____________________ on ____________

---

Only when every box above is ticked should this merge to `main`.
