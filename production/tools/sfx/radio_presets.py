#!/usr/bin/env python3
"""Write radio-voice-presets.json: ffmpeg / sox filter chains for the dialogue editor, and measure
each chain's real response on white noise (so the numbers in the file are tested, not assumed).

    python3 radio_presets.py OUTDIR
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy import signal

SR = 48000

PRESETS = {
    "suit_radio_narrow": dict(
        use="Every voice heard over a SUIT radio (Mira on radio is always filtered; Baron/Jax/Lucía in suits). Exteriors, scenes 9, 21, 24-26, 29.",
        ffmpeg="highpass=f=420,highpass=f=420,lowpass=f=2900,lowpass=f=2900,equalizer=f=1600:t=q:w=1.2:g=3,"
               "acompressor=threshold=0.05:ratio=6:attack=3:release=80:makeup=3,asoftclip=type=tanh:threshold=0.85",
        sox="highpass 420 highpass 420 lowpass 2900 lowpass 2900 equalizer 1600 1.2q 3 compand 0.003,0.08 6:-60,-60,-30,-20,0,-10 -3 -60 0.05",
        ir="radio_suit_narrow_IR.wav",
        mix_with="Add radio_open_channel_hiss_loop at about -26 dB under the voice for 'open' lines only; "
                 "bracket every line with radio_click_on / radio_click_off."),
    "open_channel_wide": dict(
        use="Customs open channel and clamp console, wider and hissier than a suit radio. Scenes 25, 27, 28 (Mira on the open channel, Noakes O.S. on her mic).",
        ffmpeg="highpass=f=300,lowpass=f=5200,lowpass=f=5200,equalizer=f=2500:t=q:w=1:g=2,"
               "acompressor=threshold=0.06:ratio=4:attack=5:release=100:makeup=2,asoftclip=type=tanh:threshold=0.9",
        sox="highpass 300 lowpass 5200 lowpass 5200 equalizer 2500 1q 2 compand 0.005,0.1 4:-60,-60,-30,-22,0,-12 -3 -60 0.05",
        ir="radio_open_wide_IR.wav",
        mix_with="radio_open_channel_hiss_loop at about -22 dB under the voice."),
    "wrist_speaker": dict(
        use="PIP and Lucía from a wrist comm or the desk-lamp speaker (scenes 5, 7, 11, 24, 27). PIP: add his own processing on top; Lucía on the wrist is 'dry and loud'.",
        ffmpeg="highpass=f=350,highpass=f=350,lowpass=f=4500,lowpass=f=4500,equalizer=f=1100:t=q:w=1.5:g=4",
        sox="highpass 350 highpass 350 lowpass 4500 lowpass 4500 equalizer 1100 1.5q 4",
        ir=None, mix_with="none"),
    "earth_call_telephone": dict(
        use="Temi from Lagos and Earth's side of any call (scenes 0, 30): bright, professional, telephone band, slightly compressed.",
        ffmpeg="highpass=f=300,lowpass=f=3400,lowpass=f=3400,acompressor=threshold=0.05:ratio=5:attack=5:release=120:makeup=3",
        sox="highpass 300 lowpass 3400 lowpass 3400 compand 0.005,0.12 5:-60,-60,-30,-20,0,-10 -3 -60 0.05",
        ir=None, mix_with="earth_call_dead_air_1p3s fills each 1.3 s gap."),
    "cab_dry": dict(
        use="Lucía and everyone INSIDE the post-chaise cab: no filter at all (the brief says the cab is dry).",
        ffmpeg="anull", sox="", ir=None, mix_with="rover_cabin_hum_moving_loop underneath."),
}


def run_chain(chain, src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", chain, "-ar", str(SR), "-ac", "1", dst], check=True)


def measure(chain, wav_in):
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "o.wav")
        run_chain(chain, wav_in, dst)
        import wave
        with wave.open(dst) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    f, p = signal.welch(x, SR, nperseg=8192)
    db = 10 * np.log10(p + 1e-20)
    sm = np.convolve(db, np.ones(9) / 9, mode="same")
    mx = sm[(f > 200) & (f < 8000)].max()
    inband = np.where(sm > mx - 6)[0]
    lo, hi = f[inband[0]], f[inband[-1]]
    at = lambda hz: float(round(sm[np.argmin(abs(f - hz))] - mx, 1))
    return dict(minus6db_band_hz=[round(float(lo)), round(float(hi))], rel_db_at_100hz=at(100), rel_db_at_250hz=at(250),
                rel_db_at_1000hz=at(1000), rel_db_at_4000hz=at(4000), rel_db_at_8000hz=at(8000))


def main(out):
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "noise.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anoisesrc=d=8:c=white:r=48000:a=0.3:seed=7", "-c:a", "pcm_s16le", src], check=True)
        res = {}
        for k, v in PRESETS.items():
            m = measure(v["ffmpeg"], src)
            res[k] = dict(v, measured_on_white_noise=m,
                          apply_example=f"ffmpeg -i dialogue.wav -af \"{v['ffmpeg']}\" dialogue_{k}.wav")
    doc = dict(note="Filter presets for the dialogue editor. Measured responses are from white noise through the real ffmpeg chain. "
                    "IR files are linear-phase (21 ms latency): ffmpeg -i dlg.wav -i IR.wav -lavfi afir=dry=0:wet=10:gtype=none dlg_ir.wav. "
                    "Nothing here is a 'good radio'; nobody has listened. Tune by ear.",
               presets=res)
    with open(os.path.join(out, "radio-voice-presets.json"), "w") as f:
        json.dump(doc, f, indent=1)
    for k, v in res.items():
        print(k, v["measured_on_white_noise"])


if __name__ == "__main__":
    main(sys.argv[1])
