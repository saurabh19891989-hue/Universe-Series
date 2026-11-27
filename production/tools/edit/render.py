#!/usr/bin/env python3
"""Secret Universe edit engine - one command from shot list to finished video.

  python production/tools/edit/render.py SHOTLIST.json --out DIR [--only SHOT_ID ...]
        [--workers 3] [--name NAME] [--review PATH] [--stills T1,T2,... --stills-dir DIR] [--force]

Steps: (1) audio first: dialogue placed from the timing sheet / stems, cues, ducking, loudness,
speech envelopes (they drive PIP's lens); (2) every shot rendered in parallel to its own H.264
segment, cached by a hash of the shot, the engine code, the assets it reads and the speech it
reacts to; (3) stream-copy concat + mux AAC; (4) .srt, render log, optional review copy and stills.
Schema: SCHEMA.md next to this file.
"""
import argparse, glob, hashlib, json, math, os, subprocess, sys, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_SCRATCH = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"

import numpy as np
import audio as A
import engine as E

DEFAULT_FINISH = dict(halation=0.45, split_tone=1.0, pre_gain=1.12, saturation=0.88, vignette=0.38,
                      black_lift=0.012, grain=0.02, weave_px=0.45)


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else json.dumps(p, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


def file_fp(p):
    try:
        st = os.stat(p)
        return f"{p}:{st.st_size}:{int(st.st_mtime)}"
    except OSError:
        return f"{p}:missing"


def strings_in(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings_in(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings_in(v)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def probe_dur(p, stream="v"):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", f"{stream}:0", "-show_entries",
                          "stream=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shotlist"); ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*"); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--name"); ap.add_argument("--review"); ap.add_argument("--review-mb", type=float, default=4.6)
    ap.add_argument("--stills"); ap.add_argument("--stills-dir"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--preview", help="comma list of shot-local fractions (e.g. 0.1,0.9): write graded JPG frames of "
                    "the --only shots (or all) to OUT/preview and stop; no encode")
    a = ap.parse_args()
    t_all = time.time()
    SL = json.load(open(a.shotlist, encoding="utf-8"))
    vars_ = {"REPO": REPO, "SCRATCH": DEFAULT_SCRATCH}
    vars_.update(SL.get("vars", {}))
    resolve = E.make_resolver(vars_)
    for k in list(vars_):
        vars_[k] = resolve(vars_[k])
    outd = os.path.abspath(a.out); os.makedirs(outd, exist_ok=True)
    segd = os.path.join(outd, "segments"); os.makedirs(segd, exist_ok=True)
    work = os.path.join(outd, "work"); os.makedirs(work, exist_ok=True)
    name = a.name or SL.get("name", os.path.splitext(os.path.basename(a.shotlist))[0])
    o = SL.get("output", {})
    W, H, fps = o.get("width", 1920), o.get("height", 1080), o.get("fps", 24)
    finish = dict(DEFAULT_FINISH); finish.update(SL.get("finish", {}))
    enc = dict(crf=o.get("crf", 18), preset=o.get("preset", "medium"))
    log = []

    # ---------------- timeline (frame-exact cut points)
    shots = SL["shots"]
    timeline = []; cum = 0.0
    for sh in shots:
        f0 = int(round(cum * fps)); cum += sh["duration_s"]; f1 = int(round(cum * fps))
        timeline.append(dict(shot=sh, start_s=f0 / fps, f0=f0, frames=f1 - f0))
    total = cum
    print(f"[edit] {len(shots)} shots, {total:.2f}s, {W}x{H}@{fps}", flush=True)

    # ---------------- audio first (envelopes drive lights)
    ta = time.time()
    if not a.no_audio:
        aud = A.build(SL, [(t["shot"].get("audio", {}), t["start_s"]) for t in timeline], total, fps, resolve, work, log)
        env = {k: v.tolist() for k, v in aud["env"].items()}
    else:
        aud = None; env = {}
    t_audio = time.time() - ta

    # ---------------- sync check: every line should start inside the shot that lists it
    sync = []
    if aud:
        for ln in aud["lines"]:
            owner = next((t["shot"]["id"] for t in timeline if t["start_s"] <= ln["start"] < t["start_s"] + t["frames"] / fps), None)
            listed = next((t["shot"]["id"] for t in timeline if ln["id"] in t["shot"].get("audio", {}).get("lines", [])), None)
            sync.append(dict(line=ln["id"], speaker=ln["speaker"], start=round(ln["start"], 3), end=round(ln["start"] + ln["dur"], 3),
                             in_shot=owner, listed_in=listed, ok=(listed is None or listed == owner)))
        bad = [s for s in sync if not s["ok"]]
        for b in bad:
            log.append(f"SYNC WARNING line {b['line']} starts at {b['start']}s in {b['in_shot']} but is listed in {b['listed_in']}")

    # ---------------- shot jobs
    src_hash = sha(*[open(p, "rb").read() for p in sorted(glob.glob(os.path.join(HERE, "*.py")))])
    ctx = dict(W=W, H=H, fps=fps, finish=finish, enc=enc, vars=vars_)
    still_times = [float(x) for x in a.stills.split(",")] if a.stills else []
    still_dir = a.stills_dir or os.path.join(outd, "stills"); os.makedirs(still_dir, exist_ok=True)
    jobs = []; seg_paths = []
    for t in timeline:
        sh = t["shot"]
        assets = sorted(file_fp(resolve(s)) for s in strings_in(sh) if ("/" in s and os.path.exists(resolve(s))) or "${" in s)
        spk = sorted({l.get("env") for l in sh.get("lights", []) if l.get("env")})
        i0, i1 = t["f0"], t["f0"] + t["frames"]
        envs = {k: env[k] for k in spk if k in env}
        env_sl = {k: [round(x, 4) for x in v[i0:i1 + 1]] for k, v in envs.items()}
        key = sha(sh, ctx["finish"], enc, [W, H, fps], src_hash, assets, env_sl, t["frames"])
        seg = os.path.join(segd, f"{sh['id']}-{key}.mp4")
        seg_paths.append(seg)
        need = a.force or not os.path.exists(seg) or bool(a.only and sh["id"] in a.only)
        if need:
            jobs.append(dict(shot=sh, ctx=dict(ctx, env=envs), out=seg, frames=t["frames"], start_s=t["start_s"]))
    if a.preview:
        pv = os.path.join(outd, "preview"); os.makedirs(pv, exist_ok=True)
        fr = [float(x) for x in a.preview.split(",")]
        pj = [dict(shot=t["shot"], ctx=dict(ctx, env={k: env[k] for k in env}), start_s=t["start_s"], fracs=fr, out_dir=pv)
              for t in timeline if not a.only or t["shot"]["id"] in a.only]
        with get_context("spawn").Pool(a.workers) as pool:
            for r in pool.imap_unordered(E.preview_shot, pj):
                print(r, flush=True)
        print("\n".join(log)); return
    print(f"[edit] audio {t_audio:.1f}s; rendering {len(jobs)} of {len(shots)} shots on {a.workers} workers "
          f"({len(shots)-len(jobs)} cached)", flush=True)
    tr = time.time(); results = []
    if jobs:
        jobs.sort(key=lambda j: -j["frames"])          # longest first for better packing
        with get_context("spawn").Pool(a.workers) as pool:
            for r in pool.imap_unordered(E.render_shot, jobs):
                results.append(r)
                print(f"  {r['id']:>5}  {r['dur']:5.2f}s  in {r['secs']:6.1f}s  ({r['secs']/r['dur']:.2f} s/s)", flush=True)
                for m in r["log"]:
                    log.append(f"{r['id']}: {m}")
    t_render = time.time() - tr
    missing = [p for p in seg_paths if not os.path.exists(p)]
    if missing:
        print("[edit] segments missing (use without --only first):", missing); sys.exit(2)

    # ---------------- concat + mux
    lst = os.path.join(work, "concat.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in seg_paths))
    vid = os.path.join(work, "video.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    final = os.path.join(outd, f"{name}.mp4")
    if aud:
        run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", aud["wav"], "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", final])
        A.srt(aud["lines"], os.path.join(outd, f"{name}.srt"))
    else:
        os.replace(vid, final)
    vd, ad = probe_dur(final, "v"), probe_dur(final, "a")

    # ---------------- stills from the finished file (what the viewer gets)
    for x in still_times:
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{x:.3f}", "-i", final, "-frames:v", "1", "-q:v", "3",
             "-vf", "scale=1280:-2:flags=lanczos", os.path.join(still_dir, f"{name}-{x:05.2f}s.jpg")])

    # ---------------- review copy (size-targeted 2-pass)
    if a.review:
        os.makedirs(os.path.dirname(os.path.abspath(a.review)), exist_ok=True)
        ab = 64
        vb = int(a.review_mb * 8 * 1024 / max(vd, 1) - ab - 8)
        vf = "scale=1280:720:flags=lanczos,hqdn3d=1.5:1.5:4:4"
        common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vb}k", "-maxrate", f"{int(vb*1.6)}k",
                  "-bufsize", f"{vb*2}k", "-pix_fmt", "yuv420p", "-vf", vf, "-passlogfile", os.path.join(work, "rv")]
        run(["nice", "ffmpeg", "-y", "-v", "error", "-i", final, *common, "-pass", "1", "-an", "-f", "mp4", "/dev/null"])
        run(["nice", "ffmpeg", "-y", "-v", "error", "-i", final, *common, "-pass", "2", "-c:a", "aac", "-b:a", f"{ab}k",
             "-movflags", "+faststart", a.review])

    # ---------------- credits and log
    credits = sorted({c for sh in shots for c in sh.get("credits", [])} | set(SL.get("credits", [])))
    wall = time.time() - t_all
    rendered_s = sum(r["dur"] for r in results)
    rep = dict(name=name, output=final, duration_video_s=vd, duration_audio_s=ad, shots=len(shots),
               rendered_shots=len(results), render_wall_s=round(t_render, 1), total_wall_s=round(wall, 1),
               render_s_per_video_s_wall=round(t_render / rendered_s, 3) if rendered_s else None,
               render_cpu_s_per_video_s=round(sum(r["secs"] for r in results) / rendered_s, 3) if rendered_s else None,
               per_shot={r["id"]: round(r["secs"] / r["dur"], 2) for r in results}, audio=aud["report"] if aud else None,
               sync=sync, notes=log, credits=credits, finish=finish)
    json.dump(rep, open(os.path.join(outd, f"{name}.log.json"), "w"), indent=1)
    print("\n".join(log))
    print(json.dumps({k: rep[k] for k in ("duration_video_s", "duration_audio_s", "render_wall_s", "total_wall_s",
                                            "render_s_per_video_s_wall", "render_cpu_s_per_video_s", "audio")}, indent=1))


if __name__ == "__main__":
    main()
