#!/usr/bin/env python3
"""Mouth cues for every dialogue line of a shot list.

usage: lipsync.py SHOTLIST.json OUT.json [--rhubarb PATH]
For each dialogue line (`dialogue.lines`: id, speaker, src, start_s, text) runs Rhubarb Lip Sync
(PocketSphinx, with the line's text as dialog hint) and stores mouth cues (A-H, X) on the episode
timeline, plus a 48 Hz loudness envelope (0..1) for lens glow and head energy.
If Rhubarb is missing, cues are derived from amplitude and spectrum instead (fallback).
"""
import json, os, subprocess, sys, tempfile, concurrent.futures as cf
import numpy as np, soundfile as sf

def expand(p, v):
    for k, x in v.items():
        p = p.replace("${%s}" % k, x)
    return p

def envelope(y, sr, hz=48):
    hop = sr // hz
    n = len(y) // hop
    if n == 0:
        return np.zeros(1)
    fr = y[: n * hop].reshape(n, hop)
    rms = np.sqrt((fr ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    e = np.clip((db + 50) / 38, 0, 1)
    return e

def fallback_cues(y, sr):
    """Amplitude + spectral centroid -> shapes. X closed, B small, C mid, D wide, E/F round."""
    hop = sr // 48
    n = len(y) // hop
    cues = []
    for i in range(n):
        fr = y[i * hop:(i + 1) * hop]
        rms = np.sqrt((fr ** 2).mean() + 1e-12)
        db = 20 * np.log10(rms + 1e-9)
        spec = np.abs(np.fft.rfft(fr * np.hanning(len(fr))))
        f = np.fft.rfftfreq(len(fr), 1 / sr)
        cen = (spec * f).sum() / (spec.sum() + 1e-9)
        if db < -42: s = "X"
        elif db < -32: s = "B"
        elif cen < 900: s = "E" if db < -24 else "F"
        elif db < -24: s = "C"
        else: s = "D"
        cues.append({"start": i / 48, "end": (i + 1) / 48, "value": s})
    return cues

def run_line(ln, rh, tmp):
    y, sr = sf.read(ln["src"], always_2d=True)
    y = y.mean(1)
    out = {"id": ln["id"], "speaker": ln["speaker"], "start_s": ln["start_s"], "dur": len(y) / sr,
           "env": [round(float(x), 3) for x in envelope(y, sr)]}
    cues = None
    lip_src = ln["src"]
    if lip_src.endswith("_treated.wav") and os.path.exists(lip_src.replace("_treated.wav", ".wav")):
        lip_src = lip_src.replace("_treated.wav", ".wav")  # dry stem reads better
    if rh and os.path.exists(rh):
        txt = os.path.join(tmp, ln["id"] + ".txt")
        open(txt, "w").write(ln.get("text", "").replace("—", " "))
        js = os.path.join(tmp, ln["id"] + ".json")
        p = subprocess.run([rh, "-f", "json", "-q", "-d", txt, "--extendedShapes", "GHX", lip_src, "-o", js],
                           capture_output=True, text=True)
        if p.returncode == 0:
            cues = json.load(open(js))["mouthCues"]
            out["method"] = "rhubarb"
    if cues is None:
        cues = fallback_cues(y, sr)
        out["method"] = "amplitude"
    out["cues"] = [{"t0": round(c["start"], 3), "t1": round(c["end"], 3), "v": c["value"]} for c in cues]
    return out

def main():
    sl, outp = sys.argv[1], sys.argv[2]
    rh = sys.argv[sys.argv.index("--rhubarb") + 1] if "--rhubarb" in sys.argv else None
    d = json.load(open(sl))
    v = dict(d.get("vars", {}))
    v.setdefault("REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    lines = []
    for ln in d["dialogue"]["lines"]:
        ln = dict(ln); ln["src"] = expand(ln["src"], v); lines.append(ln)
    tmp = tempfile.mkdtemp()
    with cf.ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda l: run_line(l, rh, tmp), lines))
    json.dump({"lines": res}, open(outp, "w"))
    print(len(res), "lines;", sum(r["method"] == "rhubarb" for r in res), "by rhubarb")

if __name__ == "__main__":
    main()
