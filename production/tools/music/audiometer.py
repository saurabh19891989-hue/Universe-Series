#!/usr/bin/env python3
"""audiometer - objective measurements for cues, effects and mixes (agents cannot hear).

python3 audiometer.py FILE [FILE ...]          one JSON line per file
python3 audiometer.py --json out.json FILE ...  also write all results to a file

Per file: integrated loudness (BS.1770 via pyloudnorm), true peak (4x oversampled), loudness
range (EBU-style: 10th-95th percentile of 3 s short-term loudness, gated), crest factor,
band shares (% of energy) in sub/low/low-mid/speech/presence/air, spectral centroid, stereo
correlation and side-to-mid ratio, silence share, and the decay time of the final tail
(time from the last loud moment to -40 dB below it: a rough reverb/release tail reading).
These are measurements, never a verdict on how it sounds.
"""
import json
import subprocess
import sys

import numpy as np

SR = 48000
BANDS = [("sub_20_60", 20, 60), ("low_60_250", 60, 250), ("lowmid_250_1k", 250, 1000),
         ("speech_1k_4k", 1000, 4000), ("presence_4k_8k", 4000, 8000), ("air_8k_16k", 8000, 16000)]


def load(path, sr=SR):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2).astype(np.float64)


def lufs(x, sr=SR):
    import pyloudnorm as pyln
    if len(x) < sr // 2:
        return -70.0
    v = pyln.Meter(sr).integrated_loudness(x)
    return float(v) if np.isfinite(v) else -70.0


def true_peak(x):
    from scipy.signal import resample_poly
    up = resample_poly(x, 4, 1, axis=0)
    return float(20 * np.log10(np.abs(up).max() + 1e-12))


def short_term(x, sr=SR, win=3.0, hop=1.0):
    """3 s short-term loudness every second (K-weighted, via pyloudnorm's filter)."""
    import pyloudnorm as pyln
    m = pyln.Meter(sr, block_size=win)
    out = []
    w, h = int(win * sr), int(hop * sr)
    for i in range(0, max(1, len(x) - w + 1), h):
        seg = x[i:i + w]
        if len(seg) < w:
            break
        try:
            v = m.integrated_loudness(seg)
        except Exception:
            v = -70
        out.append(v if np.isfinite(v) else -70.0)
    return np.array(out)


def lra(x, sr=SR):
    st = short_term(x, sr)
    st = st[st > -70]
    if len(st) < 3:
        return 0.0
    rel = 10 * np.log10(np.mean(10 ** (st / 10))) - 20
    st = st[st > rel]
    if len(st) < 3:
        return 0.0
    return float(np.percentile(st, 95) - np.percentile(st, 10))


def band_shares(x, sr=SR):
    m = x.mean(1)
    n = 1 << 15
    spec = np.zeros(n // 2 + 1)
    win = np.hanning(n)
    for i in range(0, max(1, len(m) - n), n // 2):
        seg = m[i:i + n]
        if len(seg) < n:
            break
        spec += np.abs(np.fft.rfft(seg * win)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    tot = spec[(f >= 20) & (f < 16000)].sum() + 1e-20
    out = {k: round(100 * spec[(f >= a) & (f < b)].sum() / tot, 1) for k, a, b in BANDS}
    cen = float((spec * f)[(f >= 20) & (f < 16000)].sum() / tot)
    return out, round(cen)


def stereo(x):
    l, r = x[:, 0], x[:, 1]
    mid, side = (l + r) / 2, (l - r) / 2
    corr = float(np.sum(l * r) / (np.sqrt(np.sum(l * l) * np.sum(r * r)) + 1e-20))
    sm = 10 * np.log10((np.sum(side ** 2) + 1e-20) / (np.sum(mid ** 2) + 1e-20))
    return round(corr, 3), round(float(sm), 1)


def frame_db(x, sr=SR, win=0.05):
    k = int(win * sr)
    n = len(x) // k
    r = np.sqrt((x[:n * k].reshape(n, k, -1) ** 2).mean((1, 2)) + 1e-20)
    return 20 * np.log10(r)


def tail_s(x, sr=SR):
    d = frame_db(x, sr)
    if len(d) < 10:
        return 0.0
    ref = np.percentile(d, 90)
    loud = np.where(d > ref - 6)[0]
    if not len(loud):
        return 0.0
    last = loud[-1]
    below = np.where(d[last:] < ref - 40)[0]
    return round((below[0] if len(below) else len(d) - last) * 0.05, 2)


def measure(path):
    x = load(path)
    d = frame_db(x)
    bands, cen = band_shares(x)
    corr, sm = stereo(x)
    I = lufs(x)
    rms = np.sqrt((x ** 2).mean()) + 1e-20
    pk = np.abs(x).max() + 1e-20
    return dict(file=path, dur_s=round(len(x) / SR, 2), lufs=round(I, 1), true_peak_dbtp=round(true_peak(x), 1),
                lra_lu=round(lra(x), 1), crest_db=round(float(20 * np.log10(pk / rms)), 1),
                bands_pct=bands, centroid_hz=cen, stereo_corr=corr, side_to_mid_db=sm,
                silent_pct=round(100 * float((d < -60).mean()), 1), tail_to_minus40_s=tail_s(x))


if __name__ == "__main__":
    args = sys.argv[1:]
    js = None
    if args and args[0] == "--json":
        js, args = args[1], args[2:]
    res = []
    for p in args:
        r = measure(p)
        res.append(r)
        print(json.dumps(r))
    if js:
        json.dump(res, open(js, "w"), indent=1)
