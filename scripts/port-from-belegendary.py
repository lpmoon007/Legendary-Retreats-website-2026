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


def rewrite_links(soup):
    for a in soup.find_all('a', href=True):
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
