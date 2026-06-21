# Legendary Retreats — website (2026)

Static marketing site for **Legendary Retreats** (Be Legendary), ported from the
client-approved Design Components (`*.dc.html`) to **Astro** static output for
deployment on the GoDaddy managed VPS (nginx).

## Develop

```bash
npm install
npm run dev        # http://localhost:4321
```

## Build

```bash
npm run build      # runs scripts/generate.mjs, then `astro build` -> dist/
npm run preview    # serve the built dist/
```

## How it works

- `_src/_deploy/` — the original Design Component bundle (source of truth):
  the `*.dc.html` pages, `support.js` runtime, `assets/`, and `seo/`.
- `scripts/generate.mjs` — converts each production `*.dc.html` into an Astro
  page + raw `head`/`body` fragments under `src/generated/`. It preserves the
  `<head>` meta, fonts, page-scoped `<style>` and **all JSON-LD verbatim**, and
  applies only two transforms:
  1. internal `*.dc.html` links → clean slugs (see the map in the script)
  2. relative `assets/…` → `/assets/…` (clean URLs are nested)
  The three internal artifacts (`SEO & AI Search Strategy`, `Growth Plan v2`,
  `Legendary Dials`) are excluded from the build.
- `src/layouts/Base.astro` — injects each page's original head + body unchanged.
- `src/components/LegendaryDial.jsx` — the "Pick your level of Legendary" dial,
  ported 1:1 and hydrated as a Preact island on `/ways-to-work-together`.
- `public/` — `assets/`, plus `robots.txt`, `sitemap.xml`, `llms.txt` served at root.

`src/generated/` and `src/pages/` are produced by the generator; rerun
`npm run generate` after editing anything in `_src/_deploy/`.

## Deploy

Static `dist/` served by nginx. HTTPS, gzip/brotli, long-cache `/assets/*`, the
301 redirect map (`_src/_deploy/seo/redirects.md`), and `try_files` for clean
URLs. (nginx config + step-by-step VPS instructions: pending.)

## Brand tokens

Primary `#64010a` · accent `#E08A52` · gold `#E0B973` · ink `#1C1A17` ·
paper `#EFE9DD`. Fonts: Newsreader, Hanken Grotesk, IBM Plex Mono, Archivo.
Every CTA → `https://meetings-na2.hubspot.com/jcarter28` · phone `800-513-8759`.
