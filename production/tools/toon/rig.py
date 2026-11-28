#!/usr/bin/env python3
"""Flat-cartoon puppet rig, drawn with Skia (vector, anti-aliased) — TEST 3.

A character = picture-made HEAD parts (front + three-quarter, cut from a model sheet, drawn with
no eyes/brows/mouth) + code-drawn FACE (eyes, pupils, lids, brows, 9 mouth shapes) + code-drawn
BODY (torso, upper/lower arms, 3 hand shapes, legs with 2-bone IK, feet), each part pivoting at a
joint. Poses come from keyed channels (see `Channels`) with easing, overshoot and settle; idle
motion (breathing, sway, blinks, eye darts, braid/pendant lag) is procedural and deterministic,
so any frame can be rendered on its own (parallel workers).
"""
import json, math, os
import numpy as np, skia

# ---------------------------------------------------------------- easing / channels
def smoother(x):
    x = min(max(x, 0.0), 1.0); return x * x * x * (x * (x * 6 - 15) + 10)

def ease(kind, x):
    x = min(max(x, 0.0), 1.0)
    if kind == "lin": return x
    if kind == "io": return smoother(x)
    if kind == "out": return 1 - (1 - x) ** 3
    if kind == "in": return x ** 3
    if kind == "back":      # overshoot then settle
        c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
    if kind == "snap":      # fast arrival, damped wobble (overshoot + settle)
        return 1 - math.exp(-7 * x) * math.cos(11 * x) if x < 1 else 1.0
    if kind == "step": return 1.0 if x >= 1 else 0.0
    return smoother(x)

class Channels:
    """keys: {name: [[t, value, ease, dur], ...]} — value reached at t; the move starts at t-dur
    (dur default 0.35 s). Before the first key the first value holds."""
    def __init__(self, keys, defaults):
        self.keys = keys; self.d = defaults
    def __call__(self, name, t):
        ks = self.keys.get(name)
        if not ks: return self.d.get(name, 0.0)
        v = ks[0][1]
        for k in ks:
            kt, kv = k[0], k[1]; ke = k[2] if len(k) > 2 else "io"; kd = k[3] if len(k) > 3 else 0.35
            if t >= kt: v = kv; continue
            t0 = kt - kd
            if t > t0:
                if isinstance(v, str) or isinstance(kv, str):
                    return kv if t > kt - 0.04 else v
                return v + (kv - v) * ease(ke, (t - t0) / kd)
            break
        return v

def noise1(t, seed, freq=0.5):
    # smooth deterministic noise: sum of incommensurate sines
    s = seed * 12.9898
    return (math.sin(t * freq * 6.283 + s) * 0.55 + math.sin(t * freq * 2.71 * 6.283 + s * 1.7) * 0.3
            + math.sin(t * freq * 5.13 * 6.283 + s * 3.1) * 0.15)

# ---------------------------------------------------------------- skia helpers
def col(h, a=255):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def P(color, stroke=None, cap="round"):
    p = skia.Paint(AntiAlias=True, Color=color)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def poly(pts, close=True):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]: path.lineTo(*q)
    if close: path.close()
    return path

def smooth_path(pts, close=True):
    """Catmull-Rom through pts -> cubic path."""
    n = len(pts); path = skia.Path(); path.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        path.cubicTo(*c1, *c2, *p2)
    if close: path.close()
    return path

def outlined(cv, path, fill, line, lw):
    cv.drawPath(path, P(fill)); cv.drawPath(path, P(line, lw))

def ik2(hip, foot, l1, l2, bend=1):
    """2-bone IK; returns knee point. bend=+1 knee forward (toward +x)."""
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    d = max(1e-6, math.hypot(dx, dy)); d2 = min(d, (l1 + l2) * 0.999)
    a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d2 * d2 - l2 * l2) / (2 * l1 * d2); cosb = max(-1, min(1, cosb))
    b = math.acos(cosb)
    ang = a - bend * b
    return (hip[0] + l1 * math.cos(ang), hip[1] + l1 * math.sin(ang))

# ---------------------------------------------------------------- mouth shapes (Rhubarb A-H, X)
# each: (open height, width scale, teeth top, teeth bottom, tongue, roundness) in mouth-width units
MOUTHS = {
    "X": (0.00, 0.92, 0, 0, 0, 0.0),   # rest, closed
    "A": (0.00, 0.80, 0, 0, 0, 0.0),   # M B P pressed
    "B": (0.13, 0.95, 1, 1, 0, 0.0),   # K S T, teeth together
    "C": (0.30, 1.00, 1, 0, 1, 0.1),   # EH AE
    "D": (0.52, 1.05, 1, 0, 1, 0.2),   # AA wide open
    "E": (0.36, 0.72, 0, 0, 1, 0.6),   # AO ER rounded
    "F": (0.20, 0.45, 0, 0, 0, 1.0),   # UW OW W puckered
    "G": (0.14, 0.95, 1, 0, 0, 0.0),   # F V teeth on lip
    "H": (0.34, 0.95, 1, 0, 2, 0.1),   # L tongue up
}

class Character:
    def __init__(self, rig_path, base_dir):
        self.r = json.load(open(rig_path)); r = self.r
        self.heads = {}
        for ang, hd in r["heads"].items():
            arr = __import__("cv2").imread(os.path.join(base_dir, hd["file"]), -1)
            rgba = arr[..., [2, 1, 0, 3]].copy()
            # premultiply for skia
            a = rgba[..., 3:4].astype(np.float32) / 255.0
            rgba[..., :3] = (rgba[..., :3] * a).astype(np.uint8)
            img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
            self.heads[ang] = (img, hd)
        self.C = {k: col(v) for k, v in r["colors"].items()}

    # ------------------------------------------------------------ face
    def draw_face(self, cv, hd, s, t, ch, mouth, blink):
        C = self.C; lw = hd["line_w"]
        look_x = ch("look_x", t) + 0.10 * noise1(t, self.r["seed"] + 5, 0.9)
        look_y = ch("look_y", t) + 0.06 * noise1(t, self.r["seed"] + 9, 0.7)
        lid = max(ch("lid", t), blink)              # 0 open .. 1 closed
        brow = ch("brow", t); brow_tilt = ch("brow_tilt", t); brow_asym = ch("brow_asym", t)
        for i, e in enumerate(hd["eyes"]):
            ex, ey, rx, ry = e
            # white
            white = skia.Path(); white.addOval(skia.Rect(ex - rx, ey - ry, ex + rx, ey + ry))
            cv.save(); cv.clipPath(white, doAntiAlias=True)
            cv.drawPath(white, P(C["eye_white"]))
            ir = ry * 0.78
            ix, iy = ex + look_x * rx * 0.45, ey + look_y * ry * 0.35
            cv.drawCircle(ix, iy, ir, P(C["iris"]))
            cv.drawCircle(ix, iy, ir * 0.55, P(C["pupil"]))
            cv.drawCircle(ix - ir * 0.3, iy - ir * 0.35, ir * 0.24, P(col("#ffffff")))
            # upper lid (skin) coming down
            ly = ey - ry + (2 * ry + 2) * lid
            lidp = skia.Path(); lidp.moveTo(ex - rx - 4, ey - ry - 6); lidp.lineTo(ex + rx + 4, ey - ry - 6)
            lidp.lineTo(ex + rx + 4, ly); lidp.quadTo(ex, ly + ry * 0.35 * (1 - lid), ex - rx - 4, ly); lidp.close()
            cv.drawPath(lidp, P(C["skin"]))
            cv.restore()
            # lash line on the lid edge, lower line
            ly = ey - ry + (2 * ry) * lid
            lash = skia.Path(); lash.moveTo(ex - rx * 1.08, ey - ry * 0.15 + (ly - (ey - ry)) * 0.6)
            lash.quadTo(ex, ly - ry * 0.25 * (1 - lid), ex + rx * 1.1, ey - ry * 0.25 + (ly - (ey - ry)) * 0.6)
            cv.drawPath(lash, P(C["line"], lw * 1.9))
            if lid < 0.85:
                lo = skia.Path(); lo.moveTo(ex - rx * 0.7, ey + ry * 0.92); lo.quadTo(ex, ey + ry * 1.12, ex + rx * 0.7, ey + ry * 0.9)
                cv.drawPath(lo, P(C["line"], lw * 0.7))
            # brow: raise (up = +), tilt (inner end up = +), asym raises the second brow more
            bx0, by0, bx1, by1 = hd["brows"][i]
            inner_is_right = (bx1 > bx0) == (i == 0)
            up = brow * ry * 0.9 + (brow_asym * ry * 0.9 if i == 1 else 0)
            tin = brow_tilt * ry * 0.6
            yi = (by1 if inner_is_right else by0) - up - tin
            yo = (by0 if inner_is_right else by1) - up + tin * 0.3
            p0 = (bx0, yo if inner_is_right else yi); p1 = (bx1, yi if inner_is_right else yo)
            bp = skia.Path(); bp.moveTo(*p0); bp.quadTo((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - ry * 0.35, *p1)
            cv.drawPath(bp, P(C["brow"], hd["brow_w"]))
        self.draw_mouth(cv, hd, mouth, t)

    def draw_mouth(self, cv, hd, shape, t):
        C = self.C; mx, my, mw = hd["mouth"]; lw = hd["line_w"]
        oh, ws, tt, tb, tg, rnd = MOUTHS.get(shape, MOUTHS["X"])
        w = mw * ws; h = mw * oh; smile = hd.get("smile", 0.08) * mw
        if h < 1:
            pth = skia.Path(); pth.moveTo(mx - w / 2, my - smile * 0.4)
            pth.quadTo(mx, my + smile * (0.9 if shape == "X" else 0.3), mx + w / 2, my - smile * 0.4)
            cv.drawPath(pth, P(C["line"], lw * (1.5 if shape == "A" else 1.2)))
            return
        top = my - h * 0.3; bot = my + h * 0.7
        k = 0.5 + 0.4 * rnd
        pth = skia.Path(); pth.moveTo(mx - w / 2, my)
        pth.cubicTo(mx - w / 2, top - smile * 0.2, mx - w * (0.5 - k * 0.3), top, mx, top)
        pth.cubicTo(mx + w * (0.5 - k * 0.3), top, mx + w / 2, top - smile * 0.2, mx + w / 2, my)
        pth.cubicTo(mx + w / 2, bot, mx + w * 0.2, bot, mx, bot)
        pth.cubicTo(mx - w * 0.2, bot, mx - w / 2, bot, mx - w / 2, my); pth.close()
        cv.drawPath(pth, P(C["mouth_in"]))
        cv.save(); cv.clipPath(pth, doAntiAlias=True)
        if tt: cv.drawRect(skia.Rect(mx - w / 2, top - 5, mx + w / 2, top + max(3, h * 0.28)), P(col("#fbf6ee")))
        if tb: cv.drawRect(skia.Rect(mx - w / 2, bot - max(3, h * 0.3), mx + w / 2, bot + 5), P(col("#fbf6ee")))
        if tg == 1: cv.drawOval(skia.Rect(mx - w * 0.3, bot - h * 0.38, mx + w * 0.3, bot + h * 0.3), P(C["tongue"]))
        if tg == 2: cv.drawOval(skia.Rect(mx - w * 0.22, top - h * 0.1, mx + w * 0.22, top + h * 0.45), P(C["tongue"]))
        cv.restore()
        cv.drawPath(pth, P(C["line"], lw * 1.2))
        if shape == "G":  # top teeth resting on lower lip
            cv.drawLine(mx - w * 0.3, bot + 1, mx + w * 0.3, bot + 1, P(C["lip"], lw * 1.4))

    # ------------------------------------------------------------ body pieces
    def limb(self, cv, pts, w, fill, line, lw):
        for i in range(len(pts) - 1):
            cv.drawLine(*pts[i], *pts[i + 1], P(line, w[i] + 2 * lw))
        for i in range(len(pts) - 1):
            cv.drawLine(*pts[i], *pts[i + 1], P(fill, w[i]))

    def hand(self, cv, x, y, ang, shape, u, flip=1):
        C = self.C; lw = self.r["line_w"] * u
        cv.save(); cv.translate(x, y); cv.rotate(math.degrees(ang) - 90); cv.scale(flip, 1)
        s = u * 3.0
        palm = skia.Path(); palm.addRRect(skia.RRect.MakeRectXY(skia.Rect(-s * 0.9, -s * 0.2, s * 0.9, s * 1.5), s * 0.6, s * 0.6))
        if shape == "open":
            for k in range(4):
                fx = -s * 0.65 + k * s * 0.43
                fp = skia.Path(); fp.addRRect(skia.RRect.MakeRectXY(skia.Rect(fx - s * 0.2, s * 0.9, fx + s * 0.2, s * 2.3 - abs(k - 1.5) * s * 0.25), s * 0.2, s * 0.2))
                outlined(cv, fp, C["skin"], C["line"], lw)
            th = skia.Path(); th.addRRect(skia.RRect.MakeRectXY(skia.Rect(s * 0.6, s * 0.1, s * 1.45, s * 0.55), s * 0.22, s * 0.22))
            outlined(cv, th, C["skin"], C["line"], lw)
            outlined(cv, palm, C["skin"], C["line"], lw)
            for k in range(4):
                fx = -s * 0.65 + k * s * 0.43
                cv.drawRect(skia.Rect(fx - s * 0.2 + lw * 0.6, s * 0.8, fx + s * 0.2 - lw * 0.6, s * 1.4), P(C["skin"]))
        elif shape == "point":
            fp = skia.Path(); fp.addRRect(skia.RRect.MakeRectXY(skia.Rect(-s * 0.85, s * 0.7, -s * 0.4, s * 2.6), s * 0.22, s * 0.22))
            outlined(cv, fp, C["skin"], C["line"], lw)
            outlined(cv, palm, C["skin"], C["line"], lw)
            cv.drawRect(skia.Rect(-s * 0.85 + lw * 0.6, s * 0.7, -s * 0.4 - lw * 0.6, s * 1.3), P(C["skin"]))
            for k in range(3):
                cv.drawLine(-s * 0.3 + k * s * 0.38, s * 1.05, -s * 0.3 + k * s * 0.38, s * 1.45, P(C["line"], lw * 0.7))
        else:  # fist / hold
            outlined(cv, palm, C["skin"], C["line"], lw)
            for k in range(3):
                cv.drawLine(-s * 0.45 + k * s * 0.45, s * 0.95, -s * 0.45 + k * s * 0.45, s * 1.45, P(C["line"], lw * 0.7))
        if shape == "stamp":
            st = skia.Path(); st.addRRect(skia.RRect.MakeRectXY(skia.Rect(-s * 0.5, s * 1.3, s * 0.5, s * 3.0), s * 0.3, s * 0.3))
            outlined(cv, st, col("#3c4a66"), C["line"], lw)
            b = skia.Path(); b.addRect(skia.Rect(-s * 1.3, s * 3.0, s * 1.3, s * 3.8))
            outlined(cv, b, col("#a8643a"), C["line"], lw)
            cv.drawRect(skia.Rect(-s * 1.3, s * 3.8, s * 1.3, s * 4.15), P(col("#c8312c")))
        if shape == "form":
            f = skia.Path(); f.addRect(skia.Rect(-s * 2.2, s * 0.6, s * 2.6, s * 6.4))
            outlined(cv, f, col("#f7f1df"), C["line"], lw)
            for k in range(5):
                cv.drawLine(-s * 1.6, s * (1.6 + k * 0.9), s * (1.9 - (k % 2) * 0.8), s * (1.6 + k * 0.9), P(col("#7d8aa6"), lw * 0.9))
            cv.drawRect(skia.Rect(-s * 1.6, s * 5.3, -s * 0.4, s * 5.9), P(col("#c8312c", 200)))
            outlined(cv, palm, C["skin"], C["line"], lw)
        cv.restore()

    # ------------------------------------------------------------ whole figure
    def pose_points(self, t, ch, walk):
        r = self.r; H = ch("H", t); u = H / 100.0
        x = ch("x", t); gy = ch("y", t)
        breathe = math.sin(t * 2 * math.pi / 3.6 + r["seed"]) * 0.5
        lean = math.radians(ch("lean", t) + 0.8 * noise1(t, r["seed"], 0.23))
        crouch = ch("crouch", t)
        hip_h = r["hip_h"] - crouch
        hx, hy = x, gy - hip_h * u
        feet = [(x - r["stance"] * u, gy), (x + r["stance"] * u, gy)]
        lift = [0, 0]
        if walk:
            hx, hy, feet, lift = walk(t, u)
        neck = (hx + math.sin(lean) * r["torso"] * u, hy - math.cos(lean) * r["torso"] * u - breathe * 0.35 * u)
        return dict(u=u, hip=(hx, hy), neck=neck, lean=lean, feet=feet, lift=lift, breathe=breathe)

    def draw(self, cv, t, ch, mouth="X", walk=None, extras=None):
        r = self.r; C = self.C; G = self.pose_points(t, ch, walk); u = G["u"]
        lw = r["line_w"] * u; hx, hy = G["hip"]; nx, ny = G["neck"]; lean = G["lean"]
        f = r["facing"]   # +1 faces screen-right, -1 screen-left
        # shoulders
        sw = r["shoulder_w"] * u; shrug = ch("shrug", t) * u
        ca, sa = math.cos(lean), math.sin(lean)
        sh_y = ny + 3.2 * u - shrug - G["breathe"] * 0.25 * u
        shoulders = [(nx - sw * ca, sh_y - sw * sa * 0.0), (nx + sw * ca, sh_y)]
        # back = the side the character faces (it is turned 3/4)
        back_i = 1 if f > 0 else 0
        def arm(i):
            sx, sy = shoulders[i]
            side = -1 if i == 0 else 1
            a1 = math.radians(90 + ch(f"sh{i}", t) * side * -1 * -1) if False else None
            # shoulder angle: degrees from straight down, positive = forward (toward facing)
            sa_ = math.radians(ch(f"sh{i}", t)) * f
            ea_ = math.radians(ch(f"el{i}", t)) * f
            l1, l2 = r["arm_up"] * u, r["arm_lo"] * u
            ex, ey = sx + l1 * math.sin(sa_ + lean * 0.5), sy + l1 * math.cos(sa_ + lean * 0.5)
            wx, wy = ex + l2 * math.sin(sa_ + ea_ + lean * 0.5), ey + l2 * math.cos(sa_ + ea_ + lean * 0.5)
            return (sx, sy), (ex, ey), (wx, wy), math.atan2(wy - ey, wx - ex)
        arms = [arm(0), arm(1)]
        def draw_arm(i):
            s, e, w, ang = arms[i]
            self.limb(cv, [s, e, w], [r["sleeve_w"] * u, r["sleeve_w"] * 0.85 * u], C["sleeve"], C["line"], lw)
            cv.drawLine(*w, w[0] - math.cos(ang) * 1.2 * u, w[1] - math.sin(ang) * 1.2 * u, P(C["cuff"], r["sleeve_w"] * 0.8 * u, cap="butt"))
            self.hand(cv, w[0], w[1], ang, ch(f"hand{i}", t), u, flip=f)
        def draw_leg(i):
            if not r.get("legs", True): return
            hip = (hx + (i * 2 - 1) * r["hip_w"] * u, hy)
            ft = G["feet"][i]; ankle = (ft[0], ft[1] - 3.0 * u - G["lift"][i])
            knee = ik2(hip, ankle, r["leg_up"] * u, r["leg_lo"] * u, bend=-f)
            self.limb(cv, [hip, knee, ankle], [r["leg_w"] * u, r["leg_w"] * 0.85 * u], C["trousers"], C["line"], lw)
            # boot
            bx, by = ankle; L = r["foot"] * u
            boot = skia.Path(); boot.addRRect(skia.RRect.MakeRectXY(
                skia.Rect(bx - L * 0.35 if f > 0 else bx - L * 0.75, by - 1.5 * u, bx + L * 0.75 if f > 0 else bx + L * 0.35, by + 3.2 * u), 2.2 * u, 2.2 * u))
            outlined(cv, boot, C["boot"], C["line"], lw)
        # ---- draw order: back arm, back leg, front leg, torso, head, front arm
        if extras and "under" in extras: extras["under"](cv, G)
        draw_arm(back_i)
        draw_leg(back_i); draw_leg(1 - back_i)
        self.draw_torso(cv, G, shoulders, t, ch)
        self.draw_head(cv, G, t, ch, mouth)
        draw_arm(1 - back_i)
        if extras and "over" in extras: extras["over"](cv, G, arms)
        return G, arms

    def draw_torso(self, cv, G, shoulders, t, ch):
        r = self.r; C = self.C; u = G["u"]; lw = r["line_w"] * u
        hx, hy = G["hip"]; (lx, ly), (rx_, ry_) = shoulders
        hw = r["waist_w"] * u; hem = r["hem"] * u
        sway = noise1(t - 0.25, r["seed"] + 3, 0.6) * 0.8 * u   # hem lag
        body = smooth_path([(lx - 1.0 * u, ly + 1.5 * u), (lx + 2 * u, ly - 1.2 * u), ((lx + rx_) / 2, ly - 0.8 * u),
                            (rx_ - 2 * u, ry_ - 1.2 * u), (rx_ + 1.0 * u, ry_ + 1.5 * u),
                            (hx + hw + sway, hy + hem), (hx + sway * 1.3, hy + hem + 1.0 * u), (hx - hw + sway, hy + hem)])
        outlined(cv, body, C["torso"], C["line"], lw)
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        f = r["facing"]
        # one shadow tone on the side away from the key light (key is screen-left/front)
        sx = hx + (hw * 0.55)
        cv.drawPath(poly([(sx, ly - 5 * u), (rx_ + 5 * u, ry_ - 5 * u), (hx + hw + 6 * u, hy + hem + 4 * u), (sx - 1 * u, hy + hem + 4 * u)]), P(C["torso_sh"]))
        for d in r.get("torso_details", []):
            k = d["kind"]
            if k == "collar":
                nx, ny = G["neck"]
                cv.drawPath(poly([(nx - 4.2 * u, ny + 1 * u), (nx + 4.2 * u, ny + 1 * u), (nx, ny + d["depth"] * u)]), P(col(d["color"])))
                cv.drawPath(poly([(nx - 4.2 * u, ny + 1 * u), (nx, ny + d["depth"] * u), (nx + 4.2 * u, ny + 1 * u)], close=False), P(C["line"], lw))
            elif k == "zip":
                nx, ny = G["neck"]
                cv.drawLine(nx + d["dx"] * u, ny + d["y0"] * u, hx + d["dx"] * u + sway, hy + hem, P(col(d["color"]), lw * 0.9))
            elif k == "rect":
                nx, ny = G["neck"]
                x0, y0, w, h = [v * u for v in d["r"]]
                rp = skia.Path(); rp.addRRect(skia.RRect.MakeRectXY(skia.Rect(nx + x0, ny + y0, nx + x0 + w, ny + y0 + h), 0.8 * u, 0.8 * u))
                outlined(cv, rp, col(d["color"]), C["line"], lw * 0.8)
            elif k == "belt":
                cv.drawRect(skia.Rect(hx - hw - 3 * u, hy - d["y"] * u, hx + hw + 3 * u, hy - d["y"] * u + d["h"] * u), P(col(d["color"])))
                cv.drawRect(skia.Rect(hx - 2 * u, hy - d["y"] * u - 0.3 * u, hx + 2 * u, hy - d["y"] * u + d["h"] * u + 0.3 * u), P(col("#d8a640")))
        cv.restore()
        outlined(cv, body, skia.ColorTRANSPARENT, C["line"], lw)
        nx, ny = G["neck"]
        # lag source: how far the upper body moved in the last 0.2 s (deterministic, no state)
        def neck_at(tt):
            g = self.pose_points(tt, ch, None); return g["neck"]
        if r.get("pendant"):
            p = r["pendant"]; n0 = neck_at(t - 0.18)
            swing = (nx - n0[0]) * 0.012 / u * 60 + 4 * math.sin(t * 2.6 + r["seed"])
            ang = math.radians(max(-35, min(35, -swing)))
            top = (nx, ny + 1.5 * u); L = p["len"] * u
            end = (top[0] + math.sin(ang) * L, top[1] + math.cos(ang) * L)
            cv.drawLine(nx - 3.5 * u, ny + 1 * u, end[0], end[1] - 1.5 * u, P(col(p["chain"]), lw * 0.7))
            cv.drawLine(nx + 3.5 * u, ny + 1 * u, end[0], end[1] - 1.5 * u, P(col(p["chain"]), lw * 0.7))
            cv.drawCircle(end[0], end[1], 2.1 * u, P(col(p["color"]))); cv.drawCircle(end[0], end[1], 2.1 * u, P(C["line"], lw))
            cv.drawCircle(end[0], end[1], 1.2 * u, P(col("#e9f4f7"))); cv.drawCircle(end[0] - 0.4 * u, end[1] - 0.4 * u, 0.4 * u, P(col("#ffffff")))
        if r.get("braid"):
            b = r["braid"]; n0 = neck_at(t - 0.25); n1 = neck_at(t - 0.5)
            vx = (nx - n0[0]) / u; vx2 = (n0[0] - n1[0]) / u
            x0, y0 = nx + b["dx"] * u, ny + b["dy"] * u
            pts = [(x0, y0)]; ang = math.radians(b["angle"])
            for k in range(b["n"]):
                lag = (vx if k < b["n"] / 2 else vx2)
                a = ang + math.radians(-lag * 6 + 3.5 * math.sin(t * 1.7 - k * 0.6 + r["seed"]))
                L = b["seg"] * u
                pts.append((pts[-1][0] + math.sin(a) * L, pts[-1][1] + math.cos(a) * L))
                ang = a * 0.92
            for k in range(len(pts) - 1):
                (ax, ay), (bx_, by_) = pts[k], pts[k + 1]
                w = b["w"] * u * (1 - 0.45 * k / b["n"])
                cx, cy = (ax + bx_) / 2, (ay + by_) / 2
                a = math.degrees(math.atan2(by_ - ay, bx_ - ax))
                cv.save(); cv.translate(cx, cy); cv.rotate(a)
                o = skia.Path(); o.addOval(skia.Rect(-b["seg"] * u * 0.68, -w / 2, b["seg"] * u * 0.68, w / 2))
                outlined(cv, o, col(b["color"]), C["line"], lw)
                cv.drawLine(-b["seg"] * u * 0.2, -w * 0.25, b["seg"] * u * 0.25, w * 0.2, P(col(b["shine"]), lw * 0.8))
                cv.restore()
            ex_, ey_ = pts[-1]
            cv.drawCircle(ex_, ey_, b["w"] * u * 0.35, P(col("#c8312c"))); cv.drawCircle(ex_, ey_, b["w"] * u * 0.35, P(C["line"], lw * 0.8))

    def draw_head(self, cv, G, t, ch, mouth):
        r = self.r; u = G["u"]; nx, ny = G["neck"]
        turn = ch("turn", t)                       # "front" / "tq"
        img, hd = self.heads[turn if isinstance(turn, str) else "front"]
        s = r["head_h"] * u / hd["head_h"]
        tilt = ch("tilt", t) + 1.6 * noise1(t, r["seed"] + 11, 0.35) + G.get("talk_nod", 0)
        sq = ch("squash", t)
        # extras behind head (braid root, etc.)
        cv.save(); cv.translate(nx, ny + r.get("neck_drop", 0) * u); cv.rotate(tilt + math.degrees(G["lean"]) * 0.6)
        cv.scale(s * (1 + sq * 0.5), s * (1 - sq))
        px, py = hd["pivot"]
        cv.translate(-px, -py)
        if "behind" in hd: self._behind(cv, hd, t, ch, G)
        cv.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        blink = blink_amount(t, r["seed"])
        self.draw_face(cv, hd, s, t, ch, mouth, blink)
        cv.restore()

    def _behind(self, cv, hd, t, ch, G):
        pass

def blink_amount(t, seed):
    # blinks every 2.2-4.6 s, 0.16 s long; deterministic
    import random
    rng = random.Random(seed * 1000 + 7); bt = rng.uniform(0.3, 2.0); out = 0.0
    while bt < t + 1:
        d = t - bt
        if 0 <= d < 0.16: out = math.sin(d / 0.16 * math.pi)
        bt += rng.uniform(2.2, 4.6)
    return out
