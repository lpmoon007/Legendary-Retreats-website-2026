# buildingteams.com: retreat redirects and links to legendary-retreats.com

From the Legendary Retreats session, 2026-10-26. Repo: `lpmoon007/Building-Teams-Website-2026`, branch `claude/building-teams-deploy-87vbn5`. Redirects live in the root `.htaccess`.

## Why

When retreats lived on belegendary.org, buildingteams.com 301'd its old executive and retreat URLs there. belegendary.org now 301s those pages again to legendary-retreats.com, so every one of these is a **two-hop chain**, and one (firewalking) ends on the wrong page. Chains leak link equity and slow crawlers. Point them straight at the final URL. Every target below has been checked against the live legendary-retreats.com build.

## 1. Repoint these rules in `.htaccess` (single hop)

Change only the target URL; keep the flags `[R=301,NC,L]`.

| Line (approx.) | Pattern | Old target | New target |
|---|---|---|---|
| 70 | `^experiences/off-road-immersion(/index\.html)?/?$` | belegendary.org/executive-off-road-immersion/ | `https://www.legendary-retreats.com/executive-off-road-immersion/` |
| 84 | `^experiences/corporate-sailing/?(index\.html)?$` | belegendary.org/sailing-team-building/ | `https://www.legendary-retreats.com/sailing-team-building/` |
| 88 | `^resources/executive-offsite-agenda/?(index\.html)?$` | belegendary.org/leadership-offsite-agenda/ | `https://www.legendary-retreats.com/leadership-offsite-agenda/` |
| 89 | `^resources/company-offsite-planning-checklist/?(index\.html)?$` | belegendary.org/how-to-plan-an-executive-offsite/ | `https://www.legendary-retreats.com/how-to-plan-an-executive-offsite/` |
| 90 | `^resources/corporate-retreat-ideas/?(index\.html)?$` | belegendary.org/teams/corporate-retreat-ideas/ | `https://www.legendary-retreats.com/corporate-retreat-ideas/` |
| 121 | `^adventure-team-building/sailing-as-team-building/?(index\.html)?$` | belegendary.org/sailing-team-building/ | `https://www.legendary-retreats.com/sailing-team-building/` |
| 226 | `^Adventure_Teambuilding/corporate_sailing(_shackletons_adventure)?\.htm/?$` | belegendary.org/sailing-team-building/ | `https://www.legendary-retreats.com/sailing-team-building/` |
| 227 | `^Adventure_Teambuilding/[a-z_]*off[-_]?road[a-z_]*\.htm/?$` | belegendary.org/executive-off-road-immersion/ | `https://www.legendary-retreats.com/executive-off-road-immersion/` |
| 240 | `^adventure_teambuilding/firewalking\.htm/?$` | belegendary.org/denver-executive-leadership-retreat | `https://www.legendary-retreats.com/destinations/colorado/` |
| 295 | `^off-road-immersion-retreat/?$` | belegendary.org/executive-off-road-immersion/ | `https://www.legendary-retreats.com/executive-off-road-immersion/` |

Update the two section comments ("Cross-brand move: ... -> Be Legendary") to say the pages now live on legendary-retreats.com.

## 2. Keep staff-retreat URLs on buildingteams.com

These three point at belegendary.org's corporate retreat ideas (now a chain to legendary-retreats.com). Staff and company-wide retreats are buildingteams.com's buyer, and you now have your own page, so keep the equity here:

| Line (approx.) | Pattern | New target |
|---|---|---|
| 193 | `^staff_retreat_games_ideas\.htm/?$` | `/resources/staff-retreat/` |
| 194 | `^staff_retreat_teambuilding_non_profit_organization\.htm/?$` | `/resources/staff-retreat/` |
| 292 | `^staff-retreat-games-ideas/?$` | `/resources/staff-retreat/` |

(If James would rather send that equity to legendary-retreats.com, use `https://www.legendary-retreats.com/corporate-retreat-ideas/` instead. Either way, single hop.)

## 3. Do not redirect the corporate retreat resource cluster

`/corporate-retreats/`, `/resources/corporate-retreats/` and its children (agenda, budget, ideas, timeline, activities, sponsor questions, venue checklist, what is a company retreat), `/corporate-retreat-planning/`, `/corporate-retreat-locations/`, `/resources/staff-retreat/` and `/resources/team-building-retreat/` serve company-wide and staff retreats, which is buildingteams.com's market. They stay. Link from them instead (section 5).

## 4. Deploy, then verify

```bash
for p in /experiences/off-road-immersion/ /experiences/corporate-sailing/ /resources/executive-offsite-agenda/ \
         /resources/company-offsite-planning-checklist/ /resources/corporate-retreat-ideas/ \
         /Adventure_Teambuilding/corporate_sailing.htm /adventure_teambuilding/firewalking.htm \
         /off-road-immersion-retreat/ /staff-retreat-games-ideas/; do
  printf '%-52s ' "$p"; curl -sI "https://www.buildingteams.com$p" | awk 'tolower($1)~/^http|^location/{printf "%s ", $0} END{print ""}' | tr -d '\r'
done
```

Each should show one `301` with a `location:` on legendary-retreats.com (or `/resources/staff-retreat/` for the staff rules). A `location:` on belegendary.org means the rule was not updated.

## 5. Links and references to legendary-retreats.com

Add in-body links with descriptive anchor text where executive or leadership retreats come up, especially across the corporate retreat cluster:

| buildingteams.com page | Anchor text | Link to |
|---|---|---|
| `/resources/corporate-retreats/` and `/corporate-retreats/` | "executive retreats for leadership teams" | `https://www.legendary-retreats.com/` |
| `/resources/corporate-retreats/ideas/`, `/resources/team-building-retreat/` | "adventure retreats for executive teams" | `https://www.legendary-retreats.com/best-adventure-executive-retreat-companies/` |
| `/corporate-retreat-locations/` | "executive retreat destinations" | `https://www.legendary-retreats.com/destinations/` |
| `/resources/corporate-retreats/agenda/` | "executive offsite agenda template" | `https://www.legendary-retreats.com/leadership-offsite-agenda/` |
| `/resources/corporate-retreats/budget/` | "what an executive retreat costs" | `https://www.legendary-retreats.com/field-notes/executive-retreat-cost/` |
| `/executive-team-building/success-stories/` | "executive retreat case studies" | `https://www.legendary-retreats.com/case-studies/` |
| Best-companies page | Legendary Retreats as the sister brand for executive retreats, with disclosure | `https://www.legendary-retreats.com/` |

Add one positioning line on `/corporate-retreats/` and `/resources/corporate-retreats/`: buildingteams.com plans team building and company-wide retreats; Legendary Retreats designs multi-day retreats for executive and leadership teams.

Structured data and AI files:
- Organization JSON-LD: do not put legendary-retreats.com in `sameAs` (that claims they are the same entity). If the schema already names Be Legendary as parent, no change is needed; otherwise add `"parentOrganization": {"@type": "Organization", "name": "Be Legendary", "url": "https://www.belegendary.org/"}` so all three brands connect through the parent.
- `llms.txt`: one line naming Legendary Retreats as the executive retreat brand, with the URL.

legendary-retreats.com already links back to buildingteams.com (James's bio and the corporate retreat ideas page).
