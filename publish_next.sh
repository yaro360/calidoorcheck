#!/usr/bin/env bash
# Nightly: publish one new page from the queue, rebuild site + sitemap, commit, log, deploy live.
set -euo pipefail
cd "$(dirname "$0")"
python3 publish_next.py
./deploy.sh
