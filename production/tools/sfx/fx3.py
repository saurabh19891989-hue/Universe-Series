#!/usr/bin/env python3
"""fx3 - effects quality pass using only what we already have (our synth effects + the CC0 recordings).

  vary(x, rng)               every repeat different: +-pitch/time, gain, tiny EQ tilt (no two stamps alike)
  transient(x, attack_db, sustain_db)   envelope-follower transient shaper (punch / tail)
  sub(f0, f1, dur)           pitched sub-bass thump (proper low end that phones still hint at via 2nd harmonic)
  stamp(rng)                 real rubber stamp + our heavy thunk + real desk bang + sub + ink 'tack', shaped
  landing_felt(rng)          vacuum rule: felt through the hull only (< 2 kHz): our felt thud + sub boom +
                             hull groan + low debris rattle
  suit_radio(voice)          helmet + radio: band-limit, helmet resonance, light grit, click on/off, squelch tail
  suit_bed(dur)              breathing + suit fan (the one steady sound outside), open-channel hiss
  lowg_steps(times)          low-gravity steps felt inside a suit: slowed, pitched down, muffled, with the
                             suit-cloth swish of each bound and a soft boot thump
  place(x, pan, dist)        distance: level, HF loss, more room; then pan
  demo(out)                  the 20 s effects demo used in reel 2
Agents cannot hear: levels/filters are set from measurements; listen before using in an episode.
"""
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "music"))
import dsp  # noqa: E402

SR = 48000
SCR = os.environ.get("SU_SCRATCH_ROOT", "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad")
E = os.path.join(SCR, "e01", "sfx")
R = os.path.join(SCR, "audio2", "fx_real")


def load(p):
    x, sr = sf.read(p, dtype="float32", always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    x = x[:, :2]
    if sr != SR:
        x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
    return x


def first_hit(x, pre=0.005, length=0.6, thr_db=-12):
    m = np.abs(x).max(1)
    i = int(np.argmax(m > m.max() * dsp.db(thr_db)))
    a = max(0, i - int(pre * SR))
    y = x[a:a + int(length * SR)].copy()
    f = int(0.03 * SR)
    y[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    return y


def vary(x, rng, cents=60, gain_db=1.5, tilt_db=1.5):
    r = 2 ** (rng.uniform(-cents, cents) / 1200)
    n = int(len(x) / r)
    pos = np.arange(n) * r
    pos = pos[pos < len(x) - 1]
    i0 = pos.astype(int); fr = (pos - i0)[:, None]
    y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    y = dsp.eq(y.astype(np.float32), [("hs", 3000, 0.7, rng.uniform(-tilt_db, tilt_db))])
    return y * dsp.db(rng.uniform(-gain_db, gain_db))


def transient(x, attack_db=4.0, sustain_db=0.0):
    fast = dsp.envelope(x, 0.0005, 0.02, hop=32, rms=False)
    slow = dsp.envelope(x, 0.02, 0.2, hop=32, rms=False)
    ratio = np.clip(fast / (slow + 1e-9), 0, 4)
    g_db = attack_db * np.clip(ratio - 1, 0, 1) + sustain_db * np.clip(1 - (ratio - 1), 0, 1)
    return (x * dsp.db(g_db)[:, None]).astype(np.float32)


def sub(f0=62, f1=38, dur=0.35, dec=0.12, harm=0.25):
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + harm * np.sin(2 * ph)) * np.exp(-t / dec) * np.minimum(1, t / 0.002)
    return np.stack([y, y], 1).astype(np.float32)


def mixin(*parts):
    n = max(len(p) + int(o * SR) for p, o, g in parts)
    out = np.zeros((n, 2), np.float32)
    for p, o, g in parts:
        i = int(o * SR)
        out[i:i + len(p)] += p * dsp.db(g)
    return out


def norm_peak(x, db_=-1.0):
    return x / (np.abs(x).max() + 1e-9) * dsp.db(db_)


def stamp(rng):
    real = vary(first_hit(load(os.path.join(R, "rubber_stamp_plastic.wav")), length=0.35), rng)
    thunk = vary(load(os.path.join(E, "customs_desk_stamp_heavy_a.wav")), rng, 40)
    bang = vary(first_hit(load(os.path.join(R, "bang_table_desk.wav")), length=0.4), rng)
    bang = dsp.eq(bang, [("lp", 2500, 0.7)])
    tack = vary(first_hit(load(os.path.join(R, "stamp_es.wav")), length=0.12), rng)
    x = mixin((norm_peak(real), 0, -3), (norm_peak(thunk), 0.0, -2), (norm_peak(bang), 0.002, -8),
              (sub(70, 42, 0.3, 0.09, 0.5), 0.0, -9), (norm_peak(dsp.eq(tack, [("hp", 2000, 0.7)])), 0.035, -18))
    x = transient(x, 5.0, -2.0)
    return norm_peak(dsp.eq(x, [("hp", 30, 0.7), ("peak", 350, 1.0, -2)]), -1.0)


def landing_felt(rng):
    thud = load(os.path.join(E, "rover_landing_thud_felt.wav"))
    groan = load(os.path.join(E, "grapple_fire_hull_thunk.wav"))
    t = np.arange(int(1.6 * SR)) / SR
    nz = rng.standard_normal((len(t), 2)).astype(np.float32)
    grains = (nz * (rng.random((len(t), 1)) > 0.995) * np.exp(-t / 0.5)[:, None]).astype(np.float32)
    rattle = dsp.eq(grains, [("lp", 1200, 0.7), ("hp", 150, 0.7)])
    x = mixin((norm_peak(thud), 0, -2), (sub(48, 30, 1.2, 0.45, 0.35), 0, -1),
              (norm_peak(vary(groan, rng, 300)), 0.12, -10), (norm_peak(rattle), 0.05, -16))
    x = dsp.eq(x, [("lp", 1800, 0.7), ("lp", 1800, 0.7), ("hp", 22, 0.7)])     # conducted: nothing above ~2 kHz
    return norm_peak(transient(x, 3.0, 1.0), -1.0)


def suit_radio(voice_mono, rng):
    v = np.stack([voice_mono, voice_mono], 1).astype(np.float32)
    v = dsp.eq(v, [("hp", 480, 0.9), ("hp", 480, 0.9), ("lp", 2900, 0.9), ("lp", 2900, 0.9),
                   ("peak", 1800, 1.5, 4.0)])
    v = np.tanh(v / (np.abs(v).max() + 1e-9) * 2.2).astype(np.float32) * 0.5            # radio grit
    # helmet: a 2.5 ms and 4 ms close reflection pair (small resonant shell) mixed in at -9 dB
    d1, d2 = int(0.0025 * SR), int(0.004 * SR)
    hel = np.zeros_like(v)
    hel[d1:] += v[:-d1] * 0.6; hel[d2:] += v[:-d2] * 0.45
    v = v + dsp.eq(hel, [("peak", 1100, 2.0, 5)]) * dsp.db(-9)
    v = dsp.compressor(v, -24, 4, 0.003, 0.08, 4)
    on = load(os.path.join(E, "radio_click_on.wav")); off = load(os.path.join(E, "radio_click_off.wav"))
    t = np.arange(int(0.14 * SR)) / SR
    sq = (rng.standard_normal((len(t), 2)) * np.exp(-t / 0.05)[:, None]).astype(np.float32)
    sq = dsp.eq(sq, [("hp", 900, 0.7), ("lp", 4000, 0.7)])
    return mixin((norm_peak(on), 0, -10), (norm_peak(v), 0.09, -4),
                 (norm_peak(off), 0.09 + len(v) / SR + 0.05, -10), (norm_peak(sq), 0.09 + len(v) / SR + 0.07, -20))


def suit_bed(dur, who="jax"):
    b = load(os.path.join(E, f"suit_fan_breath_{who}_loop.wav"))
    h = load(os.path.join(E, "radio_open_channel_hiss_loop.wav"))
    n = int(dur * SR)
    rep = lambda x: np.concatenate([x] * (n // len(x) + 1))[:n]  # noqa: E731  (loops are exact by design)
    x = rep(b) * dsp.db(-6) + rep(h) * dsp.db(-26)
    f = int(0.4 * SR)
    x[:f] *= np.linspace(0, 1, f, dtype=np.float32)[:, None]; x[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    return x


def lowg_steps(times, rng):
    """In-suit, low gravity: each bound = a slow cloth swish (~0.3 s before) + a muffled boot contact."""
    import mix3
    steps = mix3.slice_onsets(load(os.path.join(R, "footsteps_shoes_hard_floor.wav")), -22, 0.3, len_s=0.4)
    cloth = mix3.slice_onsets(load(os.path.join(R, "clothing_movement.wav")), -18, 0.4, len_s=0.5)
    n = int((max(times) + 1.5) * SR)
    out = np.zeros((n, 2), np.float32)
    for k, t0 in enumerate(times):
        st = steps[k % len(steps)]
        st = resample_poly(st, 4, 3, axis=0).astype(np.float32)          # slower and ~5 semitones lower
        st = vary(st, rng, 80)
        st = dsp.eq(st, [("lp", 1100, 0.7), ("lp", 1100, 0.7), ("peak", 140, 0.9, 4)])
        st = mixin((norm_peak(st), 0, -6), (sub(95, 60, 0.18, 0.05, 0.4), 0.003, -10))
        cl = vary(resample_poly(cloth[k % len(cloth)], 5, 4, axis=0).astype(np.float32), rng, 100)
        cl = dsp.eq(cl, [("hp", 300, 0.7), ("lp", 5000, 0.7)])
        for x_, o, g in ((cl, t0 - 0.32, -16), (st, t0, -4)):
            i = max(0, int(o * SR)); j = min(n, i + len(x_))
            out[i:j] += norm_peak(x_)[:j - i] * dsp.db(g + rng.uniform(-1.5, 1.0))
    return out


def place(x, pan=0.0, dist=0.0):
    """dist 0 (close) .. 1 (far): -10 dB, HF roll-off, narrower."""
    y = dsp.eq(x, [("hs", 5000, 0.7, -8 * dist)]) * dsp.db(-10 * dist)
    return dsp.place(y, pan, 0.5 * (1 - 0.6 * dist))


def demo(out, line_wav):
    rng = np.random.default_rng(28)
    T = 20.0
    mix = np.zeros((int(T * SR), 2), np.float32)

    def add(x, t, g=0.0):
        i = int(t * SR); j = min(len(mix), i + len(x))
        mix[i:j] += x[:j - i] * dsp.db(g)
    # 0-4: the stamp twice (two variations), customs-hall room on the second
    add(place(stamp(rng), 0.2), 0.5, -6)
    s2 = place(stamp(rng), -0.1, 0.3)
    ir = dsp.load_ir(os.path.join(SCR, "audio2", "libs", "voxengo", "Masonic Lodge.wav"))
    add(s2 + dsp.convolve(s2, ir, 0.012, -12), 2.2, -6)
    # 4.5-8: the landing, felt through the hull (vacuum rule: no air sound)
    add(landing_felt(rng), 4.5, -4)
    # 8.5-20: outside, in the suit: breathing bed, a radio line, then low-gravity bounding steps
    add(suit_bed(11.5), 8.5, -18)
    v, _ = sf.read(line_wav, dtype="float32")
    v = v if v.ndim == 1 else v.mean(1)
    add(suit_radio(v, rng), 9.2, -8)
    add(lowg_steps([15.2, 16.1, 17.0, 17.9, 18.8], rng), 0.0, -10)
    y = dsp.normalise(mix, -18.0, -1.5)
    sf.write(out, y, SR, subtype="PCM_24")
    return y


if __name__ == "__main__":
    demo(sys.argv[1], sys.argv[2])
