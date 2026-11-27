#!/usr/bin/env python3
"""Render the Episode 1 data visuals.  One command:

    python3 production/tools/datavis/make_all.py                 # everything
    python3 production/tools/datavis/make_all.py --only atlas pip # selected visuals
    python3 production/tools/datavis/make_all.py --quick --only warrant   # 2-second smoke test

Outputs: OUT (clips, ProRes alpha, mattes, cues.json) and STILLS (small JPGs + contact sheet).
Override with env DATAVIS_OUT / DATAVIS_STILLS; fonts cache with DATAVIS_FONTS.
Needs: python3 with pillow numpy opencv-python-headless (scipy, tifffile for the laser map), ffmpeg.
"""
import os, sys, json, argparse, glob, shutil
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib

OUT = os.environ.get("DATAVIS_OUT", "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/datavis")
STILLS = os.environ.get("DATAVIS_STILLS", "/home/user/Universe-Series/samples/e01/datavis")
RAW = os.path.join(OUT, "_stills_png")


def registry():
    import visuals_a as A, visuals_b as B, visuals_c as C
    return {
        "atlas": A.atlas_map, "pip": A.pip_report, "engine": A.engine_readouts, "screens": A.screens_dying,
        "coffee": A.coffee_light, "bank": A.bank_call, "cargo": A.cargo_screen,
        "licence": B.customs_licence, "deletion": B.customs_deletion, "wrist": B.wrist_message,
        "regulation": B.regulation, "board": B.flip_board, "clock": B.clocks, "clamp": B.clamp_console,
        "warrant": B.warrant, "map": C.laser_map, "titles": C.titles,
    }


def _job(args):
    key, idx, quick, skip = args
    spec = registry()[key]()[idx]
    dvlib.render(spec, OUT, RAW, quick=quick, skip_existing=skip)
    return key, spec.name, spec.dur, spec.cues, spec.notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--skip-existing", action="store_true", help="do not re-render clips already finished")
    a = ap.parse_args()
    reg = registry()
    keys = a.only or list(reg)
    jobs = []
    for k in keys:
        n = len(reg[k]())
        jobs += [(k, j, a.quick, a.skip_existing) for j in range(n)]
    os.makedirs(OUT, exist_ok=True)
    with Pool(a.procs) as p:
        res = p.map(_job, jobs, chunksize=1)
    cues_path = os.path.join(OUT, "cues.json")
    allc = json.load(open(cues_path)) if os.path.exists(cues_path) else {}
    for k, n, dur, cues, notes in res:
        allc[n] = {"duration_s": dur, "cues_s": cues, "notes": notes}
        print("%-44s %6.1fs" % (n, dur))
    json.dump(allc, open(cues_path, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
