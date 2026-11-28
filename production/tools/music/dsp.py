"""dsp - small offline audio processing kit (numpy/scipy, 48 kHz stereo float32).

Used by the v3 score renderer (v3mix.py), the dialogue chain and the scene mixer (mix3.py).
  eq(x, [("hp", 80, 0.7), ("peak", 3000, 1.0, +2), ("hs", 10000, 0.7, +2), ...])   RBJ biquads
  compressor(x, thr_db, ratio, attack_s, release_s, knee_db, makeup_db, key=None)
  deesser(x, f_lo, thr_db, ratio)      dynamic cut of the sibilance band only
  load_ir(path, rt_scale=1.0)  convolve(x, ir, predelay_s, wet_db)  early(ir, ms)
  pan(mono, p)  width(stereo, w)  balance(stereo, p)
  band_duck(music, key_env, ...)       sidechain duck, deeper in the speech band than outside it
  envelope(x, attack_s, release_s)     smoothed level follower
  limiter(x, ceiling_dbtp)  loudness(x)  normalise(x, target_lufs, ceiling_dbtp)
All processing is deterministic; nothing here can 'hear' - measure the result with audiometer.py.
"""
import math

import numpy as np
from scipy.signal import fftconvolve, resample_poly, sosfilt, butter

SR = 48000


def db(x):
    return 10 ** (x / 20.0)


# ------------------------------------------------------------------ filters
def biquad(kind, f, q=0.707, gain_db=0.0, sr=SR):
    """RBJ audio-EQ-cookbook biquad as one sos row."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f / sr
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / (2 * q)
    if kind == "peak":
        b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind in ("ls", "hs"):
        s = 2 * math.sqrt(A) * al
        if kind == "ls":
            b = [A * ((A + 1) - (A - 1) * cw + s), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - s)]
            a = [(A + 1) + (A - 1) * cw + s, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - s]
        else:
            b = [A * ((A + 1) + (A - 1) * cw + s), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - s)]
            a = [(A + 1) - (A - 1) * cw + s, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - s]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]; a = np.array(a) / a[0]
    return np.concatenate([b, a])[None, :]


def eq(x, bands, sr=SR):
    """bands: (kind, f, q[, gain_db]) ... applied in series."""
    if not bands:
        return x
    sos = np.concatenate([biquad(b[0], b[1], b[2], b[3] if len(b) > 3 else 0.0, sr) for b in bands])
    return sosfilt(sos, x, axis=0).astype(np.float32)


def lr_split(x, f, sr=SR):
    """Linkwitz-Riley 4th-order crossover: (low, high), low + high sums flat in magnitude."""
    lo = butter(2, f, "low", fs=sr, output="sos"); hi = butter(2, f, "high", fs=sr, output="sos")
    l = sosfilt(lo, sosfilt(lo, x, axis=0), axis=0)
    h = sosfilt(hi, sosfilt(hi, x, axis=0), axis=0)
    return l.astype(np.float32), (-h).astype(np.float32) if False else h.astype(np.float32)


# ------------------------------------------------------------------ dynamics
def envelope(x, attack_s=0.005, release_s=0.08, hop=64, sr=SR, rms=True):
    """Level follower (linear amplitude) evaluated per `hop` samples, returned per sample."""
    m = x if x.ndim == 1 else np.abs(x).max(1) if not rms else np.sqrt((x ** 2).mean(1))
    n = len(m); k = int(math.ceil(n / hop))
    mm = np.pad(np.abs(m) if not rms else m, (0, k * hop - n))
    blk = np.sqrt((mm.reshape(k, hop) ** 2).mean(1)) if rms else mm.reshape(k, hop).max(1)
    a = 1 - math.exp(-hop / (attack_s * sr)); r = 1 - math.exp(-hop / (release_s * sr))
    out = np.empty(k, np.float64); v = 0.0
    for i in range(k):
        b = blk[i]
        v += (b - v) * (a if b > v else r)
        out[i] = v
    return np.repeat(out, hop)[:n]


def gain_computer(level_db, thr_db, ratio, knee_db):
    over = level_db - thr_db
    g = np.zeros_like(level_db)
    if knee_db > 0:
        k = np.abs(over) <= knee_db / 2
        g[k] = (1 / ratio - 1) * (over[k] + knee_db / 2) ** 2 / (2 * knee_db)
        hi = over > knee_db / 2
    else:
        hi = over > 0
    g[hi] = (1 / ratio - 1) * over[hi]
    return g   # dB (<= 0)


def compressor(x, thr_db=-20, ratio=2.0, attack_s=0.01, release_s=0.12, knee_db=6, makeup_db=0.0, key=None):
    """Feed-forward RMS compressor. key: optional sidechain signal (same length)."""
    k = x if key is None else key
    env = envelope(k, attack_s, release_s)
    g = gain_computer(20 * np.log10(env + 1e-9), thr_db, ratio, knee_db) + makeup_db
    return (x * db(g)[:, None] if x.ndim == 2 else x * db(g)).astype(np.float32)


def deesser(x, f_lo=5200, thr_db=-30, ratio=4.0, attack_s=0.002, release_s=0.06):
    """Compress only the sibilance band (>= f_lo), leave the rest untouched."""
    lo, hi = lr_split(x, f_lo)
    env = envelope(hi, attack_s, release_s)
    g = db(gain_computer(20 * np.log10(env + 1e-9), thr_db, ratio, 3))
    return (lo + hi * (g[:, None] if x.ndim == 2 else g)).astype(np.float32)


def band_duck(music, key_env, speech_db=-9.0, broad_db=-4.0, f_lo=900, f_hi=4500, attack_s=0.05, release_s=0.5):
    """Duck `music` (stereo) by key activity 0..1: `speech_db` inside f_lo..f_hi, `broad_db` outside.
    key_env: per-sample 0..1 (e.g. smoothed dialogue presence). Keeps the music's body and air while
    clearing the band where consonants live."""
    lo, rest = lr_split(music, f_lo)
    mid, hi = lr_split(rest, f_hi)
    a = 1 - math.exp(-1 / (attack_s * SR)); r = 1 - math.exp(-1 / (release_s * SR))
    hop = 64
    ke = key_env[::hop]
    sm = np.empty_like(ke); v = 0.0
    aa, rr = 1 - (1 - a) ** hop, 1 - (1 - r) ** hop
    for i, t in enumerate(ke):
        v += (t - v) * (aa if t > v else rr)
        sm[i] = v
    g = np.repeat(sm, hop)[:len(music)]
    if len(g) < len(music):
        g = np.pad(g, (0, len(music) - len(g)), mode="edge")
    gs = db(speech_db * g)[:, None]; gb = db(broad_db * g)[:, None]
    return (lo * gb + mid * gs + hi * gb).astype(np.float32), g


# ------------------------------------------------------------------ space
def load_ir(path, sr=SR, trim_db=-70):
    import soundfile as sf
    ir, isr = sf.read(path, dtype="float32", always_2d=True)
    if ir.shape[1] == 1:
        ir = np.repeat(ir, 2, 1)
    ir = ir[:, :2]
    if isr != sr:
        ir = resample_poly(ir, sr, isr, axis=0).astype(np.float32)
    # trim leading silence and the noise tail
    a = np.abs(ir).max(1)
    on = int(np.argmax(a > a.max() * 0.05))
    ir = ir[max(0, on - 16):]
    e = np.cumsum((ir ** 2).sum(1)[::-1])[::-1]
    edb = 10 * np.log10(e / e[0] + 1e-20)
    end = int(np.argmax(edb < trim_db)) or len(ir)
    ir = ir[:end]
    ir = ir / (np.sqrt((ir ** 2).sum(0, keepdims=True)) + 1e-12)
    return ir.astype(np.float32)


def rt60(ir, sr=SR):
    """T30-based RT60 estimate from the Schroeder curve (mono sum)."""
    e = np.cumsum(((ir ** 2).sum(1))[::-1])[::-1]
    edb = 10 * np.log10(e / e[0] + 1e-20)
    i5, i35 = np.argmax(edb < -5), np.argmax(edb < -35)
    if i35 <= i5:
        return float("nan")
    return float(2.0 * (i35 - i5) / sr)


def early(ir, ms=70, fade_ms=20):
    n = int(ms * SR / 1000); f = int(fade_ms * SR / 1000)
    e = ir[:n].copy()
    e[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    return e / (np.sqrt((e ** 2).sum(0, keepdims=True)) + 1e-12)


def late(ir, ms=60, fade_ms=40):
    """IR with the first `ms` faded out (the tail only)."""
    n = int(ms * SR / 1000); f = int(fade_ms * SR / 1000)
    l = ir.copy()
    l[:n] = 0
    l[n:n + f] *= np.linspace(0, 1, f, dtype=np.float32)[:, None]
    return l / (np.sqrt((l ** 2).sum(0, keepdims=True)) + 1e-12)


def convolve(x, ir, predelay_s=0.0, wet_db=0.0, keep_len=True):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([fftconvolve(x[:, 0], ir[:, 0]), fftconvolve(x[:, 1], ir[:, 1])], 1).astype(np.float32)
    pre = int(predelay_s * SR)
    if pre:
        y = np.concatenate([np.zeros((pre, 2), np.float32), y])
    y *= db(wet_db)
    return y[:len(x)] if keep_len else y


# ------------------------------------------------------------------ image
def pan(mono, p):
    """mono -> stereo, constant power, p in -1..1."""
    th = (p + 1) * math.pi / 4
    return np.stack([mono * math.cos(th), mono * math.sin(th)], 1).astype(np.float32) * math.sqrt(2)


def width(x, w):
    """mid/side width: 0 = mono, 1 = unchanged, >1 wider."""
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1).astype(np.float32)


def place(x, p, w=0.7):
    """Stereo source placed at p (-1..1): narrow it to w, then pan the narrowed image."""
    y = width(x, w)
    th = (p + 1) * math.pi / 4
    gl, gr = math.cos(th) * math.sqrt(2), math.sin(th) * math.sqrt(2)
    m = (y[:, 0] + y[:, 1]) / 2
    # move the mid toward the side; keep the side component as it is
    return np.stack([y[:, 0] - m + m * gl, y[:, 1] - m + m * gr], 1).astype(np.float32)


# ------------------------------------------------------------------ level
def loudness(x):
    import pyloudnorm as pyln
    v = pyln.Meter(SR).integrated_loudness(x.astype(np.float64))
    return float(v) if np.isfinite(v) else -70.0


def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return float(20 * np.log10(np.abs(up).max() + 1e-12))


def limiter(x, ceiling_db=-1.5, release_s=0.08, lookahead_s=0.005):
    """True-peak limiter: gain from 4x-oversampled peaks, lookahead min filter, smooth release."""
    from scipy.ndimage import minimum_filter1d
    up = resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(1)
    pk = np.pad(pk, (0, max(0, 4 * len(x) - len(pk))))[:4 * len(x)].reshape(-1, 4).max(1)
    need = np.minimum(1.0, db(ceiling_db) / np.maximum(pk, 1e-9))
    la = int(lookahead_s * SR)
    g = minimum_filter1d(need, size=2 * la + 1)
    B = 32; nb = int(math.ceil(len(g) / B))
    gb = np.pad(g, (0, nb * B - len(g)), constant_values=1).reshape(nb, B).min(1)
    rb = 1 - math.exp(-B / (release_s * SR)); v = 1.0; sb = np.empty(nb)
    for i in range(nb):
        v = gb[i] if gb[i] < v else v + (gb[i] - v) * rb
        sb[i] = v
    gg = np.minimum(np.repeat(sb, B)[:len(g)], g)
    # smooth the attack edge a little (2 ms) so the limiter does not click
    k = int(0.002 * SR)
    gg = np.minimum(gg, np.convolve(gg, np.ones(k) / k, "same"))
    return (x * gg[:, None]).astype(np.float32)


def normalise(x, target=-16.0, ceiling_db=-1.5):
    y = x.astype(np.float32)
    for _ in range(4):
        y = y * db(target - loudness(y))
        y = limiter(y, ceiling_db - 0.2)
        if abs(loudness(y) - target) < 0.2 and true_peak_db(y) < ceiling_db:
            break
    return y
