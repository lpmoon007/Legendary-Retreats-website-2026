# belegendary.org → legendary-retreats.com: retreat 301 map

Ready-to-apply redirects for the belegendary.org side of the retreat split. Kept
here because this repo defines the target URLs; apply them in the Be Legendary repo.

| File | Goes into (Be Legendary repo) |
|---|---|
| `htaccess-retreat-301s.conf` | `public/.htaccess` (replace the 7 lines listed in its section C) |
| `plesk-nginx-retreat-301s.conf` | `redirects/plesk-nginx-redirects.conf` (same replacements) |

Built from, and checked against, the Be Legendary draft `docs/RETREAT-301-MAP.md`
(commit `6fb9a3d`). Same sources and targets; corrected as noted below.

## Apply order (do not reorder)

1. **Deploy www.legendary-retreats.com from this repo and verify it** (`DEPLOY.md` §6).
2. **Confirm the old redirector is gone.** The Be Legendary repo ships
   `redirects/legendary-retreats.com/nginx.conf`, which 301s *all* of
   legendary-retreats.com back to belegendary.org (catch-all → `/teams/retreats/`).
   If any version of it is still active on the legendary-retreats.com server or
   Plesk domain, applying these 301s makes every retreat URL loop between the two
   domains. Check: `curl -sI https://www.legendary-retreats.com/` must be `200`,
   not a `301` to belegendary.org. Then retire that file in the Be Legendary repo.
3. Apply both files on belegendary.org.
4. Phase 4 on belegendary.org: internal-link cleanup, page removal, homepage rebuild.
5. Verify (below).

## Corrections to the Be Legendary draft

- **Site-wide HTTP 500 (blocker).** The draft's section C puts `# comments` on the
  same line as `Redirect` directives. Apache has no trailing comments: the words
  become extra arguments, the whole `.htaccess` is rejected, and every request it
  governs returns 500. Reproduced on Apache 2.4 with the draft as written
  (`Redirect takes one, two or three arguments…`). Comments are on their own lines here.
- **No-slash URLs now redirect in one hop.** `Redirect 301 /x/` matches only the
  slash form, so `/extreme-retreats` (CNN), `/shakubuku` (Business Insider) and the
  other legacy sources 404'd without the slash. Everything uses exact
  `RedirectMatch 301 ^/x/?$` now: one hop with or without the slash, and no
  accidental prefix matches (`/teams/retreats/anything` no longer turns into a
  legendary-retreats.com 404).
- **nginx parity written out.** The draft said "+ nginx parity" without rules;
  `plesk-nginx-retreat-301s.conf` is the full mirror, including the section C
  replacements for the existing `rewrite` lines.

## Tested

On Apache 2.4 (belegendary.org's real `.htaccess` with this block merged in) and
nginx: 71 of 71 source URLs (with and without the trailing slash, plus the PDF)
return one `301` to the exact target, and every target exists in this repo's
build. Paths that stay on belegendary.org (`/`, `/teams/`, `/teams/team-lfs/`,
`/leaders/…`, `/how-we-work-together/`, `/flag-model/`, `/blog/…`) are untouched.

## Verify after applying

```bash
for p in /teams/retreats/ /teams/retreats/destinations /teams/executive-immersion/city/ \
         /case-studies/ /extreme-retreats /shakubuku/ \
         /assets/downloads/complete-retreat-planning-kit.pdf; do
  curl -sI "https://www.belegendary.org$p" | grep -iE '^(HTTP|location)'
done
# each: one 301, location https://www.legendary-retreats.com/...; then that URL returns 200
curl -sI https://www.belegendary.org/teams/        # 200, stays
```
