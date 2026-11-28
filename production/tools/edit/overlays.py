#!/usr/bin/env python3
"""Archive-format layers and overlays for the edit engine (PIP's file on the case).

Layer kinds (inside a shot's `layers`, drawn in OUTPUT pixel space, after the camera):
  viewer  - PIP's Archive Viewer: a brass-and-cream console with a 4:3 screen that plays an archive
            clip (warm grade, B&W kept B&W, gate flicker, scan lines), live gauges and a reel counter.
  slate   - text plates in PIP's voice: `exhibit` (cream filing card + rubber stamp), `strip` (slim
            telemetry / ship-camera strip with a running clock), `sheet` (full-frame sources list).

Overlays (top-level `overlays`, drawn on every shot after the film finish, so they stay crisp):
  comm_cards - who is speaking: a small brass card per speaker with a living portrait (slow push,
               flicker, scan line) and a waveform driven by the real amplitude of the line's stem.
  subtitles  - burned-in subtitles, small, bottom centre (the .srt is still written by render.py).

Everything is a pure function of time (shot-local t and global tg): deterministic, cache-safe.
"""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
MONO_B = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

_FONTS = {}


def font(path, size):
    k = (path, size)
    if k not in _FONTS:
        try:
            _FONTS[k] = ImageFont.truetype(path, size)
        except OSError:
            _FONTS[k] = ImageFont.truetype(INTER_SB, size)
    return _FONTS[k]


def noise1(seed, t, period=2.0):
    """Smooth 1-D value noise in [-1, 1]."""
    x = t / period
    i = math.floor(x); f = x - i
    def h(n):
        v = math.sin((n + seed * 0.618) * 12.9898) * 43758.5453
        return (v - math.floor(v)) * 2 - 1
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


def lum(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def over(dst, rgba, x, y):
    """Alpha-composite a float RGBA patch onto dst (float RGB) at integer x, y (clipped)."""
    h, w = rgba.shape[:2]; H, W = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return dst
    p = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = p[..., 3:4]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + p[..., :3] * a
    return dst


def pil_rgba(im):
    return np.asarray(im, np.float32) / 255


# ------------------------------------------------------------------ materials (procedural)
def brass(h, w, seed=1, dark=1.0):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    base = np.float32([0.62, 0.45, 0.20]) * dark
    grad = 0.82 + 0.30 * np.exp(-((y - 0.28) / 0.22) ** 2) - 0.12 * y
    brush = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), sigmaX=18, sigmaY=0.6) * 0.9
    spots = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 9) * 2.2
    x = base[None, None] * (grad[..., None] + 0.05 * brush[..., None] - 0.05 * np.clip(spots, 0, None)[..., None])
    x = x + np.float32([0.02, 0.025, 0.0]) * np.clip(-spots, 0, None)[..., None]        # faint verdigris in pits
    return np.clip(x, 0, 1).astype(np.float32)


def enamel(h, w, seed=2, chips=26):
    rng = np.random.default_rng(seed)
    base = np.float32([0.88, 0.83, 0.70])
    n = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 3) * 0.018
    blot = cv2.GaussianBlur(rng.standard_normal((h // 8 + 1, w // 8 + 1)).astype(np.float32), (0, 0), 2)
    blot = cv2.resize(blot, (w, h)) * 0.03
    x = base[None, None] * (1 + n[..., None] - np.abs(blot)[..., None])
    m = np.zeros((h, w), np.uint8)
    for _ in range(chips):                       # chips cluster near the edges, like PIP's housing
        side = rng.integers(4)
        cx = int(rng.uniform(0, w)) if side < 2 else (int(rng.uniform(0, 14)) if side == 2 else w - int(rng.uniform(0, 14)))
        cy = (int(rng.uniform(0, 14)) if side == 0 else h - int(rng.uniform(0, 14))) if side < 2 else int(rng.uniform(0, h))
        pts = np.int32([[cx + rng.normal(0, 5), cy + rng.normal(0, 4)] for _ in range(7)])
        cv2.fillPoly(m, [cv2.convexHull(pts)], 255)
    mf = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 0.8)[..., None]
    chip = np.float32([0.16, 0.12, 0.09])
    x = x * (1 - mf) + chip * mf
    return np.clip(x, 0, 1).astype(np.float32)


def rounded_mask(h, w, r, feather=1.0):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - 1 - r, h - 1), 255, -1)
    cv2.rectangle(m, (0, r), (w - 1, h - 1 - r), 255, -1)
    for cx, cy in ((r, r), (w - 1 - r, r), (r, h - 1 - r), (w - 1 - r, h - 1 - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    m = m.astype(np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), feather) if feather else m


def rivet(img, x, y, r=5):
    yy, xx = np.mgrid[-r - 2:r + 3, -r - 2:r + 3].astype(np.float32)
    d = np.sqrt(xx ** 2 + yy ** 2)
    a = np.clip(r + 0.5 - d, 0, 1)[..., None]
    shade = (0.75 + 0.5 * np.clip(-(xx + yy) / (2 * r), -1, 1))[..., None]
    col = np.float32([0.70, 0.52, 0.24]) * shade
    patch = np.dstack([col, a[..., 0]])
    return over(img, patch, int(x - r - 2), int(y - r - 2))


# ------------------------------------------------------------------ viewer bezel
def procedural_bezel(W, H, screen, panel, seed=5):
    """Full-frame RGBA console: brass face, a rounded 4:3 hole for the screen, a cream enamel panel."""
    img = brass(H, W, seed)
    x0, y0, x1, y1 = screen
    # bevel ring round the screen (lighter top-left, darker bottom-right)
    ring = np.zeros((H, W), np.float32)
    cv2.rectangle(ring, (x0 - 22, y0 - 22), (x1 + 22, y1 + 22), 1.0, -1)
    ring = cv2.GaussianBlur(ring, (0, 0), 6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bev = (ring * (1 - ring)) * 4
    img = img * (1 + 0.25 * bev[..., None] * np.sign(((x0 + x1) / 2 - xx) + ((y0 + y1) / 2 - yy))[..., None])
    # cream enamel panel with brass trim and rivets
    px0, py0, px1, py1 = panel
    en = enamel(py1 - py0, px1 - px0, seed + 1)
    m = rounded_mask(py1 - py0, px1 - px0, 18)[..., None]
    img[py0:py1, px0:px1] = img[py0:py1, px0:px1] * (1 - m) + en * m
    trim = np.zeros((H, W), np.float32)
    cv2.rectangle(trim, (px0 - 2, py0 - 2), (px1 + 1, py1 + 1), 1.0, 3, cv2.LINE_AA)
    img = img * (1 - 0.35 * trim[..., None])
    for (rx, ry) in ((px0 + 16, py0 + 16), (px1 - 16, py0 + 16), (px0 + 16, py1 - 16), (px1 - 16, py1 - 16),
                     (x0 - 11, y0 - 11), (x1 + 11, y0 - 11), (x0 - 11, y1 + 11), (x1 + 11, y1 + 11),
                     ((x0 + x1) // 2, y0 - 11), ((x0 + x1) // 2, y1 + 11)):
        img = rivet(img, rx, ry)
    # the hole (rounded) with a soft inner shadow on the screen
    hole = np.zeros((H, W), np.float32)
    hm = rounded_mask(y1 - y0, x1 - x0, 26, 0.8)
    hole[y0:y1, x0:x1] = hm
    a = 1 - hole
    return np.dstack([np.clip(img, 0, 1), a]).astype(np.float32)


def image_bezel(path, W, H, screen):
    """A generated bezel picture: resize to the frame, key its pure-black screen into the hole."""
    im = np.asarray(Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS), np.float32) / 255
    x0, y0, x1, y1 = screen
    dark = (cv2.GaussianBlur(im.max(2), (0, 0), 2) < 0.16).astype(np.uint8)
    roi = np.zeros_like(dark); roi[y0:y1, x0:x1] = 1
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark * roi)
    hole = np.zeros((H, W), np.float32)
    if n > 1:
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        m = np.zeros((H, W), np.uint8)
        cv2.drawContours(m, [max(cs, key=cv2.contourArea)], -1, 255, -1)       # filled: no texture islands
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        m = cv2.dilate(m, np.ones((3, 3), np.uint8))
        hole = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.2)
    return np.dstack([im, 1 - hole]).astype(np.float32)


_BEZELS = {}


def get_bezel(spec, resolve, W, H):
    screen = tuple(spec.get("screen", [56, 60, 1336, 1020]))
    panel = tuple(spec.get("panel", [1372, 44, 1880, 1036]))
    src = spec.get("bezel")
    key = (src, screen, panel, W, H)
    if key not in _BEZELS:
        if src and os.path.exists(resolve(src)):
            _BEZELS[key] = image_bezel(resolve(src), W, H, screen)
        else:
            _BEZELS[key] = procedural_bezel(W, H, screen, panel)
    return _BEZELS[key]


def archive_look(f, spec, t, seed):
    """One warm look for every archive source. B&W stays B&W (only a faint warm paper tone)."""
    look = spec.get("look", {})
    mono = spec.get("mono")
    if mono is None:      # auto: nearly no chroma = black-and-white film
        c = f[::8, ::8]; mono = float(np.abs(c - c.mean(2, keepdims=True)).mean()) < 0.02
    if mono:
        g = lum(f)
        lo, hi = np.percentile(g[::4, ::4], [1, 99.5])          # gentle auto-levels for faded prints
        g = np.clip((g - lo * 0.8) / max(0.25, hi - lo * 0.8), 0, 1) ** look.get("gamma", 1.0)
        g = g * (1 + 0.04 * (g - 0.5))
        x = g[..., None] * np.float32(look.get("tone", [1.0, 0.965, 0.90]))
    else:
        x = np.clip(f * np.float32(look.get("gain", [1.05, 1.0, 0.90])), 0, 1)
        l = lum(x)[..., None]
        x = l + (x - l) * look.get("sat", 1.22)
        x = np.clip(x, 0, 1)
        x = x * x * (3 - 2 * x) * 0.35 + x * 0.65                   # soft S contrast
    fl = look.get("flicker", 0.035)
    x = x * (1 + fl * noise1(seed + 3, t, 0.09) + 0.5 * fl * noise1(seed + 4, t, 0.31))
    return np.clip(x, 0, 1).astype(np.float32)


class Viewer:
    """kind: viewer — see SCHEMA.md."""
    def __init__(self, spec, resolve, W, H, seed, video_cls):
        self.s = spec; self.W, self.H = W, H; self.seed = seed; self.resolve = resolve
        self.bez = get_bezel(spec, resolve, W, H)
        self.screen = tuple(spec.get("screen", [56, 60, 1336, 1020]))
        self.panel = tuple(spec.get("panel", [1372, 44, 1880, 1036]))
        p = resolve(spec["src"])
        self.vid = video_cls(p, loop=spec.get("loop", True))
        x0, y0, x1, y1 = self.screen; sw, sh = x1 - x0, y1 - y0
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        d = np.sqrt(((xx - sw / 2) / (sw / 2)) ** 2 + ((yy - sh / 2) / (sh / 2)) ** 2)
        self.vig = (1 - 0.42 * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)
        self.scan = (1 - spec.get("scanlines", 0.05) * (np.sin(yy * math.pi / 1.5) ** 2))[..., None].astype(np.float32)
        gl = np.exp(-((xx / sw * 0.8 + yy / sh * 0.6 - 0.18) / 0.16) ** 2) * 0.05      # glass sheen, top-left
        self.sheen = gl[..., None].astype(np.float32) * np.float32([1.0, 0.95, 0.85])
        self.gauges = spec.get("gauges", True)

    def render(self, out, t, dur):
        s = self.s
        f = self.vid.at(s.get("in_s", 0.0) + t * s.get("speed", 1.0))
        if s.get("crop"):
            a, b, c, d = s["crop"]; hh, ww = f.shape[:2]
            f = f[int(b * hh):int(d * hh), int(a * ww):int(c * ww)]
        f = archive_look(f, s, t, self.seed)
        x0, y0, x1, y1 = self.screen; sw, sh = x1 - x0, y1 - y0
        fh, fw = f.shape[:2]
        u = t / max(dur, 1e-3)
        z0, z1 = s.get("zoom", [1.0, 1.06])
        z = z0 * (z1 / z0) ** (u * u * (3 - 2 * u))
        k = max(sw / fw, sh / fh) * z
        cx = s.get("cx", 0.5) * fw + s.get("pan_px", [0, 0])[0] * u
        cy = s.get("cy", 0.5) * fh + s.get("pan_px", [0, 0])[1] * u
        wx = 0.6 * noise1(self.seed + 9, t, 0.5); wy = 0.9 * noise1(self.seed + 10, t, 0.37)   # gate weave
        M = np.float64([[k, 0, sw / 2 - cx * k + wx], [0, k, sh / 2 - cy * k + wy]])
        scr = cv2.warpAffine(f, M, (sw, sh), flags=cv2.INTER_CUBIC if k > 1 else cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
        if s.get("soften", 0.6):
            scr = cv2.GaussianBlur(scr, (0, 0), s.get("soften", 0.6))
        scr = scr * self.vig * self.scan + self.sheen
        out = out.copy()
        out[y0:y1, x0:x1] = scr
        a = self.bez[..., 3:4]
        out = out * (1 - a) + self.bez[..., :3] * a
        if self.gauges:
            out = self.draw_dials(out, t) if self.s.get("dials") else self.draw_gauges(out, t)
        return out

    def draw_dials(self, out, t):
        """Live needles on the bezel picture's own dials: each [x, y, r] (output px) gets a warm-lit face,
        a scale arc and a needle that wanders (GATE) or follows the reel (FEED); a frame counter at `counter`."""
        for i, (cx, cy, r) in enumerate(self.s["dials"]):
            S = 2 * r + 4
            yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) - (r + 2)
            d = np.sqrt(xx ** 2 + yy ** 2)
            a = np.clip(r - d + 0.5, 0, 1)
            glow = np.exp(-(xx ** 2 + (yy - r * 0.25) ** 2) / (2 * (r * 0.75) ** 2))
            col = np.float32([0.62, 0.45, 0.24])[None, None] + glow[..., None] * np.float32([0.40, 0.42, 0.34])
            col = col * (1 + 0.04 * noise1(self.seed + 40 + i, t, 0.2))
            patch = np.dstack([np.clip(col, 0, 1), a]).astype(np.float32)
            im = Image.fromarray((patch * 255).astype(np.uint8), "RGBA"); dr = ImageDraw.Draw(im)
            px_, py_ = r + 2, r + 2 + r * 0.42
            for j in range(13):
                ang = math.radians(150 - j * 10)
                r0, r1 = r * (0.86 if j % 3 else 0.80), r * 0.96
                dr.line([px_ + math.cos(ang) * r0, py_ - math.sin(ang) * r0, px_ + math.cos(ang) * r1, py_ - math.sin(ang) * r1],
                        fill=(70, 46, 24, 255), width=2)
            v = 0.5 + 0.42 * noise1(self.seed + 20 + i, t, 1.6 + 1.3 * i) + 0.03 * math.sin(t * 21 + i)
            ang = math.radians(150 - 120 * min(1, max(0, v)))
            dr.line([px_, py_, px_ + math.cos(ang) * r * 0.92, py_ - math.sin(ang) * r * 0.92], fill=(40, 26, 16, 255), width=3)
            dr.ellipse([px_ - 7, py_ - 7, px_ + 7, py_ + 7], fill=(110, 78, 36, 255))
            out = over(out, pil_rgba(im), int(cx - r - 2), int(cy - r - 2))
        cp = self.s.get("counter")
        if cp:
            n = int(self.s.get("in_s", 0.0) * 24 + t * 24)
            im = Image.new("RGBA", (190, 56), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
            dr.rounded_rectangle([0, 0, 189, 55], 6, fill=(26, 20, 14, 245), outline=(150, 108, 48, 255), width=4)
            on = (t * 1.4) % 1.0 < 0.55
            dr.ellipse([14, 21, 28, 35], fill=(235, 60, 40, 255) if on else (90, 40, 30, 255))
            dr.text((108, 28), f"{n % 100000:05d}", font=font(MONO_B, 28), fill=(255, 190, 90, 255), anchor="mm")
            out = over(out, pil_rgba(im), int(cp[0] - 95), int(cp[1] - 28))
        return out

    def draw_gauges(self, out, t):
        px0, py0, px1, py1 = self.panel
        gy = py0 + int((py1 - py0) * 0.355)
        im = Image.new("RGBA", (px1 - px0, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        W_ = px1 - px0
        for i, (lab, per) in enumerate((("GATE", 1.7), ("FEED", 2.9))):
            cx, cy, r = int(W_ * (0.2 + 0.3 * i)), 70, 44
            d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=(150, 108, 48, 255))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 226, 200, 255), outline=(90, 62, 30, 255), width=2)
            for j in range(11):
                a = math.radians(210 - j * 24)
                d.line([cx + math.cos(a) * r * 0.78, cy - math.sin(a) * r * 0.78, cx + math.cos(a) * r * 0.92, cy - math.sin(a) * r * 0.92], fill=(60, 44, 28, 255), width=2)
            v = 0.5 + 0.38 * noise1(self.seed + 20 + i, t, per) + 0.04 * math.sin(t * 23 + i)
            a = math.radians(210 - 240 * v)
            d.line([cx, cy, cx + math.cos(a) * r * 0.82, cy - math.sin(a) * r * 0.82], fill=(170, 30, 20, 255), width=3)
            d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(120, 86, 40, 255))
            d.text((cx, cy + r * 0.45), lab, font=font(MONO_B, 13), fill=(70, 52, 32, 255), anchor="mm")
        # reel counter: rolling digits = exhibit frame number
        n = int(self.s.get("in_s", 0.0) * 24 + t * 24)
        cx = int(W_ * 0.80)
        d.rounded_rectangle([cx - 62, 44, cx + 62, 96], 6, fill=(26, 20, 14, 255), outline=(150, 108, 48, 255), width=4)
        d.text((cx, 70), f"{n % 100000:05d}", font=font(MONO_B, 26), fill=(255, 190, 90, 255), anchor="mm")
        d.text((cx, 112), "FRAME", font=font(MONO_B, 13), fill=(70, 52, 32, 255), anchor="mm")
        on = (t * 1.4) % 1.0 < 0.55
        d.ellipse([cx - 62, 118, cx - 50, 130], fill=(230, 60, 40, 255) if on else (90, 40, 30, 255))
        d.text((cx - 44, 124), "PLAYBACK", font=font(MONO_B, 12), fill=(70, 52, 32, 255), anchor="lm")
        return over(out, pil_rgba(im), px0, gy - 70)


# ------------------------------------------------------------------ slates
class Slate:
    """kind: slate — styles exhibit / strip / sheet; see SCHEMA.md."""
    def __init__(self, spec, resolve, W, H, seed):
        self.s = spec; self.W, self.H = W, H; self.seed = seed
        st = spec.get("style", "exhibit")
        self.st = st
        if st == "exhibit":
            self._prep_exhibit()
        elif st == "sheet":
            self._prep_sheet()

    def _prep_exhibit(self):
        s = self.s
        w, h = s.get("w", 470), s.get("h", 250)
        self.w, self.h = w, h
        ns = s.get("no_size", 34); self.pad = max(14, int(ns * 0.7))
        card = enamel(h, w, self.seed + 31, chips=10) * np.float32([1.02, 1.0, 0.97])
        m = rounded_mask(h, w, 10)
        im = Image.fromarray((np.dstack([card, m]) * 255).astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(im)
        d.rectangle([10, 10, w - 11, h - 11], outline=(120, 84, 40, 255), width=2)
        f_no = s.get("font", MONO_B)
        d.text((self.pad, self.pad - 2), s.get("no", "EXHIBIT"), font=font(f_no, ns), fill=(52, 34, 20, 255))
        self.rule_y = self.pad + int(ns * 1.25)
        d.line([self.pad - 4, self.rule_y, w - self.pad + 4, self.rule_y], fill=(150, 110, 60, 255), width=1)
        self.base = pil_rgba(im)
        self.fT = font(s.get("font_body", f_no), s.get("title_size", 30))
        self.fS = font(s.get("font_body", f_no), s.get("sub_size", 21))

    def _wrap(self, txt, f, maxw):
        words = txt.split(); lines = []; cur = ""
        for wd in words:
            tst = (cur + " " + wd).strip()
            if f.getlength(tst) > maxw and cur:
                lines.append(cur); cur = wd
            else:
                cur = tst
        if cur:
            lines.append(cur)
        return lines

    def render_exhibit(self, out, t):
        s = self.s
        x, y = s.get("x", 1390), s.get("y", 76)
        a_in = min(1.0, max(0.0, (t - s.get("t0", 0.0)) / 0.25))
        if a_in <= 0:
            return out
        im = Image.fromarray((self.base * 255).astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
        cps = s.get("cps", 38)
        ty = self.rule_y + 10
        n_avail = int(max(0.0, t - s.get("t0", 0.0) - 0.15) * cps)
        for key, f, col in (("title", self.fT, (40, 26, 14, 255)), ("sub", self.fS, (92, 66, 40, 255))):
            txt = s.get(key, "")
            if not txt:
                continue
            for ln in self._wrap(txt, f, self.w - 2 * self.pad):
                show = ln[:max(0, n_avail)]
                n_avail -= len(ln) + 1
                d.text((self.pad, ty), show, font=f, fill=col)
                ty += int(f.size * 1.22)
            ty += 8
        rgba = pil_rgba(im)
        stamp = s.get("stamp")
        if stamp:
            ts = t - s.get("stamp_at", 1.1)
            if ts >= 0:
                sc = 1.0 + 0.5 * math.exp(-ts * 14)
                fs = font(s.get("font", MONO_B), int(s.get("stamp_size", 30) * sc))
                sim = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0)); sd = ImageDraw.Draw(sim)
                tw = fs.getlength(stamp)
                cx, cy = self.w * s.get("stamp_x", 0.66), self.h * s.get("stamp_y", 0.80)
                sd.rounded_rectangle([cx - tw / 2 - 12, cy - fs.size * 0.72, cx + tw / 2 + 12, cy + fs.size * 0.72], 6,
                                     outline=(178, 34, 28, 230), width=4)
                sd.text((cx, cy), stamp, font=fs, fill=(178, 34, 28, 230), anchor="mm")
                sim = sim.rotate(s.get("stamp_rot", 8), resample=Image.BICUBIC, center=(cx, cy))
                sa = pil_rgba(sim)
                rng = np.random.default_rng(self.seed)
                ink = np.clip(0.78 + 0.35 * cv2.GaussianBlur(rng.standard_normal(sa.shape[:2]).astype(np.float32), (0, 0), 1.2), 0, 1)
                sa[..., 3] *= ink * min(1.0, ts / 0.05)
                rgba = rgba.copy()
                a = sa[..., 3:4]
                rgba[..., :3] = rgba[..., :3] * (1 - a) + sa[..., :3] * a
        rgba[..., 3] *= a_in
        return over(out, rgba, x, y + int((1 - a_in) * 10))

    def render_strip(self, out, t):
        s = self.s
        x, y = s.get("x", 48), s.get("y", 40)
        txt = s.get("text", "")
        clk = s.get("clock_from")
        if clk is not None:
            sec = clk + t
            txt = txt + f"  ·  {int(sec // 3600) % 24:02d}:{int(sec // 60) % 60:02d}:{int(sec) % 60:02d}:{int(sec * 24) % 24:02d}"
        f = font(s.get("font", MONO_B), s.get("size", 21))
        tw = int(f.getlength(txt)) + 70
        im = Image.new("RGBA", (tw, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, tw - 1, 39], 5, fill=(14, 12, 10, 150))
        d.rectangle([0, 0, 4, 39], fill=tuple(s.get("accent", [255, 176, 70])) + (255,))
        on = (t * 1.25) % 1.0 < 0.6
        dot = (235, 55, 40, 255) if on else (90, 40, 30, 200)
        d.ellipse([20, 13, 34, 27], fill=dot)
        d.text((46, 20), txt, font=f, fill=(242, 232, 210, 235), anchor="lm")
        rgba = pil_rgba(im)
        a = min(1.0, max(0.0, (t - s.get("t0", 0.0)) / 0.3))
        if "t1" in s:
            a *= min(1.0, max(0.0, (s["t1"] - t) / 0.3))
        rgba[..., 3] *= a * s.get("opacity", 1.0)
        return over(out, rgba, x, y)

    def _prep_sheet(self):
        s = self.s; W, H = self.W, self.H
        bg = enamel(H, W, self.seed + 40, chips=60)
        im = Image.fromarray((bg * 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
        d.rectangle([40, 40, W - 41, H - 41], outline=(120, 84, 40, 255), width=3)
        d.text((W // 2, 104), s.get("title", "SOURCES"), font=font(s.get("font", MONO_B), 44), fill=(52, 34, 20, 255), anchor="mm")
        if s.get("subtitle"):
            d.text((W // 2, 152), s["subtitle"], font=font(s.get("font", MONO_B), 22), fill=(110, 78, 44, 255), anchor="mm")
        items = s.get("lines", [])
        cols = s.get("cols", 2)
        fs = font(s.get("font_body", MONO), s.get("size", 17))
        per = int(math.ceil(len(items) / cols))
        colw = (W - 160) // cols
        for i, it in enumerate(items):
            c, r = divmod(i, per)
            d.text((80 + c * colw, 196 + r * int(fs.size * 1.32)), it, font=fs, fill=(48, 34, 22, 255))
        self.sheet = pil_rgba(im)

    def render_sheet(self, out, t):
        a = self.sheet[..., 3:4] * min(1.0, t / 0.4)
        return out * (1 - a) + self.sheet[..., :3] * a

    def render(self, out, t):
        if self.st == "exhibit":
            return self.render_exhibit(out, t)
        if self.st == "strip":
            return self.render_strip(out, t)
        return self.render_sheet(out, t)


# ------------------------------------------------------------------ comm cards + subtitles
class Overlays:
    """Global overlays for one shot. data = dict(lines=[{id,speaker,start,dur,text,sub}], amp={speaker: [..]},
    amp_rate=Hz, amp_t0=s) — sliced by render.py to the shot plus history."""
    def __init__(self, spec, data, resolve, W, H, shot):
        self.s = spec or {}; self.d = data or {}; self.W, self.H = W, H; self.resolve = resolve
        so = shot.get("overlays", {})
        self.cards_on = so.get("cards", True) and "comm_cards" in self.s
        self.subs_on = so.get("subtitles", True) and "subtitles" in self.s
        self.panel = any(L.get("kind") == "viewer" for L in shot.get("layers", []))
        self.anchor = so.get("cards_at")
        self._bg = {}; self._por = {}; self._sub = {}
        cc = self.s.get("comm_cards", {})
        self.cw, self.ch = cc.get("w", 470), cc.get("h", 132)
        self.intervals = self._intervals()

    # ---- card timing
    def _intervals(self):
        cc = self.s.get("comm_cards", {})
        pre, hold, merge = cc.get("pre_s", 0.2), cc.get("hold_s", 1.4), cc.get("merge_s", 3.0)
        skip = set(cc.get("hide", []))
        by = {}
        for ln in sorted(self.d.get("lines", []), key=lambda x: x["start"]):
            if ln["speaker"] in skip or ln.get("card") is False:
                continue
            a, b = ln["start"] - pre, ln["start"] + ln["dur"] + hold
            iv = by.setdefault(ln["speaker"], [])
            if iv and a - iv[-1][1] < merge:
                iv[-1][1] = max(iv[-1][1], b)
            else:
                iv.append([a, b])
        return by

    def _cards_at(self, tg):
        sl = self.s.get("comm_cards", {}).get("slide_s", 0.3)
        vis = []
        for spk, ivs in self.intervals.items():
            for a, b in ivs:
                if a <= tg <= b:
                    pin = min(1.0, (tg - a) / sl); pout = min(1.0, (b - tg) / sl)
                    p = min(pin, pout)
                    vis.append((a, spk, p * p * (3 - 2 * p)))
        vis.sort()
        return vis[-2:]

    def _amp(self, spk, tg):
        arr = self.d.get("amp", {}).get(spk)
        if arr is None:
            return 0.0
        i = int(round((tg - self.d.get("amp_t0", 0.0)) * self.d.get("amp_rate", 96)))
        return float(arr[i]) if 0 <= i < len(arr) else 0.0

    def _card_bg(self, spk):
        if spk in self._bg:
            return self._bg[spk]
        cc = self.s["comm_cards"]; info = cc.get("speakers", {}).get(spk, {})
        w, h = self.cw, self.ch
        b = brass(h, w, 11 + len(spk))
        en = enamel(h - 12, w - 12, 13 + len(spk), chips=8)
        body = b.copy()
        body[6:h - 6, 6:w - 6] = en
        m = rounded_mask(h, w, 12)
        im = Image.fromarray((np.dstack([body, m]) * 255).astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
        P = h - 24
        d.rectangle([11, 11, 13 + P, 13 + P], fill=(20, 16, 12, 255))
        nx = P + 30
        d.text((nx, 16), info.get("name", spk), font=font(cc.get("font_name", INTER_B), 26), fill=(40, 26, 14, 255))
        d.text((nx, 47), info.get("role", ""), font=font(cc.get("font_role", MONO_B), 15), fill=(110, 76, 40, 255))
        d.rounded_rectangle([nx, 72, w - 16, h - 14], 5, fill=(24, 19, 14, 255))
        self._bg[spk] = (pil_rgba(im), P, nx)
        return self._bg[spk]

    def _portrait(self, spk, P):
        if spk in self._por:
            return self._por[spk]
        info = self.s["comm_cards"].get("speakers", {}).get(spk, {})
        p = info.get("portrait")
        if p and os.path.exists(self.resolve(p)):
            im = np.asarray(Image.open(self.resolve(p)).convert("RGB"), np.float32) / 255
            if info.get("face"):
                a, b, c, d = info["face"]; hh, ww = im.shape[:2]
                im = im[int(b * hh):int(d * hh), int(a * ww):int(c * ww)]
            hh, ww = im.shape[:2]; s = min(hh, ww)
            im = im[(hh - s) // 2:(hh - s) // 2 + s, (ww - s) // 2:(ww - s) // 2 + s]
            im = cv2.resize(im, (int(P * 1.25), int(P * 1.25)), interpolation=cv2.INTER_AREA)
            if info.get("blur"):
                im = cv2.GaussianBlur(im, (0, 0), info["blur"])
        else:
            im = np.full((int(P * 1.25), int(P * 1.25), 3), 0.2, np.float32)
        self._por[spk] = im
        return im

    def _card(self, spk, tg, iv_start):
        rgba, P, nx = self._card_bg(spk)
        rgba = rgba.copy()
        info = self.s["comm_cards"].get("speakers", {}).get(spk, {})
        env = self._amp(spk, tg)
        # living portrait: slow push, light flicker, scan line, faint tint
        src = self._portrait(spk, P); S = src.shape[0]
        u = min(1.0, max(0.0, (tg - iv_start) / 8.0))
        z = 1.0 + 0.10 * u
        side = max(8, int(S * 0.8 / z))
        ox = int((S - side) / 2 + 3 * noise1(len(spk), tg, 3.0)); oy = int((S - side) / 2 + 3 * noise1(len(spk) + 1, tg, 3.7))
        ox = min(max(0, ox), S - side); oy = min(max(0, oy), S - side)
        por = cv2.resize(src[oy:oy + side, ox:ox + side], (P, P), interpolation=cv2.INTER_AREA)
        fl = 1 + 0.035 * noise1(len(spk) + 5, tg, 0.13)
        por = por * fl
        if info.get("lens"):        # PIP: the lens glows with his voice
            yy, xx = np.mgrid[0:P, 0:P].astype(np.float32)
            g = np.exp(-(((xx - P * info.get("lens_x", 0.5)) ** 2 + (yy - P * info.get("lens_y", 0.5)) ** 2) / (2 * (P * 0.22) ** 2)))
            por = por * (0.82 + 0.25 * env) + g[..., None] * np.float32([1.0, 0.62, 0.22]) * (0.12 + 0.75 * env)
        yy = np.arange(P, dtype=np.float32)[:, None, None]
        sl = (tg * 0.35) % 1.0 * P
        por = por * (1 - 0.05 * (np.sin(yy * math.pi / 2.0) ** 2)) + 0.10 * np.exp(-((yy - sl) / 3.0) ** 2)
        por = np.clip(por * np.float32(info.get("tint", [1.0, 0.98, 0.94])), 0, 1)
        rgba[12:12 + P, 12:12 + P, :3] = por
        # waveform: the real amplitude history of this speaker's stem (last ~1.5 s, newest on the right)
        x0, y0, x1, y1 = nx + 8, 78, self.cw - 22, self.ch - 20
        nb = 34; bw = (x1 - x0) / nb
        hist = [self._amp(spk, tg - (nb - 1 - k) / 24.0) for k in range(nb)]
        im = Image.new("RGBA", (self.cw, self.ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        mid = (y0 + y1) / 2; hh = (y1 - y0) / 2
        live = env > 0.05
        for k, v in enumerate(hist):
            hv = max(1.0, v * hh)
            col = (255, 182, 72, 255) if live else (150, 120, 80, 200)
            d.rectangle([x0 + k * bw + 1, mid - hv, x0 + (k + 1) * bw - 2, mid + hv], fill=col)
        lamp = (240, 70, 40, 255) if live else (95, 55, 40, 255)
        d.ellipse([self.cw - 30, 18, self.cw - 16, 32], fill=lamp)
        w_ = pil_rgba(im); a = w_[..., 3:4]
        rgba[..., :3] = rgba[..., :3] * (1 - a) + w_[..., :3] * a
        if not live:
            rgba[..., :3] = rgba[..., :3] * 0.88
        return rgba

    def _sub_img(self, ln):
        if ln["id"] in self._sub:
            return self._sub[ln["id"]]
        ss = self.s["subtitles"]
        f = font(ss.get("font", INTER_SB), ss.get("size", 32))
        txt = ln["text"].replace("—", "–")
        words = txt.split(); lines = []; cur = ""
        mx = ss.get("max_w", 1100)
        for wd in words:
            tst = (cur + " " + wd).strip()
            if f.getlength(tst) > mx and cur:
                lines.append(cur); cur = wd
            else:
                cur = tst
        lines.append(cur)
        lh = int(f.size * 1.25)
        tw = int(max(f.getlength(x) for x in lines)) + 32
        th = lh * len(lines) + 14
        im = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, tw - 1, th - 1], 8, fill=(8, 8, 8, int(255 * ss.get("box", 0.55))))
        for i, x in enumerate(lines):
            d.text((tw // 2, 7 + lh * i + lh // 2), x, font=f, fill=(250, 246, 236, 255), anchor="mm")
        self._sub[ln["id"]] = pil_rgba(im)
        return self._sub[ln["id"]]

    def apply(self, out, tg):
        if self.cards_on:
            cc = self.s["comm_cards"]
            if self.anchor == "left":                       # e.g. clips with a mark in the bottom-right corner
                ax, ay = cc.get("left_anchor", [48, 950])
            elif self.panel or self.anchor == "panel":
                ax, ay = cc.get("panel_anchor", [1402, 950])
            else:
                ax, ay = cc.get("anchor", [1432, 950])
            slide = -1 if self.anchor == "left" else 1
            gap = 12
            vis = self._cards_at(tg)
            yoff = 0.0
            for a, spk, p in vis:      # oldest first = bottom slot; a leaving card collapses smoothly
                card = self._card(spk, tg, a)
                card = card.copy(); card[..., 3] *= p
                x = int(ax + slide * (1 - p) * 60)
                y = int(ay - self.ch - yoff)
                out = over(out, card, x, y)
                yoff += (self.ch + gap) * p
        if self.subs_on:
            ss = self.s["subtitles"]
            cur = [ln for ln in self.d.get("lines", []) if ln.get("sub", True) and ln.get("text")
                   and ln["start"] + 0.03 <= tg <= ln["start"] + max(0.9, ln["dur"]) - 0.03]
            if cur:
                ln = max(cur, key=lambda x: x["start"])
                im = self._sub_img(ln)
                cx = ss.get("cx", 960)
                out = over(out, im, int(cx - im.shape[1] / 2), int(ss.get("bottom", 1062) - im.shape[0]))
        return out
