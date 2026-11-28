"""Bake-off: Supertonic 3 (Supertone; code MIT, weights OpenRAIL-M). ONNX Runtime on CPU.
venv: uv venv -p 3.12 v_st && uv pip install supertonic soundfile
Controls: 10 preset voices (M1-M5, F1-F5), speed 0.7-2.0, diffusion steps, inline tags <laugh> <breath> <sigh>.
Casting by measured f0 of the presets (probe sentence): JAX M1 (133 Hz, widest male range), PIP M3 (106 Hz, narrow),
MIRA F5 (162 Hz, lowest female), TEMI F2 (189 Hz, widest range).
Run: OMP_NUM_THREADS=2 HF_HOME=.../voice2/hf python -I bakeoff_supertonic.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from bakeoff_common import run
from supertonic import TTS

THREADS = int(os.environ.get("OMP_NUM_THREADS", "2"))
CAST = {"JAX": "M1", "PIP": "M3", "MIRA": "F5", "TEMI": "F2"}
# (line, take, text as directed, speed)
DIRECTED = [
    ("L1", 1, "Temi! Hi! <breath> I'm about to make a payment—", 1.35),
    ("L1", 2, "Temi! Hi, hi! I'm about to make a payment, I'm—", 1.5),
    ("L2", 1, "She is in Lagos. You are arguing with the past.", 0.95),
    ("L3", 1, "Your record isn't late, Captain. It's... blank.", 1.0),
    ("L4", 1, "GO! I'LL GET THE RAMP!", 1.2),
    ("L4", 2, "Go!! <breath> I'll get the ramp!!", 1.25),
    ("L5", 1, "<breath> It prefers her.", 0.8),
    ("L5", 2, "It... prefers her. <sigh>", 0.75),
    ("L6", 1, "Read it to me. Slowly. <laugh> I want to enjoy my name.", 1.0),
    ("L6", 2, "Read it to me. Slowly. I want to <laugh> enjoy my name.", 0.95),
    ("L7", 1, "<sigh> You gave up your job... for us.", 0.85),
    ("L8", 1, "Good morning! This is Temi in Recoveries! Your vessel is being recovered!", 1.1),
]
tts = TTS(auto_download=True)
SR = getattr(tts, "sample_rate", 44100)
STY = {}


def plan():
    return [(l, t, {"text": tx, "speed": sp, "voice": None}) for l, t, tx, sp in DIRECTED]


def synth(line, take, kw, out):
    v = CAST[line["char"]]
    kw["voice"] = v
    if v not in STY:
        STY[v] = tts.get_voice_style(v)
    wav, _ = tts.synthesize(kw["text"], voice_style=STY[v], lang="en", speed=kw["speed"], total_steps=8)
    sf.write(out, np.asarray(wav, dtype=np.float32).squeeze(), SR)


if __name__ == "__main__":
    run("supertonic3", plan, synth, THREADS, meta={"cast": CAST, "steps": 8, "sr": SR},
        only=sys.argv[1:] or None)
