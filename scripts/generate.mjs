// Build-time generator: converts each production *.dc.html Design Component into
// an Astro page + raw head/body fragments. Fidelity is the priority — the inner
// markup, <head> meta, JSON-LD, fonts and inline styles are preserved verbatim;
// only two transforms are applied:
//   1. internal href="<File>.dc.html" -> clean slug (README §3)
//   2. relative asset paths  assets/... -> /assets/...  (clean URLs are nested)
// The "Ways to Work Together" page gets the dial wired as a Preact island.
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

// File (without .dc.html) -> clean URL. From README §3 / seo/redirects.md.
const MAP = {
  'Legendary Retreats - Home': '/',
  'Leadership Retreats': '/leadership-retreats',
  'Ways to Work Together': '/ways-to-work-together',
  'The Framework': '/framework',
  'Is This Your Team': '/is-this-your-team',
  'Destinations': '/destinations',
  'Retreat - San Juan Mountains': '/destinations/san-juan-mountains-colorado',
  'Retreat - Moab': '/destinations/moab-utah',
  'Retreat - Sierra Nevada': '/destinations/sierra-nevada',
  'Retreat - Great Basin Desert': '/destinations/great-basin-desert',
  'Retreat - Death Valley': '/destinations/death-valley',
  'Retreat - Sedona': '/destinations/sedona-arizona',
  'Retreat - Napa Valley': '/destinations/napa-valley',
  'Retreat - Lake Tahoe': '/destinations/lake-tahoe',
  'Retreat - Jackson Hole': '/destinations/jackson-hole-wyoming',
  'Retreat - Montana': '/destinations/montana',
  'Format - Cabin Fever': '/formats/cabin-fever',
  'Format - Off-Road Immersion': '/formats/off-road-immersion',
  'Format - Winter Survival': '/formats/winter-survival',
  'Format - Wilderness Expedition': '/formats/wilderness-expedition',
  'Sailing Offsites': '/sailing-offsites',
  'Executive Offsites': '/executive-offsites',
  'Executive Offsite Facilitator': '/executive-offsite-facilitator',
  'For Executive Assistants': '/for-executive-assistants',
  'The Connection Deficit': '/the-connection-deficit',
  'Offsite vs Retreat': '/offsite-vs-executive-retreat',
  'Offsite vs Team Building': '/offsite-vs-team-building',
  'Team Offsite Ideas': '/team-offsite-ideas',
  'Executive Offsite Agenda': '/executive-offsite-agenda',
  'Case Studies': '/case-studies',
  'Case Study - Auto Retailer Egos': '/case-studies/online-auto-retailer-leadership-team',
  'Case Study - Federal Fiscal Team': '/case-studies/federal-fiscal-leadership-team',
  'Case Study - Everglades Abundance': '/case-studies/everglades-abundance-mindset',
  'Case Study - Alaska Vulnerability': '/case-studies/alaska-executive-vulnerability',
  'Case Study - San Juans Work Ethic': '/case-studies/san-juan-mountains-work-ethic',
  'Field Notes': '/field-notes',
  'Field Note - Do Retreats Work': '/field-notes/do-leadership-retreats-work',
  'Field Note - Two Questions': '/field-notes/two-questions-leadership-retreat',
  'Field Note - Align Your Team': '/field-notes/align-leadership-team',
  'Field Note - Questions Before Retreat': '/field-notes/questions-before-executive-retreat',
  'Field Note - 30 Day Reinforcement': '/field-notes/30-day-reinforcement',
  'Field Note - What Is An ELR': '/field-notes/what-is-an-experiential-leadership-retreat',
  'Field Note - Retreat Cost': '/field-notes/executive-retreat-cost',
  'Field Note - New And Merged Teams': '/field-notes/newly-formed-post-merger-leadership-team',
  'Field Note - Signature Vs Bespoke': '/field-notes/signature-vs-bespoke-retreat',
  'About': '/about',
  'The Experience': '/experience',
  'Contact': '/contact',
};

const DIAL_PAGE = 'Ways to Work Together';
const DIAL_MARKER = '<!--LEGENDARY_DIAL-->';

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const keyFor = (url) => (url === '/' ? 'home' : url.replace(/^\//, '').replace(/\//g, '__'));
const pageFileFor = (url) => (url === '/' ? 'index.astro' : `${url.replace(/^\//, '')}.astro`);
const depthOf = (url) => (url === '/' ? 1 : url.replace(/^\//, '').split('/').length); // ../ count to reach src/

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
  let i = 0;
  return html.replace(/<img\s/g, () => {
    const idx = i++;
    let extra = 'decoding="async" ';
    if (idx === 1) extra += 'fetchpriority="high" ';
    else if (idx >= 2) extra += 'loading="lazy" ';
    return '<img ' + extra;
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

function rewrite(s) {
  // 1. internal .dc.html links -> clean slugs (allow optional #fragment / ?query)
  for (const [name, url] of Object.entries(MAP)) {
    const re = new RegExp(`href="${esc(name)}\\.dc\\.html((?:[#?][^"]*)?)"`, 'g');
    s = s.replace(re, (_m, tail) => `href="${url}${tail}"`);
  }
  // 2. relative asset paths -> absolute (favicons already use /assets and are skipped)
  s = s.replace(/(["'(])assets\//g, '$1/assets/');
  return s;
}

// --- reset output dirs ---
rmSync(GEN, { recursive: true, force: true });
mkdirSync(GEN, { recursive: true });

const built = [];
for (const [name, url] of Object.entries(MAP)) {
  const file = join(SRC, `${name}.dc.html`);
  if (!existsSync(file)) {
    console.error(`MISSING: ${name}.dc.html`);
    process.exit(1);
  }
  let { headHtml, bodyHtml } = extract(readFileSync(file, 'utf8'));
  headHtml = rewrite(headHtml);
  headHtml = injectArticleDates(headHtml, file);
  headHtml = injectOgImage(headHtml, keyFor(url));
  headHtml = injectSpeakable(headHtml, url);
  bodyHtml = rewrite(bodyHtml);
  bodyHtml = optimizeImages(bodyHtml);

  const isDial = name === DIAL_PAGE;
  if (isDial) {
    // Replace the <dc-import name="Legendary Dials"> with an island marker.
    bodyHtml = bodyHtml.replace(
      /<dc-import\b[^>]*name="Legendary Dials"[^>]*>\s*<\/dc-import>/i,
      DIAL_MARKER
    );
    if (!bodyHtml.includes(DIAL_MARKER)) {
      console.error('Dial marker not inserted into Ways to Work Together');
      process.exit(1);
    }
  }

  const key = keyFor(url);
  writeFileSync(join(GEN, `${key}.head.html`), headHtml);
  writeFileSync(join(GEN, `${key}.body.html`), bodyHtml);

  // --- emit the Astro page ---
  const prefix = '../'.repeat(depthOf(url)); // from page file location back to src/
  const pageOut = join(PAGES, pageFileFor(url));
  mkdirSync(dirname(pageOut), { recursive: true });

  let astro;
  if (isDial) {
    astro = `---
import Base from '${prefix}layouts/Base.astro';
import LegendaryDial from '${prefix}components/LegendaryDial.jsx';
import head from '${prefix}generated/${key}.head.html?raw';
import body from '${prefix}generated/${key}.body.html?raw';
const [before, after] = body.split('${DIAL_MARKER}');
---
<Base headHtml={head}>
  <Fragment set:html={before} />
  <LegendaryDial client:visible />
  <Fragment set:html={after} />
</Base>
`;
  } else {
    astro = `---
import Base from '${prefix}layouts/Base.astro';
import head from '${prefix}generated/${key}.head.html?raw';
import body from '${prefix}generated/${key}.body.html?raw';
---
<Base headHtml={head}><Fragment set:html={body} /></Base>
`;
  }
  writeFileSync(pageOut, astro);
  built.push({ name, url, key, page: pageFileFor(url) });
}

console.log(`Generated ${built.length} pages:`);
for (const b of built) console.log(`  ${b.url.padEnd(52)} <- ${b.name}.dc.html`);
