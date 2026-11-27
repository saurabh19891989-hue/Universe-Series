"""Objective per-instrument comparison of the free sound sets (nobody can listen here).

For each colour instrument, render the same phrase with FluidR3_GM and GeneralUser GS and
measure: 95 % spectral roll-off (bandwidth), share of energy above 5 kHz, noise floor in the
note gaps, and frame-to-frame spectral flux (a crude 'liveliness' proxy: a static looped
sample scores low). For VPO SFZ instruments, count samples / velocity layers / round robins.
"""
import os
import subprocess
import tempfile
import json

import numpy as np
import pretty_midi
import soundfile as sf

import sulib
import v2mix
import sfzr

PROGS = {"sitar": 104, "koto": 107, "shakuhachi": 77, "taiko": 116, "flute": 73, "strings": 48,
         "horn": 60, "nylon": 24, "choir": 52}


def phrase(prog):
    pm = pretty_midi.PrettyMIDI()
    i = pretty_midi.Instrument(prog)
    t = 0.0
    for p, d in ((62, 1.5), (69, 0.5), (74, 2.5), (72, 0.4), (69, 3.0)):
        if prog == 116:
            p -= 24
        i.notes.append(pretty_midi.Note(100, p, t, t + d))
        t += d + 0.6
    pm.instruments.append(i)
    return pm


def measure(x):
    m = x.mean(axis=1)
    S = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / 48000)
    c = np.cumsum(S) / S.sum()
    roll = float(f[np.searchsorted(c, 0.95)])
    hi = float(10 * np.log10(S[f > 5000].sum() / S.sum() + 1e-12))
    fr = 2048
    frames = [np.abs(np.fft.rfft(m[i:i + fr] * np.hanning(fr))) for i in range(0, len(m) - fr, fr // 2)]
    F = np.array(frames)
    en = F.sum(axis=1)
    act = en > en.max() * 0.05
    flux = float(np.mean(np.abs(np.diff(F[act] / (F[act].sum(axis=1, keepdims=True) + 1e-9), axis=0)).sum(axis=1)))
    rms = np.sqrt(np.convolve(m ** 2, np.ones(2400) / 2400, "same"))
    floor = float(20 * np.log10(np.percentile(rms[rms > 0], 5) + 1e-9) - 20 * np.log10(rms.max() + 1e-9))
    return dict(rolloff95_hz=round(roll), hi5k_db=round(hi, 1), flux=round(flux, 3), floor_db=round(floor, 1))


def render(sf2, pm):
    with tempfile.TemporaryDirectory(dir=sulib.SCRATCH) as td:
        mid, wav = os.path.join(td, "p.mid"), os.path.join(td, "p.wav")
        pm.write(mid)
        subprocess.run(["fluidsynth", "-ni", "-q", "-r", "48000", "-F", wav, "-o", "synth.reverb.active=0",
                        "-o", "synth.chorus.active=0", sf2, mid], check=True)
        return sf.read(wav, always_2d=True)[0]


def main():
    out = {}
    for name, prog in PROGS.items():
        pm = phrase(prog)
        out[name] = {"FluidR3": measure(render(sulib.SF2, pm)), "GeneralUserGS": measure(render(v2mix.GUGS, pm))}
    for name, (lo, sh, _, _) in v2mix.PRESETS.items():
        regs = sfzr.parse_sfz(v2mix.P(lo))
        out["VPO:" + name] = dict(samples=len({r["_path"] for r in regs}),
                                  vel_layers=max(1, len({(r["_lovel"], r["_hivel"]) for r in regs})),
                                  round_robin=max([int(r.get("seq_length", 1)) for r in regs] + [1]),
                                  short_patch=bool(sh))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
