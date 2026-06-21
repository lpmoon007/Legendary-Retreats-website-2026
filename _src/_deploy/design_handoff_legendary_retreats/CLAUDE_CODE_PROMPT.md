# First Prompt for Claude Code

Paste this into Claude Code after opening the repo with this handoff bundle in it.

---

You are picking up a **finished marketing website** for *Legendary Retreats* (Be Legendary — premium executive leadership retreats). Read `design_handoff_legendary_retreats/README.md` in full before doing anything — it is the source of truth.

**Context:** The `*.dc.html` files are the production-final site (final copy, layout, imagery, SEO — client-approved). They render via a small runtime (`support.js`). I want them deployed as a fast static site on a GoDaddy managed VPS (nginx), with the one interactive component preserved.

**Do this, in order:**

1. **Port to Astro (static output).** Each `.dc.html`'s inner markup → an `.astro` page. Extract the shared sticky header + footer into a layout. Keep all inline styles verbatim (the design is intentionally inline-styled — do not refactor into CSS frameworks). Load the same Google Fonts (Newsreader, Hanken Grotesk, IBM Plex Mono, Archivo).

2. **Implement the exact clean-URL routing** from README §3 (file → slug map). Rewrite all internal `href="*.dc.html"` links to the clean slugs.

3. **Port the one interactive island:** the "Pick your level of Legendary" dial embedded in `/ways-to-work-together` (logic in `Legendary Dials.dc.html`). Two 0–100 sliders → live "Intensity" score + quadrant readout. Make it a React/Preact island.

4. **Preserve every page's `<head>`:** unique title, meta description, canonical, Open Graph + Twitter tags, favicon set, and all JSON-LD (`Organization`/`Service`/`Person`/`FAQPage`/`Article`/`BreadcrumbList`/`ImageGallery`). Do not drop or regenerate the structured data.

5. **Wire the `seo/` stack:** serve `sitemap.xml`, `robots.txt`, `llms.txt` at root. Implement the **301 redirects** from `seo/redirects.md` as nginx rules (old Wix URLs → new slugs, e.g. `/about-4→/about`, `/gallery` & `/film→/experience`, `/destinations/lake-tahoe→/destinations/sierra-nevada`).

6. **Exclude internal artifacts** from build + sitemap: `SEO & AI Search Strategy.dc.html`, `Growth Plan v2.dc.html`, `Legendary Dials.dc.html` (its content is inlined into Ways to Work Together).

7. **Assets:** copy `assets/` as-is. Photos are already WebP. Brand marks stay PNG (transparency). Long-cache `/assets/*`. The geography of every photo is verified correct — do not relabel alt text.

8. **Deploy config:** nginx static serve, force HTTPS, gzip/brotli, the 301 map, and `try_files` for clean URLs. Give me the nginx config and the deploy steps for the GoDaddy VPS.

**Constraints:**
- Every CTA must keep pointing to `https://meetings-na2.hubspot.com/jcarter28`; phone `800-513-8759`.
- Do not change copy, layout, colors, or imagery — this is a deploy/port task, not a redesign.
- Brand tokens (for reference, already in the markup): primary `#64010a`, accent `#E08A52`, gold `#E0B973`, ink `#1C1A17`, paper `#EFE9DD`.

When done, give me: the dev preview command, a checklist confirming all 34 pages render at their clean URLs, and the VPS deploy instructions.
