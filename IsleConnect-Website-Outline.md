# IsleConnect — Website Strategy

**Version 3.1 · 18 August 2026 · STRATEGY FROZEN**
Supersedes v2.0 (Lean V1). Re-centred on Ryde, with all five open questions now resolved. The built site lives in `site/`; `site/BUILD-SPEC.md` carries the implementation detail and the decisions log.

From this version onward, changes should be execution quality — poster frames, mobile playback, load speed, story pages, the story-to-next journey, naming consistency — not further strategic editing.

---

## 0. The change in this version

V2 built the homepage around three equal cards — Bembridge Fort, Peter J. Murray, The Garlic Farm — of which one was live, one was a book concept and one was marked *Concept*. That was a mixed pipeline dressed as proof.

**V3 builds the homepage around two things that exist and play:**

1. **Ryde 140** — Royal Victoria Arcade, evidence-led reconstruction, c.1837
2. **Ryde to Seaview Wartime Trail** — Puckpool Battery, The Sea-Face Guard

Everything else — Garlic Farm, Peter J. Murray, MiniVox, wider attractions — becomes *coming next*, not equal-weight homepage proof.

The site is more credible for it, because every claim on the homepage is now backed by something a visitor can press play on.

### Positioning

> **IsleConnect brings Ryde's stories to life — helping people discover the history, places and businesses around them.**

And, lower down and quieter:

> **Ryde is where we are proving the model. The same approach can later bring books, attractions and destinations to life.**

This stops the website trying to prove the future addressable market and instead makes **Ryde the polished reference implementation**. Once that works, "bring books, attractions and destinations to life" becomes much easier to believe.

### The governing principle, unchanged

> **Make the thing you create the star of the website, not the technology that creates it.**

### Language

Visitor-facing, lean on **stories** and **trails**, not "experiences". People parse *"Explore the stories"* and *"Follow the wartime trail"* faster than *"Explore experiences"*. Keep "experience" as internal and commercial vocabulary.

---

## 1. The two strands, and why both

They demonstrate two different products, which is more useful than either alone:

| | Ryde 140 | Ryde to Seaview Wartime Trail |
|---|---|---|
| **Shape** | Explore a place deeply | Move through a connected journey |
| **Lead asset** | Royal Victoria Arcade, old-to-new | Puckpool Battery, Sea-Face Guard |
| **Proves** | Evidence-led reconstruction | Curated multi-stop routes |
| **Sells to** | Town, culture, heritage, businesses | Venues on a route, transport, destinations |

Showing both means the site never reads as a single-format product.

---

## 2. Homepage — eight bands

```
1  Hero — Bring Ryde to life
2  Two flagship experiences — the two films
3  Discover. Experience. Go.
4  Explore Ryde — the growing network of stories
5  Collections — Ryde 140 / Ryde to Seaview Wartime Trail
6  For local venues and businesses
7  Why you can trust it
8  Beyond Ryde — categories only, no partner names
   Close + footer
```

Bands 2 and 5 both cover the collections deliberately: **band 2 shows the product** (here is the film), **band 5 shows the curation** (here is what a collection is). That distinction is what turns "we make videos" into "we build trails".

### Key copy

**Hero** — *Bring Ryde to life.* / Explore the stories, places and people that shaped Ryde — then discover where to go next. → `Explore the stories` · `For local partners`

**Band 3 closing line** — *The digital experience is there to help you discover more of the real place.* This matters more than it did in v2, because both current products are physically rooted.

**Band 6** — *Be part of the journey.* Three benefits: **Be discovered** / **Tell your story** / **See what happens next** → `Become a Ryde partner`.

That third benefit is the important one. It introduces measurement without mentioning analytics or dashboards. Once the pilot has run, it becomes concrete — *327 people discovered this story · 94 continued to another stop · 36 requested directions to a nearby venue* — and that is what makes a venue subscription tangible. The shape is already built on `partners/venues.html`, marked as illustrative until real figures exist.

**Band 7 trust** — unchanged from v2. *Real stories. Real places. Human checked.* with Sources checked / Human reviewed / Rights respected.

**Band 8** — *Beyond Ryde.* Books & authors, Attractions, Other towns & destinations. **Categories only.** Do not name Pete, Garlic Farm or MiniVox until there is a collaboration or agreed concept you can publish. That is what protects the credibility the rest of the page just built.

---

## 3. Navigation and structure

```
Explore Ryde   Ryde 140   Wartime Trail   For Partners   About
```

Five items, and they describe what actually exists. Contact sits in the mobile menu, the footer and every CTA.

```
HOME
EXPLORE RYDE
 ├── Royal Victoria Arcade      ← live
 ├── Puckpool Battery           ← live
 ├── Appley Tower               ← in development
 ├── Ryde Pier                  ← in development
 ├── Union Street               ← in development
 └── Seaview                    ← in development
RYDE 140          collection page
WARTIME TRAIL     route page, nine canonical stops
FOR PARTNERS
 ├── Venues & businesses
 ├── Authors & creators
 └── Organisations
ABOUT · CONTACT
```

**The in-development pages are real pages, not dead links.** Each says the story is being built and asks directly: *do you have photographs, memories or records connected with this place?*

That does three jobs at once — content acquisition, community engagement and evidence gathering — and it reinforces that IsleConnect is not generating material from nowhere. Used sparingly, it is a strength rather than a gap.

---

## 4. The trust argument is now visible in the product

The Royal Victoria Arcade film carries an on-screen label: **"Evidence-led AI reconstruction · c.1837"**, and closes on the sourcing — a contemporary 1837 engraving, surviving building materials, brick sources, architectural details.

That is the trust section doing its job inside the content rather than beside it. It distinguishes *reconstruction* from *established fact* in four words, on screen, where it matters. It is the strongest single piece of product language either film contains, and it should be the pattern for everything that follows.

---

## 5. What this deliberately does not do

Garlic Farm, Peter J. Murray, MiniVox / Mokee Joe named on the homepage · testimonials · partner logo strip · "stand here" previews · newsletter · News · Vectis ONE explainer page · offline caching · a mature Trails/Places/Map information architecture

**Vectis ONE appears exactly once**, unlinked, in the footer. **AI is mentioned once on the homepage**, in the trust panel, in a sentence whose subject is human responsibility.

---

## 6. Decisions — settled

1. **The lighthouse is the IsleConnect trust mark.** The Puckpool film already put it in front of visitors; fighting that created more work than value. Vectis ONE remains the underlying technical name, unlinked in the footer. This gives continuity without asking the public to understand the parent architecture.
2. **Ryde 140 is a programme name, not a date range.** The site never states what "140" refers to: *"A growing collection exploring Ryde's buildings, people and stories across the centuries."* That lets the arcade's 1836–1856 history sit naturally rather than pretending it belongs to an 1887 event.
3. **Nine stops is the canonical numbering**, taken from the film's own "Stop 7 of 9". Website, QR codes, films and print all use it. Unconfirmed stops read *"Stop number to be confirmed"* — no invented names.
4. **One trail name: Ryde to Seaview Wartime Trail.** It says what it is and where it goes. "Seaview Wartime Trail" sounded contained within Seaview; "Wartime Coast" was attractive but less clear, and is retired (available later as campaign copy).
5. **The Dell Cafe is the first story→business demonstration** — a `Nearby` module on the Puckpool page rather than a partner-logo claim. That is precisely the commercial behaviour worth measuring.

### Still to confirm

The vector logo file · the five unnamed trail stops · whether the The Dell Cafe agreement is publishable · contributor bios and portraits · hosting and domain.

---

## Appendix A — Phase 2 and beyond

Not rejected, just later. Full detail is in v2.0 of this document.

| Item | Revisit when |
|---|---|
| Garlic Farm | An agreed concept exists that the farm is happy to publish |
| Peter J. Murray / books strand | A collaboration is agreed |
| MiniVox / Mokee Joe | Same |
| Testimonials | Real attributed quotes exist from the Ryde pilot |
| Partner logo strip | Written agreements signed — The Dell Cafe may already qualify |
| "Stand here" previews | Trail testing shows people want it before they travel |
| Trails / Places / Map navigation | Behaviour data says which one matters |
| Newsletter, News | There is a reason to write to people |
| Vectis ONE explainer | The footer line starts getting clicked, or a partner asks |
| Offline caching | Field testing shows signal is genuinely breaking sessions |

**Retained and still true from earlier versions:** the brand system, the story page template, the technical notes, and the three editorial rules — no jargon, show before you tell, one AI mention.

---

*Make the thing you create the star of the website, not the technology that creates it.*
