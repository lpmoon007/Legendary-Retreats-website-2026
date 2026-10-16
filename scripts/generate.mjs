// Build-time generator: converts each production *.dc.html Design Component into
// an Astro page + raw head/body fragments. Fidelity is the priority — the inner
// markup, <head> meta, JSON-LD, fonts and inline styles are preserved verbatim;
// the transforms applied are:
//   1. internal href="<File>.dc.html" -> clean slug (retired files -> replacement)
//   2. relative asset paths  assets/... -> /assets/...  (clean URLs are nested)
//   3. trailing-slash normalisation of internal hrefs + absolute site URLs
//   4. shared header/footer from _src/_deploy/partials/ (see injectChrome)
// It also writes public/sitemap.xml from MAP.
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';
import { OG_MAP } from './og-map.mjs';

const SITE = 'https://www.legendary-retreats.com';
const OG_DEFAULT = `${SITE}/assets/brand/og-default.png`;

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, '_src', '_deploy');
const GEN = join(ROOT, 'src', 'generated');
const PAGES = join(ROOT, 'src', 'pages');

// File (without .dc.html) -> clean URL. Trailing slash is canonical (nginx
// serves /<slug>/index.html and 301s the bare form). Slugs for pages moved from
// belegendary.org match its 301 map 1:1 (domain swap + drop the /teams/ prefix).
const MAP = {
  'Legendary Retreats - Home': '/',
  'Ways to Work Together': '/ways-to-work-together/',
  'Destinations': '/destinations/',
  'Retreat - San Juan Mountains': '/destinations/san-juan-mountains-colorado/',
  'Retreat - Moab': '/destinations/moab-utah/',
  'Retreat - Sierra Nevada': '/destinations/sierra-nevada/',
  'Retreat - Great Basin Desert': '/destinations/great-basin-desert/',
  'Retreat - Death Valley': '/destinations/death-valley/',
  'Retreat - Sedona': '/destinations/sedona-arizona/',
  'Retreat - Napa Valley': '/destinations/napa-valley/',
  'Retreat - Lake Tahoe': '/destinations/lake-tahoe/',
  'Retreat - Jackson Hole': '/destinations/jackson-hole-wyoming/',
  'Retreat - Montana': '/destinations/montana/',
  'Formats': '/formats/',
  'Format - Cabin Fever': '/formats/cabin-fever/',
  'Format - Winter Survival': '/formats/winter-survival/',
  'Format - Wilderness Expedition': '/formats/wilderness-expedition/',
  'For Executive Assistants': '/for-executive-assistants/',
  'Luxury Executive Retreat': '/luxury-executive-retreat/',
  'Corporate Retreat Ideas': '/corporate-retreat-ideas/',
  'Executive Offsite Ideas': '/executive-offsite-ideas/',
  'Leadership Retreat Ideas': '/leadership-retreat-ideas/',
  'Executive Immersion': '/executive-immersion/',
  'Executive Immersion - Expedition': '/executive-immersion/expedition/',
  'Executive Immersion - City': '/executive-immersion/city/',
  'Executive Immersion - Ownership': '/executive-immersion/ownership/',
  'Executive Immersion - The City Never Sleeps': '/executive-immersion/the-city-never-sleeps/',
  'Sailing Team Building': '/sailing-team-building/',
  'Executive Off-Road Immersion': '/executive-off-road-immersion/',
  'Retreat Planning Kit': '/retreat-planning-kit/',
  'Guide - How to Plan a Leadership Retreat': '/how-to-plan-a-leadership-retreat/',
  'Guide - How to Plan an Executive Offsite': '/how-to-plan-an-executive-offsite/',
  'Guide - Leadership Offsite Agenda': '/leadership-offsite-agenda/',
  'Guide - Why Offsites Dont Stick': '/why-leadership-offsites-dont-stick/',
  'Guide - Offsite Facilitator': '/leadership-team-offsite-facilitator/',
  'Offsite vs Retreat': '/offsite-vs-executive-retreat/',
  'Offsite vs Team Building': '/offsite-vs-team-building/',
  'Case Studies': '/case-studies/',
  'Case Study - Auto Retailer Egos': '/case-studies/online-auto-retailer-leadership-team/',
  'Case Study - Federal Fiscal Team': '/case-studies/federal-fiscal-leadership-team/',
  'Case Study - Everglades Abundance': '/case-studies/everglades-abundance-mindset/',
  'Case Study - Alaska Vulnerability': '/case-studies/alaska-executive-vulnerability/',
  'Case Study - San Juans Work Ethic': '/case-studies/san-juan-mountains-work-ethic/',
  'Field Notes': '/field-notes/',
  'Field Note - Do Retreats Work': '/field-notes/do-leadership-retreats-work/',
  'Field Note - Two Questions': '/field-notes/two-questions-leadership-retreat/',
  'Field Note - Align Your Team': '/field-notes/align-leadership-team/',
  'Field Note - Questions Before Retreat': '/field-notes/questions-before-executive-retreat/',
  'Field Note - 30 Day Reinforcement': '/field-notes/30-day-reinforcement/',
  'Field Note - What Is An ELR': '/field-notes/what-is-an-experiential-leadership-retreat/',
  'Field Note - Retreat Cost': '/field-notes/executive-retreat-cost/',
  'Field Note - New And Merged Teams': '/field-notes/newly-formed-post-merger-leadership-team/',
  'Field Note - Signature Vs Bespoke': '/field-notes/signature-vs-bespoke-retreat/',
  'About': '/about/',
  'The Experience': '/experience/',
  'Contact': '/contact/',
};

// Retired Design Components (Oct 2026 consolidation). Links that still name
// them resolve straight to the replacement; deploy/nginx.conf 301s the old URLs.
const RETIRED = {
  'Leadership Retreats': '/',
  'Format - Off-Road Immersion': '/executive-off-road-immersion/',
  'Sailing Offsites': '/sailing-team-building/',
  'Executive Offsite Agenda': '/leadership-offsite-agenda/',
  'Executive Offsite Facilitator': '/leadership-team-offsite-facilitator/',
  'Executive Offsites': '/how-to-plan-an-executive-offsite/',
  'Team Offsite Ideas': '/executive-offsite-ideas/',
  'The Framework': 'https://www.belegendary.org/flag-model/',
  'Is This Your Team': 'https://www.belegendary.org/flag-model/',
  'The Connection Deficit': 'https://www.belegendary.org/flag-model/',
};

// Shared chrome: every page carries <!--lr:header--> / <!--lr:footer--> markers
// that are filled from partials/, so nav changes happen in one place.
const PARTIALS = join(SRC, 'partials');
const HEADER = readFileSync(join(PARTIALS, 'header.html'), 'utf8');
const FOOTER = readFileSync(join(PARTIALS, 'footer.html'), 'utf8');
const CHROME_CSS = readFileSync(join(PARTIALS, 'chrome.css'), 'utf8');

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const trim = (url) => url.replace(/^\//, '').replace(/\/$/, '');
const keyFor = (url) => (url === '/' ? 'home' : trim(url).replace(/\//g, '__'));
const pageFileFor = (url) => (url === '/' ? 'index.astro' : `${trim(url)}.astro`);
const depthOf = (url) => (url === '/' ? 1 : trim(url).split('/').length); // ../ count to reach src/

// Article JSON-LD has no date fields in the .dc.html exports, and the articles
// carry no visible on-page date. Derive datePublished (first commit that added
// the source) and dateModified (last commit that touched it) from git so the
// freshness signal stays honest and auto-updates when an article is edited.
// Falls back to today's date if git history is unavailable (e.g. shallow CI).
const TODAY = new Date().toISOString().slice(0, 10);
function gitDate(file, filter) {
  try {
    const out = execSync(
      `git log ${filter} --format=%aI -1 -- "${file}"`,
      { cwd: ROOT, stdio: ['ignore', 'pipe', 'ignore'] }
    ).toString().trim();
    return out ? out.slice(0, 10) : null;
  } catch { return null; }
}
// Performance: let every image decode off the main thread, prioritize the hero
// (the second <img> — the first is the header logo) for a fast LCP, and lazy-load
// everything below the fold (3rd image onward).
function optimizeImages(html) {
  // Attributes the source already sets are left alone.
  let i = 0;
  return html.replace(/<img\s([^>]*)>/g, (_m, attrs) => {
    const idx = i++;
    let extra = '';
    if (!/\bdecoding=/.test(attrs)) extra += 'decoding="async" ';
    if (idx === 1 && !/\bfetchpriority=|\bloading=/.test(attrs)) extra += 'fetchpriority="high" ';
    else if (idx >= 2 && !/\bloading=/.test(attrs)) extra += 'loading="lazy" ';
    return `<img ${extra}${attrs}>`;
  });
}

function injectArticleDates(headHtml, file) {
  // Only Article schema; skip if a date is somehow already present.
  if (!headHtml.includes('"@type":"Article"') || headHtml.includes('"datePublished"')) {
    return headHtml;
  }
  const published = gitDate(file, '--diff-filter=A --follow') || TODAY;
  const modified = gitDate(file, '') || published;
  // Insert right after the Article type declaration (one Article object per page).
  return headHtml.replace(
    '"@type":"Article"',
    `"@type":"Article","datePublished":"${published}","dateModified":"${modified}"`
  );
}

// Add a Speakable signal (voice-assistant / GEO) to every page. The page's main
// heading and standfirst paragraph are the parts worth reading aloud; we target
// the <h1> plus the first <p> after it via cssSelector. Emitted as a standalone
// WebPage node so it never collides with the page's existing JSON-LD.
function injectSpeakable(headHtml, url) {
  const canonical = url === '/' ? `${SITE}/` : `${SITE}${url}`;
  const node = `<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","url":"${canonical}","speakable":{"@type":"SpeakableSpecification","cssSelector":["h1","h1 + p"]}}</script>`;
  return `${headHtml}\n${node}`;
}

// Point og:image + twitter:image at the page-specific share card (1200x630 JPG
// from scripts/og-images.mjs) and declare its dimensions. Unmapped pages keep
// the branded default.
function injectOgImage(headHtml, key) {
  const src = OG_MAP[key];
  if (!src) return headHtml;
  const url = `${SITE}/assets/og/${src.split('/').pop()}.jpg`;
  headHtml = headHtml.split(OG_DEFAULT).join(url);
  return headHtml.replace(
    /<meta property="og:image" content="[^"]*">/i,
    (m) => `${m}<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg">`
  );
}

function extract(html) {
  // --- <head> inner, minus the support.js runtime script ---
  const head = /<head[^>]*>([\s\S]*?)<\/head>/i.exec(html)[1]
    .replace(/<script[^>]*src=["']\.\/support\.js["'][^>]*>\s*<\/script>\s*/i, '');

  // --- <x-dc> inner ---
  const xdc = /<x-dc[^>]*>([\s\S]*?)<\/x-dc>/i.exec(html)[1];
  // helmet block (fonts + page <style> + JSON-LD) -> goes into <head>
  const helmetMatch = /<helmet[^>]*>([\s\S]*?)<\/helmet>/i.exec(xdc);
  const helmet = helmetMatch ? helmetMatch[1] : '';
  // body markup = x-dc inner minus the helmet element
  const body = (helmetMatch ? xdc.replace(helmetMatch[0], '') : xdc).trim();

  return { headHtml: (head.trim() + '\n' + helmet.trim()).trim(), bodyHtml: body };
}

// Old URL paths (retired pages + the pre-trailing-slash forms) that June-era
// markup may still hard-code. Applied after slash normalisation.
const OLD_PATHS = {
  '/leadership-retreats/': '/',
  '/formats/off-road-immersion/': '/executive-off-road-immersion/',
  '/sailing-offsites/': '/sailing-team-building/',
  '/executive-offsite-agenda/': '/leadership-offsite-agenda/',
  '/executive-offsite-facilitator/': '/leadership-team-offsite-facilitator/',
  '/executive-offsites/': '/how-to-plan-an-executive-offsite/',
  '/team-offsite-ideas/': '/executive-offsite-ideas/',
  '/framework/': 'https://www.belegendary.org/flag-model/',
  '/is-this-your-team/': 'https://www.belegendary.org/flag-model/',
  '/the-connection-deficit/': 'https://www.belegendary.org/flag-model/',
};

function rewrite(s) {
  // 1. internal .dc.html links -> clean slugs (allow optional #fragment / ?query)
  for (const [name, url] of [...Object.entries(MAP), ...Object.entries(RETIRED)]) {
    const re = new RegExp(`href="${esc(name)}\\.dc\\.html((?:[#?][^"]*)?)"`, 'g');
    s = s.replace(re, (_m, tail) => `href="${url}${tail}"`);
  }
  // 2. relative asset paths -> absolute (favicons already use /assets and are skipped)
  s = s.replace(/(["'(])assets\//g, '$1/assets/');
  // 3. trailing slash is canonical: internal hrefs and absolute site URLs
  //    (canonical, og:url, JSON-LD) without a file extension get one.
  s = s.replace(/href="(\/[^"#?]*?)((?:[#?][^"]*)?)"/g, (m, path, tail) =>
    /\/$|\.[a-z0-9]+$/i.test(path) ? m : `href="${path}/${tail}"`);
  s = s.replace(/(https:\/\/www\.legendary-retreats\.com\/[^"#?\s<]*?)(?=["#?\s<])/g, (m) =>
    /\/$|\.[a-z0-9]+$/i.test(m) ? m : `${m}/`);
  // 4. retired paths -> their replacement
  s = s.replace(/href="(\/[^"#?]*)((?:[#?][^"]*)?)"/g, (m, path, tail) =>
    OLD_PATHS[path] ? `href="${OLD_PATHS[path]}${OLD_PATHS[path].startsWith('http') ? '' : tail}"` : m);
  return s;
}

function injectChrome(bodyHtml) {
  return bodyHtml
    .replace(/<!--lr:header-->[\s\S]*?<!--\/lr:header-->/, HEADER)
    .replace(/<!--lr:footer-->[\s\S]*?<!--\/lr:footer-->/, FOOTER);
}

// --- reset output dirs (src/pages is fully generated) ---
rmSync(GEN, { recursive: true, force: true });
mkdirSync(GEN, { recursive: true });
rmSync(PAGES, { recursive: true, force: true });
mkdirSync(PAGES, { recursive: true });

const built = [];
for (const [name, url] of Object.entries(MAP)) {
  const file = join(SRC, `${name}.dc.html`);
  if (!existsSync(file)) {
    console.error(`MISSING: ${name}.dc.html`);
    process.exit(1);
  }
  let { headHtml, bodyHtml } = extract(readFileSync(file, 'utf8'));
  if (!bodyHtml.includes('<!--lr:header-->') || !bodyHtml.includes('<!--lr:footer-->')) {
    console.error(`MISSING chrome markers: ${name}.dc.html`);
    process.exit(1);
  }
  headHtml = `${headHtml}\n<style>${CHROME_CSS}</style>`;
  headHtml = rewrite(headHtml);
  headHtml = injectArticleDates(headHtml, file);
  headHtml = injectOgImage(headHtml, keyFor(url));
  headHtml = injectSpeakable(headHtml, url);
  bodyHtml = rewrite(injectChrome(bodyHtml));
  bodyHtml = optimizeImages(bodyHtml);

  const key = keyFor(url);
  writeFileSync(join(GEN, `${key}.head.html`), headHtml);
  writeFileSync(join(GEN, `${key}.body.html`), bodyHtml);

  // --- emit the Astro page ---
  const prefix = '../'.repeat(depthOf(url)); // from page file location back to src/
  const pageOut = join(PAGES, pageFileFor(url));
  mkdirSync(dirname(pageOut), { recursive: true });
  writeFileSync(pageOut, `---
import Base from '${prefix}layouts/Base.astro';
import head from '${prefix}generated/${key}.head.html?raw';
import body from '${prefix}generated/${key}.body.html?raw';
---
<Base headHtml={head}><Fragment set:html={body} /></Base>
`);
  built.push({ name, url, key, file });
}

// --- sitemap.xml from the page map (lastmod = last commit touching the source) ---
const urls = built.map(({ url, file }) =>
  `  <url><loc>${SITE}${url}</loc><lastmod>${gitDate(file, '') || TODAY}</lastmod></url>`);
writeFileSync(join(ROOT, 'public', 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`);

console.log(`Generated ${built.length} pages (+ sitemap.xml):`);
for (const b of built) console.log(`  ${b.url.padEnd(52)} <- ${b.name}.dc.html`);
