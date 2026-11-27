#!/usr/bin/env python3
"""Secret Universe edit engine: per-shot frame renderer.

A shot is a stack of layers living in the coordinate space of its BASE layer (the first layer,
usually a set or character still). A virtual camera moves over that space; every other layer
is placed in base space and follows the camera with its own parallax depth. Lights and focus
act on the base layer before the camera; the film finish acts on the final frame.
See SCHEMA.md for the JSON fields. Grade/halation/grain logic grew out of look/cinema.py.
"""
import hashlib, json, math, os, subprocess
import numpy as np, cv2
from PIL import Image

import gfx

cv2.setNumThreads(1)

# ------------------------------------------------------------------ small helpers
def ease(u, kind="inout"):
    u = min(1.0, max(0.0, u))
    if kind == "linear":
        return u
    if kind == "in":
        return u * u * u
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "inout-soft":            # smoothstep
        return u * u * (3 - 2 * u)
    return u * u * u * (u * (6 * u - 15) + 10)   # smootherstep: zero velocity AND accel at ends


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), np.float32) / 255


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lum(x):
    return x @ np.float32([0.2126, 0.7152, 0.0722])


def smooth_noise(seed, t, period=3.0, octaves=3):
    """Deterministic smooth 1-D noise in [-1, 1] (sum of sines with seeded phases)."""
    rng = np.random.default_rng(seed)
    v = 0.0; tot = 0.0
    for o in range(octaves):
        f = (1.0 / period) * (1.9 ** o) * rng.uniform(0.8, 1.2)
        a = 0.55 ** o
        v += a * math.sin(2 * math.pi * f * t + rng.uniform(0, 6.283)); tot += a
    return v / tot


def rect_mask(shape, rect, feather):
    """rect = [x0,y0,x1,y1] in normalised base coords; returns float mask (h, w)."""
    h, w = shape
    m = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = [int(round(v)) for v in (rect[0] * w, rect[1] * h, rect[2] * w, rect[3] * h)]
    m[max(0, y0):y1, max(0, x0):x1] = 1
    if feather > 0:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


def shape_mask(shape, s):
    """ellipse / rect / polygon mask in normalised coords with feather (px)."""
    h, w = shape
    m = np.zeros((h, w), np.float32)
    kind = s.get("shape", "ellipse")
    if kind == "rect":
        x0, y0, x1, y1 = s["rect"]
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    elif kind == "polygon":
        pts = np.int32([[p[0] * w, p[1] * h] for p in s["points"]])
        cv2.fillPoly(m, [pts], 1.0, lineType=cv2.LINE_AA)
    else:
        cv2.ellipse(m, (int(s["x"] * w), int(s["y"] * h)), (max(1, int(s["rx"] * w)), max(1, int(s["ry"] * h))),
                    s.get("angle", 0), 0, 360, 1.0, -1, lineType=cv2.LINE_AA)
    f = s.get("feather_px", s.get("feather", 0.04) * w if s.get("feather", 0) < 1 else s.get("feather"))
    if f > 0:
        m = cv2.GaussianBlur(m, (0, 0), f)
    return m


# ------------------------------------------------------------------ sources
class Video:
    """Video plate source (any ffmpeg-readable file). Loops; returns float RGB."""
    def __init__(self, path, max_w=2400):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 24
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.idx = -1; self.frame = None; self.max_w = max_w

    def at(self, t):
        i = int(t * self.fps) % self.n
        if i != self.idx + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = self.cap.read()
        if ok:
            f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
            if f.shape[1] > self.max_w:
                s = self.max_w / f.shape[1]
                f = cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            self.frame = f
        self.idx = i
        return self.frame


def is_video(p):
    return os.path.splitext(p)[1].lower() in (".mp4", ".mov", ".mkv", ".webm", ".m4v")


# ------------------------------------------------------------------ layer prep (static, once per shot)
def apply_grade_local(img, g):
    """Per-layer light/grade override: exposure (stops), gain rgb, lift, gamma, saturation."""
    if not g:
        return img
    x = img
    if "exposure" in g:
        x = x * (2.0 ** g["exposure"])
    if "gain" in g:
        x = x * np.float32(g["gain"])
    if "gamma" in g:
        x = np.clip(x, 0, None) ** (1.0 / g["gamma"])
    if "lift" in g:
        x = x + np.float32(g["lift"]) * (1 - x)
    if "sat" in g:
        l = lum(x)[..., None]
        x = l + (x - l) * g["sat"]
    return np.clip(x, 0, 4).astype(np.float32)


def apply_relight(img, rel):
    """Static relight: list of shapes; inside gets gain_in, outside gain_out (feathered)."""
    h, w = img.shape[:2]
    for r in rel or []:
        m = shape_mask((h, w), r)[..., None]
        gi = np.float32(r.get("gain_in", 1.0)); go = np.float32(r.get("gain_out", 1.0))
        if np.ndim(gi) == 0:
            gi = np.float32([gi] * 3)
        if np.ndim(go) == 0:
            go = np.float32([go] * 3)
        img = img * (m * gi + (1 - m) * go)
    return img


def window_mask(img, spec):
    """Automatic glass mask: pixels near pure black (or pure white) inside an optional region,
    largest connected component(s), holes closed, edge feathered. Returns (mask, glass_level)."""
    h, w = img.shape[:2]
    L = lum(img)
    key = spec.get("key", "black")
    thr = spec.get("thresh", 0.05 if key == "black" else 0.88)
    raw = (L < thr) if key == "black" else (L > thr)
    raw = raw.astype(np.uint8)
    if "region" in spec:
        reg = np.zeros_like(raw)
        x0, y0, x1, y1 = spec["region"]
        reg[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
        raw &= reg
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(raw, 8)
    keep = np.zeros_like(raw)
    min_area = spec.get("min_area", 0.01) * h * w
    order = np.argsort(-stats[1:, cv2.CC_STAT_AREA]) + 1 if n > 1 else []
    for k, i in enumerate(order):
        if stats[i, cv2.CC_STAT_AREA] >= min_area and k < spec.get("max_regions", 1):
            keep[lab == i] = 1
    close = spec.get("close_px", 9)
    if close:
        keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    # fill holes (reflections / specks inside the glass)
    ff = keep.copy(); mm = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mm, (0, 0), 1)
    keep = keep | (1 - ff)
    m = keep.astype(np.float32)
    grow = spec.get("grow_px", 1.0)          # grow slightly under the frame edge so no dark rim
    if grow:
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * grow + 1),) * 2))
    feather = spec.get("feather_px", 1.6)
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    if key == "white":
        # soft luminance key on the edge so backlit hair keeps its glow instead of a hard cut
        soft = np.clip((L - (thr - 0.12)) / 0.12, 0, 1)
        m = np.minimum(m, np.maximum(soft, cv2.erode(m, np.ones((5, 5), np.uint8))))
    inside = m > 0.9
    glass = float(np.median(img[inside])) if inside.any() else 0.0
    return np.clip(m, 0, 1), glass


def inpaint_under(img, mask, dilate=9):
    m8 = (cv2.dilate((mask > 0.05).astype(np.uint8), np.ones((dilate, dilate), np.uint8)) * 255)
    small = cv2.resize((np.clip(img, 0, 1) * 255).astype(np.uint8), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m8, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    fill = cv2.inpaint(small, ms, 7, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    a = cv2.GaussianBlur(m8.astype(np.float32) / 255, (0, 0), 3)[..., None]
    return img * (1 - a) + fill * a


# ------------------------------------------------------------------ camera
def cam_at(cam, t, dur, seed):
    """Camera state (cx, cy, zoom, rot) in normalised base coords at shot time t."""
    keys = cam.get("keys")
    if not keys:
        a = cam.get("from", {"cx": 0.5, "cy": 0.5, "zoom": 1.0})
        b = cam.get("to", a)
        t0 = cam.get("start_s", 0.0); t1 = cam.get("end_s", dur)
        keys = [dict(a, t=t0), dict(b, t=t1)]
    keys = sorted(keys, key=lambda k: k["t"])
    kind = cam.get("ease", "inout")
    if t <= keys[0]["t"]:
        k0 = k1 = keys[0]; u = 0
    elif t >= keys[-1]["t"]:
        k0 = k1 = keys[-1]; u = 0
    else:
        for k0, k1 in zip(keys, keys[1:]):
            if k0["t"] <= t <= k1["t"]:
                break
        u = ease((t - k0["t"]) / max(1e-6, k1["t"] - k0["t"]), k1.get("ease", kind))
    st = {}
    for f, d in (("cx", 0.5), ("cy", 0.5), ("rot", 0.0)):
        st[f] = k0.get(f, d) + (k1.get(f, d) - k0.get(f, d)) * u
    z0, z1 = k0.get("zoom", 1.0), k1.get("zoom", 1.0)
    st["zoom"] = z0 * (z1 / z0) ** u             # log-space zoom => constant perceived speed
    # drift: slow organic float (operator breathing), in output px
    dr = cam.get("drift")
    st["dx"] = st["dy"] = 0.0
    if dr:
        amp = dr.get("amp_px", 3.0); per = dr.get("period_s", 6.0)
        st["dx"] = amp * smooth_noise(seed, t, per)
        st["dy"] = amp * 0.7 * smooth_noise(seed + 1, t, per * 1.2)
        st["rot"] += dr.get("rot_deg", 0.0) * smooth_noise(seed + 2, t, per * 1.5)
    for sh in cam.get("shake", []):
        d = t - sh["at"]
        if 0 <= d < sh.get("decay_s", 0.35) * 4:
            k = math.exp(-d / sh.get("decay_s", 0.35)) * sh.get("amp_px", 10)
            st["dy"] += k * math.cos(d * 2 * math.pi * sh.get("hz", 9))
            st["dx"] += k * 0.4 * math.sin(d * 2 * math.pi * sh.get("hz", 9) * 1.3)
    return st


def cam_matrix(st, base_wh, out_wh, depth=1.0, st0=None, extra=(0.0, 0.0)):
    """2x3 affine mapping base-space px -> output px for a layer at parallax `depth`."""
    bw, bh = base_wh; W, H = out_wh
    s0 = max(W / bw, H / bh)
    cx, cy, z = st["cx"], st["cy"], st["zoom"]
    if st0 is not None and depth != 1.0:
        cx = st0["cx"] + (cx - st0["cx"]) * depth
        cy = st0["cy"] + (cy - st0["cy"]) * depth
        z = st0["zoom"] * (z / st0["zoom"]) ** depth
    s = s0 * z
    th = math.radians(st.get("rot", 0.0))
    c, si = math.cos(th) * s, math.sin(th) * s
    px, py = cx * bw, cy * bh
    tx = W / 2 + st["dx"] * depth + extra[0] - (c * px - si * py)
    ty = H / 2 + st["dy"] * depth + extra[1] - (si * px + c * py)
    return np.float64([[c, -si, tx], [si, c, ty]])


def compose(A, B):
    """A after B for 2x3 affines."""
    A3 = np.vstack([A, [0, 0, 1]]); B3 = np.vstack([B, [0, 0, 1]])
    return (A3 @ B3)[:2]


def warp(img, M, out_wh, interp=cv2.INTER_CUBIC, border=cv2.BORDER_REFLECT101):
    return cv2.warpAffine(img, M, out_wh, flags=interp, borderMode=border)


# ------------------------------------------------------------------ lights (base space, per frame)
def bbox(m, thr=2e-3, pad=2):
    """Crop a full-size mask to where it matters: returns (slice_y, slice_x, cropped mask)."""
    ys, xs = np.where(m > thr)
    if len(ys) == 0:
        return slice(0, 0), slice(0, 0), m[:0, :0]
    y0, y1 = max(0, ys.min() - pad), min(m.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(m.shape[1], xs.max() + pad + 1)
    return slice(y0, y1), slice(x0, x1), np.ascontiguousarray(m[y0:y1, x0:x1])


class Lights:
    """All light effects work only inside each light's bounding box (cheap per frame)."""
    def __init__(self, specs, base, seed, env, fps):
        self.specs = specs or []
        self.h, self.w = base.shape[:2]
        self.env = env; self.fps = fps; self.seed = seed
        self.cache = {}
        for i, s in enumerate(self.specs):
            if s["type"] in ("die", "revive"):
                self.cache[i] = [bbox(rect_mask((self.h, self.w), r["rect"], s.get("feather_px", 4))) for r in s["regions"]]
            elif s["type"] == "flicker":
                m = rect_mask((self.h, self.w), s["rect"], s.get("feather_px", 6))
                if s.get("emissive_only", True):
                    hsv = cv2.cvtColor(np.clip(base, 0, 1), cv2.COLOR_RGB2HSV)
                    em = np.clip((hsv[..., 2] - 0.45) / 0.3, 0, 1) * np.clip((hsv[..., 1] - 0.25) / 0.3, 0, 1)
                    m = m * cv2.GaussianBlur(em, (0, 0), 2)
                self.cache[i] = bbox(m)
            elif s["type"] in ("lens", "led"):
                yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
                r = s.get("r", 0.01) * self.w
                d2 = ((xx - s["x"] * self.w) ** 2 + (yy - s["y"] * self.h) ** 2)
                core = (np.clip(1.2 - np.sqrt(d2) / r, 0, 1) ** 0.7).astype(np.float32)
                glow = np.exp(-d2 / (2 * (r * s.get("glow_r", 2.5)) ** 2)).astype(np.float32)
                ent = dict(core=bbox(core), glow=bbox(glow))
                if s.get("spill"):
                    rr = r * s["spill"].get("r", 4.0)
                    ent["spill"] = bbox(np.exp(-d2 / (2 * rr * rr)).astype(np.float32))
                self.cache[i] = ent

    def env_at(self, who, tg):
        e = self.env.get(who)
        if e is None:
            return 0.0
        i = int(round(tg * self.fps))
        return float(e[i]) if 0 <= i < len(e) else 0.0

    @staticmethod
    def switch(t, at, dur, seed, on=True):
        """0..1 state of a light switching on (or off) at `at`, with a stuttering flicker."""
        if t < at:
            return 0.0 if on else 1.0
        d = t - at
        if d >= dur:
            return 1.0 if on else 0.0
        rng = np.random.default_rng(seed + int(d * 48))
        v = (d / dur) if rng.random() < 0.6 else rng.random()
        v = 1.0 if v > 0.5 else 0.25 * v
        return v if on else 1 - v

    @staticmethod
    def mul(img, bb, k):
        """img[bb] *= 1 + (k-1)*mask  (k scalar or rgb)."""
        ys, xs, m = bb
        if m.size:
            img[ys, xs] *= 1 + (np.float32(k) - 1) * m[..., None]

    @staticmethod
    def add(img, bb, v):
        ys, xs, m = bb
        if m.size:
            img[ys, xs] += m[..., None] * v

    def apply(self, img, t, tg):
        if not self.specs:
            return img
        img = img.copy()
        for i, s in enumerate(self.specs):
            ty = s["type"]
            if ty in ("die", "revive"):
                to = s.get("to", 0.12); ds = s.get("desat", 0.8)
                for j, (r, bb) in enumerate(zip(s["regions"], self.cache[i])):
                    alive = self.switch(t, r["at"], s.get("dur", 0.4), self.seed + 31 * j + i, on=(ty == "revive"))
                    if alive >= 0.999 or not bb[2].size:
                        continue
                    ys, xs, m = bb
                    reg = img[ys, xs]
                    k = to + (1 - to) * alive
                    dead = reg * (1 - ds) + lum(reg)[..., None] * ds
                    mix = reg * alive + dead * k * (1 - alive)
                    img[ys, xs] = reg * (1 - m[..., None]) + mix * m[..., None]
            elif ty == "flicker":
                n = smooth_noise(self.seed + i, t, 1.0 / s.get("rate_hz", 9), 2)
                self.mul(img, self.cache[i], 1 + s.get("depth", 0.08) * n)
            elif ty in ("lens", "led"):
                c = self.cache[i]
                col = np.float32(s.get("color", [1.0, 0.62, 0.22]))
                if ty == "lens":
                    on = self.switch(t, s.get("on_at", -1), s.get("on_dur", 0.45), self.seed + i, True)
                    if s.get("off_at") is not None:
                        on *= self.switch(t, s["off_at"], 0.3, self.seed + i + 7, False)
                    e = self.env_at(s.get("env"), tg) if s.get("env") else 0.0
                    b = on * (s.get("idle", 0.55) + s.get("env_gain", 0.9) * e)
                    off = s.get("off_level", 0.15)
                    if "spill" in c:
                        so = s["spill"].get("off", 0.1)
                        self.mul(img, c["spill"], so + (1 - so) * min(b, 1.2))
                    self.mul(img, c["core"], off + (1 - off) * min(b, 1.0))
                    if b > 1.0:
                        self.add(img, c["core"], col * (b - 1.0) * 0.5)
                    self.add(img, c["glow"], col * s.get("glow_gain", 0.5) * b)
                else:
                    on = 1.0
                    if s.get("on_at") is not None:
                        on = self.switch(t, s["on_at"], 0.3, self.seed + i, True)
                    if s.get("off_at") is not None:
                        on *= self.switch(t, s["off_at"], s.get("off_dur", 0.5), self.seed + i, False)
                    if on > 0:
                        self.add(img, c["core"], col * 1.1 * on)
                        self.add(img, c["glow"], col * s.get("glow_gain", 0.45) * on)
            elif ty == "flash":
                d = t - s["at"]
                if 0 <= d < s.get("dur", 0.25):
                    img *= 1 + s.get("gain", 0.5) * (1 - d / s.get("dur", 0.25))
        return img


# ------------------------------------------------------------------ focus (depth-masked blur)
class Focus:
    def __init__(self, spec, shape):
        self.s = spec; h, w = shape
        d = np.full((h, w), spec.get("default_depth", 1.0), np.float32)
        for r in spec.get("regions", []):
            m = shape_mask((h, w), r)
            d = d * (1 - m) + r["depth"] * m
        self.depth = d
        self.sigmas = [0, 1.5, 3.0, 5.5, 9.0]

    def apply(self, img, t, dur):
        s = self.s
        u = ease((t - s.get("t0", 0)) / max(1e-6, s.get("t1", dur) - s.get("t0", 0)), s.get("ease", "inout"))
        f = s.get("from", 1.0) + (s.get("to", 1.0) - s.get("from", 1.0)) * u
        coc = np.clip(np.abs(self.depth - f) * s.get("strength", 10.0), 0, self.sigmas[-1])
        out = np.zeros_like(img); wsum = np.zeros(img.shape[:2], np.float32)
        prev = None
        for k, sg in enumerate(self.sigmas):
            lo = self.sigmas[k - 1] if k else -1
            hi = self.sigmas[k + 1] if k + 1 < len(self.sigmas) else 1e9
            wk = np.clip(1 - np.abs(coc - sg) / np.where(coc < sg, sg - lo if k else 1, hi - sg), 0, 1)
            if not wk.any():
                continue
            b = img if sg == 0 else cv2.GaussianBlur(img, (0, 0), sg)
            out += b * wk[..., None]; wsum += wk
        return out / np.maximum(wsum, 1e-6)[..., None]


# ------------------------------------------------------------------ film finish (applied once per frame, last)
class Finish:
    def __init__(self, spec, W, H):
        self.s = spec; self.W = W; self.H = H
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
        self.vig = (1 - spec.get("vignette", 0.38) * np.clip(d - 0.45, 0, 1) ** 1.6)[..., None].astype(np.float32)

    def apply(self, x, seed, frame_i, grade_over=None):
        s = dict(self.s); s.update(grade_over or {})
        W, H = self.W, self.H
        x = np.clip(x, 0, None)
        if s.get("exposure"):
            x = x * 2 ** s["exposure"]
        L = lum(x)[..., None]
        # halation: warm bloom of highlights
        hk = s.get("halation", 0.45)
        if hk:
            hi = np.clip(L - 0.62, 0, 2) * 2.4
            small = cv2.resize(hi * x, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
            bloom = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H), interpolation=cv2.INTER_LINEAR)
            x = x + bloom * np.float32([1.0, 0.55, 0.3]) * hk
        # split tone: teal/navy shadows, amber highlights (the muted teal-and-amber look)
        tone = s.get("split_tone", 1.0)
        L = np.clip(lum(x)[..., None], 0, 1)
        shadow = np.float32([0.004, 0.026, 0.042]) * tone
        high = 1 + (np.float32([1.05, 0.96, 0.84]) - 1) * tone
        x = x * (1 - L) * (1 + (np.float32([0.94, 1.0, 1.03]) - 1) * tone) + x * L * high + shadow * (1 - L) ** 3
        # filmic shoulder (ACES-fit), contrast
        x = np.clip(x, 0, None) * s.get("pre_gain", 1.12)
        x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
        x = np.clip(x, 0, 1)
        g = lum(x)[..., None]
        sat = s.get("saturation", 0.88)
        x = g + (x - g) * sat
        x = x * self.vig
        bl = s.get("black_lift", 0.012)        # filmic black, never digital 0
        x = bl + x * (1 - bl)
        gr = s.get("grain", 0.02)
        if gr:
            if not hasattr(self, "bank"):
                # 31 grain plates (prime count, so the cycle never lines up with a 24/48 frame rhythm),
                # each frame picks one by a seeded hash and flips/offsets it: no visible repeat
                rng = np.random.default_rng(7)
                self.bank = [cv2.resize(rng.standard_normal((H // 2 + 8, W // 2 + 8), dtype=np.float32), (W + 16, H + 16),
                                        interpolation=cv2.INTER_LINEAR) for _ in range(31)]
            h_ = (seed * 2654435761 + frame_i * 40503) & 0xFFFFFFFF
            n = self.bank[h_ % 31]
            ox, oy = (h_ >> 8) % 16, (h_ >> 12) % 16
            n = n[oy:oy + H, ox:ox + W]
            if (h_ >> 16) & 1:
                n = n[:, ::-1]
            n = n[..., None]
            x = x + n * gr * (0.35 + 0.65 * np.clip(1 - np.abs(g - 0.4) * 1.6, 0, 1))
        return np.clip(x, 0, 1)


# ------------------------------------------------------------------ screens (graphics into a quad)
def screen_treat(c, sp, t):
    """CRT/LCD look on content: black level of glass, scanlines, bloom, inner vignette."""
    h, w = c.shape[:2]
    c = np.clip(c, 0, 1)
    tint = sp.get("tint")
    if tint:
        c = c * np.float32(tint)
    sl = sp.get("scanlines", 0.18)
    if sl:
        rows = (0.5 + 0.5 * np.cos(np.arange(h, dtype=np.float32) * math.pi * 2 / sp.get("scan_period", 3.0)))
        c = c * (1 - sl * rows)[:, None, None]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    c = c * (1 - 0.35 * np.clip(d - 0.6, 0, 1))[..., None]
    c = c + cv2.GaussianBlur(c, (0, 0), max(2, w / 120)) * sp.get("bloom", 0.35)
    flick = 1 + sp.get("flicker", 0.02) * math.sin(t * 2 * math.pi * 13.7)
    c = c * flick
    return np.float32(sp.get("glass_black", 0.035)) + c * (1 - sp.get("glass_black", 0.035))


# ------------------------------------------------------------------ the shot
class Shot:
    def __init__(self, shot, ctx):
        self.sh = shot; self.ctx = ctx
        self.W, self.H, self.fps = ctx["W"], ctx["H"], ctx["fps"]
        self.dur = shot["duration_s"]
        self.seed = int(hashlib.md5(shot["id"].encode()).hexdigest()[:8], 16)
        self.log = []
        self.layers = []
        self._prep()

    def path(self, p):
        return self.ctx["resolve"](p)

    def _prep(self):
        sh = self.sh
        layers = sh.get("layers", [])
        if not layers or layers[0].get("kind", "still") not in ("still", "video", "solid", "gfx"):
            layers = [{"kind": "solid", "color": [0, 0, 0]}] + layers
        b = layers[0]
        if b.get("kind") == "solid":
            self.base_src = np.zeros((self.H, self.W, 3), np.float32) + np.float32(b.get("color", [0, 0, 0]))
            self.base_video = None
        elif b.get("kind") == "video" or is_video(self.path(b["src"])):
            self.base_video = Video(self.path(b["src"]))
            self.base_src = self.base_video.at(b.get("in_s", 0))
        elif b.get("kind") == "gfx":
            self.base_video = None
            self.base_gfx = b
            self.base_src = np.zeros((int(b.get("h", 1080)), int(b.get("w", 1920)), 3), np.float32)
        else:
            self.base_video = None
            img = load_rgb(self.path(b["src"]))
            if b.get("crop"):
                x0, y0, x1, y1 = b["crop"]; hh, ww = img.shape[:2]
                img = img[int(y0 * hh):int(y1 * hh), int(x0 * ww):int(x1 * ww)]
            if b.get("flip"):
                img = img[:, ::-1].copy()
            self.base_src = img
        self.base_spec = b
        base = self.base_src
        if self.base_video is None:
            base = apply_relight(apply_grade_local(base, b.get("grade")), b.get("relight"))
            if b.get("blur"):
                base = cv2.GaussianBlur(base, (0, 0), b["blur"])
        self.bh, self.bw = base.shape[:2]
        self.base = base.astype(np.float32)
        # window composite
        self.win = None
        if b.get("window"):
            ws = b["window"]
            m, glass = window_mask(self.base_src if self.base_video is None else self.base, ws)
            pl = ws["plate"]
            pp = self.path(pl["src"])
            if is_video(pp):
                pimg = None; pv = Video(pp)
            else:
                pimg = load_rgb(pp); pv = None
                if pl.get("crop"):
                    x0, y0, x1, y1 = pl["crop"]; hh, ww = pimg.shape[:2]
                    pimg = pimg[int(y0 * hh):int(y1 * hh), int(x0 * ww):int(x1 * ww)]
                if pl.get("flip"):
                    pimg = pimg[:, ::-1].copy()
                pimg = self._plate_level(pimg, pl, glass)
            self.win = dict(mask=m, glass=glass, spec=ws, plate=pimg, video=pv)
            rf = ws.get("reflection", 0.0)
            if rf and self.base_video is None:
                # faint reflection of the lit interior on the glass + a soft diagonal sheen; it sits on
                # top of the plate (screen blend) like real reflections on a cockpit window
                refl = cv2.GaussianBlur(self.base[::-1].copy(), (0, 0), 18) * rf
                yy, xx = np.mgrid[0:self.bh, 0:self.bw].astype(np.float32)
                sheen = np.exp(-(((xx / self.bw) - 0.9 * (yy / self.bh) - 0.25) / 0.09) ** 2) * rf * 0.5
                self.base = self.base + (refl + sheen[..., None] * np.float32([0.8, 0.9, 1.0])) * m[..., None]
            self.log.append(f"window: key={ws.get('key','black')} area={m.mean()*100:.1f}% glass_level={glass:.3f}")
        # extra layers
        for L in layers[1:]:
            k = L.get("kind", "still")
            ent = dict(spec=L, kind=k)
            if k in ("still", "cutout"):
                img = load_rgb(self.path(L["src"]))
                img = apply_relight(apply_grade_local(img, L.get("grade")), L.get("relight"))
                h, w = img.shape[:2]
                if "mask" in L:
                    a = shape_mask((h, w), L["mask"])
                elif "mask_src" in L:
                    a = np.asarray(Image.open(self.path(L["mask_src"])).convert("L").resize((w, h)), np.float32) / 255
                else:
                    a = np.ones((h, w), np.float32)
                if L.get("blur"):
                    img = cv2.GaussianBlur(img, (0, 0), L["blur"])
                if L.get("fill_behind") and (h, w) == (self.bh, self.bw):
                    self.base = inpaint_under(self.base, a)
                ent["rgba"] = np.dstack([img, a]).astype(np.float32)
            elif k == "screen":
                ent["src"] = None
                if L.get("src") and os.path.exists(self.path(L["src"])):
                    p = self.path(L["src"])
                    ent["video"] = Video(p) if is_video(p) else None
                    ent["still"] = None if is_video(p) else load_rgb(p)
                    self.log.append(f"screen content: {L['src']}")
                else:
                    g = L.get("gfx", {})
                    ent["gfx"] = gfx.Gfx(g, self.path)
                    msg = f"PLACEHOLDER screen graphic '{g.get('name')}'"
                    if L.get("src"):
                        msg += f" (expected clip {L['src']} not found)"
                    self.log.append(msg)
            elif k == "text":
                ent["gfx"] = gfx.Gfx(dict(L, name="text"), self.path)
            self.layers.append(ent)
        self.lights = Lights(sh.get("lights"), self.base, self.seed, self.ctx["env"], self.fps)
        self.focus = Focus(sh["focus"], self.base.shape[:2]) if sh.get("focus") else None
        self.cam = sh.get("camera", {})
        self.st0 = cam_at(self.cam, 0, self.dur, self.seed)

    def _plate_level(self, p, pl, glass):
        """Match the plate to the set: crush its black to the glass level, set exposure and tint."""
        lv = pl.get("level", {})
        p = np.clip((p - lv.get("black", 0.03)) / (1 - lv.get("black", 0.03)), 0, 1)
        p = p ** lv.get("gamma", 1.1) * lv.get("gain", 0.8)
        p = p * np.float32(lv.get("tint", [0.96, 0.98, 1.02]))
        if pl.get("blur", 0.7):
            p = cv2.GaussianBlur(p, (0, 0), pl.get("blur", 0.7))
        lift = glass * 0.6 if glass < 0.2 else 0.0      # only a dark glass lifts the plate's black
        return (lift + p).astype(np.float32)

    def _plate_frame(self, t, Mcam):
        w = self.win; pl = w["spec"]["plate"]
        img = w["video"].at(pl.get("in_s", 0) + t * pl.get("speed", 1.0)) if w["video"] else w["plate"]
        if w["video"]:
            img = self._plate_level(img, pl, w["glass"])
        ph, pw = img.shape[:2]
        # place plate in base space: centre (px,py) of plate at base point (x,y), width = scale*base width
        u = t / max(self.dur, 1e-6)
        dr = pl.get("drift", {})
        sc = pl.get("scale", 1.0) * (1 + dr.get("dzoom", 0.0) * u)
        bx = (pl.get("x", 0.5) + dr.get("dx", 0.0) * u) * self.bw
        by = (pl.get("y", 0.4) + dr.get("dy", 0.0) * u) * self.bh
        k = sc * self.bw / pw
        th = math.radians(pl.get("rot", 0.0) + dr.get("drot", 0.0) * u)
        c, s = math.cos(th) * k, math.sin(th) * k
        ax, ay = pl.get("ax", 0.5) * pw, pl.get("ay", 0.5) * ph
        P = np.float64([[c, -s, bx - (c * ax - s * ay)], [s, c, by - (s * ax + c * ay)]])
        st = cam_at(self.cam, t, self.dur, self.seed)
        Mp = compose(cam_matrix(st, (self.bw, self.bh), (self.W, self.H), pl.get("depth", 0.35), self.st0, self.weave), P)
        return warp(img, Mp, (self.W, self.H), border=cv2.BORDER_CONSTANT)

    def frame(self, t, tg, weave):
        self.weave = weave
        W, H = self.W, self.H
        if self.base_video is not None:
            b = self.base_video.at(self.base_spec.get("in_s", 0) + t * self.base_spec.get("speed", 1.0))
            b = apply_relight(apply_grade_local(b, self.base_spec.get("grade")), self.base_spec.get("relight"))
            self.base = b
            self.bh, self.bw = b.shape[:2]
        elif self.base_spec.get("kind") == "gfx":
            if not hasattr(self, "_bgfx"):
                self._bgfx = gfx.Gfx(self.base_spec, self.path)
            self.base = self._bgfx.render(t, self.bw, self.bh)
        base = self.lights.apply(self.base, t, tg)
        if self.focus:
            base = self.focus.apply(base, t, self.dur)
        st = cam_at(self.cam, t, self.dur, self.seed)
        Mb = cam_matrix(st, (self.bw, self.bh), (W, H), 1.0, None, weave)
        out = warp(base, Mb, (W, H))
        if self.win:
            m = warp(self.win["mask"], Mb, (W, H), cv2.INTER_LINEAR)[..., None]
            plate = self._plate_frame(t, Mb)
            gk = self.win["spec"].get("glass_keep", 0.8)
            if self.win["spec"].get("key", "black") == "black":
                # reflections/scratches on the glass stay on top (screen blend)
                comp = 1 - (1 - plate) * (1 - np.clip(out * gk, 0, 1))
            else:
                comp = plate + np.clip(out - 0.85, 0, 1) * gk * 0.3
            out = out * (1 - m) + comp * m
        for ent in self.layers:
            L = ent["spec"]; k = ent["kind"]
            d = L.get("depth", 1.0)
            Mc = cam_matrix(st, (self.bw, self.bh), (W, H), d, self.st0, weave)
            op = L.get("opacity", 1.0)
            if "fade_in" in L or "fade_out" in L:
                op *= min(1, max(0, (t - L.get("t0", 0)) / max(1e-3, L.get("fade_in", 1e-3))))
                if "t1" in L:
                    op *= min(1, max(0, (L["t1"] - t) / max(1e-3, L.get("fade_out", 1e-3))))
            if op <= 0:
                continue
            if k in ("still", "cutout"):
                rgba = ent["rgba"]; h, w = rgba.shape[:2]
                pl = L.get("place", {"x": 0.5, "y": 0.5, "scale": 1.0})
                kk = pl.get("scale", 1.0) * self.bw / w
                P = np.float64([[kk, 0, pl["x"] * self.bw - kk * w / 2], [0, kk, pl["y"] * self.bh - kk * h / 2]])
                r = warp(rgba, compose(Mc, P), (W, H), border=cv2.BORDER_CONSTANT)
                a = np.clip(r[..., 3:4], 0, 1) * op
                out = out * (1 - a) + r[..., :3] * a
            elif k == "screen":
                if ent.get("gfx") is not None:
                    cw, ch = L.get("res", [1280, 720])
                    c = ent["gfx"].render(t, cw, ch)
                elif ent.get("video") is not None:
                    c = ent["video"].at(L.get("in_s", 0) + t)
                else:
                    c = ent["still"]
                c = screen_treat(c, L.get("treat", {}), t)
                ch, cw = c.shape[:2]
                q = np.float32([[p[0] * self.bw, p[1] * self.bh] for p in L["quad"]])
                Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]]), q)
                M3 = np.vstack([Mc, [0, 0, 1]]) @ Hm
                r = cv2.warpPerspective(c, M3, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                a = cv2.warpPerspective(np.ones((ch, cw), np.float32), M3, (W, H), flags=cv2.INTER_LINEAR)
                a = cv2.GaussianBlur(a, (0, 0), 0.8)[..., None] * op
                out = out * (1 - a) + r * a
                # spill: the screen lights its surroundings a little
                sp = L.get("spill", 0.0)
                if sp:
                    small = cv2.resize(r * a, (W // 16, H // 16), interpolation=cv2.INTER_AREA)
                    out = out + cv2.resize(cv2.GaussianBlur(small, (0, 0), 4), (W, H)) * sp
            elif k == "text":
                rgba = ent["gfx"].render_rgba(t, W, H)
                a = rgba[..., 3:4] * op
                gl = L.get("glow", 0.0)
                if gl:
                    g = cv2.GaussianBlur(rgba, (0, 0), 14)
                    out = out + g[..., :3] * g[..., 3:4] * np.float32(L.get("glow_color", [1.0, 0.55, 0.2])) * gl * op
                out = out * (1 - a) + rgba[..., :3] * a
        # motion blur for whip moves: optional cheap directional blur
        mb = self.sh.get("motion_blur")
        if mb:
            for w_ in mb:
                if w_["t0"] <= t <= w_["t1"]:
                    k = int(w_.get("px", 15)) | 1
                    ker = np.zeros((k, k), np.float32)
                    if w_.get("dir", "v") == "v":
                        ker[:, k // 2] = 1.0 / k
                    else:
                        ker[k // 2, :] = 1.0 / k
                    out = cv2.filter2D(out, -1, ker)
        return out


def weave_at(seed, i, amp):
    """Gate weave: smooth sub-pixel random walk (px)."""
    if not amp:
        return (0.0, 0.0)
    t = i / 24.0
    return (amp * 0.6 * smooth_noise(seed + 11, t, 0.9, 2), amp * smooth_noise(seed + 13, t, 0.7, 2))


def render_shot(job, tries=3):
    """Worker entry with retry (a shared machine can kill an encoder under us)."""
    err = None
    for k in range(tries):
        try:
            r = _render_shot(job)
            r["retries"] = k
            return r
        except (BrokenPipeError, RuntimeError) as e:
            err = e
    raise RuntimeError(f"shot {job['shot']['id']} failed {tries}x: {err}")


def _render_shot(job):
    """Worker entry: renders one shot to an H.264 segment. job = dict(shot, ctx_spec, out, ...)."""
    import time, resource
    t0 = time.time()
    r0 = resource.getrusage(resource.RUSAGE_SELF); c0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    ctx = job["ctx"]
    ctx["resolve"] = make_resolver(ctx["vars"])
    ctx["env"] = {k: np.asarray(v, np.float32) for k, v in ctx["env"].items()}
    sh = job["shot"]
    S = Shot(sh, ctx)
    W, H, fps = ctx["W"], ctx["H"], ctx["fps"]
    fin = Finish(ctx["finish"], W, H)
    nf = job["frames"]
    tmp = job["out"] + ".part.mp4"
    enc = ctx["enc"]
    cmd = ["nice", "-n", "10", "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", enc.get("preset", "medium"),
           "-crf", str(enc.get("crf", 18)), "-profile:v", "high", "-pix_fmt", "yuv420p", "-tune", "film",
           "-x264-params", "threads=1:keyint=48", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-colorspace", "bt709", "-an", tmp]
    elog = open(job["out"] + ".enc.log", "w")
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=elog)
    trans_in = sh.get("in", {}); trans_out = sh.get("out", {})
    stills = {}
    for i in range(nf):
        t = i / fps
        tg = job["start_s"] + t
        wv = weave_at(S.seed, i, ctx["finish"].get("weave_px", 0.5))
        img = S.frame(t, tg, wv)
        img = fin.apply(img, S.seed, i, sh.get("grade"))
        if trans_in.get("type") == "fade" and t < trans_in.get("dur", 0.5):
            img = img * ease(t / trans_in.get("dur", 0.5), "inout-soft")
        if trans_out.get("type") == "fade" and t > S.dur - trans_out.get("dur", 0.5):
            img = img * ease((S.dur - t) / trans_out.get("dur", 0.5), "inout-soft")
        fr = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
        ff.stdin.write(fr.tobytes())
        for st in job.get("stills", []):
            if i == int(round(st * fps)):
                stills[st] = fr.copy()
    ff.stdin.close(); rc = ff.wait(); elog.close()
    if rc != 0:
        raise RuntimeError(f"encoder exit {rc}: " + open(job["out"] + ".enc.log").read()[-300:])
    os.replace(tmp, job["out"])
    for st, fr in stills.items():
        Image.fromarray(fr).save(f"{job['still_dir']}/{sh['id']}_{st:.2f}.jpg", quality=90)
    el = time.time() - t0
    r1 = resource.getrusage(resource.RUSAGE_SELF); c1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_py = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
    cpu_enc = (c1.ru_utime + c1.ru_stime) - (c0.ru_utime + c0.ru_stime)
    return dict(id=sh["id"], secs=el, dur=S.dur, cpu_py=cpu_py, cpu_enc=cpu_enc, log=S.log)


def make_resolver(vars_):
    def r(p):
        for k, v in vars_.items():
            p = p.replace("${" + k + "}", v)
        return p
    return r


def preview_shot(job):
    """Graded still frames of one shot at shot-local fractions (fast look-checks, no encode)."""
    import time
    t0 = time.time()
    ctx = job["ctx"]; ctx["resolve"] = make_resolver(ctx["vars"])
    ctx["env"] = {k: np.asarray(v, np.float32) for k, v in ctx["env"].items()}
    sh = job["shot"]; S = Shot(sh, ctx)
    fin = Finish(ctx["finish"], ctx["W"], ctx["H"])
    outs = []
    for f in job["fracs"]:
        t = min(S.dur - 1e-3, max(0.0, f * S.dur)); i = int(t * ctx["fps"])
        img = fin.apply(S.frame(t, job["start_s"] + t, weave_at(S.seed, i, 0)), S.seed, i, sh.get("grade"))
        p = f"{job['out_dir']}/{sh['id']}_{f:.2f}.jpg"
        Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(p, quality=88)
        outs.append(p)
    return dict(id=sh["id"], secs=round(time.time() - t0, 1), log=S.log)
