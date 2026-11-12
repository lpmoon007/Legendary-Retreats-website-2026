# buildingteams.com: a visible path for executive-team buyers to legendary-retreats.com

From the Legendary Retreats session, 2026-11-12. Repo: `lpmoon007/Building-Teams-Website-2026`.

## Why

- HubSpot: about 40 inbound contacts since Oct 15 came through buildingteams.com (5 from ChatGPT). legendary-retreats.com produced none.
- GA4 for legendary-retreats.com (Oct 15 to Nov 11) shows **zero sessions referred by buildingteams.com**. belegendary.org sent 18 sessions and 4 of the site's 6 key events. So the existing in-body links (if live) are not being clicked.
- AI engines now cite `buildingteams.com/resources/corporate-retreats/` (28 citations in 14 days, new). Executive buyers land there and have no obvious next step for a leadership-team retreat.

Goal: anyone on buildingteams.com who is planning for a leadership team of 5 to 12 sees one clear, tracked route to legendary-retreats.com. Company-wide and staff retreats stay on buildingteams.com.

## 1. Callout card on the retreat and executive pages

Place it after the first content section (above the fold on desktop if possible), not in the footer.

Pages:
- `/corporate-retreats/`, `/resources/corporate-retreats/` and every child page (agenda, budget, ideas, timeline, activities, sponsor questions, venue checklist, what is a company retreat)
- `/corporate-retreat-planning/`, `/corporate-retreat-locations/`
- `/resources/team-building-retreat/`, `/resources/staff-retreat/`
- `/executive-team-building/` and its children, including success stories
- The Leadership Team Alignment pillar and any other leadership pillar pages

Copy (use as written; no em dashes):

> **Planning a retreat for your leadership team?**
> For CEOs and executive teams of 5 to 12, our sister company Legendary Retreats designs multi-day experiential retreats built around one outcome, from off-road and winter survival to five-star estates, and measures the behavior change for 30 days afterward.
> [See executive retreats →]

Link (per page, fill in the path):
`https://www.legendary-retreats.com/?utm_source=buildingteams.com&utm_medium=referral&utm_campaign=exec_retreat_callout&utm_content=<page-path>`

On `/resources/corporate-retreats/budget/` point the button to `https://www.legendary-retreats.com/is-an-executive-retreat-worth-it/` (same UTM), and on `/corporate-retreat-locations/` to `https://www.legendary-retreats.com/best-executive-retreat-locations/`.

Style: a bordered card in the site's existing style, with a real button. It should read as a recommendation, not an ad.

## 2. Navigation

Add **Executive retreats** to the menu where corporate retreats live (Resources or Experiences dropdown), linking to
`https://www.legendary-retreats.com/?utm_source=buildingteams.com&utm_medium=referral&utm_campaign=nav`.
Mark it as external if the menu does that for other off-site links.

## 3. Contact form (optional, small)

If the Book a Call form has a group size or event type field, add the option "Leadership team retreat (5 to 12 executives)". Leave routing as is (both sites go to James's HubSpot); this is so the lead is recognizable.

## 4. Finish the earlier in-body links

Check section 5 of `buildingteams-redirects.md` (in-body links from the corporate retreat cluster, the best-companies page, Organization JSON-LD and llms.txt). Add the same UTM parameters to those links, with `utm_campaign=inbody`, so GA4 can tell them apart from the callout.

## 5. Verify

After deploy, open one cluster page, click the callout and confirm the landing URL on legendary-retreats.com carries the UTM. In a day or two, GA4 for Legendary Retreats should show `buildingteams.com / referral` sessions.

Do not move or redirect the corporate and staff retreat pages; they serve buildingteams.com's own buyers.
