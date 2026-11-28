#!/usr/bin/env python3
"""Seamless face sets: paste only the changed region of each edit picture back onto its base.
usage: s5_faces.py LANDMARKS.json PICDIR OUTDIR BASE [BASE ...]
For BASE (e.g. J5_cu) it reads PICDIR/BASE.png and every PICDIR/BASE_<key>.png edit:
 1. registers the edit to the base (ECC affine on the face area), so a slightly shifted redraw lines up;
 2. builds a soft region: mouth + jaw for mouth shapes, eyes (+ brows) for blink/brow keys, from
    MediaPipe landmarks of the base and of the edit (union, so an open jaw is fully inside);
 3. matches colour on a ring round the region, then blends with a 6-px feathered edge so no seam or cut lip remains.
Writes OUTDIR/BASE__<key>.png (full picture, same size as the base) and OUTDIR/BASE__X.png (the base).
"""
import sys, json, os, glob, subprocess, numpy as np, cv2
LMF, PIC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; bases = sys.argv[4:]
os.makedirs(OUT, exist_ok=True)
LM = json.load(open(LMF))
MOUTHS = ["A", "B", "C", "D", "E", "F", "G", "H", "smile", "shout"]
EYES = ["blink", "brow_up", "brow_frown", "brow_skeptic"]

def register(base, edit, face_mask):
    g0 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g1 = cv2.cvtColor(edit, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    s = 0.5
    a, b = cv2.resize(g0, None, fx=s, fy=s), cv2.resize(g1, None, fx=s, fy=s)
    m = cv2.resize(face_mask, None, fx=s, fy=s)
    W = np.eye(2, 3, dtype=np.float32)
    try:
        _, W = cv2.findTransformECC(a, b, W, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), m, 5)
    except cv2.error:
        pass
    W[:, 2] /= s
    return cv2.warpAffine(edit, W, (base.shape[1], base.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REPLICATE)

def region(lm, kind, shape):
    m = np.zeros(shape[:2], np.uint8)
    if kind == "mouth":
        (cx, cy), w = lm["mouth_c"], lm["mouth_w"]
        ch = lm["chin"][1]
        top = min(lm["lip_top"][1], cy) - 0.32 * w; bot = ch + 0.12 * w
        cv2.ellipse(m, (int(cx), int((top + bot) / 2)), (int(w * 0.95), int((bot - top) / 2)), 0, 0, 360, 255, -1)
    else:
        for k in (("eye_l", "eye_r") if kind == "eyes" else ("eye_l", "eye_r", "brow_l", "brow_r")):
            x0, y0, x1, y1 = lm[k]; pw, ph = (x1 - x0) * 0.45, (y1 - y0) * 0.9 + 6
            cv2.ellipse(m, (int((x0 + x1) / 2), int((y0 + y1) / 2)), (int((x1 - x0) / 2 + pw), int((y1 - y0) / 2 + ph)), 0, 0, 360, 255, -1)
        if kind == "brows":
            x0 = min(lm["brow_l"][0], lm["eye_l"][0]); x1 = max(lm["brow_r"][2], lm["eye_r"][2])
            y0 = min(lm["brow_l"][1], lm["brow_r"][1]); y1 = max(lm["eye_l"][3], lm["eye_r"][3])
            pad = (y1 - y0) * 0.45
            cv2.rectangle(m, (int(x0 - pad), int(y0 - pad * 1.2)), (int(x1 + pad), int(y1 + pad * 0.5)), 255, -1)
    return m

def face_mask(lm, shape):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(lm["oval"], np.int32)], 255)
    return cv2.dilate(m, np.ones((25, 25), np.uint8))

for b in bases:
    base = cv2.imread(f"{PIC}/{b}.png"); lmb = LM[b]
    fm = face_mask(lmb, base.shape)
    cv2.imwrite(f"{OUT}/{b}__X.png", base)
    for key in MOUTHS + EYES:
        p = f"{PIC}/{b}_{key}.png"
        if not os.path.exists(p): print("missing", p); continue
        kind = "mouth" if key in MOUTHS else ("eyes" if key == "blink" else "brows")
        m = region(lmb, kind, base.shape)
        if key == "shout": m = cv2.bitwise_or(m, region(lmb, "brows", base.shape))
        # register on the face area round the changed part (local fit: edits sometimes nudge the head)
        ed = register(base, cv2.imread(p), cv2.dilate(m, np.ones((121, 121), np.uint8)) & fm)
        lme = LM.get(f"{b}_{key}")
        if lme and kind == "mouth": m = cv2.bitwise_or(m, region(lme, kind, base.shape))
        # colour match: low-frequency offset measured on a ring just outside the region, applied inside
        # (OpenCV 5's seamlessClone returned the destination almost unchanged here, so this replaces it)
        ring = (cv2.dilate(m, np.ones((31, 31), np.uint8)) > 0) & (m == 0)
        def green(im):
            f = im.astype(np.float32); return (f[..., 1] - np.maximum(f[..., 0], f[..., 2])) > 40
        ring = ring & ~green(base) & ~green(ed)             # background never sets the colour offset
        ring = ring.astype(np.float32)[..., None]
        diff = (base.astype(np.float32) - ed.astype(np.float32)) * ring
        num = cv2.GaussianBlur(diff, (0, 0), 30); den = cv2.GaussianBlur(ring[..., 0], (0, 0), 30)[..., None] + 1e-4
        cl = np.clip(ed.astype(np.float32) + num / den, 0, 255)
        a = cv2.GaussianBlur(cv2.erode(m, np.ones((9, 9), np.uint8)).astype(np.float32) / 255, (0, 0), 6)[..., None]
        out = (base * (1 - a) + cl * a).astype(np.uint8)
        cv2.imwrite(f"{OUT}/{b}__{key}.png", out)
    print("done", b)
