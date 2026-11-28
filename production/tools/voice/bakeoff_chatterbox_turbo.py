"""Bake-off: Chatterbox-Turbo (Resemble AI; code MIT, weights MIT per HF card; output carries Resemble's
inaudible Perth watermark). PyTorch on CPU.
venv (py3.11): uv pip install chatterbox-tts soundfile "setuptools<81" --extra-index-url https://download.pytorch.org/whl/cpu
Voice: zero-shot from a ~10 s reference made ONLY of our own Kokoro production stems for that character
(voice2/refs/ref_<CHAR>.wav, built from E01 lines not in the test set), so each character keeps the stock
Kokoro voice already cast; no real person's voice is used.
Controls in Turbo: inline tags from its tokenizer: [laugh] [chuckle] [sigh] [gasp] [whispering] [angry]
[sarcastic] [happy] [surprised] [fear] [dramatic] [crying] [groan] [cough] [sniff] [shush] [clear throat]
[narration] [advertisement]; temperature/top_p/top_k; no exaggeration knob (ignored by Turbo).
Usage: [REFSET=qwen] python -I bakeoff_chatterbox_turbo.py <threads> [line ids]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, soundfile as sf
from bakeoff_common import run, V2

THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
torch.set_num_threads(THREADS)
from chatterbox.tts_turbo import ChatterboxTurboTTS

m = ChatterboxTurboTTS.from_pretrained("cpu")
# REFSET=kokoro (default): refs from our Kokoro stems; REFSET=qwen: refs designed by qwen_design_casting.py
REFSET = os.environ.get("REFSET", "kokoro")
REFDIR = {"kokoro": f"{V2}/refs", "qwen": f"{V2}/refs_qwen"}[REFSET]
REF = {c: f"{REFDIR}/ref_{c}.wav" for c in ("JAX", "PIP", "MIRA", "TEMI")}
ENGINE = "chatterbox-turbo" if REFSET == "kokoro" else "chatterbox-turbo-qwenref"
DIRECTED = [
    ("L1", 1, "[fear] Temi! Hi! I'm about to make a payment—"),
    ("L1", 2, "[surprised] [gasp] Temi! Hi! Hi! I'm about to make a payment—"),
    ("L2", 1, "[sarcastic] She is in Lagos. You are arguing with the past."),
    ("L3", 1, "[sarcastic] Your record isn't late, Captain. It's blank."),
    ("L4", 1, "[angry] Go! I'll get the ramp!"),
    ("L4", 2, "[dramatic] GO! I'LL GET THE RAMP!"),
    ("L5", 1, "[whispering] It prefers her."),
    ("L5", 2, "[whispering] [sigh] It prefers her."),
    ("L6", 1, "Read it to me. Slowly. [chuckle] I want to enjoy my name."),
    ("L6", 2, "[happy] Read it to me. Slowly. [laugh] I want to enjoy my name."),
    ("L7", 1, "[sigh] You gave up your job for us."),
    ("L8", 1, "[happy] Good morning! This is Temi in Recoveries. Your vessel is being recovered."),
]
COND = {}


def plan():
    return [(l, t, {"text": tx}) for l, t, tx in DIRECTED]


def synth(line, take, kw, out):
    ch = line["char"]
    torch.manual_seed(2000 + int(line["id"][1:]) * 10 + take)
    if COND.get("cur") != ch:  # conditionals are cached per character
        m.prepare_conditionals(REF[ch])
        COND["cur"] = ch
    w = m.generate(kw["text"], temperature=0.8)
    sf.write(out, w.squeeze(0).cpu().numpy(), m.sr)


if __name__ == "__main__":
    run(ENGINE, plan, synth, THREADS, meta={"refs": REF}, only=sys.argv[2:] or None)
