"""Render the Episode 1 score (e01_score.py) with the approved v2 sound.

python3 e01_render.py              # all cues
python3 e01_render.py M05 M09      # selected cue ids

Per cue it writes:
  scratchpad/e01/music/<name>.wav                    48 kHz 24-bit master (exact duration)
  scratchpad/e01/music/<name>-under-dialogue.wav     speech band and bass tamed, about -20 LUFS
  scratchpad/e01/music/stems/<name>-<group>.wav      melody / harmony / percussion (pre-bus, sum = mix)
  samples/e01/music/<name>.mp3 (+ -under-dialogue.mp3)  192 kbps review copies (< 3 MB)
  samples/e01/music/midi/<name>.mid, spectrograms/<name>.jpg
and updates samples/e01/music/cues.json (cue sheet + measurements).
Silences listed in a cue's metadata are forced to digital zero and verified.
"""
import json
import os
import subprocess
import sys

import numpy as np
import pretty_midi
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sulib    # noqa: E402
import sfzr     # noqa: E402
import v2mix    # noqa: E402
import e01_score as E   # noqa: E402

SR = 48000
WAV_DIR = os.path.join(os.path.dirname(sulib.SCRATCH.rstrip("/")), "e01", "music")
STEM_DIR = os.path.join(WAV_DIR, "stems")
MP3_DIR = os.path.join(sulib.REPO, "samples", "e01", "music")
MIDI_DIR = os.path.join(MP3_DIR, "midi")
SPEC_DIR = os.path.join(MP3_DIR, "spectrograms")
STING = os.path.join(sulib.OUT_DIR, "v2", "A1-endcard-sting-5s.mp3")
CUESHEET = os.path.join(MP3_DIR, "cues.json")

LIB_VPO = "Virtual Playing Orchestra 3 (SSO / VSCO-2 CE / No Budget Orchestra / Iowa samples)"
LIB_GUGS = "GeneralUser GS v2.0.3"
LIB_FR3 = "FluidR3_GM"
GM_NAMES = {6: "harpsichord", 10: "music box", 24: "nylon guitar", 25: "mandolin (GS bank 16)"}


def describe(mix):
    out = {}
    for trk, spec in mix.items():
        if trk == "drums":
            out[trk] = "percussion: VPO 3 (bass drum, cymbals, snare, triangle) + GeneralUser GS kit (woodblocks, rim, hats)"
        elif spec.get("gm"):
            lib = LIB_FR3 if spec.get("sf2") == "fluidr3" else LIB_GUGS
            prog = spec.get("program")
            name = GM_NAMES.get(prog, "GM program")
            if spec.get("bank") == 8 and prog == 6:
                name = "coupled harpsichord (GS bank 8)"
            out[trk] = f"{name} - {lib}" + (f", detuned {spec['detune']:+d} cents" if spec.get("detune") else "")
        else:
            lo = v2mix.PRESETS[spec["inst"]][0]
            out[trk] = f"{spec['inst']} - {LIB_VPO}: {lo}"
    return out


def loudnorm(inp, out, target):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", inp, "-af",
                        f"loudnorm=I={target}:TP=-1.5:LRA=18:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=18:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", inp, "-af", af + ",aresample=48000",
                    "-ar", "48000", "-c:a", "pcm_f32le", out], check=True)


def shape(x, meta):
    """Exact length, end treatment and digital silences."""
    n = int(round(meta["duration"] * SR))
    if len(x) < n:
        x = np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
    x = x[:n].copy()
    f_end = int(0.008 * SR) if meta.get("end") == "hard" else int(1.5 * SR)
    x[-f_end:] *= np.linspace(1, 0, f_end, dtype=np.float32)[:, None] ** 2
    for a, b in meta.get("silences", []):
        ia, ib = int(round(a * SR)), int(round(b * SR))
        fo = int((0.012 if meta.get("stop_cut") == a else 0.25) * SR)
        x[max(0, ia - fo):ia] *= np.linspace(1, 0, min(fo, ia), dtype=np.float32)[:, None]
        x[ia:ib] = 0.0
        fi = int(0.01 * SR)
        x[ib:ib + fi] *= np.linspace(0, 1, len(x[ib:ib + fi]), dtype=np.float32)[:, None]
    return x


def bus(raw, wav_out, meta, dialogue):
    fx = raw.replace(".wav", "-dlg-fx.wav" if dialogue else "-fx.wav")
    chain = v2mix.DIALOGUE if dialogue else v2mix.BUS
    subprocess.run(["sox", "-q", raw, fx] + chain, check=True)
    tgt = min(-20.0, meta["loud"] - 3.0) if dialogue else meta["loud"]
    ln = fx.replace(".wav", "-ln.wav")
    loudnorm(fx, ln, tgt)
    x, _ = sf.read(ln, dtype="float32", always_2d=True)
    x = shape(x, meta)
    sf.write(wav_out, x, SR, subtype="PCM_24")
    for p in (fx, ln):
        os.remove(p)
    return x


def to_mp3(wav, mp3, dur):
    kbps = 192 if dur * 192000 / 8 < 2.95e6 else 176
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, "-c:a", "libmp3lame",
                    "-b:a", f"{kbps}k", mp3], check=True)
    return kbps


def silence_check(x, meta, label):
    res = []
    for a, b in meta.get("silences", []):
        seg = x[int(round(a * SR)) + int(0.05 * SR):int(round(b * SR)) - int(0.05 * SR)]
        pk = float(np.abs(seg).max()) if len(seg) else 0.0
        res.append({"window_s": [a, b], "source": label,
                    "peak_dbfs": "-inf (digital zero)" if pk == 0 else round(20 * np.log10(pk), 1)})
    return res


def decode(mp3):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                       capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2)


def render(fn):
    c, mix, meta = fn()
    sulib.MIDI_DIR = MIDI_DIR
    for d in (WAV_DIR, STEM_DIR, MP3_DIR, MIDI_DIR, SPEC_DIR):
        os.makedirs(d, exist_ok=True)
    mid = c.write_midi()
    pm = pretty_midi.PrettyMIDI(mid)
    length = max(meta["duration"], pm.get_end_time()) + 0.5
    stems, sends, mixbus = v2mix.build_mix(pm, mix, length, meta.get("rt60", 2.4))
    g = 0.5 / (np.abs(mixbus).max() + 1e-9)
    name = c.name
    raw = os.path.join(sulib.SCRATCH, name + "-raw.wav")
    sfzr.write_wav(raw, mixbus * g)
    files, measures = {}, {}
    for kind, dlg in (("main", False), ("under_dialogue", True)):
        suffix = "" if kind == "main" else "-under-dialogue"
        wav = os.path.join(WAV_DIR, name + suffix + ".wav")
        x = bus(raw, wav, meta, dlg)
        mp3 = os.path.join(MP3_DIR, name + suffix + ".mp3")
        kbps = to_mp3(wav, mp3, meta["duration"])
        st = sulib.analyse(mp3, os.path.join(SPEC_DIR, name + suffix + ".jpg"))
        st["wav_duration_s"] = round(len(x) / SR, 4)
        st["mp3_kbps"] = kbps
        st["mp3_mb"] = round(os.path.getsize(mp3) / 1e6, 2)
        st["silences"] = silence_check(x, meta, "wav") + silence_check(decode(mp3), meta, "mp3")
        files[kind] = {"wav_master": wav, "mp3": os.path.relpath(mp3, sulib.REPO)}
        measures[kind] = st
    # stems: group dry + group reverb, same gain as the mix (pre-bus), exact length, silences zeroed
    groups = {}
    for trk, y in stems.items():
        grp = mix.get(trk, {}).get("group", "harmony")
        groups.setdefault(grp, []).append(trk)
    files["stems"] = {}
    for grp, trks in groups.items():
        dry = sum(stems[t] for t in trks)
        wet_in = sum(stems[t] * sends[t] for t in trks)
        y = (dry + sfzr.reverb(wet_in, rt60=meta.get("rt60", 2.4)) * 0.9) * g if meta.get("rt60", 2.4) > 0 else dry * g
        y = shape(y.astype(np.float32), dict(meta, end=meta.get("end")))
        p = os.path.join(STEM_DIR, f"{name}-{grp}.wav")
        sf.write(p, y, SR, subtype="PCM_24")
        files["stems"][grp] = p
    os.remove(raw)
    # optional: the bed handed into the end sting
    if meta.get("append_sting") and os.path.exists(STING):
        bed, _ = sf.read(files["main"]["wav_master"], dtype="float32", always_2d=True)
        st_ = decode(STING) * 10 ** (-4 / 20)
        xf = int(0.03 * SR)
        out = np.concatenate([bed[:-xf], bed[-xf:] * np.linspace(1, 0, xf)[:, None] + st_[:xf] *
                              np.linspace(0, 1, xf)[:, None], st_[xf:]])
        wav = os.path.join(WAV_DIR, name + "-with-end-sting.wav")
        sf.write(wav, out, SR, subtype="PCM_24")
        mp3 = os.path.join(MP3_DIR, name + "-with-end-sting.mp3")
        to_mp3(wav, mp3, len(out) / SR)
        files["with_end_sting"] = {"wav_master": wav, "mp3": os.path.relpath(mp3, sulib.REPO),
                                   "duration_s": round(len(out) / SR, 3)}
    entry = {k: meta[k] for k in ("id", "title", "scenes", "duration", "key", "tempo", "hits", "motifs")}
    entry.update({k: meta[k] for k in ("silences", "loops", "held_note", "note") if k in meta})
    entry["name"] = name
    entry["midi"] = os.path.relpath(mid, sulib.REPO)
    entry["instruments"] = describe(mix)
    entry["files"] = files
    entry["measurements"] = measures
    entry["mix"] = {"target_lufs_main": meta["loud"], "target_lufs_under_dialogue": min(-20.0, meta["loud"] - 3.0),
                    "hall_rt60_s": meta.get("rt60", 2.4)}
    return entry


def main(ids):
    sheet = {"episode": "E01 - The Parcel Nobody Ordered", "cues": []}
    if os.path.exists(CUESHEET):
        try:
            sheet = json.load(open(CUESHEET))
        except Exception:
            pass
    by_id = {c["id"]: c for c in sheet.get("cues", [])}
    for fn in E.CUES:
        c, mix, meta = fn()
        if ids and meta["id"] not in ids:
            continue
        entry = render(fn)
        by_id[entry["id"]] = entry
        m = entry["measurements"]["main"]
        print(entry["id"], entry["name"], m["wav_duration_s"], m["lufs_I"], m["true_peak_dBTP"],
              m["samples_at_full_scale"], [s["peak_dbfs"] for s in m["silences"]], flush=True)
    sheet["cues"] = [by_id[k] for k in sorted(by_id)]
    sheet["libraries"] = {
        LIB_VPO: "http://virtualplaying.com/virtual-playing-orchestra/ - 'I enforce no restrictions on using this "
                 "library to make music, even for commercial purposes'",
        LIB_GUGS: "https://github.com/mrbumpy409/GeneralUser-GS - 'You may use GeneralUser GS without restriction "
                  "for your own music creation, private or commercial.'",
        LIB_FR3: "MIT licence (Frank Wen), Debian package fluid-soundfont-gm",
    }
    sheet["notes"] = ("Hit points are in seconds from the cue start and were placed against the table-read timings "
                      "(samples/tableread/E01/timings.json, lines.csv). Nobody has listened to these files.")
    json.dump(clean(sheet), open(CUESHEET, "w"), indent=1, allow_nan=False)


def clean(o):
    """Strict JSON: non-finite floats (silent windows) become null."""
    if isinstance(o, float):
        return o if np.isfinite(o) else None
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


if __name__ == "__main__":
    main(set(sys.argv[1:]))
