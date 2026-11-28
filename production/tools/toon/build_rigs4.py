#!/usr/bin/env python3
"""Writes production/tools/toon/rigs4.json: every TEST 4 pose picture with its face landmarks
(read by eye from gridded crops made by landmark_sheet.py, picture pixel coordinates).
Per pose: eyes [[x,y,rx,ry] near, far], mouth [x,y,half_width], chin y, head ellipse [cx,cy,rx,ry],
neck pivot, anchor (the point placed on the floor / at the waist), head_h (hair top to chin).
"""
import json
CX = "${SCRATCH}/cx/toon4"
def face(src, eyes, mouth, chin, head, neck, anchor, head_h, er=(10, 5), **kw):
    e = [[eyes[0][0], eyes[0][1], er[0], er[1]], [eyes[1][0], eyes[1][1], er[0] * 0.8, er[1]]]
    d = {"src": f"{CX}/{src}.png", "eyes": e, "mouth": mouth[:2], "mouth_w": mouth[2], "chin": chin,
         "head": head, "neck": neck, "anchor": anchor, "head_h": head_h, "eye_ang": -8, "mouth_ang": -6}
    d.update(kw); return d
P = {}
# Jax, full body (wide shot) — small faces
P["J_idle"] = face("J_idle", [(823, 100), (851, 95)], (846, 124, 9), 142, [810, 85, 52, 62], [805, 150], [760, 925], 123, er=(5, 3))
P["J_sweep"] = face("J_sweep", [(803, 99), (827, 95)], (823, 124, 9), 142, [790, 85, 50, 60], [790, 150], [745, 921], 124, er=(5, 3))
P["J_shrug"] = face("J_shrug", [(792, 102), (820, 97)], (815, 121, 9), 140, [785, 85, 50, 60], [785, 150], [740, 922], 121, er=(5, 3))
# Jax, knee-up (two-shots)
P["Jk_listen"] = face("Jk_listen", [(828, 152), (876, 146)], (867, 197, 14), 230, [807, 131, 85, 105], [825, 257], [848, 940], 207)
P["Jk_plead"] = face("Jk_plead", [(812, 220), (877, 190)], (871, 285, 18), 318, [782, 169, 120, 140], [806, 354], [762, 940], 293, er=(11, 6), mouth_ang=-18, eye_ang=-22)
P["Jk_point"] = face("Jk_point", [(764, 186), (821, 165)], (815, 235, 17), 271, [735, 146, 110, 130], [753, 307], [808, 940], 238, er=(11, 5), mouth_ang=-14, eye_ang=-18)
P["Jk_self"] = face("Jk_self", [(789, 169), (839, 154)], (833, 217, 17), 250, [768, 130, 100, 125], [780, 285], [860, 940], 228, er=(10, 5), mouth_ang=-12)
P["Jk_shrug"] = face("Jk_shrug", [(820, 177), (868, 156)], (862, 235, 17), 265, [783, 150, 110, 130], [813, 301], [836, 940], 247, er=(11, 5), mouth_ang=-16, eye_ang=-20)
P["Jk_flinch"] = face("Jk_flinch", [(812, 206), (870, 194)], (846, 251, 17), 278, [779, 170, 110, 130], [803, 314], [893, 940], 252, er=(1, 1))
P["Jk_startle"] = face("Jk_startle", [(779, 175), (829, 160)], (823, 229, 17), 268, [761, 136, 105, 130], [779, 303], [919, 940], 239, er=(11, 6), mouth_ang=-14)
P["J_cu_finger"] = face("J_cu_finger", [(794, 294), (897, 257)], (873, 390, 34), 470, [778, 220, 190, 220], [810, 500], [770, 940], 446, er=(22, 10), mouth_ang=-20, eye_ang=-22)
# Mira, knee-up behind the counter, and close-ups
MK = dict(er=(16, 8))
P["M_neutral"] = face("M_neutral", [(736, 183), (813, 179)], (764, 257, 22), 299, [795, 170, 106, 130], [799, 310], [806, 940], 273, **MK)
P["M_form"] = face("M_form", [(767, 208), (841, 210)], (780, 279, 20), 318, [806, 197, 105, 130], [824, 336], [824, 940], 290, **MK)
P["M_show"] = face("M_show", [(733, 188), (817, 188)], (755, 270, 20), 314, [790, 175, 105, 130], [790, 318], [812, 940], 288, **MK)
P["M_tap"] = face("M_tap", [(733, 192), (813, 197)], (764, 275, 20), 310, [795, 180, 105, 130], [804, 322], [825, 940], 277, **MK)
P["M_stamp"] = face("M_stamp", [(745, 175), (825, 173)], (775, 255, 20), 295, [810, 170, 105, 130], [815, 320], [816, 940], 266, **MK)
P["M_stamp_up"] = face("M_stamp_up", [(770, 235), (850, 240)], (790, 310, 20), 355, [820, 225, 105, 130], [820, 380], [849, 940], 295, **MK)
P["M_slam"] = face("M_slam", [(735, 205), (820, 215)], (765, 300, 21), 340, [805, 190, 105, 130], [815, 370], [851, 940], 310, **MK)
P["M_cu"] = face("M_cu", [(788, 290), (911, 294)], (840, 404, 34), 470, [873, 270, 200, 240], [880, 510], [857, 940], 433, er=(28, 13), mouth_ang=0, eye_ang=0)
P["M_cu_look"] = face("M_cu_look", [(885, 309), (1005, 309)], (943, 431, 34), 490, [918, 228, 200, 250], [918, 540], [909, 940], 474, er=(28, 13), mouth_ang=0, eye_ang=0)
for k in ["M_neutral", "M_form", "M_show", "M_tap", "M_stamp", "M_stamp_up", "M_slam"]:
    P[k]["mouth_ang"] = 0; P[k]["eye_ang"] = 0
# Jax walk cycle: six drawings cut from one sheet; no face animation at this size
walk = {0: (152, 809), 1: (131, 805), 2: (138, 805), 3: (171, 808), 4: (152, 799), 5: (153, 801)}
for j, (hx, fy) in walk.items():
    P[f"J_walk{j}"] = {"src": f"{CX}/walk_{j}.png", "anchor": [hx, fy], "head_h": 107}
for k, v in P.items():
    if k.startswith(("Jk_", "M_", "J_cu")): v["extend"] = 0   # (tried 700-px edge extension: reads as a block; staging hides the cut instead)
json.dump({"poses": P}, open("/home/user/Universe-Series/production/tools/toon/rigs4.json", "w"), indent=1)
print(len(P), "poses")
