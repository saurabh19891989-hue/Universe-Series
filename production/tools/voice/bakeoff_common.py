"""Shared harness for the 28 Nov expressive-voice bake-off (one venv per engine).
Each engine script defines plan() -> list of (line_id, take, kwargs) and synth(line, take, kwargs, out_wav).
run() renders, times each take, records peak RSS and thread count to <out>/timings.json.
Usage inside an engine script:  from bakeoff_common import run, LINES"""
import json, os, sys, time, resource
import soundfile as sf

REPO = "/home/user/Universe-Series"
SCR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
V2 = f"{SCR}/voice2"
LINES = {l["id"]: l for l in json.load(open(f"{REPO}/production/tools/voice/bakeoff_lines.json"))["lines"]}
KOKORO_DIR = f"{SCR}/e01/dialogue"


def out_dir(engine):
    d = f"{V2}/out/{engine}"
    os.makedirs(d, exist_ok=True)
    return d


def run(engine, plan, synth, threads, meta=None, only=None):
    d = out_dir(engine)
    tp = f"{d}/timings.json"
    rec = json.load(open(tp)) if os.path.exists(tp) else {"engine": engine, "takes": {}}
    rec.update(threads=threads, **(meta or {}))
    for lid, take, kw in plan():
        if only and lid not in only:
            continue
        name = f"{lid}_t{take}"
        out = f"{d}/{name}.wav"
        t0 = time.time()
        c0 = time.process_time()
        try:
            synth(LINES[lid], take, kw, out)
        except Exception as e:  # record and continue
            rec["takes"][name] = {"error": repr(e)[:400]}
            print(name, "ERROR", e, flush=True)
            json.dump(rec, open(tp, "w"), indent=1)
            continue
        wall = time.time() - t0
        cpu = time.process_time() - c0
        dur = sf.info(out).duration
        rec["takes"][name] = dict(wall_s=round(wall, 2), cpu_s=round(cpu, 2), audio_s=round(dur, 2),
                                  rtf_wall=round(wall / max(dur, 0.01), 2), settings=kw,
                                  load1=round(os.getloadavg()[0], 2))
        rec["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2)
        print(name, rec["takes"][name], flush=True)
        json.dump(rec, open(tp, "w"), indent=1)
    return rec
