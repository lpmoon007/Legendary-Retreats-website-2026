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

- `_src/_deploy/` — the Design Component bundle (source of truth): the
  `*.dc.html` pages, `support.js` runtime, `assets/`, and `seo/`.
- `_src/_deploy/partials/` — the shared header, footer and their CSS. Every page
  carries `<!--lr:header-->` / `<!--lr:footer-->` markers that the generator fills,
  so nav changes happen in one place.
- `scripts/generate.mjs` — converts each page listed in its `MAP` into an Astro
  page + raw `head`/`body` fragments under `src/generated/`, and writes
  `public/sitemap.xml` from the same map. It preserves the `<head>` meta, fonts,
  page-scoped `<style>` and all JSON-LD verbatim, and applies:
  1. internal `*.dc.html` links → clean slugs (retired files → their replacement)
  2. relative `assets/…` → `/assets/…`
  3. trailing-slash normalisation (canonical form is `/slug/`)
  4. the shared chrome from `partials/`
  Files not in `MAP` (e.g. `Legendary Dials`, the internal strategy docs) are not built.
- `scripts/port-from-belegendary.py` — the Oct 2026 port of the retreat pages from
  belegendary.org. It reads a Be Legendary build (`dist/`), recolors it to this
  palette, rewrites links and schema to this domain, copies images, and writes the
  `.dc.html` files. Re-runnable until the split is final (it overwrites the pages
  in its `PAGES` list): build Be Legendary, then
  `python3 scripts/port-from-belegendary.py <be-legendary-repo>` and
  `npm run generate`. Needs `beautifulsoup4` + `lxml`.
- `src/layouts/Base.astro` — injects each page's head + body.
- `public/` — `assets/`, plus `robots.txt`, `sitemap.xml` (generated), `llms.txt`.

`src/generated/` and `src/pages/` are produced by the generator; rerun
`npm run generate` after editing anything in `_src/_deploy/`.

## Deploy

Static `dist/` served by nginx on the GoDaddy VPS. HTTPS, gzip/brotli, long-cache
`/assets/*`, the Wix→clean-slug 301 redirect map, and `try_files` for clean URLs.

- **nginx config:** [`deploy/nginx.conf`](deploy/nginx.conf)
- **Step-by-step guide:** [`DEPLOY.md`](DEPLOY.md)

## Brand tokens

Primary `#64010a` · accent `#E08A52` · gold `#E0B973` · ink `#1C1A17` ·
paper `#EFE9DD`. Fonts: Newsreader, Hanken Grotesk, IBM Plex Mono, Archivo.
Accent on dark sections: gold `#E0B973`. Every "Plan your retreat" CTA →
`https://meetings-na2.hubspot.com/jcarter28` (until the retreat inquiry form
exists) · phone `800-513-8759`.
