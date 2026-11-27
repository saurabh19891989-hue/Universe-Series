"""Shared primitives for the Episode 1 sound-effects generators.

Everything here is synthesis from numpy/scipy only: no samples, no third-party audio.
All randomness is seeded from the effect name, so a re-run reproduces identical files.
"""
import zlib
import wave
import numpy as np
from scipy import signal

SR = 48000
REG = []          # registry of effects, filled by the @sfx decorator


def sfx(name, desc, scenes, loop=False, review=False, conducted=False, bed=None,
        peak=None, fade_in=0.003, fade_out=0.03, group="", note="", pulsed=False):
    """Register an effect.  The function receives (R) a seeded numpy Generator and
    returns a mono (n,) or stereo (n,2) float array.

    loop       True = exact loop; the function must return exactly the loop length.
    conducted  True = vacuum rule: sound carried by the structure only (must be low-passed).
    bed        suggested integrated loudness (LUFS) of a bed in the final mix.
    peak       suggested peak level (dBFS) of a one-shot in the final mix.
    """
    def deco(fn):
        REG.append(dict(name=name, fn=fn, desc=desc, scenes=scenes, loop=loop, review=review,
                        conducted=conducted, bed=bed, peak=peak, fade_in=fade_in,
                        fade_out=fade_out, group=group, note=note, pulsed=pulsed))
        return fn
    return deco


def rng_for(name):
    return np.random.default_rng(zlib.crc32(name.encode()) & 0xFFFFFFFF)


# ---------------------------------------------------------------- basics
def T(d):
    return np.arange(int(round(d * SR))) / SR


def N(d):
    return int(round(d * SR))


def white(R, d):
    return R.standard_normal(N(d))


def pink(R, d):
    n = N(d)
    X = np.fft.rfft(R.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    X = X / np.sqrt(f / f[1])
    return np.fft.irfft(X, n)


def brown(R, d):
    x = np.cumsum(R.standard_normal(N(d)))
    return hp(x, 20, 1)


def _sos(kind, f, o):
    return signal.butter(o, f, kind, fs=SR, output="sos")


def lp(x, f, o=4):
    return signal.sosfilt(_sos("low", min(f, 23000), o), x, axis=0)


def hp(x, f, o=4):
    return signal.sosfilt(_sos("high", f, o), x, axis=0)


def bp(x, lo, hi, o=2):
    return signal.sosfilt(_sos("band", [lo, min(hi, 23000)], o), x, axis=0)


def peakfilt(x, f, q):
    b, a = signal.iirpeak(f, q, fs=SR)
    return signal.lfilter(b, a, x, axis=0)


def ex(n, tau):
    """exponential decay envelope of n samples or d seconds (float => seconds)"""
    if isinstance(n, float):
        n = N(n)
    return np.exp(-np.arange(n) / SR / tau)


def ad(d, a, tau):
    """attack (linear a s) then exp decay; d seconds long"""
    t = T(d)
    e = np.exp(-t / tau)
    na = max(1, N(a))
    e[:na] *= np.linspace(0, 1, na)
    return e


def ramp(d, a, b):
    return np.linspace(a, b, N(d))


def sine(f, d, ph=0.0):
    return np.sin(2 * np.pi * f * T(d) + ph)


def phase_of(fcurve):
    return 2 * np.pi * np.cumsum(fcurve) / SR


def harm(fcurve, nh=8, rolloff=1.0, odd=False, R=None):
    """harmonic stack following a frequency curve"""
    ph = phase_of(fcurve)
    out = np.zeros_like(ph)
    for h in range(1, nh + 1):
        if odd and h % 2 == 0:
            continue
        out += np.sin(h * ph) / h ** rolloff
    return out


def modal(freqs, amps, taus, d, R=None, rnd_phase=False):
    t = T(d)
    out = np.zeros_like(t)
    for f, a, tau in zip(freqs, amps, taus):
        ph = (R.uniform(0, 2 * np.pi) if (rnd_phase and R is not None) else 0.0)
        out += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + ph)
    return out


def smooth_noise(R, d, rate):
    """slowly wandering 0..1 control signal, `rate` Hz"""
    n = N(d)
    pts = max(4, int(d * rate) + 3)
    y = R.uniform(0, 1, pts)
    x = np.linspace(0, pts - 1, n)
    return np.interp(x, np.arange(pts), y)


def pf(f, L):
    """quantise a frequency so it has a whole number of cycles in L seconds"""
    return max(1, round(f * L)) / L


# ---------------------------------------------------------------- placing
def silence(d, ch=1):
    return np.zeros(N(d)) if ch == 1 else np.zeros((N(d), 2))


def place(buf, x, at, gain=1.0, pan=0.0, wrap=False):
    """add x into buf at time `at` (s).  pan -1..1 for stereo buf.  wrap=True folds
    past-the-end samples back onto the start (for seamless loop beds)."""
    i = N(at)
    n = len(buf)
    if x.ndim == 1 and buf.ndim == 2:
        gl = np.cos((pan + 1) * np.pi / 4)
        gr = np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * gl, x * gr], axis=1) * np.sqrt(2)
    x = x * gain
    m = len(x)
    if i >= n and not wrap:
        return buf
    if wrap:
        idx = (np.arange(m) + i) % n
        np.add.at(buf, idx, x)
    else:
        m2 = min(m, n - i)
        if m2 > 0:
            buf[i:i + m2] += x[:m2]
    return buf


def fold(x, L):
    """fold the tail beyond L samples back onto the head (circular render)."""
    out = x[:L].copy()
    k = 0
    pos = L
    while pos < len(x):
        seg = x[pos:pos + L]
        out[:len(seg)] += seg
        pos += L
    return out


def mk_loop(x, L, xf):
    """equal-power crossfade loop of UNCORRELATED material.  x must be >= L+xf samples;
    returns exactly L samples whose end continues seamlessly into its start."""
    out = x[:L].copy()
    w = np.arange(xf) / xf
    wi = np.sin(w * np.pi / 2)
    wo = np.cos(w * np.pi / 2)
    if x.ndim == 2:
        wi, wo = wi[:, None], wo[:, None]
    out[:xf] = x[:xf] * wi + x[L:L + xf] * wo
    return out


def noise_loop(fn, R, L, xf=0.5):
    """call fn(R, duration) -> array (mono/stereo); return an exact L-second loop"""
    x = fn(R, L + xf)
    return mk_loop(x, N(L), N(xf))


def to_stereo(x, width=0.0, R=None, delay_ms=0.0):
    if x.ndim == 2:
        return x
    r = np.roll(x, int(delay_ms * SR / 1000)) if delay_ms else x
    return np.stack([x, r], axis=1)


# ---------------------------------------------------------------- reverb
def make_ir(R, rt60, damp=6000, pre=0.012, d=None, tilt=1.0):
    d = d or rt60 * 1.15
    n = N(d)
    t = np.arange(n) / SR
    env = np.exp(-6.9078 * t / rt60)
    irs = []
    for _ in range(2):
        g = R.standard_normal(n) * env
        # darker as it decays: crossfade a bright and a dark version
        dark = lp(g, max(300, damp / 4), 2)
        bright = lp(g, damp, 2)
        k = np.clip(t / (rt60 * 0.6), 0, 1) ** tilt
        irs.append(bright * (1 - k) + dark * k)
    ir = np.stack(irs, axis=1)
    ir[:N(pre)] = 0
    ir /= np.sqrt((ir ** 2).sum(axis=0)).max()
    return ir


def reverb(x, R, rt60=2.0, wet=0.3, damp=6000, pre=0.012, tilt=1.0, tail=True):
    """convolution reverb with a synthetic stereo IR.  returns stereo."""
    ir = make_ir(R, rt60, damp, pre, tilt=tilt)
    xm = x if x.ndim == 1 else x.mean(axis=1)
    wl = signal.fftconvolve(xm, ir[:, 0])
    wr = signal.fftconvolve(xm, ir[:, 1])
    n = len(wl) if tail else len(xm)
    wetx = np.stack([wl[:n], wr[:n]], axis=1)
    # normalise wet energy to equal the dry energy, then scale
    dry = np.zeros((n, 2))
    if x.ndim == 1:
        dry[:len(xm), 0] = xm[:n]
        dry[:len(xm), 1] = xm[:n]
    else:
        dry[:len(xm)] = x[:n]
    e_dry = np.sqrt((xm ** 2).sum() + 1e-12)
    e_wet = np.sqrt((wetx ** 2).sum() / 2 + 1e-12)
    wetx = wetx * (e_dry / e_wet)
    return dry * (1 - wet) + wetx * wet


def circ(fn, x):
    """apply a causal filter function to an exactly periodic loop without a start transient"""
    L = len(x)
    return fn(np.tile(x, (3, 1)) if x.ndim == 2 else np.tile(x, 3))[L:2 * L]


def periodic_reverb(x, R, rt60, wet, damp=5000):
    """reverb of an exactly periodic loop: tile x three times, convolve, take the middle
    copy -> the result is itself an exact loop (steady-state response)."""
    L = len(x)
    y = reverb(np.tile(x, 3), R, rt60=rt60, wet=wet, damp=damp, tail=False)
    return y[L:2 * L]


# ---------------------------------------------------------------- common one-shots
def click(R, f=3000, bw=2.0, tau=0.003, d=0.05):
    n = white(R, d)
    x = bp(n, f / bw, min(f * bw, 22000), 2) * ex(N(d), tau)
    return x


def thud(R, f0=70, f1=40, tau=0.12, d=0.5, body=0.35, bodyf=600):
    t = T(d)
    f = f1 + (f0 - f1) * np.exp(-t / 0.04)
    s = np.sin(phase_of(f)) * np.exp(-t / tau)
    n = lp(white(R, d), bodyf, 3) * np.exp(-t / (tau * 0.5)) * body
    return s + n


def tone_burst(f, d, a=0.005, r=0.02, harm_amp=()):
    t = T(d)
    x = np.sin(2 * np.pi * f * t)
    for k, h in enumerate(harm_amp, start=2):
        x += h * np.sin(2 * np.pi * f * k * t)
    e = np.ones_like(t)
    na, nr = N(a), N(r)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] = np.linspace(1, 0, nr)
    return x * e


def bell_voice(f, d, tau, ratios=(1, 2.0, 3.0, 4.2), amps=(1, .5, .3, .15), R=None):
    return modal([f * r for r in ratios], amps, [tau / (1 + 0.6 * i) for i in range(len(ratios))], d, R, True)


# ---------------------------------------------------------------- output
def write_wav24(path, x):
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[:, None]
    q = np.ascontiguousarray(np.round(np.clip(x, -1, 1) * 8388607).astype("<i4"))
    raw = q.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(raw)


def read_wav24(path):
    with wave.open(path, "rb") as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = np.frombuffer(w.readframes(n), np.uint8)
    assert sw == 3
    raw = raw.reshape(-1, 3)
    v = (raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16))
    v = np.where(v >= 1 << 23, v - (1 << 24), v)
    return (v.astype(np.float64) / 8388607).reshape(-1, ch)


def finish(x, loop, fade_in, fade_out, peak_db=-6.0):
    """DC-remove, fade (non-loops), normalise to peak_db."""
    x = np.asarray(x, dtype=np.float64)
    x = np.nan_to_num(x)
    x = x - x.mean(axis=0)
    if not loop:
        n = len(x)
        fi, fo = min(N(fade_in), n // 4), min(N(fade_out), n // 3)
        e = np.ones(n)
        if fi:
            e[:fi] = np.linspace(0, 1, fi) ** 1.0
        if fo:
            e[-fo:] = np.linspace(1, 0, fo) ** 1.5
        x = x * (e[:, None] if x.ndim == 2 else e)
        x = x - x.mean(axis=0)
    pk = np.abs(x).max()
    x = x * (10 ** (peak_db / 20) / max(pk, 1e-12))
    return x
