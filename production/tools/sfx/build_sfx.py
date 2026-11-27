#!/usr/bin/env python3
"""Build every Episode 1 sound effect.

    python3 build_sfx.py [--out DIR] [--review DIR] [--only substr] [--no-mp3]

Writes 48 kHz / 24-bit WAVs (peak -6 dBFS), runs objective checks, writes sfx-index.json and
MP3 review copies (< 400 KB) of the effects flagged review=True.  Re-runnable: output is
deterministic (RNG seeded per effect name).  Needs numpy, scipy, ffmpeg (libmp3lame).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                       # noqa: E402
import sfxlib as S                       # noqa: E402
import sfx_ship, sfx_customs, sfx_rover_suits, sfx_inn_action, sfx_ui_trans   # noqa: E402,F401

DEF_OUT = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/sfx"
DEF_REV = "/home/user/Universe-Series/samples/e01/sfx"


# The 30 effects that get MP3 review copies (selected for script importance and variety)
REVIEW30 = """ship_bridge_roomtone_loop ship_cargohold_tone_loop ship_engine_dies_and_returns
ship_systems_powerdown_sequence coffee_machine_last_gurgle coffee_machine_triumph_click_drip
pip_stamp_thunk_a pip_lens_glow_bed_loop bank_chime bank_jingle shop_door_bell earth_call_dead_air_1p3s
customs_hall_roomtone_loop footsteps_lowg_distant_pattern flipboard_run_down_to_zero
klaxon_seal_the_port_loop clamp_release_far_through_structure rover_cabin_hum_moving_loop
rover_airborne_dropout rover_landing_thud_felt suit_fan_breath_jax_loop radio_click_on
inn_stove_ignite_whup frost_crack_ice_small grapple_fire_hull_thunk line_parting_snap_hull
trunk_knocks_inside_a liftoff_felt_in_cabin smash_cut_main_title_hit
ui_streetlamps_going_out_sequence cut_to_black_soft_tail""".split()


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", path, "-af", "ebur128=peak=none", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", p.stderr)
    try:
        v = float(m[-1])
    except Exception:
        return None
    return v if v > -69.9 else None


def analyse(x, loop, conducted, pulsed=False):
    mono = x.mean(axis=1)
    pk = np.abs(x).max()
    rms = np.sqrt((x ** 2).mean())
    dc = float(np.abs(x.mean(axis=0)).max())
    spec = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    f = np.fft.rfftfreq(len(mono), 1 / S.SR)
    tot = spec.sum() + 1e-30
    cen = float((f * spec).sum() / tot)
    r = dict(peak_dbfs=round(20 * np.log10(pk), 2), rms_dbfs=round(20 * np.log10(rms + 1e-12), 2),
             dc_offset=round(dc, 7), clipped_samples=int((np.abs(x) >= 0.999).sum()),
             spectral_centroid_hz=round(cen, 1),
             energy_above_2k_pct=round(100 * spec[f > 2000].sum() / tot, 3),
             energy_below_80_pct=round(100 * spec[f < 80].sum() / tot, 3),
             nan=bool(np.isnan(x).any()))
    ok = pk < 0.55 and r["clipped_samples"] == 0 and dc < 2e-4 and not r["nan"]
    notes = []
    if not ok:
        notes.append("level/DC/clip check FAILED")
    if conducted and r["energy_above_2k_pct"] > 3.0:
        ok = False
        notes.append("conducted effect has >3% energy above 2 kHz")
    if loop:
        n = len(x)
        j = np.abs(x[0] - x[-1])
        ref = np.percentile(np.abs(np.diff(x, axis=0)), 99.9, axis=0) + 1e-9
        ratio = float((j / ref).max())
        w = int(0.25 * S.SR)
        a = np.sqrt((x[-w:] ** 2).mean() + 1e-12)
        b = np.sqrt((x[:w] ** 2).mean() + 1e-12)
        lvl = abs(20 * np.log10(a / b))
        r["loop_join_step_ratio"] = round(ratio, 3)
        r["loop_join_level_diff_db"] = round(float(lvl), 2)
        if ratio > 1.0 or (lvl > 3.0 and not pulsed):
            ok = False
            notes.append("loop join not clean")
    r["pass"] = bool(ok)
    r["check_notes"] = notes
    return r


def one(e, out_dir):
    R = S.rng_for(e["name"])
    try:
        x = e["fn"](R)
    except Exception as ex_:
        raise RuntimeError("effect %s failed: %r" % (e["name"], ex_)) from ex_
    x = S.finish(x, e["loop"], e["fade_in"], e["fade_out"], -6.0)
    if x.ndim == 1:
        x = x[:, None]
    path = os.path.join(out_dir, e["name"] + ".wav")
    S.write_wav24(path, x)
    y = S.read_wav24(path)                        # analyse what was actually written
    a = analyse(y, e["loop"], e["conducted"], e["pulsed"])
    a["lufs_integrated"] = lufs(path)
    return e, y, path, a


def mp3(path, dest, dur):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", path]
    if dur > 20:
        cmd += ["-t", "20"]
    cmd += ["-ac", "1" if dur > 8 else "2", "-b:a", "96k" if dur > 8 else "128k", "-ar", "44100", dest]
    subprocess.run(cmd, check=True)
    return os.path.getsize(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEF_OUT)
    ap.add_argument("--review", default=DEF_REV)
    ap.add_argument("--only", default="")
    ap.add_argument("--no-mp3", action="store_true")
    ap.add_argument("--plots", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.review, exist_ok=True)
    reg = [e for e in S.REG if a.only in e["name"]]
    names = [e["name"] for e in S.REG]
    assert len(REVIEW30) == 30 and set(REVIEW30) <= set(names)
    for e in S.REG:
        e["review"] = e["name"] in REVIEW30
    assert len(names) == len(set(names)), "duplicate effect names"
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda e: one(e, a.out), reg))
    index = []
    fails = []
    for e, y, path, an in res:
        dur = len(y) / S.SR
        item = dict(file=os.path.basename(path), description=e["desc"], duration_s=round(dur, 3),
                    channels=y.shape[1], loop=e["loop"], group=e["group"],
                    source="SYNTH", licence="Original synthesis by production/tools/sfx (numpy/scipy); no third-party audio; no attribution needed.",
                    suggested_scenes=e["scenes"], conducted_vacuum_rule=e["conducted"], loudness=an)
        # mix suggestion relative to dialogue at -16 LUFS
        if e["bed"] is not None and an["lufs_integrated"] is not None:
            item["mix"] = dict(kind="bed", target_lufs_in_mix=e["bed"], gain_db_to_apply=round(e["bed"] - an["lufs_integrated"], 1),
                               db_below_dialogue=round(-16 - e["bed"], 1))
        else:
            pk = e["peak"] if e["peak"] is not None else -12
            item["mix"] = dict(kind="one-shot", target_peak_dbfs_in_mix=pk, gain_db_to_apply=round(pk - an["peak_dbfs"], 1))
        if e["note"]:
            item["note"] = e["note"]
        index.append(item)
        if not an["pass"]:
            fails.append((e["name"], an["check_notes"], an))
        if e["review"] and not a.no_mp3:
            sz = mp3(path, os.path.join(a.review, e["name"] + ".mp3"), dur)
            item["review_mp3"] = dict(path="samples/e01/sfx/" + e["name"] + ".mp3", bytes=sz)
            assert sz < 400_000, (e["name"], sz)
    with open(os.path.join(a.out, "sfx-index.json"), "w") as f:
        json.dump(dict(episode="E01", sample_rate=S.SR, bit_depth=24, peak_dbfs=-6,
                       generated_by="production/tools/sfx/build_sfx.py", count=len(index), effects=index), f, indent=1)
    print(f"{len(index)} effects; {sum(1 for i in index if i.get('review_mp3'))} review mp3s; {len(fails)} check failures")
    for n, notes, an in fails:
        print("FAIL", n, notes, an["loop_join_step_ratio"] if "loop_join_step_ratio" in an else "", an["energy_above_2k_pct"])
    import radio_presets
    radio_presets.main(a.out)
    if a.plots:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        loops = [(e, y) for e, y, p, an in res if e["loop"]]
        k = len(loops)
        cols = 4
        rows = (k + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(4 * cols, 1.6 * rows))
        for ax, (e, y) in zip(axs.ravel(), loops):
            seg = np.concatenate([y[-1200:, 0], y[:1200, 0]])
            ax.plot(seg, lw=0.5)
            ax.axvline(1200, color="r", lw=0.6)
            ax.set_title(e["name"][:30], fontsize=6)
            ax.tick_params(labelsize=4)
        fig.tight_layout()
        fig.savefig(a.plots, dpi=110)


if __name__ == "__main__":
    main()
