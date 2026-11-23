#!/usr/bin/env bash
# Ping IndexNow (Bing, Yandex, and other participating engines) with every URL in site/sitemap.xml.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f indexnow.key ]]; then
  echo "indexnow: missing indexnow.key" >&2
  exit 1
fi
if [[ ! -f site/sitemap.xml ]]; then
  echo "indexnow: site/sitemap.xml is missing. Run python3 build.py first." >&2
  exit 1
fi

payload=$(python3 - << 'PY'
import json, re
from pathlib import Path
from urllib.parse import urlparse

root = Path(".")
key = (root / "indexnow.key").read_text().strip()
cfg = json.loads((root / "config.json").read_text())
base = cfg["site_url"].rstrip("/")
host = urlparse(base).hostname or ""
xml = (root / "site" / "sitemap.xml").read_text()
urls = re.findall(r"<loc>([^<]+)</loc>", xml)
# Keep only this host; skip the key file if it ever appears.
urls = [u for u in urls if urlparse(u).hostname == host]
print(json.dumps({
    "host": host,
    "key": key,
    "keyLocation": f"{base}/{key}.txt",
    "urlList": urls,
}))
print(f"# {len(urls)} URLs", file=__import__("sys").stderr)
PY
)

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
code=$(curl -sS -o "$tmp" -w "%{http_code}" \
  -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$payload") || true

# 200 OK, 202 Accepted are success. 204 is also used by some endpoints.
if [[ "$code" == "200" || "$code" == "202" || "$code" == "204" ]]; then
  echo "indexnow: accepted (HTTP $code)"
  exit 0
fi
echo "indexnow: unexpected HTTP $code" >&2
sed -n '1,20p' "$tmp" >&2 || true
exit 1
