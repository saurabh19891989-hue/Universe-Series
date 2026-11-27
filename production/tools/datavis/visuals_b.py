"""Visuals 6-10 and 12: customs records, regulation scroll, flip board, clocks, clamp console, warrant."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from dvlib import *

PALE = (200, 255, 214)   # customs terminal phosphor (cool green-white)
AMBER = (255, 178, 46)
RED = (255, 84, 64)


# =========================================================================
# 6. CUSTOMS RECORD SCREENS
# =========================================================================
def _hdr(d, left, right=None, col=PALE):
    f = font("plex", 28)
    d.line([(90, 150), (W - 90, 150)], fill=mul(col, 0.5), width=2)
    text(d, (90, 100), left, f, mul(col, 0.7), track=3)
    if right:
        text(d, (W - 90, 100), right, f, mul(col, 0.5), "ra", track=3)


def _licence_draw(t, name="VALE, JAX", cls="MASTER, COURIER CLASS", years="7 YRS AGO"):
    img, d = canvas()
    C = PALE
    _hdr(d, "RIM PORT CUSTOMS  /  MASTER LICENCE REGISTER", "TERMINAL 02")
    text(d, (90, 190), name, font("plexmed", 120), C)
    text(d, (90, 335), cls, font("plex", 62), mul(C, 0.9))
    f = font("plex", 40)
    fields = ["BORN:", "PLACE OF ORIGIN:", "PRIOR LICENCES:", "NEXT OF KIN:", "PRIOR VESSELS:"]
    y = 425
    for k, lab in enumerate(fields):
        if t >= 1.0 + 0.22 * k:
            text(d, (90, y + k * 56), lab, f, mul(C, 0.75), track=2)   # value column left EMPTY on purpose
            d.line([(560, y + k * 56 + 46), (1300, y + k * 56 + 46)], fill=mul(C, 0.16), width=1)
    yl = y + 5 * 56 + 24
    u = smooth(ramp(t, 2.6, 3.4))
    if u > 0:
        d.line([(90, yl), (90 + (W - 180) * u, yl)], fill=C, width=3)
    if t >= 3.3:
        text(d, (W / 2, yl + 34), "RECORD BEGINS · " + years, font("plex", 34), mul(C, 0.95), "mm", track=6)
    rows = [("7 YRS AGO", "LICENCE ISSUED", "MASTER, COURIER CLASS"),
            ("7 YRS AGO", "VESSEL REGISTERED", "THE UNSCHEDULED"),
            ("6 YRS AGO", "ANNUAL RENEWAL", "NO ENDORSEMENTS")]
    for k, (a, b, c) in enumerate(rows):
        if t >= 3.9 + 0.25 * k:
            yy = yl + 76 + k * 50
            text(d, (90, yy), a, f, mul(C, 0.7))
            text(d, (420, yy), b, f, mul(C, 0.85))
            text(d, (960, yy), c, f, mul(C, 0.85))
    return img


def customs_licence(name="VALE, JAX", cls="MASTER, COURIER CLASS"):
    return [ClipSpec("06a_customs_licence", 13.0, lambda t, i, alpha=False: _licence_draw(t, name, cls), "white",
                     stills=[8.5], cues={"upper_fields_shown_empty_from": 2.2, "record_begins_line": 3.3, "fully_shown": 5.0})]


def _deletion_draw(t, address="THE SILVER HATCHET",
                   status="WITHDRAWN AT THE REQUEST OF THE OWNER", owner="—"):
    img, d = canvas()
    C = PALE
    _hdr(d, "ATLAS OFFICE  /  ADDRESS REGISTER  /  DELETION RECORD", "FILED 14:02")
    f = font("plexmed", 66)
    lines = [("ADDRESS:", address, 1.0), ("STATUS:", status, 2.0), ("OWNER:", owner, 3.4)]
    # labels left, values after; STATUS line is long -> label above value
    y = 260
    text(d, (90, y), "ADDRESS: " + typed(address, t, 1.0, 26), f, C)
    s2 = "STATUS: " + typed(status, t, 2.0, 30)
    text(d, (90, y + 170), s2, f, C)
    s3 = "OWNER: " + (owner if t >= 4.6 else "")
    text(d, (90, y + 340), s3, f, C)
    if t >= 4.6 and int(t * 2) % 2 == 0:
        x = 90 + tlen(f, "OWNER: " + owner) + 24
        d.rectangle([x, y + 344, x + 34, y + 410], fill=C)
    d.rectangle([80, y - 20, W - 80, y + 470], outline=mul(C, 0.25), width=2)
    return img


def customs_deletion():
    return [ClipSpec("06b_customs_deletion_record", 13.0, lambda t, i, alpha=False: _deletion_draw(t), "white",
                     stills=[9.0], cues={"status_line_typing": 2.0, "owner_empty_dash": 4.6, "fully_shown": 6.0})]


def _wrist_draw(t, msg="LOT 14 — PUBLIC SALE"):
    img, d = canvas()
    C = (210, 240, 255)
    d.rounded_rectangle([280, 270, W - 280, H - 270], radius=70, outline=mul(C, 0.4), width=5, fill=(6, 10, 14))
    u = ramp(t, 2.5, 2.62)
    if u <= 0:
        text(d, (W / 2, H / 2), "18:" + "07" if False else "17:12", font("sharetech", 170), mul(C, 0.35), "mm")
        return img
    flash = max(0.0, 1 - (t - 2.5) / 0.5)
    if flash > 0:
        d.rounded_rectangle([280, 270, W - 280, H - 270], radius=70, outline=mul(C, flash), width=int(4 + 12 * flash))
    text(d, (W / 2, 400), "NEW MESSAGE", font("sharetech", 40), mul(C, 0.7), "mm", track=8)
    f = font("plexmed", 92)
    text(d, (W / 2, H / 2 + 10), msg, f, C, "mm")
    # chime ripples
    for k in range(3):
        r = (t - 2.5 - k * 0.22)
        if 0 < r < 1.2:
            a = 1 - r / 1.2
            rr = 80 + r * 220
            d.ellipse([W / 2 - rr - 620, 880 - rr * 0.2, W / 2 + rr + 620, 880 + rr * 0.2], outline=mul(C, 0.35 * a), width=2) if False else None
    return img


def wrist_message():
    return [ClipSpec("06c_wrist_message_lot14", 9.0, lambda t, i, alpha=False: _wrist_draw(t), "white", alpha=False,
                     stills=[5.0], cues={"chime_message_appears": 2.5})]


# =========================================================================
# 7. THE REGULATION (copperplate scroll on a modern screen)
# =========================================================================
REG_TITLE = "Postal Regulation 41(c)"
REG_YEAR = "Anno Domini 1840"
REG_HEAD = "Of Goods Carried and Not Received."
REG_BODY = [
    "41. (c) Be it ordained, that no Parcel, Package, or Article of Freight committed to the care of a Carrier "
    "shall be accounted ABANDONED, nor be sold, forfeited, or otherwise disposed of, until the said Carrier "
    "shall have attempted delivery thereof at the physical address to which it is directed, in the presence "
    "of a customs witness.",
    "And be it further ordained, that Goods so delivered at the said address were never abandoned at all, "
    "and no Sale nor Forfeiture shall thereafter lie against them.",
    "Given under our hand and seal. This Regulation shall stand until repealed by Act; and no such Act "
    "hath been made.",
]
REG_SIGN = "J. Hill, Postmaster General"
REG_HILITE = ["physical address", "customs witness"]
_reg = {}


def _reg_page(title=REG_TITLE, body=REG_BODY, hilite=REG_HILITE):
    key = (title, tuple(body))
    if key in _reg:
        return _reg[key]
    PW = 1180
    ph = 2300
    rs = np.random.RandomState(12)
    # paper with fibres, stains, foxing
    base = np.zeros((ph, PW, 3), np.float32)
    base[...] = (0.90, 0.84, 0.69)
    base += rs.randn(ph, PW, 1).astype(np.float32) * 0.012
    n = cv2.GaussianBlur(rs.randn(ph, PW).astype(np.float32), (0, 0), 40) * 0.8
    base *= (1 + n[..., None] * 0.7)
    for _ in range(26):  # foxing
        x, y, r = rs.randint(0, PW), rs.randint(0, ph), rs.randint(4, 22)
        cv2.circle(base, (x, y), r, (0.78, 0.64, 0.44), -1)
    base = cv2.GaussianBlur(base, (0, 0), 1.6)
    edge = np.clip(np.minimum.outer(np.minimum(np.arange(ph), ph - 1 - np.arange(ph)),
                                    np.minimum(np.arange(PW), PW - 1 - np.arange(PW))) / 40.0, 0, 1)
    base *= (0.55 + 0.45 * edge[..., None])
    page = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(page)
    ink = (42, 26, 18)
    text(d, (PW / 2, 190), title, font("pinyon", 118), ink, "mm")
    text(d, (PW / 2, 330), REG_YEAR, font("fell-i", 52), ink, "mm")
    d.line([(PW / 2 - 260, 395), (PW / 2 + 260, 395)], fill=ink, width=2)
    d.ellipse([PW / 2 - 7, 388, PW / 2 + 7, 402], fill=ink)
    text(d, (PW / 2, 470), REG_HEAD, font("fell-i", 58), ink, "mm")
    f = font("fell", 56)
    y = 590
    boxes = []
    for para in body:
        words = para.split(" ")
        line, x, lh = [], 90, 84
        lines = []
        cur = ""
        for w in words:
            tst = (cur + " " + w).strip()
            if d.textlength(tst, font=f) > PW - 180 and cur:
                lines.append(cur)
                cur = w
            else:
                cur = tst
        lines.append(cur)
        for ln in lines:
            xx = 90
            for w in ln.split(" "):
                d.text((xx, y), w, font=f, fill=ink)
                wl = d.textlength(w + " ", font=f)
                boxes.append((w, xx, y, xx + d.textlength(w, font=f), y + 66))
                xx += wl
            y += lh
        y += 34
    text(d, (PW - 120, y + 30), REG_SIGN, font("pinyon", 66), ink, "ra")
    # highlight boxes for phrases
    hl = []
    words = [b[0].strip(",.;").lower() for b in boxes]
    for ph_ in hilite:
        pw = ph_.lower().split()
        for k in range(len(words) - len(pw) + 1):
            if words[k:k + len(pw)] == pw:
                seg = boxes[k:k + len(pw)]
                # group by line (same y)
                for yy in sorted(set(s[2] for s in seg)):
                    ss = [s for s in seg if s[2] == yy]
                    hl.append((min(s[1] for s in ss), yy + 2, max(s[3] for s in ss), yy + 74))
    _reg[key] = (page, hl, y + 160)
    return _reg[key]


def _reg_draw(t, t_scroll0=2.0, t_scroll1=14.0, t_hl=16.0):
    page, hl, used = _reg_page()
    img, d = canvas()
    # modern viewer chrome
    d.rectangle([0, 0, W, 84], fill=(34, 38, 46))
    text(d, (40, 42), "REGULATIONS ARCHIVE  ·  SCAN 0041-C", font("plex", 30), (200, 210, 225), "lm", track=2)
    text(d, (W - 40, 42), "PAGE 1 / 1", font("plex", 30), (140, 150, 170), "rm", track=2)
    d.rectangle([0, 84, W, H], fill=(16, 18, 24))
    u = smooth(ramp(t, t_scroll0, t_scroll1))
    total = used - (H - 84) + 80
    off = int(u * total) - 40
    px = (W - page.width) // 2
    src_y0 = max(0, off)
    view = page.crop((0, src_y0, page.width, min(page.height, src_y0 + (H - 84))))
    py = 84 + (src_y0 - off)
    img.paste(view, (px, py))
    # highlighter
    ha = smooth(ramp(t, t_hl, t_hl + 0.8))
    if ha > 0:
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for (x0, y0, x1, y1) in hl:
            yy0, yy1 = y0 - off + 84, y1 - off + 84
            od.rectangle([px + x0 - 6, yy0, px + x0 - 6 + (x1 - x0 + 12) * ha, yy1], fill=(255, 215, 40, int(120 * ha)))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        img = img
    # header redrawn over any highlight spill
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 84], fill=(34, 38, 46))
    text(d, (40, 42), "REGULATIONS ARCHIVE  \u00b7  SCAN 0041-C", font("plex", 30), (200, 210, 225), "lm", track=2)
    text(d, (W - 40, 42), "PAGE 1 / 1", font("plex", 30), (140, 150, 170), "rm", track=2)
    # scrollbar
    d.rectangle([W - 22, 100, W - 10, H - 20], fill=(30, 34, 42))
    d.rectangle([W - 22, 100 + u * (H - 260), W - 10, 100 + u * (H - 260) + 140], fill=(120, 130, 150))
    return img


def regulation():
    return [ClipSpec("07_regulation_41c_scroll", 20.0, lambda t, i, alpha=False: _reg_draw(t), "lcd", alpha=False,
                     stills=[4.0, 9.0, 18.5],
                     cues={"scroll_starts": 2.0, "scroll_ends": 14.0, "phrases_highlighted": 16.0},
                     notes="Scroll duration 12 s; re-time in the edit. Highlight marks 'physical address' and 'customs witness'.")]


# =========================================================================
# 8. FLIP-NUMBER BOARD
# =========================================================================
_flip = {}


def _glyph_img(ch, w=170, h=250):
    key = (ch, w, h)
    if key in _flip:
        return _flip[key]
    im = Image.new("RGB", (w, h), (20, 20, 20))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=(26, 26, 24), outline=(8, 8, 8), width=3)
    if ch:
        text(d, (w / 2, h / 2 + 6), ch, font("barlowsb", 230), (236, 232, 218), "mm")
    _flip[key] = im
    return im


def _flip_cell(img, x, y, a, b, u, w=170, h=250):
    """flip from glyph a to b, u in 0..1 (u=0 shows a; u=1 shows b)"""
    ga, gb = _glyph_img(a, w, h), _glyph_img(b, w, h)
    hh = h // 2
    top_new, bot_old = gb.crop((0, 0, w, hh)), ga.crop((0, hh, w, h))
    top_old, bot_new = ga.crop((0, 0, w, hh)), gb.crop((0, hh, w, h))
    if u <= 0 or u >= 1:
        g = ga if u <= 0 else gb
        img.paste(g, (x, y))
        ImageDraw.Draw(img).line([(x, y + hh), (x + w, y + hh)], fill=(0, 0, 0), width=4)
        return
    img.paste(top_new, (x, y))
    img.paste(bot_old, (x, y + hh))
    if u < 0.5:
        k = u / 0.5
        fh = max(2, int(hh * (1 - k)))
        fl = top_old.resize((w, fh)).point(lambda v: int(v * (1 - 0.6 * k)))
        img.paste(fl, (x, y + hh - fh))
    else:
        k = (u - 0.5) / 0.5
        fh = max(2, int(hh * k))
        fl = bot_new.resize((w, fh)).point(lambda v: int(v * (0.5 + 0.5 * k)))
        img.paste(fl, (x, y + hh))
    ImageDraw.Draw(img).line([(x, y + hh), (x + w, y + hh)], fill=(0, 0, 0), width=4)


def _board_cells(t, start=None, flip_dt=0.12):
    """return list of (a, b, u) for 5 cells: thousands, comma, hundreds, tens, units"""
    start_s = ["1", ",", "0", "9", "4"]
    if start is None:
        return [(c, c, 0.0) for c in start_s]
    seqs = [["1", ""], [",", ""], ["0", ""], ["9", "0", ""], ["4", "5", "6", "7", "8", "9", "0"]]
    delays = [0.55, 0.55, 0.4, 0.2, 0.0]
    steps = [0.22, 0.22, 0.22, 0.2, 0.17]
    out = []
    for k, seq in enumerate(seqs):
        if k == 0 or k == 1 or k == 2:
            pass
        tt = (t - start - delays[k]) / steps[k]
        n = len(seq) - 1
        if tt <= 0:
            out.append((seq[0], seq[0], 0.0))
        elif tt >= n:
            out.append((seq[-1], seq[-1], 0.0))
        else:
            j = int(tt)
            out.append((seq[j], seq[j + 1], tt - j))
    # last cell shows "0" at the end (units); others blank
    return out


def _board_draw(t, start=None, headline="RIM PORT CUSTOMS", sub="DAYS WITHOUT INCIDENT"):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    # painted dark panel with worn edges
    d.rectangle([140, 150, W - 140, H - 150], fill=(34, 40, 38), outline=(70, 74, 68), width=8)
    d.rectangle([166, 176, W - 166, H - 176], outline=(80, 84, 76), width=2)
    rs = np.random.RandomState(77)
    for _ in range(90):
        x, y = rs.randint(150, W - 150), rs.randint(160, H - 160)
        L = rs.randint(6, 40)
        c = rs.randint(52, 80)
        d.line([(x, y), (x + L, y + rs.randint(-3, 4))], fill=(c, c + 4, c - 2), width=1)
    for (x, y) in [(190, 200), (W - 190, 200), (190, H - 200), (W - 190, H - 200)]:
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(86, 88, 80), outline=(40, 40, 36))
    text(d, (W / 2, 262), headline, font("barlowsb", 110), (232, 226, 206), "mm", track=14)
    text(d, (W / 2, 392), sub, font("barlow", 74), (208, 190, 120), "mm", track=10)
    cw, ch = 170, 250
    xs = []
    total = 4 * cw + 70 + 4 * 16
    x = (W - total) // 2
    widths = [cw, 70, cw, cw, cw]
    for k, w_ in enumerate(widths):
        xs.append(x)
        x += w_ + 16
    cells = _board_cells(t, start)
    y = 500
    for k, (a, b, u) in enumerate(cells):
        w_ = widths[k]
        if k == 1:
            # comma cell is a narrow flap
            ga = Image.new("RGB", (w_, ch), (26, 26, 24))
            _flip_cell_small(img, xs[k], y, a, b, u, w_, ch)
        else:
            _flip_cell(img, xs[k], y, a, b, u, w_, ch)
    return img


def _flip_cell_small(img, x, y, a, b, u, w, h):
    def g(ch):
        key = ("c", ch, w, h)
        if key not in _flip:
            im = Image.new("RGB", (w, h), (26, 26, 24))
            dd = ImageDraw.Draw(im)
            dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=(26, 26, 24), outline=(8, 8, 8), width=3)
            if ch:
                text(dd, (w / 2, h * 0.80), ch, font("barlowsb", 230), (236, 232, 218), "ms")
            _flip[key] = im
        return _flip[key]
    ga, gb = g(a), g(b)
    hh = h // 2
    if u <= 0 or u >= 1:
        img.paste(ga if u <= 0 else gb, (x, y))
    else:
        img.paste(gb.crop((0, 0, w, hh)), (x, y))
        img.paste(ga.crop((0, hh, w, h)), (x, y + hh))
        if u < 0.5:
            fh = max(2, int(hh * (1 - u / 0.5)))
            img.paste(ga.crop((0, 0, w, hh)).resize((w, fh)), (x, y + hh - fh))
        else:
            fh = max(2, int(hh * (u - 0.5) / 0.5))
            img.paste(gb.crop((0, hh, w, h)).resize((w, fh)), (x, y + hh))
    ImageDraw.Draw(img).line([(x, y + hh), (x + w, y + hh)], fill=(0, 0, 0), width=4)


_boardlook = Look(base=(0.0, 0.0, 0.0), soft=0.7, bloom=0.0, bloom_r=(2, 6), scan=0.0, flicker=0.012, grain=0.018,
                  curve=0.0, vignette=0.55, dust=1.0, glare=0.03, hum=0.0, seed=31)


def flip_board(number="1,094"):
    t0 = 3.0
    done = t0 + 0.55 + 0.22 + 0.17 * 6 + 1.0

    def static(t, i, alpha=False):
        return _board_draw(t)

    def anim(t, i, alpha=False):
        return _board_draw(t, start=t0)
    return [ClipSpec("08a_board_1094_static", 10.0, static, lookobj=_boardlook, alpha=False, stills=[3.0]),
            ClipSpec("08b_board_flip_to_zero", t0 + 8.5, anim, lookobj=_boardlook, alpha=False, stills=[1.5, t0 + 1.2, t0 + 7.0],
                     cues={"flip_starts": t0, "digits_settled_on_0": round(t0 + 0.2 + 0.17 * 6, 2)},
                     notes="Flaps fall through digits; units cell runs 4-5-6-7-8-9-0, others flip to blank.")]


# =========================================================================
# 9. CLOCKS
# =========================================================================
SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg7(d, x, y, w, h, ch, col, off):
    th = int(w * 0.17)
    g = int(th * 0.35)
    pts = {
        "a": [(x + g + th * 0.5, y), (x + w - g - th * 0.5, y), (x + w - g - th, y + th), (x + g + th, y + th)],
        "d": [(x + g + th, y + h - th), (x + w - g - th, y + h - th), (x + w - g - th * 0.5, y + h), (x + g + th * 0.5, y + h)],
        "g": [(x + g + th * 0.5, y + h / 2), (x + g + th, y + h / 2 - th / 2), (x + w - g - th, y + h / 2 - th / 2),
              (x + w - g - th * 0.5, y + h / 2), (x + w - g - th, y + h / 2 + th / 2), (x + g + th, y + h / 2 + th / 2)],
        "f": [(x, y + g + th * 0.5), (x + th, y + g + th), (x + th, y + h / 2 - g - th * 0.5), (x, y + h / 2 - g)],
        "b": [(x + w, y + g + th * 0.5), (x + w - th, y + g + th), (x + w - th, y + h / 2 - g - th * 0.5), (x + w, y + h / 2 - g)],
        "e": [(x, y + h / 2 + g), (x + th, y + h / 2 + g + th * 0.5), (x + th, y + h - g - th), (x, y + h - g - th * 0.5)],
        "c": [(x + w, y + h / 2 + g), (x + w - th, y + h / 2 + g + th * 0.5), (x + w - th, y + h - g - th), (x + w, y + h - g - th * 0.5)],
    }
    for s, p in pts.items():
        d.polygon(p, fill=col if (ch in SEG and s in SEG[ch]) else off)


def _bridge_clock(t, start_s=17 * 3600 + 59 * 60 + 56, col=AMBER, show_s=True):
    img, d = canvas()
    sec = start_s + int(t)
    hh, mm, ss = sec // 3600 % 24, sec // 60 % 60, sec % 60
    digs = "%02d%02d%02d" % (hh, mm, ss)
    dw, dh, gap = 190, 330, 36
    total = 6 * dw + 4 * gap + 2 * 70
    x = (W - total) // 2
    y = 360
    off = mul(col, 0.07)
    for k, ch in enumerate(digs):
        seg7(d, x, y, dw, dh, ch, col, off)
        x += dw + gap
        if k in (1, 3):
            for yy in (y + dh * 0.32, y + dh * 0.68):
                d.rectangle([x + 4, yy - 12, x + 28, yy + 12], fill=col if (int(t * 2) % 2 == 0 or True) else off)
            x += 70
    # settled flash at 18:00:00
    if sec >= 18 * 3600 and (t - (18 * 3600 - start_s)) < 0.4:
        pass
    text(d, (W / 2, 250), "BRIDGE  ·  SHIP TIME", font("sharetech", 36), mul(col, 0.6), "mm", track=10)
    return img


def _hall_analog(t, h=17, m=44, s=55):
    img, d = canvas()
    C = (236, 232, 214)
    cx, cy, R = W // 2, H // 2, 440
    d.ellipse([cx - R - 22, cy - R - 22, cx + R + 22, cy + R + 22], fill=(20, 20, 18), outline=(120, 116, 100), width=12)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(214, 208, 186), outline=(60, 56, 48), width=5)
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = R - (50 if k % 5 == 0 else 22)
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (R - 10), cy + math.sin(a) * (R - 10))],
               fill=(30, 28, 24), width=8 if k % 5 == 0 else 3)
    for k in range(1, 13):
        a = math.radians(k * 30 - 90)
        text(d, (cx + math.cos(a) * (R - 100), cy + math.sin(a) * (R - 100)), str(k), font("barlowsb", 78), (30, 28, 24), "mm")
    # 24 h inner ring
    for k in range(13, 25):
        a = math.radians((k - 12) * 30 - 90)
        text(d, (cx + math.cos(a) * (R - 175), cy + math.sin(a) * (R - 175)), str(k % 24 if k < 24 else 24), font("barlow", 38), (120, 60, 40), "mm")
    text(d, (cx, cy - 200), "RIM PORT", font("barlow", 40), (60, 56, 48), "mm", track=8)
    # time: seconds tick with a tiny overshoot
    tot = h * 3600 + m * 60 + s + t
    sec_i = math.floor(tot)
    frac = tot - sec_i
    tick = 1.0 - math.exp(-frac * 40) * (1 + 0.0) if frac < 0.3 else 1.0
    over = 0.35 * math.sin(frac * 60) * math.exp(-frac * 18)
    s_ang = ((sec_i % 60) + clamp(tick) + over) * 6 - 90
    mm_ = (tot / 60.0) % 60
    hh_ = (tot / 3600.0) % 12
    for ang, L, w, col in [(hh_ * 30 - 90, R * 0.5, 22, (24, 22, 20)), (mm_ * 6 - 90, R * 0.78, 14, (24, 22, 20))]:
        a = math.radians(ang)
        d.line([(cx - math.cos(a) * 40, cy - math.sin(a) * 40), (cx + math.cos(a) * L, cy + math.sin(a) * L)], fill=col, width=w)
    a = math.radians(s_ang)
    d.line([(cx - math.cos(a) * 80, cy - math.sin(a) * 80), (cx + math.cos(a) * R * 0.88, cy + math.sin(a) * R * 0.88)], fill=(190, 50, 40), width=6)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(190, 50, 40))
    return img


def clocks():
    t_start = 17 * 3600 + 59 * 60 + 56
    cl = [
        ClipSpec("09a_hall_clock_analog_1745", 14.0,
                 lambda t, i, alpha=False: _hall_analog(t, 17, 44, 54), lookobj=Look(base=(0.01, 0.01, 0.008), soft=0.8, bloom=0.2, scan=0.0, flicker=0.015, curve=0.0, vignette=0.55, hum=0.0, grain=0.015, seed=41),
                 alpha=False, stills=[3.0], cues={"reads_17_45_00": 6.0}),
        ClipSpec("09b_hall_clock_digital_1745", 10.0,
                 lambda t, i, alpha=False: _bridge_clock(0, start_s=17 * 3600 + 45 * 60 + 0) if False else _digital_hm(t), "amber",
                 stills=[3.0], cues={"reads": "17:45"}),
        ClipSpec("09c_bridge_clock_175958_to_180000", 10.0,
                 lambda t, i, alpha=False: _bridge_clock(t, start_s=t_start), "amber", alpha=False,
                 stills=[2.2, 4.2, 8.0],
                 cues={"17:59:56": 0.0, "17:59:58": 2.0, "17:59:59": 3.0, "18:00:00": 4.0},
                 notes="One tick per second (hard cut of digits, like a cheap segment display)."),
    ]
    return cl


def _digital_hm(t):
    img, d = canvas()
    col = (255, 90, 70)
    dw, dh, gap = 230, 400, 44
    total = 4 * dw + 3 * gap + 90
    x = (W - total) // 2
    y = 340
    for k, ch in enumerate("1745"):
        seg7(d, x, y, dw, dh, ch, col, mul(col, 0.06))
        x += dw + gap
        if k == 1:
            for yy in (y + dh * 0.32, y + dh * 0.68):
                d.rectangle([x + 4, yy - 16, x + 36, yy + 16], fill=col if int(t) % 2 == 0 else mul(col, 0.2))
            x += 90
    text(d, (W / 2, 250), "RIM PORT  ·  HALL", font("sharetech", 36), mul(col, 0.6), "mm", track=10)
    return img


# =========================================================================
# 10. CLAMP CONSOLE
# =========================================================================
def _lamp(d, x, y, r, col, on):
    d.ellipse([x - r, y - r, x + r, y + r], fill=mul(col, 1.0 if on else 0.12), outline=mul(col, 0.5), width=3)


def _jaws(d, cx, cy, openness, col):
    """two clamp jaws; openness 0 closed .. 1 open"""
    gap = 18 + 105 * openness
    for s in (-1, 1):
        d.rectangle([cx - 190, cy + s * gap - (36 if s < 0 else 0), cx + 190, cy + s * gap + (0 if s < 0 else 36)],
                    outline=col, width=5, fill=mul(col, 0.12))
    d.rectangle([cx - 90, cy - 14, cx + 90, cy + 14], outline=mul(col, 0.35), width=2)


def _clamp_draw(t, mode, t_key2=None, t_open=None, t_pop=None, t_key2_out=None):
    """mode: 'closed' | 'open' | 'seq'."""
    img, d = canvas()
    C = (190, 235, 255)
    # state machine
    state = "CLOSED"
    openness = 0.0
    key2_in = False
    if mode == "open":
        state, openness = "OPEN", 1.0
    if mode == "seq" or mode == "popup":
        if mode == "popup":
            state, openness = "OPEN", 1.0
        else:
            if t_key2 is not None and t >= t_key2:
                key2_in = True
            if t_open is not None and t >= t_open:
                openness = smooth(ramp(t, t_open, t_open + 1.0))
                state = "OPEN" if t >= t_open + 0.5 else "CLOSED"
            if t_key2_out is not None and t >= t_key2_out:
                key2_in = False
    d.rectangle([60, 60, W - 60, H - 60], outline=mul(C, 0.45), width=3)
    text(d, (110, 100), "RIM PORT  ·  BAY CLAMP CONTROL", font("sharetech", 30), mul(C, 0.65), track=4)
    text(d, (W - 110, 100), "MAIN HALL · CONSOLE 1", font("sharetech", 30), mul(C, 0.45), "ra", track=4)
    d.line([(100, 150), (W - 100, 150)], fill=mul(C, 0.35), width=2)
    col = (255, 190, 70) if state == "CLOSED" else (110, 255, 170)
    f = font("plexmed", 100)
    text(d, (110, 250), "BAY 9 CLAMP — " + state, f, col)
    _jaws(d, 1610, 330, openness, mul(col, 0.9))
    f2 = font("plexmed", 64)
    d.line([(100, 470), (1200, 470)], fill=mul(C, 0.3), width=2)
    text(d, (110, 520), "KEY 1 — SUPERINTENDENT", f2, C)
    _lamp(d, 1390, 553, 22, (110, 255, 170), True)
    text(d, (1440, 553), "IN", font("sharetech", 40), (110, 255, 170), "lm", track=3)
    text(d, (110, 680), "KEY 2 — DUTY OFFICER", f2, C)
    if key2_in:
        _lamp(d, 1390, 713, 22, (110, 255, 170), True)
        text(d, (1440, 713), "IN" if state == "CLOSED" and openness < 0.05 else "TURNED", font("sharetech", 40), (110, 255, 170), "lm", track=3)
    else:
        _lamp(d, 1390, 713, 22, (110, 255, 170), False)
        text(d, (1440, 713), "EMPTY", font("sharetech", 40), mul(C, 0.35), "lm", track=3)
    d.line([(100, 810), (W - 100, 810)], fill=mul(C, 0.3), width=2)
    text(d, (110, 850), "LOCK: AWAITING AUTHORITY", font("sharetech", 36), mul(C, 0.5) if state == "CLOSED" else mul(C, 0.35), track=4) if (mode != "popup" and (t_pop is None or t < t_pop)) else None
    # popup
    if t_pop is not None and t >= t_pop:
        u = ramp(t, t_pop, t_pop + 0.18)
        ov = Image.new("RGBA", img.size, (0, 0, 0, int(150 * u)))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
        bw, bh = 1260 * (0.85 + 0.15 * u), 400 * (0.85 + 0.15 * u)
        x0, y0 = W / 2 - bw / 2, H / 2 - bh / 2
        d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(12, 20, 26), outline=(255, 190, 70), width=6)
        d.rectangle([x0, y0, x0 + bw, y0 + 62], fill=(255, 190, 70))
        text(d, (x0 + 24, y0 + 31), "NOTICE  ·  ATLAS OFFICE", font("sharetech", 32), (20, 14, 4), "lm", track=3)
        if u > 0.5:
            text(d, (W / 2, H / 2 + 14), "AUTHORITY TO LOCK — RECEIVED", font("plexmed", 68), (255, 236, 200), "mm")
            d.rectangle([W / 2 - 80, y0 + bh - 96, W / 2 + 80, y0 + bh - 34], outline=(255, 190, 70), width=4)
            text(d, (W / 2, y0 + bh - 65), "OK", font("sharetech", 38), (255, 190, 70), "mm", track=4)
        fl = max(0, 1 - (t - t_pop) / 0.5)
        if fl > 0:
            d.rectangle([x0 - 10, y0 - 10, x0 + bw + 10, y0 + bh + 10], outline=mul((255, 220, 140), fl), width=8)
    return img


def clamp_console():
    cl = []
    cl.append(ClipSpec("10a_clamp_closed", 10.0, lambda t, i, alpha=False: _clamp_draw(t, "closed"), "white",
                       stills=[4.0], alpha=False, cues={"note": "KEY 1 in, KEY 2 empty; loopable hold"}))
    cl.append(ClipSpec("10b_clamp_open", 10.0, lambda t, i, alpha=False: _clamp_draw(t, "open"), "white", stills=[4.0], alpha=False))
    cl.append(ClipSpec("10c_clamp_popup_authority_received", 12.0,
                       lambda t, i, alpha=False: _clamp_draw(t, "popup", t_pop=4.5), "white", alpha=False, stills=[2.0, 8.0],
                       cues={"popup_arrives": 4.5}))
    cl.append(ClipSpec("10d_clamp_sequence", 18.0,
                       lambda t, i, alpha=False: _clamp_draw(t, "seq", t_key2=3.5, t_open=5.0, t_key2_out=7.5, t_pop=9.6),
                       "white", stills=[2.0, 4.5, 8.5, 13.0],
                       cues={"key2_inserted": 3.5, "key_turned_clamp_opens": 5.0, "key2_drawn_out": 7.5,
                             "authority_popup_1.3s_after_open_label": 9.6}))
    return cl


# =========================================================================
# 12. WARRANT SCREEN (final image of the episode)
# =========================================================================
WARRANT_LINES = ["ORTEGA, LUCÍA. ENGINEER",
                 "SEN, MIRA. CARTOGRAPHER. STRUCK OFF (x2)",
                 "PIP. UNIT. DECOMMISSIONED",
                 "MUNCHAUSEN, H. K. F. DELISTED"]
W_FIELD_NOBODY = "CAPTAIN: nobody"
W_FIELD_VALE = "CAPTAIN: VALE, JAX"
WC = (200, 255, 200)


def _warrant_draw(t, tl=None):
    """tl: timeline dict"""
    tl = tl or WTL
    img, d = canvas()
    C = WC
    f = font("sharetech", 68)
    # fit longest line
    maxw = 1700
    while tlen(f, max(WARRANT_LINES, key=len)) > maxw:
        f = font("sharetech", f.size - 2)
    d.rectangle([60, 60, W - 60, H - 60], outline=mul(C, 0.4), width=3)
    text(d, (110, 100), "ATLAS OFFICE  ·  RIM PORT  ·  NOTICE OF WARRANT", font("sharetech", 30), mul(C, 0.65), track=4)
    text(d, (W - 110, 100), "PUBLISHED", font("sharetech", 30), mul(C, 0.5), "ra", track=4)
    d.line([(100, 150), (W - 100, 150)], fill=mul(C, 0.35), width=2)
    y = 250
    for k, ln in enumerate(WARRANT_LINES):
        t0 = tl["type_start"] + 0.45 * k
        s = typed(ln, t, t0, 60)
        text(d, (110, y + k * 112), s, f, C)
    yc = y + 4 * 112 + 60
    field = W_FIELD_NOBODY
    jitter = 0
    show_black = False
    if t < tl["field_in"]:
        field = ""
    elif tl["flicker0"] <= t < tl["flicker1"]:
        u = (t - tl["flicker0"])
        # unstable: a few frames of VALE, JAX interleaved with nobody, vertical tear
        fr = int(u * 24)
        field = W_FIELD_VALE if fr % 5 not in (1, 3) else W_FIELD_NOBODY
        if fr % 4 == 2:
            jitter = 6
    elif tl["flicker1"] <= t < tl["refresh1"]:
        field = W_FIELD_VALE if t < tl["flicker1"] + 0.2 else ""
    if field:
        text(d, (110 + jitter, yc), field, f, (235, 255, 235) if field == W_FIELD_NOBODY else (255, 240, 200))
    # underline cursor bar on the field before the correction
    if tl["field_in"] <= t < tl["flicker0"] and int(t * 2) % 2 == 0 and False:
        pass
    # refresh sweep
    r0, r1 = tl["refresh0"], tl["refresh1"]
    if r0 <= t < r1:
        u = (t - r0) / (r1 - r0)
        ys = int(150 + u * (H - 220))
        img2 = Image.new("RGB", (W, H), (0, 0, 0))
        # content below the sweep line is still "old/black", above is repainted; plus a bright band
        band = Image.new("RGB", (W - 160, 14), mul(C, 0.9))
        d.rectangle([80, ys, W - 80, ys + 14], fill=mul(C, 0.9))
        d.rectangle([80, ys + 14, W - 80, ys + 90], fill=mul(C, 0.18))
        if u > 0.05:
            # blank the lines below the sweep to emulate redraw
            d.rectangle([90, ys + 91, W - 90, H - 80], fill=(0, 0, 0))
            # field is redrawn only after sweep passes it
    return img


WTL = dict(type_start=0.6, field_in=3.1, flicker0=6.2, flicker1=6.8, refresh0=7.0, refresh1=7.7)


def _warrant_draw_wrap(t, i, alpha=False):
    img = _warrant_draw(t)
    # after the refresh the field must come back: redraw below the sweep
    if WTL["refresh0"] <= t < WTL["refresh1"]:
        u = (t - WTL["refresh0"]) / (WTL["refresh1"] - WTL["refresh0"])
        ys = int(150 + u * (H - 220))
        full = _warrant_draw(WTL["refresh1"] + 1.0)
        # reveal settled content above the sweep line (repaint), old below is blank
        a = np.asarray(img).copy()
        b = np.asarray(full)
        a[:max(0, ys - 4)] = b[:max(0, ys - 4)]
        # keep sweep band from img: composite brighter of band
        a = np.maximum(a, np.asarray(img))
        return Image.fromarray(a)
    return img


_warrant_hold_look = Look(base=(0.005, 0.02, 0.008), soft=0.85, bloom=1.0, scan=0.25, flicker=0.004, grain=0.006,
                          curve=0.035, hum=0.0, roll=False, seed=7, chroma=0.0)


def warrant(final_hold=6.0):
    dur = WTL["refresh1"] + final_hold
    cl = [ClipSpec("12a_warrant_screen", dur, _warrant_draw_wrap, "green", stills=[2.0, 6.5, dur - 2.0],
                   cues={"list_typed_by": 3.0, "CAPTAIN_nobody_appears": WTL["field_in"],
                         "flicker_to_VALE_JAX": WTL["flicker0"], "refresh_sweep": WTL["refresh0"],
                         "settled_nobody_from": WTL["refresh1"], "clean_hold_s": final_hold},
                   notes="Final image of the episode. Last %.0f s is a clean hold on CAPTAIN: nobody." % final_hold),
          ClipSpec("12b_warrant_final_hold", 10.0, lambda t, i, alpha=False: _warrant_draw(WTL["refresh1"] + 3.0),
                   lookobj=_warrant_hold_look, stills=[5.0], alpha=False,
                   notes="10 s of the settled last frame with minimal flicker/grain (no scan roll) for the freeze at the end.")]
    return cl
