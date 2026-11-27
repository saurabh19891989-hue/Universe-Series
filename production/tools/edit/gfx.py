#!/usr/bin/env python3
"""Built-in graphics for the edit engine: placeholder screen content (used only when the data-visual
clip a shot names is not on disk yet; the render log marks every use) and title text.

Every generator is a pure function of time, so frames are deterministic and cache-safe.
Names: bank_call, readouts, report, job, cargo, text.
"""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
MONO_R = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
SANS_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
SANS_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
AMBER = (255, 176, 70)
GREEN = (120, 235, 190)


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def to_f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255


def typed(text, t, t0, cps):
    n = int(max(0.0, t - t0) * cps)
    return text[:n]


class Gfx:
    def __init__(self, spec, resolve):
        self.s = spec; self.resolve = resolve; self._img = {}

    def img(self, key):
        if key not in self._img:
            self._img[key] = Image.open(self.resolve(key)).convert("RGB")
        return self._img[key]

    def render(self, t, w, h):
        return getattr(self, "g_" + self.s.get("name", "blank"))(t, w, h)

    def g_blank(self, t, w, h):
        return np.zeros((h, w, 3), np.float32)

    # ------------------------------------------------------------ bank call window
    def g_bank_call(self, t, w, h):
        s = self.s
        im = Image.new("RGB", (w, h), (10, 22, 30))
        d = ImageDraw.Draw(im)
        # header bar with the smiling logo (generic, invented)
        d.rectangle([0, 0, w, int(h * 0.13)], fill=(18, 48, 58))
        cx, cy, r = int(w * 0.06), int(h * 0.065), int(h * 0.045)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 214, 120), width=max(2, r // 6))
        d.arc([cx - r * 0.6, cy - r * 0.5, cx + r * 0.6, cy + r * 0.55], 20, 160, fill=(255, 214, 120), width=max(2, r // 6))
        d.text((cx + r * 1.6, cy - h * 0.03), "RECOVERIES", font=font(SANS_B, int(h * 0.05)), fill=(235, 242, 238))
        d.text((w * 0.62, cy - h * 0.022), "CALL CONNECTED · LAGOS", font=font(MONO_R, int(h * 0.03)), fill=(150, 200, 190))
        # call window with the agent's still
        logo_until = s.get("logo_until", 0.0)
        x0, y0, x1, y1 = int(w * 0.04), int(h * 0.17), int(w * 0.68), int(h * 0.95)
        d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=(60, 110, 120), width=3)
        if t >= logo_until:
            src = self.img(s["temi"])
            cw, ch = x1 - x0, y1 - y0
            crop = s.get("crop", [0.18, 0.0, 0.82, 0.92])
            sw, sh = src.size
            c = src.crop((int(crop[0] * sw), int(crop[1] * sh), int(crop[2] * sw), int(crop[3] * sh)))
            # slow push inside the call window (the still breathes a little)
            frozen = any(a <= t < b for a, b in s.get("freeze", []))
            tt = s.get("freeze_t", t) if frozen else t
            z = 1.0 + 0.04 * min(1.0, tt / 10.0)
            c = c.resize((int(cw * z), int(ch * z)), Image.LANCZOS)
            ox, oy = (c.width - cw) // 2, (c.height - ch) // 3
            c = c.crop((ox, oy, ox + cw, oy + ch))
            if frozen:
                # compression stall: macro-blocks + a buffering ring
                c = c.resize((cw // 14, ch // 14), Image.BILINEAR).resize((cw, ch), Image.NEAREST)
            im.paste(c, (x0, y0))
            if frozen:
                ring = (t * 2.0) % 1.0
                rr = int(h * 0.05); mx, my = (x0 + x1) // 2, (y0 + y1) // 2
                d.arc([mx - rr, my - rr, mx + rr, my + rr], ring * 360, ring * 360 + 260, fill=(240, 240, 240), width=6)
            d.rectangle([x0, y1 - int(h * 0.07), x1, y1], fill=(8, 18, 24))
            d.text((x0 + 14, y1 - int(h * 0.062)), "TEMI A. — RECOVERIES", font=font(MONO, int(h * 0.032)), fill=(235, 240, 235))
            lag = "SIGNAL DELAY 1.3 s" if not frozen else "RECONNECTING…"
            d.text((x1 - int(w * 0.26), y1 - int(h * 0.062)), lag, font=font(MONO_R, int(h * 0.03)), fill=(255, 190, 90))
        else:
            mx, my, rr = (x0 + x1) // 2, (y0 + y1) // 2, int(h * 0.16)
            pulse = 0.85 + 0.15 * math.sin(t * 6)
            col = tuple(int(c * pulse) for c in (255, 214, 120))
            d.ellipse([mx - rr, my - rr, mx + rr, my + rr], outline=col, width=10)
            d.arc([mx - rr * 0.6, my - rr * 0.45, mx + rr * 0.6, my + rr * 0.6], 20, 160, fill=col, width=10)
            d.ellipse([mx - rr * 0.35 - 10, my - rr * 0.35 - 10, mx - rr * 0.35 + 10, my - rr * 0.35 + 10], fill=col)
            d.ellipse([mx + rr * 0.35 - 10, my - rr * 0.35 - 10, mx + rr * 0.35 + 10, my - rr * 0.35 + 10], fill=col)
        # side panel: account status
        px = int(w * 0.71)
        f = font(MONO, int(h * 0.034)); f2 = font(MONO_R, int(h * 0.028))
        rows = s.get("panel", ["ACCOUNT", "THE UNSCHEDULED", "", "STATUS", "IN RECOVERY", "", "FULL RECOVERY", "18:00 LUNAR"])
        y = int(h * 0.19)
        for i, row in enumerate(rows):
            hot = row in ("IN RECOVERY", "18:00 LUNAR")
            col = (255, 120, 90) if hot and int(t * 2) % 2 == 0 else ((255, 190, 90) if hot else (170, 210, 200))
            d.text((px, y), row, font=f if i % 3 != 0 else f2, fill=col)
            y += int(h * 0.075 if row else h * 0.03)
        return to_f(im)

    # ------------------------------------------------------------ engine readouts dying
    def g_readouts(self, t, w, h):
        s = self.s
        im = Image.new("RGB", (w, h), (8, 12, 10))
        d = ImageDraw.Draw(im)
        labels = s.get("labels", ["ENG L", "ENG R", "NAV", "HEAT", "AIR", "COFFEE"])
        drops = s.get("drop_at", [0.4] + [99] * (len(labels) - 1))
        n = len(labels)
        bw = w * 0.8 / n
        f = font(MONO, int(h * 0.05))
        rng = np.random.default_rng(3)
        lv = rng.uniform(0.55, 0.9, n)
        for i, lab in enumerate(labels):
            x = w * 0.1 + i * bw
            v = lv[i] * (1 + 0.03 * math.sin(t * 7 + i))
            if t >= drops[i]:
                u = min(1.0, (t - drops[i]) / 0.5)
                v = v * (1 - u) ** 2
            dead = t >= drops[i] + 0.5
            col = (70, 40, 30) if dead else AMBER
            top, bot = h * 0.15, h * 0.78
            d.rectangle([x + bw * 0.2, top, x + bw * 0.8, bot], outline=(60, 70, 60), width=3)
            d.rectangle([x + bw * 0.25, bot - (bot - top) * v, x + bw * 0.75, bot - 4], fill=col)
            d.text((x + bw * 0.12, h * 0.83), lab, font=f, fill=(200, 80, 60) if dead else (200, 220, 200))
        return to_f(im)

    # ------------------------------------------------------------ PIP's report / job card (typed)
    def _typed_card(self, t, w, h, lines, col, title_col=None):
        s = self.s
        im = Image.new("RGB", (w, h), (12, 9, 5))
        d = ImageDraw.Draw(im)
        y = h * 0.14
        t0 = s.get("type_start", 0.2); cps = s.get("cps", 34)
        used = 0.0
        for i, (txt, size) in enumerate(lines):
            f = font(MONO, int(h * size))
            shown = typed(txt, t, t0 + used, cps)
            used += len(txt) / cps + 0.15
            d.text((w * 0.08, y), shown, font=f, fill=title_col if (i == 0 and title_col) else col)
            y += h * size * 1.55
        # cursor
        if int(t * 2.5) % 2 == 0:
            d.rectangle([w * 0.08, y, w * 0.08 + h * 0.03, y + h * 0.05], fill=col)
        st = s.get("stamp_at")
        if st is not None and t >= st:
            k = min(1.0, (t - st) / 0.12)
            sz = int(h * (0.22 - 0.05 * k))
            f = font(SANS_B, sz)
            txt = s.get("stamp", "FILED")
            lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            tw = dl.textlength(txt, font=f)
            dl.rectangle([w * 0.62 - 20, h * 0.62 - 10, w * 0.62 + tw + 20, h * 0.62 + sz * 1.15], outline=(220, 70, 50, 230), width=8)
            dl.text((w * 0.62, h * 0.62), txt, font=f, fill=(220, 70, 50, 230))
            lay = lay.rotate(-8, center=(w * 0.75, h * 0.7))
            im.paste(lay, (0, 0), lay)
        return to_f(im)

    def g_report(self, t, w, h):
        s = self.s
        lines = s.get("lines", [["REPORT #1,204", 0.11], ["RE: CAPTAIN", 0.065], ['"TAKE IT" (x5)', 0.065], ["ONCE IS BINDING.", 0.05]])
        return self._typed_card(t, w, h, [tuple(x) for x in lines], AMBER, (255, 214, 140))

    def g_job(self, t, w, h):
        s = self.s
        lines = s.get("lines", [["JOB · DIRECT POST", 0.075], ["1 PARCEL · SEALED · PREPAID", 0.055],
                                 ["TO: SHACKLETON CRATER", 0.055], ["BY: 18:00 LUNAR", 0.055], ["FEE: 41,882.17", 0.075]])
        return self._typed_card(t, w, h, [tuple(x) for x in lines], AMBER, (255, 214, 140))

    # ------------------------------------------------------------ cargo camera feed
    def g_cargo(self, t, w, h):
        s = self.s
        src = self.img(s["src"])
        sw, sh = src.size
        cr = s.get("crop", [0.6, 0.38, 0.82, 0.58])
        u = min(1.0, t / max(1e-3, s.get("dur", 4.0)))
        z = 1 + 0.12 * u * u * (3 - 2 * u)
        cx, cy = (cr[0] + cr[2]) / 2 * sw, (cr[1] + cr[3]) / 2 * sh
        hw, hh = (cr[2] - cr[0]) * sw / 2 / z, (cr[3] - cr[1]) * sh / 2 / z
        c = src.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh)))
        # security-camera look: low res, mono-green tint
        c = c.resize((w // 3, h // 3), Image.BILINEAR).resize((w, h), Image.BILINEAR)
        a = np.asarray(c, np.float32) / 255
        g = a @ np.float32([0.3, 0.6, 0.1])
        a = (g[..., None] * np.float32([0.75, 1.0, 0.85]) * 0.85 + a * 0.25)
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        f = font(MONO, int(h * 0.045))
        d.text((w * 0.04, h * 0.04), s.get("label", "CARGO CAM 2 · BAY 1"), font=f, fill=GREEN)
        if int(t * 1.5) % 2 == 0:
            d.ellipse([w * 0.9, h * 0.05, w * 0.9 + h * 0.035, h * 0.05 + h * 0.035], fill=(255, 70, 60))
        m = int(w * 0.03)
        for (x, y, dx, dy) in ((m, m * 2.2, 1, 1), (w - m, m * 2.2, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
            d.line([x, y, x + dx * m * 1.5, y], fill=GREEN, width=3); d.line([x, y, x, y + dy * m * 1.5], fill=GREEN, width=3)
        return to_f(im)

    # ------------------------------------------------------------ titles
    def render_rgba(self, t, w, h):
        s = self.s
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f = font(self.resolve(s.get("font", SANS_B)), int(s.get("size", 118)))
        txt = s.get("text", "")
        t0 = s.get("t0", 0.0); fi = s.get("fade_in", 0.6); fo = s.get("fade_out", 0.6)
        t1 = s.get("t1", 1e9)
        a = min(1, max(0, (t - t0) / max(fi, 1e-3))) * min(1, max(0, (t1 - t) / max(fo, 1e-3)))
        if a <= 0:
            return np.zeros((h, w, 4), np.float32)
        u = min(1.0, max(0.0, (t - t0) / max(1e-3, s.get("track_s", 8.0))))
        u = 1 - (1 - u) ** 3
        track = s.get("track_from", 14) + (s.get("track_to", 30) - s.get("track_from", 14)) * u
        widths = [d.textlength(c, font=f) for c in txt]
        tot = sum(widths) + track * (len(txt) - 1)
        x = w / 2 - tot / 2; y = h * s.get("y", 0.45)
        col = tuple(s.get("color", [242, 231, 207]))
        for c, cw in zip(txt, widths):
            d.text((x, y), c, font=f, fill=col + (int(255 * a),)); x += cw + track
        if s.get("sub"):
            f2 = font(SANS_M, int(s.get("sub_size", 28)))
            sub = s["sub"]
            d.text((w / 2 - d.textlength(sub, font=f2) / 2, y + s.get("size", 118) * 1.35), sub, font=f2,
                   fill=tuple(s.get("sub_color", [208, 96, 31])) + (int(220 * a),))
        return np.asarray(im, np.float32) / 255
