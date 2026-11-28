"""Bake-off: Orpheus TTS 3B (Canopy Labs) as a Q4_K_M GGUF through llama.cpp, SNAC 24 kHz decoder in ONNX.
Licence: orpheus-3b-0.1-ft card says Apache-2.0, but it is a fine-tune of Llama 3.2 3B, so the Llama 3.2
Community Licence also applies (commercial use allowed under 700M MAU, "Built with Llama" attribution,
Meta acceptable-use policy). GGUF: isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF (community conversion).
venv (py3.11): uv pip install orpheus-cpp llama-cpp-python soundfile --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
Controls: 8 stock voices (tara leah jess leo dan mia zac zoe, all US English), inline tags <laugh> <chuckle>
<sigh> <cough> <sniffle> <groan> <yawn> <gasp>, punctuation/caps, temperature. No whisper/shout tag.
Usage: python -I bakeoff_orpheus.py <threads> [line ids]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from bakeoff_common import run

THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
import llama_cpp
_Llama = llama_cpp.Llama


class _SmallCtx(_Llama):  # orpheus-cpp passes n_ctx=0 (= 131k-token context) which runs out of RAM here
    def __init__(self, *a, **k):
        k["n_ctx"] = 4096
        super().__init__(*a, **k)


llama_cpp.Llama = _SmallCtx
from orpheus_cpp import OrpheusCpp

m = OrpheusCpp(n_threads=THREADS, verbose=False, lang="en")
CAST = {"JAX": "zac", "PIP": "dan", "MIRA": "leah", "TEMI": "jess"}
DIRECTED = [
    ("L1", 1, "<gasp> Temi! Hi! I'm about to make a payment—"),
    ("L1", 2, "Temi! Hi! Hi! I'm- I'm about to make a payment—"),
    ("L2", 1, "She is in Lagos. You are arguing with the past."),
    ("L3", 1, "Your record isn't late, Captain. It's... blank."),
    ("L4", 1, "GO! I'LL GET THE RAMP!"),
    ("L4", 2, "Go!! I'll get the ramp!!"),
    ("L5", 1, "<sigh> It prefers her."),
    ("L5", 2, "It... prefers her."),
    ("L6", 1, "Read it to me. Slowly. <chuckle> I want to enjoy my name."),
    ("L6", 2, "Read it to me. Slowly. <laugh> I want to enjoy my name."),
    ("L7", 1, "<sigh> You gave up your job... for us."),
    ("L8", 1, "Good morning! This is Temi in Recoveries! Your vessel is being recovered!"),
]


def plan():
    return [(l, t, {"text": tx}) for l, t, tx in DIRECTED]


def synth(line, take, kw, out):
    kw["voice"] = CAST[line["char"]]
    sr, a = m.tts(kw["text"], options={"voice_id": kw["voice"], "temperature": 0.7, "max_tokens": 1500})
    a = np.asarray(a).squeeze()
    a = a.astype(np.float32) / 32768.0 if a.dtype == np.int16 else a.astype(np.float32)
    sf.write(out, a, sr)


if __name__ == "__main__":
    run("orpheus-3b-q4", plan, synth, THREADS, meta={"cast": CAST, "gguf": "isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF"},
        only=sys.argv[2:] or None)
