#!/usr/bin/env python3
"""E01 sample 5 (2:42) - final mix: score cues + dialogue (v3 chain) + effects, to the frozen shot list.

python3 sample5_mix.py CUES_DIR OUT_DIR
  CUES_DIR: cue_A.wav cue_B1.wav cue_CUT.wav cue_B2.wav (rendered from production/tools/music/sample5_score.py)
  OUT_DIR : sample5-mix.wav (48 kHz stereo, exactly the shot list's duration), stems music/effects/dialogue,
            sample5-report.json (loudness, true peak, speech-band clarity per line, silence check)
Rules built in (from the showrunner's brief):
  Part A (0-75): customs hall room (Masonic Lodge IR) on voices and effects, hall room tone, foley.
  Part B (77-162.4): VACUUM - no outside sound. Treated radio stems are NOT treated again; we add the
  helmet breathing bed, the private-channel click at 80.198, squelch tails, cloth felt inside the suit.
  144.945-147.945: TRUE SILENCE in the score and effects; only the suit breathing, 8 dB lower.
  Any line under 10 dB speech-band clarity gets the music pulled down around it until it passes.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "music"))
sys.path.insert(0, HERE)
import dsp  # noqa: E402
import fx3  # noqa: E402
import mix3  # noqa: E402

SR = 48000
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SL = json.load(open(os.path.join(REPO, "episodes", "E01", "sample5-shotlist.json")))
SCR = SL["vars"]["SCRATCH"]
E = os.path.join(SCR, "e01", "sfx")
R = os.path.join(SCR, "audio2", "fx_real")
IRD = os.path.join(SCR, "audio2", "libs", "voxengo")
TOTAL = SL["duration_s"]
N = int(round(TOTAL * SR))
SIL = (144.945, 147.945)
STOPS = [(33.0, 35.6), (47.97, 49.95)]
CUES = {"A": 0.0, "B1": 77.0, "CUT": 109.47, "B2": 133.0}
MUSIC_GAIN = {"A": -7.0, "B1": -5.0, "CUT": -6.0, "B2": -4.0}       # dB at placement (cue masters are normalised)


def z():
    return np.zeros((N, 2), np.float32)


def add(bus, x, t, g=0.0):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(N, i + len(x))
    if j > i:
        bus[i:j] += x[:j - i] * dsp.db(g)


def ld(name, d=E):
    return fx3.load(os.path.join(d, name))


def pan_for(line):
    kind = next(s["kind"] for s in SL["shots"] if s["id"] == line["shot"].split()[0])
    who = line["who"]
    if kind.startswith("cu") or kind.startswith("rim_baron") or kind.startswith("rim_jax") or kind == "cutaway":
        return 0.0
    table = {"two_shot": {"jax": -0.3, "mira": 0.3}, "two_shot_noakes": {"noakes": -0.15, "mira": 0.2},
             "wide": {"mira": 0.25, "jax": -0.2, "baron": -0.25}, "walk_track": {"mira": 0.15},
             "rim_two": {"baron": -0.12, "jax": 0.12}}
    return table.get(kind, {}).get(who, 0.0)


def dialogue():
    lines = SL["dialogue"]
    bus = z(); room_in = z(); key = np.zeros(N, np.float32)
    spk_cfg = {"jax": dict(hp=95, eq=[("peak", 220, 1.0, -2.5), ("peak", 3200, 0.9, 3.0), ("hs", 9000, 0.7, 2.0)]),
               "mira": dict(hp=110, eq=[("peak", 350, 1.0, -1.5), ("peak", 3500, 0.9, 2.5), ("hs", 10000, 0.7, 1.5)]),
               "noakes": dict(hp=85, eq=[("peak", 250, 1.0, -2.0), ("peak", 3000, 0.9, 2.5), ("hs", 9000, 0.7, 1.0)])}
    for l in lines:
        x = mix3.mono(l["src"])
        treated = "_treated" in l["src"] or "LAUGH" in l["src"]
        partA = l["start_s"] < 75.0
        if not treated and l["who"] in spk_cfg:
            c = spk_cfg[l["who"]]
            x = dsp.eq(x[:, None], [("hp", c["hp"], 0.7)] + list(c["eq"]))[:, 0]
            lvl = 20 * np.log10(np.sqrt((x[np.abs(x) > 1e-4] ** 2).mean()) + 1e-9)
            x = dsp.compressor(x, lvl + 2, 3.0, 0.008, 0.12, 6)
            x = dsp.deesser(x, 5500, lvl - 16, 4.0)
        L = dsp.loudness(np.stack([x, x], 1)) if len(x) > SR // 2 else -23
        g = -23.0 - L if L > -60 else 0.0
        if "LAUGH" in l["src"]:
            g -= 3.0                                     # the synthetic laugh sits a little under
        if l["who"] == "baron" and partA:
            g -= 1.0                                     # far down the hall (the room send does the distance)
        x = x * dsp.db(g)
        st = dsp.pan(x, pan_for(l))
        add(bus, st, l["start_s"])
        if partA:
            add(room_in, st * (dsp.db(6) if l["who"] == "baron" else 1.0), l["start_s"])
        a = int(l["start_s"] * SR)
        key[a:a + len(x)] = np.maximum(key[a:a + len(x)], (np.abs(x) > 1e-3).astype(np.float32)[:N - a])
    from scipy.ndimage import maximum_filter1d
    key = maximum_filter1d(key, int(0.12 * SR))
    ir = dsp.load_ir(os.path.join(IRD, "Masonic Lodge.wav"))
    wet = dsp.convolve(dsp.eq(room_in, [("hp", 220, 0.7), ("lp", 7000, 0.7)]), ir, 0.018, -15)
    return bus + wet, key, ir


def effects(ir, rng):
    fx = z(); room_in = z(); beds = z(); suit = z()
    # ---------- Part A: hall beds 0-75.3
    def bed(name, d, gain_lufs, hp, frm=0.0):
        x = fx3.load(os.path.join(d, name))[int(frm * SR):]
        n = int(75.4 * SR)
        while len(x) < n:
            x = np.concatenate([x, x])
        x = dsp.eq(x[:n], [("hp", hp, 0.7)])
        x = x * dsp.db(gain_lufs - dsp.loudness(x[:20 * SR]))
        f = int(0.5 * SR); x[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
        x[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR), dtype=np.float32)[:, None]
        return x
    beds[:int(75.4 * SR)] += bed("roomtone_large_interior_ac.wav", R, -48, 70, 3)
    beds[:int(75.4 * SR)] += bed("roomtone_empty_office_hallway.wav", R, -47, 80, 5)
    beds[:int(75.4 * SR)] += bed("customs_hall_roomtone_loop.wav", E, -49, 60)
    beds[:int(75.4 * SR)] += bed("fluorescent_hum_store.wav", R, -55, 110, 10)

    def hit(x, t, rel_db, pan=0.0, dist=0.0, send=-14, var=True):
        y = fx3.vary(x, rng) if var else x
        y = fx3.norm_peak(y, -9 + rel_db)
        y = fx3.place(y, pan, dist)
        add(fx, y, t); add(room_in, y * dsp.db(send), t)
    beep = ld("cargo_scale_beep.wav"); settle = ld("cargo_scale_settle_beeps.wav")
    for t in (0.35, 1.25, 2.05):
        hit(beep, t, -20, -0.35, 0.8, -4)
    hit(settle, 70.2, -22, -0.35, 0.8, -4)
    rub = fx3.first_hit(ld("rubber_stamp_plastic.wav", R), length=0.35)
    for t in (2.75, 5.95):
        hit(rub, t, -15, 0.25, 0.3, -12)                    # Mira stamping papers (small)
    hit(ld("paper_slip_rustle.wav"), 2.55, -18, 0.25, 0.3)
    hit(ld("paper_card_slide_and_tap.wav"), 22.12, -14, 0.0)
    cloth = mix3.slice_onsets(ld("clothing_movement.wav", R), -18, 0.4, len_s=0.4)
    for k, (t, p) in enumerate(((3.35, -0.2), (4.13, -0.2), (15.86, -0.1), (16.78, -0.3), (20.64, 0), (24.65, 0),
                                (26.7, 0), (29.38, 0), (35.67, -0.3), (42.57, 0), (49.93, -0.3))):
        hit(dsp.eq(cloth[k % len(cloth)], [("hp", 200, 0.7)]), t, -21, p)
    for k, (t, p) in enumerate(((22.1, 0), (37.4, 0), (47.85, 0.3), (48.7, 0.3))):
        hit(dsp.eq(cloth[(k + 3) % len(cloth)], [("hp", 260, 0.7)]), t, -23, p)
    hit(dsp.eq(fx3.first_hit(ld("bang_table_desk.wav", R), length=0.3), [("lp", 1800, 0.7)]), 15.88, -17, -0.1)
    # steps: walk pass 7.45-9.45 (left -> right), tracking 9.95-15.45 (centre), exit 50.1-51.45 (receding left)
    steps = mix3.slice_onsets(ld("footsteps_shoes_hard_floor.wav", R), -22, 0.3, len_s=0.32)
    walk = [7.45 + k * 0.5 for k in range(17)]
    for k, t in enumerate(walk):
        p = -0.6 + (t - 7.45) / 2.0 if t < 9.5 else -0.05
        hit(dsp.eq(steps[k % len(steps)], [("hp", 90, 0.7)]), t, -12 if t < 9.5 else -16, p, 0.0, -10)
    for k, t in enumerate((50.1, 50.55, 51.0, 51.45)):
        hit(dsp.eq(steps[(k + 2) % len(steps)], [("hp", 90, 0.7)]), t, -14 - 2 * k, -0.35 - 0.1 * k, 0.15 * k, -8)
    # the screen and the keyboard
    hit(ld("ui_screen_refresh_flicker.wav"), 38.45, -20, 0.1)
    tick = ld("ui_report_read_receipt_tick.wav")
    for k in range(5):
        hit(tick, 38.6 + k * 0.28, -24, 0.1)
    # THE STAMP 48.048: layered stamp + a camera-bump thump + the hall
    st = fx3.stamp(rng)
    add(fx, fx3.place(st, 0.25) * dsp.db(-4), 48.048); add(room_in, st * dsp.db(-8 - 4), 48.048)
    add(fx, fx3.sub(55, 35, 0.4, 0.15, 0.4) * dsp.db(-14), 48.05)
    # notebook: the drawer, the pen (and the pen again while Noakes closes his eyes)
    hit(ld("inlaid_box_lid_open.wav"), 51.45, -18, 0.2)
    pen = ld("pen_scratch_long_signature.wav")
    add(fx, fx3.place(fx3.norm_peak(pen[:int(3.0 * SR)], -27), 0.15), 51.7)
    add(fx, fx3.place(fx3.norm_peak(pen[int(0.5 * SR):int(2.5 * SR)], -30), 0.2), 73.1)
    hit(dsp.eq(cloth[1], [("hp", 120, 0.7), ("lp", 4000, 0.7)]), 54.5, -20, -0.15)        # Noakes bends in
    hit(dsp.eq(ld("breath_in_cold.wav"), [("lp", 3000, 0.7)]), 61.6, -24, -0.15, 0.0, -10)  # his sigh
    # the board: three flaps, then a slow tick under the prayer
    fa, fb = ld("flipboard_flap_single_a.wav"), ld("flipboard_flap_single_b.wav")
    for k, t in enumerate((65.75, 65.97, 66.22)):
        hit(fa if k % 2 == 0 else fb, t, -16, 0.35, 0.3, -8)
    wt = ld("wall_clock_tick.wav")
    for k in range(4):
        hit(wt, 67.0 + k * 1.0, -28, 0.35, 0.5, -8)
    fx += dsp.convolve(room_in, ir, 0.015)
    # ---------- Part B: inside the suits (no outside sound)
    bed_b = fx3.suit_bed(TOTAL - 77.0, "jax") * dsp.db(-2)
    bb = fx3.suit_bed(TOTAL - 77.0, "baron")
    bed_b = bed_b + bb * dsp.db(-9)
    bed_b = dsp.eq(bed_b, [("hp", 60, 0.7)])
    g = bed_b * dsp.db(-44 - dsp.loudness(bed_b[:int(20 * SR)]))
    add(suit, g, 77.0)
    add(fx, fx3.norm_peak(ld("radio_private_channel_click.wav"), -17), 80.198)
    for l in SL["dialogue"]:
        if l["start_s"] > 77.0:
            t = np.arange(int(0.12 * SR)) / SR
            sq = (rng.standard_normal((len(t), 2)) * np.exp(-t / 0.04)[:, None]).astype(np.float32)
            sq = dsp.eq(sq, [("hp", 900, 0.7), ("lp", 3500, 0.7)])
            add(fx, fx3.norm_peak(sq, -34), l["start_s"] + l["dur"] + 0.04)
    sc = [dsp.eq(fx3.vary(c_, rng, 200), [("lp", 1400, 0.7), ("hp", 150, 0.7)]) for c_ in cloth]
    for k, t in enumerate((85.5, 100.2, 101.6, 133.6, 136.55, 153.5)):
        add(fx, fx3.norm_peak(sc[k % len(sc)], -30), t)
    return fx, beds, suit


def clarity(lines, dlg, bed):
    from scipy.signal import butter, sosfilt
    sos = butter(4, [1000, 4000], btype="band", fs=SR, output="sos")
    out = []
    for l in lines:
        a = int(l["start_s"] * SR); b = int((l["start_s"] + l["dur"]) * SR)
        d = sosfilt(sos, dlg[a:b].mean(1)); e = sosfilt(sos, bed[a:b].mean(1))
        out.append(round(float(10 * np.log10((d ** 2).mean() + 1e-20) - 10 * np.log10((e ** 2).mean() + 1e-20)), 1))
    return out


def main(cues_dir, out_dir):
    rng = np.random.default_rng(5)
    os.makedirs(out_dir, exist_ok=True)
    dlg, key, ir = dialogue()
    mus = z()
    for k, t0 in CUES.items():
        x, _ = sf.read(os.path.join(cues_dir, f"cue_{k}.wav"), dtype="float32", always_2d=True)
        add(mus, x, t0, MUSIC_GAIN[k])
    # band ducking: deeper under the cutaway's back-to-back lines (the march speaks in the gaps)
    cut = np.zeros(N, np.float32); cut[int(109.47 * SR):int(128.25 * SR)] = 1
    m1, _ = dsp.band_duck(mus, key, -9.0, -4.0)
    m2, _ = dsp.band_duck(mus, key, -13.0, -7.0)
    mus = m1 * (1 - cut[:, None]) + m2 * cut[:, None]
    # dead stops (music hard out, 25 ms fade) and spot gains
    for t0, t1 in ((33.0, 35.6), (47.97, 49.95)):
        i, j = int(t0 * SR), int(t1 * SR); f_ = int(0.025 * SR)
        mus[i:i + f_] *= np.linspace(1, 0, f_, dtype=np.float32)[:, None]; mus[i + f_:j] = 0
    for t0, t1, gdb in ((37.3, 38.5, -5.0),):          # the almost-smile note: softer
        i, j = int(t0 * SR), int(t1 * SR)
        mus[i:j] *= dsp.db(gdb)
    fx, beds, suit = effects(ir, rng)
    # TRUE SILENCE 144.945-147.945: score and effects to zero (fades 0.3 s out / 0.05 s in); suit bed -8 dB
    env = np.ones(N, np.float32)
    SA, SB = int(SIL[0] * SR), int(SIL[1] * SR)
    f = int(0.3 * SR)
    env[SA - f:SA] = np.linspace(1, 0, f); env[SA:SB] = 0; env[SB:SB + int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    mus *= env[:, None]; fx *= env[:, None]
    se = np.ones(N, np.float32); se[SA:SB] = dsp.db(-8)
    sm = np.convolve(se, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same").astype(np.float32)
    suit *= sm[:, None]
    lines = SL["dialogue"]
    # clarity fix loop: pull the music under any line below 10 dB
    fixes = {}
    for it in range(4):
        cl = clarity(lines, dlg, mus + fx + beds + suit)
        bad = [(l, c) for l, c in zip(lines, cl) if c < 10.5]
        if not bad:
            break
        for l, c in bad:
            need = min(12.0, 11.0 - c)
            a = int((l["start_s"] - 0.15) * SR); b = int((l["start_s"] + l["dur"] + 0.15) * SR)
            g = np.ones(N, np.float32); r = int(0.12 * SR)
            g[a:b] = dsp.db(-need)
            g[a - r:a] = np.linspace(1, dsp.db(-need), r); g[b:b + r] = np.linspace(dsp.db(-need), 1, r)
            mus *= g[:, None]
            fixes[l["id"]] = round(fixes.get(l["id"], 0) + need, 1)
    mix = dlg + mus + fx + beds + suit
    pre = dsp.loudness(mix)
    out = dsp.normalise(mix, -16.0, -2.0)
    gain = dsp.db(dsp.loudness(out) - pre)
    out = out[:N]
    sf.write(os.path.join(out_dir, "sample5-mix.wav"), out, SR, subtype="PCM_24")
    stems = {"music": mus, "effects": fx + beds + suit, "dialogue": dlg}
    for k, v in stems.items():
        sf.write(os.path.join(out_dir, f"sample5-stem-{k}.wav"), (v * gain)[:N].astype(np.float32), SR, subtype="PCM_24")
    cl = clarity(lines, dlg, mus + fx + beds + suit)
    sil = out[SA + int(0.05 * SR):SB - int(0.05 * SR)]
    m_sil = (mus * gain)[SA:SB]
    fx_sil = (fx * gain)[SA:SB]
    rep = dict(duration_s=round(len(out) / SR, 4), samples=len(out), lufs=round(dsp.loudness(out), 2),
               true_peak_dbtp=round(dsp.true_peak_db(out), 2),
               clarity_db={l["id"]: (l["who"], c) for l, c in zip(lines, cl)},
               clarity_min=min(cl), music_pulled_down_db=fixes,
               silence_window=dict(span=SIL, score_peak_dbfs="-inf (digital zero)" if not np.any(m_sil) else
                                   round(float(20 * np.log10(np.abs(m_sil).max())), 1),
                                   effects_peak_dbfs="-inf (digital zero)" if not np.any(fx_sil) else
                                   round(float(20 * np.log10(np.abs(fx_sil).max())), 1),
                                   total_level_dbfs=round(float(20 * np.log10(np.sqrt((sil ** 2).mean()) + 1e-12)), 1)),
               part_lufs={p: round(dsp.loudness(out[int(s * SR):int(e * SR)]), 1) for p, (s, e) in
                          dict(A=(0, 75), B=(77, TOTAL)).items()},
               stem_lufs={k: round(dsp.loudness((v * gain)[:N]), 1) for k, v in stems.items()})
    json.dump(rep, open(os.path.join(out_dir, "sample5-report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
