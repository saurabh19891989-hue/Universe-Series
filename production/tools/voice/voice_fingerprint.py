#!/usr/bin/env python3
"""Voice fingerprints for Kokoro voices (and processed variants) on one fixed sentence.
Features: median f0, f0 range (p90-p10), spectral centroid, speaking rate (words/s of voiced
speech), 13 MFCC means (formant-ish envelope). Pure numpy.
Library use:  fingerprint(audio, sr, n_words) -> dict ;  distance(a, b, scale) -> float
CLI:          voice_fingerprint.py OUT.json    (all voices, raw)"""
import json, sys, numpy as np

SENTENCE = ("Whatever you were told, I am quite sure the parcel is on the table, "
            "and the Captain knows exactly where it came from. Nobody asked me; I simply noticed.")
NWORDS = len(SENTENCE.split())

def _frames(x, sr, win=0.04, hop=0.01):
    n = int(sr * win); h = int(sr * hop)
    return np.stack([x[i:i + n] for i in range(0, len(x) - n, h)]), n, h

def f0_track(x, sr):
    fr, n, h = _frames(x, sr)
    lo, hi = int(sr / 400), int(sr / 65); out = []
    e = np.sqrt((fr ** 2).mean(1)); thr = 0.15 * np.percentile(e, 90)
    for f, en in zip(fr, e):
        if en < thr: continue
        f = f - f.mean(); a = np.correlate(f, f, "full")[n - 1:]
        if a[0] <= 0: continue
        j = lo + int(np.argmax(a[lo:hi]))
        if a[j] / a[0] > 0.45: out.append(sr / j)
    return np.array(out)

def mel_fb(sr, nfft, nm=26, fmax=8000):
    mel = lambda f: 2595 * np.log10(1 + f / 700); inv = lambda m: 700 * (10 ** (m / 2595) - 1)
    pts = inv(np.linspace(mel(60), mel(fmax), nm + 2)); b = np.floor((nfft + 1) * pts / sr).astype(int)
    fb = np.zeros((nm, nfft // 2 + 1))
    for i in range(1, nm + 1):
        for k in range(b[i - 1], b[i]): fb[i - 1, k] = (k - b[i - 1]) / max(1, b[i] - b[i - 1])
        for k in range(b[i], b[i + 1]): fb[i - 1, k] = (b[i + 1] - k) / max(1, b[i + 1] - b[i])
    return fb

def mfcc_mean(x, sr, ncep=13):
    fr, n, h = _frames(x, sr)
    e = np.sqrt((fr ** 2).mean(1)); fr = fr[e > 0.15 * np.percentile(e, 90)]
    nfft = 1024; sp = np.abs(np.fft.rfft(fr * np.hanning(n), nfft)) ** 2
    ml = np.log(sp @ mel_fb(sr, nfft).T + 1e-10)
    k = np.arange(26); dct = np.cos(np.pi / 26 * (k[None, :] + 0.5) * np.arange(ncep)[:, None])
    return (ml @ dct.T).mean(0), sp, nfft

def fingerprint(x, sr, nwords=NWORDS):
    x = np.asarray(x, dtype=np.float64); x = x / (np.abs(x).max() + 1e-9)
    f0 = f0_track(x, sr)
    mf, sp, nfft = mfcc_mean(x, sr)
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    cent = float(((sp * freqs).sum(1) / (sp.sum(1) + 1e-12)).mean())
    act = np.where(np.abs(x) > 0.02)[0]; dur = (act[-1] - act[0]) / sr
    return dict(f0_median=float(np.median(f0)), f0_range=float(np.percentile(f0, 90) - np.percentile(f0, 10)),
                centroid=cent, rate_wps=float(nwords / dur), duration_s=float(dur), mfcc=[float(v) for v in mf[1:13]])

W = dict(f0_median=4.0, f0_range=1.0, centroid=2.25, rate_wps=1.0, mfcc=2.25)
def vec(fp): return np.array([fp["f0_median"], fp["f0_range"], fp["centroid"], fp["rate_wps"]] + fp["mfcc"])
def scale_from(fps):
    M = np.stack([vec(f) for f in fps]); return M.std(0) + 1e-9
def distance(a, b, sd):
    d = (vec(a) - vec(b)) / sd
    return float(np.sqrt(W["f0_median"] * d[0] ** 2 + W["f0_range"] * d[1] ** 2 + W["centroid"] * d[2] ** 2
                         + W["rate_wps"] * d[3] ** 2 + W["mfcc"] * np.mean(d[4:] ** 2)))

if __name__ == "__main__":
    from kokoro_onnx import Kokoro
    KD = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice/models/kokoro"
    k = Kokoro(f"{KD}/kokoro-v1.0.onnx", f"{KD}/voices-v1.0.bin"); res = {}
    for v in k.get_voices():
        lang = "en-gb" if v[:2] in ("bm", "bf") else "en-us"
        s, sr = k.create(SENTENCE, voice=v, speed=1.0, lang=lang)
        res[v] = fingerprint(s, sr); print(v, round(res[v]["f0_median"]), round(res[v]["centroid"]), round(res[v]["rate_wps"], 2), flush=True)
    json.dump(res, open(sys.argv[1], "w"), indent=1)
