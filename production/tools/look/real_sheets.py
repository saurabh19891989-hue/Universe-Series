#!/usr/bin/env python3
"""Photoreal round: 'filmify' raw generations (de-gloss + shared grade + grain) and build sheets.
Usage: real_sheets.py SCRATCH_REAL_DIR OUT_DIR  (edit CAST / SETS below to choose takes)"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)
FS = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 18)
RNG = np.random.default_rng(3)


def filmify(img, grain=0.022, desat=0.88, soften=0.6):
    """Take the 'AI gloss' off: soften micro-contrast, desaturate a touch, lift blacks, halation, grain."""
    x = np.asarray(img.convert("RGB"), np.float32) / 255
    h, w = x.shape[:2]
    x = cv2.GaussianBlur(x, (0, 0), soften) * 0.6 + x * 0.4
    g = (x @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    x = g + (x - g) * desat
    x = 0.025 + x * 0.96                                       # milky film black
    hi = np.clip(g - 0.7, 0, 1) * 3
    x = x + cv2.GaussianBlur(hi * x, (0, 0), w / 120) * np.float32([1, .55, .35]) * 0.35
    n = RNG.standard_normal((h * 2 // 3, w * 2 // 3, 3)).astype(np.float32)
    n = cv2.resize(n, (w, h)) * np.float32([0.8, 1, 1.2])
    x = x + n * grain * (0.4 + 0.6 * np.clip(1 - np.abs(g - 0.45) * 1.8, 0, 1))
    return Image.fromarray((np.clip(x, 0, 1) * 255 + .5).astype(np.uint8))


def sheet(cells, cell_h, title, out, cols, q=86):
    ims = [(im.resize((int(im.width * cell_h / im.height), cell_h), Image.LANCZOS), lab) for im, lab in cells]
    cw = max(i.width for i, _ in ims)
    rows = (len(ims) + cols - 1) // cols
    c = Image.new("RGB", (12 + cols * (cw + 12), 56 + rows * (cell_h + 40)), (10, 12, 16))
    d = ImageDraw.Draw(c); d.text((14, 16), title, font=F, fill=(230, 200, 150))
    for i, (im, lab) in enumerate(ims):
        x, y = 12 + (i % cols) * (cw + 12), 56 + (i // cols) * (cell_h + 40)
        c.paste(im, (x, y)); d.text((x + 4, y + cell_h + 8), lab, font=FS, fill=(220, 220, 220))
    c.save(os.path.join(OUT, out), quality=q); print(out, c.size, os.path.getsize(os.path.join(OUT, out)) // 1024, "KB")


def src(p):
    return Image.open(os.path.join(SRC, p)).convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    CAST = [l.split("|") for l in open(os.path.join(SRC, "cast_pick.txt")).read().strip().splitlines()]
    cells = []
    for f, lab in CAST:
        im = filmify(src(f)); cells.append((im, lab))
        im.save(os.path.join(OUT, "portrait-" + lab.split()[0].lower().replace(".", "") + ".jpg"), quality=88)
    sheet(cells, 480, "SECRET UNIVERSE - photoreal cast test (FLUX.1-schnell via AI Horde unless noted; shared film finish)", "cast-sheet.jpg", 6)
