"""Make one ~8-10 s 'casting clip' per character with Qwen3-TTS 1.7B VoiceDesign (Apache-2.0) from our own
invented description (no real person), to use as the FIXED voice reference for a cloning engine
(Chatterbox-Turbo). The description is used once; every later line clones the same clip, so the voice is pinned.
Usage (voice2/v_qwen): python -I qwen_design_casting.py <threads> <outdir> [seed] [CHAR ...]"""
import os, sys, glob, torch, soundfile as sf

torch.set_num_threads(int(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
which = sys.argv[4:] or ["JAX", "PIP", "MIRA", "TEMI"]
from qwen_tts import Qwen3TTSModel

V2 = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice2"
snap = glob.glob(f"{V2}/hf/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-VoiceDesign/snapshots/*")[0]
m = Qwen3TTSModel.from_pretrained(snap, device_map="cpu", dtype=torch.bfloat16)
VOICE = {
    "JAX": "A man in his late thirties with a quick, warm, slightly husky American baritone; a charming, fast-talking space courier who sells for a living. Relaxed, natural, conversational.",
    "PIP": "A crisp, precise British male voice belonging to a small, fussy ship's computer; mid-pitched, clipped consonants, very dry and literal. Calm and even.",
    "MIRA": "A woman in her mid-thirties with a low, cool, dry voice and a light Bengali Indian-English accent; exact, composed, quietly amused. Natural and conversational.",
    "TEMI": "A young woman with a bright, warm Nigerian English accent; a cheerful, polished bank call-centre agent with a smile in her voice.",
}
# casting text = ordinary lines from E01 that are NOT in the bake-off test set
TEXT = {
    "JAX": "Here's my situation. I've got a parcel, a ship and a debt, and by six tonight I'd like to have only two of those. I'm very good at my job. I'm good at it in bursts.",
    "PIP": "Captain. The bank has taken the left engine. And the navigation lights. And the heating. And the coffee machine. It was financed separately.",
    "MIRA": "Parcel, one. Sealed. Addressed to a district withdrawn at fourteen-oh-two. I'm a cartographer. I appreciate where things actually are.",
    "TEMI": "Full recovery, including the air, at six tonight, lunar time. Hello! You're speaking to Temi in Recoveries! How can I help you today?",
}
for c in which:
    torch.manual_seed(seed)
    w, sr = m.generate_voice_design(text=TEXT[c], language="English", instruct=VOICE[c])
    sf.write(f"{out}/ref_{c}.wav", w[0], sr)
    print(c, round(len(w[0]) / sr, 2), "s", flush=True)
