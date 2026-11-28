#!/usr/bin/env python3
"""Cut parts out of a design picture on a flat white background.
usage: cut_parts.py SHEET.jpg OUTDIR PREFIX [N]
Background = near-white pixels connected to the picture border (flood fill), so white inside the
drawing (eye whites, teeth) is kept. The N largest pieces (left to right) are saved as
OUTDIR/PREFIX_<i>.png (RGBA, cropped) plus PREFIX_<i>.json (bbox in the sheet, size).
"""
import sys, json, os, numpy as np, cv2
src, outdir, prefix = sys.argv[1:4]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 2
os.makedirs(outdir, exist_ok=True)
im = cv2.imread(src); h, w = im.shape[:2]
near_white = (im.min(axis=2) > 200).astype(np.uint8)
ff = near_white.copy(); mask = np.zeros((h + 2, w + 2), np.uint8)
bg = np.zeros((h, w), np.uint8)
for x in range(0, w, 7):
    for y in (0, h - 1):
        if near_white[y, x] and not bg[y, x]:
            m = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(ff, m, (x, y), 2, loDiff=0, upDiff=0, flags=8 | cv2.FLOODFILL_MASK_ONLY | (1 << 8))
            bg |= m[1:-1, 1:-1]
for y in range(0, h, 7):
    for x in (0, w - 1):
        if near_white[y, x] and not bg[y, x]:
            m = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(ff, m, (x, y), 2, loDiff=0, upDiff=0, flags=8 | cv2.FLOODFILL_MASK_ONLY | (1 << 8))
            bg |= m[1:-1, 1:-1]
fg = (1 - bg).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
k, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
idx = sorted(range(1, k), key=lambda i: -st[i, cv2.CC_STAT_AREA])[:n]
idx = sorted(idx, key=lambda i: st[i, cv2.CC_STAT_LEFT])
# soft edge: alpha from the mask, feathered 1px, and near-white fringe pixels faded
for j, i in enumerate(idx):
    x, y, bw, bh = st[i, :4]
    m = (lab == i).astype(np.float32)
    m = cv2.GaussianBlur(m, (3, 3), 0.7)
    a = (m[y:y + bh, x:x + bw] * 255).astype(np.uint8)
    rgba = cv2.cvtColor(im[y:y + bh, x:x + bw], cv2.COLOR_BGR2BGRA); rgba[..., 3] = a
    cv2.imwrite(f"{outdir}/{prefix}_{j}.png", rgba)
    json.dump({"sheet": src, "bbox": [int(x), int(y), int(bw), int(bh)]}, open(f"{outdir}/{prefix}_{j}.json", "w"))
    print(prefix, j, x, y, bw, bh)
