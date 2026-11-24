#!/usr/bin/env python3
"""Validate SEO/AEO markup and internal links in site/."""
import json, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CFG = json.loads((ROOT / "config.json").read_text())
BASE = CFG["site_url"].rstrip("/")
HOST = urlparse(BASE).hostname

def texts(html, tag):
    return re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", html, flags=re.I | re.S)

def meta(html, name=None, prop=None):
    if name:
        m = re.search(rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"', html, re.I)
        if not m:
            m = re.search(rf'<meta\s+content="([^"]*)"\s+name="{re.escape(name)}"', html, re.I)
        return m.group(1) if m else None
    if prop:
        m = re.search(rf'<meta\s+property="{re.escape(prop)}"\s+content="([^"]*)"', html, re.I)
        if not m:
            m = re.search(rf'<meta\s+content="([^"]*)"\s+property="{re.escape(prop)}"', html, re.I)
        return m.group(1) if m else None

def schemas(html):
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        out.append(json.loads(raw))
    return out

def types_of(objs):
    t = []
    for o in objs:
        if isinstance(o, dict):
            t.append(o.get("@type"))
        elif isinstance(o, list):
            t.extend(x.get("@type") for x in o if isinstance(x, dict))
    return t

def page_kind(rel):
    if rel == "index.html":
        return "home"
    if rel == "about/index.html":
        return "about"
    if rel == "garage-door-repair/index.html":
        return "cities"
    if rel.startswith("garage-door-repair/") and rel.endswith("/index.html"):
        parts = rel.split("/")
        if len(parts) == 3:
            return "county"
        if len(parts) == 4:
            return "city"
    if rel.endswith("/index.html") and not rel.startswith("garage-door-repair/"):
        return "guide"
    return "other"

issues = []
pages = [p for p in SITE.rglob("*.html") if p.name != "404.html"]
titles = Counter()

for p in sorted(pages):
    rel = str(p.relative_to(SITE))
    html = p.read_text()
    kind = page_kind(rel)
    if 'lang="en"' not in html[:200]:
        issues.append(f"{rel}: missing html lang=en")
    if 'name="viewport"' not in html:
        issues.append(f"{rel}: missing viewport")
    title = (texts(html, "title") or [""])[0].strip()
    if not title:
        issues.append(f"{rel}: missing title")
    titles[title] += 1
    if not meta(html, name="description"):
        issues.append(f"{rel}: missing meta description")
    if not re.search(r'<link rel="canonical" href="https://calidoorcheck\.com/', html):
        issues.append(f"{rel}: missing or wrong canonical")
    h1 = texts(html, "h1")
    if len(h1) != 1:
        issues.append(f"{rel}: expected 1 H1, found {len(h1)}")
    for prop in ("og:title", "og:description", "og:url", "og:type", "og:site_name", "og:locale"):
        if not meta(html, prop=prop):
            issues.append(f"{rel}: missing {prop}")
    for name in ("twitter:card", "twitter:title", "twitter:description"):
        if not meta(html, name=name):
            issues.append(f"{rel}: missing {name}")
    # Leave og:image / icons to the branding worker; do not require them.
    try:
        sch = schemas(html)
    except json.JSONDecodeError as e:
        issues.append(f"{rel}: invalid JSON-LD ({e})")
        continue
    t = types_of(sch)
    blob = json.dumps(sch)
    if re.search(r'"(@type|reviewRating|aggregateRating)"\s*:\s*"(Review|AggregateRating|Rating)"', blob) or "aggregateRating" in blob or '"review"' in blob.lower():
        if "Review" in t or "AggregateRating" in t:
            issues.append(f"{rel}: must not claim reviews or ratings")
    if "BreadcrumbList" not in t and kind != "other":
        issues.append(f"{rel}: missing BreadcrumbList")
    if kind == "home" and "WebSite" not in t:
        issues.append(f"{rel}: missing WebSite")
    if kind == "home" and "Organization" not in t:
        issues.append(f"{rel}: missing Organization")
    if kind == "home" and "SearchAction" not in blob:
        issues.append(f"{rel}: WebSite missing SearchAction")
    if kind == "city" and "ItemList" not in t:
        issues.append(f"{rel}: missing ItemList")
    if kind in ("city", "guide") and "FAQPage" not in t:
        issues.append(f"{rel}: missing FAQPage")
    if kind == "guide":
        if "Article" not in t:
            issues.append(f"{rel}: missing Article")
        else:
            arts = [s for s in sch if isinstance(s, dict) and s.get("@type") == "Article"]
            for a in arts:
                if not a.get("datePublished") or not a.get("dateModified"):
                    issues.append(f"{rel}: Article missing datePublished or dateModified")
    if kind in ("city", "guide") and "Quick answer:" not in html:
        issues.append(f"{rel}: missing Quick answer")
    if kind in ("city", "guide", "county", "about", "home") and "Last updated" not in html and "downloaded" not in html:
        issues.append(f"{rel}: missing last-updated / data source")

dupes = [t for t, n in titles.items() if n > 1 and t]
for t in dupes:
    issues.append(f"duplicate title ({titles[t]}): {t}")

# Link check
broken = []
checked = 0
skip_schemes = {"mailto", "tel", "javascript", "data"}
img_missing_alt = []

def resolve(path_rel, href):
    href = href.strip()
    if not href or href.startswith("#"):
        return None
    parsed = urlparse(href)
    if parsed.scheme in skip_schemes:
        return None
    if parsed.scheme in {"http", "https"} or parsed.netloc:
        if parsed.hostname and parsed.hostname != HOST:
            return None  # external, including protocol-relative //host/path
        path = parsed.path or "/"
    else:
        # relative or root-absolute
        base = "/" + str(Path(path_rel).parent).replace("\\", "/")
        if base.endswith("/."):
            base = "/"
        if not path_rel.endswith("index.html") and not path_rel.endswith("/"):
            base = "/" + str(Path(path_rel).parent).replace("\\", "/")
        if path_rel == "index.html":
            page_url = "/"
        elif path_rel.endswith("/index.html"):
            page_url = "/" + path_rel[: -len("index.html")]
        else:
            page_url = "/" + path_rel
        path = urlparse(urljoin("https://calidoorcheck.com" + page_url, href)).path
    path = unquote(path)
    return path

def exists(path):
    if path.endswith("/"):
        return (SITE / path.lstrip("/") / "index.html").is_file()
    candidate = SITE / path.lstrip("/")
    if candidate.is_file():
        return True
    if (candidate / "index.html").is_file():
        return True
    return False

for p in sorted(SITE.rglob("*.html")):
    rel = str(p.relative_to(SITE))
    html = p.read_text()
    for attr, val in re.findall(r'\b(href|src)="([^"]+)"', html):
        path = resolve(rel, val)
        if path is None:
            continue
        checked += 1
        if not exists(path):
            broken.append(f"{rel} -> {val} ({path})")
    for m in re.finditer(r"<img\b([^>]*)>", html, re.I):
        attrs = m.group(1)
        if not re.search(r'\balt=', attrs, re.I):
            img_missing_alt.append(rel)

print(f"Checked {len(pages)} HTML pages (excluding 404.html) and {checked} internal links.")
if img_missing_alt:
    issues.append(f"{len(img_missing_alt)} images missing alt: {img_missing_alt[:5]}")
if issues:
    print(f"VALIDATION ISSUES ({len(issues)}):")
    for i in issues:
        print(" -", i)
else:
    print("VALIDATION: all checks passed.")
print(f"BROKEN_LINKS: {len(broken)}")
for b in broken:
    print(" -", b)
sys.exit(1 if issues or broken else 0)
