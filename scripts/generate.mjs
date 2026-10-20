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
import { SITE_CONFIG } from '../site.config.mjs';

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
  'Press': '/press/',
  'Executive Retreat Planners': '/executive-retreat-planners/',
  'Board Retreat': '/board-retreat/',
  'Strategic Planning Retreat': '/strategic-planning-retreat/',
  'Not Found': '/404/', // -> src/pages/404.astro -> dist/404.html (nginx error_page)
};
const NOT_FOUND_URL = '/404/';

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
// Pixel width of a .webp file, read from its header (VP8, VP8L or VP8X).
function webpWidth(file) {
  try {
    const b = readFileSync(file);
    const kind = b.toString('ascii', 12, 16);
    if (kind === 'VP8X') return 1 + b.readUIntLE(24, 3);
    if (kind === 'VP8L') return 1 + (b.readUInt16LE(21) & 0x3fff);
    if (kind === 'VP8 ') return b.readUInt16LE(26) & 0x3fff;
  } catch { /* unreadable: no srcset */ }
  return 0;
}

// Phone- and tablet-sized copies made by scripts/image-variants.mjs.
function heroSrcset(src) {
  const m = src.match(/^\/?(assets\/.+)\.webp$/);
  if (!m) return '';
  const base = join(ROOT, 'public', m[1]);
  const full = webpWidth(`${base}.webp`);
  if (!full) return '';
  const set = [800, 1280]
    .filter((w) => existsSync(`${base}-${w}w.webp`))
    .map((w) => `/${m[1]}-${w}w.webp ${w}w`);
  return set.length ? `${set.join(', ')}, /${m[1]}.webp ${full}w` : '';
}

// Performance: let every image decode off the main thread, prioritize the hero
// (the second <img> — the first is the header logo) for a fast LCP, give it a
// phone-sized srcset, and lazy-load everything below the fold (3rd image onward).
function optimizeImages(html) {
  // Attributes the source already sets are left alone.
  let i = 0;
  return html.replace(/<img\s([^>]*)>/g, (_m, attrs) => {
    const idx = i++;
    let extra = '';
    if (!/\bdecoding=/.test(attrs)) extra += 'decoding="async" ';
    const hero = /\bfetchpriority="high"/.test(attrs) || (idx === 1 && !/\bloading=/.test(attrs));
    if (idx === 1 && !/\bfetchpriority=|\bloading=/.test(attrs)) extra += 'fetchpriority="high" ';
    else if (idx >= 2 && !/\bloading=/.test(attrs)) extra += 'loading="lazy" ';
    if (hero && !/\bsrcset=/.test(attrs)) {
      const src = (attrs.match(/\bsrc="([^"]+)"/) || [])[1] || '';
      const set = heroSrcset(src);
      if (set) extra += `srcset="${set}" sizes="100vw" `;
    }
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
  const node = `<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","url":"${canonical}","speakable":{"@type":"SpeakableSpecification","cssSelector":["h1","h1 + p",".bl-speakable"]}}</script>`;
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

// GA4 + Clarity (IDs from site.config.mjs; nothing is emitted while both are
// empty). Libraries load lazily on first interaction or shortly after load so
// they stay off the LCP path; gtag/clarity queue calls made before that. Three
// conversions are reported to both tools:
//   generate_lead   — retreat inquiry form submitted (inquiryFormGuid)
//   kit_download    — planning-kit form submitted, or the PDF link clicked
//   meetings_click  — any link to the HubSpot meetings scheduler
// Lead source: the HubSpot tracking code (same lazy load) fills each contact's
// Original Traffic Source and First Page Seen. Clicks on the meetings link carry
// the visit's landing UTMs (kept for the session) plus utm_content = the page
// clicked from, which HubSpot stores as the meeting booking's source.
const C = SITE_CONFIG;
const ANALYTICS = !(C.ga4 || C.clarity) ? '' : `<script>(function(){
var GA=${JSON.stringify(C.ga4)},CL=${JSON.stringify(C.clarity)},HS=${JSON.stringify(C.hubspotPortal)},HR=${JSON.stringify(C.hubspotRegion)},KIT=${JSON.stringify(C.kitFormGuid)},INQ=${JSON.stringify(C.inquiryFormGuid)};
var UTM={};try{var q=new URLSearchParams(location.search),k=['utm_source','utm_medium','utm_campaign','utm_term'];k.forEach(function(n){if(q.get(n))UTM[n]=q.get(n)});
if(Object.keys(UTM).length)sessionStorage.setItem('lr_utm',JSON.stringify(UTM));else UTM=JSON.parse(sessionStorage.getItem('lr_utm')||'{}');}catch(_){}
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}window.gtag=window.gtag||gtag;
if(GA){gtag('js',new Date());gtag('config',GA);}
if(CL){window.clarity=window.clarity||function(){(window.clarity.q=window.clarity.q||[]).push(arguments)};}
var done=false;function load(){if(done)return;done=true;
if(GA){var g=document.createElement('script');g.async=true;g.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(g);}
if(CL){var c=document.createElement('script');c.async=true;c.src='https://www.clarity.ms/tag/'+CL;document.head.appendChild(c);}
if(HS){var h=document.createElement('script');h.async=true;h.defer=true;h.id='hs-script-loader';h.src='https://js'+(HR&&HR!=='na1'?'-'+HR:'')+'.hs-scripts.com/'+HS+'.js';document.head.appendChild(h);}}
['pointerdown','keydown','scroll','touchstart'].forEach(function(e){addEventListener(e,load,{once:true,passive:true})});
addEventListener('load',function(){setTimeout(load,1500)});
function track(name,p){p=p||{};p.page_path=location.pathname;if(GA)gtag('event',name,p);if(CL)window.clarity('event',name);}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.href;
var where=a.closest('header')?'header':a.closest('footer')?'footer':'body';
if(/meetings(-na2)?\\.hubspot\\.com\\/jcarter28/.test(h)){track('meetings_click',{link_location:where,link_text:(a.textContent||'').trim().slice(0,60)});
try{var u=new URL(h);if(!u.searchParams.has('utm_source')){u.searchParams.set('utm_source',UTM.utm_source||'legendary-retreats.com');u.searchParams.set('utm_medium',UTM.utm_medium||'website');u.searchParams.set('utm_campaign',UTM.utm_campaign||'site_cta');if(UTM.utm_term)u.searchParams.set('utm_term',UTM.utm_term);u.searchParams.set('utm_content',location.pathname);a.href=u.toString();}}catch(_){}}
else if(/complete-retreat-planning-kit\\.pdf/.test(h))track('kit_download',{method:'direct_link'});},true);
function submitted(id){if(id&&id===KIT)track('kit_download',{method:'form'});else if(id&&INQ&&id===INQ)track('generate_lead',{form:'retreat_inquiry'});else track('form_submit',{form_id:id||'unknown'});}
addEventListener('message',function(e){var d=e.data;if(d&&d.type==='hsFormCallback'&&d.eventName==='onFormSubmitted')submitted(d.id);});
addEventListener('hs-form-event:on-submission:success',function(e){var id='';try{id=window.HubSpotFormsV4.getFormFromEvent(e).getFormId();}catch(_){id=(e.detail&&e.detail.formId)||'';}submitted(id);});
})();</script>`;
if (ANALYTICS) {
  // Fail the build rather than ship a script that throws (e.g. a lost escape).
  try { new Function(ANALYTICS.replace(/^<script>|<\/script>$/g, '')); }
  catch (e) { console.error('Analytics snippet is not valid JS:', e.message); process.exit(1); }
}
if (!ANALYTICS) console.warn('WARNING: site.config.mjs has no GA4/Clarity IDs, so analytics are OFF (launch blocker).');

// Retreat inquiry: once a HubSpot form GUID is configured, the home page's
// <!--lr:inquiry--> block (meetings-link CTA) becomes the embedded form.
// The call link stays visible under the form: if HubSpot is slow or blocked
// (ad blockers, corporate filters) the visitor still has a way to act.
const MEETINGS_URL = 'https://meetings-na2.hubspot.com/jcarter28';
const INQUIRY_FORM = C.inquiryFormGuid
  ? `<div class="hs-form-frame" data-region="${C.hubspotRegion}" data-form-id="${C.inquiryFormGuid}" data-portal-id="${C.hubspotPortal}" style="min-height:380px;"></div>` +
    `<script defer src="https://js-${C.hubspotRegion}.hsforms.net/forms/embed/${C.hubspotPortal}.js"></script>` +
    `<noscript><p class="lr-plan__alt">The form needs JavaScript. <a href="${MEETINGS_URL}">Book a 15-minute call with James</a> instead.</p></noscript>` +
    `<p class="lr-plan__alt">Prefer to talk? <a href="${MEETINGS_URL}" target="_blank" rel="noopener" data-lr-plan>Book a 15-minute call with James</a></p>`
  : null;

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
  const isNotFound = url === NOT_FOUND_URL;
  headHtml = `${headHtml}\n<style>${CHROME_CSS}</style>${ANALYTICS}`;
  headHtml = rewrite(headHtml);
  headHtml = injectArticleDates(headHtml, file);
  headHtml = injectOgImage(headHtml, keyFor(url));
  if (!isNotFound) headHtml = injectSpeakable(headHtml, url);
  bodyHtml = rewrite(injectChrome(bodyHtml));
  if (INQUIRY_FORM) bodyHtml = bodyHtml.replace(/<!--lr:inquiry-->[\s\S]*?<!--\/lr:inquiry-->/, INQUIRY_FORM);
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
  if (!isNotFound) built.push({ name, url, key, file });
}

// --- sitemap.xml from the page map (lastmod = last commit touching the source) ---
const urls = built.map(({ url, file }) =>
  `  <url><loc>${SITE}${url}</loc><lastmod>${gitDate(file, '') || TODAY}</lastmod></url>`);
writeFileSync(join(ROOT, 'public', 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`);

console.log(`Generated ${built.length} pages + 404 (+ sitemap.xml):`);
for (const b of built) console.log(`  ${b.url.padEnd(52)} <- ${b.name}.dc.html`);
