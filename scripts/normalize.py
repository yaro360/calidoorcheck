#!/usr/bin/env python3
"""Normalize raw CSLB xlsx files into data/licenses.csv and data/licenses.json."""
import json, pathlib, re, datetime
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SOURCE = "CSLB Public Data Portal - List by Classification and County (C-61/D-28), https://www.cslb.ca.gov/onlineservices/dataportal/ListByCounty"
fetched = (RAW / "FETCHED_AT.txt").read_text().strip()
def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    return re.sub(r"\s+", " ", str(v)).strip()
rows = []
for f in sorted(RAW.glob("cslb_C61D28_*.xlsx")):
    df = pd.read_excel(f, dtype=str)
    for _, r in df.iterrows():
        g = lambda k: clean(r.get(k))
        city = g("City").title()
        rows.append({
            "license_number": g("LicenseNumber"), "business_name": g("BusinessName"), "business_type": g("BusinessType"),
            "address": g("Address"), "city": city, "state": g("State"), "zip": g("ZIP Code")[:5], "county": g("County"),
            "phone": g("PhoneNumber"), "issue_date": g("IssueDate"), "expiration_date": g("ExpirationDate"),
            "classifications": g("Classification(s)"), "status": g("Status"),
            "bond_surety": g("SuretyCompany"), "bond_number": g("ContractorBondNumber"), "bond_effective": g("BondEffectiveDate"),
            "bond_cancelled": g("BondCancellationDate"),
            "workers_comp_type": g("WorkersCompCoverageType"), "workers_comp_insurer": g("WorkersCompInsuranceCompany"),
            "workers_comp_policy": g("WorkersCompPolicyNumber"), "workers_comp_effective": g("EffectiveDate"),
            "workers_comp_expires": g("ExpirationDate1"), "workers_comp_cancelled": g("CancellationDate"),
            "workers_comp_suspended": g("WorkersCompSuspendDate"),
            "source": SOURCE, "source_file": f.name, "fetched_at": fetched,
        })
# de-dupe on license number (a license appears once per county file it is listed in)
seen, out = set(), []
for r in rows:
    k = (r["license_number"], r["county"])
    if k in seen or not r["license_number"]: continue
    seen.add(k); out.append(r)
df = pd.DataFrame(out)
df.to_csv(ROOT / "data" / "licenses.csv", index=False)
(ROOT / "data" / "licenses.json").write_text(json.dumps(out, indent=1))
print(len(out), "rows"); print(df.groupby("county").size().to_string()); print(df["status"].value_counts().to_string())
print(df["workers_comp_type"].value_counts().to_string())
