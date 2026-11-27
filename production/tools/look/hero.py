#!/usr/bin/env python3
"""Photoreal hero-frame compositor: AI portrait / set / ship cut-outs over real NASA plates,
with plate matching (black level, white balance, saturation, softness), light wrap, rim light
from the plate's light direction, depth-of-field, and one shared film finish (grain, halation,
gentle filmic curve, vignette).

Usage (see __main__): hero.py OUTDIR --bridge set.webp --jax jax.webp --mira mira.webp
        --ship ship.webp --baron baron.webp --moon art001e002581.jpg --earthrise as08-14-2383.jpg
"""
import argparse, os, sys, time
import numpy as np, cv2
from PIL import Image

W, H = 1920, 1080
RNG = np.random.default_rng(11)


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), np.float32) / 255


def cutout(path, cache_dir):
    """rembg (isnet-general-use) alpha, cached as PNG."""
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, os.path.splitext(os.path.basename(path))[0] + "_cut.png")
    if not os.path.exists(out):
        from rembg import remove, new_session
        im = Image.open(path).convert("RGB")
        remove(im, session=new_session("isnet-general-use")).save(out)
    return np.asarray(Image.open(out).convert("RGBA"), np.float32) / 255


def cover(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Scale-to-cover crop of img to w x h, centred at relative (cx, cy)."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * zoom
    r = cv2.resize(img, (int(iw * s + 0.5), int(ih * s + 0.5)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    x0 = int(np.clip(cx * r.shape[1] - w / 2, 0, r.shape[1] - w)); y0 = int(np.clip(cy * r.shape[0] - h / 2, 0, r.shape[0] - h))
    return np.clip(r[y0:y0 + h, x0:x0 + w], 0, 1).copy()


def lens_blur(img, radius):
    """Disc-kernel defocus (bokeh-like), done at half res for speed."""
    if radius < 1:
        return img
    small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
    r = max(1, int(radius / 2))
    k = np.zeros((2 * r + 1, 2 * r + 1), np.float32); cv2.circle(k, (r, r), r, 1, -1, cv2.LINE_AA); k /= k.sum()
    # boost highlights before blurring so bright points bloom into discs
    lin = np.power(np.clip(small, 0, 1), 2.2); lin = lin * (1 + 3 * np.clip(lin - 0.7, 0, 1))
    b = cv2.filter2D(lin, -1, k)
    b = np.power(np.clip(b, 0, None), 1 / 2.2)
    return cv2.resize(b, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)


def stats(img, mask=None):
    px = img.reshape(-1, 3) if mask is None else img[mask > 0.5]
    lum = px @ np.float32([0.2126, 0.7152, 0.0722])
    return np.percentile(lum, 1), np.percentile(lum, 99), px.mean(0)


def match_to_plate(fg, plate, strength=0.6, sat=0.85, black=None):
    """Pull figure colour toward the plate: black level, white balance and saturation."""
    rgb, a = fg[..., :3], fg[..., 3]
    pb, pw, pm = stats(plate)
    fb, fw, fm = stats(rgb, a)
    black = pb if black is None else black
    # white balance: neutralise the plate's cast ratio onto the figure (partial)
    pm_n = pm / pm.mean(); fm_n = fm / fm.mean()
    wb = (pm_n / fm_n) ** strength
    x = rgb * wb
    # black level: lift/lower the figure's darkest tones to the plate's
    x = black + (x - fb) * (np.clip(fw, 0.3, 1) - black) / max(1e-3, np.clip(fw, 0.3, 1) - fb)
    g = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    x = g + (x - g) * sat
    out = fg.copy(); out[..., :3] = np.clip(x, 0, 1)
    return out


def rim(fg, direction=(1, 0), width=6, color=(0.9, 0.95, 1.0), k=0.6):
    """Thin rim light on the alpha edge facing `direction` (dx, dy)."""
    a = fg[..., 3]
    dx, dy = int(-direction[0] * width), int(-direction[1] * width)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    sh = cv2.warpAffine(a, M, (a.shape[1], a.shape[0]))
    e = np.clip(a - sh, 0, 1)
    e = cv2.GaussianBlur(e, (0, 0), width * 0.5) * a
    out = fg.copy()
    out[..., :3] = np.clip(out[..., :3] + e[..., None] * np.float32(color) * k, 0, 1)
    return out


def light_wrap(fg, bg_region, width=12, k=0.45):
    """Let the (blurred) background bleed over the figure edge, like real lens/light spill."""
    a = fg[..., 3]
    inner = cv2.GaussianBlur(a, (0, 0), width)
    edge = np.clip(a - inner, 0, 1) * 2
    bgb = cv2.GaussianBlur(bg_region, (0, 0), width)
    out = fg.copy()
    out[..., :3] = out[..., :3] * (1 - edge[..., None] * k) + bgb * edge[..., None] * k
    return out


def place(dst, fg, x, y, scale, wrap=True, soft=0.0, shadow=0.0):
    """Composite fg (RGBA) with top-left at (x, y) after scaling; returns dst."""
    f = cv2.resize(fg, (int(fg.shape[1] * scale), int(fg.shape[0] * scale)),
                   interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    f = np.clip(f, 0, 1)
    if soft > 0:
        f[..., :3] = cv2.GaussianBlur(f[..., :3], (0, 0), soft)
        f[..., 3] = cv2.GaussianBlur(f[..., 3], (0, 0), soft * 0.8)
    h, w = f.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    s = f[y0 - y:y1 - y, x0 - x:x1 - x]
    region = dst[y0:y1, x0:x1]
    if wrap:
        s = light_wrap(s, region)
    if shadow > 0:
        sa = cv2.GaussianBlur(s[..., 3], (0, 0), 25)
        region *= (1 - shadow * sa[..., None])
    a = s[..., 3:4]
    dst[y0:y1, x0:x1] = region * (1 - a) + s[..., :3] * a
    return dst


def finish(img, grain=0.018, halation=0.35, vignette=0.28):
    x = np.clip(img, 0, 1)
    lum = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    hi = np.clip(lum - 0.75, 0, 1) * 3
    sm = cv2.resize(hi * x, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    x = x + cv2.resize(cv2.GaussianBlur(sm, (0, 0), 5), (W, H)) * np.float32([1.0, 0.6, 0.4]) * halation
    # gentle filmic shoulder and toe
    x = np.clip(x, 0, None)
    x = 1 - np.exp(-x * 1.9); x = x / (1 - np.exp(-1.9))
    x = np.clip(x, 0, 1) ** 1.04
    y, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    x = x * (1 - vignette * np.clip(d - 0.5, 0, 1) ** 1.5)[..., None]
    # grain: per-channel, slightly coarser than a pixel, stronger in mids (like 500T film)
    n = RNG.standard_normal((H * 2 // 3, W * 2 // 3, 3)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR) * np.float32([0.8, 1.0, 1.2])
    g = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    x = x + n * grain * (0.4 + 0.6 * np.clip(1 - np.abs(g - 0.45) * 1.8, 0, 1))
    return np.clip(x, 0, 1)


def save(img, path):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, quality=90)


# --------------------------------------------------------------------- frames
def hero_bridge(a, cache):
    """Jax + Mira on the bridge, real Moon through the window."""
    setimg = load(a.bridge)
    bg = cover(setimg, W, H, 0.5, 0.45)
    lum = bg @ np.float32([0.2126, 0.7152, 0.0722])
    # window matte: the set's window is a featureless (dark or fogged) region. Take low local
    # texture, then the connected component that contains the window seed point.
    mu = cv2.GaussianBlur(lum, (0, 0), 6); sd = np.sqrt(np.clip(cv2.GaussianBlur(lum * lum, (0, 0), 6) - mu * mu, 0, 1))
    m = (sd < a.win_thresh).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    sx, sy = int(a.win_seed[0] * W), int(a.win_seed[1] * H)
    keep = (lab == lab[sy, sx]).astype(np.uint8) if lab[sy, sx] > 0 else np.zeros_like(m)
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    keep = cv2.erode(keep, np.ones((5, 5), np.uint8))
    matte = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.0)[..., None]
    moon = load(a.moon)
    ys, xs = np.nonzero(keep)
    plate = np.zeros_like(bg)
    if len(xs):
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        # fit the whole lunar limb + black space into the window opening
        plate[y0:y1, x0:x1] = cover(moon, x1 - x0, y1 - y0, a.win_cx, 0.5, zoom=a.win_zoom)
    plate = plate * 0.9
    out = bg * (1 - matte) + plate * matte
    # moonlight spill: cool light falling into the set near the window
    spill = cv2.GaussianBlur(matte[..., 0] * (plate @ np.float32([0.3, 0.4, 0.3])), (0, 0), 60)[..., None]
    out = out + spill * np.float32([0.75, 0.85, 1.0]) * 0.5
    # DoF: set is behind the actors -> defocus set + window together
    out = lens_blur(out, a.bg_blur)
    jax = cutout(a.jax, cache); mira = cutout(a.mira, cache)
    for fg, x, y, sc, rd in [(jax, a.jax_xy[0], a.jax_xy[1], a.fig_scale, (1, -0.6)), (mira, a.mira_xy[0], a.mira_xy[1], a.fig_scale, (-1, -0.6))]:
        f = match_to_plate(fg, plate[matte[..., 0] > 0.5][None] if matte.mean() > 0.01 else plate, strength=0.35, sat=0.9, black=0.02)
        f = rim(f, rd, width=7, color=(0.8, 0.9, 1.0), k=0.6)       # moonlight from the window behind
        f = rim(f, (0, -1), width=5, color=(0.8, 0.9, 1.0), k=0.35)
        place(out, f, x, y, sc, wrap=True, soft=0.5)
    # out-of-focus foreground console (taken from the set itself) hides the waist cut lines
    if a.fg_occluder:
        strip = setimg[int(setimg.shape[0] * 0.72):]
        fgc = cv2.resize(strip, (W, int(H * 0.36)), interpolation=cv2.INTER_CUBIC) * 0.55
        fgc = lens_blur(np.clip(fgc, 0, 1), 36)
        y0 = H - fgc.shape[0]
        ramp = np.clip((np.arange(fgc.shape[0]) - 0) / 40.0, 0, 1)[:, None, None]
        out[y0:] = out[y0:] * (1 - ramp) + fgc * ramp
    return finish(out)


def clean_patches(img, rects):
    """Remove AI-invented badges/flags/name tags: inpaint each rect (source px) and re-grain."""
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    m = np.zeros(u8.shape[:2], np.uint8)
    for x0, y0, x1, y1 in rects:
        m[y0:y1, x0:x1] = 255
    out = cv2.inpaint(u8, m, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    n = RNG.standard_normal(out.shape).astype(np.float32) * 0.02
    mm = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 3)[..., None]
    return np.clip(out + n * mm, 0, 1)


def hero_bridge_insitu(a, cache):
    """Bridge two-shot generated with the actors in place; replace the dark window with the real Moon."""
    src = load(a.bridge)
    if a.patches:
        r = [tuple(int(v) for v in t.split(",")) for t in a.patches.split(";")]
        src = clean_patches(src, r)
    bg = cover(src, W, H, 0.5, 0.5)
    # window matte = hand-drawn window polygon (source px)  x  NOT(people), people from rembg
    sc = max(W / src.shape[1], H / src.shape[0]); ox = (src.shape[1] * sc - W) / 2; oy = (src.shape[0] * sc - H) / 2
    poly = np.array([[float(v) for v in p.split(",")] for p in a.win_poly.split(";")]) * sc - [ox, oy]
    keep = np.zeros((H, W), np.uint8); cv2.fillPoly(keep, [poly.astype(np.int32)], 1)
    tmp = os.path.join(cache, "_src_clean.png"); os.makedirs(cache, exist_ok=True)
    Image.fromarray((src * 255).astype(np.uint8)).save(tmp)
    people = cutout(tmp, cache)[..., 3]
    people = cover(np.repeat(people[..., None], 3, 2), W, H, 0.5, 0.5)[..., 0]
    matte = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.0) * (1 - people)
    matte = matte[..., None]
    ref = np.median(bg[keep > 0].reshape(-1, 3), 0)
    bg = np.clip(bg - matte * (1 - matte) * 2 * ref, 0, 1)     # spill suppression on hair edges
    ys, xs = np.nonzero(keep)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    plate = np.zeros_like(bg)
    plate[y0:y1, x0:x1] = cover(load(a.moon), x1 - x0, y1 - y0, a.win_cx, 0.5, zoom=a.win_zoom)
    plate = lens_blur(plate, a.bg_blur) * a.plate_gain   # focus is on the actors
    plate = plate + 0.025 * np.float32([0.6, 0.7, 0.8])     # faint glass haze lifts the black of space
    out = bg * (1 - matte) + plate * matte
    # the Moon is now the brightest thing in the room: cool spill + rim on everything near the window
    glow = cv2.GaussianBlur((plate * matte).mean(2), (0, 0), 50)[..., None]
    out = out + glow * np.float32([0.7, 0.8, 0.95]) * 0.18
    edge = np.clip(cv2.GaussianBlur(matte[..., 0], (0, 0), 3) - matte[..., 0], 0, 1)[..., None]
    out = out + edge * np.float32([0.75, 0.85, 1.0]) * 0.12
    return finish(out)


def hero_ship(a, cache):
    moon = load(a.moon)
    out = cover(moon, W, H, 0.6, 0.5, zoom=1.0)
    ship = cutout(a.ship, cache)
    # luminance-refined matte so pure black studio background never leaks in
    lum = ship[..., :3].max(2)
    ship[..., 3] = ship[..., 3] * np.clip((lum - 0.015) / 0.05, 0, 1) ** 0.5
    f = match_to_plate(ship, out, strength=0.5, sat=0.65, black=0.0)
    f[..., :3] *= 0.88
    f = rim(f, (1, -0.2), width=4, color=(1.0, 0.97, 0.92), k=0.5)
    place(out, f, a.ship_x, a.ship_y, a.ship_scale, wrap=True, soft=0.7)
    return finish(out, grain=0.014)


def hero_baron(a, cache):
    er = load(a.earthrise)
    plate = cover(er, W, H, 0.743, 0.606, zoom=1.3)
    plate = lens_blur(plate, a.bg_blur * 1.4)
    bar = cutout(a.baron, cache)
    f = match_to_plate(bar, plate, strength=0.3, sat=0.92, black=0.015)
    f = rim(f, (-1, -0.4), width=10, color=(0.85, 0.92, 1.0), k=0.65)   # sunlight from plate left
    out = plate.copy()
    sc = 1080 * 1.1 / bar.shape[0]
    place(out, f, int(W - bar.shape[1] * sc * 0.95), int(H - bar.shape[0] * sc + 110), sc, wrap=True, soft=0.3)
    return finish(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    for k in ["bridge", "jax", "mira", "ship", "baron", "moon", "earthrise"]:
        ap.add_argument("--" + k)
    ap.add_argument("--win-thresh", type=float, default=0.02)
    ap.add_argument("--win-cx", type=float, default=0.45)
    ap.add_argument("--win-zoom", type=float, default=1.0)
    ap.add_argument("--win-seed", type=float, nargs=2, default=(0.5, 0.3))
    ap.add_argument("--bg-blur", type=float, default=14)
    ap.add_argument("--only", default="123")
    ap.add_argument("--insitu", type=int, default=0); ap.add_argument("--patches", default="")
    ap.add_argument("--win-poly", default="");
    ap.add_argument("--win-dist", type=float, default=0.12); ap.add_argument("--plate-gain", type=float, default=0.65)
    ap.add_argument("--jax-xy", type=int, nargs=2, default=(60, 230)); ap.add_argument("--mira-xy", type=int, nargs=2, default=(1150, 250))
    ap.add_argument("--fig-scale", type=float, default=0.9); ap.add_argument("--fg-occluder", type=int, default=1)
    ap.add_argument("--ship-x", type=int, default=760); ap.add_argument("--ship-y", type=int, default=380)
    ap.add_argument("--ship-scale", type=float, default=0.5)
    a = ap.parse_args()
    cache = os.path.join(a.outdir, "_cut")
    for k, fn in [("1", hero_bridge_insitu if a.insitu else hero_bridge), ("2", hero_ship), ("3", hero_baron)]:
        if k in a.only:
            t = time.time(); img = fn(a, cache); save(img, os.path.join(a.outdir, f"hero-{k}.jpg"))
            print(f"hero-{k} {time.time()-t:.1f}s", flush=True)
