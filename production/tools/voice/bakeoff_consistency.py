"""Speaker-consistency numbers for the bake-off: speaker embeddings from Chatterbox's VoiceEncoder
(a GE2E-style speaker encoder, MIT) for every take; reports for each engine and character the mean
cosine similarity between that character's takes (within-character: higher = the voice stays the same
person across lines) and the mean similarity to the other characters (lower = characters distinct).
Run in voice2/v_cbx. Usage: python -I bakeoff_consistency.py <out_root> > consistency.json
Rough guide for this encoder: same-speaker clips usually score above ~0.75; short (<1.5 s) or whispered
clips score lower even for the same speaker, so read the numbers per line too."""
import sys, os, glob, json
import numpy as np, librosa, torch
from chatterbox.models.voice_encoder import VoiceEncoder
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

REPO = "/home/user/Universe-Series"
SCR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
LINES = {l["id"]: l for l in json.load(open(f"{REPO}/production/tools/voice/bakeoff_lines.json"))["lines"]}
ve = VoiceEncoder()
ve.load_state_dict(load_file(hf_hub_download("ResembleAI/chatterbox-turbo", "ve.safetensors")))
ve.eval()


def emb(p):
    y, _ = librosa.load(p, sr=16000)
    e = ve.embeds_from_wavs([y], sample_rate=16000, as_spk=False)
    e = np.asarray(e).mean(0)
    return e / np.linalg.norm(e)


root = sys.argv[1]
sets = {"kokoro": {lid: [f"{SCR}/e01/dialogue/{l['kokoro']}"] for lid, l in LINES.items()}}
for d in sorted(glob.glob(f"{root}/*/")):
    e = os.path.basename(d.rstrip("/"))
    sets[e] = {}
    for w in sorted(glob.glob(f"{d}L*_t*.wav")):
        sets[e].setdefault(os.path.basename(w).split("_")[0], []).append(w)
res = {}
for eng, by_line in sets.items():
    E = {}
    for lid, ws in by_line.items():
        for w in ws:
            E[os.path.basename(w)[:-4] if eng != "kokoro" else f"{lid}_t1"] = (LINES[lid]["char"], emb(w))
    chars = sorted(set(c for c, _ in E.values()))
    out = {"per_char": {}, "per_take_vs_char_mean": {}}
    for c in chars:
        ks = [k for k, (cc, _) in E.items() if cc == c]
        V = np.stack([E[k][1] for k in ks])
        cen = V.mean(0)
        cen /= np.linalg.norm(cen)
        within = [float(V[i] @ V[j]) for i in range(len(ks)) for j in range(i + 1, len(ks))]
        others = [float(E[k][1] @ E[o][1]) for k in ks for o in E if E[o][0] != c]
        out["per_char"][c] = dict(n=len(ks), within_mean=round(np.mean(within), 3) if within else None,
                                  within_min=round(min(within), 3) if within else None,
                                  vs_other_chars_mean=round(np.mean(others), 3))
        for k in ks:
            out["per_take_vs_char_mean"][k] = round(float(E[k][1] @ cen), 3)
    # similarity of each take to the Kokoro reference clip of that character (chatterbox refs)
    ref = {c: emb(f"{SCR}/voice2/refs/ref_{c}.wav") for c in ("JAX", "PIP", "MIRA", "TEMI")}
    out["vs_kokoro_ref"] = {k: round(float(v @ ref[c]), 3) for k, (c, v) in E.items()}
    res[eng] = out
print(json.dumps(res, indent=1))
