#!/usr/bin/env python3
"""Render s1_themes cues with the v3 sound.
python3 render_v3.py [--mod s2_pieces] OUT_DIR [cue ...]      cues: main_theme title_sting end_card jax mira pip customs
Writes OUT_DIR/<name>.wav (48 kHz 24-bit), OUT_DIR/midi/<name>.mid and prints render time + measurements."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import soundfile as sf
import importlib
import sulib, s1_themes, v3mix, audiometer

args = sys.argv[1:]
mod = s1_themes
if args and args[0] == "--mod":          # e.g. --mod s2_pieces
    mod = importlib.import_module(args[1]); args = args[2:]
out = args[0]
os.makedirs(os.path.join(out, "midi"), exist_ok=True)
sulib.MIDI_DIR = os.path.join(out, "midi")
for key in (args[1:] or list(mod.ALL)):
    t0 = time.time()
    c, mix, meta = mod.ALL[key]()
    try:
        c.write_midi()
    except ValueError as e:      # >16 tracks: MIDI export needs channel sharing; the render does not
        print('midi not written:', e)
    y, _ = v3mix.render(c, mix, meta["duration"], hall=meta["hall"], target=meta["target"],
                        fade_s=meta.get("fade_s", 1.2))
    p = os.path.join(out, c.name + ".wav")
    sf.write(p, y, 48000, subtype="PCM_24")
    m = audiometer.measure(p)
    print(json.dumps(dict(cue=key, name=c.name, dur=meta["duration"], render_s=round(time.time() - t0, 1),
                          lufs=m["lufs"], tp=m["true_peak_dbtp"], lra=m["lra_lu"], corr=m["stereo_corr"],
                          bands=m["bands_pct"])))
