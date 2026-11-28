#!/usr/bin/env python3
"""mix3 - scene mixer v3: dialogue chain, per-room space, placement that follows the puppets, real + synth
effects, band sidechain ducking, -16 LUFS / -1.5 dBTP master. Agents cannot hear: it only measures.

python3 mix3.py SHOTLIST.json PLAN.json OUT.wav [--report out.json]

SHOTLIST: a toon shot list (episodes/E01/toon-test-shotlist.json style: dialogue[] with who/start_s/src,
          characters.<who>.defaults.x and keys.x for on-screen position, duration_s, vars).
PLAN (JSON; paths may use ${SCRATCH} ${A2} ${REPO}):
  {"room": {"ir": path, "wet_db": -17, "predelay_s": 0.015, "hp_hz": 250, "from_s": 6.8},   # dialogue space
   "speakers": {"jax": {"hp": 90, "eq": [["peak", 300, 1.0, -2], ...], "comp": {"thr_rel": 6, "ratio": 3}}, ...},
   "dialogue": {"line_lufs": -23, "deess": {"f": 5200, "thr_rel": 2}, "pan_scale": 0.35},
   "music": [{"src", "at", "from", "dur", "gain_db", "fade_in", "fade_out"}],
   "beds":  [same + "hp_hz", "lp_hz", "loop": true]          room tones and hums (not ducked)
   "fx":    [same + "pan" | "follow": who, "send_db": -14, "slice": {"thr_db", "min_gap_s", "pick": [...]}]
   "duck":  {"speech_db": -8, "broad_db": -3, "fx_db": -2},
   "master": {"lufs": -16, "tp": -1.5}}
"""
import json
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "music"))
import dsp  # noqa: E402

SR = 48000


def load(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    x = x[:, :2]
    if sr != SR:
        x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
    return x


def mono(path):
    return load(path).mean(1)


def clip_of(c, resolve):
    x = load(resolve(c["src"]))
    x = x[int(c.get("from", 0) * SR):]
    if "dur" in c:
        n = int(c["dur"] * SR)
        if len(x) < n:
            if c.get("loop", True):
                xf = int(0.25 * SR)
                y = x.copy()
                while len(y) < n:   # equal-power crossfade loop
                    r = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
                    y = np.concatenate([y[:-xf], y[-xf:] * np.sqrt(1 - r) + x[:xf] * np.sqrt(r), x[xf:]])
                x = y
            else:
                x = np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
        x = x[:n]
    bands = []
    if c.get("hp_hz"):
        bands.append(("hp", c["hp_hz"], 0.7))
    if c.get("lp_hz"):
        bands.append(("lp", c["lp_hz"], 0.7))
    bands += [tuple(b) for b in c.get("eq", [])]
    x = dsp.eq(x, bands)
    x = x * dsp.db(c.get("gain_db", 0))
    fi, fo = int(c.get("fade_in", 0.005) * SR), int(c.get("fade_out", 0.01) * SR)
    if fi:
        x[:fi] *= np.linspace(0, 1, min(fi, len(x)), dtype=np.float32)[:, None]
    if fo:
        x[-fo:] *= np.linspace(1, 0, min(fo, len(x)), dtype=np.float32)[:, None]
    return x


def add(bus, x, t):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(bus), i + len(x))
    if j > i:
        bus[i:j] += x[:j - i]


def slice_onsets(x, thr_db=-30, min_gap_s=0.25, pre_s=0.01, len_s=0.35):
    """Cut a recorded take (footsteps, cloth, paper) into single events at its onsets."""
    m = np.abs(x).max(1)
    env = dsp.envelope(m, 0.001, 0.03, hop=48, rms=False)
    ref = env.max()
    on = []
    above = env > ref * dsp.db(thr_db)
    i = 0
    n = len(env)
    while i < n:
        if above[i]:
            on.append(i)
            i += int(min_gap_s * SR)
        else:
            i += 48
    out = []
    for o in on:
        a = max(0, o - int(pre_s * SR)); b = min(len(x), a + int(len_s * SR))
        y = x[a:b].copy()
        f = int(0.03 * SR)
        y[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
        out.append(y)
    return out


def x_track(char, total, fps=100):
    """On-screen x (0..1920) per 10 ms from defaults.x and keys.x [[t, x, ...]]."""
    t = np.arange(int(total * fps) + 1) / fps
    d = char.get("defaults", {}).get("x", 960)
    keys = char.get("keys", {}).get("x")
    if not keys:
        return t, np.full(len(t), d, float)
    kt = [k[0] for k in keys]; kx = [k[1] for k in keys]
    # key meaning in the toon engine: value reached at time t (ease ignored here; linear is close enough)
    out = np.interp(t, kt, kx)
    return t, out


def pan_at(char, tt, total, scale):
    t, xs = x_track(char, total)
    x = float(np.interp(tt, t, xs))
    return max(-1, min(1, (x / 1920 - 0.5) * 2 * scale))


def dialogue_chain(clip, spk):
    bands = [("hp", spk.get("hp", 80), 0.7)] + [tuple(b) for b in spk.get("eq", [])]
    y = dsp.eq(clip[:, None] if clip.ndim == 1 else clip, bands)[:, 0]
    return y


def build(shot, plan, resolve, report):
    total = shot["duration_s"]
    n = int(total * SR)
    dlg = np.zeros((n, 2), np.float32); room_in = np.zeros((n, 2), np.float32)
    key = np.zeros(n, np.float32)
    dp = plan.get("dialogue", {})
    lines = shot["dialogue"]
    # per-speaker: chain on the joined speech so compression sees the whole performance
    for who in sorted({l["who"] for l in lines}):
        spk = plan.get("speakers", {}).get(who, {})
        mine = [l for l in lines if l["who"] == who]
        clips = []
        for l in mine:
            x = mono(resolve(l["src"]))
            # line-level loudness match (Kokoro lines vary), then the chain
            L = dsp.loudness(np.stack([x, x], 1)) if len(x) > SR // 2 else None
            if L is not None and L > -60:
                x = x * dsp.db(dp.get("line_lufs", -23) - L)
            clips.append(dialogue_chain(x, spk))
        joined = np.concatenate([np.concatenate([c, np.zeros(int(0.2 * SR), np.float32)]) for c in clips])
        lvl = 20 * np.log10(np.sqrt((joined[np.abs(joined) > 1e-4] ** 2).mean()) + 1e-9)
        cp = spk.get("comp", {"thr_rel": 6, "ratio": 3.0})
        de = dp.get("deess", {"f": 5200, "thr_rel": 2})
        for l, c in zip(mine, clips):
            y = dsp.compressor(c, lvl + cp.get("thr_rel", 6) - 10, cp.get("ratio", 3.0), 0.008, 0.12, 6,
                               makeup_db=cp.get("makeup", 0.0))
            y = dsp.deesser(y, de["f"], lvl + de.get("thr_rel", 2) - 18, 4.0)
            Ly = dsp.loudness(np.stack([y, y], 1)) if len(y) > SR // 2 else None
            if Ly is not None and Ly > -60:      # make-up: back to the line target after the chain
                y = y * dsp.db(dp.get("line_lufs", -23) - Ly)
            p = pan_at(shot["characters"].get(who, {}), l["start_s"] + l["dur"] / 2, total, dp.get("pan_scale", 0.35))
            st = dsp.pan(y, p)
            add(dlg, st, l["start_s"])
            a = int(l["start_s"] * SR)
            key[a:a + len(y)] = np.maximum(key[a:a + len(y)], (np.abs(y) > 1e-3).astype(np.float32))
    # smooth key (speech presence 0..1 with 120 ms hold so gaps between words do not pump)
    hold = int(0.12 * SR)
    from scipy.ndimage import maximum_filter1d
    key = maximum_filter1d(key, hold)
    room = plan.get("room")
    wet = np.zeros((n, 2), np.float32)
    if room:
        ir = dsp.load_ir(resolve(room["ir"]))
        src = dlg.copy()
        if room.get("from_s"):
            src[:int(room["from_s"] * SR)] = 0
        wet = dsp.convolve(dsp.eq(src, [("hp", room.get("hp_hz", 250), 0.7), ("lp", 7000, 0.7)]), ir,
                           room.get("predelay_s", 0.015), room.get("wet_db", -17))
    # music, beds, fx
    mus = np.zeros((n, 2), np.float32); beds = np.zeros((n, 2), np.float32)
    fx = np.zeros((n, 2), np.float32); fx_wet_in = np.zeros((n, 2), np.float32)
    for c in plan.get("music", []):
        add(mus, clip_of(c, resolve), c["at"])
    for c in plan.get("beds", []):
        add(beds, clip_of(c, resolve), c["at"])
    for c in plan.get("fx", []):
        if c.get("slice"):
            sl = c["slice"]
            pieces = slice_onsets(load(resolve(c["src"])), sl.get("thr_db", -30), sl.get("min_gap_s", 0.25),
                                  len_s=sl.get("len_s", 0.35))
            times = sl["times"]
            pick = sl.get("pick") or list(range(len(times)))
            for k, tt in enumerate(times):
                if not pieces:
                    break
                y = pieces[pick[k % len(pick)] % len(pieces)].copy()
                y = dsp.eq(y, [tuple(b) for b in c.get("eq", [])]) * dsp.db(c.get("gain_db", 0) +
                                                                            sl.get("vary_db", [0])[k % len(sl.get("vary_db", [0]))])
                p = pan_at(shot["characters"].get(c["follow"], {}), tt, total, dp.get("pan_scale", 0.35)) \
                    if c.get("follow") else c.get("pan", 0.0)
                y = dsp.place(y, p, 0.3)
                add(fx, y, tt); add(fx_wet_in, y * dsp.db(c.get("send_db", -14)), tt)
            continue
        y = clip_of(c, resolve)
        p = pan_at(shot["characters"].get(c["follow"], {}), c["at"], total, dp.get("pan_scale", 0.35)) \
            if c.get("follow") else c.get("pan", 0.0)
        y = dsp.place(y, p, c.get("width", 0.5))
        add(fx, y, c["at"])
        if c.get("send_db") is not None:
            add(fx_wet_in, y * dsp.db(c["send_db"]), c["at"])
    if room and np.any(fx_wet_in):
        fx += dsp.convolve(fx_wet_in, dsp.load_ir(resolve(room["ir"])), room.get("predelay_s", 0.015))
    du = plan.get("duck", {})
    mus_d, g = dsp.band_duck(mus, key, du.get("speech_db", -8), du.get("broad_db", -3))
    fx_d = fx * dsp.db(du.get("fx_db", -2) * g)[:, None]
    mix = dlg + wet + mus_d + beds + fx_d
    ms = plan.get("master", {"lufs": -16, "tp": -1.5})
    pre = dsp.loudness(mix)
    out = dsp.normalise(mix, ms["lufs"], ms["tp"])
    gain = ms["lufs"] - pre
    buses = {k: (v * dsp.db(gain)).astype(np.float32) for k, v in
             (("dialogue", dlg + wet), ("music", mus_d), ("beds", beds), ("fx", fx_d))}
    report.update(master_gain_db=round(gain, 2), bus_lufs={k: round(dsp.loudness(v), 1) for k, v in buses.items()},
                  final_lufs=round(dsp.loudness(out), 2), final_tp=round(dsp.true_peak_db(out), 2))
    return out, buses, key


def speech_band_snr(lines, buses, sr=SR):
    from scipy.signal import butter, sosfilt
    sos = butter(4, [1000, 4000], btype="band", fs=sr, output="sos")
    bed = buses["music"] + buses["beds"] + buses["fx"]
    res = []
    for l in lines:
        a = int(l["start_s"] * sr); b = int((l["start_s"] + l["dur"]) * sr)
        d = sosfilt(sos, buses["dialogue"][a:b].mean(1)); e = sosfilt(sos, bed[a:b].mean(1))
        res.append(round(10 * np.log10((d ** 2).mean() + 1e-20) - 10 * np.log10((e ** 2).mean() + 1e-20), 1))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    shot = json.load(open(a[0])); plan = json.load(open(a[1])); out = a[2]
    V = dict(shot.get("vars", {}))
    V.update(plan.get("vars", {}))
    V.setdefault("REPO", os.path.abspath(os.path.join(HERE, "..", "..", "..")))

    def resolve(p):
        for k, v in V.items():
            p = p.replace("${" + k + "}", v)
        return p
    rep = {}
    y, buses, key = build(shot, plan, resolve, rep)
    sf.write(out, y, SR, subtype="PCM_24")
    snr = speech_band_snr(shot["dialogue"], buses)
    rep["speech_band_dialogue_to_bed_db"] = dict(min=min(snr), median=float(np.median(snr)), per_line=snr)
    rep["music_present_pct"] = round(100 * float((np.abs(buses["music"]).max(1) > 1e-4).mean()), 1)
    if "--report" in a:
        json.dump(rep, open(a[a.index("--report") + 1], "w"), indent=1)
    print(json.dumps(rep))
