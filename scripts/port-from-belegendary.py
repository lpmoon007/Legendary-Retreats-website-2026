#!/usr/bin/env python3
"""One-time port of the retreat pages from belegendary.org into this repo's
Design Component source (_src/_deploy/*.dc.html).

The Be Legendary site is component-built Astro, so its .astro source cannot be
copied in. Instead this reads the RENDERED pages from a Be Legendary build
(`npx astro build` in that repo -> dist/), which captures the current copy,
schema, keep-reading rails and FAQs exactly as they ship today, and rewrites
them into the .dc.html shape scripts/generate.mjs consumes:

  * keeps the page body between the Be Legendary site header and footer
  * recolors the Be Legendary palette to Legendary Retreats' (context-aware:
    the rust accent becomes wine on light sections, gold on dark ones)
  * rewrites links: moved pages -> local slugs, /book/ -> the meetings link,
    everything that stays on belegendary.org -> absolute URL (new tab)
  * rebrands titles / breadcrumbs / JSON-LD to the Legendary Retreats entity
  * copies every referenced image (and the planning-kit PDF, same path)
  * inlines the small bundled scripts so pages carry no /_astro/ dependency

Re-runnable: rebuild Be Legendary, then
  python3 scripts/port-from-belegendary.py <be-legendary-repo-dir>
then `npm run generate`. Pages listed in PAGES are overwritten.
"""
import json
import re
import shutil
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_src' / '_deploy'
PUBLIC = ROOT / 'public'
SITE = 'https://www.legendary-retreats.com'
BL = 'https://www.belegendary.org'
MEETINGS = 'https://meetings-na2.hubspot.com/jcarter28'

# Be Legendary rendered path -> (Design Component name, Legendary Retreats URL)
PAGES = {
    'teams/retreats/destinations': ('Destinations', '/destinations/'),
    'teams/retreats/formats': ('Formats', '/formats/'),
    'teams/retreats/ways-to-work-together': ('Ways to Work Together', '/ways-to-work-together/'),
    'teams/retreats/for-executive-assistants': ('For Executive Assistants', '/for-executive-assistants/'),
    'teams/luxury-executive-retreat': ('Luxury Executive Retreat', '/luxury-executive-retreat/'),
    'teams/corporate-retreat-ideas': ('Corporate Retreat Ideas', '/corporate-retreat-ideas/'),
    'teams/executive-offsite-ideas': ('Executive Offsite Ideas', '/executive-offsite-ideas/'),
    'teams/leadership-retreat-ideas': ('Leadership Retreat Ideas', '/leadership-retreat-ideas/'),
    'teams/executive-immersion': ('Executive Immersion', '/executive-immersion/'),
    'teams/executive-immersion/expedition': ('Executive Immersion - Expedition', '/executive-immersion/expedition/'),
    'teams/executive-immersion/city': ('Executive Immersion - City', '/executive-immersion/city/'),
    'teams/executive-immersion/ownership': ('Executive Immersion - Ownership', '/executive-immersion/ownership/'),
    'teams/executive-immersion/the-city-never-sleeps': ('Executive Immersion - The City Never Sleeps', '/executive-immersion/the-city-never-sleeps/'),
    'sailing-team-building': ('Sailing Team Building', '/sailing-team-building/'),
    'executive-off-road-immersion': ('Executive Off-Road Immersion', '/executive-off-road-immersion/'),
    'retreat-planning-kit': ('Retreat Planning Kit', '/retreat-planning-kit/'),
    'case-studies/online-auto-retailer-leadership-team': ('Case Study - Auto Retailer Egos', '/case-studies/online-auto-retailer-leadership-team/'),
    'case-studies/san-juan-mountains-work-ethic': ('Case Study - San Juans Work Ethic', '/case-studies/san-juan-mountains-work-ethic/'),
    'case-studies/everglades-abundance-mindset': ('Case Study - Everglades Abundance', '/case-studies/everglades-abundance-mindset/'),
    'case-studies/federal-fiscal-leadership-team': ('Case Study - Federal Fiscal Team', '/case-studies/federal-fiscal-leadership-team/'),
    'case-studies/alaska-executive-vulnerability': ('Case Study - Alaska Vulnerability', '/case-studies/alaska-executive-vulnerability/'),
    'how-to-plan-a-leadership-retreat': ('Guide - How to Plan a Leadership Retreat', '/how-to-plan-a-leadership-retreat/'),
    'how-to-plan-an-executive-offsite': ('Guide - How to Plan an Executive Offsite', '/how-to-plan-an-executive-offsite/'),
    'leadership-offsite-agenda': ('Guide - Leadership Offsite Agenda', '/leadership-offsite-agenda/'),
    'why-leadership-offsites-dont-stick': ('Guide - Why Offsites Dont Stick', '/why-leadership-offsites-dont-stick/'),
    'leadership-team-offsite-facilitator': ('Guide - Offsite Facilitator', '/leadership-team-offsite-facilitator/'),
    # Not published as-is: section sources for the new homepage.
    'teams/retreats': ('_port - Retreats Hub', None),
    'home-preview': ('_port - Home Preview', None),
}

# Be Legendary internal path -> Legendary Retreats path (moved content).
MOVED = {'/' + k + '/': v for k, (_, v) in PAGES.items() if v}
MOVED.update({
    '/teams/retreats/': '/',
    '/case-studies/': '/case-studies/',
    '/field-notes/': '/field-notes/',
    '/resources/': '/field-notes/',
    '/about/james-carter/': '/about/',
    '/contact/': '/contact/',
    '/assets/downloads/complete-retreat-planning-kit.pdf': '/assets/downloads/complete-retreat-planning-kit.pdf',
})
BOOK_PATHS = {'/book/'}

# ── palette ───────────────────────────────────────────────────────────────────
# Neutrals: Be Legendary -> Legendary Retreats (same role, LR's warmer values).
NEUTRAL = {
    '#15130E': '#141210', '#1B1810': '#1C1A17', '#211D15': '#24201B',
    '#100E0A': '#0E0D0B', '#191610': '#1A1714', '#2A2620': '#2B2722',
    '#F4F0E7': '#EFE9DD', '#FBF8F1': '#FBF7EF', '#EFE8DA': '#E8E0D0',
    '#F6F1E7': '#F6EFE0', '#FBF9F4': '#FBF7EF', '#F4EFE5': '#F1EADF',
}
ACCENTS = {'#C04A26', '#E0744A', '#D98A5E', '#9E3A1C'}
WINE, WINE_DEEP, GOLD, GOLD_DEEP = '#64010a', '#4A0108', '#E0B973', '#C9A35E'
INK = '#1C1A17'
RUST_RGB = '192,74,38'
GOLD_RGB, WINE_RGB = '224,185,115', '100,1,10'
WHITES = {'#FFF', '#FFFFFF', '#FBF8F1', '#FBF7EF', '#F4F0E7', '#EFE9DD', 'WHITE', '#FBF3E7'}

HEX_RE = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b')


def hex_lum(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def bg_is_dark(style):
    """None if the style sets no opaque background, else True/False."""
    m = re.search(r'background(?:-color)?\s*:\s*([^;]+)', style or '')
    if not m:
        return None
    v = m.group(1)
    hx = HEX_RE.search(v)
    rg = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', v)
    first = None
    if hx and (not rg or hx.start() < rg.start()):
        first = hex_lum(hx.group(0))
    elif rg:
        a = float(rg.group(4)) if rg.group(4) else 1.0
        if a < 0.5:
            return None
        first = (0.2126 * int(rg.group(1)) + 0.7152 * int(rg.group(2)) + 0.0722 * int(rg.group(3))) / 255
    if first is None:
        return None
    return first < 0.45


def recolor_value(prop, val, dark):
    def sub_hex(m):
        h = m.group(0).upper()
        if h in NEUTRAL:
            return NEUTRAL[h]
        if h in ACCENTS:
            if prop.startswith('background'):
                if dark:
                    return GOLD_DEEP if h == '#9E3A1C' else GOLD
                return WINE_DEEP if h == '#9E3A1C' else WINE
            return GOLD if dark else WINE
        return m.group(0)
    val = HEX_RE.sub(sub_hex, val)
    val = re.sub(r'rgba\(\s*192\s*,\s*74\s*,\s*38', 'rgba(' + (GOLD_RGB if dark else WINE_RGB), val)
    return val


def recolor_style(style, dark, only=None):
    """Recolor declarations. only='bg' touches backgrounds, 'fg' everything else."""
    out = []
    for decl in style.split(';'):
        if ':' not in decl:
            out.append(decl)
            continue
        prop, val = decl.split(':', 1)
        p = prop.strip().lower()
        is_bg = p.startswith('background') or p.endswith('shadow')  # judged against the parent
        if only == 'bg' and not is_bg or only == 'fg' and is_bg:
            out.append(decl)
            continue
        out.append(prop + ':' + recolor_value(p, val, dark))
    return ';'.join(out)


def recolor_css(css, dark=True):
    """Stylesheets have no element context; treat accents per `dark`."""
    def rule(m):
        return m.group(1) + recolor_style(m.group(2), dark) + '}'
    return re.sub(r'(\{)([^{}]*)\}', rule, css)


def recolor_tree(node, dark):
    for el in node.find_all(recursive=False):
        style = el.get('style', '')
        ctx = dark
        if style:
            # Backgrounds are mapped against the PARENT's context; the element's
            # own (new) background then sets the context for its text and children.
            new = recolor_style(style, dark, only='bg')
            own = bg_is_dark(new)
            ctx = dark if own is None else own
            new = recolor_style(new, ctx, only='fg')
            # An accent background flipped to gold needs dark text.
            if re.search(r'background(?:-color)?\s*:\s*' + GOLD, new, re.I):
                new = re.sub(r'(^|;)(\s*)color\s*:\s*([^;]+)',
                             lambda m: m.group(1) + m.group(2) + 'color:' + (INK if m.group(3).strip().upper() in WHITES else m.group(3)),
                             new)
            el['style'] = new
        for attr in ('fill', 'stroke', 'stop-color', 'color'):
            if el.has_attr(attr):
                el[attr] = recolor_value('color', el[attr], ctx)
        # Inline hover handlers (this.style.background='#C04A26') need the same map.
        for attr in ('onmouseover', 'onmouseout', 'onfocus', 'onblur'):
            if el.has_attr(attr):
                el[attr] = re.sub(
                    r"style\.(\w+)\s*=\s*'([^']*)'",
                    lambda m: f"style.{m.group(1)}='" + recolor_value(
                        'background' if m.group(1).startswith('background') else 'color',
                        m.group(2), dark if m.group(1).startswith('background') else ctx) + "'",
                    el[attr])
        recolor_tree(el, ctx)


# ── links ─────────────────────────────────────────────────────────────────────
def map_href(href):
    """Return (new_href, external_bl)."""
    if not href or not href.startswith('/') or href.startswith('//'):
        return href, False
    path, sep, frag = re.match(r'([^#?]*)([#?]?)(.*)', href).groups()
    tail = (sep + frag) if sep else ''
    if path in BOOK_PATHS:
        return MEETINGS, False
    if path in MOVED:
        return MOVED[path] + tail, False
    if path == '/':
        return BL + '/' + tail, True
    return BL + path + tail, True


# Absolute links that point somewhere better on this domain: the CNN Money
# piece is live again on cnn.com, and press coverage has its own page here.
LINK_FIXES = {
    'https://web.archive.org/web/20180827210716/https://money.cnn.com/2018/08/27/pf/executive-retreats/index.html':
        'https://www.cnn.com/2018/09/30/success/executive-retreats',
    'https://www.belegendary.org/press/': '/press/',
    '/press/': '/press/',
}


def rewrite_links(soup):
    for a in soup.find_all('a', href=True):
        if a['href'] in LINK_FIXES:
            a['href'] = LINK_FIXES[a['href']]
            if a['href'].startswith('/'):
                del a['target']
                del a['rel']
            continue
        new, ext = map_href(a['href'])
        a['href'] = new
        if ext or new == MEETINGS:
            a['target'] = '_blank'
            a['rel'] = 'noopener'


# Copy that names the seller: on this domain the seller is Legendary Retreats.
TEXT_FIXES = [
    ('Founder of Be Legendary and creator of the Flag Model', 'Founder of Legendary Retreats and Be Legendary, and creator of the Flag Model'),
    ('a full Be Legendary retreat', 'a full Legendary Retreat'),
    ('Be Legendary designs and delivers', 'Legendary Retreats designs and delivers'),
    ('Be Legendary runs three levels', 'Legendary Retreats runs three levels'),
    ('introduce Be Legendary to your principal', 'introduce us to your principal'),
]


# Tier prices on legendary-retreats.com: Focused $35K-$50K, Signature
# $45K-$150K (Be Legendary still publishes $25K-$50K and $35K-$100K).
# Raw-string swaps so visible copy, meta and JSON-LD all match. Order matters:
# Signature is rewritten before Focused so the new $35K floor isn't re-matched.
# The Business Insider headline ("$25,000 Executive Getaways") is a quote: untouched.
PRICE_FIXES = [
    ('$35,000–$100,000', '$45,000–$150,000'),
    ('$35,000-$100,000', '$45,000-$150,000'),
    ('$35,000 to $100,000', '$45,000 to $150,000'),
    ('$35k–$100k', '$45k–$150k'),
    ('$35K–$100K', '$45K–$150K'),
    ('"name":"Signature Retreat","priceCurrency":"USD","price":"35000"',
     '"name":"Signature Retreat","priceCurrency":"USD","price":"45000"'),
    ('$25,000–$50,000', '$35,000–$50,000'),
    ('$25,000-$50,000', '$35,000-$50,000'),
    ('$25,000 to $50,000', '$35,000 to $50,000'),
    ('$25k–$50k', '$35k–$50k'),
    ('$25K–$50K', '$35K–$50K'),
    ('$25,000–$100,000', '$35,000–$150,000'),
    ('about $25,000 for a Focused', 'about $35,000 for a Focused'),
    ('"name":"Focused Retreat","priceCurrency":"USD","price":"25000"',
     '"name":"Focused Retreat","priceCurrency":"USD","price":"35000"'),
]


def fix_prices(text):
    for a, b in PRICE_FIXES:
        text = text.replace(a, b)
    return text


def fix_text(soup):
    for t in soup.find_all(string=True):
        new = str(t)
        for a, b in TEXT_FIXES:
            new = new.replace(a, b)
        if new != t:
            t.replace_with(new)


# "Calibration Call" is Be Legendary's diagnostic-call language; on the retreat
# site the call is a planning conversation. Primary CTA: "Plan your retreat";
# single-day experience pages (not retreats) say "Book a call".
CALL_SENTENCES = [
    ('See where your team breaks first.', 'Shape your retreat in 15 minutes.'),
    ("A Calibration Call is 15 minutes — you leave with a concrete read on your team, whether or not we work together. It's a calibration, not a pitch.",
     'Fifteen minutes with James. You leave with a clear shape for the retreat: the outcome, the format and an honest range, whether or not we work together. No pitch.'),
    ('We start with a calibration call to find the one outcome', 'We start with a 15-minute call to find the one outcome'),
    ("A Calibration Call is 15 minutes — you'll leave knowing which discipline your team most needs to work on, whether or not we work together.",
     "In a 15-minute call with James you'll leave knowing the one outcome worth building the offsite around, whether or not we work together."),
    ('A Calibration Call is 15 minutes. You\'ll leave knowing which discipline your team most needs to change in the operating rhythm — so the next offsite holds, whether or not we work together.',
     'Book a 15-minute call with James. You\'ll leave knowing the one thing your team needs to change for the next offsite to hold, whether or not we work together.'),
    ('free 15-minute Calibration Call', 'free 15-minute call'),
]
DAY_PAGES = ('teams/executive-immersion', 'executive-off-road-immersion', 'sailing-team-building')


def retreat_voice(soup, bl_path):
    cta = 'Book a call' if bl_path.startswith(DAY_PAGES) else 'Plan your retreat'
    # "A <strong>Calibration Call</strong> is 15 minutes. Tell us ..."
    for st in soup.find_all('strong'):
        if st.get_text(strip=True) == 'Calibration Call':
            st.string = 'call with James'
            nxt = st.next_sibling
            if isinstance(nxt, NavigableString) and nxt.startswith(' is 15 minutes.'):
                nxt.replace_with(nxt.replace(' is 15 minutes.', ' takes 15 minutes.', 1))
    for t in soup.find_all(string=True):
        new = str(t)
        for a, b in CALL_SENTENCES:
            new = new.replace(a, b)
        new = new.replace('Book a Calibration Call', cta)
        if new != t:
            t.replace_with(new)
    left = [t for t in soup.find_all(string=re.compile('[Cc]alibration'))]
    if left:
        print('  ! unconverted "Calibration" copy:', [str(t)[:80] for t in left])


# Extra sections inserted into specific ported pages, after the first element
# whose text contains the anchor. Source lives in _src/_deploy/extras/.
# mode 'after' inserts after the anchor's section; 'replace' swaps it out.
PAGE_EXTRAS = {
    'teams/luxury-executive-retreat': [('The trap of the beautiful off-site', 'luxury-gallery.html', 'after'),
                                       ('Where the work happens.', 'press-strip.html', 'after')],
    'teams/retreats/ways-to-work-together': [('Three ways to run a legendary retreat.', 'press-strip.html', 'after')],
    'teams/retreats/for-executive-assistants': [('After hundreds of luxury retreats', 'press-strip.html', 'after')],
    'teams/retreats/destinations': [('Somewhere farther afield', 'destinations-worldwide.html', 'replace')],
}


# Full-bleed photo hero: the page's breadcrumb + <h1> move onto the photo; the
# rest of the original header (e.g. "The short answer") stays below it.
PHOTO_HEROES = {
    'teams/luxury-executive-retreat': {
        'src': '/assets/lr-lodge.webp', 'width': 1800, 'height': 655,
        'alt': 'A five-star mountain estate at golden hour',
        'eyebrow': 'Luxury executive retreats',
        # Images the hero (or the gallery) already shows, dropped from the body.
        'drop_imgs': ['/assets/lr-lodge.webp'],
    },
    'teams/retreats/formats': {
        'src': '/assets/sailing/schooner.webp', 'width': 1916, 'height': 821,
        'alt': 'An executive team aboard a classic schooner under full sail at golden hour',
        'eyebrow': 'Retreat formats',
    },
    'teams/executive-immersion': {
        'src': '/assets/img/canyon-overlook.C9_Bw8rH_Z12nC9J.webp', 'width': 1672, 'height': 941,
        'alt': 'An executive team at a canyon overlook at golden hour',
        'eyebrow': None, 'lede': True, 'cta': True, 'drop_local_imgs': True,
    },
    'teams/executive-immersion/expedition': {
        'src': '/assets/sedona/sedona-vista.webp', 'width': 1400, 'height': 1050,
        'alt': 'Red-rock buttes and a long valley view near Sedona, Arizona',
        'eyebrow': 'Executive Immersion · Expedition', 'lede': True,
    },
    'teams/executive-immersion/city': {
        'src': '/assets/img/reach-front-door.Cn0YwnHe_Z2v6ibM.webp', 'width': 1672, 'height': 941,
        'alt': 'Executives walking a city street together with a map',
        'eyebrow': 'Executive Immersion · City', 'lede': True,
    },
    'teams/executive-immersion/ownership': {
        'src': '/assets/img/empty-table.BCuMPEcG_Z2su3hy.webp', 'width': 1672, 'height': 941,
        'alt': 'A long dining table set and empty while a team works in the kitchen behind it',
        'eyebrow': 'Executive Immersion · Ownership', 'lede': True,
    },
    'case-studies/online-auto-retailer-leadership-team': {
        'src': '/assets/cs-autoretailer.webp', 'width': 1500, 'height': 995,
        'alt': 'Executives on an off-road desert retreat built for an auto-retail leadership team',
        'eyebrow': None, 'lede': True,
    },
    'case-studies/san-juan-mountains-work-ethic': {
        'src': '/assets/field/w-img12322.webp', 'width': 1500, 'height': 1125,
        'alt': 'A dog sled team crossing snow on a winter survival leadership retreat',
        'eyebrow': None, 'lede': True,
    },
    'case-studies/everglades-abundance-mindset': {
        'src': '/assets/cs-everglades.webp', 'width': 1600, 'height': 900,
        'alt': 'An executive team in the Florida Everglades on a survival-simulation retreat',
        'eyebrow': None, 'lede': True,
    },
    'case-studies/federal-fiscal-leadership-team': {
        'src': '/assets/field/w-img1235.webp', 'width': 1500, 'height': 1125,
        'alt': 'An executive leadership team in a working session at a mountain lodge',
        'eyebrow': None, 'lede': True,
    },
    'case-studies/alaska-executive-vulnerability': {
        'src': '/assets/field/overlook-alaska.webp', 'width': 945, 'height': 630,
        'alt': 'An executive team taking in the view together from an Alaskan overlook',
        'eyebrow': None, 'lede': True, 'img_opacity': 0.85,
    },
    'how-to-plan-a-leadership-retreat': {
        'src': '/assets/field/g-img1357.webp', 'width': 1500, 'height': 1124,
        'alt': 'Trail signs for Engineer Pass and Cinnamon Pass in a high mountain valley',
        'eyebrow': None, 'lede': True, 'tall': False,  # lede = the byline; short answer stays below
    },
    'how-to-plan-an-executive-offsite': {
        'src': '/assets/field/new-img-9364.webp', 'width': 1700, 'height': 1275,
        'alt': 'An executive team standing together beside their vehicles in the desert',
        'eyebrow': None, 'lede': True, 'tall': False,  # lede = the byline; short answer stays below
    },
    'leadership-offsite-agenda': {
        'src': '/assets/field/raft-img0942.webp', 'width': 1600, 'height': 1200,
        'alt': 'An executive team on rafts on a mountain river',
        'eyebrow': None, 'lede': True, 'tall': False,  # lede = the byline; short answer stays below
    },
    'leadership-team-offsite-facilitator': {
        'src': '/assets/offroad/colorado/co-offroad-facilitation.webp', 'width': 1536, 'height': 1024,
        'alt': 'A facilitator leading an executive team in a circle in the mountains',
        'eyebrow': None, 'lede': True, 'tall': False,  # lede = the byline; short answer stays below
    },
    'why-leadership-offsites-dont-stick': {
        'src': '/assets/sedona/sedona-hero.webp', 'width': 1760, 'height': 1338,
        'alt': 'Red-rock country near Sedona, Arizona',
        'eyebrow': 'Field note', 'lede': True, 'tall': False,  # lede = the byline; short answer stays below
    },
    'teams/leadership-retreat-ideas': {
        'src': '/assets/site-photos/telluride-ferrata.webp', 'width': 1600, 'height': 1100,
        'alt': 'A climber on the via ferrata above Telluride, Colorado',
        'eyebrow': 'Retreat ideas',
    },
    'teams/executive-offsite-ideas': {
        'src': '/assets/site-photos/brush-creek-horses.webp', 'width': 1600, 'height': 1100,
        'alt': 'Horses running at a ranch retreat',
        'eyebrow': 'Offsite ideas',
    },
    'teams/corporate-retreat-ideas': {
        'src': '/assets/site-photos/castle-horses.webp', 'width': 1600, 'height': 1100,
        'alt': 'Riders on horseback below a hilltop castle estate',
        'eyebrow': 'Ideas & locations',
    },
    'teams/retreats/destinations': {
        'src': '/assets/field/kayak-fjord.webp', 'width': 1500, 'height': 1000,
        'alt': 'Red sea kayaks drawn up on a fjord shore beneath steep peaks',
        'eyebrow': None,  # reuse the page's own eyebrow ("Locations & destinations")
    },
}
HERO_CSS = '''
.lr-phero{position:relative;width:100vw;margin-left:calc(50% - 50vw);min-height:min(72vh,640px);display:flex;align-items:flex-end;overflow:hidden;background:#0E0D0B}
.lr-phero__img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 60%}
.lr-phero__scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,13,11,.25) 0%,rgba(14,13,11,.05) 35%,rgba(14,13,11,.55) 70%,rgba(14,13,11,.88) 100%)}
.lr-phero__in{position:relative;width:100%;max-width:1240px;margin:0 auto;padding:120px 32px 56px}
.lr-phero nav[aria-label="Breadcrumb"]{color:rgba(239,233,221,.75)!important;margin-bottom:18px!important}
.lr-phero nav[aria-label="Breadcrumb"] span:last-child{color:#E0B973!important}
.lr-phero__eyebrow{font:700 12.5px 'Hanken Grotesk',sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#E0B973;margin-bottom:16px}
.lr-phero h1{color:#FBF7EF!important;max-width:20ch!important;font-size:clamp(38px,5.6vw,72px)!important;text-shadow:0 2px 30px rgba(0,0,0,.35)}
/* Heroes carrying an intro (and buttons) have a tall text block: shade starts higher. */
.lr-phero__scrim--tall{background:linear-gradient(90deg,rgba(14,13,11,.55) 0%,rgba(14,13,11,0) 62%),linear-gradient(180deg,rgba(14,13,11,.35) 0%,rgba(14,13,11,.5) 22%,rgba(14,13,11,.8) 48%,rgba(14,13,11,.95) 100%)!important}
@media (max-width:860px){.lr-phero__scrim--tall{background:linear-gradient(180deg,rgba(14,13,11,.45) 0%,rgba(14,13,11,.82) 28%,rgba(14,13,11,.95) 60%)!important}}
.lr-phero__in > a:first-child{display:inline-block;margin-bottom:16px;color:rgba(239,233,221,.78)!important}
.lr-phero__in > div:not(.lr-phero__cta) span{color:rgba(239,233,221,.72)}
.lr-phero__lede{margin-top:22px!important;color:rgba(239,233,221,.88)!important;max-width:58ch!important}
.lr-phero__lede *{color:inherit!important}
.lr-phero__cta{margin-top:30px!important}
.lr-phero__cta a{color:#E0B973!important}
.lr-phero__cta a:first-child{background:#E0B973!important;color:#1C1A17!important;border-color:#E0B973!important}
@media (max-width:860px){.lr-phero{min-height:480px}.lr-phero__in{padding:96px 22px 36px}}
'''


def _prune_empty(el):
    """Remove el and empty ancestors left behind after moving hero content."""
    while el is not None and el.name not in ('main', 'body', 'article', '[document]'):
        if el.get_text(strip=True) or el.find(['img', 'iframe', 'video', 'svg']):
            return
        parent = el.parent
        el.decompose()
        el = parent


def add_photo_hero(soup, bl_path):
    cfg = PHOTO_HEROES.get(bl_path)
    if not cfg:
        return False
    h1 = soup.find('h1')
    header = h1.find_parent('header') or h1.parent
    crumb = (header.find('nav', attrs={'aria-label': re.compile('readcrumb')})
             or soup.find('nav', attrs={'aria-label': re.compile('readcrumb')})
             or next((a for a in header.find_all('a', recursive=False) if a.get_text(strip=True).startswith('←')), None))
    for src in cfg.get('drop_imgs', []):
        for img in soup.find_all('img', src=src):
            if not img.find_parent(class_=re.compile('lx-gal')):
                box = img.parent if img.parent.name in ('div', 'figure') and len(img.parent.find_all(True)) == 1 else img
                box.decompose()
    lede = h1.find_next_sibling('p') if cfg.get('lede') else None
    cta = None
    if cfg.get('cta') and lede is not None:
        cta = lede.find_next_sibling('div')
        if cta is not None and not cta.find('a'):
            cta = None
    eyebrow, eyebrow_el = cfg['eyebrow'], None
    if eyebrow is None:
        prev = h1.find_previous_sibling(['p', 'div'])
        if prev is not None and prev.name == 'div':
            eyebrow_el, eyebrow = prev, ''   # e.g. the gold "Case study" tag row
        else:
            eyebrow = prev.get_text(' ', strip=True).replace('\xa0', ' ') if prev else ''
            if prev:
                prev.decompose()
    hero = BeautifulSoup(
        f'<section class="lr-phero"><img class="lr-phero__img" src="{cfg["src"]}" alt="{cfg["alt"]}" '
        f'width="{cfg["width"]}" height="{cfg["height"]}" loading="eager" fetchpriority="high" decoding="async"'
        f'{(" style=" + chr(34) + "opacity:" + str(cfg["img_opacity"]) + chr(34)) if cfg.get("img_opacity") else ""}>'
        f'<div class="lr-phero__scrim{" lr-phero__scrim--tall" if cfg.get("tall", cfg.get("lede")) else ""}"></div>'
        f'<div class="lr-phero__in"><p class="lr-phero__eyebrow">{eyebrow}</p></div></section>',
        'html.parser')
    inner = hero.find(class_='lr-phero__in')
    anchor = header if header.name in ('header', 'section') else (h1.find_parent(['header', 'section']) or header)
    anchor.insert_before(hero)
    if crumb:
        crumb_parent = crumb.parent
        inner.insert(0, crumb.extract())
        _prune_empty(crumb_parent)
    h1_parent = h1.parent
    if eyebrow_el is not None:
        inner.find(class_='lr-phero__eyebrow').replace_with(eyebrow_el.extract())
    inner.append(h1.extract())
    for el, cls in ((lede, 'lr-phero__lede'), (cta, 'lr-phero__cta')):
        if el is not None:
            el['class'] = (el.get('class') or []) + [cls]
            inner.append(el.extract())
    if cfg.get('drop_local_imgs'):
        local = h1_parent.find_parent('section') or h1_parent
        for img in local.find_all('img'):
            img.decompose()
    _prune_empty(h1_parent)
    if anchor.parent is not None:  # still on the page (not pruned away)
        anchor['style'] = re.sub(r'padding:\s*(?:52|56|64|80)px', 'padding:40px', anchor.get('style', ''))
    return True


# Pages whose ported hero already has a photo: restyle it to the house hero
# (photo shown, bottom gradient, text anchored low) instead of replacing it.
# Doubled class selectors outrank the original [data-astro-cid] rules.
HERO_RESTYLES = {
    'sailing-team-building': {
        'css': '''
.sail-hero.sail-hero{min-height:min(88vh,860px);display:flex;align-items:flex-end}
/* The deck photo is busy and the text block is tall, so shade starts higher than on other heroes. */
.sail-hero__scrim.sail-hero__scrim{background:linear-gradient(90deg,rgba(14,13,11,.55) 0%,rgba(14,13,11,0) 62%),linear-gradient(180deg,rgba(14,13,11,.35) 0%,rgba(14,13,11,.5) 22%,rgba(14,13,11,.8) 48%,rgba(14,13,11,.95) 100%)}
.sail-hero__inner.sail-hero__inner{width:100%;max-width:1240px;padding:140px 32px 64px}
.sail-hero h1{text-shadow:0 2px 30px rgba(0,0,0,.35)}
.lr-moved{max-width:1240px;margin:0 auto;padding:40px 32px 8px}
@media (max-width:860px){.sail-hero__scrim.sail-hero__scrim{background:linear-gradient(180deg,rgba(14,13,11,.45) 0%,rgba(14,13,11,.82) 28%,rgba(14,13,11,.95) 60%)}.sail-hero.sail-hero{min-height:auto}.sail-hero__inner.sail-hero__inner{padding:120px 22px 44px}.lr-moved{padding:28px 22px 0}}
''',
        'move_below': 'What is sailing team building?',
    },
    'executive-off-road-immersion': {
        'css': '''
.odi-hero__scrim.odi-hero__scrim{background:linear-gradient(180deg,rgba(14,13,11,.3) 0%,rgba(14,13,11,.06) 28%,rgba(14,13,11,.58) 58%,rgba(14,13,11,.92) 100%)}
.odi-hero h1{font-weight:400!important;text-shadow:0 2px 30px rgba(0,0,0,.35)}
.odi-hero__inner.odi-hero__inner{max-width:1240px;padding-top:140px}
.odi-hero nav[aria-label="Breadcrumb"]{font-size:13px;color:rgba(239,233,221,.75);margin-bottom:18px;display:flex;gap:8px}
.odi-hero nav[aria-label="Breadcrumb"] a{color:inherit;text-decoration:none}
.odi-hero nav[aria-label="Breadcrumb"] span:last-child{color:#E0B973}
''',
        'crumb': 'Off-Road Immersion',
    },
}


INLINE_HERO_RESTYLES = {'teams/executive-immersion/the-city-never-sleeps'}


def restyle_inline_hero(hero):
    """Hero built from inline styles (img + gradient divs + content div)."""
    hero['style'] = (hero.get('style', '').rstrip(';') +
                     ';min-height:min(88vh,860px);display:flex;align-items:flex-end;')
    shades = [d for d in hero.find_all('div', recursive=False) if 'gradient' in d.get('style', '')]
    for d in shades[1:]:
        d.decompose()
    if shades:
        shades[0]['style'] = 'position:absolute;inset:0;'
        shades[0]['class'] = ['lr-phero__scrim--tall']
    content = [d for d in hero.find_all('div', recursive=False) if 'gradient' not in d.get('style', '')]
    if content:
        st = content[-1].get('style', '')
        st = re.sub(r'max-width:\s*\d+px', 'max-width:1240px', st)
        st = re.sub(r'padding:[^;]+', 'padding:150px 40px 60px', st)
        content[-1]['style'] = st + ';width:100%'
    h1 = hero.find('h1')
    h1['style'] = re.sub(r'font-weight:\s*500', 'font-weight:400', h1.get('style', ''))
    h1['style'] = re.sub(r'font-size:clamp\([^)]*\)', 'font-size:clamp(38px,5.6vw,72px)', h1['style'])
    h1['style'] += ';text-shadow:0 2px 30px rgba(0,0,0,.35)'


def restyle_hero(soup, bl_path):
    if bl_path in INLINE_HERO_RESTYLES:
        restyle_inline_hero(soup.find('h1').find_parent('section'))
        return (HERO_CSS.split('/* Heroes carrying')[1].split('.lr-phero__lede')[0].join(['/*', ''])
                + '@media (max-width:860px){main section:first-of-type h1{font-size:clamp(34px,9vw,44px)!important}}')
    cfg = HERO_RESTYLES.get(bl_path)
    if not cfg:
        return None
    h1 = soup.find('h1')
    hero = h1.find_parent('section')
    if cfg.get('move_below'):
        hit = hero.find(string=re.compile(re.escape(cfg['move_below'])))
        box = hit.find_parent('div') if hit else None
        if box is None:
            raise SystemExit(f'hero box not found on {bl_path}')
        wrap = soup.new_tag('section', attrs={'class': 'lr-moved'})
        box['style'] = re.sub(r'margin-top:\s*\d+px;?', 'margin-top:0;', box.get('style', ''))
        wrap.append(box.extract())
        hero.insert_after(wrap)
    if cfg.get('crumb') and not hero.find('nav', attrs={'aria-label': re.compile('readcrumb')}):
        nav = BeautifulSoup(f'<nav aria-label="Breadcrumb"><a href="/">Legendary Retreats</a><span>/</span>'
                            f'<span>{cfg["crumb"]}</span></nav>', 'html.parser')
        h1.find_parent(lambda t: t.name == 'div' and t.find('h1') is not None and t.find('p') is not None).insert(0, nav)
    return cfg['css']


def add_extras(soup, bl_path):
    for anchor, fname, mode in PAGE_EXTRAS.get(bl_path, []):
        hit = soup.find(string=re.compile(re.escape(anchor)))
        sec = hit.find_parent('section') if hit else None
        if sec is None:
            raise SystemExit(f'extras anchor not found on {bl_path}: {anchor!r}')
        frag = BeautifulSoup((OUT / 'extras' / fname).read_text(), 'html.parser')
        if mode == 'replace':
            sec.replace_with(frag)
        else:
            sec.insert_after(frag)


def swap_low_commitment_cta(soup):
    """Be Legendary's 'start free' card points at its Break-Point assessment;
    on the retreat site the free first step is the retreat planning kit."""
    for a in soup.find_all('a', href=re.compile(r'break-point-self-assessment')):
        a['href'] = '/retreat-planning-kit/'
        for k in ('target', 'rel'):
            if a.has_attr(k):
                del a[k]
        for t in a.find_all(string=True):
            new = (t.replace('Take the free Break-Point Self-Assessment', 'Get the free retreat planning kit')
                    .replace('See which of the five components your team is most likely to lose first — in ~4 minutes. No email required to see your result.',
                             'The agenda shape, venue checklist, budget worksheet and 30-day follow-through, in one PDF.')
                    .replace('Start the assessment', 'Get the kit'))
            if new != t:
                t.replace_with(new)


def fix_breadcrumbs(soup):
    for nav in soup.find_all('nav', attrs={'aria-label': re.compile('readcrumb')}):
        for a in list(nav.find_all('a')):
            if a['href'].startswith(BL) or a['href'] == '/':
                sep = a.find_next_sibling()
                if sep is not None and sep.name == 'span' and sep.get_text(strip=True) in ('/', '›', '>'):
                    sep.decompose()
                a.decompose()
        for a in nav.find_all('a', href='/field-notes/'):
            if a.get_text(strip=True) == 'Resources':
                a.string = 'Guides'
        first = nav.find(['a', 'span'])
        home = soup.new_tag('a', href='/', style='color:inherit;text-decoration:none;')
        home.string = 'Legendary Retreats'
        sep = soup.new_tag('span')
        sep.string = '/'
        if first is not None:
            first.insert_before(home)
            first.insert_before(sep)


# ── JSON-LD ───────────────────────────────────────────────────────────────────
LR_ORG_ID = SITE + '/#org'
LR_ORG = {
    '@type': 'Organization', '@id': LR_ORG_ID, 'name': 'Legendary Retreats',
    'url': SITE + '/', 'logo': SITE + '/assets/brand/snail-maroon-web.png',
    'telephone': '+1-800-513-8759',
    'parentOrganization': {'@type': 'Organization', 'name': 'Be Legendary', 'url': BL + '/'},
    'founder': {'@type': 'Person', '@id': BL + '/about/james-carter/#person', 'name': 'James Carter'},
}


def map_url(u):
    if not isinstance(u, str) or not u.startswith(BL):
        return u
    path = u[len(BL):] or '/'
    p, _, frag = path.partition('#')
    if p in BOOK_PATHS:
        return MEETINGS
    if p in MOVED:
        return SITE + MOVED[p] + ('#' + frag if frag else '')
    return u


def fix_ld(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == '@id' and isinstance(v, str) and v.startswith(BL + '/#org'):
                out[k] = LR_ORG_ID
            elif isinstance(v, str):
                v = map_url(v)
                if k == 'name' and v == 'Be Legendary':
                    v = 'Legendary Retreats'
                out[k] = v.replace('| Be Legendary', '| Legendary Retreats') if isinstance(v, str) else v
            else:
                out[k] = fix_ld(v)
        return out
    if isinstance(obj, list):
        return [fix_ld(x) for x in obj]
    return obj


def transform_ld(raw):
    data = json.loads(raw)
    nodes = data.get('@graph', [data])
    keep = []
    for n in nodes:
        t = n.get('@type')
        nid = n.get('@id', '')
        if t in ('Organization', 'WebSite', 'ProfessionalService') and nid.startswith(BL):
            continue  # Be Legendary's site-level entities stay on belegendary.org
        if t == 'BreadcrumbList':
            items = []
            for it in n.get('itemListElement', []):
                url = map_url(it.get('item', ''))
                if isinstance(url, str) and url.startswith(BL):
                    continue
                items.append({**it, 'item': url})
            items = [i for i in items if i.get('item') != SITE + '/']
            items.insert(0, {'@type': 'ListItem', 'name': 'Legendary Retreats', 'item': SITE + '/'})
            for i, it in enumerate(items, 1):
                it['position'] = i
            n = {**n, 'itemListElement': items}
        keep.append(fix_ld(n))
    if not keep:
        return None
    keep.insert(0, LR_ORG)
    return json.dumps({'@context': 'https://schema.org', '@graph': keep}, ensure_ascii=False, separators=(',', ':'))


# ── assets ────────────────────────────────────────────────────────────────────
def copy_asset(url, bl_dist, bl_public):
    path = url.split('?')[0]
    if path.startswith('/_astro/'):
        src = bl_dist / path.lstrip('/')
        dest_url = '/assets/img/' + Path(path).name
    elif path.startswith('/assets/'):
        src = bl_public / path.lstrip('/')
        if not src.exists():
            src = bl_dist / path.lstrip('/')
        dest_url = path
    else:
        return url
    dest = PUBLIC / dest_url.lstrip('/')
    if src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
    else:
        print('  ! missing asset', url)
    return dest_url


def rewrite_assets(html, bl_dist, bl_public):
    def one(m):
        return m.group(1) + copy_asset(m.group(2), bl_dist, bl_public)
    html = re.sub(r'((?:src|href|poster|data-src)=")(/(?:_astro|assets)/[^"]+)', one, html)
    html = re.sub(r'(url\([\'"]?)(/(?:_astro|assets)/[^\'")]+)', one, html)

    def srcset(m):
        parts = []
        for item in m.group(2).split(','):
            bits = item.strip().split(' ', 1)
            if bits[0].startswith(('/_astro/', '/assets/')):
                bits[0] = copy_asset(bits[0], bl_dist, bl_public)
            parts.append(' '.join(bits))
        return m.group(1) + ', '.join(parts) + '"'
    return re.sub(r'(srcset=")([^"]+)"', srcset, html)


# ── page assembly ─────────────────────────────────────────────────────────────
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Hanken+Grotesk:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Archivo:wght@600;700;800;900&display=swap" rel="stylesheet">')


def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


# Page titles aimed at what buyers search on this domain ("executive team
# building" for the one-day format).
TITLE_OVERRIDES = {
    'teams/executive-immersion': 'Executive Team Building: One-Day Executive Immersion',
    'teams/retreats/destinations': 'Executive Retreat Locations & Destinations | Legendary Retreats',
}


def rebrand_title(t):
    t = re.sub(r'\s*[|—–-]\s*Be Legendary\s*$', ' | Legendary Retreats', t)
    return t


def global_css(bl_dist):
    css_file = next((bl_dist / '_astro').glob('index.*.css'))
    css = css_file.read_text()
    css = re.sub(r'@font-face\{[^}]*\}', '', css)
    # Drop Be Legendary header/nav rules; the LR chrome brings its own.
    css = re.sub(r'\.bl-(?:nav-item|caret|dropdown|dd-[a-z]+)[^{]*\{[^}]*\}', '', css)
    css = re.sub(r'\.bl-nav-item:[^{]*\{[^}]*\}', '', css)
    css = css.replace('body{font-family:Hanken Grotesk,system-ui,sans-serif;background:#15130e;', 'body{font-family:Hanken Grotesk,system-ui,sans-serif;')
    return recolor_css(css, dark=True)


def port(bl_repo):
    bl_dist = bl_repo / 'dist'
    bl_public = bl_repo / 'public'
    gcss = global_css(bl_dist)
    report = []
    for bl_path, (name, url) in PAGES.items():
        html = (bl_dist / bl_path / 'index.html').read_text()
        soup = BeautifulSoup(html, 'lxml')
        head, body = soup.head, soup.body

        title = rebrand_title(head.title.get_text())
        desc = (head.find('meta', attrs={'name': 'description'}) or {}).get('content', '')
        ogt = (head.find('meta', attrs={'property': 'og:title'}) or {}).get('content', title)
        ogd = (head.find('meta', attrs={'property': 'og:description'}) or {}).get('content', desc)
        ogt = rebrand_title(ogt)
        if bl_path in TITLE_OVERRIDES:
            title = ogt = TITLE_OVERRIDES[bl_path]

        ld = []
        for s in soup.find_all('script', type='application/ld+json'):
            t = transform_ld(s.string or '')
            if t:
                ld.append(t)
            s.decompose()

        page_styles = [recolor_css(s.get_text(), dark=True) for s in head.find_all('style')]
        inline_js = []
        for s in head.find_all('script'):
            code = s.string or ''
            if 'GA_ID' in code or 'CLARITY' in code or s.get('src'):
                continue
            if code.strip():
                inline_js.append(code)

        body_style = body.get('style', '')
        dark_body = bg_is_dark(body_style)
        dark_body = True if dark_body is None else dark_body

        # Content = between the Be Legendary site header and site footer.
        site_header = body.find('header', recursive=False)
        site_footer = body.find_all('footer', recursive=False)
        site_footer = site_footer[-1] if site_footer else None
        for el in body.find_all(class_='bl-skip'):
            el.decompose()
        if site_header:
            site_header.decompose()
        if site_footer:
            site_footer.decompose()
        for c in body.find_all(string=lambda t: isinstance(t, Comment)):
            c.extract()

        # Inline the hoisted Astro bundles (tiny) and analytics-free scripts.
        for s in body.find_all('script'):
            src = s.get('src', '')
            if src.startswith('/_astro/'):
                code = (bl_dist / src.lstrip('/')).read_text()
                new = soup.new_tag('script', type='module')
                new.string = code
                s.replace_with(new)
            elif 'GA_ID' in (s.string or '') or 'CLARITY' in (s.string or ''):
                s.decompose()

        rewrite_links(body)
        swap_low_commitment_cta(body)
        fix_text(body)
        retreat_voice(body, bl_path)
        fix_breadcrumbs(body)
        recolor_tree(body, dark_body)
        add_extras(body, bl_path)  # after recolor: extras are authored in the LR palette
        if add_photo_hero(body, bl_path):
            page_styles.append(HERO_CSS)
        restyle_css = restyle_hero(body, bl_path)
        if restyle_css:
            page_styles.append(restyle_css)
        for s in body.find_all('style'):
            s.string = recolor_css(s.get_text(), dark=dark_body)

        content = body.decode_contents().strip()
        content = rewrite_assets(content, bl_dist, bl_public)
        page_css = '\n'.join(page_styles)
        page_css = rewrite_assets(page_css, bl_dist, bl_public)

        body_bg = '#141210' if dark_body else '#EFE9DD'
        body_color = '#EFE9DD' if dark_body else INK
        canonical = SITE + (url or '/')
        robots = '' if url else '<meta name="robots" content="noindex">\n'

        doc = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="/assets/brand/favicon-512.png">
<link rel="apple-touch-icon" href="/assets/brand/favicon-180.png">
<meta name="theme-color" content="#64010a">
{robots}<title>{esc_attr(title)}</title>
<meta name="description" content="{esc_attr(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{'article' if bl_path.startswith(('how-to', 'why-', 'leadership-', 'case-studies')) else 'website'}">
<meta property="og:site_name" content="Legendary Retreats">
<meta property="og:title" content="{esc_attr(ogt)}">
<meta property="og:description" content="{esc_attr(ogd)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/brand/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc_attr(ogt)}">
<meta name="twitter:description" content="{esc_attr(ogd)}">
<meta name="twitter:image" content="{SITE}/assets/brand/og-default.png">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html{{scroll-behavior:smooth}}
  body{{background:{body_bg};color:{body_color};font-family:'Hanken Grotesk',system-ui,sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased}}
  ::selection{{background:#64010a;color:#F6EFE0}}
  /* ported from belegendary.org (recolored) */
  {gcss}
  {page_css}
</style>
{''.join(f'<script type="application/ld+json">{x}</script>' + chr(10) for x in ld)}{''.join(f'<script>{x}</script>' + chr(10) for x in inline_js)}</helmet>
<!--lr:header--><!--/lr:header-->
<main id="main">
{content}
</main>
<!--lr:footer--><!--/lr:footer-->
</x-dc>
</body>
</html>
'''
        doc = fix_prices(doc)
        dest = OUT if url else ROOT / '_src' / '_port'  # section sources aren't published
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f'{name}.dc.html').write_text(doc)
        bl_mentions = len(re.findall(r'Be Legendary', BeautifulSoup(content, 'lxml').get_text()))
        ext = len(re.findall(r'href="' + re.escape(BL), content))
        report.append(f'{name:48} {url or "(section source)":48} BL-mentions={bl_mentions:<3} external-links={ext}')

    # The planning-kit PDF keeps its exact path (it is baked into HubSpot emails).
    copy_asset('/assets/downloads/complete-retreat-planning-kit.pdf', bl_dist, bl_public)
    print('\n'.join(report))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: port-from-belegendary.py <be-legendary-repo-dir (built: dist/ present)>')
    port(Path(sys.argv[1]).resolve())
