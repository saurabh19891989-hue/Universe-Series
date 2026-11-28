"""Per-take word error rate for the voice bake-off. Same model and normalisation as wer.py
(faster-whisper small, int8, CPU, beam 5). Run in voice/v_main (has faster-whisper + jiwer).
Usage: python -I bakeoff_wer.py <out_root> > wer.json   (also scores the Kokoro production stems)"""
import sys, os, re, glob, json, subprocess
import numpy as np, jiwer
from faster_whisper import WhisperModel

REPO = "/home/user/Universe-Series"
SCR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
LINES = {l["id"]: l for l in json.load(open(f"{REPO}/production/tools/voice/bakeoff_lines.json"))["lines"]}


def norm(t):
    t = t.lower().replace("—", " ").replace("-", " ").replace("’", "'")
    t = re.sub(r"[^a-z0-9' ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


m = WhisperModel("small", device="cpu", compute_type="int8", download_root=f"{SCR}/voice/whisper",
                 cpu_threads=int(os.environ.get("OMP_NUM_THREADS", "2")))


def score(path, lid):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw, dtype=np.float32), language="en", beam_size=5)
    hyp = " ".join(s.text for s in segs)
    ref = norm(LINES[lid]["text"])
    w = jiwer.wer(ref, norm(hyp) or "x")
    return dict(wer=round(w, 3), heard=hyp.strip())


res = {"kokoro": {}}
for lid, l in LINES.items():
    res["kokoro"][f"{lid}_t1"] = score(f"{SCR}/e01/dialogue/{l['kokoro']}", lid)
for d in sorted(glob.glob(f"{sys.argv[1]}/*/")):
    eng = os.path.basename(d.rstrip("/"))
    res[eng] = {os.path.basename(w)[:-4]: score(w, os.path.basename(w).split("_")[0])
                for w in sorted(glob.glob(f"{d}L*_t*.wav"))}
print(json.dumps(res, indent=1))
