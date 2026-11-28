"""Build the bake-off listening reel: per test line, the Kokoro production take, then each candidate's takes,
each preceded by a short spoken slate (Kokoro voice am_michael, not a cast voice) and a 0.6 s gap.
Every clip gets the same loudness: two-pass ffmpeg loudnorm, linear gain to -20 LUFS, true peak -1.5 dBTP.
Parts are cut on line boundaries so each MP3 stays under 2.9 MB. Writes ORDER.txt with start times.
Run in voice/v_main (kokoro-onnx). Usage: python -I bakeoff_reel.py <out_root> <dest_dir> engine1 engine2 ..."""
import sys, os, json, glob, subprocess, re
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

REPO = "/home/user/Universe-Series"
SCR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
LINES = json.load(open(f"{REPO}/production/tools/voice/bakeoff_lines.json"))["lines"]
SR = 44100
KBPS = 112
MAX_BYTES = 2.85e6
NAMES = {"kokoro": "Kokoro, current", "supertonic3": "Supertonic", "qwen3-design": "Qwen voice design",
         "chatterbox-turbo": "Chatterbox Turbo", "orpheus-3b-q4": "Orpheus"}
NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
root, dest, engines = sys.argv[1], sys.argv[2], sys.argv[3:]
tmp = f"{SCR}/voice2/reel_tmp"
os.makedirs(tmp, exist_ok=True)
os.makedirs(dest, exist_ok=True)
kok = Kokoro(f"{SCR}/voice/models/kokoro/kokoro-v1.0.onnx", f"{SCR}/voice/models/kokoro/voices-v1.0.bin")


def norm_clip(src, dst, target=-20.0):
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", f"loudnorm=I={target}:TP=-1.5:LRA=20:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=20:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", str(SR), "-ac", "1", dst], check=True)
    x, _ = sf.read(dst, dtype="float32")
    return x, float(j["input_i"])


def slate(text, i):
    a, sr = kok.create(text, voice="am_michael", speed=1.1, lang="en-us")
    p = f"{tmp}/slate{i}.wav"
    sf.write(p, a, sr)
    x, _ = norm_clip(p, f"{tmp}/slate{i}_n.wav", -24.0)
    return x


def sil(s):
    return np.zeros(int(SR * s), dtype=np.float32)


blocks = []  # (line, [segments], [order rows])
n = 0
for li, l in enumerate(LINES):
    segs = [slate(f"Line {NUM[li + 1]}. {l['char'].title()}, {l['kind']}.", n), sil(0.5)]
    n += 1
    rows = []
    takes = [("kokoro", 1, f"{SCR}/e01/dialogue/{l['kokoro']}")]
    for e in engines:
        for w in sorted(glob.glob(f"{root}/{e}/{l['id']}_t*.wav")):
            takes.append((e, int(re.search(r"_t(\d+)", w).group(1)), w))
    multi = {e: sum(1 for t in takes if t[0] == e) > 1 for e in set(t[0] for t in takes)}
    for e, t, w in takes:
        label = NAMES.get(e, e) + (f", take {NUM[t]}" if multi[e] else "")
        segs += [slate(label + ".", n), sil(0.35)]
        n += 1
        x, li_in = norm_clip(w, f"{tmp}/c{n}.wav")
        rows.append(dict(line=l["id"], char=l["char"], kind=l["kind"], model=e, take=t, file=os.path.basename(w),
                         clip_s=round(len(x) / SR, 2), input_lufs=li_in, offset_in_block=round(sum(len(s) for s in segs) / SR, 2)))
        segs += [x, sil(0.9)]
    segs.append(sil(0.6))
    blocks.append((l, segs, rows))

# pack blocks into parts under the size cap
parts, cur = [], []
for b in blocks:
    secs = sum(len(s) for s in b[1]) / SR
    cur_s = sum(sum(len(s) for s in c[1]) / SR for c in cur)
    if cur and (cur_s + secs) * KBPS * 1000 / 8 > MAX_BYTES:
        parts.append(cur)
        cur = []
    cur.append(b)
parts.append(cur)
order = ["Voice bake-off listening reel, 28 Nov 2026. Nobody has listened to this (agents cannot hear).",
         "Every clip is set to the same loudness (-20 LUFS, linear gain) so whispers and shouts play at the same level;",
         "judge acting and voice, not volume. Slates are spoken by a Kokoro voice (am_michael) that is not in the cast.",
         f"Engines: {', '.join(NAMES.get(e, e) for e in ['kokoro'] + engines)}.", ""]
for pi, p in enumerate(parts, 1):
    fn = f"bakeoff-reel-part{pi}.mp3"
    audio = np.concatenate([s for b in p for s in b[1]])
    wav = f"{tmp}/part{pi}.wav"
    sf.write(wav, audio, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", f"{KBPS}k", f"{dest}/{fn}"], check=True)
    size = os.path.getsize(f"{dest}/{fn}")
    order.append(f"== {fn}  ({len(audio) / SR:.0f} s, {size / 1e6:.2f} MB)")
    t0 = 0.0
    for l, segs, rows in p:
        order.append(f"  {int(t0 // 60)}:{t0 % 60:04.1f}  LINE {l['id'][1:]} {l['char']} ({l['kind']}): \"{l['text']}\"")
        order.append(f"           direction: {l['direction']}")
        for r in rows:
            ts = t0 + r["offset_in_block"]
            order.append(f"    {int(ts // 60)}:{ts % 60:04.1f}  {r['line']}  {NAMES.get(r['model'], r['model']):<22} take {r['take']}  "
                         f"({r['clip_s']} s, source {r['input_lufs']} LUFS)  [{r['file']}]")
        t0 += sum(len(s) for s in segs) / SR
    order.append("")
open(f"{dest}/ORDER.txt", "w").write("\n".join(order) + "\n")
print("\n".join(order))
