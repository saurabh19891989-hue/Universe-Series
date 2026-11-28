#!/usr/bin/env python3
"""Writes episodes/E01/toon-test4-shotlist.json — TEST 4 (painted pose library) of the same scene
as test 3 (E01 scene 3 lines 1-17 + exterior landing). Dialogue, audio and timing are taken from
the test 3 file so the two can be compared directly. Pose keys: [t, "pose"] (held drawings,
snappy swaps); body keys [t, value, ease, dur] as in test 3.
"""
import json
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
t3 = json.load(open(f"{R}/episodes/E01/toon-test-shotlist.json"))
L = {d["id"]: d["start_s"] for d in t3["dialogue"]}
E = {d["id"]: d["start_s"] + d["dur"] for d in t3["dialogue"]}
WALK0, WALK1, X0, X1 = 11.2, 13.8, 300, 1130

jax = {
 "pose": [[0, "J_idle"], [L["3-02"] + 0.05, "J_sweep"], [9.3, "J_idle"], [10.05, "J_shrug"], [10.7, "J_idle"],
          [WALK0, "walk"], [WALK1, "J_idle"],
          [17.6, "Jk_listen"], [L["3-05"] + 0.1, "Jk_plead"], [L["3-06"] + 0.3, "Jk_listen"], [L["3-07"] + 0.05, "Jk_point"],
          [L["3-08"] + 0.4, "Jk_listen"], [L["3-09"] + 0.15, "Jk_point"], [L["3-09"] + 1.75, "Jk_plead"], [E["3-09"] + 0.4, "Jk_listen"],
          [33.0, "J_cu_finger"], [37.0, "Jk_listen"],
          [L["3-15"] + 0.05, "Jk_self"], [E["3-15"] + 0.3, "Jk_listen"], [L["3-17"] + 0.05, "Jk_shrug"],
          [53.02, "Jk_flinch"], [53.65, "Jk_startle"]],
 "dx": [[0, 0], [WALK0, 0, "step"], [WALK1, X1 - X0, "io", WALK1 - WALK0]],
 "lean": [[0, 0], [WALK1, 0], [WALK1 + 0.12, 4, "out", 0.12], [WALK1 + 0.45, 0, "snap", 0.33],
          [L["3-09"] + 1.75, 3, "back", 0.25], [E["3-09"] + 0.4, 0], [53.02, -5, "snap", 0.1], [53.65, -2, "back", 0.2]],
 "squash": [[0, 0], [10.05, 0.05, "out", 0.08], [10.3, 0, "snap", 0.25], [53.0, 0.08, "out", 0.05], [53.4, 0, "snap", 0.35],
            [53.62, -0.06, "out", 0.06], [53.95, 0, "snap", 0.3]],
 "dy": [[0, 0], [WALK0, 0]],
}
mira = {
 "pose": [[0, "M_form"], [L["3-03"], "M_neutral"], [L["3-04"] + 0.1, "M_form"], [16.4, "M_neutral"],
          [L["3-08"] + 0.05, "M_show"], [E["3-08"] + 0.2, "M_neutral"], [L["3-10"] + 1.2, "M_tap"], [E["3-10"] + 0.2, "M_neutral"],
          [37.0, "M_cu"], [40.85, "M_cu_look"], [42.4, "M_neutral"],
          [L["3-14"] + 2.2, "M_stamp"], [52.3, "M_stamp_up"], [53.0, "M_slam"]],
 "lean": [[0, 0], [40.6, 2, "out", 0.2], [40.85, -3, "snap", 0.15], [42.3, 0], [52.3, -4, "out", 0.4], [53.0, 5, "in", 0.08], [53.6, 1, "snap", 0.4]],
 "squash": [[0, 0], [40.6, 0.05, "out", 0.2], [40.85, -0.03, "snap", 0.2], [41.3, 0], [52.95, -0.04, "out", 0.4], [53.0, 0.06, "in", 0.06], [53.4, 0, "snap", 0.3]],
 "dx": [[0, 0]], "dy": [[0, 0], [52.3, -6, "out", 0.4], [53.0, 4, "in", 0.08], [53.5, 0, "snap", 0.4]],
}
WIDE = {"jax": {"x": X0, "y": 1010, "head": 92, "use_dx": True}, "mira": {"x": 1650, "y": 508, "head": 62, "behind_fg": True, "align": "neck"}}
TWO = {"jax": {"x": 790, "y": 482, "head": 165, "align": "neck", "behind_fg": True}, "mira": {"x": 1420, "y": 495, "head": 150, "behind_fg": True, "align": "neck"}}
CUJ = {"jax": {"x": 820, "y": 500, "head": 230, "align": "neck"}, "mira": {"hide": True}}
CUM = {"mira": {"x": 1300, "y": 540, "head": 215, "behind_fg": True, "align": "neck"}, "jax": {"hide": True}}
SC = "${SCRATCH}"
shot = {
 "name": "E01-toon-test4", "episode": "E01", "scene": "3 (customs desk), lines 1-17",
 "note": "TEST 4: painted pose-library puppets over real NASA video. Built by production/tools/toon/build_e01_desk4.py.",
 "vars": {"SCRATCH": S, "REPO": R, "TOON": S + "/toon"}, "rigs": "${REPO}/production/tools/toon/rigs4.json",
 "duration_s": 56.0, "dialogue": t3["dialogue"], "audio": t3["audio"],
 "characters": {
   "jax": {"keys": jax, "defaults": {"pose": "J_idle"},
           "walk": {"t0": WALK0, "t1": WALK1, "x0": 0, "stride": 365, "frames": [f"J_walk{i}" for i in range(6)], "phase": 0}},
   "mira": {"keys": mira, "defaults": {"pose": "M_form"}}},
 "sets": {
   "wide": {"src": f"{SC}/cx/toon4/set_wide.png", "window_region": [0.17, 0.11, 0.88, 0.59],
            "fg_polys": [[[1135, 543], [1672, 543], [1672, 941], [1135, 941]]],
            "plate": {"src": f"{SC}/toon/plates/window2.mp4", "t_offset": 7.0, "x": 240, "y": 30, "w": 1560, "parallax": 0.3, "gain": 1.3}},
   "desk": {"src": f"{SC}/cx/toon4/set_desk.png", "window_region": [0.03, 0.09, 0.97, 0.68],
            "fg_polys": [[[586, 606], [1672, 606], [1672, 941], [586, 941]]],
            "plate": {"src": f"{SC}/toon/plates/window2.mp4", "t_offset": 7.0, "x": -40, "y": -20, "w": 2000, "parallax": 0.3, "gain": 1.3}}},
 "ext": {"src": f"{SC}/toon/plates/ext.mp4", "ship": f"{SC}/cx/toon4/ship.png", "gain": 1.08, "rim_dir": [-0.8, -0.6],
         "touchdown": 5.2, "ground_point": [1050, 760], "ground_off": [0, -150], "ground_y": 900,
         "keys": {"x": [[0, -350], [3.4, 760, "out", 3.4], [5.2, 1050, "io", 1.8]],
                  "y": [[0, 170], [3.4, 470, "io", 3.4], [5.2, 610, "out", 1.8]],
                  "scale": [[0, 0.26], [3.4, 0.36, "io", 3.4], [5.2, 0.40, "io", 1.8]],
                  "rot": [[0, -12], [1.8, 7, "io", 1.8], [3.6, -2, "io", 1.8], [5.0, -5, "io", 1.4], [5.35, 0, "snap", 0.3]],
                  "alt": [[0, 650], [3.4, 300, "io", 3.4], [5.2, 0, "out", 1.8]],
                  "settle": [[5.2, 8], [5.5, 0, "snap", 0.3]],
                  "thrust": [[0, 0.8], [3.6, 1.0], [5.0, 1.6, "io", 1.2], [5.6, 0.15, "out", 0.5]]},
         "dust_t0": 4.2, "dust_t1": 5.8,
         "engines": [[0.014, 0.27, 40], [0.014, 0.47, 40], [0.014, 0.69, 40], [0.014, 0.90, 40]]},
 "shots": [
   {"id": "T4-01", "kind": "ext", "t0": 0.0, "t1": 7.0, "fade_in": 0.5, "note": "EXT: the Unscheduled comes in over the Moon and sets down; the camera flies on past it"},
   {"id": "T4-02", "kind": "set", "set": "wide", "t0": 7.0, "t1": 17.6, "chars": WIDE, "note": "WIDE: the hall, Earth rising in the window; Jax walks to the desk",
    "camera": {"cx": [[7.0, 960], [17.6, 1040, "io", 10.6]], "cy": [[7.0, 545], [17.6, 560, "io", 10.6]], "zoom": [[7.0, 1.0], [17.6, 1.1, "io", 10.6]]}},
   {"id": "T4-03", "kind": "set", "set": "desk", "t0": 17.6, "t1": 33.0, "chars": TWO, "note": "TWO-SHOT at the counter",
    "camera": {"cx": [[17.6, 1090], [33.0, 1100, "io", 15]], "cy": [[17.6, 560], [33.0, 555]], "zoom": [[17.6, 1.3], [33.0, 1.36, "io", 15]]}},
   {"id": "T4-04", "kind": "set", "set": "desk", "t0": 33.0, "t1": 37.0, "chars": CUJ, "bg_blur": 2.2, "note": "CLOSE: Jax, Section Twelve",
    "camera": {"cx": [[33.0, 900], [37.0, 910, "io", 4]], "cy": [[33.0, 420], [37.0, 415]], "zoom": [[33.0, 2.0], [37.0, 2.08, "io", 4]]}},
   {"id": "T4-05", "kind": "set", "set": "desk", "t0": 37.0, "t1": 42.4, "chars": CUM, "bg_blur": 2.2, "note": "CLOSE: Mira; the look to camera",
    "camera": {"cx": [[37.0, 1260], [40.6, 1260], [40.9, 1280, "snap", 0.2]], "cy": [[37.0, 430], [40.6, 430], [40.9, 410, "snap", 0.2]],
               "zoom": [[37.0, 2.0], [40.6, 2.02], [40.9, 2.18, "snap", 0.2]]}},
   {"id": "T4-06", "kind": "set", "set": "desk", "t0": 42.4, "t1": 56.0, "chars": TWO, "fade_out": 0.6, "note": "TWO-SHOT: the stamp",
    "camera": {"cx": [[42.4, 1090], [56.0, 1090]], "cy": [[42.4, 560], [56.0, 555]], "zoom": [[42.4, 1.3], [52.9, 1.36, "io", 10], [53.05, 1.44, "snap", 0.12]]},
    "shake": [{"at": 53.0, "amp": 14, "dur": 0.5}]}]
}
json.dump(shot, open(f"{R}/episodes/E01/toon-test4-shotlist.json", "w"), indent=1)
print("ok")
