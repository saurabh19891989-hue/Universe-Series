#!/usr/bin/env python3
"""SAMPLE 5 renderer (stage 2b): the frozen 2:42.4 timeline, picture side.
usage: s5_build.py OUTDIR [--still T ...] [--frames a:b] [--workers 4]
Characters are pose libraries of approved variant-B pictures; faces animate with picture-made sets
(close-ups: edits of the base; medium shots: the close-up set carried over by s5_transfer.py). Pose
changes cut on the frame with a squash-and-settle pop, through a drawn in-between where one exists;
nothing is dissolved or flow-morphed. Walks: a 12-drawing cycle held on twos with each drawing
placed so its planted foot stays where it was (full-body pass) and a knee-up tracking walk with the
set sliding behind. Real NASA video in every window and behind Part B. Cutaway = engraving cut-outs
in a paper theatre. Deterministic per frame.
"""
import json, math, os, subprocess, sys, time, random
import numpy as np, cv2, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import ease, noise1, col, P
import s5_stage as ST

W, H, FPS = 1920, 1080, 24
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
CX, FACES = f"{S}/cx/s5", f"{S}/s5/faces"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SL = ST.SL; DUR = SL["duration_s"]
LM = json.load(open(f"{S}/s5/lm_all.json"))
MARK = json.load(open(f"{S}/s5/setmarks.json"))

# ------------------------------------------------------------------ basics
def key_green(im):
    f = im.astype(np.float32) / 255
    d = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
    a = 1 - np.clip((d - 0.10) / 0.20, 0, 1)
    a = cv2.GaussianBlur(cv2.erode(a, np.ones((3, 3), np.uint8)), (0, 0), 0.7)
    f[..., 1] = np.minimum(f[..., 1], np.maximum(f[..., 0], f[..., 2]) + 0.03)
    return np.dstack([f[..., ::-1] * a[..., None], a]).astype(np.float32)
def over(dst, rgba): return dst * (1 - rgba[..., 3:4]) + rgba[..., :3]
def place(rgba, sx, src, dst, rot=0.0, sy=None, flip=False):
    sy = sx if sy is None else sy
    a = math.radians(rot); c, s_ = math.cos(a), math.sin(a)
    fx = -1 if flip else 1
    M = np.array([[c * sx * fx, -s_ * sy, 0], [s_ * sx * fx, c * sy, 0]], np.float64)
    M[:, 2] = np.array(dst) - M[:, :2] @ np.array(src)
    return cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
_IMG = {}
def pic(name):
    if name not in _IMG: _IMG[name] = key_green(cv2.imread(f"{CX}/{name}.png"))
    return _IMG[name]
def face(base, key):
    p = f"{FACES}/{base}__{key}.png"
    if not os.path.exists(p): return None
    if p not in _IMG: _IMG[p] = key_green(cv2.imread(p))
    return _IMG[p]
def bbox(name):
    a = pic(name)[..., 3] > 0.05; ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max(), ys.max()
def face_geo(name):
    """(face centre, face height) from landmarks; fallback from the figure's bounding box"""
    l = LM.get(name)
    if l:
        ey = (l["eye_l"][1] + l["eye_l"][3] + l["eye_r"][1] + l["eye_r"][3]) / 4
        return np.array(l["nose"]), max(10.0, l["chin"][1] - ey) * 1.0
    x0, y0, x1, y1 = bbox(name); hh = y1 - y0
    return np.array([(x0 + x1) / 2, y0 + hh * 0.09]), hh * 0.055

# ------------------------------------------------------------------ speech
CUES, ENV = {}, {}
import soundfile as sf
for l in SL["dialogue"]:
    p = f"{S}/s5/lips/{l['id']}.json"
    CUES[l["id"]] = [(c["start"], c["end"], c["value"]) for c in json.load(open(p))["mouthCues"]] if os.path.exists(p) else []
    a, sr = sf.read(l["src"], always_2d=True); a = a.mean(1); hop = sr // 48
    e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) for i in range(max(1, len(a) // hop))]); ENV[l["id"]] = e / (e.max() + 1e-9)
def speaking(who, t):
    for l in SL["dialogue"]:
        if l["who"] == who and l["start_s"] - 0.02 <= t < l["start_s"] + l["dur"] + 0.03: return l
    return None
BMAP = {"X": "X", "A": "X", "B": "C", "C": "C", "D": "E", "E": "E", "F": "F", "G": "C", "H": "C"}   # Baron A/D edits smeared the moustache: not used
def mouth(who, t):
    l = speaking(who, t)
    if not l: return "X", 0.0
    lt = t - l["start_s"]; v = "X"
    for c0, c1, vv in CUES[l["id"]]:
        if c0 <= lt < c1: v = vv; break
    if not CUES[l["id"]]:      # no Rhubarb track (the new laugh line): open/close on loudness
        e = ENV[l["id"]][min(len(ENV[l["id"]]) - 1, int(lt * 48))]; v = "D" if e > 0.5 else "C" if e > 0.2 else "X"
    e = float(ENV[l["id"]][min(len(ENV[l["id"]]) - 1, int(lt * 48))])
    if who == "baron": v = BMAP.get(v, "C")
    return v, e
def blink(t, seed):
    rng = random.Random(seed); bt = rng.uniform(0.5, 2.0)
    while bt < t + 1:
        if 0 <= t - bt < 0.125: return True
        bt += rng.uniform(2.2, 4.5)
    return False

def head_img(base, who, t, brows=(), seed=1, allow_blink=True):
    """the pose picture with its face set: mouth key + blink + brow keys (regions differ only)"""
    X = face(base, "X")
    if X is None: return pic(base)
    m, e = mouth(who, t)
    img = face(base, m) if m != "X" and face(base, m) is not None else X
    img = img.copy() if img is X else img.copy()
    for k, amt in brows:
        b = face(base, k)
        if b is not None and amt > 0.02: img += (b - X) * amt
    if allow_blink and blink(t, seed):
        b = face(base, "blink")
        if b is not None: img += (b - X)
    return np.clip(img, 0, 1)

FALLBACK = {"Jk_inb_point": "Jk_point", "Jk_inb_finger": "Jk_finger", "Mk_inb_up": "Mk_stampup"}
def pose_at(keys, t):
    cur, tk = keys[0][1], keys[0][0]
    for k in keys:
        if k[0] <= t: cur, tk = k[1], k[0]
        else: break
    if cur in FALLBACK and not os.path.exists(f"{CX}/{cur}.png"): cur = FALLBACK[cur]
    return cur, t - tk
def pop(dt):   # squash-and-settle after a pose change
    if dt < 0 or dt > 0.45: return 0.0
    return 0.05 * math.exp(-dt * 10) * math.cos(dt * 28)

# ------------------------------------------------------------------ sets and plates
class Plate:
    def __init__(self, p): self.cap = cv2.VideoCapture(p); self.n = int(self.cap.get(7)); self.pos = -2; self.f = None
    def frame(self, i):
        i = i % self.n
        if i != self.pos:
            if i != self.pos + 1: self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, f = self.cap.read(); self.f = f[:, :, ::-1].astype(np.float32) / 255; self.pos = i
        return self.f
PLATE = None
def plate_img(t, w_px, ox, oy, gain=1.25, speed=1.0):
    global PLATE
    if PLATE is None: PLATE = Plate(f"{S}/toon/plates/window.mp4")
    f = PLATE.frame(int(t * FPS * speed)); s = w_px / f.shape[1]
    return np.clip(cv2.warpAffine(f, np.float64([[s, 0, ox], [0, s, oy]]), (W, H), flags=cv2.INTER_LINEAR) * gain, 0, 1)
SET = {}
def set_world(name):
    if name in SET: return SET[name]
    im = cv2.imread(f"{CX}/{name}.png")[:, :, ::-1].astype(np.float32) / 255
    k = W / im.shape[1]; up = cv2.resize(im, (W, int(im.shape[0] * k)), interpolation=cv2.INTER_LANCZOS4)[:H]
    up = np.clip(up * 1.3 - cv2.GaussianBlur(up, (0, 0), 1.5) * 0.3, 0, 1)
    mk = MARK[name]
    lum = up.max(2); x0, y0, x1, y1 = [int(v * k) for v in mk["window_bbox"]]
    win = np.zeros((H, W), np.uint8); win[y0:y1, x0:x1] = lum[y0:y1, x0:x1] < 0.09
    n, lab, st, _ = cv2.connectedComponentsWithStats(win, 8)
    big = [i for i in range(1, n) if st[i, 4] > 2000]
    win = np.isin(lab, big).astype(np.uint8)
    win = cv2.GaussianBlur(cv2.dilate(win, np.ones((3, 3))).astype(np.float32), (0, 0), 1.2)
    fg = np.zeros((H, W), np.float32)
    for poly in mk.get("fg", []): cv2.fillPoly(fg, [(np.array(poly) * k).astype(np.int32)], 1.0)
    fg = cv2.GaussianBlur(fg, (0, 0), 1.0)
    SET[name] = (up, win, fg, k, (x0, y0, x1, y1)); return SET[name]
def set_bg(name, t, cam):
    up, win, fg, k, (x0, y0, x1, y1) = set_world(name)
    cx, cy, z = cam
    # plate: lit ground fills most of the glass, Earth above it; slower parallax than the set
    pw = (x1 - x0) * 1.7; par = 0.35
    pl = plate_img(t, pw, x0 - pw * 0.30 + (cx - W / 2) * par, y0 - pw * 0.5625 * 0.12 + (cy - H / 2) * par)
    world = up * (1 - win[..., None]) + pl * win[..., None]
    M = np.float64([[z, 0, W / 2 - cx * z], [0, z, H / 2 - cy * z]])
    img = cv2.warpAffine(world.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fgw = cv2.warpAffine(fg, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    fgi = cv2.warpAffine(up.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return img, fgw, fgi, M

def rim(layer, k=0.45, w=3, d=(1, -1)):
    a = layer[..., 3]; sh = np.zeros_like(a)
    dx, dy = int(d[0] * w), int(d[1] * w)
    sh[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = a[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    r = np.clip(a - sh, 0, 1) * a
    out = layer.copy(); out[..., :3] += cv2.GaussianBlur(r, (0, 0), 1.2)[..., None] * np.array([0.75, 0.88, 1.0], np.float32) * k
    return out
def contact(img, x, y, rx, ry, k=0.35):
    m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(x), int(y)), (max(1, int(rx)), max(1, int(ry))), 0, 0, 360, 1.0, -1)
    return img * (1 - k * cv2.GaussianBlur(m, (0, 0), max(1, ry) * 0.8)[..., None])

# ------------------------------------------------------------------ character placement
def char_layer(name, img, head_xy, head_h, t, seed, M=None, rot_extra=0.0, sq=0.0, flip=False):
    """place pose picture so its face centre lands on head_xy (world) at face height head_h (world)"""
    c, fh = face_geo(name)
    s = head_h / fh
    br = 0.005 * math.sin(t * 2 * math.pi / 3.4 + seed)
    rot = 0.5 * noise1(t, seed, 0.25) + rot_extra
    lay = place(img, s * (1 + sq * 0.6), c, head_xy, rot=rot, sy=s * (1 - sq + br), flip=flip)
    if M is not None and (abs(M[0, 0] - 1) > 1e-6 or abs(M[0, 2]) > 1e-6 or abs(M[1, 2]) > 1e-6):
        lay = cv2.warpAffine(lay, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return lay
def cam_of(shot, t):
    c = shot.get("cam", (W / 2, H / 2, 1.0)); c2 = shot.get("cam2", c)
    k = ease("io", (t - shot["start_s"]) / max(0.1, shot["end_s"] - shot["start_s"]))
    cx, cy, z = [a + (b - a) * k for a, b in zip(c, c2)]
    cx += 3 * noise1(t, 21, 0.13) / z; cy += 2 * noise1(t, 22, 0.11) / z
    if 0 <= t - ST.STAMP < 0.4:
        a = 12 * math.exp(-(t - ST.STAMP) * 8) / z; cx += a * math.sin((t - ST.STAMP) * 70); cy += a * math.cos((t - ST.STAMP) * 83)
    hw, hh = W / 2 / z, H / 2 / z
    return min(max(cx, hw), W - hw), min(max(cy, hh), H - hh), z

# ------------------------------------------------------------------ walks
def cut_sheet(name, n):
    im = cv2.imread(f"{CX}/{name}.png"); f = im.astype(np.float32) / 255
    a = ((f[..., 1] - np.maximum(f[..., 0], f[..., 2])) < 0.2).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); a2 = cv2.dilate(a, np.ones((9, 9), np.uint8))
    k, lab, st, _ = cv2.connectedComponentsWithStats(a2, 8)
    idx = sorted(sorted(range(1, k), key=lambda i: -st[i, 4])[:n], key=lambda i: st[i, 0])
    out = []
    for i in idx:
        x, y, w, h = st[i, :4]; m = (lab == i)
        c = im.copy(); c[~m] = (0, 255, 0)
        out.append(key_green(c[max(0, y - 10):y + h + 10, max(0, x - 10):x + w + 10]))
    return out
WALK = None
def walk_setup():
    global WALK
    if WALK: return WALK
    dr = cut_sheet("J5_walkA", 6) + cut_sheet("J5_walkB", 6)
    # the two sheets came out at different sizes: bring every drawing to one figure height first
    hs = [float(np.ptp(np.nonzero(d[..., 3] > 0.05)[0])) for d in dr]; href = float(np.median(hs[:6]))
    dr = [cv2.resize(d, None, fx=href / h, fy=href / h, interpolation=cv2.INTER_AREA) for d, h in zip(dr, hs)]
    info = []
    for d in dr:
        a = d[..., 3] > 0.05; ys, xs = np.nonzero(a); y0, y1 = ys.min(), ys.max()
        top = a[y0:y0 + int((y1 - y0) * 0.12)]; hx = float(np.nonzero(top.any(0))[0].mean())
        prof = a[y1 - 7:y1 + 1].any(0).astype(np.float32)
        u = np.zeros(1600, np.float32); off = int(800 - hx); u[off:off + len(prof)] = prof
        info.append(dict(hx=hx, gy=float(y1), h=float(y1 - y0), prof=u))
    # planted-foot shift between consecutive drawings (1-D overlap of the ground-contact rows)
    D, ov = [], []
    for k in range(12):
        A_, B_ = info[k]["prof"], info[(k + 1) % 12]["prof"]; best = (0, 0)
        for d in range(0, 160):
            sc = (A_[d:] * B_[:len(B_) - d]).sum() if d else (A_ * B_).sum()
            if sc > best[0]: best = (sc, d)
        D.append(best[1]); ov.append(best[0])
    hmean = np.mean([i["h"] for i in info])
    stride = max(sum(D), hmean * 0.72)          # one cycle travels about 0.7 body heights
    miss = [k for k in range(12) if ov[k] < 5]
    if miss:
        rest = (stride - sum(D[k] for k in range(12) if k not in miss)) / len(miss)
        for k in miss: D[k] = max(0, rest)
    D = [min(d, 80.0) for d in D]                # a contact switch with no shared foot can mis-match: cap it
    WALK = dict(dr=dr, info=info, D=D, stride=float(sum(D)), h=hmean)
    json.dump({"delta_px": [float(d) for d in D], "stride_px": float(sum(D)), "overlap": [float(o) for o in ov]}, open(f"{OUT}/walk_measure.json", "w"))
    return WALK
def walk_full_layer(t, t0, x0, ground, height):
    w = walk_setup(); s = height / w["h"]
    n = int((t - t0) * 12)                       # drawing index on twos (12 per second)
    k = n % 12; cyc = n // 12
    bx = cyc * w["stride"] + sum(w["D"][:k])      # body position of drawing n (sheet px)
    i = w["info"][k]
    return place(w["dr"][k], s, (i["hx"], i["gy"]), (x0 + bx * s, ground)), x0 + bx * s, s * w["stride"] * 12 / 12
KNEE = None
def knee_layer(t, x, ytop, height):
    global KNEE
    if KNEE is None: KNEE = cut_sheet("J5_walkknee", 6)
    n = int(t * 12) % 6; d = KNEE[n]; a = d[..., 3] > 0.05; ys, xs = np.nonzero(a)
    hx = float(np.nonzero(a[ys.min():ys.min() + 40].any(0))[0].mean())
    hh = max(1, ys.max() - ys.min()); s = height / hh
    return place(d, s, (hx, ys.min()), (x, ytop + 6 * math.sin(t * 2 * math.pi * 2)))

# ------------------------------------------------------------------ Part A
def mira_layer(t, shot, M, head_xy, head_h, cu=None):
    name, dt = pose_at(ST.MIRA, t)
    base = cu or name
    img = head_img(base, "mira", t, brows=brows_for(shot, t), seed=8)
    return char_layer(base, img, head_xy, head_h, t, 8, M, sq=pop(dt) if not cu else 0.0)
def jax_layer(t, shot, M, head_xy, head_h, cu=None, rot_extra=0.0):
    name, dt = pose_at(ST.JAX, t)
    base = cu or name
    img = head_img(base, "jax", t, brows=brows_for(shot, t), seed=5)
    return char_layer(base, img, head_xy, head_h, t, 5, M, sq=pop(dt) if not cu else 0.0, rot_extra=rot_extra)
def brows_for(shot, t):
    out = []
    for at, k, amt in ST.BROW.get(shot["id"], []):
        if t >= at: out = [(kk, a) for kk, a in out if kk != k] + [(k, amt * ease("snap", (t - at) / 0.25))]
    return out
def wide_A(t, shot):
    cam = cam_of(shot, t); img, fgw, fgi, M = set_bg("S5_wide2", t, cam)
    mk = MARK["S5_wide2"]; k = W / 1672
    # tiny Baron far down the hall on the scale, a little drone circling him
    bn = "B5_arms" if t >= ST.L("3-25") - 0.2 else "B5_scale"
    bx, by = [v * k for v in mk["baron_feet"]]; bh = mk["baron_h"] * k
    bb = bbox(bn); s = bh / (bb[3] - bb[1])
    hop = 3 * abs(math.sin(t * 3.1)) if bn == "B5_scale" else 0
    lay = place(pic(bn), s, ((bb[0] + bb[2]) / 2, bb[3]), (bx, by - hop))
    img = over(img, cv2.warpAffine(lay, M, (W, H), borderValue=(0, 0, 0, 0)))
    dx, dy = bx + 34 * math.cos(t * 2.2), by - bh * 0.8 + 10 * math.sin(t * 4.4)
    p = M @ np.array([dx, dy, 1.0]); cv2.circle(img, (int(p[0]), int(p[1])), max(2, int(5 * cam[2])), (0.35, 0.38, 0.42), -1)
    if int(t * 3) % 2: cv2.circle(img, (int(p[0]), int(p[1])), max(1, int(2 * cam[2])), (1.0, 0.3, 0.2), -1)
    # Mira behind her counter (and Noakes in the last wide)
    mx, my = [v * k for v in mk["mira_head"]]
    img = over(img, rim(mira_layer(t, shot, M, (mx, my), mk["mira_face_h"] * k), 0.4))
    if shot["id"] == "A19":
        name = "N5_lean"; img = over(img, char_layer(name, head_img(name, "noakes", t, seed=3), (mx + 90 * k, my - 20 * k), mk["mira_face_h"] * k * 1.05, t, 3, M))
    img = img * (1 - fgw) + fgi * fgw
    # Jax
    if shot["kind"] == "wide" and shot["id"] == "A01":
        jx, jy = [v * k for v in mk["jax_feet"]]; jh = mk["jax_h"] * k
        bb = bbox("J5_stop"); s = jh / (bb[3] - bb[1])
        look = 1 if (ST.L("3-01") + 0.8 < t < ST.L("3-02")) else 0   # looks round: turns his head away and back
        lay = place(pic("J5_stop"), s, ((bb[0] + bb[2]) / 2, bb[3]), (jx, jy), rot=0.5 * noise1(t, 5, 0.25), flip=bool(look))
        lay = cv2.warpAffine(lay, M, (W, H), borderValue=(0, 0, 0, 0))
        fp = M @ np.array([jx, jy, 1.0]); img = contact(img, fp[0], fp[1], 60 * cam[2], 10 * cam[2])
        img = over(img, rim(lay))
    if shot["kind"] == "walk_full":
        jx, jy = [v * k for v in mk["walk_start"]]; jh = mk["jax_h"] * k
        lay, xw, _ = walk_full_layer(t, shot["start_s"], jx, jy, jh)
        lay = cv2.warpAffine(lay, M, (W, H), borderValue=(0, 0, 0, 0))
        fp = M @ np.array([xw, jy, 1.0]); img = contact(img, fp[0], fp[1], 60 * cam[2], 10 * cam[2])
        img = over(img, rim(lay))
    return img
def walk_track(t, shot):
    # knee-up tracking: Jax stays in frame, the hall slides past; he arrives at the counter on "Seized"
    t_arr = ST.L("3-04", 0.93)
    sp = 210.0                                        # world px per second of slide (matches the stroll)
    u = min(t, t_arr) - shot["start_s"]
    cx = 420 + sp * u - (sp * 0.5 * max(0, u - (t_arr - shot["start_s"] - 0.8)) ** 2 / 0.8 if u > t_arr - shot["start_s"] - 0.8 else 0)
    cam = (cx, 520, 1.75)
    img, fgw, fgi, M = set_bg("S5_wide2", t, cam)
    if t < t_arr:
        lay = knee_layer(t, 760, 150, 1000)
        img = over(img, rim(lay))
    else:
        img = over(img, rim(jax_layer(t, shot, None, (760, 300), 80)))
    return img * (1 - fgw) + fgi * fgw
def two_shot(t, shot):
    mk = MARK["S5_wide2"]; k = W / 1672
    cam = cam_of(shot, t); img, fgw, fgi, M = set_bg("S5_wide2", t, cam)
    mx, my = [v * k for v in mk["mira_head"]]
    img = over(img, rim(mira_layer(t, shot, M, (mx, my), mk["mira_face_h"] * k), 0.4))
    if shot["kind"] == "two_shot_noakes":
        name, dt = pose_at(ST.NOAKES, t)
        brows = []
        im = head_img(name, "noakes", t, seed=3, allow_blink=True)
        if shot["id"] == "A20" and t > shot["start_s"] + 0.5:
            b = face(name, "blink")
            if b is not None: im = b
        img = over(img, rim(char_layer(name, im, (mx + 120 * k, my + 5 * k), mk["mira_face_h"] * k * 1.1, t, 3, M, sq=pop(dt)), 0.4))
        return img * (1 - fgw) + fgi * fgw
    img = img * (1 - fgw) + fgi * fgw
    jx, jy = [v * k for v in mk["jax_head_two"]]
    name, dt = pose_at(ST.JAX, t)
    if name == "Jk_salute" and t > ST.STAMP + 0.9: jx -= 260 * ease("in", (t - ST.STAMP - 1.2) / 0.8)   # he goes
    return over(img, rim(jax_layer(t, shot, M, (jx, jy), mk["mira_face_h"] * k * 1.05)))
def cu(t, shot):
    base = ST.CU[shot["id"]]; who = "mira" if base.startswith("M") else "jax"
    mk = MARK["S5_wide2"]; k = W / 1672
    # background: the warm hall wall and lamps beside the window, pushed in and soft
    cx, cy = [v * k for v in mk["cu_bg_mira" if who == "mira" else "cu_bg_jax"]]
    img, _, _, _ = set_bg("S5_wide2", t, (cx, cy, 2.2)); img = cv2.GaussianBlur(img, (0, 0), 3.0)
    l = speaking(who, t); e = 0.0
    if l: e = float(ENV[l["id"]][min(len(ENV[l["id"]]) - 1, int((t - l["start_s"]) * 48))])
    tilt = 0.8 * noise1(t, 4, 0.3) + 2.0 * e * math.sin(t * 6.0)
    img_c = head_img(base, who, t, brows=brows_for(shot, t), seed=5 if who == "jax" else 8)
    c, fh = face_geo(base); s = 330 / fh
    x = 760 if who == "jax" else 1160
    if base.endswith("front"): x = 960
    lay = place(img_c, s, c, (x, 470 + 3 * e), rot=tilt, sy=s * (1 + 0.006 * math.sin(t * 2 * math.pi / 3.2)))
    return over(img, rim(lay, 0.45, 4))

# ------------------------------------------------------------------ inserts (drawn in code)
def text(cv, s, x, y, size, c, face_="DejaVu Sans Mono", bold=False):
    f = skia.Font(skia.Typeface(face_, skia.FontStyle.Bold() if bold else skia.FontStyle.Normal()), size)
    cv.drawString(s, x, y, f, P(c))
def surf_img(draw):
    s = skia.Surface(W, H); cv = s.getCanvas(); draw(cv)
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32) / 255
def insert(t, shot):
    dt = t - shot["start_s"]; d = shot["desc"]
    if "screen" in d:
        def dr(cv):
            cv.clear(col("#3a2a1c")); cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(160, 90, 1760, 990), 40, 40), P(col("#b8893c")))
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(210, 140, 1710, 940), 24, 24), P(col("#0d2b2a")))
            off = -300 * (1 - ease("io", (dt - 0.3) / 1.1))
            rows = [("", False)] * 3 + [("", False)] * 3 + [("VALE, JAX.", True), ("MASTER, COURIER CLASS.", True), ("RECORD BEGINS: SEVEN YEARS AGO", True), ("ROUTES: 1,204   CLAIMS: 0", True)]
            for i, (s_, filled) in enumerate(rows):
                y = 200 + i * 95 + off
                if 150 < y < 930:
                    cv.drawRect(skia.Rect(280, y - 50, 1640, y + 22), P(col("#1d4d48", 255), 2))
                    if filled: text(cv, s_, 300, y, 52, col("#ffcf6a"))
            if int(t * 2) % 2: cv.drawRect(skia.Rect(300, 850, 330, 900), P(col("#ffcf6a")))
        return surf_img(dr)
    if "notebook" in d:
        prog = ease("lin", dt / 2.8)
        def dr(cv):
            cv.clear(col("#5b3b26")); cv.save(); cv.rotate(-3); cv.drawRect(skia.Rect(260, 60, 1680, 1060), P(col("#f2e6c8"))); cv.restore()
            for i in range(9): cv.drawLine(300, 170 + i * 92, 1640, 140 + i * 92, P(col("#b9c7d6"), 2))
            old = ["37. GRIMALDI DRY DOCK", "38. THE LANTERN STEPS", "39. NOLL'S CROSSING", "40. ST. ULRIC'S POST"]
            for i, s_ in enumerate(old):
                text(cv, s_ + "    OWNER: —", 330, 160 + i * 92 - i * 4, 40, col("#2a2f55"), "DejaVu Serif")
            s_ = "41. THE SILVER HATCHET.   OWNER: —"; n = int(len(s_) * prog)
            text(cv, s_[:n], 330, 160 + 4 * 92 - 16, 46, col("#1c2148"), "DejaVu Serif")
            f = skia.Font(skia.Typeface("DejaVu Serif"), 46); px = 330 + f.measureText(s_[:n])
            cv.drawLine(px, 520, px + 140, 330, P(col("#2b1d14"), 16)); cv.drawLine(px, 520, px + 20, 495, P(col("#c9a040"), 6))
        return surf_img(dr)
    def dr(cv):  # the board
        cv.clear(col("#173a3c")); cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(140, 160, 1780, 920), 30, 30), P(col("#b8893c")))
        cv.drawRect(skia.Rect(190, 210, 1730, 870), P(col("#0f1f22")))
        text(cv, "RIM PORT CUSTOMS", 520, 330, 78, col("#f3e2b5"), "DejaVu Sans", True)
        text(cv, "DAYS WITHOUT INCIDENT", 470, 450, 70, col("#f3e2b5"), "DejaVu Sans")
        digits = "1,094" if dt > 0.35 else "1,093"
        for i, ch in enumerate(digits):
            x = 560 + i * 165; cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, 540, x + 140, 800), 12, 12), P(col("#2b2b2b")))
            cv.drawLine(x, 670, x + 140, 670, P(col("#111111"), 4))
            sq = 1.0 if not (i == 4 and 0.2 < dt < 0.35) else abs(math.cos((dt - 0.2) / 0.15 * math.pi))
            cv.save(); cv.translate(x + 70, 670); cv.scale(1, sq); text(cv, ch, -45, 80, 210, col("#f7f3e8"), "DejaVu Sans", True); cv.restore()
    return surf_img(dr)

# ------------------------------------------------------------------ Part B
def rim_plate(t, zoom=1.0, blur=0.0):
    # frame on the plate's lit side: x 0-55%, y 13-68% of the plate (sunlit ground below, Earth above the limb)
    pw = W / 0.55 * zoom; ph = pw * 0.5625
    img = plate_img(t, pw, -(pw - W / 0.55) * 0.35, -0.13 * ph - (ph - H / 0.55 * 0.5625 * 0) * 0 - 60 * (zoom - 1), gain=1.3, speed=0.5)
    return cv2.GaussianBlur(img, (0, 0), blur) if blur else img
def drift(t, seed, amp=6):
    return amp * math.sin(t * 2 * math.pi / 5.3 + seed), amp * 0.7 * math.sin(t * 2 * math.pi / 4.1 + seed * 2)
def rim_shot(t, shot):
    k = shot["kind"]
    if k == "rim_earth": return rim_plate(t)
    if k in ("rim_wide", "rim_two"):
        z = 1.0 if k == "rim_wide" else 1.25
        img = rim_plate(t, z, 0 if k == "rim_wide" else 1.2)
        rock = pic("S5_rock"); rb = bbox("S5_rock")
        rw = 1100 if k == "rim_wide" else 1900
        s = rw / (rb[2] - rb[0]); ry = 1000 if k == "rim_wide" else 1200
        img = over(img, place(rock, s, ((rb[0] + rb[2]) / 2, rb[1] + (rb[3] - rb[1]) * 0.18), (960, ry - (rb[3] - rb[1]) * s * 0.0 - 220 * (1 if k == "rim_wide" else 0.6))))
        seat_y = ry - 220 * (1 if k == "rim_wide" else 0.6)
        fig_h = 430 if k == "rim_wide" else 1050
        for name, x, who, seed in (("JS_seat", 960 - (210 if k == "rim_wide" else 380), "jax", 5), ("BS_seat", 960 + (210 if k == "rim_wide" else 380), "baron", 7)):
            dx, dy = drift(t, seed, 3)
            bb = bbox(name); s = fig_h / (bb[3] - bb[1])
            im = head_img(name, who, t, seed=seed) if k == "rim_two" else pic(name)
            lay = place(im, s, ((bb[0] + bb[2]) / 2, bb[1] + (bb[3] - bb[1]) * 0.78), (x + dx, seat_y + dy), rot=0.6 * noise1(t, seed, 0.2))
            img = over(img, rim(lay, 0.5, 3, (-1, -1)))
        return img
    who = "baron" if k == "rim_baron" else "jax"
    base = "BS_cu" if who == "baron" else "JS_cu"
    img = rim_plate(t, 1.15, 2.0)
    brows = []
    if shot["id"] == "B05" and t < ST.L("21-10") + 0.3: brows = [("brow_up", ease("snap", (t - shot["start_s"]) / 0.3))]
    if who == "jax" and (t < ST.L("21-16") + 2 and shot["id"] == "B07"): brows = [("smile", 0.0)]
    lo, hi = ST.LAUGH
    dx, dy = drift(t, 3 if who == "baron" else 4, 5)
    rot = 0.9 * math.sin(t * 2 * math.pi / 6.0)
    if who == "jax" and lo <= t <= hi:
        im = face("JS_cu", "X") if face("JS_cu", "X") is not None else pic("JS_cu")
        lp = pic("JS_laugh"); kk = (t - lo)
        im = lp
        dy += -14 * min(1, kk / 0.2) + 7 * math.sin(kk * 2 * math.pi * 5.5); rot += -3.5 * min(1, kk / 0.2)
    else:
        im = head_img(base, who, t, brows=brows, seed=6 if who == "baron" else 4)
        if who == "jax" and t > hi and shot["id"] in ("B09",): im = head_img(base, who, t, brows=[("smile", 1.0)], seed=4)
    c, fh = face_geo(base if not (who == "jax" and lo <= t <= hi) else "JS_cu"); s = 300 / fh
    x = 1120 if who == "baron" else 800
    lay = place(im, s, c, (x + dx, 470 + dy), rot=rot)
    img = over(img, rim(lay, 0.5, 4, (-1, -1)))
    if who == "jax" and lo <= t <= hi + 0.6:           # breath fog on the inside of the glass
        fog = np.zeros((H, W), np.float32); cv2.ellipse(fog, (int(x + dx + 40), int(470 + dy + 260)), (240, 90), 0, 0, 360, 1.0, -1)
        fog = cv2.GaussianBlur(fog, (0, 0), 40) * 0.22 * min(1, (t - lo) / 0.5) * max(0, 1 - max(0, t - hi) / 0.6)
        img = img * (1 - fog[..., None]) + fog[..., None] * 0.92
    return img

# ------------------------------------------------------------------ cutaway: paper theatre
def cw(name, flip=False):
    key = name + ("_f" if flip else "")
    if key not in _IMG:
        im = pic(name); _IMG[key] = im[:, ::-1].copy() if flip else im
    return _IMG[key]
def paper(img_rgba, sx, x, y, rot=0.0, shadow=True):
    lay = place(img_rgba, sx, (img_rgba.shape[1] / 2, img_rgba.shape[0] / 2), (x, y), rot=rot)
    if shadow:
        sh = np.zeros_like(lay); sh[..., 3] = lay[..., 3] * 0.35; sh = np.roll(np.roll(sh, 10, 0), 12, 1)
        return sh, lay
    return None, lay
def arc(p0, p1, h, u):
    u = min(max(u, 0), 1); return p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - h * 4 * u * (1 - u)
def cutaway(t, home=False):
    C = ST.CUT
    bgimg = pic("CW_bg")[..., :3]
    dt = t - C["cutaway starts: 'when it fired'"]
    pan = 40 * dt
    sb = W * 1.2 / bgimg.shape[1]
    img = cv2.warpAffine(bgimg, np.float64([[sb, 0, -40 - pan * 0.25], [0, sb, -50]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    layers = []
    sway = lambda sd: 2.0 * math.sin(t * 4.2 + sd)
    if home:
        u = (t - C["rode it home (2 s insert inside B08)"]) / 2.0
        x, y = arc((1500, 380), (300, 520), 120, u)
        layers.append(paper(cw("CW_land"), 0.55, x, y, sway(1)))
    else:
        t_fire, t_ast, t_doubt = C["jumps on the ball"] - 0.5, C["astride, like a horse but rounder"], C["doubts"]
        t_pass, t_chg = C["the other ball passes"], C["changed (the swap, mid-air)"]
        # cannon (mid layer, slides with less parallax), fires at t_fire
        cn = cw("CW_cannon"); s = 760 / cn.shape[1]
        layers.append(paper(cn, s, 430 - pan * 0.7, 760, 0))
        if t_fire <= t < t_fire + 0.15: img = np.clip(img + 0.35, 0, 1)
        # the hussar's flight
        if t < t_fire: pass
        elif t < t_fire + 0.7:
            u = (t - t_fire) / 0.7; x, y = arc((560 - pan * 0.7, 560), (900, 330), 160, u)
            layers.append(paper(cw("CW_leap"), 0.55, x, y, sway(0) - 10 * (1 - u)))
        elif t < t_chg - 0.35:
            u = (t - t_fire - 0.7) / max(0.1, (t_chg - 0.35) - (t_fire + 0.7))
            x, y = 900 + 260 * u, 330 + 30 * math.sin(u * 6) + 10 * math.sin(t * 3)
            pose = "CW_doubt" if t >= t_doubt else "CW_ride"
            layers.append(paper(cw(pose), 0.6, x, y, sway(1)))
            if t >= t_pass:                                    # the Turkish ball comes the other way
                v = (t - t_pass) / max(0.1, (t_chg - 0.35) - t_pass)
                bx = 2100 - (2100 - (x + 40)) * ease("out", v); layers.append(paper(cw("CW_ball"), 0.42, bx, y + 120, 0))
        else:
            tt = t - (t_chg - 0.35)
            bx0 = 1160
            # his old ball keeps going right, empty; the other ball goes left
            layers.append(paper(cw("CW_ball", flip=True), 0.42, bx0 + 60 + 300 * tt, 360 + 20 * tt, 0))
            ox = bx0 + 40 - 260 * tt
            if tt < 1.25: layers.append(paper(cw("CW_ball"), 0.42, ox, 450, 0))   # (the landing drawing carries its own ball)
            if tt < 0.35:          # anticipation: crouch
                layers.append(paper(cw("CW_crouch"), 0.6, bx0 + 300 * tt * 0.3, 330 + 12 * ease("out", tt / 0.35), sway(2)))
            elif tt < 1.25:        # the leap (the drawing has the hat lifting off and lingering above his head)
                u = ease("io", (tt - 0.35) / 0.9); x, y = arc((bx0 + 40, 300), (ox, 330), 170, u)
                layers.append(paper(cw("CW_jump"), 0.6, x, y, 8 - 16 * u))
            else:                  # landing with a bow, hat swept off (settles with a bounce)
                layers.append(paper(cw("CW_land"), 0.6, ox, 300 + 14 * math.exp(-(tt - 1.25) * 6) * math.cos((tt - 1.25) * 20), sway(3)))
    for sh, lay in layers:
        if sh is not None: img = over(img, sh)
        img = over(img, lay)
    # paper-theatre proscenium: cream card frame with a soft shadow
    fr = np.zeros((H, W), np.float32); fr[:44] = 1; fr[-44:] = 1; fr[:, :44] = 1; fr[:, -44:] = 1
    shd = cv2.GaussianBlur(fr, (0, 0), 14) * 0.45
    img = img * (1 - shd[..., None])
    img = img * (1 - fr[..., None]) + fr[..., None] * np.array([0.93, 0.86, 0.70])
    return img

# ------------------------------------------------------------------ title
def title(t, shot):
    img = rim_plate(t, 1.0)
    def dr(cv):
        cv.clear(skia.ColorTRANSPARENT)
        f = skia.Font(skia.Typeface("DejaVu Serif", skia.FontStyle.Bold()), 74); s = "LATER  —  THE OUTER RIM"
        x = (W - f.measureText(s)) / 2
        cv.drawString(s, x + 4, 560, f, P(col("#000000", 180))); cv.drawString(s, x, 556, f, P(col("#f6e7c2")))
    s = skia.Surface(W, H); cv = s.getCanvas(); dr(cv)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32) / 255
    k = min(1, (t - shot["start_s"]) / 0.3, (shot["end_s"] - t) / 0.3)
    return img * (1 - a[..., 3:4] * k) + a[..., :3] * a[..., 3:4] * k

# ------------------------------------------------------------------ frame
SHOTS = SL["shots"]
STAGE = {  # camera per shot (centre x, y on the set at 1920 scale, zoom) -> filled from setmarks
}
def shot_at(t):
    for s in SHOTS:
        if s["start_s"] <= t < s["end_s"]: return s
    return SHOTS[-1]
VIG = None
def finish(img, t):
    global VIG
    x = np.clip(img, 0, 1); lum = x.mean(2, keepdims=True); x = lum + (x - lum) * 1.05
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        VIG = (1 - 0.12 * np.clip((((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) * 0.6, 0, 1))[..., None]
    x = x * VIG + cv2.resize(np.random.default_rng(int(t * FPS) + 3).normal(0, 0.008, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None]
    out = np.clip(x * 255 + 0.5, 0, 255).astype(np.uint8)
    l = None
    for ln in SL["dialogue"]:
        if ln["start_s"] - 0.05 <= t < ln["start_s"] + ln["dur"] + 0.25 and not ln["new_line"]: l = ln
    if l:
        s = skia.Surface(W, H); cv = s.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
        f = skia.Font(skia.Typeface("DejaVu Sans"), 32); tw = f.measureText(l["text"])
        cv.drawString(l["text"], (W - tw) / 2, H - 52, f, P(col("#000000", 220), 6)); cv.drawString(l["text"], (W - tw) / 2, H - 52, f, P(col("#ffffff")))
        a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32); al = a[..., 3:4] / 255
        out = (out * (1 - al) + a[..., :3] * al).astype(np.uint8)
    return out
def frame(t):
    sh = shot_at(t); k = sh["kind"]
    cams = MARK["cams"]
    if sh["id"] in cams: sh = dict(sh, cam=tuple(cams[sh["id"]][0]), cam2=tuple(cams[sh["id"]][1]))
    home = ST.CUT["rode it home (2 s insert inside B08)"]
    if k == "cutaway": img = cutaway(t)
    elif home <= t < home + 2.0: img = cutaway(t, home=True)
    elif k in ("wide", "walk_full"): img = wide_A(t, sh)
    elif k == "walk_track": img = walk_track(t, sh)
    elif k.startswith("two_shot"): img = two_shot(t, sh)
    elif k.startswith("cu_"): img = cu(t, sh)
    elif k == "insert": img = insert(t, sh)
    elif k == "title": img = title(t, sh)
    else: img = rim_shot(t, sh)
    out = finish(img, t)
    if t < 0.4: out = (out * (t / 0.4)).astype(np.uint8)
    if DUR - t < 0.8: out = (out * max(0, (DUR - t) / 0.8)).astype(np.uint8)
    return out

def chunk(args):
    a, b, fn = args; cv2.setNumThreads(1)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-threads", "1", fn], stdin=subprocess.PIPE)
    c0 = time.process_time()
    for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); return time.process_time() - c0

if __name__ == "__main__":
    args = sys.argv[2:]
    if "--still" in args:
        for tt in args[args.index("--still") + 1:]:
            cv2.imwrite(f"{OUT}/still_{float(tt):07.2f}.jpg", cv2.cvtColor(frame(float(tt)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
        sys.exit(0)
    nf = int(round(DUR * FPS)); a0, b0 = 0, nf
    if "--frames" in args: a0, b0 = map(int, args[args.index("--frames") + 1].split(":"))
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 4
    nch = workers * 6; sz = math.ceil((b0 - a0) / nch)
    jobs = [(a0 + i * sz, min(b0, a0 + (i + 1) * sz), f"{OUT}/seg_{i:03d}.mp4") for i in range(nch) if a0 + i * sz < b0]
    import multiprocessing as mpc
    w0 = time.time()
    with mpc.get_context("spawn").Pool(workers) as pool: cpu = pool.map(chunk, jobs)
    open(f"{OUT}/segs.txt", "w").write("".join(f"file '{os.path.basename(j[2])}'\n" for j in jobs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/segs.txt", "-c", "copy", f"{OUT}/picture.mp4"], check=True)
    json.dump({"frames": b0 - a0, "wall_s": round(time.time() - w0, 1), "cpu_s": round(sum(cpu), 1), "cpu_s_per_video_s": round(sum(cpu) / ((b0 - a0) / FPS), 1)}, open(f"{OUT}/render.json", "w"))
    print("done")
