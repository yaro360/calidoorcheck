#!/usr/bin/env python3
"""Publish ONE new page from queue.json: mark it in state/published.json, rebuild, commit, log."""
import json, pathlib, subprocess, datetime, sys
ROOT = pathlib.Path(__file__).resolve().parent
Q = json.loads((ROOT / "queue.json").read_text())
PUBF = ROOT / "state" / "published.json"
pub = json.loads(PUBF.read_text()) if PUBF.exists() else []
done = {p["id"] for p in pub}
now = datetime.datetime.now().astimezone()
LOG = ROOT / "PUBLISH_LOG.md"
if not LOG.exists(): LOG.write_text("# FairDoorLA publish log\n\n| When (local) | Queue id | Page | URL path | Pages in site |\n|---|---|---|---|---|\n")

def ready(q):
    if q["type"] == "guide": return (ROOT / "content" / "guides" / f'{q["slug"]}.html').exists()
    return True

skipped = []
item = None
for q in Q:
    if q["id"] in done: continue
    if ready(q): item = q; break
    skipped.append(q["id"])
if item is None:
    msg = f"| {now:%Y-%m-%d %H:%M %Z} | — | Nothing ready to publish | — | — |\n"
    with LOG.open("a") as f: f.write(msg)
    print("Nothing ready. Guides waiting for content:", ", ".join(skipped) or "none"); sys.exit(0)

pub.append({"id": item["id"], "published_at": now.isoformat(timespec="seconds")})
PUBF.write_text(json.dumps(pub, indent=1))
sys.path.insert(0, str(ROOT))
import build  # noqa: E402  (module import builds nothing; call build())
n = build.build()
slug = lambda s: build.slug(s)
if item["type"] == "city": path = build.city_path(item["county"], item["city"])
elif item["type"] == "county": path = build.county_path(item["county"])
elif item["type"] == "report": path = f'/reports/{item["slug"]}/'
else: path = f'/{item["slug"]}/'
if not (ROOT / "site" / path.lstrip("/") / "index.html").exists():
    print("ERROR: page not generated", path); sys.exit(1)
with LOG.open("a") as f:
    f.write(f'| {now:%Y-%m-%d %H:%M %Z} | `{item["id"]}` | {item["title"]} | `{path}` | {n} |\n')
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
subprocess.run(["git", "commit", "-q", "-m", f'Publish {item["id"]}: {item["title"]} ({path})'], cwd=ROOT, check=True)
remaining = sum(1 for q in Q if q["id"] not in {p["id"] for p in pub})
print(f"Published {item['id']} -> {path}. Site now {n} pages. {remaining} queue items left" + (f"; skipped (needs content): {', '.join(skipped)}" if skipped else ""))
