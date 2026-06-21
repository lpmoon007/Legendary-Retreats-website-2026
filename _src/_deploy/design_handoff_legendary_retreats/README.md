# Handoff: Legendary Retreats — Full Website (2026 rebuild)

**Target repo:** https://github.com/lpmoon007/Legendary-Retreats-website-2026.git
**Prepared for:** Claude Code, to finalize and deploy to a managed VPS (GoDaddy).

---

## 0. TL;DR for Claude Code

This bundle is a **complete, finished marketing website** for *Be Legendary / Legendary Retreats* (premium executive leadership retreats). It is built as a set of **Design Components (`*.dc.html`)** — self-contained HTML files that render live in a browser via a small runtime (`support.js`). They are **not rough mockups**; the copy, layout, imagery, and SEO are production-final and have been reviewed by the client.

Your job is to:
1. Get these pages serving as a fast, static, **SEO/GEO-correct** website on the client's VPS.
2. Preserve the **interactive bits** (slide-in nav behavior is minimal; the one genuinely interactive component is the "Pick your level of Legendary" dial on *Ways to Work Together*).
3. Implement the **clean URL map**, **301 redirects**, **sitemap/robots/llms.txt**, and **per-page meta** exactly as specified in `seo/`.

There are **two valid implementation paths** — pick based on the client's appetite (see §6):
- **A. Ship the DC runtime as-is** (fastest; keep `.dc.html` + `support.js`, add a server/redirect layer + clean URLs). The pages already include full `<head>` SEO, so they're crawlable.
- **B. Port to a static framework** (Astro/11ty/Next static export). Recommended for long-term maintainability. The DC files are trivially convertible — each is plain semantic HTML with inline styles; the only dynamic piece is the dial component (port to a tiny React/vanilla island).

---

## 1. What this site is

- **Brand:** Be Legendary. Public name on this site: *Legendary Retreats*.
- **Offering:** Immersive, fully-facilitated executive leadership retreats for CEOs and their senior teams, with measurable 30-day behavioral reinforcement.
- **Primary conversion:** Book a strategy call — every CTA points to `https://meetings-na2.hubspot.com/jcarter28`. Secondary: phone `800-513-8759`.
- **Positioning:** Pain-first, CEO-as-hero. The methodology (LDOL / "Lost Disciplines of Leadership") is opt-in depth, never imposed.
- **Founder/guide:** James Carter. LinkedIn: https://www.linkedin.com/in/jlcarter/ (wired into Person schema `sameAs`).

---

## 2. About the design files (read this)

Every page is a `*.dc.html` file. Structure of each file:
- A real, complete HTML document: `<!DOCTYPE html> … <head> (full SEO meta) … <body>`.
- Inside `<body>`: an `<x-dc>` element wrapping a `<helmet>` (fonts + page-scoped `<style>` + JSON-LD) and the page markup.
- `<script src="./support.js"></script>` in `<head>` is the **DC runtime** that hydrates `<x-dc>`. For most pages this just renders static markup. Two files use it for real interactivity (see §5).
- **All visual styling is inline** on elements (by design). There is no external CSS file and no CSS framework. Fonts load from Google Fonts (Newsreader, Hanken Grotesk, IBM Plex Mono, Archivo).

**If porting (path B):** the inline styles + semantic markup convert 1:1 to JSX/components. Strip the `<x-dc>/<helmet>/support.js` wrapper, keep the inner markup, move the `<head>` block into your framework's head management, and re-implement the dial as an island.

**Fidelity: high (hifi).** Colors, type, spacing, and copy are final. Recreate pixel-accurate.

---

## 3. Page inventory & clean URL map

Each page's intended production URL is already in its `<link rel="canonical">`. Use these slugs.

| File | Clean URL |
|---|---|
| `Legendary Retreats - Home.dc.html` | `/` |
| `Leadership Retreats.dc.html` | `/leadership-retreats` |
| `Ways to Work Together.dc.html` | `/ways-to-work-together` |
| `The Framework.dc.html` | `/framework` |
| `Is This Your Team.dc.html` | `/is-this-your-team` |
| `Destinations.dc.html` | `/destinations` |
| `Retreat - San Juan Mountains.dc.html` | `/destinations/san-juan-mountains-colorado` |
| `Retreat - Moab.dc.html` | `/destinations/moab-utah` |
| `Retreat - Sierra Nevada.dc.html` | `/destinations/sierra-nevada` |
| `Retreat - Great Basin Desert.dc.html` | `/destinations/great-basin-desert` |
| `Retreat - Death Valley.dc.html` | `/destinations/death-valley` |
| `Format - Cabin Fever.dc.html` | `/formats/cabin-fever` |
| `Format - Off-Road Immersion.dc.html` | `/formats/off-road-immersion` |
| `Format - Winter Survival.dc.html` | `/formats/winter-survival` |
| `Format - Wilderness Expedition.dc.html` | `/formats/wilderness-expedition` |
| `Case Studies.dc.html` | `/case-studies` |
| `Case Study - Auto Retailer Egos.dc.html` | `/case-studies/online-auto-retailer-leadership-team` |
| `Case Study - Federal Fiscal Team.dc.html` | `/case-studies/federal-fiscal-leadership-team` |
| `Case Study - Everglades Abundance.dc.html` | `/case-studies/everglades-abundance-mindset` |
| `Case Study - Alaska Vulnerability.dc.html` | `/case-studies/alaska-executive-vulnerability` |
| `Case Study - San Juans Work Ethic.dc.html` | `/case-studies/san-juan-mountains-work-ethic` |
| `Field Notes.dc.html` | `/field-notes` |
| `Field Note - Do Retreats Work.dc.html` | `/field-notes/do-leadership-retreats-work` |
| `Field Note - Two Questions.dc.html` | `/field-notes/two-questions-leadership-retreat` |
| `Field Note - Align Your Team.dc.html` | `/field-notes/align-leadership-team` |
| `Field Note - Questions Before Retreat.dc.html` | `/field-notes/questions-before-executive-retreat` |
| `Field Note - 30 Day Reinforcement.dc.html` | `/field-notes/30-day-reinforcement` |
| `Field Note - What Is An ELR.dc.html` | `/field-notes/what-is-an-experiential-leadership-retreat` |
| `Field Note - Retreat Cost.dc.html` | `/field-notes/executive-retreat-cost` |
| `Field Note - New And Merged Teams.dc.html` | `/field-notes/newly-formed-post-merger-leadership-team` |
| `Field Note - Signature Vs Bespoke.dc.html` | `/field-notes/signature-vs-bespoke-retreat` |
| `About.dc.html` | `/about` |
| `The Experience.dc.html` | `/experience` |
| `Contact.dc.html` | `/contact` |

**Internal links in the markup currently point to the `.dc.html` filenames** (e.g. `href="Case Studies.dc.html"`). When you implement clean URLs, rewrite these to the slugs above. A simple build-time string map handles it. (If shipping path A as-is on a static host, also serve each file at its clean path and keep the `.dc.html` links working, or rewrite them.)

**NOT for production** (internal strategy artifacts — exclude from deploy & sitemap): `SEO & AI Search Strategy.dc.html`, `Growth Plan v2.dc.html`, `Legendary Dials.dc.html` (the dial is embedded into Ways to Work Together via `<dc-import>`; if porting, inline it there).

---

## 4. The `seo/` folder — implement exactly

- `seo/sitemap.xml` — all production URLs. Serve at `/sitemap.xml`.
- `seo/robots.txt` — allows all + AI crawler-friendly; points to sitemap. Serve at `/robots.txt`.
- `seo/llms.txt` — AI-search summary of the whole site. Serve at `/llms.txt`.
- `seo/redirects.md` + `seo/redirects.map.txt` — **301 map from the old Wix URLs** (e.g. `/about-4 → /about`, `/projects-8 → /experience`, `/gallery` & `/film → /experience`, `/destinations/lake-tahoe → /destinations/sierra-nevada`). Implement as real 301s at the server/CDN.
- `seo/meta-map.md` — per-page `<title>` + description reference (already baked into each page's `<head>`; use this to verify).

Every page already carries: unique `<title>`, meta description, canonical, Open Graph + Twitter cards (share image `/assets/brand/og-default.png`), favicon set, and JSON-LD (`Organization`/`Service`/`Person`/`FAQPage`/`Article`/`BreadcrumbList`/`ImageGallery` as appropriate). **Preserve all of it** when porting.

---

## 5. Interactive / dynamic pieces

1. **"Pick your level of Legendary" dial** (`Legendary Dials.dc.html`, embedded in `Ways to Work Together.dc.html`). Two 0–100 range sliders (Physical, Emotional) that compute a live "Intensity" score and a quadrant-aware readout. Logic is in the DC's `Component` class (`renderVals()`). **Port to a small React/vanilla island** — it's ~40 lines of state + string interpolation.
2. **Vimeo/YouTube embeds** on `/experience` — standard responsive iframes, no JS.
3. **Sticky headers** — pure CSS (`position:sticky`). No JS.

Everything else is static.

---

## 6. Recommended deploy approach

The client is on a **GoDaddy managed VPS** and wants the interactive bits preserved.

**Recommended: Path B — static build.**
- Port to **Astro** (best fit: islands for the one dial, file-based routing matching the URL map, trivial static output, built-in sitemap). Each `.dc.html` inner markup becomes an `.astro` page; shared header/footer become a layout; the dial becomes a React/Preact island.
- Output static HTML → serve via nginx on the VPS. Add the 301 map as nginx `return 301` rules (see `seo/redirects.md` which already contains nginx-format snippets).
- Force HTTPS, gzip/brotli, long-cache `/assets/*` (images are already WebP).

**Faster: Path A — ship as-is.**
- Serve the `.dc.html` files + `support.js` + `/assets` statically. Map clean URLs → files via nginx `try_files`/rewrites. Add the 301s. Rewrite internal `.dc.html` links to clean URLs with a one-time sed pass.
- Tradeoff: ships the DC runtime JS to users; fine for SEO (full HTML is in `<head>`/`<body>`) but heavier than a static port.

Either way: **preserve every `<head>` block, all JSON-LD, the `seo/` files, and the asset paths.**

---

## 7. Assets

- `assets/brand/` — logo/snail marks (transparent PNGs — keep as PNG for transparency), favicons, `og-default.png` share image.
- `assets/field/` — all photography, **already converted to WebP** and referenced as `.webp`. These are the client's real retreat photos (off-road, winter/dogsled, alpine, river, AlUla, lodge, fire-circle) plus a few destination shots. Geography is verified correct — do not relabel.
- `assets/retreat-photos/`, `assets/site-photos/` — legacy/source extracts; only the few still referenced matter. Safe to keep.
- `support.js` — the DC runtime. Required for Path A; not needed if you fully port (Path B).

---

## 8. Brand / design tokens

- **Primary (oxblood/maroon):** `#64010a`  ·  **Accent (terracotta):** `#E08A52`  ·  **Gold:** `#E0B973`
- **Ink:** `#1C1A17`  ·  **Body text:** `#403B33` / `#5A5448`  ·  **Paper bg:** `#EFE9DD` / `#F4EFE5`  ·  **Cards:** `#FBF9F4`  ·  **Dark sections:** `#1C1A17` / `#141210`
- **Type:** Newsreader (serif display/headlines), Hanken Grotesk (body/UI), IBM Plex Mono (eyebrows/labels), Archivo (heavy uppercase wordmark/stats).
- **Radii:** cards 14–18px, pills 999px. **Shadows:** soft, low-opacity (`0 28px 64px -36px rgba(28,26,23,.5)` for feature cards).

---

## 9. Off-site / post-deploy (client to action, note for completeness)

Not code, but flag in your deploy notes: set up Google Search Console + GA4, submit the sitemap, claim/optimize a Google Business Profile, and pursue backlinks (book page, podcasts, directories). These strengthen the entity authority already wired into the schema.

---

## 10. Files in this bundle

The entire project is included: all `*.dc.html` pages, `support.js`, the `assets/` tree, and the `seo/` folder. The three internal artifacts named in §3 should be excluded from production. Start from `Legendary Retreats - Home.dc.html` and the URL map in §3.

A `CLAUDE_CODE_PROMPT.md` is included in this folder — paste it into Claude Code to kick off the build.

## 11. Screenshots

Representative full-page captures live in `screenshots/` (reference only — the live `.dc.html` files are authoritative; note iframe video embeds and web fonts don't render in these static captures):
- `01-home.png` — Home (hero, pain section, proof)
- `03-ways-to-work-together.png` — Signature/Bespoke ladder + the dial + format cards
- `04-the-framework.png` — LDOL framework page
- `06-destinations.png` — Destinations hub (US map, destination cards)
- `10-death-valley.png` — a destination detail page
- `16-case-studies.png` — Case Studies index
- `22-field-notes.png` — Field Notes index
