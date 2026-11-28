#!/usr/bin/env python3
"""Cut-out animation renderer (v1, 28 Nov) — code-driven puppets over real video.

usage: anim.py SHOTLIST.json --cues CUES.json --out DIR [--only ID ...] [--workers 3] [--preview F,..]

Reads every shot that has an "anim" block, renders it to DIR/<id>.mp4 (1920x1080, 24 fps, no audio,
CRF 16). The edit engine then uses these clips as `video` base layers and does sound, subtitles and
the film finish. Coordinates of rigs are pixels of the rig's own picture. See production/ANIMATION-FORMAT.md.
"""
import json, math, os, subprocess, sys, time, hashlib, concurrent.futures as cf
import numpy as np, cv2

W, H, FPS = 1920, 1080, 24

def expand(p, v):
    if not isinstance(p, str):
        return p
    for k, x in v.items():
        p = p.replace("${%s}" % k, x)
    return p

def smooth01(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def rng_for(*keys):
    h = hashlib.md5("|".join(map(str, keys)).encode()).hexdigest()
    return np.random.default_rng(int(h[:8], 16))

# ----------------------------------------------------------------------------------------- speech
class Speech:
    """Mouth cues and loudness envelopes for every speaker on the episode timeline."""
    SHAPES = {  # open (x mouth half-width), width factor, teeth, tongue
        "X": (0.0, 1.0, 0, 0), "A": (0.0, 0.95, 0, 0), "B": (0.16, 0.85, 1, 0),
        "C": (0.40, 0.92, 1, 0), "D": (0.72, 1.0, 1, 1), "E": (0.42, 0.66, 0.5, 0),
        "F": (0.26, 0.42, 0, 0), "G": (0.14, 0.85, 1, 0), "H": (0.48, 0.86, 1, 1)}

    def __init__(self, cues):
        self.lines = cues["lines"]

    def _lines(self, spk):
        return [l for l in self.lines if l["speaker"] == spk]

    def mouth(self, spk, t):
        """Blended mouth params at absolute time t: (open, width, teeth, tongue)."""
        for l in self._lines(spk):
            lt = t - l["start_s"]
            if -0.05 <= lt <= l["dur"] + 0.05:
                prev, cur, c0 = "X", "X", None
                for c in l["cues"]:
                    if c["t0"] <= lt < c["t1"]:
                        cur, c0 = c["v"], c["t0"]
                        break
                    prev = c["v"]
                a = np.array(self.SHAPES.get(cur, self.SHAPES["X"]))
                if c0 is None:
                    return a
                b = np.array(self.SHAPES.get(prev, self.SHAPES["X"]))
                k = smooth01((lt - c0) / 0.06)
                return b + (a - b) * k
        return np.array(self.SHAPES["X"])

    def env(self, spk, t, smooth=0.0):
        """Loudness 0..1 of speaker at t (48 Hz envelope), optionally averaged over +-smooth s."""
        if smooth > 0:
            ts = np.linspace(t - smooth, t + smooth, 7)
            return float(np.mean([self.env(spk, x) for x in ts]))
        for l in self._lines(spk):
            lt = t - l["start_s"]
            if 0 <= lt < l["dur"]:
                i = int(lt * 48)
                e = l["env"]
                return float(e[min(i, len(e) - 1)])
        return 0.0

    def speaking(self, spk, t):
        return any(0 <= t - l["start_s"] < l["dur"] for l in self._lines(spk))

# ------------------------------------------------------------------------------------------- rigs
_RIG_CACHE = {}

def load_rgba(src, key, v):
    src = expand(src, v)
    ck = (src, json.dumps(key, sort_keys=True))
    if ck in _RIG_CACHE:
        return _RIG_CACHE[ck]
    im = cv2.imread(src, cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32) / 255.0
    if key and key.get("type") == "green":
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        d = g - np.maximum(r, b)
        a = 1.0 - np.clip((d - key.get("t0", 0.12)) / (key.get("t1", 0.32) - key.get("t0", 0.12)), 0, 1)
        a = cv2.erode(a, np.ones((3, 3), np.uint8))
        a = cv2.GaussianBlur(a, (0, 0), 0.8)
        im[..., 1] = np.minimum(g, np.maximum(r, b) + 0.03)  # despill
    elif key and key.get("type") == "mask":
        a = cv2.imread(expand(key["src"], v), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
    else:
        a = np.ones(im.shape[:2], np.float32)
    rgba = np.dstack([im * a[..., None], a]).astype(np.float32)  # premultiplied
    _RIG_CACHE[ck] = rgba
    return rgba

def soft_ellipse(shape, cx, cy, rx, ry, feather=0.35):
    h, w = shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - cx) / max(rx, 1)) ** 2 + ((y - cy) / max(ry, 1)) ** 2)
    return np.clip((1 + feather - d) / feather, 0, 1) if feather > 0 else (d <= 1).astype(np.float32)

def draw_ss(shape, polys, ss=4, blur=0.0):
    """Anti-aliased coverage mask (float 0..1) of filled polygons, by supersampling."""
    h, w = shape
    m = np.zeros((h * ss, w * ss), np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.round(np.asarray(p) * ss).astype(np.int32)], 255)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    if blur > 0:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    return m

def polyline_ss(shape, pts, thick, ss=4, blur=0.0):
    h, w = shape
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.polylines(m, [np.round(np.asarray(pts) * ss).astype(np.int32)], False, 255, max(1, int(thick * ss)), cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    if blur > 0:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    return m

def paint(rgba, mask, color, alpha=1.0):
    """Paint premultiplied colour over an RGBA ROI where mask (0..1)."""
    m = (mask * alpha)[..., None]
    c = np.array(list(color) + [1.0], np.float32)
    c[:3] *= 1.0
    # keep the existing alpha where the picture is already opaque
    out = rgba * (1 - m) + np.concatenate([np.array(color, np.float32) * rgba[..., 3:4], rgba[..., 3:4]], -1) * m
    return out

class Puppet:
    """One character picture with face landmarks; produces an animated RGBA each frame."""

    def __init__(self, rig, v, seed):
        self.r = rig
        self.img = load_rgba(rig["src"], rig.get("key"), v)
        self.h, self.w = self.img.shape[:2]
        self.seed = seed
        self.style = rig.get("style", "ink")
        self.phase = float(rng_for(seed, "phase").uniform(0, 6.28))
        rg = rng_for(seed, "blink")
        ts, t = [], rg.uniform(0.3, 1.6)
        while t < 200:
            ts.append(t)
            t += rg.uniform(1.8, 4.2)
        self.blinks = ts
        rg = rng_for(seed, "dart")
        ds, t = [], 0.0
        while t < 200:
            ds.append((t, rg.uniform(-1, 1), rg.uniform(-0.4, 0.4)))
            t += rg.uniform(0.7, 1.9)
        self.darts = ds
        self.lid_col = []
        for (ex, ey, rx, ry) in rig.get("eyes", []):
            y0 = int(ey - ry * 1.9); x0, x1 = int(ex - rx * 0.5), int(ex + rx * 0.5)
            patch = self.img[max(y0 - 2, 0):y0 + 2, x0:x1]
            a = np.clip(patch[..., 3:4], 1e-3, 1)
            self.lid_col.append(np.median((patch[..., :3] / a).reshape(-1, 3), 0))

    # --- channels
    def blink(self, t):
        b = 0.0
        for t0 in self.blinks:
            dt = t - t0
            if 0 <= dt < 0.2:
                b = max(b, smooth01(dt / 0.06) if dt < 0.06 else (1.0 if dt < 0.09 else 1 - smooth01((dt - 0.09) / 0.11)))
        return b

    def dart(self, t):
        prev, cur = (0, 0.0, 0.0), (0, 0.0, 0.0)
        for d in self.darts:
            if d[0] > t:
                break
            prev, cur = cur, d
        k = smooth01((t - cur[0]) / 0.08)
        return (prev[1] + (cur[1] - prev[1]) * k, prev[2] + (cur[2] - prev[2]) * k)

    # --- frame
    def frame(self, t, speech, spk, look=None, extra=None):
        r = self.r
        img = self.img
        extra = extra or {}
        if "face" not in r and "lens" not in r and "parts" not in r:
            return img
        out = img.copy()
        if "mouth" in r:
            out = self._face(out, t, speech, spk, look, extra)
        for part in r.get("parts", []):
            ang = extra.get(part["name"] + "_rot", 0.0)
            dy = extra.get(part["name"] + "_dy", 0.0)
            if part["name"] == "head":
                e = speech.env(spk, t, 0.12) if spk else 0.0
                ang += part.get("sway", 1.4) * math.sin(2 * math.pi * t / 4.3 + self.phase) \
                    + part.get("talk", 2.6) * e * math.sin(2 * math.pi * t * 0.95 + 1.0)
                dy += part.get("nod", 3.0) * e * math.sin(2 * math.pi * t * 1.9)
            if abs(ang) > 1e-3 or abs(dy) > 1e-3:
                out = self._rotate_part(out, part, ang, dy)
        if "lens" in r:
            out = self._lens(out, t, speech, spk, extra)
        return out

    def _rotate_part(self, im, part, ang, dy):
        x0, y0, x1, y1 = part["roi"]
        px, py = part["pivot"]
        roi = im[y0:y1, x0:x1]
        hh, ww = roi.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        X, Y = xx + x0, yy + y0
        reg = part["region"]  # ellipse cx cy rx ry (weight 1 inside, soft edge)
        wgt = soft_ellipse((hh, ww), reg[0] - x0, reg[1] - y0, reg[2], reg[3], part.get("feather", 0.45))
        a = -math.radians(ang) * wgt
        ca, sa = np.cos(a), np.sin(a)
        sx = px + ca * (X - px) - sa * (Y - py)
        sy = py + sa * (X - px) + ca * (Y - py) - dy * wgt
        warped = cv2.remap(im, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        im = im.copy()
        # only replace inside the ROI; outside the region weight the source is unchanged
        im[y0:y1, x0:x1] = warped[0:hh, 0:ww] if warped.shape[:2] == (hh, ww) else warped
        return im

    def _face(self, im, t, speech, spk, look, extra):
        r = self.r
        mx, my = r["mouth"]
        hw = r["mouth_w"]
        ang = math.radians(r.get("mouth_ang", 0.0))
        chin = r["chin"]
        fx0, fy0, fx1, fy1 = r["face"]
        roi = im[fy0:fy1, fx0:fx1].copy()
        hh, ww = roi.shape[:2]
        if spk and extra.get("freeze_mouth") is None:
            op, wf, teeth, tongue = speech.mouth(spk, t)
        elif extra.get("freeze_mouth") is not None:
            op, wf, teeth, tongue = speech.mouth(spk, extra["freeze_mouth"])
        else:
            op, wf, teeth, tongue = Speech.SHAPES["X"]
        opx = op * hw * r.get("open_gain", 1.0)
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        X, Y = xx + fx0, yy + fy0
        # rotate into mouth frame
        ca, sa = math.cos(-ang), math.sin(-ang)
        U = ca * (X - mx) - sa * (Y - my)
        V = sa * (X - mx) + ca * (Y - my)
        mapx, mapy = X.copy(), Y.copy()
        if opx > 0.2:
            span = max(chin - my, 10)
            prof = np.where(V < 0, 0.0, np.where(V < span * 0.22, smooth_np(V / (span * 0.22)),
                            np.where(V < span, 1.0, np.clip(1 - (V - span) / (span * 0.7), 0, 1))))
            lat = np.exp(-(U / (hw * r.get("jaw_w", 2.1))) ** 2)
            d = opx * prof * lat
            mapx = X + d * math.sin(ang)
            mapy = Y - d * math.cos(ang)
        # eye darts
        dx, dyy = self.dart(t)
        if look is not None:
            dx, dyy = look
        for (ex, ey, rx, ry) in r.get("eyes", []):
            wgt = np.exp(-(((X - ex) / (rx * 0.75)) ** 2 + ((Y - ey) / (ry * 0.9)) ** 2))
            mapx = mapx - dx * rx * 0.16 * wgt
            mapy = mapy - dyy * ry * 0.18 * wgt
        roi = cv2.remap(im, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)
        # mouth interior
        if opx > 0.6:
            n = 24
            hwx = hw * wf
            xs = np.linspace(-hwx, hwx, n)
            prof = (1 - (xs / hwx) ** 2)
            top = -0.12 * opx * prof ** 0.6
            bot = opx * prof ** 0.75
            poly_u = np.concatenate([np.stack([xs, top], 1), np.stack([xs[::-1], bot[::-1]], 1)])
            def to_roi(p):
                c, s = math.cos(ang), math.sin(ang)
                return np.stack([mx + c * p[:, 0] - s * p[:, 1] - fx0, my + s * p[:, 0] + c * p[:, 1] - fy0], 1)
            ink = self.style == "ink"
            inner = draw_ss((hh, ww), [to_roi(poly_u)], blur=0.0 if ink else 0.8)
            colI = r.get("mouth_col", [0.30, 0.08, 0.10] if ink else [0.20, 0.07, 0.07])
            roi = paint(roi, inner, colI)
            if teeth > 0.05:
                th = min(opx * 0.42, hw * 0.22)
                tp = np.concatenate([np.stack([xs * 0.86, top - 1], 1), np.stack([xs[::-1] * 0.86, (top + th)[::-1]], 1)])
                tm = draw_ss((hh, ww), [to_roi(tp)], blur=0.0 if ink else 0.7) * inner
                roi = paint(roi, tm, r.get("teeth_col", [0.95, 0.93, 0.88] if ink else [0.80, 0.76, 0.70]), min(1, teeth))
            if tongue > 0.05:
                tg = np.stack([xs * 0.6, bot * 0.55 + opx * 0.45 * prof], 1)
                tgp = np.concatenate([tg, np.stack([xs[::-1] * 0.6, bot[::-1] + 2], 1)])
                gm = draw_ss((hh, ww), [to_roi(tgp)], blur=0.6) * inner
                roi = paint(roi, gm, [0.78, 0.35, 0.36] if ink else [0.55, 0.25, 0.25], tongue * 0.9)
            if ink:
                outline = polyline_ss((hh, ww), np.concatenate([to_roi(poly_u), to_roi(poly_u)[:1]]), r.get("ink_w", 1.6))
                roi = paint(roi, outline, r.get("ink_col", [0.16, 0.07, 0.05]), 0.9)
            else:
                lipm = polyline_ss((hh, ww), np.concatenate([to_roi(poly_u), to_roi(poly_u)[:1]]), 2.5, blur=1.2)
                roi = paint(roi, lipm, r.get("lip_col", [0.45, 0.25, 0.22]), 0.5)
        # eyelids
        b = self.blink(t)
        b = max(b, extra.get("lids", 0.0))
        if b > 0.02:
            for i, (ex, ey, rx, ry) in enumerate(r.get("eyes", [])):
                RX, RY = rx * 1.22, ry * 1.55
                edge = -RY + 2 * RY * b * 0.92
                xs = np.linspace(-RX, RX, 28)
                el = RY * np.sqrt(np.clip(1 - (xs / RX) ** 2, 0, 1))
                lid_bot = np.minimum(edge + (0.25 * RY * b) * (1 - (xs / RX) ** 2), el)
                top = -el
                poly = np.concatenate([np.stack([xs, top - 1.5], 1), np.stack([xs[::-1], lid_bot[::-1]], 1)])
                ea = math.radians(r.get("eye_ang", r.get("mouth_ang", 0.0)))
                c, s = math.cos(ea), math.sin(ea)
                def tr(p):
                    return np.stack([ex + c * p[:, 0] - s * p[:, 1] - fx0, ey + s * p[:, 0] + c * p[:, 1] - fy0], 1)
                m = draw_ss((hh, ww), [tr(poly)], blur=0.5 if self.style == "ink" else 1.3)
                col = self.lid_col[i] * r.get("lid_shade", 0.9)
                roi = paint(roi, m, col)
                lash = polyline_ss((hh, ww), tr(np.stack([xs, lid_bot], 1)[3:-3]),
                                   r.get("lash_w", 2.0) if self.style == "ink" else 1.6,
                                   blur=0.0 if self.style == "ink" else 0.9)
                roi = paint(roi, lash * min(1, b * 1.6), r.get("lash_col", [0.12, 0.07, 0.05]), 0.95 if self.style == "ink" else 0.6)
        im[fy0:fy1, fx0:fx1] = roi
        return im

    def _lens(self, im, t, speech, spk, extra):
        lx, ly, lr = self.r["lens"]
        e = speech.env(spk, t, 0.04) if spk else 0.0
        iris = lr * (0.62 - 0.30 * e + 0.04 * math.sin(t * 2.3)) * extra.get("iris_gain", 1.0)
        x0, y0, x1, y1 = int(lx - lr * 1.2), int(ly - lr * 1.2), int(lx + lr * 1.2), int(ly + lr * 1.2)
        roi = im[y0:y1, x0:x1]
        hh, ww = roi.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        d = np.sqrt((xx + x0 - lx) ** 2 + (yy + y0 - ly) ** 2)
        ring = np.clip((d - iris) / 2.0, 0, 1) * np.clip((lr * 0.92 - d) / 2.0, 0, 1)
        roi = paint(roi, ring, [0.16, 0.09, 0.03], 0.82)
        core = np.clip(1 - d / max(iris, 1), 0, 1) ** 1.5 * (0.35 + 0.9 * e)
        roi = roi.copy()
        roi[..., :3] = np.clip(roi[..., :3] + core[..., None] * np.array([1.0, 0.72, 0.30]) * roi[..., 3:4], 0, 4)
        im[y0:y1, x0:x1] = roi
        return im

def smooth_np(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

# ------------------------------------------------------------------------------------- video read
class VideoReader:
    def __init__(self, src, in_s=0.0, speed=1.0, crop=None, w=W, h=H, loop=True):
        self.src, self.in_s, self.speed, self.crop, self.w, self.h, self.loop = src, in_s, speed, crop, w, h, loop
        self.p = None
        self._open(in_s)
        self.last = np.zeros((h, w, 3), np.float32)

    def _open(self, start):
        vf = []
        if self.crop:
            x0, y0, x1, y1 = self.crop
            vf.append(f"crop=iw*{x1 - x0}:ih*{y1 - y0}:iw*{x0}:ih*{y0}")
        vf.append(f"scale={self.w}:{self.h}:force_original_aspect_ratio=increase:flags=lanczos,crop={self.w}:{self.h}")
        if self.speed != 1.0:
            vf.insert(0, f"setpts=PTS/{self.speed}")
        vf.append(f"fps={FPS}")
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", self.src, "-an", "-vf", ",".join(vf),
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)

    def read(self):
        n = self.w * self.h * 3
        b = self.p.stdout.read(n)
        if len(b) < n:
            if self.loop:
                self.p.stdout.close(); self.p.wait()
                self._open(self.in_s)
                b = self.p.stdout.read(n)
            if len(b) < n:
                return self.last
        self.last = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3).astype(np.float32) / 255.0
        return self.last

    def close(self):
        try:
            self.p.stdout.close(); self.p.kill()
        except Exception:
            pass

# ------------------------------------------------------------------------------------------- shot
def affine(scale_x, scale_y, rot_deg, anchor_src, anchor_dst):
    a = math.radians(rot_deg)
    c, s = math.cos(a), math.sin(a)
    M = np.array([[c * scale_x, -s * scale_y, 0], [s * scale_x, c * scale_y, 0]], np.float64)
    p = M[:, :2] @ np.array(anchor_src)
    M[:, 2] = np.array(anchor_dst) - p
    return M

def cam_apply(M, cam, depth):
    """Apply camera (zoom about frame centre + offset), scaled by layer depth."""
    z, ox, oy, rot = cam
    zd = 1 + (z - 1) * depth
    C = affine(zd, zd, rot * depth, (W / 2, H / 2), (W / 2 + ox * depth, H / 2 + oy * depth))
    A = np.vstack([M, [0, 0, 1]])
    B = np.vstack([C, [0, 0, 1]])
    return (B @ A)[:2]

def over(dst, rgba):
    a = rgba[..., 3:4]
    dst *= (1 - a)
    dst += rgba[..., :3]
    return dst

def warp_rgba(rgba, M):
    return cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

def add_glow(dst, x, y, r, color, k):
    if k <= 0.001:
        return
    R = int(r * 3)
    x0, y0, x1, y1 = max(int(x - R), 0), max(int(y - R), 0), min(int(x + R), W), min(int(y + R), H)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)) * k
    dst[y0:y1, x0:x1] += g[..., None] * np.array(color, np.float32)

def window_mask(img_rgb, region, thresh=0.06):
    h, w = img_rgb.shape[:2]
    x0, y0, x1, y1 = [int(v) for v in (region[0] * w, region[1] * h, region[2] * w, region[3] * h)]
    lum = img_rgb.max(2)
    m = np.zeros((h, w), np.uint8)
    m[y0:y1, x0:x1] = (lum[y0:y1, x0:x1] < thresh).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return np.zeros((h, w), np.float32)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    m = (lab == k).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    m = np.zeros_like(m)
    cv2.drawContours(m, cnts, -1, 255, -1)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m.astype(np.float32) / 255.0, (0, 0), 1.2)

def eval_keys(keys, t, default=0.0):
    """keys: [[t, v], ...] -> smooth interpolation."""
    if not keys:
        return default
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * smooth01((t - t0) / max(t1 - t0, 1e-6))
    return keys[-1][1]

class ShotRenderer:
    def __init__(self, shot, rigs, speech, v, t_abs0):
        self.s, self.a = shot, shot["anim"]
        self.rigs, self.speech, self.v, self.T0 = rigs, speech, v, t_abs0
        self.dur = shot["duration_s"]
        self.readers = {}
        self.cache = {}

    def reader(self, key, spec):
        if key not in self.readers:
            self.readers[key] = VideoReader(expand(spec["src"], self.v), spec.get("in_s", 0.0), spec.get("speed", 1.0),
                                            spec.get("crop"), loop=spec.get("loop", True))
        return self.readers[key]

    def camera(self, t):
        c = self.a.get("camera", {})
        k = t / self.dur
        z = c.get("z0", 1.0) * (c.get("z1", c.get("z0", 1.0)) / c.get("z0", 1.0)) ** smooth01(k) if "z0" in c else 1.0
        px = c.get("pan", [0, 0]); py = c.get("tilt", [0, 0])
        ox = px[0] + (px[1] - px[0]) * smooth01(k)
        oy = py[0] + (py[1] - py[0]) * smooth01(k)
        amp = c.get("drift", 6.0)
        ox += amp * math.sin(2 * math.pi * t / 5.7 + 0.4)
        oy += amp * 0.6 * math.sin(2 * math.pi * t / 4.3 + 1.3)
        rot = c.get("roll", 0.25) * math.sin(2 * math.pi * t / 6.1)
        for sh in c.get("shake", []):
            dt = t - sh["at"]
            if 0 <= dt < sh.get("decay_s", 0.4) * 3:
                e = sh["amp_px"] * math.exp(-dt / sh.get("decay_s", 0.4))
                ox += e * math.sin(2 * math.pi * 13 * dt)
                oy += e * math.cos(2 * math.pi * 11 * dt)
        return (z, ox, oy, rot)

    def set_layer(self, L):
        key = ("set", L["src"])
        if key not in self.cache:
            img = cv2.imread(expand(L["src"], self.v))[:, :, ::-1].astype(np.float32) / 255.0
            if L.get("grade"):
                g = L["grade"]
                img = np.clip(img * g.get("gain", 1.0) + g.get("lift", 0.0), 0, 1) ** g.get("gamma", 1.0)
            a = np.ones(img.shape[:2], np.float32)
            if L.get("window"):
                a = 1 - window_mask(img, L["window"]["region"], L["window"].get("thresh", 0.06))
            if L.get("blur"):
                img = cv2.GaussianBlur(img, (0, 0), L["blur"])
            rgba = np.dstack([img * a[..., None], a]).astype(np.float32)
            h, w = img.shape[:2]
            crop = L.get("crop", [0, 0, 1, 1])
            cw, ch = (crop[2] - crop[0]) * w, (crop[3] - crop[1]) * h
            sc = max(W / cw, H / ch) * L.get("overscan", 1.06)
            M = affine(sc, sc, 0, ((crop[0] + crop[2]) / 2 * w, (crop[1] + crop[3]) / 2 * h), (W / 2, H / 2))
            self.cache[key] = (rgba, M)
        return self.cache[key]

    def render_frame(self, i):
        t = i / FPS
        T = self.T0 + t
        cam = self.camera(t)
        out = np.zeros((H, W, 3), np.float32)
        glows = []
        for li, L in enumerate(self.a["layers"]):
            k = L["kind"]
            if "t0" in L and t < L["t0"]:
                continue
            if "t1" in L and t >= L["t1"]:
                continue
            depth = L.get("depth", 1.0)
            if k == "video":
                fr = self.reader(li, L).read()
                if L.get("grade"):
                    g = L["grade"]
                    fr = np.clip(fr * g.get("gain", 1.0) + g.get("lift", 0.0), 0, 1)
                os_ = L.get("overscan", 1.08)
                dr = L.get("drift", [0, 0])
                off = L.get("offset", [0, 0])
                M = affine(os_, os_, 0, (W / 2, H / 2), (W / 2 + off[0] + dr[0] * t / self.dur, H / 2 + off[1] + dr[1] * t / self.dur))
                M = cam_apply(M, cam, depth)
                fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                if L.get("freeze_at") is not None and t >= L["freeze_at"]:
                    fr = self.cache.setdefault(("freeze", li), fr)
                out = fr.copy() if li == 0 else over(out, np.dstack([fr, np.ones((H, W, 1), np.float32)]))
            elif k == "set":
                rgba, M = self.set_layer(L)
                bri = eval_keys(L.get("bright", []), t, 1.0)
                fl = L.get("flicker", 0.0)
                if fl:
                    bri *= 1 + fl * (0.5 * math.sin(t * 37.0) + 0.5 * math.sin(t * 23.0 + 1))
                bri *= 1 + 0.025 * math.sin(2 * math.pi * t / 2.7)
                lay = warp_rgba(rgba, cam_apply(M, cam, depth))
                lay[..., :3] *= bri
                out = over(out, lay)
            elif k in ("puppet", "prop"):
                out = self.puppet_layer(L, t, T, cam, out, glows, li)
            elif k == "callscreen":
                out = self.callscreen(L, t, T, cam, out, li)
        for (x, y, r, col, kk) in glows:
            add_glow(out, x, y, r, col, kk)
        if self.a.get("pixelate"):
            p = self.a["pixelate"]
            if p.get("t0", 0) <= t:
                f = p.get("block", 18)
                sm = cv2.resize(out, (W // f, H // f), interpolation=cv2.INTER_AREA)
                out = cv2.resize(sm, (W, H), interpolation=cv2.INTER_NEAREST)
        return np.clip(out, 0, 1)

    def puppet_rgba(self, L, t, T, pose_name, li):
        rig = self.rigs[pose_name]
        key = ("pup", li, pose_name)
        if key not in self.cache:
            self.cache[key] = Puppet(rig, self.v, f"{self.s['id']}-{li}-{pose_name}")
        P = self.cache[key]
        extra = {}
        for ch, keys in L.get("channels", {}).items():
            extra[ch] = eval_keys(keys, t)
        if L.get("freeze_at") is not None and t >= L["freeze_at"]:
            extra["freeze_mouth"] = self.T0 + L["freeze_at"]
            T = self.T0 + L["freeze_at"]
        look = L.get("look")
        if L.get("look_keys"):
            look = (eval_keys(L["look_keys"]["x"], t), eval_keys(L["look_keys"].get("y", []), t))
        spk = L.get("speaker")
        return P, P.frame(T, self.speech, spk, look, extra), rig

    def placement(self, L, rig, t, T, first_rig):
        h_img = rig["size"][1]
        sc = L["h"] * H / h_img
        if first_rig is not None and first_rig is not rig and "eyes" in rig and "eyes" in first_rig:
            fe = np.mean([[e[0], e[1]] for e in first_rig["eyes"]], 0)
            ce = np.mean([[e[0], e[1]] for e in rig["eyes"]], 0)
            sc0 = L["h"] * H / first_rig["size"][1]
            fx = L["x"] * W + (fe[0] - first_rig["size"][0] / 2) * sc0
            fy = L["y"] * H + (fe[1] - first_rig["size"][1]) * sc0
            anchor_src = (ce[0], ce[1]); anchor_dst = (fx, fy)
            bottom = (rig["size"][0] / 2, rig["size"][1])
            # convert to bottom anchor so breathing pivots at the bottom
            anchor_dst = (fx + (bottom[0] - ce[0]) * sc, fy + (bottom[1] - ce[1]) * sc)
            anchor_src = bottom
        else:
            anchor_src = (rig["size"][0] / 2, rig["size"][1])
            anchor_dst = (L["x"] * W, L["y"] * H)
        spk = L.get("speaker")
        e = self.speech.env(spk, T, 0.15) if spk else 0.0
        seed = float(rng_for(L.get("name", "p")).uniform(0, 6.28))
        breath = L.get("breath", 1.0)
        sy = 1 + breath * 0.009 * math.sin(2 * math.pi * t / 3.4 + seed)
        sx = 1 + breath * 0.003 * math.sin(2 * math.pi * t / 3.4 + seed + 0.5)
        rot = L.get("sway", 0.5) * math.sin(2 * math.pi * t / 5.1 + seed) + 0.7 * e * math.sin(2 * math.pi * t * 0.7)
        rot += eval_keys(L.get("rot_keys", []), t)
        dx = eval_keys(L.get("x_keys", []), t) * W
        dy = eval_keys(L.get("y_keys", []), t) * H + L.get("bob", 0.0) * math.sin(2 * math.pi * t / 2.1 + seed) \
            - 4.0 * e * abs(math.sin(2 * math.pi * t * 1.4))
        M = affine(sc * sx, sc * sy, rot, anchor_src, (anchor_dst[0] + dx, anchor_dst[1] + dy))
        if L.get("flip"):
            F = np.array([[-1, 0, rig["size"][0]], [0, 1, 0], [0, 0, 1]], np.float64)
            M = (np.vstack([M, [0, 0, 1]]) @ F)[:2]
        return M

    def puppet_layer(self, L, t, T, cam, out, glows, li):
        poses = L.get("poses") or [[0, L["rig"]]]
        cur, prv, tsw = poses[0][1], None, None
        for (ts, name) in poses:
            if t >= ts:
                prv, cur, tsw = cur, name, ts
        first_rig = self.rigs[poses[0][1]]
        depth = L.get("depth", 1.2)
        P, rgba, rig = self.puppet_rgba(L, t, T, cur, li)
        M = cam_apply(self.placement(L, rig, t, T, first_rig), cam, depth)
        lay = warp_rgba(rgba, M)
        if L.get("shade"):
            lay[..., :3] *= L["shade"]
        xf = 0.12
        if prv is not None and tsw is not None and t - tsw < xf and prv != cur:
            k = smooth01((t - tsw) / xf)
            P2, rgba2, rig2 = self.puppet_rgba(L, t, T, prv, li)
            M2 = cam_apply(self.placement(L, rig2, t, T, first_rig), cam, depth)
            lay2 = warp_rgba(rgba2, M2)
            lay = lay * k + lay2 * (1 - k)
        if L.get("shadow", 0) > 0:
            a = cv2.GaussianBlur(lay[..., 3], (0, 0), 14)
            a = np.roll(a, (14, 10), (0, 1)) * L["shadow"]
            out *= (1 - a[..., None])
        out = over(out, lay)
        # glows (engines, lens)
        if "engines" in rig:
            g = eval_keys(L.get("glow_keys", []), t, 1.0) * (0.85 + 0.15 * math.sin(t * 31) * math.sin(t * 17))
            for (ex, ey, er) in rig["engines"]:
                p = M @ np.array([ex, ey, 1.0])
                s = math.hypot(M[0, 0], M[1, 0])
                glows.append((p[0], p[1], er * s * 0.6, [0.35, 0.65, 1.0], 0.9 * g))
                glows.append((p[0], p[1], er * s * 1.6, [0.25, 0.45, 1.0], 0.35 * g))
        if "lens" in rig:
            lx, ly, lr = rig["lens"]
            p = M @ np.array([lx, ly, 1.0])
            s = math.hypot(M[0, 0], M[1, 0])
            e = self.speech.env(L.get("speaker"), T, 0.04) if L.get("speaker") else 0.0
            glows.append((p[0], p[1], lr * s * 1.4, [1.0, 0.62, 0.22], 0.12 + 0.55 * e))
            glows.append((p[0], p[1], lr * s * 3.5, [1.0, 0.55, 0.18], 0.05 + 0.18 * e))
        return out

    def callscreen(self, L, t, T, cam, out, li):
        fz = L.get("freeze_at")
        if fz is not None and t >= fz and ("csfz", li) in self.cache:
            fr0 = self.cache[("csfz", li)]
            M2 = cam_apply(affine(1.04, 1.04, 0, (W / 2, H / 2), (W / 2, H / 2)), cam, 1.0)
            return cv2.warpAffine(fr0, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        fr = self.reader(("cs", li), L).read().copy()
        key = ("matte", li)
        if key not in self.cache:
            m = cv2.imread(expand(L["matte"], self.v), 0).astype(np.float32) / 255.0
            self.cache[key] = m
        m = self.cache[key]
        ys, xs = np.where(m > 0.5)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        P, rgba, rig = self.puppet_rgba(L, t, T, L["rig"], li)
        rw, rh = rig["size"]
        sc = max((x1 - x0) / rw, (y1 - y0) / rh) * L.get("zoom", 1.04)
        bob = 3 * math.sin(2 * math.pi * t / 3.1)
        M = affine(sc, sc, 0.4 * math.sin(2 * math.pi * t / 4.7), (rw / 2, rh / 2), ((x0 + x1) / 2, (y0 + y1) / 2 + bob))
        person = cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR)[..., :3]
        flat = np.median(fr[y0 + 60:y1 - 60, x0 + 300:x1 - 300].reshape(-1, 3), 0)
        bright = (fr.max(2) - flat.max()) > 0.10
        keep = cv2.GaussianBlur((bright & (m > 0.5)).astype(np.float32), (0, 0), 1.0)
        comp = person * m[..., None] + fr * (1 - m[..., None])
        comp = comp * (1 - keep[..., None]) + fr * keep[..., None]
        if fz is not None and t >= fz:
            self.cache[("csfz", li)] = comp
        M2 = cam_apply(affine(1.04, 1.04, 0, (W / 2, H / 2), (W / 2, H / 2)), cam, 1.0)
        return cv2.warpAffine(comp, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def close(self):
        for r in self.readers.values():
            r.close()

def render_shot(args):
    shot, rigs, cues, v, T0, outdir, preview = args
    sp = Speech(cues)
    R = ShotRenderer(shot, rigs, sp, v, T0)
    n = int(round(shot["duration_s"] * FPS))
    t0 = time.time()
    if preview:
        os.makedirs(os.path.join(outdir, "preview"), exist_ok=True)
        want = {min(int(f * n), n - 1): f for f in preview}
        for j in range(max(want) + 1):
            fr = R.render_frame(j)
            if j in want:
                cv2.imwrite(os.path.join(outdir, "preview", f"{shot['id']}_{want[j]:.2f}.jpg"),
                            (np.clip(fr, 0, 1)[:, :, ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
        R.close()
        return shot["id"], 0, time.time() - t0
    path = os.path.join(outdir, shot["id"] + ".mp4")
    enc = subprocess.Popen(["nice", "-n", "5", "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "15",
                            "-pix_fmt", "yuv420p", "-threads", "1", path + ".tmp.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        fr = R.render_frame(i)
        enc.stdin.write((fr * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    os.replace(path + ".tmp.mp4", path)
    R.close()
    cpu = time.process_time()
    return shot["id"], n, time.time() - t0

def main():
    a = sys.argv
    sl = json.load(open(a[1]))
    cues = json.load(open(a[a.index("--cues") + 1]))
    outdir = a[a.index("--out") + 1]
    os.makedirs(outdir, exist_ok=True)
    only = []
    if "--only" in a:
        i = a.index("--only") + 1
        while i < len(a) and not a[i].startswith("--"):
            only.append(a[i]); i += 1
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 3
    preview = [float(x) for x in a[a.index("--preview") + 1].split(",")] if "--preview" in a else None
    v = dict(sl.get("vars", {}))
    v.setdefault("REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    rigs = {}
    for k, r in sl["rigs"].items():
        r = dict(r)
        im = cv2.imread(expand(r["src"], v))
        r["size"] = [im.shape[1], im.shape[0]]
        rigs[k] = r
    jobs, T = [], 0.0
    for s in sl["shots"]:
        if "anim" in s and (not only or s["id"] in only):
            jobs.append((s, rigs, cues, v, T, outdir, preview))
        T += s["duration_s"]
    t0 = time.time()
    log = []
    with cf.ProcessPoolExecutor(workers) as ex:
        for sid, n, secs in ex.map(render_shot, jobs):
            print(f"{sid}: {n} frames in {secs:.1f}s", flush=True)
            log.append({"id": sid, "frames": n, "secs": round(secs, 1)})
    json.dump({"shots": log, "wall_s": round(time.time() - t0, 1)}, open(os.path.join(outdir, "anim-log.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
