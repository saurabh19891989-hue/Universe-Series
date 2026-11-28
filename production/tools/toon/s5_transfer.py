#!/usr/bin/env python3
"""Medium-shot lip-sync: carry a close-up's picture-made mouth (and blink) set onto a smaller pose
picture of the same character at the same head angle.
usage: s5_transfer.py LANDMARKS.json PICDIR FACEDIR SRC_BASE TARGET [TARGET ...]
For each key in FACEDIR/SRC_BASE__<key>.png: take the mouth (or eye) region, map it onto TARGET with
a similarity transform fitted to the landmarks (mouth corners + lip centre, or the two eye boxes),
colour-match on a ring, feather the edge, write FACEDIR/TARGET__<key>.png (+ TARGET__X.png = TARGET).
"""
import sys, json, os, numpy as np, cv2
LM = json.load(open(sys.argv[1])); PIC, FACES, SRC = sys.argv[2], sys.argv[3], sys.argv[4]; TGTS = sys.argv[5:]
MOUTHS = ["A", "B", "C", "D", "E", "F", "G", "H", "smile", "shout"]
def pts_mouth(l): return np.float32([l["mouth_l"], l["mouth_r"], l["lip_top"], l["lip_bot"]])
def pts_eyes(l):
    c = lambda b: [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]
    return np.float32([c(l["eye_l"]), c(l["eye_r"]), [l["eye_l"][0], l["eye_l"][1]], [l["eye_r"][2], l["eye_r"][3]]])
def region(l, kind, shape):
    m = np.zeros(shape[:2], np.uint8)
    if kind == "mouth":
        (cx, cy), w = l["mouth_c"], l["mouth_w"]
        top = min(l["lip_top"][1], cy) - 0.32 * w; bot = l["chin"][1] + 0.1 * w
        cv2.ellipse(m, (int(cx), int((top + bot) / 2)), (int(w * 0.9), int((bot - top) / 2)), 0, 0, 360, 255, -1)
    else:
        for k in ("eye_l", "eye_r"):
            x0, y0, x1, y1 = l[k]; cv2.ellipse(m, (int((x0 + x1) / 2), int((y0 + y1) / 2)), (int((x1 - x0) * 0.85), int((y1 - y0) * 1.6 + 4)), 0, 0, 360, 255, -1)
    return m
def green(im):
    f = im.astype(np.float32); return (f[..., 1] - np.maximum(f[..., 0], f[..., 2])) > 40
ls = LM[SRC]
src_base = cv2.imread(f"{FACES}/{SRC}__X.png")
for T in TGTS:
    lt = LM.get(T)
    if lt is None: print("no landmarks for", T); continue
    tgt = cv2.imread(f"{PIC}/{T}.png"); h, w = tgt.shape[:2]
    cv2.imwrite(f"{FACES}/{T}__X.png", tgt)
    for key in MOUTHS + ["blink"]:
        p = f"{FACES}/{SRC}__{key}.png"
        if not os.path.exists(p): continue
        kind = "eyes" if key == "blink" else "mouth"
        A = pts_eyes(ls) if kind == "eyes" else pts_mouth(ls)
        B = pts_eyes(lt) if kind == "eyes" else pts_mouth(lt)
        Mx, _ = cv2.estimateAffinePartial2D(A, B)
        if Mx is None: continue
        src = cv2.imread(p)
        warped = cv2.warpAffine(src, Mx, (w, h), flags=cv2.INTER_AREA if Mx[0, 0] < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        wbase = cv2.warpAffine(src_base, Mx, (w, h), flags=cv2.INTER_AREA if Mx[0, 0] < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        m = region(lt, kind, tgt.shape)
        # only paste where the close-up's version differs from its own base (the changed part), so the
        # target keeps its own skin, stubble and outline everywhere else
        diff = cv2.GaussianBlur((np.abs(warped.astype(np.float32) - wbase).sum(2) > 30).astype(np.float32), (0, 0), 2)
        diff = cv2.dilate(diff, np.ones((7, 7), np.uint8))
        mm = np.clip(diff, 0, 1) * (m > 0)
        ring = (cv2.dilate((mm > 0.05).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0) & (mm < 0.05) & ~green(tgt) & ~green(warped)
        rf = ring.astype(np.float32)[..., None]
        num = cv2.GaussianBlur((tgt.astype(np.float32) - warped.astype(np.float32)) * rf, (0, 0), 12)
        den = cv2.GaussianBlur(rf[..., 0], (0, 0), 12)[..., None] + 1e-4
        fixed = np.clip(warped.astype(np.float32) + num / den, 0, 255)
        a = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 1.5)[..., None]
        out = (tgt * (1 - a) + fixed * a).astype(np.uint8)
        cv2.imwrite(f"{FACES}/{T}__{key}.png", out)
    print("done", T)
