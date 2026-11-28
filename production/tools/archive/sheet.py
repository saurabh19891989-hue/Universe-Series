"""Scene-detect one vault film and write a labelled contact sheet of its usable shots.
usage: sheet.py FILM.mp4 OUT_DIR [min_len_s]   -> OUT_DIR/<id>.jpg and OUT_DIR/<id>.scenes.json"""
import sys, os, json, subprocess, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
src, outd = sys.argv[1], sys.argv[2]; minlen = float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
iid = os.path.splitext(os.path.basename(src))[0]
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).decode().strip())
r = subprocess.run(["nice", "ffmpeg", "-v", "info", "-threads", "1", "-i", src, "-an", "-vf",
                    "scale=160:-2,select='gt(scene,0.28)',showinfo", "-f", "null", "-"], capture_output=True, text=True)
cuts = [0.0] + [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)] + [dur]
scenes = []
for a, b in zip(cuts[:-1], cuts[1:]):
    if b - a < minlen:
        continue
    n = max(1, int((b - a) // 8))           # long takes: one thumb per ~8 s piece
    for j in range(n):
        scenes.append((a + (b - a) * j / n, a + (b - a) * (j + 1) / n))
cap = cv2.VideoCapture(src)
thumbs = []
for k, (a, b) in enumerate(scenes):
    fr = []
    for f in (0.3, 0.7):
        cap.set(cv2.CAP_PROP_POS_MSEC, (a + (b - a) * f) * 1000); ok, im = cap.read()
        fr.append(im if ok else None)
    if fr[0] is None:
        continue
    motion = float(np.abs(cv2.resize(fr[0], (64, 48)).astype(np.float32) - cv2.resize(fr[1], (64, 48)).astype(np.float32)).mean()) if fr[1] is not None else 0
    lumv = float(cv2.cvtColor(fr[0], cv2.COLOR_BGR2GRAY).mean())
    thumbs.append(dict(k=len(thumbs), a=round(a, 2), b=round(b, 2), motion=round(motion, 1), luma=round(lumv), img=cv2.resize(fr[0], (192, 144))))
json.dump(dict(id=iid, dur=dur, w=int(cap.get(3)), h=int(cap.get(4)), scenes=[{k: v for k, v in t.items() if k != "img"} for t in thumbs]),
          open(os.path.join(outd, iid + ".scenes.json"), "w"), indent=0)
cols = 10; per = 80
f = ImageFont.truetype("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf", 13)
for pg in range(0, max(1, len(thumbs)), per):
    chunk = thumbs[pg:pg + per]; rows = max(1, (len(chunk) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * 192, rows * 144), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    for i, t in enumerate(chunk):
        x, y = (i % cols) * 192, (i // cols) * 144
        sheet.paste(Image.fromarray(cv2.cvtColor(t["img"], cv2.COLOR_BGR2RGB)), (x, y))
        lab = f"{t['k']} {t['a']:.0f}-{t['b']:.0f} m{t['motion']:.0f}"
        d.rectangle([x, y, x + 8 * len(lab), y + 16], fill=(0, 0, 0)); d.text((x + 2, y), lab, font=f, fill=(255, 220, 80))
    sheet.save(os.path.join(outd, f"{iid}{'' if pg == 0 else '_p%d' % (pg // per + 1)}.jpg"), quality=72)
print(iid, f"{dur:.0f}s", len(thumbs), "shots")
