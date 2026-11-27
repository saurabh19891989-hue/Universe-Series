"""Visual 11 (Mira's laser map, built from real LRO LOLA elevation data) and 13 (title cards)."""
import os, math, urllib.request
import numpy as np
import cv2
from PIL import Image, ImageDraw
from dvlib import *

# ---------------------------------------------------------------------------
# 11. MIRA'S LASER MAP
# Data: LRO/LOLA, "High-Resolution LOLA Topography for Lunar South Pole Sites" (M. K. Barker, E. Mazarico et al.),
# PGDA product 78, Site04 (Shackleton rim), file Site04_final_adj_5mpp_surf.tif (5 m/pix surface height, polar
# stereographic, MOON_ME).  Credit: NASA / LRO / LOLA / GSFC PGDA.
# Crop used: pixel cols 1200-1440, rows 1320-1455 (240 x 135 px = 1200 m x 675 m).  The rover, path, boulder, ramp and
# labels are fictional overlays.
# ---------------------------------------------------------------------------
LOLA_URL = "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_surf.tif"
LOLA_FILE = "Site04_final_adj_5mpp_surf.tif"
CROP = (1320, 1455, 1200, 1440)  # r0, r1, c0, c1
PALE = (206, 238, 255)
WARN = (255, 176, 84)
_map = {}


def _lola_crop():
    cache = os.environ.get("DATAVIS_LOLA", os.path.expanduser("~/.cache/su-datavis-lola"))
    os.makedirs(cache, exist_ok=True)
    p = os.path.join(cache, LOLA_FILE)
    if not os.path.exists(p):
        urllib.request.urlretrieve(LOLA_URL, p)
    import tifffile
    d = tifffile.imread(p).astype(np.float32)
    r0, r1, c0, c1 = CROP
    return d[r0:r1, c0:c1]


def _smoothstep_arr(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _map_build(synthetic=False):
    key = ("m", synthetic)
    if key in _map:
        return _map[key]
    if synthetic:
        yy, xx = np.mgrid[0:135, 0:240].astype(np.float32)
        z = 1700 - 6 * np.clip(xx - 110, 0, None) - 0.6 * (yy - 60) ** 0 * 0 + 8 * np.sin(xx / 17.0) * np.exp(-xx / 160.0)
    else:
        z = _lola_crop()
    zs = cv2.GaussianBlur(cv2.resize(z, (W, H), interpolation=cv2.INTER_CUBIC), (0, 0), 9)
    gy, gx = np.gradient(zs, 1200.0 / W)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    hs = np.clip(0.5 + (gx - gy) * 0.35, 0, 1).astype(np.float32)
    # --- contours, 10 m, index 50 m
    zmin, zmax = float(zs.min()), float(zs.max())
    levels = np.arange(np.ceil(zmin / 10) * 10, zmax, 10.0)
    C = np.zeros((H, W), np.float32)
    for L in levels:
        m = (zs >= L).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        idx = int(round(L)) % 50 == 0
        for c in cs:
            if len(c) < 30:
                continue
            c2 = c.reshape(-1, 1, 2)
            cv2.polylines(C, [c2], False, 1.0 if idx else 0.55, 2 if idx else 1, cv2.LINE_AA)
    # --- laser footprint lattice and ground tracks
    D = np.zeros((H, W), np.float32)
    for y in range(18, H, 24):
        for x in range(18, W, 24):
            D[y, x] = 0.6
    D = cv2.GaussianBlur(D, (0, 0), 1.0) * 3.0
    Tk = np.zeros((H, W), np.float32)
    rs = np.random.RandomState(6)
    for k in range(9):
        x0 = 120 + k * 215 + rs.randint(-30, 30)
        for yy in range(0, H, 7):
            xx = x0 + yy * 0.14
            cv2.circle(Tk, (int(xx), yy), 1, 0.9, -1, cv2.LINE_AA)
    # light grid
    Gd = np.zeros((H, W), np.float32)
    Gd[::120, :] = 0.12
    Gd[:, ::120] = 0.12
    # --- cliff edge: first x (from left) where smoothed slope > 24 deg, per row
    Ledge = zmax - 0.09 * (zmax - zmin)       # top of the steep wall (about the 1 700 m index contour)
    edge = np.zeros(H, np.float32)
    for y in range(H):
        xs = np.where(zs[y] >= Ledge)[0]
        edge[y] = xs[-1] if len(xs) else W - 1
    edge = cv2.GaussianBlur(edge.reshape(-1, 1), (0, 0), 18).ravel()
    # --- reveal time per pixel: by elevation distance from rover elevation (contour by contour) + radius
    start = (470.0, 1000.0)
    zr = zs[int(start[1]) - 1, int(start[0])]
    dist = np.hypot(*(np.mgrid[0:H, 0:W].astype(np.float32) - np.array([start[1], start[0]], np.float32)[:, None, None]))
    Tm = 6.0 * np.abs(zs - zr) / max(1.0, (zmax - zmin)) * 1.6 + 3.5 * dist / np.hypot(W, H)
    # labels for index contours
    labels = []
    for L in levels:
        if int(round(L)) % 50 != 0:
            continue
        for y in (160, 880):
            xs = np.where(np.diff((zs[y] >= L).astype(np.int8)) != 0)[0]
            if len(xs):
                labels.append((int(xs[0]), y, "%d" % int(round(L))))
    out = dict(C=C, D=D, Tk=Tk, Gd=Gd, hs=hs, edge=edge, T=Tm, labels=labels, zs=zs, start=start, zr=zr,
               zmin=zmin, zmax=zmax)
    _map[key] = out
    return out


def _path(m):
    e = m["edge"]
    ex = lambda y: float(e[int(clamp(y, 0, H - 1))])
    P = []
    # start, then drive up alongside the wall; pass the stop point (7 px = ~4 m from edge), forward 40 m, round the boulder, ramp
    sx, sy = m["start"]
    pts = [(sx, sy)]
    y = sy
    while y > 700:
        y -= 8
        k = (sy - y) / (sy - 700.0)
        pts.append((lerp(sx, ex(700) - 7, smooth(k)), y))
    stop1 = len(pts) - 1
    while y > 640:  # forward 40 m = 64 px
        y -= 4
        pts.append((ex(y) - 7, y))
    fwd_end = len(pts) - 1
    while y > 560:  # round the boulder on the left
        y -= 4
        k = (640 - y) / 80.0
        pts.append((ex(y) - 7 - 105 * math.sin(math.pi * clamp(k)) ** 0.8, y))
    boulder_end = len(pts) - 1
    while y > 225:  # now right, now straight, up the ramp
        y -= 6
        k = clamp((560 - y) / 70.0)
        pts.append((lerp(ex(560) - 7, ex(y) - 58, smooth(k)) if k < 1 else ex(y) - 58, y))
    P = np.array(pts, np.float32)
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    return P, s, stop1, fwd_end, boulder_end


def _pos(P, s, ss):
    ss = clamp(ss, 0, s[-1])
    k = int(np.searchsorted(s, ss))
    k = min(max(k, 1), len(s) - 1)
    u = (ss - s[k - 1]) / max(1e-6, s[k] - s[k - 1])
    p = P[k - 1] * (1 - u) + P[k] * u
    v = P[min(k + 3, len(P) - 1)] - P[max(k - 3, 0)]
    return p, math.atan2(v[1], v[0])


def laser_map(synthetic=False, source_label="LOLA 5 M/PX"):
    m = _map_build(synthetic)
    P, s, i_stop, i_fwd, i_boul = _path(m)
    s_stop, s_fwd, s_boul, s_end = s[i_stop], s[i_fwd], s[i_boul], s[-1]
    # timeline
    T_BLOOM0, T_DOT = 3.0, 2.0
    T_MOVE1 = (13.0, 20.0)       # drive to the stop
    T_FWD = (26.0, 28.5)
    T_BOUL = (28.5, 31.5)
    T_RAMP = (31.5, 42.0)
    DUR = 49.0
    e = m["edge"]

    def sprog(t):
        if t < T_MOVE1[0]:
            return 0.0
        if t < T_MOVE1[1]:
            return s_stop * smooth((t - T_MOVE1[0]) / (T_MOVE1[1] - T_MOVE1[0]))
        if t < T_FWD[0]:
            return s_stop
        if t < T_FWD[1]:
            return lerp(s_stop, s_fwd, smooth((t - T_FWD[0]) / (T_FWD[1] - T_FWD[0])))
        if t < T_BOUL[1]:
            return lerp(s_fwd, s_boul, smooth((t - T_BOUL[0]) / (T_BOUL[1] - T_BOUL[0])))
        if t < T_RAMP[1]:
            return lerp(s_boul, s_end, smooth((t - T_RAMP[0]) / (T_RAMP[1] - T_RAMP[0])))
        return s_end

    base_rgb = np.array(PALE, np.float32) / 255.0
    ramp_pts = None

    def draw(t, i, alpha=False):
        tt = t - T_BLOOM0
        vis = _smoothstep_arr((tt - m["T"]) / 0.7)
        layer = (m["C"] * 1.0 + m["D"] * 0.55 + m["Tk"] * 0.35 + m["Gd"] + m["hs"] * 0.10 * (m["C"] * 0 + 1)) * vis
        # flat hillshade tint only where revealed
        fr = layer[..., None] * base_rgb * 0.82
        # leading "scan front" glow
        front = np.exp(-((tt - m["T"] - 0.1) / 0.18) ** 2) * (tt > 0)
        fr = fr + (front * m["C"] * 0.9)[..., None] * base_rgb
        img = Image.fromarray((np.clip(fr, 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        # HUD
        fs = font("sharetech", 26)
        if t > 1.0:
            text(d, (70, 66), "LASER ALTIMETRY  ·  RELIEF 10 M", fs, mul(PALE, 0.75), track=3)
            text(d, (W - 70, 66), source_label, fs, mul(PALE, 0.5), "ra", track=3)
        for (lx, ly, lab) in m["labels"]:
            a = float(vis[ly, min(W - 1, lx)])
            if a > 0.5:
                text(d, (lx + 6, ly - 22), lab, font("sharetech", 22), mul(PALE, 0.7 * a))
        # scale bar 100 m = 160 px
        if tt > 4:
            d.line([(70, H - 80), (230, H - 80)], fill=mul(PALE, 0.8), width=3)
            d.line([(70, H - 88), (70, H - 72)], fill=mul(PALE, 0.8), width=3)
            d.line([(230, H - 88), (230, H - 72)], fill=mul(PALE, 0.8), width=3)
            text(d, (150, H - 104), "100 M", fs, mul(PALE, 0.8), "mm", track=3)
        # cliff edge (appears with the wall; hatches point downhill = right)
        ea = smooth(ramp(t, T_BLOOM0 + 5.5, T_BLOOM0 + 8.0))
        stopped = (T_MOVE1[1] - 0.2 <= t < T_FWD[0] + 0.5)
        if ea > 0:
            ec = mul(WARN, ea * (1.0 if stopped else 0.55))
            poly = [(float(e[y]), y) for y in range(0, H, 6)]
            d.line(poly, fill=ec, width=4 if stopped else 2)
            for y in range(20, H, 34):
                x = float(e[y])
                d.line([(x, y), (x + 20, y + 8)], fill=ec, width=2)
            if ea > 0.5:
                text(d, (float(e[430]) + 70, 430), "CLIFF", font("sharetech", 34), mul(WARN, ea), "lm", track=6)
        # ramp (appears when named)
        if t >= 32.0:
            ra = smooth(ramp(t, 32.0, 34.0))
            ytop = 190
            xr = float(e[ytop]) - 58
            for k in range(5):
                yy = ytop + 20 + k * 20
                d.line([(xr - 70, yy + 12), (xr, yy - 8), (xr + 70, yy + 12)], fill=mul(PALE, 0.9 * ra), width=4)
            d.rectangle([xr - 90, ytop - 6, xr + 90, ytop + 140], outline=mul(PALE, 0.85 * ra), width=3)
            text(d, (xr + 120, ytop + 62), "SERVICE RAMP · BAY 9", font("sharetech", 30), mul(PALE, ra), "lm", track=4)
        # boulder marker
        if t >= 24.5:
            ba = smooth(ramp(t, 24.5, 26.0))
            bx, by = float(e[600]) - 12, 600
            d.ellipse([bx - 26, by - 26, bx + 26, by + 26], outline=mul(PALE, 0.9 * ba), width=3)
            for a in range(0, 360, 45):
                ra_ = math.radians(a)
                d.line([(bx + 18 * math.cos(ra_), by + 18 * math.sin(ra_)), (bx + 30 * math.cos(ra_), by + 30 * math.sin(ra_))], fill=mul(PALE, 0.7 * ba), width=2)
            text(d, (bx - 40, by), "BOULDER", font("sharetech", 26), mul(PALE, 0.85 * ba), "rm", track=3)
        # rover
        sp = sprog(t)
        pos, ang = _pos(P, s, sp)
        if t >= T_DOT:
            da = smooth(ramp(t, T_DOT, T_DOT + 1.0))
            # trail
            if sp > 2:
                ks = [_pos(P, s, q)[0] for q in np.linspace(0, sp, max(2, int(sp / 10)))]
                for q in ks[::1]:
                    d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=mul(PALE, 0.5 * da))
            x, y = float(pos[0]), float(pos[1])
            pulse = 0.5 + 0.5 * math.sin(t * 5.0)
            moving = abs(sprog(t + 0.05) - sprog(t - 0.05)) > 0.01
            rr = 22 + 8 * pulse
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=mul(PALE, 0.5 * da), width=2)
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(255, 255, 255) if da > 0.9 else mul((255, 255, 255), da))
            hx, hy = math.cos(ang), math.sin(ang)
            d.polygon([(x + hx * 36, y + hy * 36), (x + hx * 20 - hy * 9, y + hy * 20 + hx * 9), (x + hx * 20 + hy * 9, y + hy * 20 - hx * 9)],
                      fill=mul(PALE, 0.9 * da))
            # stop callout: gap to the edge
            if stopped and t >= T_MOVE1[1] + 0.3:
                ex_ = float(e[int(y)])
                ca = smooth(ramp(t, T_MOVE1[1] + 0.3, T_MOVE1[1] + 1.2))
                d.line([(x + 10, y), (ex_, y)], fill=mul(WARN, ca), width=3)
                d.line([(ex_, y - 14), (ex_, y + 14)], fill=mul(WARN, ca), width=3)
                bx0 = ex_ + 40
                d.line([(ex_, y), (bx0, y - 70)], fill=mul(WARN, 0.7 * ca), width=2)
                text(d, (bx0 + 10, y - 74), "EDGE  4 M", font("sharetech", 44), mul(WARN, ca), "lm", track=4)
            hdg = "HDG  000" if t < 12.5 else ("HDG  349" if t < T_FWD[0] else "HDG  000")
            text(d, (W - 70, H - 80), ("HOLD" if (sp == s_stop and stopped) else ("MOVE" if moving else "STBY")),
                 font("sharetech", 34), mul(WARN if stopped else PALE, 0.9 * da), "rm", track=5)
            text(d, (W - 70, H - 124), hdg, fs, mul(PALE, 0.7 * da), "rm", track=3)
        return img

    return [ClipSpec("11_laser_map_mira", DUR, draw, lookobj=Look(base=(0.003, 0.006, 0.01), soft=0.8, bloom=1.0, bloom_r=(2.5, 11),
                                                                  chroma=1.0, scan=0.12, flicker=0.02, curve=0.0, vignette=0.55,
                                                                  dust=0.8, seed=51, hum=0.04),
                     stills=[5.0, 8.0, 12.0, 22.0, 27.0, 31.0, 38.0, 46.0],
                     cues={"black_until": 2.0, "dot_appears": 2.0, "contours_bloom": "3-12", "left_eleven_degrees": 12.5,
                           "driving": "13-20", "stop_4m_from_edge": 20.0, "forward_40m": "26-28.5", "round_boulder": "28.5-31.5",
                           "ramp_named": 32.0, "reaches_ramp": 42.0},
                     notes=("REAL DATA: LRO LOLA 5 m LDEM Site04 (Shackleton rim), PGDA product 78 "
                            "(Site04_final_adj_5mpp_surf.tif), NASA/GSFC. Rover, route, boulder, ramp, cliff labels are fiction." if not synthetic
                            else "SYNTHETIC slope."))]


# =========================================================================
# 13. TITLE CARDS
# =========================================================================
def _text_layer(lines, mask_only=True):
    """lines: list of (text, fontname, size, wght, y, track, color); returns float RGB image + alpha mask"""
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for (s, fn, size, wg, y, track, col) in lines:
        while tlen(font(fn, size, wg), s, track) > 1560 and size > 20:
            size -= 4
        text(d, (W / 2, y), s, font(fn, size, wg), col, "mm", track=track)
    return np.asarray(img, np.float32) / 255.0


def _title_clip(name, dur, layers, sweep_col, sweep_dir=(1, 0.35), fade=None, zoom=0.035,
                sweep_t=(3.0, 7.2), extras=None):
    fade = fade or (0.6, 2.4, dur - 1.2, dur)
    base = _text_layer(layers)
    glow = cv2.GaussianBlur(base, (0, 0), 26)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = sweep_dir
    proj = (xx - W / 2) * nx + (yy - H / 2) * ny
    pmin, pmax = proj.min(), proj.max()
    sc = np.array(sweep_col, np.float32) / 255.0
    rs = np.random.RandomState(2)
    motes = [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0.4, 1.0), rs.uniform(8, 30)) for _ in range(40)]

    def draw(t, i, alpha=False):
        f_in = smooth(ramp(t, fade[0], fade[1]))
        f_out = 1 - smooth(ramp(t, fade[2], fade[3]))
        k = f_in * f_out
        z = 1.0 + zoom * (t / dur)
        M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]])
        u = ramp(t, sweep_t[0], sweep_t[1])
        pos = lerp(pmin - 300, pmax + 300, smooth(u))
        band = np.exp(-((proj - pos) / 120.0) ** 2).astype(np.float32)
        band2 = np.exp(-((proj - pos + 90) / 40.0) ** 2).astype(np.float32) * 0.5
        txt = base * (0.80 + 1.7 * (band + band2)[..., None] * sc)
        fr = txt + glow * (0.18 + 0.9 * band[..., None] * 0.35)
        fr = cv2.warpAffine(fr, M, (W, H))
        # dust motes drifting through the light
        for (mx, my, mb, mr) in motes:
            x = (mx + t * 6 * mb) % W
            y = (my - t * 3 * mb) % H
            a = float(np.exp(-((proj[int(y), int(x)] - pos) / 260.0) ** 2)) * 0.5 * mb
            if a > 0.02:
                cv2.circle(fr, (int(x), int(y)), 2, tuple(float(c) * a for c in sc), -1, cv2.LINE_AA)
        return np.clip(fr * k, 0, 1.4)
    return ClipSpec(name, dur, draw, "title", alpha=False, stills=[dur * 0.55, dur - 0.5 if False else dur * 0.3],
                    cues={"fade_in_done": fade[1], "sweep": "%.1f-%.1f" % sweep_t, "fade_out_starts": fade[2]})


GOLD = (226, 205, 160)
SILVER = (222, 228, 236)


def titles():
    cl = []
    # ---- Option A: classical (Cinzel + Cormorant Garamond Italic)
    A_main = [("SECRET", "cinzel", 200, 600, 430, 46, GOLD), ("UNIVERSE", "cinzel", 200, 600, 650, 46, GOLD),
              ("—  ✦  —", "cormorant", 52, 500, 805, 10, mul(GOLD, 0.8))]
    A_main = [("SECRET UNIVERSE", "cinzel", 170, 600, 500, 40, GOLD),
              ("—   ✦   —", "cormorant", 56, 500, 650, 6, mul(GOLD, 0.75))]
    cl.append(_title_clip("13a_title_main_optionA_cinzel", 10.0, A_main, (255, 240, 200)))
    A_ep = [("EPISODE ONE", "cinzel", 44, 500, 440, 28, mul(GOLD, 0.8)),
            ("The Parcel Nobody Ordered", "cormorant-i", 150, 500, 570, 2, (236, 226, 204))]
    cl.append(_title_clip("13b_episode_card_optionA_cormorant", 8.0, A_ep, (255, 246, 220), fade=(0.5, 2.0, 6.8, 8.0),
                          sweep_t=(2.2, 6.0), zoom=0.03))
    # ---- Option B: modern (Jost light, wide tracking)
    B_main = [("SECRET", "jost", 168, 300, 420, 70, SILVER), ("UNIVERSE", "jost", 168, 300, 625, 70, SILVER)]
    cl.append(_title_clip("13c_title_main_optionB_jost", 10.0, B_main, (215, 235, 255), sweep_dir=(1, 0.0)))
    B_ep = [("EPISODE 1", "jost", 40, 400, 450, 34, mul(SILVER, 0.7)),
            ("THE PARCEL NOBODY ORDERED", "jost", 74, 300, 570, 16, SILVER)]
    cl.append(_title_clip("13d_episode_card_optionB_jost", 8.0, B_ep, (215, 235, 255), sweep_dir=(1, 0.0),
                          fade=(0.5, 2.0, 6.8, 8.0), sweep_t=(2.2, 6.0), zoom=0.03))
    return cl
