"""worldsynth - Indian and world instruments synthesised in our own code (fully ours, no samples).

Plucked / struck strings (Karplus-Strong, vectorised one period at a time, exact pitch by resampling,
pitch bends = meend / gamaka):
  sitar    bright pluck, strong one-sided 'jawari' bridge buzz (curved-bridge contact), sympathetic taraf
  veena    deeper, softer jawari, long sustain, made for gamaka
  tanpura  very strong jawari, long ring; use tanpura() for the Pa-Sa-Sa-Sa cycle
  santoor  hammered, three detuned courses, bright, long ring
  koto     plectrum, bright, bends;   kora  soft thumb pluck, harp-like;   oud  fretless, warm, short
Wind and bowed (additive harmonic engine with a per-sample pitch curve, breath / bow noise, body formants):
  bansuri  breathy bamboo flute (harmonic-locked breath noise, chiff)
  shehnai  double reed, bright and nasal (also stands for nadaswaram)
  duduk    mellow double reed, dark
  erhu     two-string fiddle: nasal formants, wide vibrato, portamento
  sarangi  bowed, vocal formants + sympathetic resonance
Drums (modal synthesis, stroke = key; see BOLS):
  tabla, mridangam, dholak, djembe, talkdrum (talking drum: pitch follows the bend curve)

Use from v3mix: mix spec {"synth": "<name>", "tonic": "C#4" (drums), "taraf": ["C4","D4",...] (sitar,
sarangi), ...}. Note velocity -> level; pitch bends (cents, sulib Cue.bend) -> slides.
Agents cannot hear: every voice here is a model built from published acoustics, measured, never judged.
"""
import math

import numpy as np
from scipy.signal import fftconvolve

import dsp

SR = 48000


def hz(p):
    return 440.0 * 2 ** ((p - 69) / 12.0)


def note_hz(name):
    import pretty_midi
    return hz(pretty_midi.note_name_to_number(name))


# ------------------------------------------------------------------ plucked strings
def ks(f0, dur, t60=3.0, bright=0.5, excite="pluck", jawari=0.0, rng=None, pos=0.13):
    """Karplus-Strong string. bright: 0 (very bright) .. 1 (dark). jawari: 0..1 one-sided bridge buzz."""
    rng = rng or np.random.default_rng(0)
    N = max(2, int(SR / f0))
    n = int(dur * SR) + N + 2
    y = np.zeros(n, np.float64)
    if excite == "hammer":
        ex = rng.standard_normal(N) * np.exp(-np.arange(N) / (N * 0.15))
    elif excite == "thumb":
        ex = np.convolve(rng.standard_normal(N), np.ones(6) / 6, "same")
    else:   # plectrum / finger: noise with a pluck-position comb
        ex = rng.standard_normal(N)
    k = max(1, int(pos * N))
    ex = ex - np.roll(ex, k)                   # pluck position notch
    ex -= ex.mean()
    y[1:N + 1] = ex / (np.abs(ex).max() + 1e-9)
    g = 10 ** (-3 * (N / SR) / t60)
    s = 0.5 * bright + 0.02
    i = N + 1
    peak = 1.0
    while i < n:
        j = min(n, i + N)
        blk = g * ((1 - s) * y[i - N:j - N] + s * y[i - N - 1:j - N - 1])
        if jawari > 0:
            # curved-bridge contact: the string is stopped on one side above a threshold that tracks
            # its amplitude; the clipped part is folded back -> a bright, evolving 'buzz'
            peak = max(1e-6, 0.995 * peak + 0.005 * np.abs(blk).max())
            h = peak * (1 - 0.6 * jawari)
            over = blk > h
            blk[over] = h - (blk[over] - h) * (0.5 + 0.4 * jawari)
        y[i:j] = blk
        i = j
    out = y[1:]
    f_act = SR / N
    return out, f_act


def resample_pitch(x, ratio):
    """Read x at a time-varying rate (array or scalar), linear interpolation."""
    n_out = int(len(x) / (np.mean(ratio) if np.ndim(ratio) else ratio)) - 2
    if np.ndim(ratio):
        r = np.interp(np.arange(n_out), np.arange(len(ratio)), ratio)
    else:
        r = np.full(n_out, ratio)
    pos = np.concatenate([[0.0], np.cumsum(r[:-1])])
    pos = pos[pos < len(x) - 1]
    i0 = pos.astype(np.int64); fr = pos - i0
    return x[i0] * (1 - fr) + x[i0 + 1] * fr


def sympathetic_ir(freqs, dur=3.0, t60=2.5):
    t = np.arange(int(dur * SR)) / SR
    ir = np.zeros(len(t))
    for f in freqs:
        for k in range(1, 7):
            if k * f < 12000:
                ir += np.sin(2 * np.pi * k * f * t) * np.exp(-6.91 * t / (t60 / (1 + 0.15 * k))) / k
    return ir / (np.sqrt((ir ** 2).sum()) + 1e-9)


PLUCK = {   # t60, bright, excite, jawari, body EQ
    "sitar": dict(t60=3.5, bright=0.18, excite="pluck", jawari=0.75, pos=0.08,
                  eq=[("hp", 120, 0.7), ("peak", 900, 1.0, 3), ("peak", 3000, 1.2, 4), ("hs", 7000, 0.7, 2)]),
    "veena": dict(t60=4.5, bright=0.32, excite="pluck", jawari=0.4, pos=0.12,
                  eq=[("hp", 60, 0.7), ("peak", 250, 0.9, 4), ("peak", 1800, 1.0, 2)]),
    "tanpura": dict(t60=7.0, bright=0.25, excite="thumb", jawari=0.95, pos=0.1,
                    eq=[("hp", 50, 0.7), ("peak", 200, 0.8, 3), ("peak", 2500, 1.0, 3)]),
    "santoor": dict(t60=3.2, bright=0.12, excite="hammer", jawari=0.0, pos=0.11, courses=3,
                    eq=[("hp", 180, 0.7), ("peak", 2500, 1.0, 3), ("hs", 8000, 0.7, 3)]),
    "koto": dict(t60=2.6, bright=0.2, excite="pluck", jawari=0.05, pos=0.15,
                 eq=[("hp", 90, 0.7), ("peak", 600, 1.0, 3), ("peak", 2800, 1.2, 2)]),
    "kora": dict(t60=2.2, bright=0.42, excite="thumb", jawari=0.08, pos=0.2,
                 eq=[("hp", 70, 0.7), ("peak", 180, 0.8, 4), ("peak", 1400, 1.0, 2)]),
    "oud": dict(t60=1.3, bright=0.38, excite="pluck", jawari=0.0, pos=0.18, courses=2,
                eq=[("hp", 60, 0.7), ("peak", 140, 0.8, 5), ("peak", 900, 1.0, -2), ("peak", 2200, 1.0, 2)]),
}


def pluck_note(name, f, dur, vel, bend_fn, t0, rng):
    P = PLUCK[name]
    ring = dur + min(P["t60"], 4.0)
    out = None
    for c in range(P.get("courses", 1)):
        det = 2 ** ((c - (P.get("courses", 1) - 1) / 2) * 3.0 / 1200)    # +-3 cents per course
        x, fa = ks(f * det * 1.003, ring, P["t60"], P["bright"] * (1.2 - vel / 127 * 0.4), P["excite"],
                   P["jawari"], rng, P["pos"])
        base = f * det / fa
        if bend_fn is not None:
            t = t0 + np.arange(int(ring * SR)) / SR
            ratio = base * 2 ** (bend_fn(t) / 1200)
        else:
            ratio = base
        y = resample_pitch(x, ratio)
        out = y if out is None else out[:min(len(out), len(y))] + y[:min(len(out), len(y))]
    # damp at note end only for short-ring instruments (oud) - others ring on
    if name == "oud":
        e = int(dur * SR)
        if e < len(out):
            out[e:] *= np.exp(-np.arange(len(out) - e) / (0.12 * SR))
    return out * (vel / 127) ** 1.6


# ------------------------------------------------------------------ wind and bowed (additive)
WIND = {
    "bansuri": dict(amps=[1, .22, .1, .045, .025, .012], breath=.16, broad=.025, att=.07, vib=(5.0, 14, .35),
                    eq=[("hp", 150, 0.7), ("peak", 2500, 1.0, 1.5)], chiff=.12),
    "shehnai": dict(amps=[1 / k ** .55 for k in range(1, 26)], breath=.03, broad=.01, att=.03, vib=(6.2, 22, .2),
                    eq=[("hp", 250, 0.7), ("peak", 1300, 1.3, 8), ("peak", 2800, 1.4, 6), ("peak", 600, 1.0, -4)]),
    "duduk": dict(amps=[1 / k ** 1.4 for k in range(1, 16)], breath=.05, broad=.012, att=.09, vib=(5.0, 10, .4),
                  eq=[("hp", 100, 0.7), ("peak", 700, 1.0, 5), ("peak", 1800, 1.2, 2), ("hs", 4000, 0.7, -6)]),
    "erhu": dict(amps=[1 / k ** .9 for k in range(1, 31)], breath=.035, broad=.02, att=.08, vib=(6.0, 32, .25),
                 eq=[("hp", 200, 0.7), ("peak", 850, 1.2, 6), ("peak", 2400, 1.3, 5), ("peak", 400, 1.0, -4)]),
    "sarangi": dict(amps=[1 / k ** .8 for k in range(1, 31)], breath=.03, broad=.018, att=.1, vib=(5.5, 26, .3),
                    eq=[("hp", 120, 0.7), ("peak", 700, 1.0, 5), ("peak", 1500, 1.2, 3), ("peak", 3000, 1.2, 4)]),
}


def wind_note(name, f, dur, vel, bend_fn, t0, rng):
    W = WIND[name]
    rel = 0.12
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    cents = bend_fn(t0 + t) if bend_fn is not None else np.zeros(n)
    vr, vd, vdel = W["vib"]
    vib = vd * np.sin(2 * np.pi * vr * t + rng.uniform(0, 6)) * np.clip((t - vdel) / 0.4, 0, 1)
    ff = f * 2 ** ((cents + vib) / 1200)
    ph = np.cumsum(ff) / SR
    x = np.zeros(n)
    fmax = ff.max()
    for k, a in enumerate(W["amps"], 1):
        if k * fmax > 15000:
            break
        lfo = 1 + 0.06 * np.sin(2 * np.pi * rng.uniform(0.3, 1.2) * t + rng.uniform(0, 6))
        x += a * lfo * np.sin(2 * np.pi * k * ph + rng.uniform(0, 6))
    nz = rng.standard_normal(n)
    x += W["breath"] * nz * (0.5 + 0.5 * np.sin(2 * np.pi * ph)) * 2      # harmonic-locked breath / bow
    x += W["broad"] * nz
    env = np.minimum(1, t / W["att"]) * np.clip((dur + rel - t) / rel, 0, 1)
    env *= 0.85 + 0.15 * np.minimum(1, t / (dur + 1e-3))                    # slight swell through the note
    if W.get("chiff"):
        x += W["chiff"] * nz * np.exp(-t / 0.03) * 3
    return x * env * (vel / 127) ** 1.3 * 0.3


# ------------------------------------------------------------------ drums (modal)
BOLS = dict(na=60, tin=61, ta=62, te=63, re=64, ge=65, ke=66, dha=67, dhin=68, ki=69, tun=70, ghe_up=71,
            dhi=72, ti=73, kat=74)
# mridangam: tha=te, dhi=tin, thom=ge, nam=na, chapu=tun ; djembe: bass=ge, tone=tin, slap=na
MRI = dict(tha=63, dhi=61, thom=65, nam=60, chapu=70, thi=63, ka=66)
DJE = dict(bass=65, tone=61, slap=60, mute=63)


def modes(freqs, amps, decays, n, glide=None):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, a, d in zip(freqs, amps, decays):
        if glide is not None:
            ph = np.cumsum(f * glide) / SR
            out += a * np.sin(2 * np.pi * ph) * np.exp(-t / d)
        else:
            out += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return out


def noise_burst(n, dec, lp, rng, hp=None):
    t = np.arange(n) / SR
    x = rng.standard_normal(n) * np.exp(-t / dec)
    b = [("lp", lp, 0.7)] + ([("hp", hp, 0.7)] if hp else [])
    return dsp.eq(x[:, None].astype(np.float32), b)[:, 0]


DRUM = {  # dayan fundamental from tonic; bayan / bass from tonic * low
    "tabla": dict(low=0.35, ring=1.0, glide_amt=0.18), "mridangam": dict(low=0.3, ring=0.8, glide_amt=0.25),
    "dholak": dict(low=0.28, ring=0.5, glide_amt=0.35), "djembe": dict(low=0.25, ring=0.35, glide_amt=0.05),
    "talkdrum": dict(low=0.5, ring=0.6, glide_amt=0.0)}


def drum_stroke(kind, key, f, vel, rng, bend_cents=0.0):
    D = DRUM[kind]
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    fb = f * D["low"]
    rg = D["ring"]
    harm = [1, 2, 3, 4, 5]
    jit = 2 ** (rng.uniform(-6, 6) / 1200)          # stroke-to-stroke pitch variation
    f = f * jit * 2 ** (bend_cents / 1200)

    def right(open_=True, bright=1.0):
        if kind == "djembe":
            fr = [f * r for r in (1, 1.59, 2.14, 2.65)]
            return modes(fr, [1, .5, .3, .2], [0.12 * rg, .08, .05, .04], n)
        amps = [0.5, 1, .6, .35, .22] if bright > 1 else [1, .45, .22, .1, .05]
        dec = [x * rg * (1 if open_ else 0.07) for x in (0.45, 0.9, 0.55, 0.35, 0.25)]
        return modes([f * h for h in harm], amps, dec, n)

    def left(glide_up=0.0):
        g = 1 + D["glide_amt"] * glide_up * (1 - np.exp(-t / 0.12)) + 0.03 * np.exp(-t / 0.02)
        fr = [fb, fb * 1.59, fb * 2.14]
        x = modes(fr, [1, .3, .12], [0.55 * rg, 0.2, 0.12], n, glide=g)
        return x + noise_burst(n, 0.01, 400, rng) * 0.4

    def click(lp=6000, dec=0.004):
        return noise_burst(n, dec, lp, rng) * 0.5

    k = key
    if kind == "talkdrum":
        g = 2 ** (bend_cents / 1200) * np.ones(n)
        x = modes([f * 0.6, f * 0.96, f * 1.3], [1, .35, .15], [0.35, .15, .08], n, glide=g) + click(3000, .006)
    elif k == BOLS["na"]:
        x = right(True, 2) * 0.8 + click(8000)
    elif k in (BOLS["tin"], BOLS["tun"]):
        x = right(True, 1) + click(3000) * 0.5
    elif k == BOLS["ta"]:
        x = right(True, 2) * 0.6 + click(8000) * 1.2
        x *= np.exp(-t / 0.25)
    elif k in (BOLS["te"], BOLS["ti"], BOLS["re"], BOLS["kat"]):
        x = right(False, 1) * 0.6 + click(5000 if k != BOLS["re"] else 3000, 0.012) * 1.4
    elif k == BOLS["ge"]:
        x = left(0.0)
    elif k == BOLS["ghe_up"]:
        x = left(1.0)
    elif k in (BOLS["ke"], BOLS["ki"]):
        x = noise_burst(n, 0.02, 1500, rng) * 1.2 + modes([fb * 1.2], [0.5], [0.04], n)
    elif k == BOLS["dha"]:
        x = right(True, 2) * 0.7 + click(8000) + left(0.3) * 0.9
    elif k in (BOLS["dhin"], BOLS["dhi"]):
        x = right(True, 1) * 0.9 + left(0.3) * 0.9 + click(3000) * 0.5
    else:
        x = right(True, 1)
    if kind == "djembe" and k == BOLS["na"]:      # slap: bright and short
        x = noise_burst(n, 0.03, 9000, rng, hp=700) * 1.5 + right() * 0.4
    return x * (vel / 127) ** 1.5 * 0.5


# ------------------------------------------------------------------ track render
def render_track(spec, pm_inst, length):
    name = spec["synth"]
    rng = np.random.default_rng(spec.get("seed", 7))
    n = int(length * SR) + SR
    out = np.zeros(n)
    bends = sorted((b.time, b.pitch / 8191 * 200.0) for b in pm_inst.pitch_bends)
    import sfzr
    bend_fn = sfzr.bend_curve(bends) if bends else None
    for nt in sorted(pm_inst.notes, key=lambda x: x.start):
        dur = nt.end - nt.start
        if name in PLUCK:
            y = pluck_note(name, hz(nt.pitch), dur, nt.velocity, bend_fn, nt.start, rng)
        elif name in WIND:
            y = wind_note(name, hz(nt.pitch), dur, nt.velocity, bend_fn, nt.start, rng)
        elif name in DRUM:
            f = note_hz(spec.get("tonic", "C4")) if name != "talkdrum" else hz(nt.pitch)
            bc = float(bend_fn(nt.start)) if bend_fn is not None else 0.0
            y = drum_stroke(name, nt.pitch, f, nt.velocity, rng, bc)
        else:
            raise ValueError(name)
        s = int(nt.start * SR)
        e = min(n, s + len(y))
        if e > s:
            out[s:e] += y[:e - s]
    if name in PLUCK or name in DRUM:      # crest control: soft-limit transients above ~20 dB over the body
        act = out[np.abs(out) > 1e-4]
        if len(act):
            lim = 10 * np.sqrt((act ** 2).mean())
            out = np.where(np.abs(out) > lim * 0.7, np.sign(out) * (lim * 0.7 + lim * 0.3 *
                           np.tanh((np.abs(out) - lim * 0.7) / (lim * 0.3))), out)
    x = out.astype(np.float32)[:, None]
    eqb = PLUCK.get(name, WIND.get(name, {})).get("eq", [])
    if name in DRUM:
        eqb = [("hp", 40, 0.7), ("peak", 3500, 1.0, 2)]
    x = dsp.eq(x, eqb)[:, 0]
    if spec.get("taraf") or name == "sarangi":
        fr = [note_hz(p) for p in spec.get("taraf", ["C4", "D4", "E4", "G4", "A4", "C5"])]
        x = x + fftconvolve(x, sympathetic_ir(fr))[:len(x)].astype(np.float32) * spec.get("taraf_gain", 0.35)
    # tiny stereo life: 0.4 ms inter-channel offset + decorrelated early tail would be the room's job
    d = 18
    st = np.stack([x, np.concatenate([np.zeros(d, np.float32), x[:-d]])], 1)
    return st.astype(np.float32)


# ------------------------------------------------------------------ idiomatic sequencing helpers
THEKA = {
    "teental": "dha dhin dhin dha | dha dhin dhin dha | dha tin tin ta | ta dhin dhin dha",
    "keherwa": "dha ge na ti | na ke dhin na",
    "dadra": "dha dhin na | dha tin na",
    "rupak": "tin tin na | dhi na | dhi na",
}


def theka(c, key, name, beat0, cycles, matra=0.5, vel=78, fill_last=True, accent_sam=10, rng_seed=1):
    """Lay a tabla theka on track `key`: one bol per matra (matra length in beats), the sam accented,
    small velocity life, and on the last cycle the final 2 matras become a 'tirakita' fill into sam."""
    import random
    r = random.Random(rng_seed)
    bols = THEKA[name].replace("|", " ").split()
    b = beat0
    for cy in range(cycles):
        for i, bol in enumerate(bols):
            last = fill_last and cy == cycles - 1 and i >= len(bols) - 2
            if last:
                for k, s in enumerate(("te", "re", "ki", "ta")):
                    c.note(key, BOLS[s], b + k * matra / 4, matra / 4, vel - 14 + k * 3 + r.randint(-4, 4), human=False)
            else:
                v = vel + (accent_sam if i == 0 else 0) + r.randint(-6, 6)
                c.note(key, BOLS[bol], b, matra, v)
                if bol in ("dhin", "tin") and r.random() < 0.25:     # occasional 'ke' ghost
                    c.note(key, BOLS["ke"], b + matra / 2, matra / 2, vel - 30)
            b += matra
    return b


def tanpura(c, key, beat0, beats, sa="C3", cycle=4.0, vel=64, pa=True):
    """Pa(lower) - Sa - Sa - Sa(lower) plucks, evenly spaced, each ringing on through the next."""
    import pretty_midi
    s = pretty_midi.note_name_to_number(sa)
    strings = [s - 5 if pa else s - 1, s, s, s - 12]
    b = beat0
    while b < beat0 + beats:
        for i, p in enumerate(strings):
            c.note(key, p, b + i * cycle / 4, cycle * 1.4, vel + (6 if i == 0 else 0), human=True, legato=1.0)
        b += cycle
