#!/usr/bin/env python3
"""TEST 4 renderer: painted pose-library puppets over real NASA video.

usage: toon4.py SHOTLIST.json OUTDIR [--still T ...] [--workers 4] [--frames a:b]

Characters are libraries of PAINTED POSE PICTURES (one picture per held pose, chroma green, cut by
key). Between poses: snappy pose-to-pose swaps (hard cut + squash/settle pop; optional dissolve), and on top
of every pose the painted face moves (Rhubarb mouths with jaw warp, blinks, eye darts, head
tilt/nod warp — engine copied from test 1, paintface.py), plus body breathing, lean, sway.
Walks play a painted 6-drawing walk cycle. Sets are paintings with the NASA plate keyed into the
black window glass; counters are cut out as a foreground layer.
"""
import json, math, os, subprocess, sys, time, random
import numpy as np, cv2, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paintface as pf
from rig import Channels, ease, noise1, col, P

W, H, FPS = 1920, 1080, 24
SL = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
VARS = SL["vars"]
def path(p):
    for k, v in VARS.items(): p = p.replace("${%s}" % k, v)
    return p
RIGS = json.load(open(path(SL["rigs"])))

# ------------------------------------------------------------------ speech (test-1 format)
import soundfile as sf
cue_lines = []
for ln in SL["dialogue"]:
    j = json.load(open(path(ln["lips"])))
    a, sr = sf.read(path(ln["src"]), always_2d=True); a = a.mean(1)
    hop = sr // 48; n = max(1, len(a) // hop)
    e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    e = (e / (e.max() + 1e-9)).tolist()
    cue_lines.append({"speaker": ln["who"], "start_s": ln["start_s"], "dur": ln["dur"], "env": e,
                      "cues": [{"t0": c["start"], "t1": c["end"], "v": c["value"]} for c in j["mouthCues"]]})
SPEECH = pf.Speech({"lines": cue_lines})
SPEECH.SHAPES = dict(pf.Speech.SHAPES)

# ------------------------------------------------------------------ poses
POSES = {}
def pose(name):
    if name in POSES: return POSES[name]
    r = dict(RIGS["poses"][name]); r["src"] = path(r["src"])
    r.setdefault("key", {"type": "green", "t0": 0.10, "t1": 0.30})
    r.setdefault("style", "ink"); r.setdefault("open_gain", 1.9); r.setdefault("ink_w", 1.4)
    if "eyes" in r:
        (ex0, ey0, _, _), (ex1, ey1, _, _) = r["eyes"]
        cx, cy, rx, ry = r["head"]
        r["face"] = [int(cx - rx * 1.05), int(cy - ry * 1.05), int(cx + rx * 1.05), int(r["chin"] + ry * 0.25)]
        r["parts"] = [{"name": "head", "roi": [int(cx - rx * 1.6), int(cy - ry * 1.5), int(cx + rx * 1.6), int(r["neck"][1] + ry * 0.2)],
                       "pivot": r["neck"], "region": [cx, cy, rx * 1.15, ry * 1.2], "feather": 0.5, "sway": 1.2, "talk": 2.4, "nod": 2.5}]
    if "parts" in r:
        hh_, ww_ = cv2.imread(r["src"]).shape[:2]
        def clamp(b): return [max(0, b[0]), max(0, b[1]), min(ww_, b[2]), min(hh_, b[3])]
        r["face"] = clamp(r["face"]); r["parts"][0]["roi"] = clamp(r["parts"][0]["roi"])
    pp = pf.Puppet(r, VARS, sum(map(ord, name)) % 1000)
    # knee-up / chest-up pictures end in a straight cut: continue the bottom rows downward so the
    # cut never shows when poses are aligned at the neck
    if r.get("extend", 0):
        h0 = pp.img.shape[0]
        pp.img = np.pad(pp.img, ((0, int(r["extend"])), (0, 0), (0, 0)), mode="edge")
        ext = pp.img[h0 - 6:]
        pp.img[h0 - 6:] = cv2.GaussianBlur(ext, (0, 0), sigmaX=9, sigmaY=0.1)   # plain cloth, not streaks
        a = pp.img[h0 - 6:, :, 3:4]; pp.img[h0 - 6:, :, :3] *= 0.92               # a touch darker = in shadow
        pp.h = pp.img.shape[0]
    POSES[name] = (r, pp)
    return POSES[name]

def affine(sx, sy, rot, a_src, a_dst):
    a = math.radians(rot); c, s = math.cos(a), math.sin(a)
    M = np.array([[c * sx, -s * sy, 0], [s * sx, c * sy, 0]], np.float64)
    M[:, 2] = np.array(a_dst) - M[:, :2] @ np.array(a_src)
    return M

def compose(A, B):   # A after B
    return (np.vstack([A, [0, 0, 1]]) @ np.vstack([B, [0, 0, 1]]))[:2]

# ------------------------------------------------------------------ channels
CH = {cid: Channels(c["keys"], c.get("defaults", {})) for cid, c in SL["characters"].items()}
def last_switch(cid, name, t):
    ks = SL["characters"][cid]["keys"].get(name, [])
    prev, tk = ks[0][1] if ks else None, -99
    for k in ks:
        if k[0] <= t:
            if k[1] != prev: tk = k[0]
            prev_val = prev; prev = k[1]
        else: break
    # previous value before the last switch
    pv = None
    for k in ks:
        if k[0] < tk: pv = k[1]
    return tk, pv

def char_layer(cid, t, place, camM, speak_id):
    ch = CH[cid]; c = SL["characters"][cid]
    pname = ch("pose", t)
    walk = c.get("walk")
    if pname == "walk" and walk:
        tt = (t - walk["t0"]) / (walk["t1"] - walk["t0"])
        dist = abs(ch("dx", t) - walk["x0"])
        pname = walk["frames"][int(dist / walk["stride"] * len(walk["frames"]) + walk.get("phase", 0)) % len(walk["frames"])]
    tk, prev = last_switch(cid, "pose", t)
    def one(pn, alpha=1.0):
        r, pp = pose(pn)
        img = pp.frame(t, SPEECH, speak_id if "eyes" in r else None,
                       look=None, extra={"lids": max(0.0, ch("lids", t))})
        s = place["head"] / r["head_h"]
        dt = t - tk
        pop = 0.0
        if 0 <= dt < 0.5 and prev is not None:
            pop = 0.045 * math.exp(-dt * 9) * math.cos(dt * 26)          # squash/settle after a pose swap
        sq = ch("squash", t) + pop
        br = 0.006 * math.sin(2 * math.pi * t / 3.4 + (7 if cid == "jax" else 3))
        x = place["x"] + (ch("dx", t) if place.get("use_dx") else 0); y = place["y"] + ch("dy", t)
        lean = ch("lean", t) + 0.6 * noise1(t, (5 if cid == "jax" else 11), 0.25)
        src_pt = r["neck"] if place.get("align") == "neck" else r["anchor"]
        M = affine(s * (1 + sq * 0.6), s * (1 - sq + br), lean, src_pt, (x, y))
        M = compose(camM, M)
        out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        return out * alpha, M, r
    out, M, r = one(pname)
    dt = t - tk
    if SL.get("pose_dissolve_frames", 0) and prev is not None and prev != "walk" and 0 <= dt < SL["pose_dissolve_frames"] / FPS and prev in RIGS["poses"]:
        k = dt / (SL["pose_dissolve_frames"] / FPS)
        o2, _, _ = one(prev)
        out = out * k + o2 * (1 - k)
    foot = M @ np.array([r["anchor"][0], r["anchor"][1], 1.0])
    return out, foot, place["head"] * camM[0, 0]

# ------------------------------------------------------------------ sets and plates
class Video:
    def __init__(self, p): self.cap = cv2.VideoCapture(p); self.n = int(self.cap.get(7)); self.pos = -1; self.f = None
    def frame(self, i):
        i = max(0, min(self.n - 1, i))
        if i == self.pos and self.f is not None: return self.f
        if i != self.pos + 1: self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = self.cap.read()
        if ok: self.f = f
        self.pos = i
        return self.f
VIDS = {}
def vid(p):
    if p not in VIDS: VIDS[p] = Video(path(p))
    return VIDS[p]

SETS = {}
def get_set(name):
    if name in SETS: return SETS[name]
    s = SL["sets"][name]
    im = cv2.imread(path(s["src"]))[:, :, ::-1].astype(np.float32) / 255.0
    sc = W / im.shape[1]
    up = cv2.resize(im, (W, int(im.shape[0] * sc)), interpolation=cv2.INTER_LANCZOS4)
    # mild unsharp so close shots stay crisp after upscaling
    up = np.clip(up * 1.35 - cv2.GaussianBlur(up, (0, 0), 1.6) * 0.35, 0, 1)
    up = up[:H] if up.shape[0] >= H else cv2.resize(up, (W, H))
    win = pf.window_mask(up, s["window_region"], s.get("window_thresh", 0.07))
    fg = np.zeros((H, W), np.float32)
    for poly in s.get("fg_polys", []):
        cv2.fillPoly(fg, [(np.array(poly) * sc).astype(np.int32)], 1.0)
    fg = cv2.GaussianBlur(fg, (0, 0), 1.0)
    SETS[name] = (up, win, fg, s)
    return SETS[name]

def camera(shot, t):
    c = shot["camera"]; g = lambda n, d: Channels(c, {n: d})(n, t)
    cx, cy, z = g("cx", 960), g("cy", 540), g("zoom", 1.0)
    cx += 3 * noise1(t, 21, 0.13) / z; cy += 2.5 * noise1(t, 22, 0.11) / z
    for sh in shot.get("shake", []):
        dt = t - sh["at"]
        if 0 <= dt < sh["dur"]:
            a = sh["amp"] * math.exp(-dt * 6) / z; cx += a * math.sin(dt * 70); cy += a * math.cos(dt * 83)
    hw, hh = W / 2 / z, H / 2 / z
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    return np.float64([[z, 0, W / 2 - cx * z], [0, z, H / 2 - cy * z]]), cx, cy, z

def rim(layer, light_dir, colr, w, k):
    a = layer[..., 3]
    dx, dy = int(round(light_dir[0] * w)), int(round(light_dir[1] * w))
    sh = np.zeros_like(a)
    ys, ye = max(0, dy), H + min(0, dy); xs, xe = max(0, dx), W + min(0, dx)
    sh[ys:ye, xs:xe] = a[ys - dy:ye - dy, xs - dx:xe - dx]
    r_ = np.clip(a - sh, 0, 1) * a
    r_ = cv2.GaussianBlur(r_, (0, 0), max(0.8, w * 0.4))
    out = layer.copy(); out[..., :3] += r_[..., None] * np.array(colr, np.float32) * k
    return out

def contact_shadow(img, x, y, rx, ry, k):
    m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, (int(x), int(y)), (max(1, int(rx)), max(1, int(ry))), 0, 0, 360, 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), max(2, ry * 0.7))
    return img * (1 - k * m[..., None])

def render_set_shot(shot, t):
    M, cx, cy, z = camera(shot, t)
    up, win, fg, s = get_set(shot["set"])
    pl = s["plate"]; V = vid(pl["src"])
    fr = V.frame(int((t - pl.get("t_offset", 0)) * FPS * pl.get("speed", 1.0)) % V.n)[:, :, ::-1].astype(np.float32) / 255.0
    par = pl.get("parallax", 0.3)
    pw = pl["w"]; sx = pw / fr.shape[1]
    Mp = np.float64([[sx, 0, pl["x"] + (cx - W / 2) * par], [0, sx, pl["y"] + (cy - H / 2) * par]])
    plate = cv2.warpAffine(fr, Mp, (W, H), flags=cv2.INTER_LINEAR) * pl.get("gain", 1.2)
    world = up * (1 - win[..., None]) + plate * win[..., None]
    # glass sheen
    world = world + win[..., None] * 0.05 * np.clip(np.sin((np.arange(W)[None, :] * 0.6 + np.arange(H)[:, None]) / 90.0), 0, 1)[..., None] ** 8
    blur = shot.get("bg_blur", 0)
    img = cv2.warpAffine(world.astype(np.float32), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if blur: img = cv2.GaussianBlur(img, (0, 0), blur)
    fgw = cv2.warpAffine(fg, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    fgimg = cv2.warpAffine(up.astype(np.float32), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if blur: fgimg = cv2.GaussianBlur(fgimg, (0, 0), blur * 0.7)
    light = s.get("rim_dir", [-0.4, -1.0]); rimc = s.get("rim_color", [0.75, 0.88, 1.0])
    # characters in depth order; those with "behind_fg" are drawn before the counter
    order = shot["chars"]
    for stage in ("behind", "front"):
        for cid, place in order.items():
            if (stage == "behind") != bool(place.get("behind_fg")): continue
            if place.get("hide"): continue
            lay, foot, head_px = char_layer(cid, t, place, M, cid)
            lay = rim(lay, light, rimc, max(2.0, head_px * 0.025), 0.55)
            if place.get("shadow", True) and not place.get("behind_fg"):
                img = contact_shadow(img, foot[0], foot[1], head_px * 0.9, head_px * 0.14, 0.4)
            img = img * (1 - lay[..., 3:4]) + lay[..., :3]
        if stage == "behind":
            img = img * (1 - fgw) + fgimg * fgw
    return img

# ------------------------------------------------------------------ exterior
SHIP = None
def render_ext(shot, t):
    global SHIP
    e = SL["ext"]
    if SHIP is None:
        SHIP = pf.load_rgba(path(e["ship"]), {"type": "green", "t0": 0.10, "t1": 0.30}, VARS)
        ys, xs = np.nonzero(SHIP[..., 3] > 0.05); SHIP = SHIP[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    V = vid(e["src"]); lt = t - shot["t0"]
    fi = int(lt * FPS)
    img = V.frame(fi)[:, :, ::-1].astype(np.float32) / 255.0 * e.get("gain", 1.08)
    g = lambda n, d=0.0: Channels(e["keys"], {n: d})(n, t)
    td = e["touchdown"]
    hs, ws = SHIP.shape[:2]
    if t < td:
        x, y, sc, rot = g("x"), g("y"), g("scale"), g("rot")
        alt = g("alt")
    else:
        # after touchdown the ship is glued to the ground: follow the tracked ground point of the plate
        tr = TRACK.get(fi) or TRACK[max(TRACK)]
        x, y = tr[0] + e["ground_off"][0], tr[1] + e["ground_off"][1]
        sc = g("scale") * tr[2]; rot = g("rot"); alt = 0.0
        y += Channels(e["keys"], {"settle": 0})("settle", t)
    # shadow on the ground under the ship
    gx, gy = x + alt * 0.2, (TRACK.get(int(td * FPS), (0, e["ground_y"]))[1] + e["ground_off"][1] + hs * sc * 0.48) if t < td else y + hs * sc * 0.48
    if t < td: gy = e["ground_y"] - (1 - min(1, alt / 600)) * 0  # ground line under the approach
    m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, (int(gx), int(gy)), (int(ws * sc * 0.45), int(ws * sc * 0.06)), 0, 0, 360, 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), 5 + alt * 0.05)
    img = img * (1 - m[..., None] * float(np.clip(0.7 - alt / 900, 0.12, 0.65)))
    M = affine(sc, sc, rot, (ws / 2, hs / 2), (x, y))
    lay = cv2.warpAffine(SHIP, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    lay = rim(lay, e.get("rim_dir", [-0.8, -0.6]), [1.0, 0.95, 0.85], 4, 0.6)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # engine glow
    thrust = g("thrust", 1.0)
    for i, (ex, ey, er) in enumerate(e["engines"]):
        p = M @ np.array([ex * ws, ey * hs, 1.0])
        fl = 1 + 0.12 * math.sin(t * 37 + i * 2)
        pf.add_glow(img, p[0], p[1], er * sc * 1.2 * thrust * fl, [1.0, 0.62, 0.25], 0.55 * thrust)
        pf.add_glow(img, p[0], p[1], er * sc * 0.5 * fl, [1.0, 0.95, 0.8], 0.8 * thrust)
    # dust puffs (painted-style soft discs) around touchdown
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
    rng = random.Random(5)
    for i in range(80):
        birth = e["dust_t0"] + rng.uniform(0, e["dust_t1"] - e["dust_t0"])
        age = t - birth
        if age < 0 or age > 1.8: continue
        side = rng.choice([-1, 1]); sp = rng.uniform(150, 480)
        dx_ = side * sp * (1 - math.exp(-age * 2.2)) / 2.2
        px = gx + side * rng.uniform(0, ws * sc * 0.3) + dx_
        py = gy - rng.uniform(0, 25) - 50 * (1 - math.exp(-age * 1.5)) * rng.uniform(0.3, 1)
        if t >= td and TRACK: pass
        r_ = (10 + 45 * age) * rng.uniform(0.6, 1.2); al = int(170 * max(0, 1 - age / 1.8))
        cv.drawCircle(px, py, r_, P(col("#e8e1d3", al)))
    a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32) / 255.0
    a = cv2.GaussianBlur(a, (0, 0), 2.0)
    img = img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    return img

TRACK = {}
def build_track():
    """Track a patch of ground in the exterior plate from touchdown onward (optical flow),
    returning per frame (x, y, scale) so the landed ship stays put on the ground."""
    e = SL.get("ext")
    if not e: return
    cache = os.path.join(OUT, "ext_track.json")
    if os.path.exists(cache):
        TRACK.update({int(k): v for k, v in json.load(open(cache)).items()}); return
    cap = cv2.VideoCapture(path(e["src"])); f0 = int(e["touchdown"] * FPS)
    frames = []
    for i in range(int(SL["shots"][0]["t1"] * FPS) + 2):
        ok, f = cap.read()
        if not ok: break
        frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    gx, gy = e["ground_point"]
    pts = np.array([[gx + dx, gy + dy] for dx in (-120, -60, 0, 60, 120) for dy in (-30, 0, 30)], np.float32).reshape(-1, 1, 2)
    base = pts.copy(); TRACK[f0] = (gx, gy, 1.0)
    for i in range(f0 + 1, len(frames)):
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(frames[i - 1], frames[i], pts, None, winSize=(41, 41), maxLevel=3)
        good = st.reshape(-1) == 1
        if good.sum() < 4: TRACK[i] = TRACK[i - 1]; continue
        pts = nxt
        c = pts[good].reshape(-1, 2).mean(0); c0 = base[good].reshape(-1, 2).mean(0)
        spread = np.linalg.norm(pts[good].reshape(-1, 2) - c, axis=1).mean() / max(1e-3, np.linalg.norm(base[good].reshape(-1, 2) - c0, axis=1).mean())
        TRACK[i] = (float(c[0]), float(c[1]), float(spread))
    json.dump(TRACK, open(cache, "w"))

# ------------------------------------------------------------------ finishing
VIG = None
def finish(img, t):
    global VIG
    x = np.clip(img, 0, 1)
    x = np.clip((x - 0.5) * 1.03 + 0.5 + 0.008, 0, 1)
    lum = x.mean(axis=2, keepdims=True); x = lum + (x - lum) * 1.06
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        VIG = (1 - 0.14 * np.clip(v * 0.6, 0, 1))[..., None].astype(np.float32)
    x = x * VIG
    rng = np.random.default_rng(int(t * FPS) + 1)
    gr = rng.normal(0, 0.010, (H // 2, W // 2)).astype(np.float32)
    x = x + cv2.resize(gr, (W, H))[..., None]
    return np.clip(x * 255 + 0.5, 0, 255).astype(np.uint8)

def subtitles(img, t):
    for ln in SL["dialogue"]:
        if ln["start_s"] - 0.05 <= t < ln["start_s"] + ln["dur"] + 0.25:
            surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
            font = skia.Font(skia.Typeface("DejaVu Sans"), 34)
            tw = font.measureText(ln["text"]); x, y = (W - tw) / 2, H - 58
            cv.drawString(ln["text"], x, y, font, P(col("#000000", 220), 6)); cv.drawString(ln["text"], x, y, font, P(col("#ffffff")))
            a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
            al = a[..., 3:4] / 255.0
            img = (img * (1 - al) + a[..., :3] * al).astype(np.uint8)
    return img

def frame(t):
    for shot in SL["shots"]:
        if shot["t0"] <= t < shot["t1"]: break
    img = render_ext(shot, t) if shot["kind"] == "ext" else render_set_shot(shot, t)
    out = finish(img, t)
    fi, fo = shot.get("fade_in", 0), shot.get("fade_out", 0)
    if fi and t - shot["t0"] < fi: out = (out * ((t - shot["t0"]) / fi)).astype(np.uint8)
    if fo and shot["t1"] - t < fo: out = (out * ((shot["t1"] - t) / fo)).astype(np.uint8)
    return subtitles(out, t)

def render_chunk(args):
    a, b, fn = args
    os.nice(5); cv2.setNumThreads(1)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "1", fn], stdin=subprocess.PIPE)
    t0 = time.process_time()
    for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    return time.process_time() - t0

if __name__ == "__main__":
    build_track()
    args = sys.argv[3:]
    if "--still" in args:
        for tt in args[args.index("--still") + 1:]:
            if tt.startswith("--"): break
            cv2.imwrite(os.path.join(OUT, f"still_{float(tt):06.2f}.jpg"), cv2.cvtColor(frame(float(tt)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit(0)
    nf = int(round(SL["duration_s"] * FPS)); a0, b0 = 0, nf
    if "--frames" in args: a0, b0 = map(int, args[args.index("--frames") + 1].split(":"))
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 4
    nch = workers * 4; size = math.ceil((b0 - a0) / nch)
    jobs = [(a0 + i * size, min(b0, a0 + (i + 1) * size), os.path.join(OUT, f"seg_{i:03d}.mp4")) for i in range(nch) if a0 + i * size < b0]
    from multiprocessing import Pool
    wall = time.time()
    with Pool(workers) as pool: cpu = pool.map(render_chunk, jobs)
    wall = time.time() - wall
    with open(os.path.join(OUT, "segs.txt"), "w") as f:
        for j in jobs: f.write(f"file '{os.path.basename(j[2])}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "segs.txt"), "-c", "copy", os.path.join(OUT, SL["name"] + "-picture.mp4")], check=True)
    json.dump({"frames": b0 - a0, "wall_s": round(wall, 1), "cpu_s_render": round(sum(cpu), 1),
               "cpu_s_per_video_s": round(sum(cpu) / ((b0 - a0) / FPS), 1), "workers": workers},
              open(os.path.join(OUT, SL["name"] + ".render.json"), "w"), indent=1)
    print("done", wall, sum(cpu))
