# Legendary Retreats — 90-Day SEO & GEO Growth Plan
*Goal: become the #1-ranked and most AI-quoted authority for the executive "offsite / leadership retreat" category.*

---

## Honest framing (read this first)

The on-page and technical work is essentially done — schema, speed, mobile, the
content clusters, the entity graph, original data (the Connection Deficit report),
and the comparison page are all live. **That was the 2% we fully control.** From
here, ranking #1 and getting AI-quoted is won off-page, and it compounds over
*months*, not days.

One expectation to set: the bare word **"offsite"** is a giant, generic,
mixed-intent term (software, Slack status, storage, events). We do **not** chase
it head-on. We win the **qualified cluster** — *executive offsite, leadership
offsite, executive retreat, offsite facilitator, executive offsite agenda/ideas/
cost* — where the intent is a buyer like ours. Own that cluster and the broad
"offsite" associations follow from topical authority. That is the realistic,
high-ROI path.

**Two scoreboards:**
1. **SEO** — Google rankings, impressions, clicks for the qualified cluster.
2. **GEO** — being cited/quoted by ChatGPT, Perplexity, Google AI Overviews, and
   Claude when someone asks "best executive retreat company," "how much does an
   executive offsite cost," "offsite vs retreat," etc.

---

## Phase 1 — Foundation & Indexing (Days 1–30)
*Make sure the work we did gets seen, measured, and crawled. Mostly free, mostly one-time.*

### 1. Search Console + Bing Webmaster (Day 1–2) — **highest priority**
- Verify the domain in **Google Search Console** (GSC) and **Bing Webmaster Tools**
  (Bing powers ChatGPT search + Copilot — GEO matters here).
- Submit `https://www.legendary-retreats.com/sitemap.xml` in both.
- Use **URL Inspection → Request Indexing** for the 8 newest pages:
  `/the-connection-deficit`, `/offsite-vs-executive-retreat`,
  `/for-executive-assistants`, and the 5 destinations (Sedona, Napa, Tahoe,
  Jackson Hole, Montana). Don't wait for natural crawl.
- Confirm `llms.txt` is reachable at the root and not blocked by robots.

### 2. Analytics & rank baseline (Day 2–3)
- Confirm GA4 (or Plausible) is firing on every page.
- Pick 25–30 target queries (the qualified cluster) and record today's position as
  the baseline. Free option: GSC "Queries" tab after data accrues; paid: a rank
  tracker (Ahrefs/Semrush) if budget allows.

### 3. Google Business Profile (Day 3–7)
- Create/claim a **Google Business Profile** for Be Legendary (Denver, CO — matches
  the schema address). Category: *Business management consultant* / *Corporate
  entertainment service*. This is a trust signal Google and AI both read, and it
  unlocks reviews (below).

### 4. The cross-domain authority link (Day 3–7) — **easy, high value**
- `belegendary.org` and `buildingteams.com` are *yours* and already have age/
  authority. Add a prominent, crawlable link from each (ideally the main nav or
  About/footer) to `legendary-retreats.com`, with anchor text like
  *"Executive Leadership Retreats"*. This passes real authority to the new domain —
  the single fastest legitimate link you can build because you own both ends.
- We already declared these as `sameAs`; the actual hyperlink makes it count for ranking.

### 5. First reviews (Day 7–30)
- Ask 5–10 past clients for a Google review (and a LinkedIn recommendation for
  James). Even a handful moves the needle for a high-trust service category and
  feeds AI "is this company reputable" judgments.

**End-of-Phase-1 result:** every page indexed, measurement live, GBP up, the
strongest owned-domain links in place, first reviews landing.

---

## Phase 2 — Authority & GEO (Days 31–60)
*Build the external signals that separate #2 from #1, and get into the sources AI quotes.*

### 6. Turn the report into a link magnet (Day 31–45)
- *The Connection Deficit* is original, data-backed, and citable — exactly what
  earns links and AI citations. Promote it:
  - Post James's summary + the key stats on **LinkedIn** (his strongest channel),
    linking to the report.
  - Pitch it as a guest article / data source to 2–3 leadership or HR publications
    (the same world that ran his CNN/Business Insider coverage).
  - Answer relevant **HARO / Qwoted / Featured** queries on remote work, CEO
    loneliness, and AI's effect on teams — link the report as the data source.
- Each external citation of the report's stats is both a backlink *and* a GEO signal
  (AI engines quote pages that other trusted pages cite).

### 7. Get into the "best executive retreat" listicles (Day 31–60) — **GEO gold**
- When someone asks an AI "best executive retreat companies," it largely
  regurgitates listicles ("Top 10 Executive Retreat Facilitators…"). Identify the
  ones currently ranking for *"best executive offsite companies / leadership
  retreat facilitators"* and get Be Legendary added (outreach, contribution, or
  paid placement where legitimate). This is the highest-leverage GEO play after the report.

### 8. Targeted backlinks (Day 31–60)
Priority targets, in rough order of value:
- **Co-author / association halo** — James co-authored with Covey, Blanchard,
  Chopra, Tracy. Any author bio, book page, or speaker directory that lists him
  should link to legendary-retreats.com.
- **Speaker & facilitator directories** — legitimate listings for executive
  facilitators/keynote speakers.
- **Venue & destination partners** — the lodges/venues used (Ranch at Rock Creek,
  Alila Napa, Jenny Lake, etc.) often have "partners/experiences" pages. Reciprocal
  mentions are natural and relevant.
- **Client/case-study links** — where a client can publicly credit the work, a link
  from their site is gold (high relevance, high trust).
- **Podcasts** — book James on 3–5 leadership/CEO podcasts; show-notes links + the
  spoken authority feed both SEO and GEO.

### 9. Reviews to critical mass (ongoing) — aim for 10+ on GBP, plus G2/Clutch if a fit.

**End-of-Phase-2 result:** the report is being cited, Be Legendary appears in
"best of" lists AI pulls from, and a first wave of relevant, high-trust backlinks
is live.

---

## Phase 3 — Content Cadence & Moat (Days 61–90)
*Out-publish the category on the questions buyers and AIs actually ask.*

### 10. Publish answer-style cluster pages (1–2 per week)
Each targets a real query, gives a direct extractable answer up top (snippet/AI
friendly), and links into the existing cluster. High-value candidates:
- "Executive offsite agenda" / a downloadable **sample agenda template**
- "Team offsite ideas for executives" (ideas hub → links to formats/destinations)
- "How much does a corporate/executive retreat cost" (you have the data — expand it)
- "How to plan a leadership offsite" checklist
- "Executive offsite vs team building" (another comparison, like offsite-vs-retreat)
- "Best time of year / where to host an executive retreat"
- More **destination pages** as real photos allow (Aspen, Scottsdale, Park City,
  Charleston, Sun Valley) — each is a long-tail magnet.

> Production note: these slot straight into the existing pipeline — author a new
> `.dc.html`, add it to `MAP` in `scripts/generate.mjs`, `og-map.mjs`, `sitemap.xml`,
> and `llms.txt`. ~30 min each once written.

### 11. Strengthen topical authority (Day 61–90)
- Interlink aggressively: every new page links to 3–5 siblings and the pillars
  (Executive Offsites, Ways to Work Together, the report).
- Refresh the 2–3 oldest Field Notes with a 2026 update + the report's data.
- Add an **"offsite vs team building"** and an **"executive retreat vs conference"**
  comparison to complete the comparison set (AI loves clean comparisons).

### 12. GEO reinforcement (Day 61–90)
- Keep `llms.txt` updated as pages ship (already the habit).
- Make sure every key page leads with a **direct, quotable answer** in the first
  paragraph — that's what AI extracts. (The report and comparison page already do this.)
- Pursue a **Wikidata** entry for James Carter / Be Legendary once there's enough
  independent coverage to support it — Wikidata/Wikipedia are disproportionately
  trusted by AI engines for entity facts.

**End-of-Phase-3 result:** a deep, interlinked cluster that owns the qualified
"offsite/retreat" question space, with the freshness and breadth that compounds.

---

## Weekly cadence (sustaining, after Day 90)
- **Mon** — check GSC: new queries gaining impressions; pick next content target.
- **Wed** — publish/refresh 1 page; update llms.txt + sitemap.
- **Fri** — 1 outreach action (link, listicle, podcast, or review request).
- **Monthly** — re-run the Rich Results test on key pages; re-request indexing for
  anything updated; review rank movement on the 25–30 target queries.

---

## KPIs & realistic 90-day targets
| Metric | Baseline (Day 0) | Day 90 target |
|---|---|---|
| Indexed pages (GSC) | ~37 → 45 just shipped | 45/45 + new content indexed |
| Qualified-cluster queries in top 10 | record now | +8–12 terms |
| Referring domains | record now | +15–25 *relevant* domains |
| GBP reviews | 0 | 10+ |
| AI citations (spot-check ChatGPT/Perplexity for "best executive offsite", "offsite vs retreat", "executive retreat cost") | record now | quoted/cited in ≥3 of the test prompts |
| Report backlinks | 0 | 5+ |

> "#1 for *executive offsite / leadership retreat*" within 90 days is achievable
> with disciplined links + cadence. "#1 for bare *offsite*" is a 6–12 month
> byproduct of category dominance, not a 90-day target — and not where the buyers are.

---

## What needs *you* vs. what I can do
**Needs you (accounts / real-world):** GSC + Bing verification, GBP, the
belegendary.org/buildingteams.com nav links, review requests, podcast/PR outreach,
listicle placements, any new destination photos.

**I can do anytime:** write every new cluster/comparison/destination page (schema +
internal links + OG + sitemap + llms.txt), draft the LinkedIn/outreach/HARO copy,
draft the report-promotion assets, audit indexing once GSC is connected, and keep
the entity graph current as new profiles (book Amazon URLs, Wikidata) appear.

*Tell me which Phase-3 pages to start writing and I'll begin immediately — that's
the part we don't have to wait on anyone for.*
