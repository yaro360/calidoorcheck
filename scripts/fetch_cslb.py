#!/usr/bin/env python3
"""Download CSLB 'List by Classification and County' (official, free) for C-61/D-28
(Doors, Gates & Activating Devices) in SoCal counties. Saves raw .xlsx to data/raw/."""
import re, sys, datetime, pathlib, requests
URL = "https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty"
COUNTIES = {"19": "Los Angeles", "30": "Orange", "33": "Riverside", "36": "San Bernardino", "37": "San Diego", "56": "Ventura"}
CLASSES = ["C-61/D-28"]
RAW = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (FairDoorLA data refresh)"
def hidden(html):
    return {m.group(1): m.group(2) for m in re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html)}
for cid, cname in COUNTIES.items():
    page = s.get(URL, timeout=60).text
    data = hidden(page)
    data.update({"__EVENTTARGET": "ctl00$MainContent$btnSearch", "__EVENTARGUMENT": ""})
    form = list(data.items()) + [("ctl00$MainContent$lbClassification", c) for c in CLASSES] + [("ctl00$MainContent$lbCounty", cid)]
    r = s.post(URL, data=form, timeout=180)
    ct = r.headers.get("Content-Type", "")
    out = RAW / f"cslb_C61D28_{cname.replace(' ', '_')}.xlsx"
    if "html" in ct and b"<table" not in r.content[:5000].lower():
        print(f"!! {cname}: got HTML, not a file ({len(r.content)} bytes)", file=sys.stderr)
        (RAW / f"error_{cid}.html").write_bytes(r.content); continue
    out.write_bytes(r.content)
    print(f"{cname}: {len(r.content)} bytes, {ct}, {r.headers.get('Content-Disposition','')}")
(RAW / "FETCHED_AT.txt").write_text(datetime.datetime.now().astimezone().isoformat() + "\n")
