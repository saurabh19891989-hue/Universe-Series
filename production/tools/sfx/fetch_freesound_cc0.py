#!/usr/bin/env python3
"""Fetch CC0 sound effects from Freesound (no account / API key needed) with a per-file licence check.

  python3 fetch_freesound_cc0.py search "footsteps concrete" [--n 8] [--max-dur 30]
  python3 fetch_freesound_cc0.py get OUT_DIR MANIFEST.json ID[:name] [ID[:name] ...]

`search` lists CC0-filtered results (id, author, duration, title) to pick from.
`get` opens each sound's own page, REFUSES the file unless the page's licence link is
http(s)://creativecommons.org/publicdomain/zero/1.0/ (CC0 1.0), then downloads the public
high-quality preview (OGG ~192 kbps, falling back to the HQ MP3 ~128 kbps; the original WAV needs a
logged-in account), converts it to 48 kHz WAV, and appends the record (URL, author, title,
licence wording, licence URL, preview URL, retrieved date) to MANIFEST.json.
CC0 needs no credit; we still record the author so the credits can thank them.
Downloaded audio is untrusted data: it is only decoded by ffmpeg, never executed.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

CC0 = re.compile(r'href="https?://creativecommons\.org/publicdomain/zero/1\.0/?"[^>]*>\s*Creative Commons 0\s*<')
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-client"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def search(q, n=8, max_dur=60.0):
    url = "https://freesound.org/search/?" + urllib.parse.urlencode({"q": q, "f": 'license:"Creative Commons 0"'})
    page = get(url).decode("utf-8", "replace")
    ids = []
    for m in re.finditer(r'href="/people/([^/"]+)/sounds/(\d+)/"', page):
        if (m.group(1), m.group(2)) not in ids:
            ids.append((m.group(1), m.group(2)))
    out = []
    for user, sid in ids[: n * 2]:
        info = page_info(user, sid)
        if info and info["duration_s"] <= max_dur:
            out.append(info)
        if len(out) >= n:
            break
    return out


def page_info(user, sid):
    url = f"https://freesound.org/people/{user}/sounds/{sid}/"
    try:
        page = get(url).decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None
    title = re.search(r'<meta property="og:audio:title" content="([^"]*)"', page)
    dur = re.search(r'data-duration="([\d.]+)"', page)
    ok = bool(CC0.search(page))
    prev = re.findall(r'https://cdn\.freesound\.org/previews/\d+/' + sid + r'_\d+-hq\.(?:ogg|mp3)', page)
    if not prev:
        lq = re.findall(r'https://cdn\.freesound\.org/previews/\d+/' + sid + r'_\d+-lq\.mp3', page)
        prev = [lq[0].replace("-lq.mp3", "-hq.ogg"), lq[0].replace("-lq.mp3", "-hq.mp3")] if lq else []
    return dict(id=int(sid), author=user, title=html.unescape(title.group(1)) if title else "",
                url=url, duration_s=float(dur.group(1)) if dur else 0.0, cc0=ok, previews=sorted(set(prev), reverse=True))


def fetch(out_dir, manifest, specs):
    os.makedirs(out_dir, exist_ok=True)
    man = json.load(open(manifest)) if os.path.exists(manifest) else []
    have = {m["freesound_id"] for m in man}
    for spec in specs:
        sid, _, name = spec.partition(":")
        if int(sid) in have:
            continue
        # the user path is not needed: freesound redirects /s/<id>/ to the sound page
        page = get(f"https://freesound.org/s/{sid}/").decode("utf-8", "replace")
        user = re.search(r'href="/people/([^/"]+)/sounds/' + sid + '/', page)
        info = page_info(user.group(1) if user else "x", sid)
        if not info or not info["cc0"]:
            print(f"REFUSED {sid}: licence on its page is not CC0 1.0")
            continue
        dst = os.path.join(out_dir, (name or f"fs{sid}") + ".wav")
        tmp = dst + ".dl"
        src = None
        for pv in info["previews"]:
            try:
                open(tmp, "wb").write(get(pv)); src = pv; break
            except Exception:  # noqa: BLE001
                continue
        if not src:
            print(f"FAILED {sid}: no preview"); continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", "48000", "-c:a", "pcm_s24le", dst], check=True)
        os.remove(tmp)
        rec = dict(name=name or f"fs{sid}", file=os.path.basename(dst), freesound_id=int(sid), title=info["title"],
                   author=info["author"], source_url=info["url"], licence="Creative Commons 0 (CC0 1.0 Universal)",
                   licence_url="https://creativecommons.org/publicdomain/zero/1.0/",
                   licence_wording_on_page="Creative Commons 0", downloaded=src,
                   quality_note="Freesound public HQ preview (lossy); original WAV needs a logged-in download",
                   duration_s=info["duration_s"], retrieved=datetime.date.today().isoformat(),
                   credit=f'"{info["title"]}" by {info["author"]} (freesound.org, CC0)')
        man.append(rec)
        json.dump(man, open(manifest, "w"), indent=1)
        print("OK", rec["name"], info["duration_s"], info["title"], "by", info["author"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "search":
        n = int(a[a.index("--n") + 1]) if "--n" in a else 8
        md = float(a[a.index("--max-dur") + 1]) if "--max-dur" in a else 60.0
        for r in search(a[1], n, md):
            print(r["id"], r["author"], round(r["duration_s"], 1), "CC0" if r["cc0"] else "NOT-CC0", r["title"])
    elif a and a[0] == "get":
        fetch(a[1], a[2], a[3:])
    else:
        print(__doc__)
