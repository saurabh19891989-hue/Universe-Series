#!/usr/bin/env python3
"""Cinematography test: builds a ~21 s 1920x1080 H.264 sequence from real NASA lunar imagery,
code-built puppets (Route 3) and a locally generated, upscaled, cut-out character (Route 2).

Shots
  A  6.0 s  slow push-in on the Moon (Artemis I art001e002581) + original courier-ship silhouette
  B  7.0 s  bridge two-shot, Jax + PIP rigs, 4-layer parallax truck, breathing, blinks, lip-flap
  C  5.0 s  Mira close-up, rim light, heavy background defocus + bokeh, slow dolly-in
  D  3.5 s  title card
One grade (navy lift / teal shadows / warm highlights, halation, vignette, grain, 2.39 letterbox)
is applied to every frame.

Usage: cinema.py --moon A.jpg --surface B.jpg --mira mira_cut.png --out look-test.mp4 --stills DIR
"""
import argparse, io, math, os, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

sys.path.insert(0, os.path.dirname(__file__))
import puppets as P

W, H, FPS = 1920, 1080, 24
RNG = np.random.default_rng(7)
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"


def ease(t):
    return t * t * (3 - 2 * t)


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), np.float32) / 255


def svg_rgba(svg, scale=1.0):
    png = cairosvg.svg2png(bytestring=svg.encode(), scale=scale)
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"), np.float32) / 255


def over(dst, rgba, x, y, opacity=1.0):
    """Alpha-composite rgba (float, straight alpha) onto dst at integer x, y (clipped)."""
    h, w = rgba.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return dst
    s = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4] * opacity
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + s[..., :3] * a
    return dst


def place(dst, rgba, cx, cy, scale):
    """Composite rgba scaled about its own centre, centred at (cx, cy) (sub-pixel via warp)."""
    h, w = rgba.shape[:2]
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    r = cv2.resize(rgba, (nw, nh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    return over(dst, np.clip(r, 0, 1), int(round(cx - nw / 2)), int(round(cy - nh / 2)))


def view(src, cx, cy, zoom, out_w=W, out_h=H, base_w=None):
    """Virtual camera: crop of src centred (cx, cy) in src px, where zoom=1 shows base_w px wide."""
    base_w = base_w or src.shape[1]
    s = out_w / base_w * zoom
    M = np.float32([[s, 0, out_w / 2 - cx * s], [0, s, out_h / 2 - cy * s]])
    return cv2.warpAffine(src, M, (out_w, out_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


# ------------------------------------------------------------------ grade
def make_vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    return (1 - 0.42 * np.clip(d - 0.45, 0, 1) ** 1.6)[..., None]


VIG = None


def grade(img, t_global, letterbox=True, grain=0.028):
    global VIG
    if VIG is None:
        VIG = make_vignette()
    x = np.clip(img, 0, 1)
    lum = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    # halation: bloom of highlights, warm tinted
    hi = np.clip(lum - 0.62, 0, 1) * 2.4
    small = cv2.resize(hi * x, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    bloom = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H), interpolation=cv2.INTER_LINEAR)
    x = x + bloom * np.float32([1.0, 0.55, 0.3]) * 0.5
    # split-tone: teal/navy shadows, warm highlights
    lum = np.clip((x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None], 0, 1)
    shadow = np.float32([0.004, 0.03, 0.05]); high = np.float32([1.05, 0.95, 0.82])
    x = x * (1 - lum) * np.float32([0.93, 1.0, 1.03]) + x * lum * high + shadow * (1 - lum) ** 3
    # filmic S-curve, slight desat in mids
    x = np.clip(x, 0, None) * 1.15
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)   # ACES-style filmic curve
    x = np.clip(x, 0, 1)
    g = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    x = g + (x - g) * np.clip(1.25 - g * 0.6, 0.7, 1.2) * np.where(x.mean(2, keepdims=True) < 0.2, 0.8, 1.0)
    x = x * VIG
    # grain (luma, mid-weighted, generated at half res)
    n = RNG.standard_normal((H // 2, W // 2)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    x = x + n * grain * (0.35 + 0.65 * (1 - np.abs(g - 0.45) * 1.6).clip(0, 1))
    if letterbox:
        bar = int((H - W / 2.39) / 2)
        x[:bar] = 0; x[H - bar:] = 0
    return np.clip(x, 0, 1)


# ------------------------------------------------------------------ assets
SHIP_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="520" height="200" viewBox="0 0 520 200">
<defs><linearGradient id="h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a5470"/><stop offset=".2" stop-color="#121828"/><stop offset="1" stop-color="#05070d"/></linearGradient>
<radialGradient id="e"><stop offset="0" stop-color="#fff7e0"/><stop offset=".3" stop-color="#ffb347" stop-opacity=".9"/><stop offset="1" stop-color="#ff6a00" stop-opacity="0"/></radialGradient></defs>
<ellipse cx="78" cy="104" rx="70" ry="34" fill="url(#e)"/>
<ellipse cx="86" cy="138" rx="44" ry="20" fill="url(#e)"/>
<path d="M110,80 L300,62 L430,84 L506,104 L430,118 L300,134 L180,140 L110,128 Z" fill="url(#h)" stroke="#05070d" stroke-width="3"/>
<path d="M210,64 L250,22 L300,22 L292,62 Z" fill="url(#h)" stroke="#05070d" stroke-width="3"/>
<rect x="160" y="128" width="150" height="26" rx="6" fill="url(#h)" stroke="#05070d" stroke-width="3"/>
<rect x="100" y="90" width="30" height="30" rx="4" fill="#20283c"/><rect x="104" y="124" width="26" height="24" rx="4" fill="#20283c"/>
<path d="M300,62 L430,84 L506,104" fill="none" stroke="#ffcf9a" stroke-width="3" opacity=".9"/>
<path d="M250,22 L300,22" stroke="#ffcf9a" stroke-width="3"/>
<path d="M430,96 l36,6" stroke="#7fe6e0" stroke-width="4"/>
<circle cx="350" cy="96" r="3" fill="#ffd28a"/><circle cx="366" cy="97" r="3" fill="#ffd28a"/><circle cx="382" cy="99" r="3" fill="#ffd28a"/>
</svg>"""


def bridge_svg():
    """Bridge interior as two layers: wall+window frame (window transparent) and console foreground."""
    frame = f"""<svg xmlns="http://www.w3.org/2000/svg" width="2300" height="1200" viewBox="0 0 2300 1200">
<defs><linearGradient id="w" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0d1630"/><stop offset=".5" stop-color="#070d1e"/><stop offset="1" stop-color="#03060e"/></linearGradient>
<linearGradient id="s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a3554"/><stop offset=".4" stop-color="#0e1529"/><stop offset="1" stop-color="#060a14"/></linearGradient>
</defs>
<path fill-rule="evenodd" d="M0,0 H2300 V1200 H0 Z M300,140 L2000,140 L2160,760 L140,760 Z" fill="url(#w)"/>
<path d="M300,140 L2000,140 L2160,760 L140,760 Z" fill="none" stroke="#2c3a5e" stroke-width="26"/>
<path d="M300,140 L2000,140 L2160,760 L140,760 Z" fill="none" stroke="#d0601f" stroke-width="3" opacity=".7"/>
<path d="M860,140 L800,760" stroke="url(#s)" stroke-width="44"/><path d="M1440,140 L1500,760" stroke="url(#s)" stroke-width="44"/>
<path d="M300,450 L2080,450" stroke="url(#s)" stroke-width="18" opacity=".9"/>
<g fill="#1e8c8a" opacity=".8">{''.join(f'<rect x="{60+i*34}" y="{820+(i%3)*14}" width="18" height="6" rx="2"/>' for i in range(60))}</g>
<g fill="#ffb02e">{''.join(f'<circle cx="{120+i*130}" cy="70" r="5"/>' for i in range(16))}</g>
</svg>"""
    console = """<svg xmlns="http://www.w3.org/2000/svg" width="2300" height="1200" viewBox="0 0 2300 1200">
<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3658"/><stop offset=".08" stop-color="#121a31"/><stop offset="1" stop-color="#03060d"/></linearGradient>
<radialGradient id="g"><stop offset="0" stop-color="#7ff5ea" stop-opacity=".9"/><stop offset="1" stop-color="#1e8c8a" stop-opacity="0"/></radialGradient></defs>
<path d="M0,960 C600,900 1700,900 2300,960 L2300,1200 L0,1200 Z" fill="url(#c)"/>
<path d="M0,960 C600,900 1700,900 2300,960" fill="none" stroke="#d0601f" stroke-width="4" opacity=".8"/>
<ellipse cx="420" cy="1010" rx="160" ry="34" fill="url(#g)"/><ellipse cx="1650" cy="1000" rx="200" ry="40" fill="url(#g)"/>
<rect x="320" y="990" width="200" height="34" rx="6" fill="#0c3b40" stroke="#7ff5ea" stroke-width="2"/>
<rect x="1540" y="980" width="230" height="40" rx="6" fill="#0c3b40" stroke="#7ff5ea" stroke-width="2"/>
<g fill="#ffb02e"><circle cx="900" cy="1000" r="7"/><circle cx="930" cy="1000" r="7"/><circle cx="1200" cy="996" r="7" fill="#ff5a3c"/></g>
</svg>"""
    return svg_rgba(frame), svg_rgba(console)


def starfield(h, w, n=2600):
    img = np.zeros((h, w), np.float32)
    ys = RNG.integers(0, h, n); xs = RNG.integers(0, w, n)
    img[ys, xs] = RNG.uniform(0.15, 1.0, n) ** 3
    img = cv2.GaussianBlur(img, (0, 0), 0.8) * 3
    return np.repeat(np.clip(img, 0, 1)[..., None], 3, 2) * np.float32([0.9, 0.95, 1.0])


# --------------------------------------------------------------- lip-sync
VIS_MAP = {**{c: "AI" for c in "aiy"}, "e": "E", "o": "O", "u": "U", "w": "U", "q": "U",
           **{c: "MBP" for c in "mbp"}, **{c: "FV" for c in "fv"}, "l": "L", "t": "L", "d": "L", "n": "L",
           **{c: "E" for c in "cgjkrsxzh"}}


def viseme_track(text, t0, t1):
    seq = []
    for wd in text.lower().split():
        letters = [c for c in wd if c.isalpha()]
        vs = []
        for c in letters:
            v = VIS_MAP.get(c, "E")
            if not vs or vs[-1] != v:
                vs.append(v)
        seq += vs[: max(2, len(vs) * 2 // 3)] + ["rest"]
    dt = (t1 - t0) / len(seq)
    return [(t0 + i * dt, v) for i, v in enumerate(seq)]


def at(track, t):
    v = "rest"
    for ts, vv in track:
        if t >= ts:
            v = vv
    return v


def blink_val(t, times):
    for b in times:
        d = t - b
        if 0 <= d < 0.16:
            return math.sin(d / 0.16 * math.pi)
    return 0.0


# ------------------------------------------------------------------- shots
class Shots:
    def __init__(self, a):
        self.moon = load_rgb(a.moon)
        self.surface = load_rgb(a.surface)
        self.stars = starfield(1400, 2400)
        self.ship = svg_rgba(SHIP_SVG)
        self.frame_l, self.console_l = bridge_svg()
        m = Image.open(a.mira).convert("RGBA")
        self.mira = np.asarray(m, np.float32) / 255
        self.pcache = {}

    def puppet(self, char, st, scale):
        key = (char, tuple(sorted((k, v if not isinstance(v, float) else round(v, 2)) for k, v in st.items())), scale)
        if key not in self.pcache:
            im = P.render(char, st, scale=scale, rim_dir=(-1, -0.5) if char == "jax" else (1, -0.5), rim_k=1.2)
            # scene integration: cool ambient + falloff of the key light toward the bottom of frame
            hgt = im.shape[0]
            fall = np.linspace(1.08, 0.55, hgt, dtype=np.float32)[:, None, None]
            im[..., :3] = np.clip(im[..., :3] * np.float32([0.95, 0.97, 1.02]) * fall, 0, 1)
            self.pcache[key] = im
            if len(self.pcache) > 400:
                self.pcache.pop(next(iter(self.pcache)))
        return self.pcache[key]

    # A: push-in on the Moon
    def A(self, t, dur):
        u = ease(t / dur)
        src = self.moon
        h, w = src.shape[:2]
        # composite stars behind the Moon (only where the photo is black space)
        img = view(src, w * 0.52 + 60 * u, h * 0.5 + 30 * u, 1.0 + 0.16 * u, base_w=w * 0.92)
        st = view(self.stars, 1200 + 20 * u, 700, 1.0 + 0.04 * u, base_w=2200)
        lum = img.max(axis=2, keepdims=True)
        mask = np.clip(1 - lum / 0.05, 0, 1)
        img = img + st * mask * 0.8
        # ship crossing (from 1.2 s to 5.6 s), scaling up slightly as it nears camera
        p = (t - 1.0) / 4.8
        if 0 <= p <= 1:
            pe = p
            sx = -300 + 2500 * pe
            sy = 760 - 180 * pe - 40 * math.sin(pe * math.pi)
            sc = 0.38 + 0.2 * pe
            ship = self.ship.copy()
            ship = cv2.GaussianBlur(ship, (0, 0), sigmaX=1.6, sigmaY=0.3)  # motion blur along travel
            place(img, ship, sx, sy, sc)
        return img

    # B: bridge two-shot
    def B(self, t, dur):
        u = ease(t / dur)
        cam = -70 + 140 * u            # truck right
        zoom = 1.0 + 0.05 * u
        img = np.zeros((H, W, 3), np.float32)
        # L0: lunar surface through window (slightly soft, slowest)
        sh, sw = self.surface.shape[:2]
        bg = view(self.surface, sw * 0.5 + cam * 0.25, sh * 0.42, (1.0 + 0.02 * u), base_w=sw * 0.8)
        bg = cv2.GaussianBlur(bg, (0, 0), 3.0)
        bg = bg * np.float32([0.78, 0.84, 0.95]) * np.linspace(0.75, 0.35, H, dtype=np.float32)[:, None, None]
        img[:] = bg
        # L1: bridge wall + window frame
        fr = cv2.resize(self.frame_l, None, fx=zoom * 0.95, fy=zoom * 0.95, interpolation=cv2.INTER_AREA)
        over(img, fr, int(W / 2 - fr.shape[1] / 2 - cam * 0.6), int(H / 2 - fr.shape[0] / 2 - 40))
        # characters (L2)
        br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.6)
        jt = viseme_track("It's a crater, Pip. Craters don't leave.", 0.4, 2.9)
        pt = viseme_track("The crater is present. The address has been withdrawn.", 3.3, 6.6)
        jax_st = {"expr": "smirk" if t < 3.0 else "worried", "mouth": at(jt, t) if t < 3.0 else "rest",
                  "blink": round(blink_val(t, [1.6, 4.9]), 2), "look": (6, 0) if t < 3.2 else (8, 1),
                  "head": round(-2 + 2.5 * math.sin(t * 1.3), 1) if t < 3.0 else 3.0, "breathe": round(br, 2),
                  "arm_l": 0, "arm_r": 0}
        pip_st = {"expr": "smirk" if t < 4.6 else "angry", "mouth": at(pt, t) if t > 3.2 else "rest",
                  "blink": round(blink_val(t, [2.2, 5.6]), 2), "look": (-8, 2),
                  "head": round(-4 + 3 * math.sin(t * 0.9), 1), "breathe": round(0.5 + 0.5 * math.sin(t * 2.4), 2),
                  "arm_r": round(10 * math.sin(t * 1.7), 0) if t > 3.2 else 0}
        jx = self.puppet("jax", jax_st, 1.0)
        px = self.puppet("pip", pip_st, 0.95)
        # contact/ambient: darken lower body a touch
        place(img, jx, 640 - cam * 1.0, 660, zoom * 1.1)
        place(img, px, 1340 - cam * 1.0, 560, zoom * 0.95)
        # L3: console foreground (fastest, defocused)
        cs = cv2.resize(self.console_l, None, fx=zoom * 0.95, fy=zoom * 0.95, interpolation=cv2.INTER_AREA)
        cs = cv2.GaussianBlur(cs, (0, 0), 3.5)
        over(img, cs, int(W / 2 - cs.shape[1] / 2 - cam * 1.5), int(H / 2 - cs.shape[0] / 2 - 40))
        # warm key spill from the window side
        return img

    # C: Mira close-up
    def C(self, t, dur):
        u = ease(t / dur)
        sh, sw = self.surface.shape[:2]
        if not hasattr(self, "c_bg"):
            # defocused bridge plate: window+surface+frame rendered once, then blurred heavily + bokeh
            base = np.zeros((H, W, 3), np.float32)
            base[:] = view(self.surface, sw * 0.62, sh * 0.35, 1.4, base_w=sw * 0.8)
            fr = cv2.resize(self.frame_l, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_AREA)
            over(base, fr, -600, -250)
            bok = np.zeros((H, W, 3), np.float32)
            for _ in range(26):
                cx, cy = int(RNG.uniform(0, W * 0.65)), int(RNG.uniform(H * 0.2, H * 0.95))
                col = (0.5, 0.95, 0.92) if RNG.random() < 0.6 else (1.0, 0.65, 0.25)
                cv2.circle(bok, (cx, cy), int(RNG.uniform(18, 46)), col, -1, lineType=cv2.LINE_AA)
            base = cv2.GaussianBlur(base, (0, 0), 16) * 0.75
            bok = cv2.GaussianBlur(bok, (0, 0), 2.5) * 0.45
            self.c_bg = np.clip(base + bok, 0, 1.2)
            # Mira: rim light from window (left) in orange + teal fill from right
            m = self.mira
            s = 1080 * 1.18 / m.shape[0]
            m = cv2.resize(m, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            self.c_mira = P.finish(m, rim=(1.0, 0.6, 0.25), rim_dir=(-1, -0.3), rim_w=10, rim_k=1.1,
                                   fill=(0.3, 0.8, 0.85), fill_k=0.25)
        bgz = 1.0 + 0.03 * u
        img = cv2.warpAffine(self.c_bg, np.float32([[bgz, 0, W / 2 * (1 - bgz) + 30 * u], [0, bgz, H / 2 * (1 - bgz)]]),
                             (W, H), borderMode=cv2.BORDER_REFLECT)
        # slow dolly-in on Mira with breathing
        z = 1.0 + 0.09 * u
        br = 1 + 0.004 * math.sin(t * 2 * math.pi / 3.8)
        m = self.c_mira
        mh, mw = m.shape[:2]
        mm = cv2.resize(m, (int(mw * z), int(mh * z * br)), interpolation=cv2.INTER_LINEAR)
        over(img, np.clip(mm, 0, 1), int(1260 - mm.shape[1] / 2 - 40 * u), int(H - mm.shape[0] * 0.80))
        return img

    # D: title card
    def D(self, t, dur):
        u = t / dur
        h, w = self.moon.shape[:2]
        img = view(self.moon, w * 0.74 - 40 * u, h * 0.55, 1.5 + 0.08 * u, base_w=w * 0.92) * 0.5
        img += view(self.stars, 1200, 700, 1.0, base_w=2200) * 0.6
        title = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(title)
        f = ImageFont.truetype(FONT_B, 118); f2 = ImageFont.truetype(FONT_M, 26)
        txt = "SECRET UNIVERSE"
        track = 18 + 22 * ease(min(1, u * 1.2))
        widths = [d.textlength(c, font=f) for c in txt]
        tot = sum(widths) + track * (len(txt) - 1)
        x = W / 2 - tot / 2
        a = int(255 * min(1, t / 0.8) * min(1, (dur - t) / 0.6))
        for c, cw in zip(txt, widths):
            d.text((x, H / 2 - 80), c, font=f, fill=(242, 231, 207, a)); x += cw + track
        sub = "LOOK TEST  ·  NOT FOR BROADCAST"
        d.text((W / 2 - d.textlength(sub, font=f2) / 2, H / 2 + 70), sub, font=f2, fill=(208, 96, 31, a))
        cr = "Moon imagery: NASA / Artemis I (art001e002581, art001e002164). Characters & ship: original."
        f3 = ImageFont.truetype(FONT_M, 18)
        d.text((W / 2 - d.textlength(cr, font=f3) / 2, H - 190), cr, font=f3, fill=(180, 190, 205, int(a * 0.8)))
        tl = np.asarray(title, np.float32) / 255
        glow = cv2.GaussianBlur(tl, (0, 0), 14)
        img = img + glow[..., :3] * glow[..., 3:4] * np.float32([1.0, 0.55, 0.2]) * 1.6
        over(img, tl, 0, 0)
        # light sweep
        sweep = np.exp(-((np.arange(W) - (-300 + 2600 * u)) / 140.0) ** 2).astype(np.float32)
        img = img + tl[..., 3:4] * sweep[None, :, None] * 0.6
        return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moon", required=True); ap.add_argument("--surface", required=True)
    ap.add_argument("--mira", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--stills", required=True); ap.add_argument("--crf", default="24")
    ap.add_argument("--only")
    a = ap.parse_args()
    S = Shots(a)
    plan = [("A", 6.0), ("B", 7.0), ("C", 5.0), ("D", 3.5)]
    if a.only:
        plan = [p for p in plan if p[0] in a.only]
    os.makedirs(a.stills, exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                           "-crf", a.crf, "-pix_fmt", "yuv420p", "-tune", "film", "-movflags", "+faststart", a.out],
                          stdin=subprocess.PIPE)
    t0 = time.time(); gt = 0.0; n = 0
    stills = {"A": 4.2, "B": 1.4, "C": 3.6, "D": 2.0}
    timings = {}
    for name, dur in plan:
        ts = time.time()
        nf = int(round(dur * FPS))
        for i in range(nf):
            t = i / FPS
            img = getattr(S, name)(t, dur)
            # 8-frame dip between shots for A->B; hard cuts otherwise (except fade-in / fade-out)
            if name == "A" and t < 0.6:
                img = img * (t / 0.6)
            out = grade(img, gt, letterbox=(name != "D"))
            if name == "D" and t > dur - 0.5:
                out = out * max(0, (dur - t) / 0.5)
            fr = (out * 255 + 0.5).astype(np.uint8)
            ff.stdin.write(fr.tobytes())
            if abs(t - stills[name]) < 0.5 / FPS:
                Image.fromarray(fr).save(f"{a.stills}/still-{name}.jpg", quality=88)
            gt += 1 / FPS; n += 1
        timings[name] = (time.time() - ts) / dur
        print(f"shot {name}: {dur}s rendered in {time.time()-ts:.1f}s ({timings[name]:.1f} s per s)", flush=True)
    ff.stdin.close(); ff.wait()
    tot = time.time() - t0
    print(f"TOTAL {n} frames, {n/FPS:.1f}s video in {tot:.1f}s -> {tot/(n/FPS):.2f} s render per s of video", flush=True)


if __name__ == "__main__":
    main()
