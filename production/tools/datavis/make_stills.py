#!/usr/bin/env python3
"""Pick one still per clip from the rendered PNGs, write <500 KB JPGs and contact sheets.
   python3 production/tools/datavis/make_stills.py
"""
import os, glob, re, collections
from PIL import Image, ImageDraw, ImageFont

RAW = os.environ.get("DATAVIS_RAW", "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/datavis/_stills_png")
OUT = os.environ.get("DATAVIS_STILLS", "/home/user/Universe-Series/samples/e01/datavis")
MAXB = 480_000


def save_small(im, path, width=1280):
    im = im.convert("RGB")
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    q = 88
    while True:
        im.save(path, "JPEG", quality=q, optimize=True)
        if os.path.getsize(path) <= MAXB or q <= 40:
            return
        q -= 6


def main():
    os.makedirs(OUT, exist_ok=True)
    groups = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RAW, "*.png"))):
        m = re.match(r"(.+)__t([\d.]+)\.png$", os.path.basename(f))
        groups[m.group(1)].append((float(m.group(2)), f))
    picks = []
    for name, lst in sorted(groups.items()):
        lst.sort()
        t, f = lst[len(lst) // 2] if len(lst) > 2 else lst[-1]
        save_small(Image.open(f), os.path.join(OUT, name + ".jpg"))
        picks.append((name, f))
    font = ImageFont.load_default()
    # two contact sheets (4 columns, 480x270 cells)
    half = len(picks) // 2 + 1
    for si, part in enumerate([picks[:half], picks[half:]]):
        cols, cw, ch = 4, 480, 270
        rows = (len(part) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cw, rows * (ch + 18)), (10, 10, 10))
        d = ImageDraw.Draw(sheet)
        for k, (name, f) in enumerate(part):
            x, y = (k % cols) * cw, (k // cols) * (ch + 18)
            sheet.paste(Image.open(f).convert("RGB").resize((cw - 4, ch - 4), Image.LANCZOS), (x + 2, y + 2))
            d.text((x + 4, y + ch), name, fill=(220, 220, 200), font=font)
        save_small(sheet, os.path.join(OUT, "contact-sheet-%d.jpg" % (si + 1)), width=1920)
    print(len(picks), "stills written to", OUT)


if __name__ == "__main__":
    main()
