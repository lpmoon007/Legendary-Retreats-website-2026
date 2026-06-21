# Deploying Legendary Retreats to the GoDaddy VPS (nginx)

The site is a **static build** (Astro → plain HTML/CSS/JS in `dist/`). nginx just
serves files — no Node runtime is needed *in production*. Node is only needed to
*build* (either on the VPS or on your Mac, then upload).

- **Domain / canonical host:** `https://www.legendary-retreats.com` (apex + http
  are 301'd to www).
- **Web root on the server:** `/var/www/legendary-retreats/dist`
- **nginx config:** `deploy/nginx.conf` in this repo.

---

## 0. Before you start
- A **GoDaddy VPS** (or any VPS) with Ubuntu/Debian and root/sudo (`ssh root@YOUR_SERVER_IP`).
- Your domain's DNS managed where you can edit **A records** (GoDaddy DNS).
- Know the server's **public IP** (GoDaddy VPS dashboard).

---

## 1. Point the domain at the VPS (do this first — DNS takes time to propagate)
In **GoDaddy → Domains → DNS** for `legendary-retreats.com`:

| Type | Name | Value            | TTL  |
|------|------|------------------|------|
| A    | `@`  | `YOUR_SERVER_IP` | 600  |
| A    | `www`| `YOUR_SERVER_IP` | 600  |

(If GoDaddy only allows CNAME for `www`, a CNAME `www → legendary-retreats.com`
also works.) Wait until `dig +short www.legendary-retreats.com` returns your IP.

---

## 2. Install nginx, Node, certbot on the VPS
```bash
sudo apt update
sudo apt install -y nginx git
# Node 20 LTS (only needed to build on the server — see step 3, Option A)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
# certbot for free Let's Encrypt SSL
sudo apt install -y certbot python3-certbot-nginx
```

---

## 3. Get the built site onto the server (`/var/www/legendary-retreats/dist`)

### Option A — build on the server (recommended; reproducible)
```bash
sudo mkdir -p /var/www/legendary-retreats
sudo chown -R "$USER" /var/www/legendary-retreats
cd /var/www/legendary-retreats

git clone https://github.com/lpmoon007/Legendary-Retreats-website-2026.git .
git checkout main          # or claude/exciting-shannon-exms0i
npm install
npm run build              # runs the generator + astro build -> ./dist
```

### Option B — build on your Mac, upload `dist/`
```bash
# on your Mac, inside the project:
npm run build
rsync -avz --delete dist/ root@YOUR_SERVER_IP:/var/www/legendary-retreats/dist/
```

Either way you should end up with `/var/www/legendary-retreats/dist/index.html`
and the `assets/`, `about/`, `field-notes/`, … folders beside it.

---

## 4. Install the nginx config
```bash
# copy the config from the repo (adjust path if you used Option B)
sudo cp /var/www/legendary-retreats/deploy/nginx.conf \
        /etc/nginx/sites-available/legendary-retreats.conf
sudo ln -sf /etc/nginx/sites-available/legendary-retreats.conf \
            /etc/nginx/sites-enabled/legendary-retreats.conf

# remove the default placeholder site if present
sudo rm -f /etc/nginx/sites-enabled/default

sudo mkdir -p /var/www/certbot          # for the ACME challenge
sudo nginx -t                            # will WARN about missing certs — expected
```
`nginx -t` will complain that the SSL cert files don't exist yet — that's fine,
certbot creates them in the next step.

---

## 5. Get the SSL certificate (HTTPS)
```bash
sudo certbot --nginx \
  -d legendary-retreats.com -d www.legendary-retreats.com \
  --redirect -m jcarter@belegendary.org --agree-tos --no-eff-email
```
certbot fetches the cert for both names and wires it into the config. Auto-renewal
is installed automatically (`systemctl list-timers | grep certbot`).

Then reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 6. Verify
```bash
curl -I https://www.legendary-retreats.com/                      # 200
curl -I http://legendary-retreats.com/                           # 301 -> https://www
curl -I https://www.legendary-retreats.com/about-4               # 301 -> /about
curl -I https://www.legendary-retreats.com/destinations/lake-tahoe  # 301 -> /destinations/sierra-nevada
curl -I https://www.legendary-retreats.com/sitemap.xml           # 200
```
In a browser, click through the nav, the dial on /ways-to-work-together, and the
HubSpot booking iframe on /contact.

---

## What the nginx config does (`deploy/nginx.conf`)
- **Forces HTTPS** and the **www** canonical host (matches every page's canonical).
- **Clean URLs** via `try_files $uri $uri/` (Astro emits `/<slug>/index.html`).
- **301 redirects** from the old Wix URLs (`/about-4`, `/gallery`, `/film`,
  `/projects-8`, `/leadership`, `/book`, `/destinations/lake-tahoe → …/sierra-nevada`,
  etc.) — see the `map` block at the top.
- **Long-cache** `/assets/*` and `/_astro/*` (`Cache-Control: immutable`, 1 year).
- **gzip** on by default; **brotli** lines are included but commented (uncomment
  only if your nginx has the `ngx_brotli` module compiled in).
- Serves `robots.txt`, `sitemap.xml`, `llms.txt` from the site root.
- Security headers (HSTS, nosniff, frame, referrer).

---

## Updating the site later
```bash
cd /var/www/legendary-retreats
git pull
npm install            # only if dependencies changed
npm run build
sudo systemctl reload nginx   # not strictly needed for content, but harmless
```
(With Option B: rebuild on your Mac and re-run the `rsync` command.)

---

## Notes / external bits (not code)
- **External requests still go out from the browser:** Google Fonts, the HubSpot
  booking iframe (`meetings-na2.hubspot.com/jcarter28`). No server config needed;
  just don't add a Content-Security-Policy that blocks them without allowlisting.
- **GoDaddy *shared* hosting (cPanel) instead of a VPS?** That's Apache, not nginx
  — you'd upload `dist/` to `public_html/` and translate the 301s into a
  `.htaccess` (the Apache forms are in `_src/_deploy/seo/redirects.md`). Tell me if
  that's your setup and I'll generate the `.htaccess`.
- Post-launch: submit `https://www.legendary-retreats.com/sitemap.xml` in Google
  Search Console; verify JSON-LD with the Rich Results Test.
