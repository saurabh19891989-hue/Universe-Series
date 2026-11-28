#!/usr/bin/env python3
"""Builds episodes/E01/animation-test-shotlist.json (Episode 1 cold open, animated test, 70 s).

Timeline and dialogue placement follow episodes/E01/archive-sample-shotlist.json (cold open = 0..64 s).
Shots with an "anim" block are rendered by production/tools/anim/anim.py into ${SCRATCH}/anim/clips/,
then the edit engine (production/tools/edit/render.py) cuts, mixes and subtitles everything.
"""
import json, os, copy

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
SCR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
arch = json.load(open(f"{REPO}/episodes/E01/archive-sample-shotlist.json"))
ART = "${SCRATCH}/anim/art"
PL = "${SCRATCH}/e01/plates"
MOON = {"kind": "video", "src": f"{PL}/lunarflyby_1min_2160p30.mp4", "in_s": 22.0, "depth": 0.25}
EARTH = {"kind": "video", "src": f"{PL}/jsc2026m000089_Artemis_II_Moments_Around_the_Moon_1080p_AVAIL.mp4",
         "in_s": 30.6, "crop": [0.34, 0.36, 0.80, 1.0], "depth": 0.25}
SCARP = f"{PL}/GSFC_20190513_m4714_Lee_Lincoln_Scarp_Moon_Flyover.mp4"

rigs = {
    "jax_front": {"src": f"{ART}/A_jax_front.jpg", "key": {"type": "green"},
                  "eyes": [[642, 227, 19, 7], [742, 225, 18, 7]], "mouth": [697, 328], "mouth_w": 28, "chin": 400,
                  "face": [560, 170, 840, 470],
                  "parts": [{"name": "head", "region": [700, 230, 170, 200], "roi": [480, 10, 920, 520], "pivot": [700, 470]}]},
    "jax_point": {"src": f"{ART}/A_jax_point.jpg", "key": {"type": "green"},
                  "eyes": [[611, 230, 21, 8], [720, 231, 21, 8]], "mouth": [673, 335], "mouth_w": 30, "chin": 419,
                  "face": [540, 170, 820, 490],
                  "parts": [{"name": "head", "region": [668, 240, 150, 200], "roi": [450, 10, 880, 540], "pivot": [668, 480]}]},
    "jax_plead": {"src": f"{ART}/A_jax_plead.jpg", "key": {"type": "green"},
                  "eyes": [[630, 227, 24, 8], [749, 226, 24, 8]], "mouth": [691, 352], "mouth_w": 34, "chin": 440,
                  "face": [560, 170, 840, 510],
                  "parts": [{"name": "head", "region": [690, 250, 165, 210], "roi": [470, 10, 920, 560], "pivot": [690, 500]}]},
    "jax_side": {"src": f"{ART}/A_jax_side.jpg", "key": {"type": "green"},
                 "eyes": [[573, 240, 22, 8], [685, 210, 16, 7]], "eye_ang": -15, "mouth": [660, 343], "mouth_ang": -16,
                 "mouth_w": 30, "chin": 430, "face": [530, 160, 790, 500],
                 "parts": [{"name": "head", "region": [620, 240, 170, 200], "roi": [400, 10, 830, 520], "pivot": [600, 470]}]},
    "temi": {"src": f"{ART}/A_temi.jpg", "eyes": [[637, 246, 28, 11], [779, 275, 26, 10]], "eye_ang": 11.5,
             "mouth": [687, 392], "mouth_ang": 5, "mouth_w": 44, "chin": 480, "face": [560, 190, 830, 560]},
    "pip": {"src": f"{ART}/A_pip.jpg", "key": {"type": "green"}, "lens": [740, 167, 48],
            "parts": [{"name": "head", "region": [690, 170, 150, 125], "roi": [500, 0, 900, 340], "pivot": [600, 125],
                       "sway": 2.0, "talk": 3.5, "nod": 4.0},
                      {"name": "arm", "region": [905, 390, 125, 125], "roi": [770, 230, 1040, 560], "pivot": [800, 390],
                       "sway": 0.0, "talk": 0.0, "nod": 0.0}]},
    "ship": {"src": f"{ART}/A_ship.jpg", "key": {"type": "green"}, "engines": [[160, 203, 45], [163, 503, 45]]},
    "jax_real": {"src": "${REPO}/assets/characters/jax/ref-front.jpg",
                 "key": {"type": "mask", "src": f"{ART}/B_jax_real_mask.png"}, "style": "photo",
                 "eyes": [[797, 250, 20, 8], [893, 248, 20, 8]], "mouth": [852, 351], "mouth_w": 34, "chin": 420,
                 "face": [740, 190, 960, 490],
                 "parts": [{"name": "head", "region": [845, 250, 160, 200], "roi": [640, 0, 1060, 520], "pivot": [845, 470]}]},
}
for k in ("jax_front", "jax_point", "jax_plead", "jax_side"):
    rigs[k]["style"] = "ink"

def bridge_bg(crop=(0.08, 0.0, 0.92, 0.70), blur=2.2, src="A_bridge_wide.jpg", bright=None):
    L = {"kind": "set", "src": f"{ART}/{src}", "window": {"region": [0.1, 0.03, 0.92, 0.5]}, "crop": list(crop),
         "blur": blur, "depth": 0.6}
    if bright:
        L["bright"] = bright
    return L

def console_bg(blur=1.6):
    return {"kind": "set", "src": f"{ART}/A_console.jpg", "window": {"region": [0.15, 0.0, 1.0, 0.36]},
            "crop": [0.0, 0.0, 1.0, 1.0], "blur": blur, "depth": 0.6}

def plate(base, **kw):
    p = copy.deepcopy(base); p.update(kw); return p

def jax(poses, x=0.5, h=1.12, y=1.10, **kw):
    L = {"kind": "puppet", "name": "jax", "speaker": "JAX", "poses": poses, "x": x, "y": y, "h": h, "depth": 1.25,
         "shadow": 0.25}
    L.update(kw); return L

def pip(x=0.55, h=1.0, y=1.02, **kw):
    L = {"kind": "puppet", "name": "pip", "speaker": "PIP", "rig": "pip", "x": x, "y": y, "h": h, "depth": 1.2,
         "shadow": 0.3}
    L.update(kw); return L

def ship(x_keys, y=0.62, h=0.5, glow=None, rot=None):
    return {"kind": "puppet", "name": "ship", "rig": "ship", "x": 0.5, "y": y, "h": h, "depth": 1.4,
            "x_keys": x_keys, "rot_keys": rot or [[0, -2.0], [4, 2.0]], "glow_keys": glow or [], "bob": 6, "breath": 0.0,
            "sway": 0.8}

S = []  # (id, dur, anim | engine layers, note, lines)
def A(i, dur, layers, note, lines=(), camera=None, **extra):
    a = {"layers": layers, "camera": camera or {"z0": 1.0, "z1": 1.04, "drift": 6}}
    a.update(extra)
    S.append({"id": i, "duration_s": dur, "type": "ANIMATION", "note": note, "anim": a,
              "layers": [{"kind": "video", "src": f"${{SCRATCH}}/anim/clips/{i}.mp4"}],
              "audio": {"lines": list(lines)}})

def E(i, dur, layers, note, lines=(), camera=None, typ="INSERT", **extra):
    s = {"id": i, "duration_s": dur, "type": typ, "note": note, "layers": layers, "audio": {"lines": list(lines)},
         "camera": camera or {"from": {"zoom": 1.0}, "to": {"zoom": 1.04}}}
    s.update(extra); S.append(s)

# ---- timeline (cut points from the archive sample's dialogue placement)
A("A01", 4.60, [plate({"kind": "video", "src": SCARP, "in_s": 16.0, "depth": 0.3}),
                ship([[0, -0.42], [4.6, 0.30]], y=0.58, h=0.46, rot=[[0, -3], [2.5, 1.5], [4.6, -1]])],
  "REAL NASA video (LRO flyover, Lee Lincoln scarp); the ship flies across. PIP V.O.: the bank has taken the left engine.",
  ["0-01"], camera={"z0": 1.0, "z1": 1.06, "drift": 4})
A("A02", 1.15, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(), jax([[0, "jax_front"]])],
  "Jax MS, Moon in the window behind: 'Which one's the left?'", ["0-02"])
A("A03", 1.70, [plate(MOON, offset=[260, -300], overscan=1.35, in_s=27), console_bg(), pip()],
  "PIP on the console, lens glowing with his voice: 'The one that has stopped.'", ["0-03"])
E("A04", 2.00, [{"kind": "video", "src": "${SCRATCH}/e01/datavis/03_engine_readouts_to_zero.mp4", "in_s": 3.0}],
  "ANIMATED SCREEN: engine readouts drop to zero. PIP V.O.", ["0-04"])
A("A05", 2.10, [plate(MOON, in_s=30, overscan=1.0, offset=[0, -180]),
                bridge_bg(crop=(0, 0, 1, 1), blur=0, bright=[[0, 1.0], [0.5, 1.0], [0.6, 0.78], [1.1, 0.78], [1.2, 0.62], [2.1, 0.6]]),
                ],
  "Bridge wide, real Moon in the big window; the lights go down in steps.", [], camera={"z0": 1.0, "z1": 1.07, "drift": 5},
  )
S[-1]["anim"]["layers"][1]["flicker"] = 0.04
A("A06", 1.65, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(), jax([[0, "jax_front"], [0.45, "jax_point"]])],
  "Jax, indignant, finger up: 'They can't take the coffee machine.'", ["0-05"], camera={"z0": 1.02, "z1": 1.08, "drift": 6})
A("A07", 2.00, [plate(MOON, offset=[260, -300], overscan=1.35, in_s=27), console_bg(), pip(x=0.5, h=1.08, y=1.06)],
  "PIP: 'It was financed separately.'", ["0-06"])
A("A08", 3.80, [{"kind": "callscreen", "src": "${SCRATCH}/e01/datavis/04_bank_call_live.mp4", "in_s": 0.5,
                 "matte": "${SCRATCH}/e01/datavis/04_bank_call_live_matte.png", "rig": "temi", "speaker": "TEMI"}],
  "ANIMATED SCREEN: the bank call; Temi talks (lip-synced): 'Good morning! This is Temi in Recoveries...'", ["0-07"],
  camera={"z0": 1.0, "z1": 1.05, "drift": 3})
A("A09", 2.40, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(),
                jax([[0, "jax_front"]], look_keys={"x": [[0, -1.0], [0.8, -1.0], [1.0, 0.6], [1.8, 0.6], [2.0, -0.8]]})],
  "Jax listening to Temi (V.O.): eyes go to the screen and back, a slow sag.", [], camera={"z0": 1.0, "z1": 1.05, "drift": 5})
A("A10", 2.00, [{"kind": "callscreen", "src": "${SCRATCH}/e01/datavis/04_bank_call_live.mp4", "in_s": 2.5,
                 "matte": "${SCRATCH}/e01/datavis/04_bank_call_live_matte.png", "rig": "temi", "speaker": "TEMI"}],
  "Temi: '...at six tonight, lunar time. Please remain seated while-'", [], camera={"z0": 1.03, "z1": 1.08, "drift": 3})
A("A11", 2.90, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(), jax([[0, "jax_front"], [0.35, "jax_plead"]], h=1.10)],
  "Jax, all charm, palms up: 'Temi! Hi! I'm about to make a payment-'", ["0-09"])
A("A12", 0.92, [{"kind": "callscreen", "src": "${SCRATCH}/e01/datavis/04_bank_call_live.mp4", "in_s": 4.0,
                 "matte": "${SCRATCH}/e01/datavis/04_bank_call_live_matte.png", "rig": "temi", "speaker": "TEMI",
                 "freeze_at": 0.25}],
  "Temi freezes mid-word on a blocky frame: '-we disable your-'", ["0-10"], camera={"z0": 1.06, "z1": 1.06, "drift": 2},
  pixelate={"t0": 0.25, "block": 14})
A("A13", 0.93, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(), jax([[0, "jax_plead"]], h=1.10)],
  "Jax: 'A big one. Enormous-'", ["0-11"], camera={"z0": 1.04, "z1": 1.09, "drift": 6})
A("A14", 2.45, [{"kind": "callscreen", "src": "${SCRATCH}/e01/datavis/04_bank_call_live.mp4", "in_s": 0.0,
                 "matte": "${SCRATCH}/e01/datavis/04_bank_call_live_matte.png", "rig": "temi", "speaker": "TEMI"}],
  "Reset: 'Hello! You're speaking to Temi in Recoveries!'", ["0-12"], camera={"z0": 1.0, "z1": 1.04, "drift": 3})
A("A15", 1.45, [plate(MOON, offset=[380, -280], overscan=1.3, in_s=27), bridge_bg(crop=(0.2, 0.0, 1.0, 0.7)),
                jax([[0, "jax_side"]], x=0.40, h=1.12)],
  "Jax turns to PIP: 'Why does she keep doing that?'", ["0-13"])
A("A16", 3.30, [plate(EARTH, offset=[260, -300], overscan=1.0), console_bg(), pip(x=0.45, h=1.0)],
  "PIP, the real Earth in the window behind him: 'She is in Lagos. You are arguing with the past.'", ["0-14"],
  camera={"z0": 1.0, "z1": 1.06, "drift": 5})
A("A17", 1.05, [plate(EARTH, offset=[430, -250], overscan=1.0), bridge_bg(), jax([[0, "jax_front"]], h=1.14)],
  "Jax: 'And I'm winning.'", ["0-15"], camera={"z0": 1.05, "z1": 1.10, "drift": 6})
A("A18", 4.20, [plate(MOON, offset=[260, -300], overscan=1.35, in_s=27), console_bg(),
                pip(x=0.55, h=1.0, channels={"head_rot": [[0, 0], [0.2, -14], [0.6, -14], [1.0, 0]]})],
  "Shop bell: PIP's head swivels to it, then the job: 'A job, posted to us directly. One parcel, sealed, prepaid...'",
  ["0-16"], camera={"z0": 1.0, "z1": 1.08, "drift": 5})
A("B1", 10.40, [plate(EARTH, offset=[430, -250], overscan=1.0, in_s=30.6, speed=0.4),
                {"kind": "set", "src": "${REPO}/assets/sets/bridge/master-bright.jpg", "window": {"region": [0.1, 0.03, 0.92, 0.5]},
                 "crop": [0.05, 0.0, 0.95, 0.75], "blur": 2.0, "depth": 0.6},
                {"kind": "puppet", "name": "jaxr", "speaker": "JAX", "rig": "jax_real", "x": 0.5, "y": 1.12, "h": 1.15,
                 "depth": 1.25, "shadow": 0.2}],
  "LOOK B (photoreal cut-out, same rig): Jax listens to the fee, then 'Is?' ... 'Take it.' ... 'Take it take it take it take it-'",
  ["0-17", "0-19", "0-21"], camera={"z0": 1.0, "z1": 1.10, "drift": 6})
A("A19", 1.70, [plate(MOON, offset=[260, -300], overscan=1.35, in_s=27), console_bg(),
                pip(x=0.5, h=1.0, channels={"arm_rot": [[0, 0], [0.25, -10], [0.38, 16], [0.62, 16], [0.95, 0]]})],
  "PIP's stamp arm comes down: 'Accepted.'", [], camera={"z0": 1.02, "z1": 1.06, "drift": 4,
                                                          "shake": [{"at": 0.41, "amp_px": 9, "decay_s": 0.12}]})
E("A20", 2.90, [{"kind": "video", "src": "${SCRATCH}/e01/datavis/02_pip_report_1204.mp4", "in_s": 0.6}],
  "ANIMATED SCREEN: REPORT #1,204 typed out. PIP V.O.: '...filing a report on you. Once is binding.'", [])
A("A21", 2.40, [plate({"kind": "video", "src": SCARP, "in_s": 23.0, "depth": 0.3}),
                ship([[0, 0.25], [2.4, -0.15]], y=0.60, h=0.40, glow=[[0, 0.0], [0.15, 0.6], [0.25, 0.0], [0.45, 0.9], [0.55, 0.2], [0.8, 1.0]],
                     rot=[[0, 3], [2.4, -2]])],
  "REAL NASA video: the ship drifts; the engine coughs back to life. Jax V.O.: 'Who sends a parcel to a crater?'",
  ["0-23"], camera={"z0": 1.03, "z1": 1.08, "drift": 4, "shake": [{"at": 0.12, "amp_px": 6, "decay_s": 0.2}]})
E("A22", 2.95, [{"kind": "video", "src": "${SCRATCH}/arch/clips/C22_BanksAndCred.mp4", "in_s": 0.0,
                 "grade": {"sat": 1.0}}],
  "OLD FILM GAG (Banks and Credit, 1950s, public domain): 'Someone who knew precisely how much we owed.'",
  ["0-24"], typ="ARCHIVE")
A("A23", 3.05, [plate(MOON, offset=[120, -300], overscan=1.3, in_s=27), bridge_bg(crop=(0.05, 0.0, 0.95, 0.72)),
                pip(x=0.78, h=0.62, y=1.0, depth=1.1),
                jax([[0, "jax_front"]], x=0.33, h=1.0, y=1.08, look_keys={"x": [[0, 0.0], [0.7, 0.0], [0.9, 1.0], [3.05, 1.0]]})],
  "Two-shot: Jax and PIP, Moon in the window: 'Lucky.' / 'Filed under \"arithmetic\".'", ["0-25", "0-26"],
  camera={"z0": 1.0, "z1": 1.05, "drift": 5})

title = [s for s in arch["shots"] if s["id"] == "TITLE"][0]
title = copy.deepcopy(title); title["duration_s"] = 6.0
title["note"] = "MAIN TITLE over the real Moon (NASA SVS flyby)."
S.append(title)

# sanity: cut points
t = 0
for s in S:
    s["_t0"] = round(t, 3); t += s["duration_s"]
total = t

lines = [l for l in arch["dialogue"]["lines"] if l["id"].startswith("0-")]
sfx = [copy.deepcopy(x) for x in arch["sfx"] if (x.get("start_s") or 0) < 64.5 and "cargohold" not in x["id"]]
for x in sfx:
    if x.get("loop_s"):
        x["loop_s"] = min(x["loop_s"], 64.0)
music = [copy.deepcopy(m) for m in arch["music"] if m["id"] in ("M01", "title-sting")]
for m in music:
    if m["id"] == "title-sting":
        m["trim_s"] = 6.0; m["fade_out"] = 1.8

out = {
    "version": 1, "name": "E01-animation-test", "episode": "E01", "unit": "animation-test",
    "note": "Episode 1 cold open as code-driven cut-out animation over real NASA video. Built by production/tools/anim/e01_test_build.py; "
            "animation clips by production/tools/anim/anim.py; cut, mix and subtitles by production/tools/edit/render.py.",
    "vars": {"SCRATCH": SCR},
    "output": {"width": 1920, "height": 1080, "fps": 24, "crf": 18, "preset": "medium"},
    "finish": {"grain": 0.012, "halation": 0.25, "weave_px": 0.0, "vignette": 0.18, "saturation": 1.04, "split_tone": 0.0},
    "dialogue": {"lines": lines},
    "music": music, "sfx": sfx,
    "duck": arch.get("duck", {"music_db": -12, "sfx_db": -5}),
    "loudness": {"integrated": -16, "true_peak_ceiling": -2.0},
    "overlays": {"subtitles": arch["overlays"]["subtitles"]},
    "credits": [],
    "rigs": rigs,
    "shots": S,
}
for s in S:
    s.setdefault("overlays", {"cards": False})
json.dump(out, open(f"{REPO}/episodes/E01/animation-test-shotlist.json", "w"), indent=1, ensure_ascii=False)
print("shots", len(S), "total", round(total, 2))
for s in S:
    print(s["_t0"], s["id"], s["duration_s"], s["audio"]["lines"] if "audio" in s else "")
