#!/usr/bin/env python3
"""SAMPLE 5 animatic: one held frame per shot (built from the stage-1 pictures, or a labelled sketch
where art does not exist yet), shot captions, subtitles, the dialogue guide.
usage: s5_animatic.py OUT.mp4"""
import json, os, sys, subprocess, numpy as np, cv2
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
sys.argv = [sys.argv[0], f"{S}/s5/animatic_tmp"] + sys.argv[1:]
OUTV = sys.argv[2]
import s5_proof as P                                       # reuse the stage-1 proof engine (hall, plate, faces)
SL = json.load(open(f"{R}/episodes/E01/sample5-shotlist.json"))
W, H = 1280, 720
CX = f"{S}/cx/s5"
def rd(p): return cv2.imread(p)
def to_bgr(img_rgb01): return cv2.cvtColor((np.clip(img_rgb01, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
def fit(im, w=W, h=H): return cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
def keyed(p, scale):
    im = rd(p); f = im.astype(np.float32) / 255; a = 1 - np.clip(((f[..., 1] - np.maximum(f[..., 0], f[..., 2])) - 0.1) / 0.2, 0, 1)
    im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA); a = cv2.resize(a, None, fx=scale, fy=scale)
    return im, a
def paste(bg, im, a, x, y):
    h, w = im.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(bg.shape[1], x + w), min(bg.shape[0], y + h)
    if x1 <= x0 or y1 <= y0: return bg
    sub = im[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32); al = a[y0 - y:y1 - y, x0 - x:x1 - x, None]
    bg[y0:y1, x0:x1] = (bg[y0:y1, x0:x1] * (1 - al) + sub * al).astype(np.uint8); return bg
def earth(t=8.0):
    return fit(to_bgr(P.plate(t)))
def hall(t=8.0):
    return fit(to_bgr(P.world_bg(t)))
def label(img, txt, xy, s=0.9):
    cv2.putText(img, txt, xy, 0, s, (0, 0, 0), 5); cv2.putText(img, txt, xy, 0, s, (255, 255, 255), 2); return img
def helmet(bg, face_p, cx, cy, r, scale):
    im, a = keyed(face_p, scale)
    c = np.zeros(bg.shape[:2], np.uint8); cv2.circle(c, (cx, cy), r, 255, -1)
    canvas = bg.copy(); canvas = paste(canvas, im, a, cx - im.shape[1] // 2, cy - int(im.shape[0] * 0.45))
    m = (c > 0)[..., None]; bg = np.where(m, canvas, bg)
    cv2.circle(bg, (cx, cy), r, (235, 245, 250), 4); cv2.ellipse(bg, (cx - r // 3, cy - r // 2), (r // 4, r // 9), -30, 0, 360, (255, 255, 255), 2)
    return bg
FRAME = {}
def shot_frame(sh):
    k = sh["kind"]
    if k == "wide": return fit(to_bgr(P.wide(12.5)))
    if k == "walk_full": return fit(to_bgr(P.wide(2.6)))
    if k == "walk_track":
        f = to_bgr(P.wide(2.6)); x = int(P.X_START + ((2.6 - P.T_WALK0) / P.CYCLE_S * P.STRIDE) * P.WALK_S)
        return fit(f[380:900, max(0, x - 460):max(0, x - 460) + 924])
    if k == "cu_mira": return fit(to_bgr(P.cu_shot(9.0, "mira")))
    if k == "cu_jax": return fit(to_bgr(P.cu_shot(6.3, "jax")))
    if k == "two_shot":
        bg = hall(); bg = cv2.GaussianBlur(bg, (0, 0), 2)
        im, a = keyed(f"{CX}/J5_cu.png", 0.48); bg = paste(bg, im, a, 80, 720 - im.shape[0])
        im, a = keyed(f"{CX}/M5_cu.png", 0.5); bg = paste(bg, im, a, 620, 690 - im.shape[0])
        cv2.rectangle(bg, (560, 560), (1280, 720), (40, 70, 120), -1); return label(bg, "counter", (900, 650), 0.7)
    if k == "two_shot_noakes":
        bg = hall(); bg = cv2.GaussianBlur(bg, (0, 0), 2)
        cv2.ellipse(bg, (900, 260), (95, 120), 0, 0, 360, (90, 90, 110), -1); cv2.rectangle(bg, (790, 360), (1010, 720), (70, 70, 90), -1)
        label(bg, "NOAKES (design to come)", (760, 120), 0.8)
        im, a = keyed(f"{CX}/M5_cu.png", 0.45); return paste(bg, im, a, 330, 720 - im.shape[0])
    if k == "insert":
        img = np.full((H, W, 3), (40, 52, 60), np.uint8)
        d = sh["desc"].split(":", 1)[1].strip() if ":" in sh["desc"] else sh["desc"]
        for i, line in enumerate([d[j:j + 52] for j in range(0, len(d), 52)][:6]):
            cv2.putText(img, line, (90, 250 + i * 50), 0, 1.0, (200, 240, 220), 2)
        return img
    if k == "title":
        img = earth(1.0); return label(img, "LATER  -  THE OUTER RIM", (360, 380), 1.4)
    if k == "cutaway":
        return fit(rd(f"{CX}/S5_cutaway.png"))
    img = earth(10.0)
    if k == "rim_wide":
        for x in (520, 700):
            cv2.ellipse(img, (x, 560), (55, 70), 0, 0, 360, (225, 225, 230), -1); cv2.circle(img, (x, 470), 42, (240, 248, 250), 3)
        cv2.ellipse(img, (610, 650), (230, 60), 0, 0, 360, (110, 110, 115), -1)
        return label(img, "two suited figures on a boulder (sketch)", (330, 120), 0.8)
    if k == "rim_earth": return img
    if k == "rim_two":
        img = helmet(img, f"{CX}/J5_cu.png", 380, 420, 190, 0.36)
        return helmet(img, f"{CX}/baron_B.png", 900, 420, 190, 0.45)
    if k == "rim_jax": return helmet(img, f"{CX}/J5_cu.png", 640, 400, 290, 0.55)
    if k == "rim_baron": return helmet(img, f"{CX}/baron_B.png", 640, 400, 290, 0.62)
    return img
os.makedirs(f"{S}/s5/animatic", exist_ok=True)
lines = SL["dialogue"]; shots = SL["shots"]
cuts = sorted(set([s["start_s"] for s in shots] + [s["end_s"] for s in shots] + [l["start_s"] for l in lines] + [round(l["start_s"] + l["dur"] + 0.2, 3) for l in lines]))
cuts = [c for c in cuts if c <= SL["duration_s"]]
seg = []
for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
    if b - a < 0.02: continue
    mid = (a + b) / 2
    sh = [s for s in shots if s["start_s"] <= mid < s["end_s"]][0]
    if sh["id"] not in FRAME: FRAME[sh["id"]] = shot_frame(sh)
    img = FRAME[sh["id"]].copy()
    cv2.rectangle(img, (0, 0), (W, 34), (0, 0, 0), -1)
    cv2.putText(img, f"{sh['id']}  {sh['desc'][:110]}", (8, 23), 0, 0.5, (255, 255, 200), 1)
    for l in lines:
        if l["start_s"] - 0.01 <= mid < l["start_s"] + l["dur"] + 0.2:
            t = l["text"]; tw = cv2.getTextSize(t, 0, 0.75, 2)[0][0]
            cv2.putText(img, t, ((W - tw) // 2, 690), 0, 0.75, (0, 0, 0), 5); cv2.putText(img, t, ((W - tw) // 2, 690), 0, 0.75, (255, 255, 255), 2)
    for bt in SL["beats"]:
        if bt["at_s"] <= mid < bt["at_s"] + bt["dur_s"]:
            label(img, bt["what"][:80], (20, 80), 0.6)
    fn = f"{S}/s5/animatic/seg_{i:04d}.png"; cv2.imwrite(fn, img); seg.append((fn, b - a))
with open(f"{S}/s5/animatic/list.txt", "w") as f:
    for fn, d in seg: f.write(f"file '{fn}'\nduration {d:.4f}\n")
    f.write(f"file '{seg[-1][0]}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{S}/s5/animatic/list.txt", "-i", f"{S}/s5/sample5-dialogue-guide.wav",
                "-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "30", "-c:a", "aac", "-b:a", "96k", "-shortest", OUTV], check=True)
print("segments", len(seg))
