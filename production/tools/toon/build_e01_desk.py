#!/usr/bin/env python3
"""Writes episodes/E01/toon-test-shotlist.json — the pose-and-timing file for TEST 3
(E01 scene 3, the customs desk, lines 1-17, plus an exterior landing in front).
Times are seconds on the test's own timeline. Channel keys: [t, value, ease, dur]
(value reached at t; move starts at t-dur). Eases: io, out, in, back (overshoot), snap
(overshoot + settle), step.
"""
import json, os
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
conf = json.load(open(f"{R}/episodes/E01/dialogue-conform.json"))
sc3 = [s for s in conf["scenes"] if s["scene"] == "3"][0]
T0 = 7.0          # scene 3 starts after the 7 s exterior
SHIFT14 = 1.6     # extra pause before line 14: room for Mira's reaction beat
dialogue = []
for l in sc3["lines"][:17]:
    st = T0 + l["start_in_scene_s"] + (SHIFT14 if l["index"] >= 14 else 0)
    b = l["file_dry"][:-4]
    dialogue.append({"id": f"3-{l['index']:02d}", "who": l["speaker"].lower(), "start_s": round(st, 3),
                     "dur": l["duration_s"], "text": l["text_spoken"],
                     "src": "${SCRATCH}/e01/dialogue/" + l["file_dry"], "lips": "${TOON}/lips/" + b + ".json"})
L = {d["id"]: d["start_s"] for d in dialogue}
E = {d["id"]: d["start_s"] + d["dur"] for d in dialogue}

# ---------------------------------------------------------------- Jax
JX0, JX1 = 300, 1300
jax_keys = {
    "x": [[0, JX0], [10.8, JX0, "step"], [14.2, JX1, "lin", 3.4]],
    "turn": [[0, "tq"]],
    "look_x": [[0, 0.9], [8.0, 0.3], [9.4, 0.9], [21.0, 1.0], [24.9, -0.4], [26.0, 0.9], [53.9, 0.2], [54.7, 1.0]],
    "look_y": [[0, 0.0], [53.9, 0.8, "out", 0.2], [54.7, 0.0, "io", 0.3]],
    "brow": [[0, 0.1], [L["3-02"] + 0.1, 0.7, "back", 0.25], [9.3, 0.1], [L["3-05"] + 0.1, 0.6, "back"],
             [L["3-06"] + 0.2, -0.2], [L["3-07"], 0.4, "back", 0.2], [L["3-09"] + 2.8, 0.8, "back", 0.2], [L["3-09"] + 3.2, 0.3, "io", 0.2],
             [L["3-09"] + 3.6, 0.8, "back", 0.2], [L["3-09"] + 4.2, 0.2], [L["3-11"], 0.7, "back"], [L["3-11"] + 2.6, 1.0, "back", 0.2],
             [37.5, 0.2], [L["3-15"], 0.6, "back"], [L["3-16"] + 0.5, -0.3], [L["3-17"], 0.5, "back"],
             [53.05, -0.4, "snap", 0.1], [53.7, 1.1, "back", 0.15], [55.0, 0.4]],
    "brow_tilt": [[0, 0.0], [L["3-16"] + 0.5, 0.6], [L["3-17"] + 0.2, 0.3], [53.6, 0.0]],
    "lid": [[0, 0.0], [L["3-09"] + 3.0, 0.25], [L["3-09"] + 4.5, 0.0], [53.05, 1.0, "out", 0.08], [53.55, 1.0, "step"], [53.65, 0.0, "out", 0.08]],
    "tilt": [[0, 0], [L["3-05"], -4], [L["3-07"], 5, "back"], [L["3-08"] + 0.5, 0], [L["3-09"] + 2.2, -7, "back"], [L["3-10"], 0],
             [L["3-11"] + 2.4, -5, "back"], [37.0, 0], [L["3-17"], 6, "back"], [53.05, -3, "snap", 0.1], [54.0, 4], [55.5, 0]],
    "lean": [[0, 0], [14.2, 6, "snap", 0.5], [15.2, 2], [L["3-05"], 6], [L["3-09"] + 2.0, 9, "back"], [L["3-10"] + 0.5, 3],
             [L["3-15"], -4, "back"], [L["3-16"] + 0.3, 2], [53.05, -7, "snap", 0.1], [54.3, -2]],
    "crouch": [[0, 0], [L["3-09"] + 2.0, 2.5], [L["3-10"] + 0.5, 0], [53.05, 4, "snap", 0.1], [53.8, 0, "back", 0.3]],
    "shrug": [[0, 0], [10.0, 2.5, "back", 0.25], [10.5, 0], [L["3-17"] + 0.1, 3.2, "back", 0.25], [E["3-17"] + 0.2, 0.5], [53.05, 3.8, "snap", 0.1], [54.0, 0.6]],
    "squash": [[0, 0], [14.1, 0.04, "out", 0.12], [14.35, -0.02, "snap", 0.2], [14.6, 0], [53.0, 0.07, "out", 0.06], [53.3, -0.03, "snap", 0.2], [53.7, 0],
               [53.75, -0.05, "back", 0.1], [54.0, 0]],
    # arm 0 = the front arm (screen side away from where he faces); angles: deg from straight down, + = forward
    "sh0": [[0, 8], [L["3-02"] + 0.2, 75, "back", 0.3], [9.4, 8], [14.3, 40, "back", 0.35], [L["3-05"] + 0.2, 55, "back"],
            [L["3-06"] + 0.3, 40], [L["3-07"] + 0.1, 80, "back", 0.2], [L["3-08"] + 0.4, 40], [L["3-09"] + 0.2, 105, "back", 0.3],
            [L["3-09"] + 1.6, 45], [L["3-09"] + 2.2, 50, "back"], [L["3-11"] + 0.3, 60, "back"], [L["3-11"] + 2.6, 85, "back", 0.15],
            [L["3-11"] + 3.4, 60], [37.5, 30], [L["3-15"] + 0.1, 20, "back"], [L["3-16"], 30], [L["3-17"] + 0.1, 40, "back"],
            [53.05, 70, "snap", 0.1], [54.0, 25]],
    "el0": [[0, 12], [L["3-02"] + 0.2, 15, "back", 0.3], [9.4, 12], [14.3, 20], [L["3-05"] + 0.2, 70, "back"], [L["3-07"] + 0.1, 10, "back", 0.2],
            [L["3-08"] + 0.4, 25], [L["3-09"] + 0.2, 0, "back", 0.3], [L["3-09"] + 2.2, 70, "back"], [L["3-11"] + 0.3, 95, "back"],
            [L["3-11"] + 2.6, 90, "back", 0.15], [37.5, 30], [L["3-15"] + 0.1, 150, "back"], [L["3-16"], 40], [L["3-17"] + 0.1, 70, "back"],
            [53.05, 80, "snap", 0.1], [54.0, 30]],
    "hand0": [[0, "fist"], [L["3-02"], "open"], [9.4, "fist"], [L["3-05"], "open"], [L["3-07"], "point"], [L["3-08"] + 0.3, "open"],
              [L["3-09"], "point"], [L["3-09"] + 1.6, "open"], [L["3-11"], "point"], [37.5, "open"], [L["3-15"], "point"], [L["3-16"], "fist"],
              [L["3-17"], "open"]],
    "sh1": [[0, -6], [14.3, -10], [L["3-09"] + 2.2, 30, "back"], [L["3-10"] + 0.5, -6], [L["3-17"] + 0.1, 35, "back"], [53.05, 55, "snap", 0.1], [54.2, -6]],
    "el1": [[0, 10], [L["3-09"] + 2.2, 60, "back"], [L["3-10"] + 0.5, 10], [L["3-17"] + 0.1, 60, "back"], [54.2, 10]],
    "hand1": [[0, "fist"], [L["3-09"] + 2.0, "open"], [L["3-10"] + 0.5, "fist"], [L["3-17"], "open"], [54.2, "fist"]],
}
# ---------------------------------------------------------------- Mira (faces screen-left; arm 1 = front arm)
mira_keys = {
    "turn": [[0, "tq"], [40.85, "front"], [42.3, "tq"], [54.0, "front"]],
    "look_x": [[0, -0.2], [L["3-03"], -1.0], [11.4, -0.1], [16.4, -1.0], [40.85, 0.0, "snap", 0.15], [42.3, -1.0], [54.0, 0.1]],
    "look_y": [[0, 0.7], [L["3-03"], 0.0], [11.4, 0.8], [16.4, 0.0], [L["3-08"] + 0.1, 0.6], [L["3-08"] + 1.5, 0.0], [40.85, 0.0]],
    "lid": [[0, 0.25], [L["3-06"], 0.38, "out", 0.15], [L["3-08"] + 2.5, 0.25], [L["3-12"], 0.4], [40.6, 0.6, "out", 0.2],
            [40.85, 0.42, "snap", 0.15], [42.3, 0.3], [L["3-16"], 0.4], [53.0, 0.1, "out", 0.1], [54.0, 0.35]],
    "brow": [[0, 0.0], [L["3-03"], 0.25, "back"], [11.4, 0], [L["3-06"], -0.2], [L["3-10"], 0.2, "back"], [L["3-12"], -0.1], [40.85, 0.1, "snap", 0.15],
             [44.0, 0.3, "back"], [L["3-16"], -0.2], [52.3, 0.5, "back"], [53.0, -0.3, "snap", 0.08], [54.0, 0.2]],
    "brow_tilt": [[0, 0], [L["3-06"], -0.5], [L["3-08"] + 2.5, -0.1], [L["3-12"], -0.35], [40.85, 0, "snap", 0.15], [L["3-16"], -0.5], [53.0, -0.6], [54.0, 0]],
    "brow_asym": [[0, 0], [40.6, -0.1, "out", 0.2], [40.85, 1.0, "snap", 0.15], [42.3, 0.0], [54.0, 0.6, "back"]],
    "tilt": [[0, 2], [L["3-03"], -3], [11.4, 4], [L["3-06"], -6, "back"], [L["3-08"] + 1.0, 2], [L["3-10"], -4], [L["3-10"] + 2.0, 3],
             [L["3-12"], 0], [40.6, 3, "out", 0.2], [40.85, -8, "snap", 0.15], [42.3, 0], [L["3-14"] + 2.0, 4], [L["3-16"], -3], [54.0, 6, "back"]],
    "squash": [[0, 0], [40.6, 0.06, "out", 0.2], [40.85, -0.04, "snap", 0.15], [41.2, 0], [52.9, -0.04, "out", 0.4], [53.0, 0.05, "in", 0.08], [53.4, 0, "snap", 0.3]],
    "lean": [[0, 0], [L["3-06"], 3, "back"], [L["3-08"] + 2.0, 0], [L["3-14"], 2], [52.9, -5, "out", 0.5], [53.0, 7, "in", 0.08], [53.6, 1, "snap", 0.4]],
    "shrug": [[0, 0], [40.85, 1.2, "snap", 0.15], [42.0, 0]],
    "sh1": [[0, 35], [11.0, 40], [16.4, 30], [L["3-08"] + 0.1, 70, "back", 0.3], [L["3-08"] + 2.4, 32], [L["3-10"] + 0.9, 55, "back"],
            [L["3-10"] + 2.6, 30], [L["3-14"] + 2.0, 60, "back", 0.4], [52.9, 140, "out", 0.55], [53.0, 50, "in", 0.08], [54.2, 40]],
    "el1": [[0, 70], [L["3-08"] + 0.1, 80, "back", 0.3], [L["3-08"] + 2.4, 70], [L["3-10"] + 0.9, -10, "back"], [L["3-10"] + 2.6, 70],
            [L["3-14"] + 2.0, 75, "back", 0.4], [52.9, 40, "out", 0.55], [53.0, 25, "in", 0.08], [54.2, 60]],
    "hand1": [[0, "form"], [16.4, "form"], [L["3-08"] + 2.5, "fist"], [L["3-10"] + 0.6, "point"], [L["3-10"] + 2.6, "fist"], [L["3-14"] + 1.6, "stamp"]],
    "sh0": [[0, 20], [L["3-04"] + 2.0, 35, "back"], [16.0, 20], [L["3-14"], 25], [52.9, 10]],
    "el0": [[0, 40], [L["3-04"] + 2.0, 75, "back"], [16.0, 40]],
    "hand0": [[0, "fist"], [L["3-04"] + 1.8, "open"], [16.0, "fist"]],
}
def ch(defaults, keys, rig, extra=None):
    d = {"rig": rig, "defaults": defaults, "keys": keys}
    if extra: d.update(extra)
    return d
shot = {
 "name": "E01-toon-test", "episode": "E01", "scene": "3 (customs desk), lines 1-17",
 "note": "TEST 3: flat 2D puppet rig over real NASA video. Built by production/tools/toon/build_e01_desk.py.",
 "vars": {"SCRATCH": S, "TOON": S + "/toon"},
 "duration_s": 56.0, "subtitles": True,
 "dialogue": dialogue,
 "characters": {
   "mira": ch({"H": 580, "x": 1800, "y": 1002, "turn": "tq", "lid": 0.25, "mouth_rest": "X"}, mira_keys, f"{R}/production/tools/toon/rigs/mira.json"),
   "jax": ch({"H": 640, "x": JX0, "y": 1075, "turn": "tq", "mouth_rest": "X"}, jax_keys, f"{R}/production/tools/toon/rigs/jax.json",
             {"walk": {"t0": 10.8, "t1": 14.2, "x0": JX0, "x1": JX1, "cycles": 3.5, "y": 1075, "lift": 5, "bob": 2.4, "ease": "io"}}),
 },
 "hall": {"bg": "${TOON}/pics/hall_bg.jpg", "paint_out": [1232, 466, 1300, 526], "paint_fill_from": [1300, 500],
          "window_bbox": [345, 70, 1376, 500], "desk_poly": [[1028, 556], [1080, 512], [1376, 492], [1376, 768], [1028, 768]],
          "lamp_poly": [[1103, 392], [1150, 378], [1236, 408], [1236, 472], [1196, 474], [1168, 452], [1150, 548], [1192, 552], [1192, 580], [1120, 580], [1128, 548], [1110, 425]],
          "glass_world": [1478, 440, 1920, 800],
          "plate": {"src": "${TOON}/plates/window.mp4", "t_offset": 7.0, "x": 0, "y": 98, "w": 1955, "parallax": 0.25, "gain": 1.25},
          "rim_color": [205, 228, 255], "rim_dir": [-0.45, -1.0]},
 "ext": {"src": "${TOON}/plates/ext.mp4", "gain": 1.12, "rim_dir": [-0.8, -0.6],
         "keys": {"x": [[0, -350], [4.4, 1050, "out", 4.4], [6.3, 1120, "io", 1.9]],
                  "y": [[0, 200], [4.4, 520, "io", 4.4], [6.2, 680, "out", 1.8], [6.45, 670, "snap", 0.25]],
                  "scale": [[0, 0.32], [4.4, 0.55, "io", 4.4], [6.3, 0.6]],
                  "rot": [[0, -14], [2.2, 6, "io", 2.2], [4.4, -3, "io", 2.2], [6.2, -6, "io", 1.2], [6.45, 0, "snap", 0.3]],
                  "alt": [[0, 700], [4.4, 360, "io", 4.4], [6.25, 0, "out", 1.85]],
                  "ground_y": [[0, 1010], [6.3, 960]],
                  "thrust": [[0, 0.8], [4.6, 1.0], [6.0, 1.6, "io", 1.2], [6.5, 0.25, "out", 0.4]]},
         "dust_t0": 4.9, "dust_t1": 6.6, "engines": [[0.012, 0.18, 50], [0.012, 0.395, 50], [0.012, 0.693, 50], [0.012, 0.902, 50]]},
 "ship": {"file": "${TOON}/parts/ship_0.png"},
 "shots": [
   {"id": "T3-01", "kind": "ext", "t0": 0.0, "t1": 7.0, "fade_in": 0.5, "note": "EXT: the Unscheduled comes in low over the Moon and sets down at Rim Port"},
   {"id": "T3-02", "kind": "hall", "t0": 7.0, "t1": 17.6, "note": "WIDE: the empty hall, Earth in the window; Jax walks to the desk",
    "camera": {"cx": [[7.0, 960], [17.6, 1080, "io", 10.6]], "cy": [[7.0, 540], [17.6, 560, "io", 10.6]], "zoom": [[7.0, 1.0], [17.6, 1.12, "io", 10.6]]}},
   {"id": "T3-03", "kind": "hall", "t0": 17.6, "t1": 33.0, "note": "TWO-SHOT over the desk",
    "camera": {"cx": [[17.6, 1320], [33.0, 1330]], "cy": [[17.6, 600], [33.0, 590]], "zoom": [[17.6, 1.6], [33.0, 1.66, "io", 15]]}},
   {"id": "T3-04", "kind": "hall", "t0": 33.0, "t1": 37.0, "note": "CLOSE: Jax and his Section Twelve",
    "camera": {"cx": [[33.0, 1330], [37.0, 1340]], "cy": [[33.0, 540], [37.0, 535]], "zoom": [[33.0, 2.5], [37.0, 2.62, "io", 4]]}},
   {"id": "T3-05", "kind": "hall", "t0": 37.0, "t1": 42.4, "note": "CLOSE: Mira; the reaction beat (look to camera)",
    "camera": {"cx": [[37.0, 1577], [42.4, 1577]], "cy": [[37.0, 520], [40.6, 520], [40.9, 512, "snap", 0.2]], "zoom": [[37.0, 2.7], [40.6, 2.72], [40.9, 2.9, "snap", 0.2]]}},
   {"id": "T3-06", "kind": "hall", "t0": 42.4, "t1": 56.0, "fade_out": 0.6, "note": "TWO-SHOT: the stamp",
    "camera": {"cx": [[42.4, 1320], [56.0, 1320]], "cy": [[42.4, 600], [56.0, 590]], "zoom": [[42.4, 1.62], [52.9, 1.7, "io", 10], [53.05, 1.78, "snap", 0.12]]},
    "shake": [{"at": 53.0, "amp": 14, "dur": 0.5}]}
 ],
 "audio": {
   "music": [{"src": "${SCRATCH}/e01/music/E01-M02-approach.wav", "at": 0.0, "from": 30.0, "dur": 8.2, "gain_db": -4, "fade_in": 0.6, "fade_out": 1.6},
             {"src": "${SCRATCH}/e01/music/E01-C1-button-a.wav", "at": 53.15, "from": 0.0, "dur": 3.0, "gain_db": -3, "fade_out": 0.4}],
   "sfx": [{"src": "${SCRATCH}/e01/sfx/ship_engine_idle_loop.wav", "at": 0.0, "dur": 6.4, "gain_db": -8, "fade_in": 0.8, "fade_out": 0.3},
           {"src": "${SCRATCH}/e01/sfx/ship_engine_spindown.wav", "at": 6.2, "dur": 2.6, "gain_db": -9, "fade_out": 1.2},
           {"src": "${SCRATCH}/e01/sfx/customs_hall_roomtone_loop.wav", "at": 6.8, "dur": 49.2, "gain_db": -16, "fade_in": 0.4, "fade_out": 0.6},
           {"src": "${SCRATCH}/e01/sfx/footsteps_lowg_distant_pattern.wav", "at": 10.8, "from": 0.0, "dur": 3.5, "gain_db": -6, "fade_out": 0.4},
           {"src": "${SCRATCH}/e01/sfx/paper_slip_rustle.wav", "at": L["3-08"], "gain_db": -10},
           {"src": "${SCRATCH}/e01/sfx/customs_desk_stamp_heavy_a.wav", "at": 52.98, "gain_db": -1}],
   "duck_music_db": -10, "loudness": -16.0}
}
json.dump(shot, open(f"{R}/episodes/E01/toon-test-shotlist.json", "w"), indent=1)
print("wrote", len(dialogue), "lines; last line ends", max(E.values()))
