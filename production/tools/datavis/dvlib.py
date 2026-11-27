"""Shared machinery for the Episode 1 data visuals (Universe Undelivered).

Everything is drawn in code (Pillow + numpy + OpenCV) and piped to ffmpeg.
A visual is a ClipSpec: a draw(t, i) function that returns the *emissive*
picture (what the display itself lights up, RGB on black), plus a Look that
turns it into a photographed-looking screen (softness, bloom, scan lines,
flicker, grain, glass curvature, dust and scratches).

Two outputs per clip:
  <name>.mp4   1920x1080 24 fps H.264 CRF 16, full "display on glass" look
  <name>.mov   ProRes 4444 with alpha (emissive core only: no glass, no
               vignette, no dust) so the editor can map it onto a screen in a
               photo with its own glass.
"""
import os, sys, json, math, subprocess, hashlib, urllib.request
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(1)
W, H, FPS = 1920, 1080, 24

# --------------------------------------------------------------------------
# Fonts (all SIL Open Font License, from Google Fonts / github.com/google/fonts)
# --------------------------------------------------------------------------
FONT_DIR = os.environ.get("DATAVIS_FONTS",
                          os.path.expanduser("~/.cache/su-datavis-fonts"))
GF = "https://raw.githubusercontent.com/google/fonts/main/"
FONT_FILES = {
    "vt323":     ("VT323-Regular.ttf", "ofl/vt323/VT323-Regular.ttf"),
    "sharetech": ("ShareTechMono-Regular.ttf", "ofl/sharetechmono/ShareTechMono-Regular.ttf"),
    "plex":      ("IBMPlexMono-Regular.ttf", "ofl/ibmplexmono/IBMPlexMono-Regular.ttf"),
    "plexmed":   ("IBMPlexMono-Medium.ttf", "ofl/ibmplexmono/IBMPlexMono-Medium.ttf"),
    "space":     ("SpaceMono-Regular.ttf", "ofl/spacemono/SpaceMono-Regular.ttf"),
    "barlow":    ("BarlowCondensed-Medium.ttf", "ofl/barlowcondensed/BarlowCondensed-Medium.ttf"),
    "barlowsb":  ("BarlowCondensed-SemiBold.ttf", "ofl/barlowcondensed/BarlowCondensed-SemiBold.ttf"),
    "cinzel":    ("Cinzel.ttf", "ofl/cinzel/Cinzel%5Bwght%5D.ttf"),
    "cormorant": ("CormorantGaramond.ttf", "ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"),
    "cormorant-i": ("CormorantGaramond-Italic.ttf", "ofl/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf"),
    "pinyon":    ("PinyonScript-Regular.ttf", "ofl/pinyonscript/PinyonScript-Regular.ttf"),
    "fell":      ("IMFellEnglish-Regular.ttf", "ofl/imfellenglish/IMFeENrm28P.ttf"),
    "fell-i":    ("IMFellEnglish-Italic.ttf", "ofl/imfellenglish/IMFeENit28P.ttf"),
    "jost":      ("Jost.ttf", "ofl/jost/Jost%5Bwght%5D.ttf"),
    "oswald":    ("Oswald.ttf", "ofl/oswald/Oswald%5Bwght%5D.ttf"),
}
_fc = {}


def font(name, size, wght=None):
    key = (name, size, wght)
    if key in _fc:
        return _fc[key]
    fn, url = FONT_FILES[name]
    p = os.path.join(FONT_DIR, fn)
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(GF + url, p)
    f = ImageFont.truetype(p, size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    _fc[key] = f
    return f


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    """0 before a, 1 after b, linear between."""
    return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= a else 0.0)


def mul(col, k):
    k = max(0.0, k)
    return tuple(int(clamp(c * k, 0, 255)) for c in col)


def rnd(*seed):
    """deterministic 0..1 float from a seed tuple"""
    h = hashlib.md5(repr(seed).encode()).digest()
    return int.from_bytes(h[:4], "little") / 2 ** 32


def canvas():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    return img, ImageDraw.Draw(img)


def text(d, xy, s, f, col, anchor="la", track=0):
    """draw text, optional letter-spacing (track px)."""
    if not s:
        return
    if track == 0:
        d.text(xy, s, font=f, fill=col, anchor=anchor)
        return
    wtot = sum(d.textlength(c, font=f) + track for c in s) - track
    x, y = xy
    if anchor[0] == "m":
        x -= wtot / 2
    elif anchor[0] == "r":
        x -= wtot
    for c in s:
        d.text((x, y), c, font=f, fill=col, anchor="l" + anchor[1])
        x += d.textlength(c, font=f) + track


def tlen(f, s, track=0):
    im = ImageDraw.Draw(Image.new("L", (4, 4)))
    return sum(im.textlength(c, font=f) + track for c in s) - track if track else im.textlength(s, font=f)


def typed(s, t, start, cps=30):
    n = int(max(0, (t - start)) * cps)
    return s[:n]


def to_f(img):
    return np.asarray(img, dtype=np.float32) / 255.0


# --------------------------------------------------------------------------
# the look
# --------------------------------------------------------------------------
class Look:
    def __init__(self, base=(0.012, 0.02, 0.018), soft=0.8, bloom=0.9, bloom_r=(2.5, 9.0),
                 chroma=0.0, scan=0.22, scan_period=3.0, flicker=0.025, grain=0.012,
                 curve=0.035, vignette=0.45, dust=1.0, glare=0.04, seed=1, roll=True,
                 hum=0.05, lcd=False):
        self.__dict__.update(locals())
        del self.__dict__["self"]


LOOKS = {
    "amber": Look(base=(0.028, 0.017, 0.004), soft=0.9, bloom=1.1, flicker=0.03, scan=0.26, seed=3),
    "teal": Look(base=(0.006, 0.02, 0.02), soft=0.8, bloom=0.9, chroma=1.0, flicker=0.02, seed=5),
    "green": Look(base=(0.005, 0.02, 0.008), soft=0.85, bloom=1.0, flicker=0.025, scan=0.25, seed=7),
    "white": Look(base=(0.02, 0.024, 0.026), soft=0.7, bloom=0.7, chroma=0.8, flicker=0.015, scan=0.15, seed=9),
    "lcd": Look(base=(0.02, 0.03, 0.045), soft=0.6, bloom=0.45, chroma=0.0, flicker=0.008, scan=0.06,
                scan_period=2.0, curve=0.0, hum=0.0, grain=0.008, seed=11, lcd=True),
    "paper": Look(base=(0.0, 0.0, 0.0), soft=0.6, bloom=0.25, scan=0.0, flicker=0.01, curve=0.0,
                  vignette=0.5, hum=0.0, grain=0.02, dust=0.8, seed=13),
    "title": Look(base=(0, 0, 0), soft=0.5, bloom=0.7, bloom_r=(3, 14), scan=0.0, flicker=0.0, curve=0.0,
                  vignette=0.0, hum=0.0, grain=0.01, dust=0.0, glare=0.0, seed=17),
}

_noise_big = None
_cache = {}


def _noise(i):
    """cheap grain: crop a random window out of a big pre-generated noise field"""
    global _noise_big
    if _noise_big is None:
        rs = np.random.RandomState(1234)
        _noise_big = rs.randn(H * 2, W * 2).astype(np.float32)
    ox = int(rnd("nx", i) * W)
    oy = int(rnd("ny", i) * H)
    return _noise_big[oy:oy + H, ox:ox + W]


def _glass(look):
    """static per-look overlays: vignette, dust, scratches, glare, curvature map"""
    key = ("glass", look.seed, look.curve, look.vignette, look.dust)
    if key in _cache:
        return _cache[key]
    rs = np.random.RandomState(look.seed * 101)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r2 = nx * nx * 0.55 + ny * ny * 0.9
    vig = 1.0 - look.vignette * np.clip(r2 - 0.12, 0, 1) ** 1.3
    # dust and scratches (additive light), smudges (multiplicative dark)
    dust = np.zeros((H, W), np.float32)
    if look.dust > 0:
        for _ in range(int(260 * look.dust)):
            x, y = rs.randint(0, W), rs.randint(0, H)
            r = rs.choice([1, 1, 1, 2, 2, 3])
            cv2.circle(dust, (x, y), int(r), float(rs.uniform(0.05, 0.22)), -1, cv2.LINE_AA)
        for _ in range(int(14 * look.dust)):  # fibres / hairs
            x, y = rs.randint(0, W), rs.randint(0, H)
            a = rs.uniform(0, 6.28)
            L = rs.uniform(20, 120)
            pts = []
            for k in range(8):
                a += rs.uniform(-0.5, 0.5)
                x += math.cos(a) * L / 8
                y += math.sin(a) * L / 8
                pts.append([x, y])
            cv2.polylines(dust, [np.array(pts, np.int32)], False, float(rs.uniform(0.06, 0.16)), 1, cv2.LINE_AA)
        for _ in range(int(9 * look.dust)):  # scratches
            x, y = rs.randint(0, W), rs.randint(0, H)
            a = rs.uniform(-0.9, 0.9) + (math.pi / 2 if rs.rand() < 0.3 else 0)
            L = rs.uniform(60, 420)
            cv2.line(dust, (int(x), int(y)), (int(x + math.cos(a) * L), int(y + math.sin(a) * L)),
                     float(rs.uniform(0.04, 0.12)), 1, cv2.LINE_AA)
        dust = cv2.GaussianBlur(dust, (0, 0), 0.8)
    smudge = np.ones((H, W), np.float32)
    if look.dust > 0:
        sm = np.zeros((H, W), np.float32)
        for _ in range(6):
            cv2.ellipse(sm, (rs.randint(0, W), rs.randint(0, H)), (rs.randint(80, 260), rs.randint(40, 140)),
                        rs.uniform(0, 180), 0, 360, float(rs.uniform(0.05, 0.11)), -1)
        sm = cv2.GaussianBlur(sm, (0, 0), 60)
        smudge = 1.0 - sm
    glare = np.clip(1 - np.abs((nx * 0.7 + ny * 0.5) + 0.55) * 2.2, 0, 1) ** 2 * look.glare
    # barrel distortion map
    k = look.curve
    if k > 0:
        rr = nx * nx + ny * ny
        mx = ((nx * (1 + k * rr)) * (W / 2) + W / 2).astype(np.float32)
        my = ((ny * (1 + k * rr)) * (H / 2) + H / 2).astype(np.float32)
        s = 1 / (1 + k * 1.0)  # keep corners roughly inside
        mx = ((nx * s * (1 + k * rr)) * (W / 2) + W / 2).astype(np.float32)
        my = ((ny * s * (1 + k * rr)) * (H / 2) + H / 2).astype(np.float32)
        remap = (mx, my)
    else:
        remap = None
    out = (vig[..., None].astype(np.float32), dust[..., None], smudge[..., None], glare[..., None], remap)
    _cache[key] = out
    return out


def core(frame, i, t, look, return_pre=False):
    """emissive display look: soft + bloom + scan lines + flicker + grain. float32 RGB 0..~1.5"""
    x = frame.astype(np.float32)
    if look.soft > 0:
        x = cv2.GaussianBlur(x, (0, 0), look.soft)
    if look.bloom > 0:
        small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        b1 = cv2.GaussianBlur(small, (0, 0), look.bloom_r[0])
        b2 = cv2.GaussianBlur(small, (0, 0), look.bloom_r[1])
        bl = cv2.resize(b1 * (0.55 * look.bloom) + b2 * (0.45 * look.bloom), (W, H), interpolation=cv2.INTER_LINEAR)
        x += bl
    if look.chroma:
        c = look.chroma
        x[..., 0] = cv2.warpAffine(x[..., 0], np.float32([[1, 0, c], [0, 1, 0]]), (W, H))
        x[..., 2] = cv2.warpAffine(x[..., 2], np.float32([[1, 0, -c], [0, 1, 0]]), (W, H))
    yy = np.arange(H, dtype=np.float32)
    mod = np.ones(H, np.float32)
    if look.scan > 0:
        ph = (t * 0.35 if look.roll else 0.0)
        mod *= 1.0 - look.scan * (0.5 + 0.5 * np.cos(2 * np.pi * (yy / look.scan_period + ph)))
    if look.hum > 0:  # slow-moving brightness band
        y0 = (t * 55 + look.seed * 200) % (H + 300) - 150
        mod *= 1.0 + look.hum * np.exp(-((yy - y0) / 120.0) ** 2)
    g = 1.0 + look.flicker * (math.sin(t * 7.3 + look.seed) * 0.5 + (rnd(look.seed, i) - 0.5) * 1.6)
    x *= (mod * g)[:, None, None].astype(np.float32)
    pre = np.minimum(x, 1.5)
    if not return_pre:
        pre = x
    if look.grain > 0:
        n = _noise(i)
        gl = np.minimum(x[..., 1], 1.0)
        x = x + (n * (look.grain * (0.25 + gl)))[..., None]
    x = np.clip(x, 0, 1.5)
    return (x, pre) if return_pre else x


def glass(x, i, t, look):
    """returns uint8 RGB (H,W,3) after glass effects."""
    vig, dust, smudge, gl, remap = _glass(look)
    key = ("gain", look.seed, look.curve, look.vignette, look.dust, look.base)
    if key not in _cache:
        gain = (vig * smudge).astype(np.float32)
        add = (dust * 0.1375 + gl * np.array([0.8, 0.9, 1.0], np.float32)).astype(np.float32)
        _cache[key] = (gain, add, dust[..., 0] * 0.88)
    gain, add, dcoup = _cache[key]
    b = np.array(look.base, np.float32)
    y = (x + b) * gain
    y += add
    if look.dust > 0:
        lum = cv2.resize(np.minimum(x[..., 1], 1.0), (W // 8, H // 8), interpolation=cv2.INTER_AREA)
        lum = cv2.resize(cv2.GaussianBlur(lum, (0, 0), 3), (W, H), interpolation=cv2.INTER_LINEAR)
        y += (dcoup * lum)[..., None]
    out = np.empty((H, W, 3), np.uint8)
    np.multiply(np.clip(y, 0, 1), 255, out=y)
    out[:] = (y + 0.5).astype(np.uint8)
    if remap is not None:
        out = cv2.remap(out, remap[0], remap[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return out


def to_alpha(x):
    """emissive RGB -> straight RGBA (alpha from brightness) as 8-bit"""
    x = np.minimum(x, 1.0)
    a = np.minimum(cv2.transform(x, np.ones((1, 3), np.float32) * 1.5), 1.0)   # >= 1.5*max channel
    inv = 1.0 / np.maximum(a, 1e-3)
    rgb = np.minimum(x * inv[..., None], 1.0)
    out = np.empty((H, W, 4), np.uint8)
    out[..., :3] = (rgb * 255 + 0.5).astype(np.uint8)
    out[..., 3] = (a * 255 + 0.5).astype(np.uint8)
    return out


# --------------------------------------------------------------------------
# clip rendering
# --------------------------------------------------------------------------
class ClipSpec:
    def __init__(self, name, dur, draw, look="amber", alpha=True, stills=(), cues=None,
                 matte=None, dual=False, notes="", prores=True, lookobj=None, prores_q=16):
        """draw(t, i, alpha=False) -> PIL image or float array.
        dual=True: the alpha version is drawn separately (alpha=True), e.g. to leave a placeholder
        window empty; matte = list of (x0,y0,x1,y1) rectangles saved as a PNG matte."""
        self.name, self.dur, self.draw = name, dur, draw
        self.look = lookobj or LOOKS[look]
        self.alpha, self.stills, self.cues, self.notes = alpha, list(stills), cues or {}, notes
        self.matte, self.dual, self.prores, self.prores_q = matte, dual, prores, prores_q


def _ff_h264(path):
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
         "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-threads", "1", "-r", str(FPS),
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-movflags", "+faststart", path], stdin=subprocess.PIPE)


def _ff_prores(path, q=16):
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-qscale:v", str(q),
         "-pix_fmt", "yuva444p10le", "-vendor", "apl0", "-threads", "1", path], stdin=subprocess.PIPE)


def _call(spec, t, i, alpha):
    try:
        return spec.draw(t, i, alpha)
    except TypeError:
        return spec.draw(t, i)


def render(spec, outdir, stilldir=None, quick=False, skip_existing=False):
    os.makedirs(outdir, exist_ok=True)
    if skip_existing:
        p = os.path.join(outdir, spec.name + ".mp4")
        pa = os.path.join(outdir, spec.name + "_alpha.mov")
        if os.path.exists(p) and os.path.getsize(p) > 20000 and (not (spec.alpha and spec.prores) or os.path.exists(pa)):
            return spec.name
    n = int(round(spec.dur * FPS))
    if quick:
        n = min(n, 48)
    p264 = _ff_h264(os.path.join(outdir, spec.name + ".mp4"))
    pm = _ff_prores(os.path.join(outdir, spec.name + "_alpha.mov"), spec.prores_q) if (spec.alpha and spec.prores) else None
    still_idx = {int(round(s * FPS)): k for k, s in enumerate(spec.stills)}
    for i in range(n):
        t = i / FPS
        img = _call(spec, t, i, False)
        fr = to_f(img) if isinstance(img, Image.Image) else img
        c, c_pre = core(fr, i, t, spec.look, True)
        g = glass(c, i, t, spec.look)
        out8 = g
        p264.stdin.write(out8.tobytes())
        if pm is not None:
            if spec.dual:
                img2 = _call(spec, t, i, True)
                fr2 = to_f(img2) if isinstance(img2, Image.Image) else img2
                c2 = core(fr2, i, t, spec.look, True)[1]
            else:
                c2 = c_pre
            pm.stdin.write(to_alpha(c2).tobytes())
        if i in still_idx and stilldir:
            os.makedirs(stilldir, exist_ok=True)
            Image.fromarray(out8).save(os.path.join(stilldir, f"{spec.name}__t{spec.stills[still_idx[i]]:05.2f}.png"))
    for p in (p264, pm):
        if p is not None:
            p.stdin.close()
            p.wait()
    if spec.matte:
        m = np.zeros((H, W), np.uint8)
        for (x0, y0, x1, y1) in spec.matte:
            m[y0:y1, x0:x1] = 255
        Image.fromarray(m).save(os.path.join(outdir, spec.name + "_matte.png"))
    return spec.name


def mkgrid(d, color, step, x0=0, y0=0, x1=W, y1=H, width=1):
    for x in range(x0, x1 + 1, step):
        d.line([(x, y0), (x, y1)], fill=color, width=width)
    for y in range(y0, y1 + 1, step):
        d.line([(x0, y0 + (y - y0)), (x1, y)], fill=color, width=width)
