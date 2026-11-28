#!/usr/bin/env python3
"""Builds episodes/E01/archive-sample-shotlist.json (PIP's file on the case, first ~5 min of E01),
pre-cuts every archive / NASA range it uses into arch/clips, and writes the usage table used by the
vault log. Run: python3 build.py [--no-cut]"""
import json, os, subprocess, sys, hashlib

REPO = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
A = f"{S}/arch"; V = f"{S}/vault/dl"; P = f"{S}/e01/plates"
U = "/root/.claude/uploads/3757f133-43aa-510b-bfaf-b45b089ed136"
CUT = "--no-cut" not in sys.argv
os.makedirs(f"{A}/clips", exist_ok=True)

conf = json.load(open(f"{REPO}/episodes/E01/dialogue-conform.json"))
SC = {s["scene"]: s for s in conf["scenes"]}

# ---------------------------------------------------------------- dialogue timeline
first = {"0": 2.0, "1": 75.6, "2": 109.6, "3": 157.4, "4": 216.9, "5": 241.6}
shift_from = {("0", 16): 0.9, ("3", 23): 0.8}          # added beats: shop bell, SEIZED stamp
HALL = {"3", "4", "5"}
lines = []; T = {}
for sc, t0 in first.items():
    add = 0.0
    for ln in SC[sc]["lines"]:
        add += shift_from.get((sc, ln["index"]), 0.0)
        st = round(t0 + ln["start_in_scene_s"] + add, 3)
        f = ln["file_treated"] or ln["file_dry"]
        lid = f"{sc}-{ln['index']:02d}"
        spk = {"LUCÍA": "LUCIA"}.get(ln["speaker"], ln["speaker"])
        rec = dict(id=lid, speaker=spk, src="${SCRATCH}/e01/dialogue/" + f, start_s=st, text=ln["text_spoken"])
        if sc in HALL and not ln["treatment"]:
            rec.update(reverb_db=-17, reverb_ir="${SCRATCH}/e01/sfx/customs_hall_reverb_tail_ir.wav")
        lines.append(rec)
        T[lid] = (st, st + ln["duration_s"])

def ls(i): return T[i][0]
def le(i): return T[i][1]

# ---------------------------------------------------------------- sources
SHIP = {"lens": f"{U}/96a4611b-Brass_robot_lens_waking_up_147eeb4c_1080p.mp4",
        "sandwich": f"{U}/9f9a45a9-Man_eating_sandwich_in_cockpit_b97ea111_1080p.mp4",
        "pilot": f"{U}/a0d34438-Pilot_taps_dead_cockpit_screen_0ea31db0_1080p.mp4",
        "stamp": f"{U}/ba3e7073-Robot_arm_stamping_paper_49081d01.mp4",
        "grin": f"{U}/b532efb6-Man_urging_someone_to_take_2fe4efd7.mp4"}
NASA = {"a2": (f"{P}/a2_flyby_1min_2160p30.mp4", "NASA's Scientific Visualization Studio / Ernie Wright", "NASA SVS VISUALISATION"),
        "viper": (f"{P}/ARC-20210920-AAV3366-VIPER-LandingSiteAnnouncement-YouTubeHD.mp4", "NASA's Scientific Visualization Studio", "NASA SVS VISUALISATION"),
        "shadow": (f"{P}/GSFC_20130306_Moons_m11218_Shadowed.mp4", "Dan Gallagher, Chris Smith (NASA/GSFC)", "NASA/GSFC VISUALISATION"),
        "moonview": (f"{P}/GSFC_20110617_LRO_m10794_Eclipse_Moonview.mp4", "Genna Duberstein, Ernie Wright, Chris Smith, Chris Meaney (NASA/GSFC)", "NASA/GSFC VISUALISATION"),
        "scarp": (f"{P}/GSFC_20190513_m4714_Lee_Lincoln_Scarp_Moon_Flyover.mp4", "David Ladd, Tom Waters, Ernie Wright (NASA/GSFC SVS)", "NASA SVS VISUALISATION · LRO DATA")}
for k, v in list(NASA.items()):
    if not os.path.exists(v[0]):
        import glob
        g = glob.glob(f"{P}/{os.path.basename(v[0]).split('.')[0][:30]}*")
        NASA[k] = (g[0], v[1], v[2])
DV = "${SCRATCH}/e01/datavis/"
usage = []   # (vault id, a, b, shot id)


def cut(src, a, dur, out, vf="fps=24", w=None):
    if os.path.exists(out) and os.path.getsize(out) > 1000 and "--recut" not in sys.argv:
        return
    vf2 = vf + (f",scale={w}:-2:flags=lanczos" if w else "")
    subprocess.run(["nice", "ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{dur + 0.3:.3f}", "-an",
                    "-vf", vf2, "-c:v", "libx264", "-crf", "15", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], check=True)


shots = []; exhibit_no = [0]
SRCLOG = {}   # clip -> (direct url or local file, a, dur)


def best_source(vid):
    """Prelinger: the MPEG-2 original on archive.org (much cleaner than the 640x480 h.264 derivative);
    we fetch only the range we use. LOC: the local 1440x1080 viewing copy."""
    if vid.startswith("loc-"):
        return f"{V}/{vid}.mp4", False
    fp = f"{S}/vault/meta/{vid}.files.json"
    if not os.path.exists(fp):
        import urllib.request
        d = json.load(urllib.request.urlopen(f"https://archive.org/metadata/{vid}", timeout=90))
        json.dump([{k: f.get(k) for k in ("name", "format", "size", "width", "height", "md5")} for f in d["files"]], open(fp, "w"))
    fl = json.load(open(fp))
    mp = [f for f in fl if f.get("format") == "MPEG2"]
    if mp:
        return f"https://archive.org/download/{vid}/{mp[0]['name']}", True
    return f"{V}/{vid}.mp4", False
VIEW = {"bezel": "${SCRATCH}/arch/bezel_agy1.jpg", "screen": [205, 150, 1207, 922], "panel": [1432, 36, 1844, 1030],
        "dials": [[1636, 352, 74], [1637, 657, 74]], "counter": [1638, 915]}


def add(sid, t0, t1, layers, kind, note="", camera=None, cards_at=None, sfx=None, music=None, credits=None, grade=None, extra=None):
    sh = dict(id=sid, duration_s=round(t1 - t0, 3), type=kind, note=note, layers=layers, _t0=round(t0, 3))
    if camera: sh["camera"] = camera
    if cards_at: sh["overlays"] = {"cards_at": cards_at}
    au = {}
    if sfx: au["sfx"] = sfx
    if music: au["music"] = music
    if au: sh["audio"] = au
    if credits: sh["credits"] = credits
    if grade: sh["grade"] = grade
    if extra: sh.update(extra)
    shots.append(sh)


def archive(sid, t0, t1, vid, a, title, sub, stamp=None, cont=False, speed=1.0, zoom=(1.0, 1.07), cx=0.5, cy=0.5, crop=None, note=""):
    dur = (t1 - t0) * speed
    out = f"{A}/clips/{sid}_{vid}.mp4"
    src, remote = best_source(vid)
    if remote:
        if not (os.path.exists(out) and os.path.getsize(out) > 1000) or "--recut" in sys.argv:
            subprocess.run(["nice", "ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, a - 2.0):.3f}", "-i", src, "-ss", f"{min(a, 2.0):.3f}",
                            "-t", f"{dur + 0.3:.3f}", "-an", "-vf", "bwdif=0,fps=24", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", out], check=True)
    else:
        cut(src, a, dur, out)
    SRCLOG[os.path.basename(out)] = (src, round(a, 3), round(dur, 3))
    usage.append((vid, round(a, 2), round(a + dur, 2), sid))
    if not cont:
        exhibit_no[0] += 1
    no = f"EXHIBIT {exhibit_no[0]}" + (" (CONT.)" if cont else "")
    v = dict(kind="viewer", src="${SCRATCH}/arch/clips/" + os.path.basename(out), in_s=0.0, speed=speed, loop=False,
             zoom=list(zoom), cx=cx, cy=cy, crop=crop or [0.015, 0.02, 0.985, 0.98], **VIEW)
    sl = dict(kind="slate", style="exhibit", x=1444, y=46, w=388, h=196, no=no, title=title, sub=sub, no_size=30, title_size=24,
              sub_size=19, cps=75, t0=-9.0 if cont else 0.05, font="${SCRATCH}/fonts/IBMPlexMono-Medium.ttf")
    if stamp:
        sl.update(stamp=stamp, stamp_at=0.9 if not cont else -1, stamp_size=24, stamp_x=0.70, stamp_y=0.17, stamp_rot=7)
    add(sid, t0, t1, [{"kind": "solid", "color": [0, 0, 0]}, v, sl], "ARCHIVE", note, credits=[vid])


def nasa(sid, t0, t1, key, a, label, speed=1.0, zoom=(1.0, 1.05), grade=None):
    src, credit, tag = NASA[key]
    dur = (t1 - t0) * speed
    out = f"{A}/clips/{sid}_nasa_{key}.mp4"
    cut(src, a, dur, out, w=1920)
    usage.append(("nasa:" + key, round(a, 2), round(a + dur, 2), sid))
    L = [{"kind": "video", "src": "${SCRATCH}/arch/clips/" + os.path.basename(out), "in_s": 0.0, "speed": speed, "loop": False,
          "grade": grade or {"gain": [1.07, 1.0, 0.92], "sat": 1.25, "exposure": 0.1}},
         {"kind": "slate", "style": "strip", "text": f"{label}  ·  {tag}  ·  REAL", "x": 44, "y": 40, "size": 22, "accent": [120, 200, 255]}]
    add(sid, t0, t1, L, "REAL_FOOTAGE", camera={"from": {"zoom": zoom[0]}, "to": {"zoom": zoom[1]}}, credits=[f"{credit} (NASA)"])


def shipcam(sid, t0, t1, key, a, label, clock, window=None, note=""):
    v = {"kind": "video", "src": SHIP[key], "in_s": a, "loop": False, "grade": {"exposure": 0.12, "sat": 1.08}}
    if window:
        v["window"] = window
    L = [v, {"kind": "slate", "style": "strip", "text": label, "clock_from": clock, "x": 44, "y": 40, "size": 22}]
    usage.append(("ship:" + key, round(a, 2), round(a + t1 - t0, 2), sid))
    add(sid, t0, t1, L, "SHIP_CAM", note, cards_at="left")


def screen(sid, t0, t1, clip, in_s, speed=1.0, inset=None, zoom=(1.0, 1.035), note="", extra_layers=None):
    """Data visual / ship screen, full frame with a slow push."""
    if inset:
        L = [{"kind": "solid", "color": [0.02, 0.03, 0.035]},
             {"kind": "screen", "src": DV + clip, "in_s": in_s, "speed": speed, "res": [1920, 1080], "spill": 0.0,
              "treat": {"scanlines": 0.04, "bloom": 0.10, "glass_black": 0.02}, "quad": [[0, 0], [1, 0], [1, 1], [0, 1]], "inset": inset}]
    else:
        L = [{"kind": "video", "src": DV + clip, "in_s": in_s, "speed": speed, "loop": False}]
    L += extra_layers or []
    add(sid, t0, t1, L, "DATA_VISUAL", note, camera={"from": {"zoom": zoom[0]}, "to": {"zoom": zoom[1]}})


MOONWIN = {"key": "black", "thresh": 0.05, "region": [0.3, 0.0, 1.0, 0.55], "feather_px": 1.4, "grow_px": 1, "glass_keep": 0.9,
           "track_px": 30, "smooth": 0.35,
           "plate": {"src": "${SCRATCH}/mv/plates/nasa_a2.mp4", "x": 0.64, "y": 0.22, "scale": 0.8, "depth": 0.3, "in_s": 10.6,
                     "speed": 0.5, "blur": 0.6, "drift": {"dx": -0.01}, "level": {"black": 0.04, "gamma": 1.0, "gain": 1.2, "tint": [1.06, 1.0, 0.92]}}}
TEMI_LIVE = {"src": "${REPO}/assets/characters/temi/master.jpg", "matte": DV + "04_bank_call_live_matte.png",
             "crop": [0.14, 0.0, 0.86, 0.95], "cx": 0.5, "cy": 0.42, "zoom_per_s": 0.012}

# ================================================================ COLD OPEN
CO = 49265  # 13:41:05 ship clock
shipcam("C01", 0.0, 5.75, "lens", 0.0, "SHIP CAM 4  ·  THE UNSCHEDULED  ·  BRIDGE", CO)
shots[-1]["layers"].append({"kind": "slate", "style": "exhibit", "x": 1180, "y": 300, "w": 600, "h": 236, "no": "CASE FILE 1,204",
                            "title": "THE PARCEL NOBODY ORDERED", "sub": "Reconstructed by PIP from ship cameras, space feeds and Earth archives (some misfiled).",
                            "no_size": 30, "title_size": 25, "sub_size": 18, "cps": 40, "t0": 0.4, "stamp": "OPEN", "stamp_at": 3.2,
                            "font": "${SCRATCH}/fonts/IBMPlexMono-Medium.ttf"})
shipcam("C02", 5.75, 7.45, "sandwich", 4.1, "SHIP CAM 1  ·  BRIDGE  ·  CAPTAIN'S SEAT", CO + 5.75, window=MOONWIN)
screen("C03", 7.45, 10.35, "03_engine_readouts_to_zero.mp4", 1.0, speed=1.6)
screen("C04", 10.35, 11.55, "03_coffee_light_goes_out.mp4", 2.4)
archive("C05", 11.55, 15.2, "Designfo1956", 241.6, "THE COFFEE MACHINE", "EARTH, 1956 · FINANCED SEPARATELY", stamp="REPOSSESSED")
screen("C06", 15.2, 19.0, "04_bank_call_sequence.mp4", 3.6, inset=TEMI_LIVE)
archive("C07", 19.0, ls("0-09"), "Operator1949", 48.0, "RECOVERIES DEPARTMENT", "EARTH, 1949 · LAGOS OFFICE NOT PICTURED")
shipcam("C08", ls("0-09"), 26.25, "pilot", 0.6, "SHIP CAM 2  ·  BRIDGE  ·  REAR", CO + 23.4, window=dict(MOONWIN, region=[0.45, 0.0, 1.0, 0.42],
        thresh=0.035, plate=dict(MOONWIN["plate"], x=0.74, y=0.18, scale=0.6)))
screen("C09", 26.25, ls("0-12") - 0.05, "04_bank_call_frozen.mp4", 1.0, inset=dict(TEMI_LIVE, zoom_per_s=0.0, pixelate=16))
screen("C10", ls("0-12") - 0.05, le("0-12") + 0.05, "04_bank_call_live.mp4", 0.3, inset=TEMI_LIVE)
archive("C11", le("0-12") + 0.05, ls("0-14"), "Operator1949", 99.0, "THE SAME CALL, AGAIN", "EARTH, 1949 · 1.3 SECONDS AGO")
archive("C12", ls("0-14"), le("0-15") + 0.1, "loc-00694408", 120.0, "THE PAST", "EARTH, 1906 · STILL BEING ARGUED WITH", stamp="DISPUTED")
shipcam("C13", le("0-15") + 0.1, ls("0-16"), "lens", 5.2, "SHIP CAM 4  ·  BRIDGE  ·  PIP UNIT", CO + 36.3)
archive("C14", ls("0-16"), ls("0-16") + 3.3, "loc-00564539", 20.0, "ONE PARCEL, SEALED, PREPAID", "EARTH, 1903 · POSTED TO US DIRECTLY")
nasa("C15", ls("0-16") + 3.3, ls("0-17"), "viper", 136.5, "FEED 9  ·  SHACKLETON CRATER, LUNAR SOUTH POLE", zoom=(1.0, 1.06))
archive("C16", ls("0-17"), le("0-18") + 0.1, "Usingthe1947", 494.5, "EXACTLY WHAT WE OWE", "EARTH, 1947 · TO THE CENT", stamp="VERIFIED")
tk = [le("0-18") + 0.1, ls("0-20"), ls("0-21"), le("0-21") - 0.05]
archive("C17a", tk[0], tk[1], "big_board", 89.5, '"TAKE IT" (x5)', "EARTH, 1957 · THE CAPTAIN'S METHOD", stamp="NOTED", zoom=(1.0, 1.12))
archive("C17b", tk[1], tk[2], "big_board", 245.3, '"TAKE IT" (x5)', "EARTH, 1957 · THE CAPTAIN'S METHOD", stamp="NOTED", cont=True, zoom=(1.05, 1.15))
archive("C17c", tk[2], tk[3], "big_board", 341.0, '"TAKE IT" (x5)', "EARTH, 1957 · THE CAPTAIN'S METHOD", stamp="NOTED", cont=True, zoom=(1.08, 1.2))
STAMP_IN = 0.9
shipcam("C18", tk[3], tk[3] + 2.15, "stamp", STAMP_IN, "SHIP CAM 3  ·  BRIDGE  ·  STAMP ARM", CO + tk[3])
screen("C19", tk[3] + 2.15, le("0-22") + 0.15, "02_pip_report_1204.mp4", 3.0)
shipcam("C20", le("0-22") + 0.15, ls("0-23") - 0.02, "grin", 2.2, "SHIP CAM 1  ·  BRIDGE  ·  CAPTAIN'S SEAT", CO + 55.0)
screen("C21", ls("0-23") - 0.02, ls("0-25"), "05_cargo_screen.mp4", 1.0,
       inset={"src": "${REPO}/samples/look-codex/jax-6-cargo-parcel.jpg", "matte": DV + "05_cargo_screen_matte.png", "crop": [0.58, 0.36, 0.84, 0.6],
              "cx": 0.5, "cy": 0.5, "zoom_per_s": 0.03, "mono": [0.62, 0.9, 0.7], "gain": 0.85, "pixelate": 2})
archive("C22", ls("0-25"), 64.0, "BanksAndCred", 215.4, "ARITHMETIC", "EARTH, 1948 · SEE ALSO: LUCK", stamp="FILED")
add("TITLE", 64.0, 74.0, [{"kind": "video", "src": DV + "13a_title_main_optionA_cinzel.mp4", "in_s": 0.0, "loop": False}], "TITLE",
    extra={"overlays": {"cards": False, "subtitles": False}})

# ================================================================ SCENE 1  CARGO HOLD
archive("S1a", 74.0, le("1-02") + 0.1, "MasterHa1936", 149.6, "A SPANNER, ELEVEN", "EARTH, 1936 · SUPPLIED: NINE")
archive("S1b", le("1-02") + 0.1, le("1-03") + 0.1, "Exercise1949", 213.0, "A NINE THAT BELIEVES IN ITSELF", "EARTH, 1949 · CONFIDENCE, UNEARNED")
archive("S1c", le("1-03") + 0.1, le("1-04") + 0.2, "MasterHa1936", 123.0, "VOLUNTEERING", "EARTH, 1936 · UNPAID, EIGHT MONTHS", stamp="OVERDUE")
archive("S1d", le("1-04") + 0.2, le("1-07") + 0.15, "Usingthe1947", 516.2, "OFF THE TOP", "EARTH, 1947 · BEFORE FUEL, FOOD, CAPTAIN", stamp="PROMISED")
shipcam("S1e", le("1-07") + 0.15, ls("1-09"), "lens", 2.0, "SHIP CAM 6  ·  CARGO HOLD  ·  PIP SPEAKER", 49450 + 14.0)
archive("S1f", ls("1-09"), ls("1-09") + 3.0, "IWanttoB1941", 425.6, "THE CAPTAIN'S PROMISES", "EARTH, 1941 · MARCH, MAY, TODAY", stamp="ON RECORD")
archive("S1g", ls("1-09") + 3.0, le("1-09") + 0.2, "big_board", 82.5, "THE CAPTAIN'S PROMISES", "MAY'S · LOUDER", cont=True, zoom=(1.0, 1.1))
screen("S1h", le("1-09") + 0.2, ls("1-11"), "05_cargo_screen.mp4", 4.0,
       inset={"src": "${REPO}/samples/look-codex/jax-6-cargo-parcel.jpg", "matte": DV + "05_cargo_screen_matte.png", "crop": [0.58, 0.36, 0.84, 0.6],
              "cx": 0.5, "cy": 0.5, "zoom_per_s": 0.05, "mono": [0.62, 0.9, 0.7], "gain": 0.85, "pixelate": 2})
archive("S1i", ls("1-11"), ls("1-11") + 3.0, "WorldThr1957", 108.6, "STAMPS, TWENTY YEARS OF", "EARTH, 1957 · ALL AT 21 °C", zoom=(1.0, 1.12))
archive("S1j", ls("1-11") + 3.0, le("1-11") + 0.1, "WorldThr1957", 117.6, "STAMPS, TWENTY YEARS OF", "EARTH, 1957 · ALL AT 21 °C", cont=True, zoom=(1.04, 1.14))
archive("S1k", le("1-11") + 0.1, le("1-12") - 1.1, "Chickeno1948", 567.6, "CONTENTS: UNDECLARED", "EARTH, 1948 · ALIVE, OR WELL WRAPPED")
archive("S1l", le("1-12") - 1.1, 106.9, "Chickeno1948", 518.0, "CONTENTS: UNDECLARED", "EARTH, 1948 · ALIVE, OR WELL WRAPPED", cont=True, stamp="WARM")

# ================================================================ SCENE 2  BRIDGE — ON APPROACH
nasa("S2a", 106.9, 113.0, "viper", 4.6, "FEED 9  ·  LUNAR SOUTH POLE  ·  APPROACH", zoom=(1.0, 1.05))
shipcam("S2b", 113.0, 116.2, "pilot", 3.6, "SHIP CAM 2  ·  BRIDGE  ·  REAR", 49742 + 6.0, window=dict(MOONWIN, region=[0.6, 0.0, 1.0, 0.4],
        thresh=0.035, plate=dict(MOONWIN["plate"], x=0.80, y=0.16, scale=0.55, in_s=14.0)))
screen("S2c", 116.2, 117.9, "01_atlas_continuous.mp4", 5.2)
screen("S2d", 117.9, 119.6, "01_atlas_continuous.mp4", 8.8)
screen("S2e", 119.6, ls("2-07"), "01_atlas_continuous.mp4", 15.4)
archive("S2f", ls("2-07"), le("2-08") + 0.1, "CaughtMa1940", 33.6, "AN ADDRESS", "EARTH, 1940 · 'THE' DOES NOT QUALIFY")
nasa("S2g", le("2-08") + 0.1, le("2-09") + 0.2, "shadow", 42.3, "FEED 9  ·  SHACKLETON CRATER FLOOR", zoom=(1.02, 1.08))
screen("S2h", le("2-09") + 0.2, ls("2-12"), "01_atlas_continuous.mp4", 20.5, speed=1.15)
archive("S2i", ls("2-12"), ls("2-13"), "OnGuard1956", 382.3, "RIM PORT CONTROL", "EARTH, 1956 · MISFILED UNDER 'MOON'")
archive("S2j", ls("2-13"), ls("2-14") + 1.4, "PlaneTal1965", 448.6, "BAY NINE", "EARTH, 1965 · ALL GOODS HELD", stamp="DO NOT OPEN")
nasa("S2k", ls("2-14") + 1.4, le("2-14") + 0.3, "moonview", 46.0, "FEED 3  ·  THE CLIENT'S LAST KNOWN ADDRESS", zoom=(1.0, 1.04))
screen("S2l", le("2-14") + 0.3, le("2-15") + 0.15, "02_pip_report_1205.mp4", 1.6)
archive("S2m", le("2-15") + 0.15, 155.9, "IWanttoB1941", 417.6, "REPORTS, UNREAD", "EARTH, 1941 · NOT THE POINT OF THEM", stamp="FILED")

# ================================================================ SCENE 3  CUSTOMS HALL — THE DESK
nasa("S3a", 155.9, 158.3, "scarp", 13.0, "FEED 11  ·  APPROACH, RIM PORT", zoom=(1.0, 1.06))
archive("S3b", 158.3, ls("3-04"), "PlaneTal1965", 230.6, "RIM PORT CUSTOMS HALL", "CAPACITY 2,000 · STAFF 3 · QUEUE 1")
archive("S3c", ls("3-04"), ls("3-04") + 3.2, "loc-00564567", 22.0, "PARCEL, ONE", "SEALED · DISTRICT WITHDRAWN 14:02")
archive("S3d", ls("3-04") + 3.2, ls("3-05"), "loc-00564573", 30.0, "PARCEL, ONE", "SEIZED 14:19", cont=True)
archive("S3e", ls("3-05"), le("3-07") + 0.1, "DateWith1950", 482.5, "THE AUNT", "EARTH, 1950 · NOT PICTURED · NOT ON FORM", stamp="NONE")
archive("S3f", le("3-07") + 0.1, ls("3-09") + 1.8, "Exercise1949", 174.5, "FLEXIBILITY", "EARTH, 1949 · OFFERED TO CUSTOMS")
archive("S3g", ls("3-09") + 1.8, ls("3-10"), "Exercise1949", 218.0, "FLEXIBILITY", "EARTH, 1949 · OFFERED TO CUSTOMS", cont=True, stamp="DECLINED")
archive("S3h", ls("3-10"), ls("3-11"), "CaughtMa1940", 236.3, "WHERE THINGS ACTUALLY ARE", "EARTH, 1940 · DR SEN'S SPECIALITY")
archive("S3i", ls("3-11"), ls("3-13"), "Suggesti1945", 103.6, "SECTION TWELVE", "OF NINE · VERY EXCLUSIVE")
archive("S3j", ls("3-13"), ls("3-14"), "IWanttoB1941", 483.0, "SECTION TWELVE", "OF NINE · VERY EXCLUSIVE", cont=True, stamp="NOT FOUND")
archive("S3k", ls("3-14"), ls("3-15") - 0.05, "MasterHa1936", 159.6, "SOMETHING TRUE", "REQUESTED BY CUSTOMS · NONE SUPPLIED")
archive("S3l", ls("3-15") - 0.05, ls("3-16"), "MasterHa1936", 134.3, "VERY GOOD AT HIS JOB", "EARTH, 1936 · SELF-ASSESSED")
screen("S3m", ls("3-16"), ls("3-17") - 0.1, "09a_hall_clock_analog_1745.mp4", 0.5)
archive("S3n", ls("3-17") - 0.1, le("3-17") + 0.25, "Designfo1956", 411.0, "IN BURSTS", "EARTH, 1956 · SEE: CAPTAIN, JOB")
screen("S3o", le("3-17") + 0.25, ls("3-21"), "06a_customs_licence.mp4", 1.0, speed=1.1)
archive("S3p", ls("3-21"), le("3-22") + 0.05, "IWanttoB1941", 666.5, "A PROBLEM", "FOR CUSTOMS: NOT ONE")
archive("S3q", le("3-22") + 0.05, ls("3-24"), "loc-00564539", 45.0, "PARCEL, ONE", "RIM PORT · 14:19", stamp="SEIZED")
archive("S3r", ls("3-24"), le("3-25") + 0.2, "HealthYo1953", 309.6, "GENTLEMAN, TRICORN, ON SCALE", "EARTH, 1953 · FORMERLY TALLER (CLAIMED)", zoom=(1.0, 1.15))

# ================================================================ SCENE 4  MIRA'S DESK
screen("S4a", le("3-25") + 0.2, ls("4-02"), "06b_customs_deletion_record.mp4", 2.6)
archive("S4b", ls("4-02"), ls("4-04"), "AnotherCupOf", 654.0, "THE NOTEBOOK", "ENTRY 41 · OWNER: —")
archive("S4c", ls("4-04"), ls("4-05"), "CaughtMa1940", 131.6, "THE MAP", "EARTH, 1940 · WRONG (PER DR SEN)")
archive("S4d", ls("4-05"), ls("4-07"), "CaughtMa1940", 66.0, "OFFICIAL", "A DEPARTMENT, NOT AN OPPOSITE")
screen("S4e", ls("4-07"), ls("4-08") - 0.1, "08a_board_1094_static.mp4", 1.0)
archive("S4f", ls("4-08") - 0.1, 240.8, "AnotherCupOf", 660.0, "THE NOTEBOOK", "STILL OPEN", cont=False, stamp="QUIET (PROMISED)")

# ================================================================ SCENE 5  A BENCH
archive("S5a", 240.8, ls("5-02"), "Gossip1953", 322.0, "THE BOX", "EARTH, 1953 · ENGINEER'S POSITION: AGAINST", speed=0.93)
archive("S5b", ls("5-02"), le("5-03") + 0.2, "Gossip1953", 588.0, "IT'S THE BOX", "EARTH, 1953 · REPEATED FOR THE RECORD")
shipcam("S5c", le("5-03") + 0.2, ls("5-05"), "lens", 4.2, "WRIST UNIT  ·  CUSTOMS HALL  ·  AUDIO ONLY", 52270)
archive("S5d", ls("5-05"), ls("5-07"), "AnotherCupOf", 27.5, "MAN, AVERAGE", "EARTH, 1948 · WITH TEACUP (APPROX.)")
archive("S5e", ls("5-07"), ls("5-08") + 1.2, "BanksAndCred", 377.6, "THE LIEN: 182,000", "ON THE UNSCHEDULED · NOTED BY STRANGER")
archive("S5f", ls("5-08") + 1.2, ls("5-09"), "Suggesti1945", 308.3, "LOYALTY, EIGHT MONTHS", "EARTH, 1945 · UNPAID", speed=0.9)
archive("S5g", ls("5-09"), ls("5-10") + 3.4, "Usingthe1947", 556.4, "A BUYER", "EARTH, 1947 · NAME WITHHELD")
archive("S5h", ls("5-10") + 3.4, ls("5-11"), "loc-00564550", 40.0, "WHAT THE REGISTER FORGOT", "EARTH, 1903 · STILL WORKS")
add("S5i", ls("5-11"), ls("5-13"), [{"kind": "still", "src": "${SCRATCH}/arch/card.png"}], "INSERT", "calling card (rendered in code)",
    camera={"from": {"zoom": 1.0, "cx": 0.5, "cy": 0.5}, "to": {"zoom": 1.16, "cx": 0.47, "cy": 0.52}})
archive("S5j", ls("5-13"), ls("5-15"), "big_board", 49.4, "MAN, AVERAGE (ONE OF THESE)", "EARTH, 1957 · LOGGED", zoom=(1.0, 1.1))
archive("S5k", ls("5-15"), 285.8, "big_board", 74.6, "MAN, AVERAGE (ONE OF THESE)", "EARTH, 1957 · LOGGED", cont=True, stamp="AVERAGE", zoom=(1.06, 1.18))

# ================================================================ SOURCES SLATE
json.dump(dict(usage=usage, srclog=SRCLOG), open(f"{A}/usage.json", "w"), indent=0)
vault_meta = {}
for vid in sorted({u[0] for u in usage if not u[0].startswith(("nasa:", "ship:"))}):
    m = json.load(open(f"{S}/vault/meta/{vid}.json"))
    vault_meta[vid] = m
src_lines = []
for vid, m in vault_meta.items():
    yr = str(m.get("year") or "")[:4]
    who = (m.get("creator") or "")
    if isinstance(who, list): who = who[0]
    lib = "Library of Congress" if vid.startswith("loc-") else "Prelinger Archives"
    src_lines.append(f"{m['title'][:56]}" + (f" ({yr})" if yr.isdigit() else "") + f" · {lib}")
for k in sorted({u[0][5:] for u in usage if u[0].startswith("nasa:")}):
    src_lines.append(f"{NASA[k][1][:52]} · NASA")
add("SRC", 285.8, 291.8, [{"kind": "solid", "color": [0, 0, 0]},
    {"kind": "slate", "style": "sheet", "title": "SOURCES OF THIS FILE", "subtitle": "Archive films: public domain. Space footage: NASA (no endorsement implied).",
     "lines": src_lines, "cols": 2, "size": 21, "font": "${SCRATCH}/fonts/IBMPlexMono-Medium.ttf", "font_body": "${SCRATCH}/fonts/IBMPlexMono-Regular.ttf"}],
    "TITLE", extra={"overlays": {"cards": False, "subtitles": False}, "out": {"type": "fade", "dur": 0.6}})

# ---------------------------------------------------------------- audio cues
def fx(name, at, g_index, extra=0.0, **kw):
    d = dict(id=name, src="${SCRATCH}/e01/sfx/" + name + ".wav", start_s=round(at, 3), gain_db=round(g_index - 7 + extra, 1))
    d.update(kw); return d

sfx = [
    fx("ship_bridge_roomtone_loop", 0.0, -21.0, loop_s=64.0, fade_in=1.5, fade_out=0.05),
    fx("pip_lens_glow_on", 0.5, -8.0, duck=False),
    fx("ship_systems_powerdown_sequence", ls("0-04") - 0.3, -4.0, extra=-3),
    fx("coffee_machine_last_gurgle", 10.4, -4.0, extra=-3),
    fx("bank_chime", 15.0, -3.0, duck=False),
    fx("ship_relay_click_a", 24.9, -6.0),
    fx("shop_door_bell", le("0-15") + 0.2, -3.0, duck=False),
    fx("pip_stamp_thunk_b", tk[3] + 0.62, -2.0, duck=False),
    fx("ui_report_filed_blip", tk[3] + 2.3, -6.0, duck=False),
    fx("earth_call_dead_air_1p3s", le("0-22"), -34.2, duck=False),
    fx("ship_engine_cough_restart", le("0-22") + 0.9, -4.0, extra=-2),
    fx("smash_cut_main_title_hit", 64.0, 0.0, extra=-2, duck=False),
    fx("ship_cargohold_tone_loop", 74.0, -17.8, loop_s=33.0, fade_in=0.6, fade_out=0.6),
    fx("ship_bridge_roomtone_loop", 106.9, -21.0, loop_s=49.0, fade_in=0.8, fade_out=0.6),
    fx("ui_letter_blink_out", 116.8, -8.0), fx("ui_letter_blink_out", 118.2, -8.0), fx("ui_letter_blink_out", 119.9, -8.0),
    fx("ui_streetlamps_going_out_sequence", le("2-09") + 0.5, -5.0),
    fx("radio_click_on", ls("2-12") - 0.15, -6.0, duck=False), fx("radio_click_off", le("2-14") + 0.05, -6.0, duck=False),
    fx("radio_open_channel_hiss_loop", ls("2-12") - 0.1, -23.3, loop_s=le("2-14") - ls("2-12") + 0.2, fade_in=0.05, fade_out=0.1, duck=False),
    fx("ui_report_filed_blip", le("2-14") + 1.1, -6.0, duck=False),
    fx("customs_hall_roomtone_loop", 155.9, -19.6, loop_s=129.9, fade_in=1.0, fade_out=1.0),
    fx("customs_desk_stamp_heavy_a", le("3-22") + 0.35, -2.0, duck=False),
    fx("cargo_scale_settle_beeps", ls("3-25") - 0.6, -6.0, extra=-4),
    fx("flipboard_flap_single_a", ls("4-07") + 0.4, -6.0),
    fx("wristcomm_buzz", 240.9, -4.0, duck=False),
    fx("wristcomm_click", le("5-03") + 0.1, -6.0, duck=False),
    fx("paper_card_slide_and_tap", ls("5-11") + 0.2, -8.0),
]
MUS = "${SCRATCH}/e01/music/"
music = [
    dict(id="M01", src=MUS + "E01-M01-cold-open-under-dialogue.wav", start_s=0.3, gain_db=-6, duck=True, fade_in=2.0, fade_out=1.2, trim_s=63.5),
    dict(id="title-sting", src="${REPO}/samples/music/v2/A1-title-sting-10s.mp3", start_s=64.0, gain_db=-3, duck=False, fade_out=0.6),
    dict(id="C10", src=MUS + "E01-C10-parcel-bell-celesta.wav", start_s=ls("1-10") - 0.35, gain_db=-7, duck=False),
    dict(id="C7", src=MUS + "E01-C7-lucia-motif-under-dialogue.wav", start_s=ls("1-10") + 0.3, gain_db=-6, duck=True, fade_out=1.0, trim_s=106.9 - ls("1-10") - 0.2),
    dict(id="M02", src=MUS + "E01-M02-approach-under-dialogue.wav", start_s=106.9, gain_db=-5, duck=True, fade_in=0.8, fade_out=1.6, trim_s=ls("2-12") - 106.9),
    dict(id="button-2", src=MUS + "E01-C1-button-a.wav", start_s=le("2-17") + 0.15, gain_db=-7, duck=False, fade_out=0.4),
    dict(id="M04a-tiny", src=MUS + "E01-M04a-baron-theme-grand-30s-under-dialogue.wav", start_s=ls("3-25") - 0.4, gain_db=-14, duck=False, fade_out=0.8, trim_s=3.4),
    dict(id="M2-mira", src="${REPO}/samples/music/v2/M2-mira-motif-v2.mp3", start_s=ls("4-08") - 0.4, gain_db=-12, duck=True, fade_out=1.0, trim_s=240.8 - ls("4-08") + 0.6),
    dict(id="M03a", src=MUS + "E01-M03a-chichikov-motif-20s-under-dialogue.wav", start_s=ls("5-05") - 0.3, gain_db=-7, duck=True, fade_in=1.0, fade_out=1.5, trim_s=20.0),
    dict(id="button-end", src=MUS + "E01-C1-button-b.wav", start_s=le("5-16") + 0.15, gain_db=-6, duck=False, fade_out=0.5),
]

SPK = {
    "PIP": dict(name="PIP", role="SHIP'S COMPUTER · POSTAL AUDIT", portrait="${REPO}/assets/props/pip/master.jpg", face=[0.44, 0.04, 0.62, 0.36], lens=True, lens_x=0.48, lens_y=0.62),
    "JAX": dict(name="JAX VALE", role="CAPTAIN · THE UNSCHEDULED", portrait="${REPO}/assets/characters/jax/master.jpg", face=[0.345, 0.03, 0.598, 0.48]),
    "TEMI": dict(name="TEMI ADEYEMI", role="RECOVERIES · BRINDLELARK, LAGOS", portrait="${REPO}/assets/characters/temi/master.jpg", face=[0.37, 0.0, 0.62, 0.45]),
    "LUCIA": dict(name="LUCÍA ORTEGA", role="ENGINEER · UNPAID, 8 MONTHS", portrait="${REPO}/assets/characters/lucia/master.jpg", face=[0.4, 0.0, 0.65, 0.45]),
    "MAMANI": dict(name="OFFICER MAMANI", role="RIM PORT CONTROL · RADIO", portrait="${REPO}/assets/characters/mamani/master.jpg", face=[0.29, 0.02, 0.545, 0.47]),
    "MIRA": dict(name="DR MIRA SEN", role="CUSTOMS · RIM PORT", portrait="${REPO}/assets/characters/mira/master.jpg", face=[0.29, 0.02, 0.53, 0.44]),
    "BARON": dict(name="UNIDENTIFIED", role="TRICORN HAT · ON CARGO SCALE", portrait="${REPO}/assets/characters/baron/master.jpg", blur=2.5, face=[0.28, 0.06, 0.56, 0.56]),
    "NOAKES": dict(name="SUPT. NOAKES", role="RIM PORT CUSTOMS", portrait="${REPO}/assets/characters/noakes/master.jpg", face=[0.4, 0.04, 0.65, 0.48]),
    "CHICHIKOV": dict(name="MAN, AVERAGE", role="AS LOGGED · FACE NOT RETAINED", portrait="${REPO}/assets/characters/chichikov/master.jpg", blur=5, face=[0.26, 0.02, 0.5, 0.44]),
}
total = round(sum(s["duration_s"] for s in shots), 3)
for s in shots:
    s.pop("_t0", None)
SL = {
    "version": 1, "name": "E01-archive-sample", "episode": "E01", "unit": "archive-sample",
    "note": "PIP's file on the case: first ~4:52 of Episode 1 (cold open, title, scenes 1-5) in the archive format. Built by arch/build.py.",
    "vars": {"SCRATCH": S},
    "output": {"width": 1920, "height": 1080, "fps": 24, "crf": 18, "preset": "medium"},
    "finish": {"grain": 0.018, "halation": 0.35, "weave_px": 0.3, "vignette": 0.30, "saturation": 1.05, "split_tone": 0.6, "pre_gain": 1.18},
    "dialogue": {"lines": lines, "gain_db": 0.0},
    "music": music, "sfx": sfx,
    "duck": {"music_db": -9, "sfx_db": -5},
    "loudness": {"integrated": -16.0, "true_peak_ceiling": -2.0},
    "overlays": {
        "comm_cards": {"w": 440, "h": 124, "speakers": SPK, "pre_s": 0.2, "hold_s": 1.2, "merge_s": 3.0,
                       "font_name": "${SCRATCH}/fonts/BarlowCondensed-SemiBold.ttf", "font_role": "${SCRATCH}/fonts/IBMPlexMono-Medium.ttf"},
        "subtitles": {"size": 31, "max_w": 860, "cx": 940, "bottom": 1062, "box": 0.55}},
    "credits": [],
    "shots": shots,
}
json.dump(SL, open(f"{REPO}/episodes/E01/archive-sample-shotlist.json", "w"), indent=1, ensure_ascii=False)
print(f"shots {len(shots)}  total {total:.2f}s  lines {len(lines)}  archive uses {sum(1 for u in usage if not ':' in u[0])}")
