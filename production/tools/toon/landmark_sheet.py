#!/usr/bin/env python3
"""Gridded head crops for reading face landmarks by eye (eyes, mouth, chin, head ellipse, neck).
usage: landmark_sheet.py OUT.jpg FRACTION PIC [PIC ...]   (FRACTION = share of figure height to crop from the top)
Labels are in the picture's own pixel coordinates. Also prints each figure's bbox and foot anchor.
"""
import sys, cv2, numpy as np
out, frac, pics = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
tiles = []
for p in pics:
    im = cv2.imread(p); f = im.astype(np.float32) / 255
    a = (f[..., 1] - np.maximum(f[..., 0], f[..., 2])) < 0.2
    a = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ys, xs = np.nonzero(a)
    y0, y1 = ys.min(), ys.max(); hgt = y1 - y0
    bot = ys > y1 - hgt * 0.02
    print(p.split('/')[-1], "bbox", xs.min(), y0, xs.max(), y1, "foot", int(np.median(xs[bot])), y1)
    cy1 = int(y0 + hgt * frac)
    rows = np.nonzero(a[y0:cy1].any(1))[0]
    cols = np.nonzero(a[y0:int(y0 + (cy1 - y0) * 0.75)].any(0))[0]
    x0, x1 = max(0, cols.min() - 10), min(im.shape[1], cols.max() + 10)
    x0 = max(x0, (x0 + x1) // 2 - int((cy1 - y0) * 0.6)); x1 = min(x1, (x0 + x1) // 2 + int((cy1 - y0) * 0.6))
    crop = im[max(0, y0 - 10):cy1, x0:x1].copy()
    sc = 520 / crop.shape[0]
    crop = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    oy, ox = max(0, y0 - 10), x0
    step = 20 if hgt * frac < 300 else 40
    for v in range((oy // step + 1) * step, cy1, step):
        yy = int((v - oy) * sc); cv2.line(crop, (0, yy), (crop.shape[1], yy), (0, 0, 255) if v % (step * 5) == 0 else (120, 120, 255), 1)
        cv2.putText(crop, str(v), (2, yy - 2), 0, 0.4, (0, 0, 255), 1)
    for u in range((ox // step + 1) * step, x1, step):
        xx = int((u - ox) * sc); cv2.line(crop, (xx, 0), (xx, crop.shape[0]), (255, 0, 0) if u % (step * 5) == 0 else (255, 150, 150), 1)
        cv2.putText(crop, str(u), (xx + 1, 12), 0, 0.4, (255, 0, 0), 1)
    cv2.putText(crop, p.split('/')[-1][:-4], (4, crop.shape[0] - 6), 0, 0.6, (0, 0, 0), 2)
    tiles.append(crop)
w = sum(t.shape[1] for t in tiles)
cv2.imwrite(out, np.hstack([np.pad(t, ((0, 520 - t.shape[0]), (0, 4), (0, 0))) for t in tiles]))
