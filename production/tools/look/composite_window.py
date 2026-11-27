#!/usr/bin/env python3
"""Pillow composite of a real NASA photo into a set's window (screen blend, graded, grained).
usage: composite_window.py set.png moon.jpg out.jpg"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = 1376/1280
# window polygon measured on test1 (1280-wide coords)
POLY = [(748,18),(1000,8),(1185,8),(1225,60),(1262,300),(1258,410),(1230,428),(1000,400),(760,370),(722,330),(716,120)]
setp, moonp, out = sys.argv[1:4]
base = Image.open(setp).convert("RGB"); W, H = base.size
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(x*S, y*S) for x, y in POLY], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(6))
moon = Image.open(moonp).convert("L")
# place: scale moon so it fills the window with the limb crossing it
mw = int(640*S); moon = moon.resize((mw, int(mw*moon.height/moon.width)), Image.LANCZOS)
canvas = Image.new("L", (W, H), 0); canvas.paste(moon, (int(690*S), int(-40*S)))
m = np.asarray(canvas, np.float32)/255
m = np.clip((m-0.04)*1.15, 0, 1)**1.1 * 0.85          # crush black, soften
# grade: teal shadows, amber-ish highlights, matching test1
r = m*0.95 + 0.02*(1-m); g = m*0.97 + 0.04*(1-m); b = m*0.92 + 0.07*(1-m)
moonrgb = np.stack([r, g, b], -1)
moonrgb = np.asarray(Image.fromarray((moonrgb*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)/255
rng = np.random.default_rng(1); moonrgb = np.clip(moonrgb + rng.normal(0, 0.018, moonrgb.shape), 0, 1)
B = np.asarray(base, np.float32)/255
glass = B*0.55                                           # darken existing glass, keep scratches/reflections
screen = 1-(1-glass)*(1-moonrgb)
M = (np.asarray(mask, np.float32)/255)[..., None]
res = B*(1-M) + screen*M
img = Image.fromarray((np.clip(res, 0, 1)*255).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS)
img.save(out, "JPEG", quality=88, optimize=True)
