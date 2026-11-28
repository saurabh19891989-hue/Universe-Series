#!/usr/bin/env python3
"""TEST 3 renderer: flat-cartoon puppets over real NASA video.

usage: scene.py SHOTLIST.json OUTDIR [--frames a:b] [--still T ...] [--workers 2]
Reads the pose-and-timing file (shotlist), renders 1920x1080 24 fps in parallel chunks,
mixes audio (dialogue stems, score, effects) to -16 LUFS, burns small subtitles, writes
OUTDIR/<name>.mp4 and OUTDIR/<name>.render.json (render speed).
"""
import json, math, os, subprocess, sys, time, random
import numpy as np, cv2, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig
from rig import Channels, col, P, noise1, ease

W, H, FPS = 1920, 1080, 24
SL = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
S = SL["vars"]["SCRATCH"]; T = SL["vars"]["TOON"]
def path(p): return p.replace("${SCRATCH}", S).replace("${TOON}", T)

# ------------------------------------------------------------------ assets
CHARS = {cid: rig.Character(path(c["rig"]), T) for cid, c in SL["characters"].items()}
CH = {cid: Channels(c["keys"], c["defaults"]) for cid, c in SL["characters"].items()}
LIPS = {}
for ln in SL["dialogue"]:
    j = json.load(open(path(ln["lips"])))
    LIPS[ln["id"]] = [(c["start"], c["end"], c["value"]) for c in j["mouthCues"]]
# speech envelopes for talk-nods
ENV = {}
import soundfile as sf
for ln in SL["dialogue"]:
    a, sr = sf.read(path(ln["src"]), always_2d=True); a = a.mean(1)
    hop = sr // FPS; n = len(a) // hop
    e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) if n else np.zeros(1)
    ENV[ln["id"]] = e / (e.max() + 1e-9)

def speech(cid, t):
    """mouth shape and loudness for character cid at time t"""
    for ln in SL["dialogue"]:
        if ln["who"] != cid: continue
        lt = t - ln["start_s"]
        if 0 <= lt < ln["dur"] + 0.05:
            m = "X"
            for s0, s1, v in LIPS[ln["id"]]:
                if s0 <= lt < s1: m = v; break
            e = ENV[ln["id"]]; i = min(len(e) - 1, int(lt * FPS))
            return m, float(e[i])
    return None, 0.0

HALL = cv2.imread(path(SL["hall"]["bg"]))
k = W / HALL.shape[1]
# paint out the printed stamp (Mira holds a drawn one)
x0, y0, x1, y1 = SL["hall"]["paint_out"]
fill = SL["hall"].get("paint_fill_from", [x1 + 4, (y0 + y1) // 2])
HALL[y0:y1, x0:x1] = HALL[fill[1], fill[0]]       # flat art: a flat fill is cleaner than inpainting
HALL_W = cv2.resize(HALL, (W, H), interpolation=cv2.INTER_CUBIC)
win = SL["hall"]["window_bbox"]                                  # in bg pixels
dark = (HALL_W.max(axis=2) < 28).astype(np.uint8)
wm = np.zeros_like(dark); X0, Y0, X1, Y1 = [int(v * k) for v in win]; wm[Y0:Y1, X0:X1] = 1
WIN_MASK = cv2.GaussianBlur((dark * wm).astype(np.float32), (5, 5), 1.2)[..., None]
fg_poly = (np.array(SL["hall"]["desk_poly"]) * k).astype(np.int32)
FG_MASK = np.zeros((H, W), np.float32); cv2.fillPoly(FG_MASK, [fg_poly], 1.0)
if "lamp_poly" in SL["hall"]:
    cv2.fillPoly(FG_MASK, [(np.array(SL["hall"]["lamp_poly"]) * k).astype(np.int32)], 1.0)
FG_MASK = cv2.GaussianBlur(FG_MASK, (3, 3), 0.8)[..., None]

SHIP = None
if "ship" in SL and os.path.exists(path(SL["ship"]["file"])):
    a = cv2.imread(path(SL["ship"]["file"]), -1)
    rgba = a[..., [2, 1, 0, 3]].copy(); al = rgba[..., 3:4].astype(np.float32) / 255
    rgba[..., :3] = (rgba[..., :3] * al).astype(np.uint8)
    SHIP = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)

class Video:
    def __init__(self, p): self.p = p; self.cap = cv2.VideoCapture(p); self.n = int(self.cap.get(7)); self.pos = -1; self.f = None
    def frame(self, i):
        i = max(0, min(self.n - 1, i))
        if i != self.pos + 1 or self.f is None:
            if i == self.pos and self.f is not None: return self.f
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = self.cap.read()
        if ok: self.f = f
        self.pos = i
        return self.f
VIDS = {}
def vid(p):
    if p not in VIDS: VIDS[p] = Video(path(p))
    return VIDS[p]

# ------------------------------------------------------------------ helpers
def chan_keys(keys, t, name, default):
    return Channels(keys, {name: default})(name, t)

def camera(shot, t):
    c = shot["camera"]; d = {"cx": W / 2, "cy": H / 2, "zoom": 1.0}
    cx = chan_keys(c, t, "cx", c.get("cx0", 960)); cy = chan_keys(c, t, "cy", c.get("cy0", 540))
    z = chan_keys(c, t, "zoom", c.get("zoom0", 1.0))
    cx += 4 * noise1(t, 21, 0.13) / z; cy += 3 * noise1(t, 22, 0.11) / z     # breathing handheld drift
    for sh in shot.get("shake", []):
        dt = t - sh["at"]
        if 0 <= dt < sh["dur"]:
            a = sh["amp"] * math.exp(-dt * 6) / z
            cx += a * math.sin(dt * 70); cy += a * math.cos(dt * 83)
    # keep inside the world
    hw, hh = W / 2 / z, H / 2 / z
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    return cx, cy, z

def world_to_screen(cx, cy, z):
    return np.float32([[z, 0, W / 2 - cx * z], [0, z, H / 2 - cy * z]])

def to_np(surface):
    """RGBA, colour PREMULTIPLIED by alpha (skia hands back unpremultiplied pixels)"""
    a = surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
    a[..., :3] *= a[..., 3:4] / 255.0
    return a

def comp(dst, rgba_premul):
    a = rgba_premul[..., 3:4].astype(np.float32) / 255.0
    return dst * (1 - a) + rgba_premul[..., :3].astype(np.float32)

def rim_and_shadow(layer, light_dir, rim_col, rim_w, rim_k):
    """layer: RGBA premult uint8 (RGB order). adds a rim light on edges facing the light."""
    a = layer[..., 3].astype(np.float32) / 255.0
    dx, dy = int(round(light_dir[0] * rim_w)), int(round(light_dir[1] * rim_w))
    sh = np.zeros_like(a)
    ys, ye = max(0, dy), H + min(0, dy); xs, xe = max(0, dx), W + min(0, dx)
    sh[ys:ye, xs:xe] = a[ys - dy:ye - dy, xs - dx:xe - dx]
    rim = np.clip(a - sh, 0, 1) * a
    rim = cv2.GaussianBlur(rim, (0, 0), max(0.6, rim_w * 0.25))
    out = layer.astype(np.float32)
    out[..., :3] += rim[..., None] * np.array(rim_col, np.float32) * rim_k
    return np.clip(out, 0, 255), a

def contact_shadow(img, cxs, cy, rx, ry, k=0.45):
    m = np.zeros((H, W), np.float32)
    for cx in cxs: cv2.ellipse(m, (int(cx), int(cy)), (max(1, int(rx)), max(1, int(ry))), 0, 0, 360, 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), max(2, ry * 0.6))
    return img * (1 - k * m[..., None])

def grade(img, g):
    x = img / 255.0
    x = np.clip((x - 0.5) * g.get("contrast", 1.04) + 0.5 + g.get("lift", 0.01), 0, 1)
    lum = x.mean(axis=2, keepdims=True)
    x = lum + (x - lum) * g.get("sat", 1.08)
    warm = np.array([1.03, 1.0, 0.95]); cool = np.array([0.95, 0.99, 1.05])
    x = x * (cool + (warm - cool) * lum)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    x *= (1 - g.get("vignette", 0.18) * np.clip(v * 0.6, 0, 1))[..., None]
    return np.clip(x * 255, 0, 255)

VIG = None
def finish(img, t, g):
    global VIG
    x = img / 255.0
    x = np.clip((x - 0.5) * g.get("contrast", 1.04) + 0.5 + g.get("lift", 0.012), 0, 1)
    lum = x.mean(axis=2, keepdims=True)
    x = lum + (x - lum) * g.get("sat", 1.08)
    x = x * (np.array([0.96, 0.99, 1.04]) + np.array([0.07, 0.01, -0.09]) * lum)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        VIG = (1 - 0.16 * np.clip(v * 0.6, 0, 1))[..., None].astype(np.float32)
    x = x * VIG
    rng = np.random.default_rng(int(t * FPS) + 1)
    gr = rng.normal(0, g.get("grain", 0.012), (H // 2, W // 2)).astype(np.float32)
    x = x + cv2.resize(gr, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(x * 255 + 0.5, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ walk
def make_walk(spec):
    t0, t1, xa, xb, steps = spec["t0"], spec["t1"], spec["x0"], spec["x1"], spec["cycles"]
    Sd = (xb - xa) / steps
    def walk(t, u, gy=None):
        if t < t0 or t > t1: return None
        p = steps * ease(spec.get("ease", "io"), (t - t0) / (t1 - t0))
        hx = xa + p * Sd
        feet, lift = [], []
        for i in range(2):
            q = p + 0.5 * i; n = math.floor(q); fr = q - n
            plant = lambda m: xa + (m + 0.25 - 0.5 * i) * Sd
            if fr < 0.5: fx = plant(n); lf = 0
            else:
                s = (fr - 0.5) / 0.5; s2 = rig.smoother(s)
                fx = plant(n) + (plant(n + 1) - plant(n)) * s2; lf = math.sin(s * math.pi) * spec.get("lift", 5) * u
            feet.append((fx, spec["y"])); lift.append(lf)
        bob = spec.get("bob", 2.2) * u * (math.cos(4 * math.pi * (p - 0.25)) - 1) * 0.5
        hip_h = spec["hip_h"] * u
        return hx, spec["y"] - hip_h + bob, feet, lift, p
    return walk

WALKS = {}
for cid, c in SL["characters"].items():
    if "walk" in c:
        w = dict(c["walk"]); w["hip_h"] = CHARS[cid].r["hip_h"]
        WALKS[cid] = make_walk(w)

class WalkCh:
    """channel wrapper: during a walk, arms swing and the torso leans; otherwise pass-through"""
    def __init__(self, ch, wf): self.ch = ch; self.wf = wf; self.p = None
    def __call__(self, name, t):
        v = self.ch(name, t)
        if self.p is None: return v
        p, a = self.p
        if name == "sh0": return 24 * math.sin(2 * math.pi * p) * a + v * (1 - a)
        if name == "sh1": return -24 * math.sin(2 * math.pi * p) * a + v * (1 - a)
        if name == "el0": return 18 * a + v * (1 - a)
        if name == "el1": return 18 * a + v * (1 - a)
        if name == "lean": return v + 5 * a
        return v

# ------------------------------------------------------------------ drawing characters
def draw_char(cid, t, M, extras=None):
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
    cv.concat(skia.Matrix.MakeAll(M[0, 0], 0, M[0, 2], 0, M[1, 1], M[1, 2], 0, 0, 1))
    ch = CH[cid]; mouth, env = speech(cid, t)
    rest = ch("mouth_rest", t) if isinstance(ch("mouth_rest", t), str) else "X"
    wf = WALKS.get(cid); walk = None; wch = WalkCh(ch, wf)
    if wf:
        r = wf(t, ch("H", t) / 100.0)
        if r:
            hx, hy, feet, lift, p = r
            # arm swing fades in/out over the first/last half step
            spec = SL["characters"][cid]["walk"]; tt = (t - spec["t0"]) / (spec["t1"] - spec["t0"])
            wch.p = (p, min(1, tt * 6, (1 - tt) * 6))
            walk = lambda t_, u_: (hx, hy, feet, lift)
    G, arms = CHARS[cid].draw(cv, t, wch, mouth=mouth or rest, walk=walk, extras=extras)
    return to_np(surf), G

def render_hall(shot, t):
    cx, cy, z = camera(shot, t)
    M = world_to_screen(cx, cy, z)
    # background with the NASA plate in the window
    pl = SL["hall"]["plate"]; V = vid(pl["src"])
    pt = (t - pl.get("t_offset", 0)) * pl.get("speed", 1.0)
    fr = V.frame(int(pt * FPS) % V.n)
    par = pl.get("parallax", 0.25)
    px, py, pw = pl["x"] + (cx - W / 2) * par, pl["y"] + (cy - H / 2) * par, pl["w"]
    ph = pw * fr.shape[0] / fr.shape[1]
    sx = pw / fr.shape[1]
    Mp = np.float32([[sx, 0, px], [0, sx, py]])
    plate_w = cv2.warpAffine(fr, Mp, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    plate_w = np.clip(plate_w.astype(np.float32) * pl.get("gain", 1.15), 0, 255)
    world = HALL_W.astype(np.float32) * (1 - WIN_MASK) + plate_w * WIN_MASK
    # flat-style glass shine over the window
    world_u8 = world.astype(np.uint8)
    bg = cv2.warpAffine(world_u8, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if z > 1.3:
        bg = cv2.GaussianBlur(bg, (0, 0), min(3.0, (z - 1.0) * 1.1))   # soft background = depth
    img = bg[..., ::-1].astype(np.float32)                              # RGB
    glass = skia.Surface(W, H); gc = glass.getCanvas(); gc.clear(skia.ColorTRANSPARENT)
    gc.concat(skia.Matrix.MakeAll(M[0, 0], 0, M[0, 2], 0, M[1, 1], M[1, 2], 0, 0, 1))
    for (a0, a1, w_) in [(640, 980, 70), (760, 1040, 26), (1500, 1800, 90)]:
        gc.drawPath(rig.poly([(a0, 110), (a0 + w_, 110), (a1 + w_ - 300, 690), (a1 - 300, 690)]), P(col("#ffffff", 16)))
    img = comp(img, to_np(glass).astype(np.float32))
    # rim colour from the plate (cool Earth/sun light)
    rim_col = SL["hall"].get("rim_color", [200, 225, 255])
    light_dir = SL["hall"].get("rim_dir", [-0.5, -1.0])
    # Mira (behind the desk)
    lay, G = draw_char("mira", t, M)
    lay, a = rim_and_shadow(lay, light_dir, rim_col, 3.2 * z, 0.55)
    img = img * (1 - a[..., None]) + lay[..., :3]
    # desk in front of her, then her glass screen
    desk_s = cv2.warpAffine((HALL_W.astype(np.float32)), M, (W, H), flags=cv2.INTER_CUBIC)[..., ::-1]
    fgm = cv2.warpAffine(FG_MASK[..., 0], M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    if z > 1.3: desk_s = cv2.GaussianBlur(desk_s, (0, 0), min(2.0, (z - 1.0) * 0.6))
    img = img * (1 - fgm) + desk_s * fgm
    gl = skia.Surface(W, H); gc = gl.getCanvas(); gc.clear(skia.ColorTRANSPARENT)
    gc.concat(skia.Matrix.MakeAll(M[0, 0], 0, M[0, 2], 0, M[1, 1], M[1, 2], 0, 0, 1))
    gx0, gy0, gx1, gy1 = SL["hall"]["glass_world"]
    gc.drawRect(skia.Rect(gx0, gy0, gx1, gy1), P(col("#bfe9f2", 22)))
    for (o, w_) in [(40, 26), (95, 9)]:
        gc.drawPath(rig.poly([(gx0 + o, gy0), (gx0 + o + w_, gy0), (gx0 + o + w_ - 120, gy1), (gx0 + o - 120, gy1)]), P(col("#ffffff", 30)))
    gc.drawLine(gx0, gy0, gx0, gy1, P(col("#d8f4fa", 160), 5)); gc.drawLine(gx0, gy0, gx1, gy0, P(col("#d8f4fa", 140), 4))
    img = comp(img, to_np(gl).astype(np.float32))
    # Jax (in front), with contact shadow
    lay, G = draw_char("jax", t, M)
    feet = [(M[0, 0] * f[0] + M[0, 2], M[1, 1] * f[1] + M[1, 2]) for f in G["feet"]]
    u = G["u"] * z
    img = contact_shadow(img, [f[0] for f in feet], feet[0][1] + 1 * u, 7 * u, 1.8 * u, 0.42)
    lay, a = rim_and_shadow(lay, light_dir, rim_col, 3.2 * z, 0.6)
    img = img * (1 - a[..., None]) + lay[..., :3]
    return img

def render_ext(shot, t):
    e = SL["ext"]; V = vid(e["src"])
    lt = t - shot["t0"]
    fr = V.frame(int(lt * FPS * e.get("speed", 1.0)))
    img = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) * e.get("gain", 1.1)
    k_ = e["keys"]
    g = lambda n, d=0: chan_keys(k_, t, n, d)
    sx_, sy_, sc, rot = g("x"), g("y"), g("scale"), g("rot")
    alt = g("alt")
    # ground shadow (soft, darker as the ship comes down)
    shd = np.zeros((H, W), np.float32)
    sw = SHIP.width() * sc
    gyy = g("ground_y")
    cv2.ellipse(shd, (int(sx_ + alt * 0.25), int(gyy)), (int(sw * 0.42), int(sw * 0.06)), 0, 0, 360, 1.0, -1)
    shd = cv2.GaussianBlur(shd, (0, 0), 6 + alt * 0.06)
    img = img * (1 - shd[..., None] * float(np.clip(0.75 - alt / 900, 0.15, 0.7)))
    # dust: flat puffs kicked out near the ground
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
    rng = random.Random(5)
    for i in range(70):
        birth = e["dust_t0"] + rng.uniform(0, e["dust_t1"] - e["dust_t0"])
        age = t - birth
        if age < 0 or age > 1.6: continue
        side = rng.choice([-1, 1]); sp = rng.uniform(180, 520)
        dxp = side * sp * (1 - math.exp(-age * 2.2)) / 2.2
        x = sx_ + alt * 0.25 + side * rng.uniform(0, sw * 0.25) + dxp
        y = gyy - rng.uniform(0, 30) - 60 * (1 - math.exp(-age * 1.5)) * rng.uniform(0.3, 1)
        r = (10 + 40 * age) * rng.uniform(0.6, 1.2)
        al = int(200 * max(0, 1 - age / 1.6))
        cv.drawCircle(x, y, r, P(col("#e6dfd2", al))); cv.drawCircle(x, y, r, P(col("#8e8678", al // 2), 2.5))
    # ship
    cv.save(); cv.translate(sx_, sy_); cv.rotate(rot); cv.scale(sc, sc)
    cv.translate(-SHIP.width() / 2, -SHIP.height() / 2)
    cv.drawImage(SHIP, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    cv.restore()
    lay = to_np(surf)
    lay_f, a = rim_and_shadow(lay, e.get("rim_dir", [0.7, -0.7]), [255, 245, 225], 4, 0.7)
    img = img * (1 - a[..., None]) + lay_f[..., :3]
    # engine glow (additive), flickering
    gl = skia.Surface(W, H); gc = gl.getCanvas(); gc.clear(skia.ColorTRANSPARENT)
    gc.translate(sx_, sy_); gc.rotate(rot); gc.scale(sc, sc); gc.translate(-SHIP.width() / 2, -SHIP.height() / 2)
    thrust = g("thrust", 1.0)
    for i, (ex, ey, er) in enumerate(e["engines"]):
        fl = 1 + 0.12 * math.sin(t * 37 + i * 2) + 0.08 * math.sin(t * 23 + i)
        for rr, al in [(er * 2.6 * thrust * fl, 50), (er * 1.5 * fl, 110), (er * 0.8, 230)]:
            gc.drawCircle(ex * SHIP.width(), ey * SHIP.height(), rr, P(col("#ffb45a" if rr > er else "#fff2c8", al)))
    glow = to_np(gl).astype(np.float32)
    img = np.clip(img + glow[..., :3] * 0.9, 0, 255)
    return img

def subtitles(img, t):
    for ln in SL["dialogue"]:
        if ln["start_s"] - 0.05 <= t < ln["start_s"] + ln["dur"] + 0.25:
            surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
            font = skia.Font(skia.Typeface("DejaVu Sans"), 34)
            txt = ln["text"]; tw = font.measureText(txt)
            x, y = (W - tw) / 2, H - 58
            st = P(col("#000000", 220), 6); cv.drawString(txt, x, y, font, st)
            cv.drawString(txt, x, y, font, P(col("#ffffff")))
            img = comp(img, to_np(surf).astype(np.float32))
    return img

def frame(t):
    for shot in SL["shots"]:
        if shot["t0"] <= t < shot["t1"]: break
    img = render_ext(shot, t) if shot["kind"] == "ext" else render_hall(shot, t)
    out = finish(img, t, shot.get("grade", {}))
    fi, fo = shot.get("fade_in", 0), shot.get("fade_out", 0)
    if fi and t - shot["t0"] < fi: out = (out * ((t - shot["t0"]) / fi)).astype(np.uint8)
    if fo and shot["t1"] - t < fo: out = (out * ((shot["t1"] - t) / fo)).astype(np.uint8)
    if SL.get("subtitles", True): out = subtitles(out.astype(np.float32), t).astype(np.uint8)
    return out

# ------------------------------------------------------------------ main
def render_chunk(args):
    a, b, fn = args
    os.nice(5)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "1", fn],
                         stdin=subprocess.PIPE)
    t0 = time.process_time()
    for i in range(a, b):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    return time.process_time() - t0

if __name__ == "__main__":
    args = sys.argv[3:]
    if "--still" in args:
        for tt in args[args.index("--still") + 1:]:
            if tt.startswith("--"): break
            cv2.imwrite(os.path.join(OUT, f"still_{float(tt):06.2f}.jpg"), cv2.cvtColor(frame(float(tt)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit(0)
    nf = int(round(SL["duration_s"] * FPS))
    a0, b0 = 0, nf
    if "--frames" in args:
        a0, b0 = map(int, args[args.index("--frames") + 1].split(":"))
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 2
    nch = workers * 4; size = math.ceil((b0 - a0) / nch)
    jobs = [(a0 + i * size, min(b0, a0 + (i + 1) * size), os.path.join(OUT, f"seg_{i:03d}.mp4")) for i in range(nch) if a0 + i * size < b0]
    from multiprocessing import Pool
    wall = time.time()
    with Pool(workers) as pool: cpu = pool.map(render_chunk, jobs)
    wall = time.time() - wall
    with open(os.path.join(OUT, "segs.txt"), "w") as f:
        for j in jobs: f.write(f"file '{os.path.basename(j[2])}'\n")
    name = SL["name"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "segs.txt"), "-c", "copy", os.path.join(OUT, name + "-picture.mp4")], check=True)
    json.dump({"frames": b0 - a0, "wall_s": round(wall, 1), "cpu_s_render": round(sum(cpu), 1),
               "cpu_s_per_video_s": round(sum(cpu) / ((b0 - a0) / FPS), 1), "workers": workers},
              open(os.path.join(OUT, name + ".render.json"), "w"), indent=1)
    print("done", wall, sum(cpu))
