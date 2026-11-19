#!/usr/bin/env bash
# Re-download CSLB C-61/D-28 lists for the 6 SoCal counties, normalize, rebuild, commit.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/fetch_cslb.py
python3 scripts/normalize.py
python3 build.py
git add -A
git commit -q -m "Data refresh: CSLB C-61/D-28 lists $(date +%F)" || echo "No changes to commit"
