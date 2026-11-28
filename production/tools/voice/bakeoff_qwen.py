"""Bake-off: Qwen3-TTS (Alibaba Qwen; code and weights Apache-2.0). PyTorch on CPU.
venv (py3.12): uv pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cpu ; uv pip install qwen-tts soundfile
Modes:
  design  -> Qwen3-TTS-12Hz-1.7B-VoiceDesign: voice = free-text description (our own invented character
             descriptions, no real person), acting = the line direction appended to the description.
  custom  -> Qwen3-TTS-12Hz-{0.6B,1.7B}-CustomVoice: fixed preset speaker + `instruct` style direction.
Usage: python -I bakeoff_qwen.py design <threads> [fp32|bf16] [line ids...]
       python -I bakeoff_qwen.py custom17 <threads> ...
Seeds are fixed per take so a take can be re-rendered exactly."""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, soundfile as sf
from bakeoff_common import run, V2

MODE, THREADS = sys.argv[1], int(sys.argv[2])
DT = {"fp32": torch.float32, "bf16": torch.bfloat16}[sys.argv[3] if len(sys.argv) > 3 else "fp32"]
ONLY = sys.argv[4:] or None
torch.set_num_threads(THREADS)
from qwen_tts import Qwen3TTSModel

REPOS = {"design": "Qwen3-TTS-12Hz-1.7B-VoiceDesign", "custom17": "Qwen3-TTS-12Hz-1.7B-CustomVoice",
         "custom06": "Qwen3-TTS-12Hz-0.6B-CustomVoice"}
snap = glob.glob(f"{V2}/hf/hub/models--Qwen--{REPOS[MODE]}/snapshots/*")[0]
m = Qwen3TTSModel.from_pretrained(snap, device_map="cpu", dtype=DT)

# Invented character voices (bible: Jax American, Pip British computer, Mira Bengali, Temi in Lagos).
VOICE = {
    "JAX": "A man in his late thirties with a quick, warm, slightly husky American baritone; a charming, fast-talking space courier who sells for a living.",
    "PIP": "A crisp, precise British male voice belonging to a small, fussy ship's computer; mid-pitched, clipped consonants, very dry and literal.",
    "MIRA": "A woman in her mid-thirties with a low, cool, dry voice and a light Bengali Indian-English accent; exact, composed, quietly amused.",
    "TEMI": "A young woman with a bright, warm Nigerian English accent; a cheerful, polished bank call-centre agent with a smile in her voice.",
}
PRESET = {"JAX": "ryan", "PIP": "aiden", "MIRA": "serena", "TEMI": "vivian"}  # custom mode only
# (line, take, spoken text, direction). Take 2 = a second reading with different wording of the note.
DIRECTED = [
    ("L1", 1, "Temi! Hi! I'm about to make a payment—", "Panicked and breathless, speaking very fast with desperate fake cheer, voice rising, cut off at the end."),
    ("L1", 2, "Temi! Hi! I'm about to make a payment—", "Frantic, talking over someone at top speed, high-pitched nervous excitement."),
    ("L2", 1, "She is in Lagos. You are arguing with the past.", "Completely deadpan and flat, bone-dry, unhurried and precise, no emotion at all."),
    ("L3", 1, "Your record isn't late, Captain. It's blank.", "A cool, cutting put-down, calm and slightly amused, the last word low and final."),
    ("L4", 1, "Go! I'll get the ramp!", "Shouting at full volume across a distance, urgent, out of breath, adrenaline."),
    ("L4", 2, "Go! I'll get the ramp!", "Yelling loudly in an emergency, strained and forceful."),
    ("L5", 1, "It prefers her.", "Whispering very softly and tenderly, almost to herself, a small sad smile."),
    ("L5", 2, "It prefers her.", "A hushed, breathy whisper, very quiet and gentle."),
    ("L6", 1, "Read it to me. Slowly. I want to enjoy my name.", "Relaxed and savouring the moment, with a short amused laugh before the last sentence, grinning."),
    ("L6", 2, "Read it to me. Slowly. Ha! I want to enjoy my name.", "Chuckling, delighted and smug, laughing as he speaks."),
    ("L7", 1, "You gave up your job for us.", "Quiet, warm and sincere, slightly moved and touched, slower than usual."),
    ("L8", 1, "Good morning! This is Temi in Recoveries. Your vessel is being recovered.", "Very bright, chirpy and sing-song, professional call-centre cheer, smiling."),
]


def plan():
    return [(l, t, {"text": tx, "direction": d}) for l, t, tx, d in DIRECTED]


def synth(line, take, kw, out):
    torch.manual_seed(1000 + int(line["id"][1:]) * 10 + take)
    ch = line["char"]
    if MODE == "design":
        kw["instruct"] = VOICE[ch] + " " + kw["direction"]
        w, sr = m.generate_voice_design(text=kw["text"], language="English", instruct=kw["instruct"])
    else:
        kw["speaker"] = PRESET[ch]
        w, sr = m.generate_custom_voice(text=kw["text"], language="English", speaker=PRESET[ch], instruct=kw["direction"])
    sf.write(out, w[0], sr)


if __name__ == "__main__":
    run(f"qwen3-{MODE}", plan, synth, THREADS, meta={"model": REPOS[MODE], "dtype": str(DT)}, only=ONLY)
