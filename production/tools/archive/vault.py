#!/usr/bin/env python3
"""Writes assets/archive-vault.json: the legal record of every archive item downloaded for the E01
archive-format sample (used or not), with licence basis quoted from the item's own metadata."""
import json, os, glob, hashlib, re
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
REPO = "/home/user/Universe-Series"
U = json.load(open(f"{S}/arch/usage.json"))
usage, srclog = U["usage"], U["srclog"]
REJECT = {
    "Immigrat1946": "Not used (taste): Ellis Island inspections of real immigrants; cutting comedy against them would be distasteful.",
    "salvaged_skills": "Not used (taste): wounded veterans' rehabilitation framed as 'salvage'; wrong as a joke about things 'the register forgot'.",
    "Financin1935": "Not used: corporate name and logo (Household Finance Corporation) on screen.",
}
items = []
for mp in sorted(glob.glob(f"{S}/vault/meta/*.json")):
    if mp.endswith(".files.json"):
        continue
    m = json.load(open(mp)); vid = m["id"]
    if m.get("skip"):
        items.append(dict(id=vid, status="not downloaded", reason=m["skip"]))
        continue
    md = m.get("meta", {})
    uses = [dict(shot=u[3], from_s=u[1], to_s=u[2]) for u in usage if u[0] == vid]
    ranged = sorted({(v[0], v[1], v[2]) for k, v in srclog.items() if k.split("_", 1)[1][:-4] == vid and v[0].startswith("http")})
    rec = dict(id=vid, title=m.get("title"), year=str(m.get("year") or "")[:4] or None, source_page_url=m["page"],
               direct_file_url=m["url"], local_path=m["local"], bytes=m["bytes"], sha256=m["sha256"])
    if vid.startswith("loc-"):
        rights = m["lic"][0] if isinstance(m["lic"], list) and m["lic"] else str(m["lic"])
        first = re.sub("<[^>]+>", "", rights).strip().split("\n")[0]
        rec.update(licence_basis={"rights_field_quote": first[:400], "created_published": md.get("created_published"),
                                  "basis": "Published in the United States in 1903-1906 (before 1931): public domain in the US."},
                   credit_line="Library of Congress, Motion Picture, Broadcasting, and Recorded Sound Division",
                   producer=(md.get("contributor_names") or [None])[0] if isinstance(md.get("contributor_names"), list) else md.get("contributor_names"))
    else:
        rec.update(licence_basis={"licenseurl": md.get("licenseurl") or m.get("lic"), "collection": "prelinger",
                                  "basis": "Item metadata field 'licenseurl' states Public Domain (archive.org)."},
                   credit_line=f"{m.get('title')}" + (f" ({rec['year']})" if rec["year"] else "") + " · Prelinger Archives (public domain), via Internet Archive",
                   producer=m.get("creator"))
    if ranged:
        rec["ranges_fetched_from_original"] = [dict(direct_url=r[0], from_s=r[1], duration_s=r[2],
                                                    note="ffmpeg -ss/-t range read of the MPEG-2 original (cleaner than the h.264 derivative); "
                                                         "audio discarded") for r in ranged]
    rec["time_ranges_used"] = uses
    rec["audio"] = "stripped (never used)"
    if vid in REJECT:
        rec["status"] = "downloaded, rejected"; rec["reason"] = REJECT[vid]
    else:
        rec["status"] = "used" if uses else "downloaded, not used in this sample"
    items.append(rec)
out = dict(
    purpose="Archive vault for the Episode 1 archive-format sample (PIP's file on the case). This file is the legal record.",
    built="2026-11-28", local_vault=f"{S}/vault/dl (scratch; large media never goes in git)",
    rules=["Only items whose own metadata states public domain (Prelinger licenseurl) or US films published before 1931 (LOC).",
           "No NonCommercial or ShareAlike items. No celebrity, brand-logo-filling or distasteful news material.",
           "All archive audio stripped."],
    items=items)
json.dump(out, open(f"{REPO}/assets/archive-vault.json", "w"), indent=1, ensure_ascii=False)
n_used = sum(1 for i in items if i.get("status") == "used")
print(f"{len(items)} items, {n_used} used, {sum(i.get('bytes', 0) for i in items) / 1e9:.2f} GB")
