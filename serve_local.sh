#!/usr/bin/env bash
# Serve site/ under the same path prefix used in production (e.g. /fairdoorla/).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8080}"
PREFIX=$(python3 -c 'import json; from urllib.parse import urlparse; print(urlparse(json.load(open("config.json"))["site_url"]).path.rstrip("/"))')
if [[ -z "$PREFIX" ]]; then
  echo "Serving site/ at http://127.0.0.1:${PORT}/"
  exec python3 -m http.server "$PORT" --directory site
fi
tmp=$(mktemp -d)
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT
mkdir -p "$(dirname "$tmp$PREFIX")"
ln -s "$(pwd)/site" "$tmp$PREFIX"
cat > "$tmp/index.html" <<HTML
<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=${PREFIX}/">
<p><a href="${PREFIX}/">FairDoorLA</a></p>
HTML
echo "Serving at http://127.0.0.1:${PORT}${PREFIX}/"
python3 -m http.server "$PORT" --directory "$tmp"
