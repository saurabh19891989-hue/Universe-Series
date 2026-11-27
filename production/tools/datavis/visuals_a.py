"""Visuals 1-5: Atlas map, PIP report screen, engine readouts / dying screens / coffee light,
bank call window, cargo screen.  One function per visual; each returns a list of ClipSpec."""
import math
import numpy as np
from PIL import Image, ImageDraw
from dvlib import *

TEAL = (120, 255, 222)
AMBER = (255, 178, 46)
GREEN = (120, 255, 120)


# =========================================================================
# 1. ATLAS MAP (scene 2)
# =========================================================================
_atlas_bg = {}


def _atlas_background():
    if "bg" in _atlas_bg:
        return _atlas_bg["bg"]
    img, d = canvas()
    rs = np.random.RandomState(4)
    # crater floor: very dark stipple inside a rim ring, faint grid
    for x in range(120, W, 120):
        d.line([(x, 90), (x, H - 90)], fill=mul(TEAL, 0.10), width=1)
    for y in range(90, H - 89, 120):
        d.line([(60, y), (W - 60, y)], fill=mul(TEAL, 0.10), width=1)
    for _ in range(2600):
        x, y = rs.randint(130, W - 130), rs.randint(120, H - 120)
        d.point((x, y), fill=mul(TEAL, rs.uniform(0.08, 0.2)))
    cx, cy = 960, 540
    for k, (rx, ry, b) in enumerate([(820, 395, 0.38), (790, 372, 0.18), (610, 285, 0.10), (360, 168, 0.08)]):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=mul(TEAL, b), width=2 if k < 2 else 1)
    for a in range(0, 360, 3):  # hachures on the rim
        ra = math.radians(a)
        x0, y0 = cx + 820 * math.cos(ra), cy + 395 * math.sin(ra)
        x1, y1 = cx + 790 * math.cos(ra), cy + 372 * math.sin(ra)
        d.line([(x0, y0), (x1, y1)], fill=mul(TEAL, 0.16), width=1)
    # frame + ticks
    d.rectangle([40, 40, W - 40, H - 40], outline=mul(TEAL, 0.55), width=2)
    for x in range(60, W - 40, 30):
        d.line([(x, 40), (x, 52 if x % 150 else 64)], fill=mul(TEAL, 0.5))
        d.line([(x, H - 40), (x, H - 52 if x % 150 else H - 64)], fill=mul(TEAL, 0.5))
    for y in range(60, H - 40, 30):
        d.line([(40, y), (52 if y % 150 else 64, y)], fill=mul(TEAL, 0.5))
        d.line([(W - 40, y), (W - 52 if y % 150 else W - 64, y)], fill=mul(TEAL, 0.5))
    f = font("sharetech", 26)
    text(d, (84, 86), "ATLAS // RIM SECTOR 7 // SHACKLETON", f, mul(TEAL, 0.7), track=3)
    text(d, (W - 84, 86), "REG 41 - PUBLISHED", f, mul(TEAL, 0.5), "ra", track=3)
    text(d, (84, H - 116), "SCALE 1:20 000   GRID 500 M", f, mul(TEAL, 0.5), track=2)
    text(d, (W - 84, H - 116), "N  0.0   E  0.0   ELEV -2 100", f, mul(TEAL, 0.5), "ra", track=2)
    _atlas_bg["bg"] = img
    return img


STREETS_DEFAULT = [
    # name, text position, street polyline, lamp dots
    ("HATCHET LANE", (330, 700), [(250, 735), (520, 700), (780, 650), (905, 598)]),
    ("BEAN ROW", (1180, 395), [(1000, 470), (1180, 430), (1420, 420), (1640, 440)]),
    ("STRAW STAIRS", (1150, 760), [(1000, 600), (1090, 690), (1220, 770), (1400, 800)]),
]


def _atlas_draw(t_state, label, streets, alpha=False):
    """t_state: dict(label_in 0..1, removed float, street_b list)"""
    img = _atlas_background().copy()
    d = ImageDraw.Draw(img)
    f = font("sharetech", 62)
    adv = f.getlength("M") + 3
    x0 = 960 - len(label) * adv / 2
    y = 520
    lin = t_state["label_in"]
    rem = t_state["removed"]
    n = len(label)
    for i, ch in enumerate(label):
        k = n - 1 - i  # 0 = last letter
        b = clamp(1 - (rem - k)) * lin
        if ch != " " and b > 0.004:
            text(d, (x0 + i * adv, y), ch, f, mul((140, 255, 228), 0.15 + 0.85 * b ** 1.6 if b < 1 else 1.0)
                 if b < 1 else (140, 255, 228))
    # pin
    pb = lin * clamp(1 - rem / 3.0)
    if pb > 0.01:
        px, py = 960, 470
        d.polygon([(px, py - 16), (px + 12, py), (px, py + 16), (px - 12, py)], outline=mul(TEAL, pb), width=3)
        d.line([(px, py + 16), (px, y - 8)], fill=mul(TEAL, 0.6 * pb), width=2)
    # streets
    fs = font("sharetech", 30)
    for (name, tp, poly), b in zip(streets, t_state["street_b"]):
        if b <= 0.004:
            continue
        d.line(poly, fill=mul(TEAL, 0.45 * b), width=2)
        for (px, py) in poly:
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=mul((255, 236, 170), 0.9 * b))
        text(d, tp, name, fs, mul(TEAL, 0.95 * b), track=4)
    return img


def atlas_map(label="THE SILVER HATCHET — SHACKLETON FLOOR",
              stages=("THE SILVER HATCH", "THE SILVER HAT", "THE SILVER", "THE", ""),
              streets=("HATCHET LANE", "BEAN ROW", "STRAW STAIRS"), stage_hold=2.8, char_time=0.075):
    """Continuous take + each held stage as its own clip (5 s)."""
    st = [s for s in STREETS_DEFAULT if s[0] in streets]
    n = len(label)
    removes = [n - len(s) for s in stages]
    # --- timeline for the continuous take
    t_in, t_full = 1.0, 3.2  # label glows in 1.0-2.2, then held until 4.2
    segs = []  # (t0,t1,rem0,rem1)
    t = 4.2
    cur = 0
    cues = {"label_full_from": 2.2}
    for s, r in zip(stages, removes):
        dur = max(0.5, (r - cur) * char_time)
        segs.append((t, t + dur, cur, r))
        cues["stage_%r_reached" % s] = round(t + dur, 2)
        t += dur + stage_hold
        cur = r
    t_streets = t - stage_hold + 0.8  # first street goes out 0.8 s after label gone... then one every 1.5 s
    t_streets = t - stage_hold + 2.0
    street_out = [t_streets + 1.6 * k for k in range(len(st))]
    for k, s in enumerate(st):
        cues["street_out_" + s[0]] = round(street_out[k], 2)
    dur_total = street_out[-1] + 1.0 + 3.2
    cues["all_dark_from"] = round(street_out[-1] + 0.8, 2)

    def state_at(tt):
        lab = smooth(ramp(tt, t_in, 2.2))
        rem = 0.0
        for (a, b, r0, r1) in segs:
            if tt >= b:
                rem = r1
            elif tt > a:
                rem = lerp(r0, r1, (tt - a) / (b - a))
                break
            else:
                break
        sb = []
        for k in range(len(st)):
            base = smooth(ramp(tt, 1.6 + 0.3 * k, 2.6 + 0.3 * k))
            to = street_out[k]
            if tt >= to:
                # lamp-out: two stutters then gone
                u = (tt - to) / 0.8
                if u >= 1:
                    base = 0
                else:
                    base *= 0.0 if (u > 0.35 and u < 0.5) else (0.4 if u > 0.2 else 1.0) * (1 - smooth((u - 0.5) * 2))
            sb.append(base)
        return dict(label_in=lab, removed=rem, street_b=sb)

    def draw_cont(tt, i, alpha=False):
        return _atlas_draw(state_at(tt), label, st)

    clips = [ClipSpec("01_atlas_continuous", dur_total, draw_cont, "teal",
                      stills=[3.5, segs[0][1] + 1.0, dur_total - 1.0], cues=cues,
                      notes="Continuous take: label glows in, loses letters from the end in held stages, "
                            "then street names go out like lamps; ends on dark.")]
    # --- held stages
    held = [("00_full", dict(label_in=1, removed=0, street_b=[1] * len(st)))]
    for s, r in zip(stages, removes):
        nm = "%d_%s" % (len(held), (s.replace(" ", "_") or "label_gone"))
        held.append((nm, dict(label_in=1, removed=r, street_b=[1] * len(st))))
    for k in range(len(st)):
        sb = [0 if j <= k else 1 for j in range(len(st))]
        sb = [0 if j <= k else 1 for j in range(len(st))]
        held.append(("street_out_%d_%s" % (k + 1, st[k][0].replace(" ", "_")),
                     dict(label_in=1, removed=n, street_b=sb)))
    for nm, state in held:
        def dr(tt, i, alpha=False, state=state):
            return _atlas_draw(state, label, st)
        clips.append(ClipSpec("01_atlas_held_" + nm, 5.0, dr, "teal", stills=[2.0 if nm.startswith("00") else 5.0 and 2.0]))
    return clips


# =========================================================================
# 2. PIP'S REPORT SCREEN (amber monochrome)
# =========================================================================
def _pip_draw(t, report, re_line, extra, sent_read=False, t_line=2.0, t_read=None):
    img, d = canvas()
    A = AMBER
    d.rounded_rectangle([60, 60, W - 60, H - 60], radius=26, outline=mul(A, 0.55), width=3)
    f_s = font("vt323", 40)
    text(d, (110, 100), "PIP // POSTAL AUDIT UNIT", f_s, mul(A, 0.75), track=4)
    text(d, (W - 110, 100), "FILING TERMINAL", f_s, mul(A, 0.55), "ra", track=4)
    d.line([(100, 160), (W - 100, 160)], fill=mul(A, 0.4), width=2)
    f = font("vt323", 112)
    n_head = f"REPORT {report}"
    line1 = n_head + (" — " + re_line if re_line else "")
    s1 = typed(line1, t, t_line, 38)
    blink = int(t * 2.2) % 2 == 0
    text(d, (110, 330), s1, f, A)
    y2 = 330
    done1 = len(s1) >= len(line1)
    cur_x_line = 1
    if extra:
        s2 = typed(extra, t, t_line + len(line1) / 38 + 0.25, 24)
        text(d, (110, 330 + 150), s2, f, A)
        cur_line = 2 if len(s1) >= len(line1) else 1
        last = s2 if len(s1) >= len(line1) else s1
    else:
        last = s1
        cur_line = 1
    yc = 330 + (cur_line - 1) * 150
    if blink or (t - t_line) < 0 or not (len(last) >= (len(extra) if cur_line == 2 else len(line1))):
        cx = 110 + tlen(f, last) + 8
        d.rectangle([cx, yc + 22, cx + 44, yc + 96], fill=A)
    if sent_read and t_read is not None and t >= t_read:
        fr = font("vt323", 58)
        text(d, (110, 330 + 170), "READ — 00:00:01.3", fr, (150, 148, 140))
    f_s2 = font("vt323", 38)
    text(d, (110, H - 130), "FILED BY: PIP    COPIES: 1", f_s2, mul(A, 0.55), track=4)
    return img


def pip_report():
    clips = []
    specs = [
        ("1204", "#1,204", "RE: CAPTAIN", '"TAKE IT" (x5)'),
        ("1205", "#1,205", "RE: THE ATLAS", None),
        ("1206", "#1,206", "RE: MAN, AVERAGE", None),
    ]
    for key, num, re_line, extra in specs:
        def dr(t, i, alpha=False, num=num, re_line=re_line, extra=extra):
            return _pip_draw(t, num, re_line, extra)
        clips.append(ClipSpec("02_pip_report_" + key, 9.0, dr, "amber", stills=[7.0],
                              cues={"typing_starts": 2.0, "complete_by": 5.0}))
    # 1,207 SENT, then exactly 2.6 s later READ line
    t_sent = 2.0
    sent_len = len("REPORT #1,207 — SENT")
    t_sent_done = t_sent + sent_len / 38.0
    t_read = t_sent_done + 2.6

    def dr207(t, i, alpha=False):
        return _pip_draw(t, "#1,207", "SENT", None, sent_read=True, t_read=t_read)
    clips.append(ClipSpec("02_pip_report_1207_sent_read", t_read + 4.5, dr207, "amber",
                          stills=[t_sent_done + 1.0, t_read + 2.0],
                          cues={"SENT_fully_shown": round(t_sent_done, 3), "held_s": 2.6,
                                "READ_line_appears": round(t_read, 3)},
                          notes="SENT fully typed at cue, held exactly 2.6 s, then grey READ line appears."))
    return clips


# =========================================================================
# 3. ENGINE READOUT ROW, DYING SCREENS, COFFEE LIGHT
# =========================================================================
ENG_TILES = [  # label, unit, nominal, colour, font, format
    ("L ENG  RPM", "x100", 482, AMBER, "vt323"),
    ("L ENG  THRUST", "kN", 61.4, TEAL, "sharetech"),
    ("FUEL FLOW", "kg/h", 318, (150, 255, 130), "plex"),
    ("L ENG  TEMP", "degC", 640, (235, 235, 215), "barlowsb"),
    ("OIL  PRESS", "bar", 7.2, (255, 150, 90), "space"),
]


def _engine_draw(t, t_drop=2.5):
    img, d = canvas()
    f_lab = font("sharetech", 28)
    text(d, (96, 96), "PROPULSION // PORT SIDE", f_lab, mul(AMBER, 0.55), track=4)
    tw, gap, x0, y0, th = 336, 28, 70, 270, 500
    for k, (lab, unit, nom, col, fn) in enumerate(ENG_TILES):
        x = x0 + k * (tw + gap)
        d.rectangle([x, y0, x + tw, y0 + th], fill=(10, 10, 10), outline=mul(col, 0.45), width=3)
        # bezel
        d.rectangle([x - 14, y0 - 14, x + tw + 14, y0 + th + 14], outline=(40, 38, 34), width=6)
        td = t_drop + k * 0.16
        u = smooth(ramp(t, td, td + 0.95))
        v = nom * (1 - u)
        if t < td:
            v = nom * (1 + 0.012 * math.sin(t * 9 + k * 2) + 0.006 * (rnd(k, int(t * 24)) - 0.5))
        txt = ("%.1f" % v) if isinstance(nom, float) else "%d" % round(v)
        if u >= 1:
            txt = "0.0" if isinstance(nom, float) else "0"
        fb = font(fn, 112 if fn != "vt323" else 140, wght=None)
        text(d, (x + tw / 2, y0 + 230), txt, fb, col, "mm")
        text(d, (x + 20, y0 + 26), lab, font("sharetech", 26), mul(col, 0.85), track=2)
        text(d, (x + tw - 20, y0 + 70), unit, font("sharetech", 26), mul(col, 0.6), "ra")
        # bar gauge
        bx0, by0, bw, bh = x + 26, y0 + 360, tw - 52, 34
        d.rectangle([bx0, by0, bx0 + bw, by0 + bh], outline=mul(col, 0.5), width=2)
        frac = clamp(v / nom) if nom else 0
        segs = 16
        for s in range(segs):
            if (s + 0.5) / segs <= frac:
                d.rectangle([bx0 + 4 + s * (bw - 8) / segs, by0 + 5, bx0 + 4 + (s + 1) * (bw - 8) / segs - 4, by0 + bh - 5],
                            fill=col)
        if u >= 1 and int(t * 2.5) % 2 == 0:
            text(d, (x + tw / 2, y0 + th - 44), "NO SIGNAL", font("sharetech", 28), mul((255, 90, 70), 1.0), "mm", track=3)
    return img


def engine_readouts():
    dur = 11.0

    def dr(t, i, alpha=False):
        return _engine_draw(t)
    return [ClipSpec("03_engine_readouts_to_zero", dur, dr, "amber", stills=[1.5, 6.5],
                     cues={"drop_starts": 2.5, "all_zero_by": round(2.5 + 4 * 0.16 + 0.95, 2)},
                     notes="Row of five mismatched engine readouts, all dropping to zero.")]


# -- dying screens: six mismatched tiles collapse like CRTs, one by one ------
def _tile_content(k, t):
    """return PIL image (tw x th) for tile k, content alive."""
    sizes = [(300, 420), (360, 300), (300, 360), (330, 440), (360, 330), (290, 400)]
    tw, th = sizes[k]
    img = Image.new("RGB", (tw, th), (0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = [AMBER, TEAL, (150, 255, 130), (235, 235, 215), (255, 150, 90), (120, 200, 255)]
    col = cols[k]
    fn = ["vt323", "sharetech", "plex", "barlowsb", "space", "sharetech"][k]
    labs = ["L ENG", "NAV LIGHTS", "HEATING", "COOLANT", "AIR / O2", "COMMS"]
    d.rectangle([2, 2, tw - 3, th - 3], outline=mul(col, 0.5), width=2)
    text(d, (16, 12), labs[k], font("sharetech", 26), mul(col, 0.9), track=2)
    if k == 0:
        text(d, (tw / 2, th / 2), "482", font("vt323", 120), col, "mm")
        text(d, (tw / 2, th - 60), "RPM x100", font("sharetech", 24), mul(col, 0.6), "mm")
    elif k == 1:
        for j, (cx, cy) in enumerate([(70, 130), (230, 130), (150, 200), (90, 250), (210, 250)]):
            on = (int(t * 2) + j) % 2 == 0
            d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=col if on else mul(col, 0.25))
    elif k == 2:
        pts = [(20 + j * 14, 240 - 50 * math.sin(j / 3.0) - 6 * math.sin(t * 3 + j)) for j in range(20)]
        d.line(pts, fill=col, width=4)
        text(d, (tw / 2, 80), "21.4 C", font(fn, 54), col, "mm")
    elif k == 3:
        for j in range(5):
            h = 60 + 40 * math.sin(j * 1.3 + t) + 10 * j
            d.rectangle([22 + j * 56, th - 40 - h, 60 + j * 56, th - 40], fill=col)
    elif k == 4:
        text(d, (tw / 2, 160), "20.9%", font(fn, 64), col, "mm")
        for j in range(6):
            d.rectangle([20 + j * 55, 250, 60 + j * 55, 290], outline=col, width=2)
    else:
        for j in range(24):
            h = 16 + 70 * abs(math.sin(j * 0.7 + t * 4)) * (0.4 + 0.6 * rnd(j, int(t * 12)))
            d.rectangle([14 + j * 11, 250 - h, 22 + j * 11, 250], fill=col)
    return img


def screens_dying(order=(0, 1, 2, 3, 4, 5), t_first=3.0, gap_s=0.9):
    dur = t_first + gap_s * 6 + 4.0
    base_x = [70, 405, 805, 1140, 1520, 1870]  # replaced below by computed layout
    sizes = [(300, 420), (360, 300), (300, 360), (330, 440), (360, 330), (290, 400)]
    pad = 36
    total = sum(s[0] for s in sizes) + pad * 5
    xs = []
    x = (W - total) / 2
    for s in sizes:
        xs.append(int(x))
        x += s[0] + pad
    yb = 760  # bottoms aligned

    def dr(t, i, alpha=False):
        img, d = canvas()
        text(d, (96, 96), "BRIDGE // SYSTEMS", font("sharetech", 28), mul(AMBER, 0.5), track=4)
        for k in range(6):
            tw, th = sizes[k]
            td = t_first + order.index(k) * gap_s
            u = (t - td) / 0.42  # 0..1 collapse
            tile = _tile_content(k, t)
            x, y = xs[k], yb - th
            d.rectangle([x - 12, y - 12, x + tw + 12, yb + 12], outline=(40, 38, 34), width=5)
            if u <= 0:
                img.paste(tile, (x, y))
            elif u < 1:
                # CRT collapse: vertical squash to a line with brightness spike, then dot
                hh = max(3, int(th * (1 - smooth(u)) ** 1.5))
                tl = tile.resize((tw, hh)).point(lambda v: min(255, int(v * (1 + 1.2 * u))))
                img.paste(tl, (x, y + (th - hh) // 2))
            elif u < 1.9:
                v = (u - 1) / 0.9
                wlen = int(tw * (1 - smooth(v)) ** 1.2)
                if wlen > 2:
                    d.rectangle([x + (tw - wlen) // 2, y + th // 2 - 1, x + (tw + wlen) // 2, y + th // 2 + 1],
                                fill=(255, 255, 235))
                    d.ellipse([x + tw // 2 - 3 - int(5 * (1 - v)), y + th // 2 - 3, x + tw // 2 + 3 + int(5 * (1 - v)), y + th // 2 + 3], fill=(255, 255, 240))
            # afterglow dot fading
            if 1.9 <= u < 3.2:
                a = 1 - (u - 1.9) / 1.3
                d.ellipse([x + tw // 2 - 3, y + th // 2 - 3, x + tw // 2 + 3, y + th // 2 + 3], fill=mul((255, 255, 240), a))
        return img
    cues = {"screen_%d_dark" % (k + 1): round(t_first + order.index(k) * gap_s + 0.5, 2) for k in range(6)}
    return [ClipSpec("03_screens_dying", dur, dr, "amber", stills=[1.5, t_first + 2.5 * gap_s + 0.2, dur - 1], cues=cues,
                     notes="Six mismatched screens collapse one by one: L ENG, NAV LIGHTS, HEATING, COOLANT, AIR/O2, COMMS.")]


def coffee_light():
    G = (70, 255, 90)

    def draw(mode):
        def dr(t, i, alpha=False):
            img, d = canvas()
            cx, cy = 960, 540
            # plastic fascia: faint, lit only by the LED
            on = 1.0
            if mode == "out":
                t0 = 2.6
                if t < t0:
                    on = 1.0
                elif t < t0 + 0.9:
                    u = t - t0
                    on = [1, 0.3, 1, 0.15, 0.7, 0.05][min(5, int(u / 0.15))]
                else:
                    on = 0.0
            else:
                t0 = 2.6
                if t < t0:
                    on = 0.0
                elif t < t0 + 1.2:
                    u = t - t0
                    on = [0.2, 0, 0.5, 0.1, 0.8, 0.4, 0.9, 0.7][min(7, int(u / 0.15))]
                else:
                    on = 1.0
            d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(22, 24, 22), outline=(46, 48, 44), width=3)
            if on > 0.01:
                d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=mul(G, on))
                d.ellipse([cx - 7, cy - 9, cx + 1, cy - 2], fill=mul((220, 255, 220), on))
            text(d, (cx, cy + 74), "BREW", font("sharetech", 28), mul((90, 90, 84), 1.0), "mm", track=6)
            return img
        return dr
    lk = Look(base=(0.004, 0.006, 0.004), soft=0.9, bloom=1.4, bloom_r=(3, 22), scan=0.0, flicker=0.01,
              curve=0.0, vignette=0.4, hum=0.0, grain=0.01, seed=21)
    return [ClipSpec("03_coffee_light_goes_out", 7.0, draw("out"), lookobj=lk, stills=[1.0, 5.5],
                     cues={"light_starts_dying": 2.6, "fully_out": 3.5}),
            ClipSpec("03_coffee_light_comes_back_on", 7.0, draw("on"), lookobj=lk, stills=[1.0, 5.5],
                     cues={"light_starts_returning": 2.6, "steady_on": 3.8})]


# =========================================================================
# 4. BANK CALL WINDOW
# =========================================================================
BANK_NAME = "MERRILARK"  # invented, generic. Rights check still advised.
FR = (700, 170, 1840, 811)  # video frame (1140x641 ~ 16:9)


def _bank_logo(d, cx, cy, r):
    """cheerful invented logo: sun-yellow coin with a big smile and one raised eyebrow-less happy face."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 208, 64))
    d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], outline=(255, 236, 150), width=6)
    d.ellipse([cx - r * 0.42 - 12, cy - r * 0.28 - 18, cx - r * 0.42 + 12, cy - r * 0.28 + 18], fill=(30, 60, 120))
    d.ellipse([cx + r * 0.42 - 12, cy - r * 0.28 - 18, cx + r * 0.42 + 12, cy - r * 0.28 + 18], fill=(30, 60, 120))
    d.arc([cx - r * 0.62, cy - r * 0.35, cx + r * 0.62, cy + r * 0.62], 15, 165, fill=(30, 60, 120), width=14)


def _spinner(d, cx, cy, r, t, col):
    for k in range(12):
        a = (k / 12 - t * 1.0) * 2 * math.pi
        b = ((k / 12 - (t * 1.0) % 1.0) % 1.0)
        c = mul(col, 0.15 + 0.85 * (1 - b))
        d.line([(cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6),
                (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=c, width=7)


def _bank_draw(t, state, alpha, timer_stop=None):
    img, d = canvas()
    if state == "black":
        return img
    # window chrome
    d.rectangle([0, 0, W, H], fill=(18, 34, 62))
    d.rectangle([0, 0, W, 76], fill=(12, 24, 46))
    text(d, (36, 38), BANK_NAME + " · RECOVERIES", font("jost", 32, 600), (255, 208, 64), "lm", track=4)
    text(d, (W - 36, 38), "SECURE CALL", font("jost", 28, 400), (150, 180, 220), "rm", track=3)
    # logo column
    d.rounded_rectangle([60, 130, 640, 880], radius=24, fill=(26, 48, 86))
    _bank_logo(d, 350, 420, 190)
    text(d, (350, 700), BANK_NAME.title(), font("jost", 84, 600), (255, 255, 255), "mm", track=2)
    text(d, (350, 780), "Here to help you thrive!", font("jost", 36, 400), (255, 208, 64), "mm")
    # video frame
    x0, y0, x1, y1 = FR
    if not alpha:
        for yy in range(y0, y1, 2):
            g = int(lerp(78, 58, (yy - y0) / (y1 - y0)))
            d.line([(x0, yy), (x1, yy)], fill=(g, g + 12, g + 28))
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=(90, 120, 170), width=4)
    # caption and controls
    cap = "TEMI ADEYEMI  ·  Recoveries"
    live = state in ("live", "frozen")
    if state == "connecting":
        cap = "Connecting…"
    text(d, (x0, y1 + 40), cap, font("jost", 40, 500), (235, 240, 250), "lm")
    # delay and timer
    tt = t if timer_stop is None else min(t, timer_stop)
    clock = "%02d:%02d" % (int(tt) // 60, int(tt) % 60) if live else "--:--"
    text(d, (x1, y1 + 40), clock, font("sharetech", 40), (200, 215, 240), "rm")
    text(d, (x1 - 190, y1 + 40), "DELAY 1.3 s" if live else "", font("sharetech", 30), (150, 180, 220), "rm")
    # LIVE tag
    if live:
        dot_on = (int(t * 1.6) % 2 == 0) and state == "live"
        d.rounded_rectangle([x0 + 20, y0 + 20, x0 + 150, y0 + 66], radius=10, fill=(20, 24, 36))
        d.ellipse([x0 + 34, y0 + 34, x0 + 52, y0 + 52], fill=(255, 60, 60) if (dot_on or state == "frozen") else (90, 30, 30))
        text(d, (x0 + 64, y0 + 43), "LIVE" if state == "live" else "LIVE", font("jost", 28, 600), (255, 255, 255), "lm")
    # controls
    for k, c in enumerate([(70, 90, 130), (70, 90, 130)]):
        d.ellipse([60 + k * 100, 940, 120 + k * 100, 1000], fill=c)
    d.ellipse([W - 130, 936, W - 60, 1006], fill=(210, 50, 50))
    text(d, (W - 95, 971), "END", font("jost", 22, 600), (255, 255, 255), "mm")
    # state overlays
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if state == "connecting":
        if not alpha:
            d.rectangle([x0, y0, x1, y1], fill=(14, 22, 38))
        _spinner(d, cx, cy - 30, 54, t, (255, 208, 64))
        dots = "." * (int(t * 2.5) % 4)
        text(d, (cx, cy + 90), "Connecting you to Recoveries" + dots, font("jost", 36, 400), (200, 215, 240), "mm")
    if state == "frozen":
        # buffering ring over the frame
        _spinner(d, cx, cy, 36, t, (255, 255, 255))
        text(d, (x0 + 22, y1 - 36), "poor connection", font("jost", 26, 400), (255, 255, 255), "lm")
    return img


def bank_call():
    mk = lambda st, **kw: (lambda t, i, alpha=False: _bank_draw(t, st, alpha, **kw))
    lk = LOOKS["lcd"]
    m = [FR]
    clips = []
    for st, dur in [("connecting", 6.0), ("live", 6.0), ("frozen", 6.0), ("black", 4.0)]:
        kw = {"timer_stop": 2.0} if st == "frozen" else {}
        clips.append(ClipSpec("04_bank_call_" + st, dur, mk(st, **kw), "lcd", stills=[3.0], dual=True,
                              matte=m if st in ("live", "frozen") else None))

    def seq(t, i, alpha=False):
        if t < 4.0:
            return _bank_draw(t, "connecting", alpha)
        if t < 10.0:
            return _bank_draw(t - 4.0, "live", alpha)
        if t < 14.0:
            return _bank_draw(t - 10.0 + 6.0, "frozen", alpha, timer_stop=2.0 + 6.0 - 6.0 + 0.0) if False else \
                _bank_draw(t - 10.0, "frozen", alpha, timer_stop=2.0)
        return _bank_draw(t, "black", alpha)
    clips.append(ClipSpec("04_bank_call_sequence", 19.0, seq, "lcd", dual=True, matte=m,
                          stills=[2.0, 7.0, 12.0],
                          cues={"connecting": 0.0, "live": 4.0, "frozen": 10.0, "black": 14.0},
                          notes="connecting -> live -> frozen -> black. Video frame region is transparent in the alpha "
                                "version; place the agent still under it (matte PNG provided)."))
    return clips


# =========================================================================
# 5. CARGO SCREEN
# =========================================================================
CF = (260, 150, 1660, 938)  # 1400x788 ~ 16:9


def _cargo_draw(t, alpha, temp="21°"):
    img, d = canvas()
    G = (130, 255, 196)
    x0, y0, x1, y1 = CF
    if not alpha:  # placeholder view: dim noisy grey-green with vignette
        rs = np.random.RandomState(8)
        base = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
        yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]
        r = np.sqrt(((xx - (x1 - x0) / 2) / (x1 - x0)) ** 2 + ((yy - (y1 - y0) / 2) / (y1 - y0)) ** 2)
        lvl = (0.30 - 0.28 * r) + 0.02 * rs.randn(*r.shape)
        base[..., 0] = lvl * 0.55
        base[..., 1] = lvl * 0.9
        base[..., 2] = lvl * 0.7
        patch = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))
        img.paste(patch, (x0, y0))
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=mul(G, 0.8), width=3)
    L = 70
    for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line([(cx + sx * 24, cy + sy * 24), (cx + sx * (24 + L), cy + sy * 24)], fill=G, width=4)
        d.line([(cx + sx * 24, cy + sy * 24), (cx + sx * 24, cy + sy * (24 + L))], fill=G, width=4)
    f = font("sharetech", 34)
    text(d, (x0 + 50, y0 + 44), "CARGO HOLD · CAM 2", f, G, track=3)
    if int(t * 1.4) % 2 == 0:
        d.ellipse([x1 - 210, y0 + 48, x1 - 190, y0 + 68], fill=(255, 70, 60))
    text(d, (x1 - 174, y0 + 44), "REC", f, G, track=3)
    # bottom bar outside the frame: temperature
    text(d, (x0, y1 + 76), "TEMP", font("sharetech", 40), mul(G, 0.75), "lm", track=4)
    text(d, (x0 + 150, y1 + 70), temp, font("sharetech", 100), G, "lm")
    tc = "%02d:%02d:%02d:%02d" % (int(t) // 3600, int(t) // 60 % 60, int(t) % 60, int(t * 24) % 24)
    text(d, (x1, y1 + 76), "TC " + tc, font("sharetech", 36), mul(G, 0.7), "rm", track=2)
    text(d, (x1, y1 + 118 - 4), "HOLD SEALED", font("sharetech", 28), mul(G, 0.5), "rm", track=3)
    return img


def cargo_screen(temp="21°"):
    return [ClipSpec("05_cargo_screen", 10.0, lambda t, i, alpha=False: _cargo_draw(t, alpha, temp), "green",
                     dual=True, matte=[CF], stills=[4.0],
                     notes="Framed view placeholder (transparent in alpha version, matte PNG provided) + 21 deg read-out.")]
