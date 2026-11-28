#!/usr/bin/env python3
"""SAMPLE 5 stage-1 proof (about 13 s): new animated designs; planted-foot walk with optical-flow
in-betweens; stop; close-ups with seamless picture-made mouth/blink/brow sets; real NASA Earthrise
in the window, zoomed so it fills more of the glass.
usage: s5_proof.py OUTDIR [--still T ...]   (renders OUTDIR/proof-picture.mp4 otherwise, 4 workers)
"""
import json, math, os, subprocess, sys, time
import numpy as np, cv2, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import Channels, ease, noise1, col, P

W, H, FPS = 1920, 1080, 24
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
CX, FACES = f"{S}/cx/s5", f"{S}/s5/faces"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DUR = 13.0
T_WALK0, CYCLE_S = 0.3, 1.15            # walk start, seconds per cycle (a relaxed stroll)
LINES = [  # (id, who, start, stem, rhubarb)
    ("3-05", "jax", 6.05, f"{S}/e01/dialogue/E01_S03_L005_JAX.wav", f"{S}/toon/lips/E01_S03_L005_JAX.json"),
    ("3-06", "mira", 8.45, f"{S}/e01/dialogue/E01_S03_L006_MIRA.wav", f"{S}/toon/lips/E01_S03_L006_MIRA.json")]
TEXT = {"3-05": "Here's my situation. My aunt—", "3-06": "You don't have an aunt."}
SHOTS = [("wide", 0.0, 5.9), ("cu_jax", 5.9, 8.25), ("cu_mira", 8.25, 11.7), ("wide", 11.7, 13.0)]

def key_green(im):
    f = im.astype(np.float32) / 255
    d = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
    a = 1 - np.clip((d - 0.10) / 0.20, 0, 1)
    a = cv2.GaussianBlur(cv2.erode(a, np.ones((3, 3), np.uint8)), (0, 0), 0.7)
    f[..., 1] = np.minimum(f[..., 1], np.maximum(f[..., 0], f[..., 2]) + 0.03)
    rgb = f[..., ::-1]
    return np.dstack([rgb * a[..., None], a]).astype(np.float32)        # premultiplied RGBA

def crop_alpha(rgba, pad=12):
    ys, xs = np.nonzero(rgba[..., 3] > 0.02)
    y0, y1, x0, x1 = max(0, ys.min() - pad), ys.max() + pad, max(0, xs.min() - pad), xs.max() + pad
    return rgba[y0:y1, x0:x1].copy(), (x0, y0)

def over(dst, rgba):
    return dst * (1 - rgba[..., 3:4]) + rgba[..., :3]

def place(rgba, sx, ax, ay, X, Y, rot=0.0, sy=None):
    """put picture point (ax, ay) at screen (X, Y), scale sx (sy), rotate deg about that point"""
    sy = sx if sy is None else sy
    a = math.radians(rot); c, s_ = math.cos(a), math.sin(a)
    M = np.array([[c * sx, -s_ * sy, 0], [s_ * sx, c * sy, 0]], np.float64)
    M[:, 2] = np.array([X, Y]) - M[:, :2] @ np.array([ax, ay])
    return cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))

# ------------------------------------------------------------------ walk: planted feet + flow in-betweens
WI = json.load(open(f"{CX}/w5.json"))
WALK = [crop_alpha(key_green(cv2.imread(f"{CX}/w5_{j}.png")))[0] for j in range(8)]
# stance foot (picture x, relative to the head) per drawing, read from the sheet; contacts use the front foot
REL = [87, 20, -12, -73, 72, 12, -12, None]
# body x per drawing over one cycle so that the stance foot stays planted (see TOON-FORMAT, sample 5)
BX = [-87, -20, 12, 73, 81, 141, 165, 199]; STRIDE = 319.0
INC = [BX[k + 1] - BX[k] for k in range(7)] + [BX[0] + STRIDE - BX[7]]
CUM = np.concatenate([[0], np.cumsum(INC)])
# crop offsets: drawing-local head x and ground y
HEADX = []; GROUND = []
for j in range(8):
    a = WALK[j][..., 3] > 0.05; ys, xs = np.nonzero(a)
    top = a[ys.min():ys.min() + int((ys.max() - ys.min()) * 0.12)]
    HEADX.append(float(np.nonzero(top.any(0))[0].mean())); GROUND.append(float(ys.max()))
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def canvas_pair(A, xa, B, xb, h):
    """A and B on one canvas, head-x positions xa/xb (canvas px), ground at row h-20"""
    Wc = int(max(xa, xb) + 400); C = np.zeros((h, Wc, 4), np.float32)
    def put(R, x_head, hx, gy):
        out = C.copy(); ox = int(round(x_head - hx)); oy = int(round(h - 20 - gy))
        y0, x0 = max(0, oy), max(0, ox); y1, x1 = min(h, oy + R.shape[0]), min(Wc, ox + R.shape[1])
        out[y0:y1, x0:x1] = R[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
        return out
    return put
FLOWS = {}
def morph(A, B, t, key):
    """optical-flow in-between of two RGBA pictures on the same canvas"""
    if key not in FLOWS:
        g = lambda R: cv2.cvtColor((over(np.full(R.shape[:2] + (3,), 0.5, np.float32), R) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        ga, gb = g(A), g(B)
        FLOWS[key] = (DIS.calc(ga, gb, None), DIS.calc(gb, ga, None))
    fab, fba = FLOWS[key]
    h, w = A.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = float(t)
    Aw = cv2.remap(A, (xx - t * fab[..., 0]).astype(np.float32), (yy - t * fab[..., 1]).astype(np.float32), cv2.INTER_LINEAR)
    Bw = cv2.remap(B, (xx - (1 - t) * fba[..., 0]).astype(np.float32), (yy - (1 - t) * fba[..., 1]).astype(np.float32), cv2.INTER_LINEAR)
    return Aw * (1 - t) + Bw * t

WALK_S = 0.906                      # sheet px -> world px (figure ~600 px tall)
X_END = 1130.0                      # where he stops (head x, world)
N_CYC = 4.0
X_START = X_END - (N_CYC * STRIDE + BX[0] - BX[0]) * WALK_S
T_WALK1 = T_WALK0 + N_CYC * CYCLE_S
GROUND_Y = 1000.0

def walk_frame(t):
    """returns RGBA (screen, world coords) for the walk at time t, with in-betweens"""
    d = (t - T_WALK0) / CYCLE_S * STRIDE                    # sheet px travelled (constant speed)
    d = min(max(d, 0), N_CYC * STRIDE - 1e-3)
    n, r = divmod(d, STRIDE)
    k = int(np.searchsorted(CUM, r, side="right") - 1); k = min(k, 7)
    f = (r - CUM[k]) / INC[k]
    k2 = (k + 1) % 8
    xa = BX[k] + n * STRIDE; xb = (BX[k2] + (n + (1 if k2 == 0 else 0)) * STRIDE)
    h = 760; base = min(xa, xb) - 300
    put = canvas_pair(WALK[k], xa - base, WALK[k2], xb - base, h)
    A = put(WALK[k], xa - base, HEADX[k], GROUND[k]); B = put(WALK[k2], xb - base, HEADX[k2], GROUND[k2])
    M = morph(A, B, f, (k, k2, int(xb - xa)))
    # canvas x of the body = xa + f*(xb-xa); world x = X_START + (that - BX[0]) * scale
    return place(M, WALK_S, (xa - base), h - 20, X_START + (xa - BX[0]) * WALK_S, GROUND_Y)

STOP = crop_alpha(key_green(cv2.imread(f"{CX}/J5_stop.png")))[0]
def stop_anchor():
    a = STOP[..., 3] > 0.05; ys, xs = np.nonzero(a)
    top = a[ys.min():ys.min() + int((ys.max() - ys.min()) * 0.10)]
    return float(np.nonzero(top.any(0))[0].mean()), float(ys.max()), float(ys.max() - ys.min())
SHX, SGY, SHH = stop_anchor()
STOP_S = 612 / SHH
def jax_wide(t):
    br = 1 + 0.006 * math.sin(t * 2 * math.pi / 3.3)
    sway = 0.5 * noise1(t, 3, 0.3)
    if t < T_WALK1:
        return walk_frame(t)
    # 5-frame flow morph from the last walk drawing into the stop pose, then a moving hold
    stop = place(STOP, STOP_S, SHX, SGY, X_END, GROUND_Y, rot=sway, sy=STOP_S * br)
    k = (t - T_WALK1) / 0.22
    if k < 1:
        last = walk_frame(T_WALK1 - 1e-3)
        both = np.concatenate([last, stop], 2)
        x0 = int(X_END - 400); x1 = int(X_END + 400); y0 = int(GROUND_Y - 700); y1 = int(GROUND_Y + 30)
        A, B = last[y0:y1, x0:x1], stop[y0:y1, x0:x1]
        m = morph(np.ascontiguousarray(A), np.ascontiguousarray(B), ease("io", k), ("stop",))
        out = np.zeros_like(stop); out[y0:y1, x0:x1] = m
        return out
    return stop

MIRA = key_green(cv2.imread(f"{CX}/M5_idle.png"))
def mira_wide(t):
    br = 1 + 0.006 * math.sin(t * 2 * math.pi / 3.7 + 1)
    return place(MIRA, 0.35, 830, 940, 1660, 709, rot=0.6 * noise1(t, 9, 0.25), sy=0.35 * br)

# ------------------------------------------------------------------ set + window plate
HALL = cv2.imread(f"{CX}/S5_hall.png")[:, :, ::-1].astype(np.float32) / 255
k_ = W / HALL.shape[1]
HALL = cv2.resize(HALL, (W, int(HALL.shape[0] * k_)), interpolation=cv2.INTER_LANCZOS4)[:H]
HALL = np.clip(HALL * 1.3 - cv2.GaussianBlur(HALL, (0, 0), 1.5) * 0.3, 0, 1)
lum = HALL.max(2); win = np.zeros((H, W), np.uint8)
win[int(120 * k_):int(560 * k_), int(250 * k_):int(1510 * k_)] = (lum[int(120 * k_):int(560 * k_), int(250 * k_):int(1510 * k_)] < 0.08)
n, lab, st, _ = cv2.connectedComponentsWithStats(win, 8); kk = 1 + int(np.argmax(st[1:, 4]))
WIN = cv2.GaussianBlur(cv2.dilate((lab == kk).astype(np.uint8), np.ones((3, 3))).astype(np.float32), (0, 0), 1.2)
FG = np.zeros((H, W), np.float32)
cv2.fillPoly(FG, [(np.array([[1135, 553], [1672, 553], [1672, 941], [1600, 941], [1135, 662]]) * k_).astype(np.int32)], 1.0)
FG = cv2.GaussianBlur(FG, (0, 0), 1.0)
CAP = cv2.VideoCapture(f"{S}/toon/plates/window2.mp4"); NPL = int(CAP.get(7)); PLPOS = [-1, None]
def plate(t):
    i = int(t * FPS) % NPL
    if i != PLPOS[0] + 1: CAP.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, f = CAP.read(); PLPOS[0] = i
    f = f[:, :, ::-1].astype(np.float32) / 255 * 1.3
    pw = 2700.0; s = pw / f.shape[1]
    M = np.float64([[s, 0, -330], [0, s, -150]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR)

def world_bg(t):
    return HALL * (1 - WIN[..., None]) + plate(t) * WIN[..., None]

def rim(layer, k=0.5, w=3):
    a = layer[..., 3]; sh = np.zeros_like(a); sh[w:, :-w] = a[:-w, w:]   # light from upper right (window)
    r = np.clip(a - sh, 0, 1) * a
    out = layer.copy(); out[..., :3] += cv2.GaussianBlur(r, (0, 0), 1.2)[..., None] * np.array([0.7, 0.85, 1.0], np.float32) * k
    return out

def contact(img, x, y, rx, ry, k=0.35):
    m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(x), int(y)), (int(rx), int(ry)), 0, 0, 360, 1.0, -1)
    return img * (1 - k * cv2.GaussianBlur(m, (0, 0), ry * 0.8)[..., None])

# ------------------------------------------------------------------ faces
import soundfile as sf
CUES, ENV = {}, {}
for lid, who, st0, wav, rh in LINES:
    CUES[lid] = (who, st0, [(c["start"], c["end"], c["value"]) for c in json.load(open(rh))["mouthCues"]])
    a, sr = sf.read(wav, always_2d=True); a = a.mean(1); hop = sr // 48
    e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) for i in range(len(a) // hop)]); ENV[lid] = (st0, e / e.max())
FCACHE = {}
def face_img(base, key):
    p = f"{FACES}/{base}__{key}.png"
    if not os.path.exists(p): p = f"{FACES}/{base}__X.png"
    if p not in FCACHE: FCACHE[p] = key_green(cv2.imread(p))
    return FCACHE[p]
def mouth_at(who, t):
    for lid, (w_, st0, cues) in CUES.items():
        if w_ != who: continue
        lt = t - st0
        for c0, c1, v in cues:
            if c0 <= lt < c1: return v, max(0.0, lt - c0)
    return "X", 9.0
def env_at(who, t):
    for lid, (st0, e) in ENV.items():
        if CUES[lid][0] == who and 0 <= t - st0 < len(e) / 48: return float(e[int((t - st0) * 48)])
    return 0.0
def blink_at(t, seed):
    import random
    rng = random.Random(seed); bt = rng.uniform(0.4, 1.5)
    while bt < t + 1:
        if 0 <= t - bt < 0.17: return math.sin((t - bt) / 0.17 * math.pi)
        bt += rng.uniform(2.0, 4.0)
    return 0.0
def head_rgba(base, who, t, brow_key=None, brow_amt=0.0, seed=1):
    """the close-up picture with its mouth/blink/brow set blended (only those regions differ)"""
    m, since = mouth_at(who, t)
    prev = mouth_at(who, t - 0.07)[0]
    k = min(1.0, since / 0.07)                         # 2-frame mouth dissolve, seamless: same base picture
    img = face_img(base, m) * k + face_img(base, prev) * (1 - k) if prev != m else face_img(base, m).copy()
    if brow_key and brow_amt > 0:
        X = face_img(base, "X"); img = img + (face_img(base, brow_key) - X) * brow_amt
    b = blink_at(t, seed)
    if b > 0:
        X = face_img(base, "X"); img = img + (face_img(base, "blink") - X) * b
    return img

def cu_shot(t, who):
    # background: the hall window, pushed in and soft
    cx, cy, z = (900, 330, 2.1) if who == "jax" else (1150, 330, 2.1)
    M = np.float64([[z, 0, W / 2 - cx * z], [0, z, H / 2 - cy * z]])
    bg = cv2.GaussianBlur(cv2.warpAffine(world_bg(t).astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), (0, 0), 3)
    e = env_at(who, t)
    if who == "jax":
        img = head_rgba("J5_cu", "jax", t, seed=5)
        if t > 7.75: img = img + (face_img("J5_cu", "brow_up") - face_img("J5_cu", "X")) * ease("out", (t - 7.75) / 0.15)
        X, Y = 760, 1080
    else:
        amt = ease("snap", (t - 10.05) / 0.25) if t > 10.05 else 0.0
        if 9.9 < t <= 10.05: amt = -0.25 * ease("out", (t - 9.9) / 0.15)       # anticipation: brows dip first
        img = head_rgba("M5_cu", "mira", t, "brow_skeptic", max(0.0, amt), seed=8)
        if amt < 0: img = img + (face_img("M5_cu", "brow_frown") - face_img("M5_cu", "X")) * (-amt)
        X, Y = 1150, 1080
    tilt = 0.9 * noise1(t, 4 if who == "jax" else 6, 0.3) + 2.2 * e * math.sin(t * 6.0)
    br = 1 + 0.007 * math.sin(t * 2 * math.pi / 3.2)
    lay = place(np.clip(img, 0, None), 1.15, 836, 941, X, Y + 4 * e, rot=tilt, sy=1.15 * br)
    return over(bg, rim(lay, 0.45, 4))

def wide(t):
    img = world_bg(t)
    lm = rim(mira_wide(t), 0.4, 2)
    img = over(img, lm)
    img = img * (1 - FG[..., None]) + HALL * FG[..., None]
    j = rim(jax_wide(t), 0.5, 3)
    img = contact(img, X_END if t >= T_WALK1 else X_START + ((t - T_WALK0) / CYCLE_S * STRIDE) * WALK_S, GROUND_Y + 2, 70, 11)
    return over(img, j)

VIG = None
def finish(img, t):
    global VIG
    x = np.clip(img, 0, 1); lum_ = x.mean(2, keepdims=True); x = lum_ + (x - lum_) * 1.05
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        VIG = (1 - 0.13 * np.clip((((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) * 0.6, 0, 1))[..., None]
    x = x * VIG + cv2.resize(np.random.default_rng(int(t * FPS)).normal(0, 0.008, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None]
    out = np.clip(x * 255 + 0.5, 0, 255).astype(np.uint8)
    for lid, (who, st0, cues) in CUES.items():
        if st0 - 0.05 <= t < st0 + cues[-1][1] + 0.25:
            surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
            font = skia.Font(skia.Typeface("DejaVu Sans"), 34); tw = font.measureText(TEXT[lid])
            cv.drawString(TEXT[lid], (W - tw) / 2, H - 58, font, P(col("#000000", 220), 6)); cv.drawString(TEXT[lid], (W - tw) / 2, H - 58, font, P(col("#ffffff")))
            a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32); al = a[..., 3:4] / 255
            out = (out * (1 - al) + a[..., :3] * al).astype(np.uint8)
    return out

def frame(t):
    for name, t0, t1 in SHOTS:
        if t0 <= t < t1: break
    img = wide(t) if name == "wide" else cu_shot(t, "jax" if name == "cu_jax" else "mira")
    out = finish(img, t)
    if t < 0.4: out = (out * (t / 0.4)).astype(np.uint8)
    if DUR - t < 0.5: out = (out * ((DUR - t) / 0.5)).astype(np.uint8)
    return out

def chunk(args):
    a, b, fn = args; cv2.setNumThreads(1)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "1", fn], stdin=subprocess.PIPE)
    c0 = time.process_time()
    for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); return time.process_time() - c0

if __name__ == "__main__":
    args = sys.argv[2:]
    if "--still" in args:
        for tt in args[args.index("--still") + 1:]:
            cv2.imwrite(f"{OUT}/still_{float(tt):06.2f}.jpg", cv2.cvtColor(frame(float(tt)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit(0)
    nf = int(DUR * FPS); nch = 8; sz = math.ceil(nf / nch)
    jobs = [(i * sz, min(nf, (i + 1) * sz), f"{OUT}/seg_{i}.mp4") for i in range(nch)]
    from multiprocessing import Pool
    w0 = time.time()
    with Pool(4) as pool: cpu = pool.map(chunk, jobs)
    open(f"{OUT}/segs.txt", "w").write("".join(f"file 'seg_{i}.mp4'\n" for i in range(nch)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/segs.txt", "-c", "copy", f"{OUT}/proof-picture.mp4"], check=True)
    json.dump({"wall_s": round(time.time() - w0, 1), "cpu_s": round(sum(cpu), 1), "cpu_s_per_video_s": round(sum(cpu) / DUR, 1)}, open(f"{OUT}/render.json", "w"))
    print("done")
