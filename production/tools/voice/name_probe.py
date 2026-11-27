#!/usr/bin/env python3
"""Choose respellings for names Whisper mishears: render each candidate in 3 sentences with the real cast voice,
transcribe with faster-whisper small, count agreement. Writes names_choice.json next to this script.
Usage: python name_probe.py CAST_JSON"""
import json, os, re, subprocess, sys, numpy as np
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel
cast = json.load(open(sys.argv[1]))["cast"]
SV = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice"
k = Kokoro(f"{SV}/models/kokoro/kokoro-v1.0.onnx", f"{SV}/models/kokoro/voices-v1.0.bin")
m = WhisperModel("small", device="cpu", compute_type="int8", download_root=f"{SV}/whisper")
TESTS = {
 "oczakow": ("BARON", ["He dropped their gate on him at {}.", "{}. The Turks had the fortress. We had the fish.", "I turned back a Turk at {}!"],
             ["Ochakoff", "Och-a-koff", "Ochakov", "Ockakoff", "Otchakoff", "Ochakof"], r"\bo[ck]?z?c?h?a[ck]?k?[oa]?(ov|off|of|ow)\b", r"\boczakow\b"),
 "mira": ("JAX", ["Jax. It's {}. Don't move.", "That's {}'s notebook.", "Doctor {} Sen is at the desk."],
          ["Meera", "Mira", "Mihra", "Meerah", "Mirra", "Mear-a"], r"\bmira('s)?\b", r"\bmira('s)?\b"),
 "noakes": ("MIRA", ["Superintendent {} will see you now.", "{}'s office, then the corridor.", "That was an incident, said {}."],
            ["Noaks", "Noakes", "Nokes", "Noax", "Noakz", "Noke"], r"\bnoakes('s)?\b", r"\bnoa?kes?('s)?\b|\bnoaks\b"),
}
def render(role, text):
    c = cast[role]; s, sr = k.create(text, voice=c["voice"], speed=c["speed"], lang=c["lang"]); x = np.asarray(s, dtype="float32")
    chain = []
    if abs(c["pitch"] - 1) > 1e-6: chain.append(f"rubberband=pitch={c['pitch']}:formant={c['formant']}")
    if c.get("band"): chain.append("highpass=f=250,lowpass=f=4500")
    chain.append("aresample=16000")
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-af", ",".join(chain), "-f", "f32le", "-ar", "16000", "-ac", "1", "-"], input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4")
res = {}; choice = {}
for name, (role, sents, cands, strict, lenient) in TESTS.items():
    res[name] = {}
    for c in cands:
        hits = []; hyps = []
        for s in sents:
            segs, _ = m.transcribe(render(role, s.format(c)), language="en", beam_size=5); h = " ".join(x.text for x in segs).lower(); hyps.append(h)
            hits.append((bool(re.search(strict, h)), bool(re.search(lenient, h))))
        res[name][c] = dict(strict=sum(a for a, b in hits), lenient=sum(b for a, b in hits), heard=hyps)
        print(name, c, res[name][c]["strict"], res[name][c]["lenient"], hyps, flush=True)
    best = max(cands, key=lambda c: (res[name][c]["strict"], res[name][c]["lenient"], -cands.index(c)))
    choice[name] = best
json.dump(choice, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "names_choice.json"), "w"), indent=1)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "name_probe.json"), "w"), indent=1)
print(choice)
