"""Per-take numbers for the voice bake-off (cannot judge sound; these are rough proxies only).
Needs librosa + soundfile (any venv with them, e.g. voice2/v_qwen).
Usage: python -I bakeoff_analyze.py <out_root> > metrics.json
<out_root>/<engine>/<LINE>_t<n>.wav ; also analyses the Kokoro production stem as engine 'kokoro'.
Measures: duration, words/s, f0 median Hz, f0 range (semitones p5-p95), f0 std (st), voiced fraction
(low = breathy/whispered), loudness dynamics (std of active 25 ms frame RMS in dB), active RMS dBFS,
peak dBFS, clipped samples, lead/trail silence, internal pause fraction, spectral centroid."""
import sys, os, glob, json, re
import numpy as np, soundfile as sf, librosa

REPO = "/home/user/Universe-Series"
LINES = {l["id"]: l for l in json.load(open(f"{REPO}/production/tools/voice/bakeoff_lines.json"))["lines"]}
KOK = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/dialogue"


def words(t):
    t = re.sub(r"<[^>]+>|\[[^\]]+\]|\([^)]*\)", " ", t)
    return len(re.findall(r"[A-Za-z0-9']+", t))


def analyse(path, lid):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    peak = float(np.max(np.abs(x)) + 1e-9)
    clipped = int(np.sum(np.abs(x) >= 0.999))
    y = librosa.resample(x, orig_sr=sr, target_sr=16000) if sr != 16000 else x
    hop = 400  # 25 ms
    rms = librosa.feature.rms(y=y, frame_length=800, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-9)
    thr = db.max() - 35
    act = db > thr
    idx = np.where(act)[0]
    lead = float(idx[0] * hop / 16000) if len(idx) else 0.0
    trail = float((len(db) - 1 - idx[-1]) * hop / 16000) if len(idx) else 0.0
    span = act[idx[0]:idx[-1] + 1] if len(idx) else act
    pause_frac = float(1 - span.mean()) if len(span) else 0.0
    f0, vflag, _ = librosa.pyin(y, fmin=60, fmax=600, sr=16000, frame_length=1024, hop_length=320)
    f0v = f0[~np.isnan(f0)]
    voiced = float(np.mean(vflag[: len(vflag)])) if len(vflag) else 0.0
    # voiced fraction measured only inside the active span
    if len(idx):
        a0, a1 = int(idx[0] * hop / 320), int((idx[-1] + 1) * hop / 320)
        voiced = float(np.mean(vflag[a0:a1])) if a1 > a0 else voiced
    st = 12 * np.log2(f0v / np.median(f0v)) if len(f0v) > 5 else np.array([0.0])
    dur = len(x) / sr
    sp_dur = max(dur - lead - trail, 0.01)
    return dict(
        dur_s=round(dur, 2), speech_s=round(sp_dur, 2), wps=round(words(LINES[lid]["text"]) / sp_dur, 2),
        f0_med=round(float(np.median(f0v)), 1) if len(f0v) > 5 else None,
        f0_range_st=round(float(np.percentile(st, 95) - np.percentile(st, 5)), 1),
        f0_std_st=round(float(np.std(st)), 2), voiced_frac=round(voiced, 2),
        loud_std_db=round(float(np.std(db[act])), 1), active_rms_dbfs=round(float(np.mean(db[act])), 1),
        peak_dbfs=round(20 * np.log10(peak), 1), clipped=clipped,
        lead_s=round(lead, 2), trail_s=round(trail, 2), pause_frac=round(pause_frac, 2),
        centroid_hz=int(np.mean(librosa.feature.spectral_centroid(y=y, sr=16000)[0][act])) if act.any() else 0)


if __name__ == "__main__":
    root = sys.argv[1]
    res = {"kokoro": {}}
    for lid, l in LINES.items():
        res["kokoro"][f"{lid}_t1"] = analyse(f"{KOK}/{l['kokoro']}", lid)
    for d in sorted(glob.glob(f"{root}/*/")):
        eng = os.path.basename(d.rstrip("/"))
        res[eng] = {}
        for w in sorted(glob.glob(f"{d}L*_t*.wav")):
            n = os.path.basename(w)[:-4]
            res[eng][n] = analyse(w, n.split("_")[0])
    print(json.dumps(res, indent=1))
