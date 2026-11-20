#!/usr/bin/env python3
"""FairDoorLA static site generator. Rebuilds site/ from data/, content/, queue.json and state/published.json."""
import json, re, html, shutil, pathlib, datetime
from collections import defaultdict
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "site"
CFG = json.loads((ROOT / "config.json").read_text())
BRAND, BASE = CFG["brand"], CFG["site_url"].rstrip("/")
# Path prefix when hosted in a subdirectory (GitHub Pages project site).
# Filesystem paths and PAGES entries stay unprefixed; HTML links, CSS, and the search index use PREFIX.
PREFIX = urlparse(BASE).path.rstrip("/")
TODAY = datetime.date.today().isoformat()
E = lambda s: html.escape(str(s or ""), quote=True)

def u(path):
    """Turn a site-absolute path into a public URL path, including PREFIX."""
    if not path.startswith("/"):
        path = "/" + path
    return PREFIX + path

def prefix_hrefs(text):
    """Rewrite root-absolute href/src so they work under PREFIX. Idempotent."""
    if not PREFIX:
        return text
    def repl(m):
        attr, path = m.group(1), m.group(2)
        if path.startswith("//") or path == PREFIX or path.startswith(PREFIX + "/"):
            return m.group(0)
        return f'{attr}="{PREFIX}{path}"'
    return re.sub(r'\b(href|src)="(/[^"]*)"', repl, text)

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def county_path(c): return f"/garage-door-repair/{slug(c)}-county/"
def city_path(c, city): return f"{county_path(c)}{slug(city)}/"
def fmt_phone(p):
    d = re.sub(r"\D", "", p or "")
    return (f"({d[:3]}) {d[3:6]}-{d[6:10]}", f"+1{d[:10]}") if len(d) >= 10 else (p, "")

# ---------- data ----------
LIC = json.loads((ROOT / "data" / "licenses.json").read_text())
FETCHED = LIC[0]["fetched_at"][:10] if LIC else TODAY
by_county = defaultdict(lambda: defaultdict(list))
for r in LIC:
    if r["status"].upper() != "CLEAR": continue
    by_county[r["county"]][r["city"]].append(r)
for c in by_county:
    for city in by_county[c]: by_county[c][city].sort(key=lambda r: r["business_name"])

def load_guide(sl):
    p = ROOT / "content" / "guides" / f"{sl}.html"
    if not p.exists(): return None
    txt = p.read_text()
    m = re.match(r"<!--META (\{.*?\}) -->\n?", txt, re.S)
    meta = json.loads(m.group(1)); meta["body"] = txt[m.end():]; meta["slug"] = sl
    meta["path"] = f"/{sl}/"
    return meta

QUEUE = json.loads((ROOT / "queue.json").read_text())
PUB_PATH = ROOT / "state" / "published.json"
PUBLISHED = json.loads(PUB_PATH.read_text()) if PUB_PATH.exists() else []
PUB_IDS = {p["id"]: p for p in PUBLISHED}
core_guides = [g for g in (load_guide(p.stem) for p in sorted((ROOT / "content" / "guides").glob("*.html"))) if g and g.get("core")]
pub_guides = [load_guide(q["slug"]) for q in QUEUE if q["type"] == "guide" and q["id"] in PUB_IDS]
pub_guides = [g for g in pub_guides if g]
live_counties = [CFG["core_county"]] + [q["county"] for q in QUEUE if q["type"] == "county" and q["id"] in PUB_IDS]
def city_live(c, city):
    return c == CFG["core_county"] or f"city:{slug(c)}:{slug(city)}" in PUB_IDS

PAGES = []  # (path, lastmod)

# ---------- templates ----------
NAV = [("/", "Find a pro"), ("/how-to-check-a-garage-door-contractor-license/", "Check a license"),
       ("/garage-door-repair-scams/", "Scams"), ("/garage-door-spring-replacement-cost/", "Prices")]

def lead_form(city=""):
    return f"""<h2 id="quote">Get a quote from licensed pros</h2>
<!-- TODO: lead form has NO backend yet. Wire to a form handler (e.g. Hostinger PHP/Node endpoint or a form service) and only route leads to CSLB-licensed companies. -->
<form class="lead" onsubmit="event.preventDefault();this.querySelector('.msg').hidden=false;">
<p class="meta" style="margin:0"><strong>Coming soon (TODO):</strong> this form is not live yet and does not send anything.</p>
<div><label for="lf-name">Name</label><input id="lf-name" name="name" autocomplete="name" required></div>
<div><label for="lf-zip">ZIP code</label><input id="lf-zip" name="zip" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" required></div>
<div><label for="lf-job">Job type</label><select id="lf-job" name="job_type" required><option value="">Choose…</option><option>Broken spring</option><option>Cable / off track</option><option>Opener repair or replacement</option><option>Panel / door damage</option><option>New garage door</option><option>Tune-up</option><option>Other</option></select></div>
<div><label for="lf-phone">Phone</label><input id="lf-phone" name="phone" type="tel" autocomplete="tel" required></div>
<input type="hidden" name="city" value="{E(city)}">
<button class="btn" type="submit">Request quotes</button>
<p class="msg meta" hidden>Thanks — this form isn't connected yet, so nothing was sent. Please contact a licensed company below directly.</p>
</form>"""

FEATURED = '<div class="slot" aria-label="Featured listing placeholder"><strong>Featured listing slot (empty)</strong> — reserved for a CSLB-licensed company. Paid placements will always be labeled "Sponsored". <!-- TODO: featured listings --></div>'

def page(path, title, desc, body, schema=None, crumbs=None, lastmod=None):
    url = BASE + path
    sch = "".join(f'<script type="application/ld+json">{json.dumps(s, separators=(",", ":"))}</script>' for s in (schema or []))
    if crumbs:
        sch += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate(crumbs)]}, separators=(",", ":")) + "</script>"
        cr = '<div class="crumbs">' + " › ".join(f'<a href="{p}">{E(n)}</a>' for n, p in crumbs[:-1]) + f" › {E(crumbs[-1][0])}</div>"
    else: cr = ""
    nav = "".join(f'<a href="{h}">{E(t)}</a>' for h, t in NAV)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website">
<link rel="stylesheet" href="/assets/style.css">{sch}</head><body>
<header class="site"><div class="wrap"><a class="logo" href="/">Fair<span>Door</span>LA</a><nav class="top">{nav}</nav></div></header>
<main><div class="wrap">{cr}{body}</div></main>
<footer class="site"><div class="wrap"><p><strong>{BRAND}</strong> — {E(CFG["tagline"])} Company data: <a href="https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty">California Contractors State License Board public data</a>, downloaded {FETCHED}. Licenses change daily; always confirm on <a href="https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx">CSLB Instant License Check</a>. {BRAND} is not affiliated with CSLB.</p>
<p><a href="/garage-door-repair/">All cities</a> · <a href="/about/">About &amp; methodology</a> · <a href="/sitemap.xml">Sitemap</a></p></div></footer>
</body></html>"""
    doc = prefix_hrefs(doc)
    f = OUT / path.lstrip("/") / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True); f.write_text(doc)
    PAGES.append((path, lastmod or TODAY))

def company_card(r):
    ph, tel = fmt_phone(r["phone"])
    wc = r["workers_comp_type"]
    if wc.startswith("Workers' Compensation"): wct = f'<span class="tag ok">Workers\' comp on file{(" · " + E(r["workers_comp_insurer"].title())) if r["workers_comp_insurer"] else ""}</span>'
    elif wc == "Exempt": wct = '<span class="tag">Workers\' comp: exempt (no employees declared)</span>'
    elif wc: wct = f'<span class="tag warn">{E(wc)}</span>'
    else: wct = ""
    since = r["issue_date"][-4:] if r["issue_date"] else ""
    return f"""<div class="card"><h3>{E(r["business_name"])}</h3>
<div class="meta">CSLB license #{E(r["license_number"])} · {E(r["classifications"])} · {E(r["business_type"])}<br>{E(r["city"])}, CA {E(r["zip"])}{f' · <a href="tel:{tel}">{E(ph)}</a>' if tel else ""}</div>
<span class="tag ok">License status on list: {E(r["status"].title())}</span>{f'<span class="tag">Licensed since {since}</span>' if since else ""}<span class="tag">Expires {E(r["expiration_date"])}</span>{f'<span class="tag">Bond: {E(r["bond_surety"].title())}</span>' if r["bond_surety"] else ""}{wct}
</div>"""

def company_schema(rows, name):
    items = []
    for i, r in enumerate(rows):
        ph, tel = fmt_phone(r["phone"])
        b = {"@type": "LocalBusiness", "name": r["business_name"], "address": {"@type": "PostalAddress", "addressLocality": r["city"], "postalCode": r["zip"], "addressRegion": "CA", "addressCountry": "US"},
             "identifier": {"@type": "PropertyValue", "propertyID": "CSLB license", "value": r["license_number"]}}
        if tel: b["telephone"] = tel
        items.append({"@type": "ListItem", "position": i + 1, "item": b})
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(rows), "itemListElement": items}

CAVEAT = f"""<div class="note">Listed: contractors holding a <strong>CSLB D-28 (Doors, Gates &amp; Activating Devices)</strong> license whose business address of record is in this area, from CSLB's public list of currently renewed licenses (downloaded {FETCHED}). The address is not a service area, D-28 also covers gates and other doors, and a license doesn't guarantee fair pricing. <a href="/how-to-check-a-garage-door-contractor-license/">Re-check the license</a> and get a written estimate.</div>"""

# ---------- builders ----------
def build_city(c, city):
    rows = by_county[c][city]; path = city_path(c, city)
    others = sorted((x for x in by_county[c] if x != city and city_live(c, x)), key=lambda x: -len(by_county[c][x]))[:12]
    body = f"""<h1>Licensed garage door companies in {E(city)}, CA</h1>
<p class="lede">{len(rows)} {'company holds' if len(rows)==1 else 'companies hold'} an active CSLB D-28 license with a business address in {E(city)} ({E(c)} County). Verify before you call.</p>
{CAVEAT}{FEATURED}
<h2>{E(city)} D-28 license holders</h2>{''.join(company_card(r) for r in rows)}
<h2>Before you call</h2><ul><li><a href="/how-to-check-a-garage-door-contractor-license/">How to check a license in 60 seconds</a></li><li><a href="/garage-door-spring-replacement-cost/">Fair price for spring replacement</a></li><li><a href="/garage-door-repair-scams/">How the garage door scam works</a></li></ul>
{lead_form(city)}
{('<h2>Nearby in ' + E(c) + ' County</h2><ul class="grid">' + ''.join(f'<li><a href="{city_path(c,x)}">{E(x)}</a> ({len(by_county[c][x])})</li>' for x in others) + '</ul>') if others else ''}"""
    page(path, f"Licensed Garage Door Repair in {city}, CA ({len(rows)} CSLB-licensed) | {BRAND}",
         f"{len(rows)} garage door companies with an active California D-28 license in {city}, {c} County. License numbers, bond and workers' comp from CSLB data ({FETCHED}).",
         body, [company_schema(rows, f"CSLB D-28 licensed garage door contractors in {city}, CA")],
         [("Home", "/"), ("Cities", "/garage-door-repair/"), (f"{c} County", county_path(c)), (city, path)])

def build_county(c):
    cities = by_county[c]; n = sum(len(v) for v in cities.values()); path = county_path(c)
    order = sorted(cities, key=lambda x: (-len(cities[x]), x))
    def link(x): return f'<a href="{city_path(c,x)}">{E(x)}</a>' if city_live(c, x) else E(x)
    body = f"""<h1>Licensed garage door companies in {E(c)} County</h1>
<p class="lede">{n} contractors with an active CSLB D-28 license list a business address in {E(c)} County, across {len(cities)} cities.</p>{CAVEAT}{FEATURED}
<h2>By city</h2><ul class="grid">{''.join(f'<li>{link(x)} ({len(cities[x])})</li>' for x in order)}</ul>"""
    rows_all = []
    rest = [x for x in order if not city_live(c, x)]
    if rest: body += "<h2>Cities without their own page yet</h2>"
    for x in order:
        rows_all += cities[x]
        if x in rest: body += f'<h3 id="{slug(x)}">{E(x)}</h3>' + "".join(company_card(r) for r in cities[x])
    body += lead_form()
    page(path, f"Licensed Garage Door Repair in {c} County, CA ({n} CSLB-licensed) | {BRAND}",
         f"All {n} garage door contractors with an active California D-28 license in {c} County, by city, from CSLB public data ({FETCHED}).",
         body, [{"@context": "https://schema.org", "@type": "ItemList", "name": f"Cities with CSLB D-28 licensed garage door contractors in {c} County",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x, "url": BASE + city_path(c, x)} for i, x in enumerate(y for y in order if city_live(c, y))]}]
         + ([company_schema([r for x in rest for r in cities[x]], f"Other CSLB D-28 licensed contractors in {c} County")] if rest else []),
         [("Home", "/"), ("Cities", "/garage-door-repair/"), (f"{c} County", path)])

def build_guide(g):
    src = "".join(f'<li><a href="{E(s["url"])}" rel="nofollow noopener">{E(s["title"])}</a></li>' for s in g.get("sources", []))
    body = f'<h1>{E(g["h1"])}</h1><p class="meta">Updated {E(g.get("updated", TODAY))}</p>{g["body"]}{FEATURED}{lead_form()}<h2>Sources</h2><ol class="sources">{src}</ol>'
    art = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "dateModified": g.get("updated", TODAY), "publisher": {"@type": "Organization", "name": BRAND},
           "citation": [s["url"] for s in g.get("sources", [])]}
    page(g["path"], f'{g["title"]} | {BRAND}', g["description"], body, [art], [("Home", "/"), (g["h1"], g["path"])], g.get("updated"))

def build_report(q):
    c = q["county"]; rows = [r for city in by_county[c].values() for r in city]; path = f'/reports/{q["slug"]}/'
    if q["report"] == "wc_insured":
        sel = sorted([r for r in rows if r["workers_comp_type"].startswith("Workers' Compensation")], key=lambda r: (r["city"], r["business_name"]))
        h1 = f"{c} County garage door companies with workers' comp insurance on file"
        intro = f"Of {len(rows)} active D-28 license holders in {c} County on CSLB's list, {len(sel)} show a workers' compensation insurance policy on file. CSLB warns that if an uninsured worker is injured on your property you could be financially liable. The rest are mostly marked exempt (no employees declared)."
    elif q["report"] == "new_licenses":
        yr = q["year"]; sel = sorted([r for r in rows if r["issue_date"].endswith(str(yr))], key=lambda r: r["issue_date"][-4:] + r["issue_date"][:5], reverse=True)
        h1 = f"New garage door contractor licenses in {c} County ({yr})"
        intro = f"{len(sel)} active D-28 licenses on CSLB's {c} County list were issued in {yr}. A new license isn't a red flag by itself, but you can't rely on a long track record — check reviews and get a written estimate."
    elif q["report"] == "longest_licensed":
        def key(r):
            m, d, y = (r["issue_date"] + "//").split("/")[:3]; return (y or "9999") + m + d
        sel = sorted([r for r in rows if r["issue_date"]], key=key)[:q.get("limit", 40)]
        h1 = f"Longest-licensed garage door companies in {c} County"
        intro = f"The {len(sel)} active D-28 license holders in {c} County with the earliest license issue dates on CSLB's list. Longevity is one trust signal, not a guarantee."
    else: raise ValueError(q["report"])
    body = f'<h1>{E(h1)}</h1><p class="lede">{E(intro)}</p>{CAVEAT}{FEATURED}' + "".join(company_card(r) for r in sel) + lead_form()
    body += f'<h2>Sources</h2><ol class="sources"><li><a href="https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty">CSLB Public Data Portal, List by Classification and County (C-61/D-28), downloaded {FETCHED}</a></li><li><a href="https://cslb.ca.gov/consumers/hire_a_contractor/finding_the_right_contractor.aspx">CSLB: finding the right licensed contractor</a></li></ol>'
    page(path, f"{h1} | {BRAND}", intro[:155], body, [company_schema(sel, h1)], [("Home", "/"), ("Reports", "/garage-door-repair/"), (h1, path)])
    return path, h1

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True); shutil.copy(ROOT / "assets" / "style.css", OUT / "assets" / "style.css")
    extra_links = []
    for g in core_guides + pub_guides: build_guide(g)
    for c in live_counties:
        build_county(c)
    for c in by_county:
        for city in by_county[c]:
            if city_live(c, city): build_city(c, city)
    for q in QUEUE:
        if q["type"] == "report" and q["id"] in PUB_IDS: extra_links.append(build_report(q))
    # cities index
    body = "<h1>Licensed garage door companies by city</h1><p class='lede'>Southern California cities with active CSLB D-28 license holders.</p>"
    for c in CFG["counties"]:
        if c not in by_county: continue
        live = [x for x in sorted(by_county[c]) if city_live(c, x)]
        hub = f'<a href="{county_path(c)}">{E(c)} County</a>' if c in live_counties else f"{E(c)} County (coming soon)"
        body += f"<h2>{hub}</h2>" + ("<ul class='grid'>" + "".join(f'<li><a href="{city_path(c,x)}">{E(x)}</a> ({len(by_county[c][x])})</li>' for x in live) + "</ul>" if live else "")
    if extra_links: body += "<h2>Reports</h2><ul>" + "".join(f'<li><a href="{p}">{E(t)}</a></li>' for p, t in extra_links) + "</ul>"
    page("/garage-door-repair/", f"Garage Door Repair by City – CSLB-Licensed Pros in SoCal | {BRAND}", "Find CSLB-licensed garage door companies by city across Los Angeles County and Southern California.", body, crumbs=[("Home", "/"), ("Cities", "/garage-door-repair/")])
    # about
    page("/about/", f"About {BRAND} & Methodology", f"How {BRAND} builds its list of licensed garage door companies from CSLB public data.",
         f"""<h1>About {BRAND}</h1><p class="lede">{BRAND} helps Southern California homeowners verify a garage door company before they call.</p>
<h2>Where the company data comes from</h2><p>Every listing comes from the California Contractors State License Board's free <a href="https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty">List by Classification and County</a> download for classification C-61/D-28 (Doors, Gates &amp; Activating Devices), which contains currently renewed licenses. Last downloaded {FETCHED}. We show license number, business name, city, ZIP, phone, classifications, dates, bond surety and workers' comp status as published by CSLB. We do not show street addresses on listing pages.</p>
<h2>What we don't do</h2><ul><li>We don't invent prices; price pages cite their sources.</li><li>We don't rank companies by payment. Any future paid placement will be labeled "Sponsored" and limited to CSLB-licensed companies.</li></ul>
<h2>Corrections</h2><p>Licenses change daily. If a listing is wrong, CSLB's <a href="https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx">Instant License Check</a> is the source of truth. <!-- TODO: corrections contact email --></p>""",
         crumbs=[("Home", "/"), ("About", "/about/")])
    # home
    core = by_county[CFG["core_county"]]; n_core = sum(len(v) for v in core.values())
    n_all = sum(len(v) for c in by_county.values() for v in c.values())
    search_idx = {}
    for c in by_county:
        for city, rows in by_county[c].items():
            if not city_live(c, city): continue
            search_idx[city.lower()] = u(city_path(c, city))
            for r in rows: search_idx.setdefault(r["zip"], u(city_path(c, city)))
    top = sorted(core, key=lambda x: -len(core[x]))[:24]
    guides_html = "".join(f'<li><a href="{g["path"]}">{E(g["h1"])}</a></li>' for g in core_guides + pub_guides)
    body = f"""<section class="hero"><h1>Verify before you call.</h1>
<p class="lede">Find garage door companies with an active California contractor license (CSLB D-28), see fair published prices, and learn the scam playbook — before anyone touches your door.</p>
<form class="search" onsubmit="event.preventDefault();var v=this.q.value.trim().toLowerCase();var u=IDX[v];if(u){{location.href=u}}else{{document.getElementById('nf').hidden=false}}">
<input name="q" list="cities" placeholder="City or ZIP, e.g. Pasadena or 91101" aria-label="City or ZIP"><button class="btn">Search</button></form>
<datalist id="cities">{''.join(f'<option value="{E(k.title())}">' for k in sorted(k for k in search_idx if not k.isdigit()))}</datalist>
<p id="nf" class="meta" hidden>No listed companies there yet. Try a nearby city or <a href="/garage-door-repair/">browse all cities</a>.</p></section>
<p><strong>{n_core}</strong> active D-28 license holders in Los Angeles County and <strong>{n_all}</strong> across six SoCal counties, from CSLB public data downloaded {FETCHED}.</p>
<div class="note">ABC7 reported in Sept 2026 that a $97 garage door tune-up ad turned into a ~$4,000 bill for a Woodland Hills homeowner. <a href="/garage-door-repair-scams/">See how the scam works</a>.</div>
<h2>Three checks before you call</h2><ol><li><strong>Ask for the license number</strong> — California requires it on every contractor ad. <a href="/how-to-check-a-garage-door-contractor-license/">Check it in 60 seconds.</a></li><li><strong>Know the fair range</strong> — <a href="/garage-door-spring-replacement-cost/">spring replacement</a> is typically a few hundred dollars per published sources.</li><li><strong>Get it in writing</strong> before work starts.</li></ol>
<h2>Popular Los Angeles County cities</h2><ul class="grid">{''.join(f'<li><a href="{city_path(CFG["core_county"],x)}">{E(x)}</a> ({len(core[x])})</li>' for x in top)}</ul>
<p><a href="/garage-door-repair/">All cities →</a></p>
{FEATURED}<h2>Guides</h2><ul>{guides_html}</ul>{lead_form()}
<script>var IDX={json.dumps(search_idx, separators=(",", ":"))};</script>"""
    site_schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": BASE + "/"},
                   {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": BASE + "/"}]
    page("/", f"{BRAND} – Licensed Garage Door Repair in Los Angeles. Verify Before You Call.",
         f"Find CSLB-licensed garage door companies in Los Angeles and SoCal, check licenses, see sourced fair prices and avoid garage door repair scams.", body, site_schema)
    # sitemap + robots + 404
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{lm}</lastmod></url>\n" for p, lm in sorted(PAGES)) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm)
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (OUT / "404.html").write_text(prefix_hrefs(f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/style.css"><div class="wrap"><h1>Page not found</h1><p><a href="/">{BRAND} home</a></p></div>'))
    (OUT / ".nojekyll").write_text("")
    return len(PAGES)

if __name__ == "__main__":
    print(f"built {build()} pages into {OUT}")
