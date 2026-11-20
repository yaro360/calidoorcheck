# FairDoorLA — licensed garage door companies in LA / SoCal (v1)

Static directory site. "Verify before you call."

## Layout
- `data/raw/` — raw CSLB downloads (`cslb_C61D28_<County>.xlsx`) + `FETCHED_AT.txt`
- `data/licenses.csv`, `data/licenses.json` — normalized license rows (source + fetch date on every row)
- `scripts/fetch_cslb.py` — downloads CSLB "List by Classification and County" (free, official) for C-61/D-28 in LA, Orange, Riverside, San Bernardino, San Diego, Ventura
- `scripts/normalize.py` — xlsx → CSV/JSON
- `content/guides/*.html` — sourced guide pages (`<!--META {json} -->` header with title, description, sources). `"core": true` pages are always built.
- `queue.json` — nightly publish queue (county hubs + cities, then data reports, then guides)
- `state/published.json` — which queue items are live
- `build.py` — generator → `site/` (pages, sitemap.xml, robots.txt, 404.html)
- `publish_next.sh` — publish ONE queue item, rebuild, git commit, append `PUBLISH_LOG.md`
- `refresh_data.sh` — re-download CSLB data, normalize, rebuild, commit
- `config.json` — brand + `site_url` (`https://yaro360.github.io/fairdoorla`; path prefix is derived from this)
- `deploy.sh` — push the source branch and publish `site/` to the `gh-pages` branch (GitHub Pages)
- `serve_local.sh` — local preview at the same path prefix as production

## Commands
```bash
cd /workspace/garagedoor
./publish_next.sh        # nightly: one new page, commit, deploy to GitHub Pages
./deploy.sh              # push source + publish site/ to gh-pages (does not add a queue page)
./refresh_data.sh        # weekly-ish: refresh CSLB data (licenses change daily)
python3 build.py         # rebuild only
./serve_local.sh         # local preview at http://127.0.0.1:8080/fairdoorla/
```

## Live site
- Site: https://yaro360.github.io/fairdoorla/
- Repo: https://github.com/yaro360/fairdoorla
- Pages source: `gh-pages` branch, root (`site/` contents plus `.nojekyll`)

## Data source
CSLB Public Data Portal → List by Classification and County: https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty
Classification option `C-61/D-28` (Doors, Gates & Activating Devices); counties 19 (LA), 30 (Orange), 33 (Riverside), 36 (San Bernardino), 37 (San Diego), 56 (Ventura). Returns .xlsx of currently renewed licenses: license #, business name/type, address, city, ZIP, county, phone, issue/expiry, classifications, status, bond surety/number/dates, workers' comp type/insurer/policy/dates. No email (B&P Code §27). Free.
Manual fallback: open the URL, select C-61/D-28 + counties (max 10 each), click Download.

## Queue guides that need content
Guide items whose `content/guides/<slug>.html` doesn't exist are skipped (logged) until someone writes them with cited sources. Never invent prices or quotes.

## TODO
- Lead form backend (form posts nowhere now), featured listings, corrections contact, custom domain (FairDoorLA.com is still unregistered; do not buy without approval).
