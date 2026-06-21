# Deploy map & 301 redirects — Wix → VPS

## 1. Clean URL map (DC file → production path)

Serve each Design Component at a clean path. On the VPS, render/export each
`.dc.html` to static HTML at the path below (e.g. `/leadership-retreats/index.html`).

| Design Component file              | Production URL                                     |
|------------------------------------|----------------------------------------------------|
| `Legendary Retreats - Home.dc.html`| `/`                                                |
| `Leadership Retreats.dc.html`      | `/leadership-retreats`                             |
| `Destinations.dc.html`             | `/destinations`                                    |
| `Retreat - Moab.dc.html`           | `/destinations/moab-utah`                          |
| `Retreat - San Juan Mountains.dc.html`      | `/destinations/san-juan-mountains-colorado`                |
| `Retreat - Sierra Nevada.dc.html`   | `/destinations/sierra-nevada`  (old `/destinations/lake-tahoe` 301 here)  |
| `Retreat - Great Basin Desert.dc.html` | `/destinations/great-basin-desert`              |
| `About.dc.html`                    | `/about`                                            |
| `The Experience.dc.html`           | `/experience`  (old `/gallery` + `/film` 301 here)  |
| `Contact.dc.html`                  | `/contact`                                          |

> Before deploy, update the in-page `<a href="...">` nav/footer links and the
> sitemap/llms URLs from the `.dc.html` filenames to these clean paths.

## 2. 301 redirects from the old Wix URLs

Preserve the equity already earned. Add these to your server config
(Apache `.htaccess` or Nginx) — adjust left-hand paths to your real Wix slugs.

```
# --- Apache (.htaccess) ---
Redirect 301 /about-4            /about
Redirect 301 /contact-4         /contact
Redirect 301 /projects-8        /experience
Redirect 301 /gallery           /experience
Redirect 301 /film              /experience
Redirect 301 /leadership-retreats-1 /leadership-retreats
# old query/hash home variations resolve to /
```

```
# --- Nginx ---
location = /about-4    { return 301 /about; }
location = /contact-4  { return 301 /contact; }
location = /projects-8 { return 301 /experience; }
location = /gallery    { return 301 /experience; }
location = /film       { return 301 /experience; }
location = /leadership-retreats-1 { return 301 /leadership-retreats; }
```

## 3. Post-deploy checklist
- [ ] Submit `https://www.legendary-retreats.com/sitemap.xml` in Google Search Console.
- [ ] Confirm `robots.txt`, `sitemap.xml`, and `llms.txt` are served from the domain root.
- [ ] Verify each JSON-LD block with Google's Rich Results Test.
- [ ] Force HTTPS + canonical host (www vs apex — pick one, 301 the other).
- [ ] Set per-page `<title>` and `<meta name="description">` (see seo/meta-map.md).
- [ ] Re-encode the PDF-extracted photos at full resolution; swap in real hero video.
