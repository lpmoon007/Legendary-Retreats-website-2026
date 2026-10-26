# belegendary.org: retreat redirects and links to legendary-retreats.com

From the Legendary Retreats session, 2026-10-26. Repo: `lpmoon007/be-legendary-website-2026`, branch `claude/epic-carson-cjyx09`.

## Why

The retreat split (commit 93a8d29, 2026-10-17) is in the repo and every target URL below has been checked against the live legendary-retreats.com build. Otterly citations through 2026-10-25 still show AI engines citing old belegendary.org retreat URLs, often **without a trailing slash** (`/teams/retreats`, `/sailing-team-building`, `/sedona-executive-leadership-retreat`). Three fixes, then verify on the live server.

## 1. Retarget two redirects (both files)

Legendary Retreats now has destination pages, so these should land there instead of the off-road page.

`public/.htaccess`, replace:
```apache
Redirect 301 /denver-executive-leadership-retreat/ https://www.legendary-retreats.com/executive-off-road-immersion/
Redirect 301 /sedona-executive-leadership-retreat/ https://www.legendary-retreats.com/executive-off-road-immersion/
```
with:
```apache
RedirectMatch 301 ^/denver-executive-leadership-retreat/?$ https://www.legendary-retreats.com/destinations/colorado/
RedirectMatch 301 ^/sedona-executive-leadership-retreat/?$ https://www.legendary-retreats.com/destinations/sedona-arizona/
```

`redirects/plesk-nginx-redirects.conf`, replace the two matching lines with:
```nginx
rewrite ^/denver-executive-leadership-retreat/?$   https://www.legendary-retreats.com/destinations/colorado/        permanent;
rewrite ^/sedona-executive-leadership-retreat/?$   https://www.legendary-retreats.com/destinations/sedona-arizona/  permanent;
```

## 2. Make the .htaccess retreat rules match with or without the trailing slash

Apache `Redirect 301 /sailing-team-building/ ...` only matches the slash form. The pages were deleted, so `/sailing-team-building` (no slash, the form AI engines cite) no longer gets a directory slash-redirect and can 404. The nginx conf already uses `/?$`; make `.htaccess` match it.

In `public/.htaccess`, replace the whole "Retreats split out to legendary-retreats.com (2026-10-17)" block (from `Redirect 301 /teams/retreats/` through `RedirectMatch 301 ^/case-studies/?$ ...`) with:

```apache
# ── Retreats split out to legendary-retreats.com (2026-10-17) ──
# Single hop, www + trailing slash on the target. /?$ so both slash forms match.
RedirectMatch 301 ^/teams/retreats/?$ https://www.legendary-retreats.com/
RedirectMatch 301 ^/teams/retreats/(.+)$ https://www.legendary-retreats.com/$1
RedirectMatch 301 ^/teams/luxury-executive-retreat/?$ https://www.legendary-retreats.com/luxury-executive-retreat/
RedirectMatch 301 ^/teams/corporate-retreat-ideas/?$ https://www.legendary-retreats.com/corporate-retreat-ideas/
RedirectMatch 301 ^/teams/executive-offsite-ideas/?$ https://www.legendary-retreats.com/executive-offsite-ideas/
RedirectMatch 301 ^/teams/leadership-retreat-ideas/?$ https://www.legendary-retreats.com/leadership-retreat-ideas/
RedirectMatch 301 ^/teams/executive-immersion/?$ https://www.legendary-retreats.com/executive-immersion/
RedirectMatch 301 ^/teams/executive-immersion/(.+)$ https://www.legendary-retreats.com/executive-immersion/$1
RedirectMatch 301 ^/sailing-team-building/?$ https://www.legendary-retreats.com/sailing-team-building/
RedirectMatch 301 ^/executive-off-road-immersion/?$ https://www.legendary-retreats.com/executive-off-road-immersion/
RedirectMatch 301 ^/how-to-plan-a-leadership-retreat/?$ https://www.legendary-retreats.com/how-to-plan-a-leadership-retreat/
RedirectMatch 301 ^/how-to-plan-an-executive-offsite/?$ https://www.legendary-retreats.com/how-to-plan-an-executive-offsite/
RedirectMatch 301 ^/leadership-offsite-agenda/?$ https://www.legendary-retreats.com/leadership-offsite-agenda/
RedirectMatch 301 ^/why-leadership-offsites-dont-stick/?$ https://www.legendary-retreats.com/why-leadership-offsites-dont-stick/
RedirectMatch 301 ^/leadership-team-offsite-facilitator/?$ https://www.legendary-retreats.com/leadership-team-offsite-facilitator/
RedirectMatch 301 ^/retreat-planning-kit/?$ https://www.legendary-retreats.com/retreat-planning-kit/
RedirectMatch 301 ^/assets/downloads/complete-retreat-planning-kit\.pdf$ https://www.legendary-retreats.com/assets/downloads/complete-retreat-planning-kit.pdf
RedirectMatch 301 ^/case-studies/(online-auto-retailer-leadership-team|san-juan-mountains-work-ethic|everglades-abundance-mindset|federal-fiscal-leadership-team|alaska-executive-vulnerability)/?$ https://www.legendary-retreats.com/case-studies/$1/
RedirectMatch 301 ^/case-studies/?$ https://www.legendary-retreats.com/case-studies/
```

Also convert the three legacy press-link rules near the top to the same form (CNN and Business Insider link to these):
```apache
RedirectMatch 301 ^/shakubuku/?$ https://www.legendary-retreats.com/
RedirectMatch 301 ^/extreme-retreats/?$ https://www.legendary-retreats.com/
RedirectMatch 301 ^/experiential-leadership-retreats/?$ https://www.legendary-retreats.com/
```

Check that no `RewriteRule` or earlier `Redirect` line catches these paths first (mod_alias runs in file order for `Redirect`/`RedirectMatch`).

## 3. Deploy, then verify on the live server

After deploying, if Plesk's "Additional nginx directives" holds a copy of `redirects/plesk-nginx-redirects.conf`, paste the updated file there too (Plesk > Websites & Domains > belegendary.org > Apache & nginx Settings > Additional nginx directives > OK).

Run each line and confirm a single `301` whose `location:` is the legendary-retreats.com URL (not a second hop, not a 404, not a 200):

```bash
for p in /teams/retreats /teams/retreats/ /teams/retreats/destinations/ /sailing-team-building /sailing-team-building/ \
         /sedona-executive-leadership-retreat /denver-executive-leadership-retreat/ /leadership-offsite-agenda \
         /how-to-plan-an-executive-offsite /teams/luxury-executive-retreat /teams/executive-immersion/city/ \
         /retreat-planning-kit /case-studies/alaska-executive-vulnerability /shakubuku/ /extreme-retreats; do
  printf '%-48s ' "$p"; curl -sI "https://www.belegendary.org$p" | awk 'tolower($1)~/^http|^location/{printf "%s ", $0} END{print ""}' | tr -d '\r'
done
```

Any URL that returns `200` is still being served by belegendary.org, which is why AI engines keep citing it. Fix those first.

## 4. Links and references to legendary-retreats.com (keep these on belegendary.org)

Redirects move old URLs; links tell search engines and AI that the brands are related. Add in-body links with descriptive anchor text (not "click here"), opening in the same tab is fine:

| belegendary.org page | Add | Link to |
|---|---|---|
| `/best-executive-team-development-companies` (cited heavily by ChatGPT) | An entry or line for Legendary Retreats as the sister brand for experiential executive retreats, with a disclosure | `https://www.legendary-retreats.com/` |
| `/executive-team-building/`, `/teams/`, `/how-we-work-together/` | One sentence, e.g. "For a facilitated, experiential retreat, see Legendary Retreats." | `https://www.legendary-retreats.com/` |
| `/leaders/executive-burnout-retreat` | "luxury executive retreats" | `https://www.legendary-retreats.com/luxury-executive-retreat/` |
| Any how-to or comparison content that mentions offsites | "how to plan an executive offsite", "executive retreat companies compared" | `https://www.legendary-retreats.com/how-to-plan-an-executive-offsite/`, `https://www.legendary-retreats.com/best-executive-retreat-companies/` |
| Anything that mentions retreat cost or ROI | "is an executive retreat worth it" | `https://www.legendary-retreats.com/is-an-executive-retreat-worth-it/` |

Structured data and AI files:
- Organization JSON-LD: add `"subOrganization": {"@type": "Organization", "name": "Legendary Retreats", "url": "https://www.legendary-retreats.com/"}`. (legendary-retreats.com already declares Be Legendary as `parentOrganization`.)
- `llms.txt`: one line naming Legendary Retreats as the retreat brand, with the URL.

Do not re-add retreat pages or retreat copy to belegendary.org; link out instead.
