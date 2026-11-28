#!/usr/bin/env python3
"""Mix TEST 3 audio from the shotlist: dialogue stems, score and effects, music ducked under
speech, normalised to the target integrated loudness with a true-peak guard.
usage: mix_audio.py SHOTLIST.json OUT.wav
Agents cannot hear: this only measures. Nobody has listened to the result.
"""
import json, sys, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import resample_poly
SL = json.load(open(sys.argv[1])); out = sys.argv[2]
S = SL["vars"]["SCRATCH"]; T = SL["vars"]["TOON"]
def path(p): return p.replace("${SCRATCH}", S).replace("${TOON}", T)
SR = 48000; N = int(SL["duration_s"] * SR)
def load(p):
    a, sr = sf.read(path(p), always_2d=True)
    if a.shape[1] == 1: a = np.repeat(a, 2, 1)
    if sr != SR: a = resample_poly(a, SR, sr, axis=0)
    return a.astype(np.float64)
def place(bus, c):
    a = load(c["src"])
    fr = int(c.get("from", 0) * SR); a = a[fr:]
    if "dur" in c:
        n = int(c["dur"] * SR)
        if len(a) < n:  # loop
            a = np.concatenate([a] * (n // max(1, len(a)) + 1))
        a = a[:n]
    a = a * 10 ** (c.get("gain_db", 0) / 20)
    fi, fo = int(c.get("fade_in", 0.01) * SR), int(c.get("fade_out", 0.02) * SR)
    if fi: a[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo: a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    s = int(c["at"] * SR); e = min(N, s + len(a))
    if e > s: bus[s:e] += a[:e - s]
dia = np.zeros((N, 2)); mus = np.zeros((N, 2)); sfx = np.zeros((N, 2))
for ln in SL["dialogue"]: place(dia, {"src": ln["src"], "at": ln["start_s"], "gain_db": 0})
for c in SL["audio"]["music"]: place(mus, c)
for c in SL["audio"]["sfx"]: place(sfx, c)
# duck music under speech (60 ms attack, 450 ms release)
act = np.zeros(N)
for ln in SL["dialogue"]:
    s = int(ln["start_s"] * SR); e = int((ln["start_s"] + ln["dur"]) * SR); act[s:e] = 1
g = np.ones(N); lo = 10 ** (SL["audio"]["duck_music_db"] / 20); cur = 1.0
step = 480
for i in range(0, N, step):
    tgt = lo if act[i:i + step].any() else 1.0
    k = 1 - np.exp(-step / SR / (0.06 if tgt < cur else 0.45))
    nxt = cur + (tgt - cur) * k; g[i:i + step] = np.linspace(cur, nxt, len(g[i:i + step])); cur = nxt
mix = dia + mus * g[:, None] + sfx
meter = pyln.Meter(SR)
# normalise, then true-peak guard (4x oversampled, soft limit to -1.6 dBTP); repeat to converge
ceil = 10 ** (-1.6 / 20)
for _ in range(4):
    L0 = meter.integrated_loudness(mix)
    mix *= 10 ** ((SL["audio"]["loudness"] - L0) / 20)
    tp = np.abs(resample_poly(mix, 4, 1, axis=0)).max()
    if tp > ceil:
        x = mix / ceil; over = np.abs(x) > 0.8
        x[over] = np.sign(x[over]) * (0.8 + 0.2 * np.tanh((np.abs(x[over]) - 0.8) / 0.2))
        mix = x * ceil * 0.985
L1 = meter.integrated_loudness(mix)
sf.write(out, mix.astype(np.float32), SR, subtype="PCM_24")
print(json.dumps({"integrated_lufs": round(L1, 2), "true_peak_dbtp": round(20 * np.log10(np.abs(resample_poly(mix, 4, 1, axis=0)).max()), 2)}))
