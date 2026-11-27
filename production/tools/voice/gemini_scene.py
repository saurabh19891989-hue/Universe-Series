"""Gemini 3.8 Flash TTS test: per-line scene, multi-speaker scene, alt cast, range clips, consistency.
No secrets: the sandbox network proxy injects the real key; we send a dummy header.
Usage: python gemini_scene.py perline|alt|multi|range|consistency|voices
Reuses LINES / gaps / loudnorm from common.py so output is comparable with the free-engine bake-off."""
import os, sys, json, time, base64, subprocess, requests, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from common import LINES, CHARS, SCRATCH, SAMPLES, _mp3

API = "https://generativelanguage.googleapis.com/v1beta"
HDR = {"x-goog-api-key": "placeholder"}   # dummy; proxy substitutes the real key
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash-tts")
SUF = os.environ.get("GEMINI_SUFFIX", "")   # e.g. "-lite" when the quota of the main model is exhausted
class Quota(Exception): pass
OUT = f"{SAMPLES}/gemini"; W = f"{SCRATCH}/gemini"
os.makedirs(OUT, exist_ok=True); os.makedirs(W, exist_ok=True); os.makedirs(f"{OUT}/range", exist_ok=True)
LOG = f"{W}/requests.jsonl"

CAST = {"JAX": "zubenelgenubi", "MIRA": "en-in-podcaster-6", "PIP": "en-gb-advisor-8", "BARON": "de-de-storyteller-8"}
ALT = {"JAX": "en-us-tutor-7", "MIRA": "en-in-training-7", "PIP": "en-gb-tutor-8", "BARON": "en-us-enzo"}

# acting direction per scene line (index = LINES index)
STYLE = [
 "fast, confiding voiceover, wry, a salesman's warmth, like narrating a heist film, slightly self-mocking",
 "flat, clipped, precise, officious British civil servant, never raising his voice",
 "quick, exasperated but amused, rapid retort",
 "flat, clipped, pedantic, officious, deadpan bureaucratic precision",
 "dry, precise, low-key, matter-of-fact, quietly alarmed underneath",
 "theatrically indignant, bombastic, booming, grand, an elderly aristocratic stage actor deeply offended",
 "quick, puzzled and wary",
 "flat, deadpan, reading from a registry, clipped and officious",
 "genuinely hushed, almost a whisper, quiet, slow and serious",
 "fast confiding voiceover, wry, then slowing with rueful self-mockery on the last sentence",
]
TEXT = {i: l[1] for i, l in enumerate(LINES)}
TEXT[8] = "Jax. <short pause> If they can erase a place... they can erase the people in it."

def log(rec):
    with open(LOG, "a") as f: f.write(json.dumps(rec) + "\n")

def _strip_wav(b):
    return b

def tts(label, text, voice, style=None, out=None, speakers=None, turns=None, model=MODEL, retries=10):
    """Single-speaker if turns is None. turns=[(speaker,text,style)] with speakers={name:voice} for multi."""
    def block(t, s, spk=None):
        ann = {"type": "speech_metadata"}
        if spk: ann["speaker"] = spk
        if s: ann["style"] = s
        d = {"type": "text", "text": t}
        if len(ann) > 1: d["annotations"] = [ann]
        return d
    if "3.1" in model and style and not turns:   # 3.1 preview has no speech_metadata: direction goes in the text
        text = f"Say this {style}: {text}"; style = None
    if turns:
        content = [block(t, s, sp) for sp, t, s in turns]
        sc = {"speakers": [{"speaker": k, "voice": v} for k, v in speakers.items()]}
    else:
        content = [block(text, style)]
        sc = [{"voice": voice}]
    body = {"model": model, "input": [{"type": "user_input", "content": content}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": sc}}
    for a in range(retries):
        t0 = time.time()
        try:
            r = requests.post(f"{API}/interactions", headers=HDR, json=body, timeout=300)
        except Exception as e:
            log({"label": label, "err": str(e)}); time.sleep(3); continue
        dt = time.time() - t0
        rec = {"label": label, "model": model, "voice": voice or speakers, "status": r.status_code, "secs": round(dt, 2), "attempt": a}
        if r.status_code != 200:
            rec["err"] = r.text[:300]; rec["retry_after"] = r.headers.get("retry-after"); log(rec)
            time.sleep((float(r.headers.get('retry-after') or 15) + 2) if r.status_code == 429 else 3); continue
        j = r.json(); u = j.get("usage", {})
        aud = [c for s in j["steps"] for c in s.get("content", []) if c.get("type") == "audio"]
        if not aud: rec["err"] = "no audio"; log(rec); continue
        wav = base64.b64decode(aud[-1]["data"])
        path = out or f"{W}/{label}.wav"
        if wav[:4] != b"RIFF":   # 3.1 preview returns headerless PCM (24 kHz mono s16le)
            import io, wave
            buf = io.BytesIO(); w = wave.open(buf, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(wav); w.close(); wav = buf.getvalue()
        open(path, "wb").write(wav)
        dur = sf.info(path).duration
        rec.update(dur=round(dur, 2), out_tokens=u.get("total_output_tokens"), in_tokens=u.get("total_input_tokens"))
        log(rec); return path
    raise RuntimeError(f"failed {label}")

def load_wav(p):
    x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    assert sr == 24000, sr
    return x

def build(clips, gaps, name):
    """clips: list of (char, wav); gaps: seconds after each. Writes scene mp3 + returns per-char parts."""
    scene = []; per = {c: [] for c in CHARS}
    for (ch, p), g in zip(clips, gaps):
        x = load_wav(p)
        scene += [x, np.zeros(int(24000 * g), "float32")]
        if ch in per: per[ch] += [x, np.zeros(int(24000 * 0.4), "float32")]
    sf.write(f"{W}/{name}.wav", np.concatenate(scene), 24000)
    _mp3(f"{W}/{name}.wav", f"{OUT}/{name}.mp3")
    return per

def perline(cast, name):
    clips = []
    for i, (ch, _, gap, _) in enumerate(LINES):
        p = tts(f"{name}_{i:02d}_{ch}", TEXT[i], cast[ch], STYLE[i])
        clips.append((ch, p))
    per = build(clips, [l[2] for l in LINES], name)
    return per

def cmd_perline():
    per = perline(CAST, "scene-perline"+SUF)
    for c in CHARS:
        sf.write(f"{W}/{c}.wav", np.concatenate(per[c]), 24000); _mp3(f"{W}/{c}.wav", f"{OUT}/{c.lower()}.mp3")
    json.dump({"model": MODEL, "primary": CAST, "alt": ALT, "styles": STYLE}, open(f"{OUT}/casting.json", "w"), indent=2)

def cmd_alt():
    perline(ALT, "scene-altcast"+SUF)

# two-hander chunks (<=2 speakers per request): indexes into LINES
CHUNKS = [[0, 1, 2, 3], [4, 5], [6, 7], [8, 9]]
def cmd_multi():
    clips = []; gaps = []
    for k, idxs in enumerate(CHUNKS):
        chars = []
        for i in idxs:
            if LINES[i][0] not in chars: chars.append(LINES[i][0])
        assert len(chars) <= 2
        speakers = {c: CAST[c] for c in chars}
        turns = [(LINES[i][0], TEXT[i], STYLE[i]) for i in idxs]
        p = tts(f"multi_{k}{SUF}", None, None, speakers=speakers, turns=turns)
        clips.append(("MULTI", p)); gaps.append(LINES[idxs[-1]][2])
    build(clips, gaps, "scene-multispeaker"+SUF)

def vlist():
    p = f"{W}/allvoices.json"
    if os.path.exists(p): return json.load(open(p))
    allv = []; tok = None
    while True:
        params = {"page_size": 1000}
        if tok: params["page_token"] = tok
        d = requests.get(f"{API}/voices", headers=HDR, params=params, timeout=60).json()
        allv += d["voices"]; tok = d.get("next_page_token")
        if not tok: break
    json.dump(allv, open(p, "w")); return allv

def pick(lang, gender=None, accent_sub=None):
    for v in vlist():
        if v["language_code"] == lang and (gender is None or v["gender"] == gender) and (accent_sub is None or accent_sub.lower() in v["accent"].lower()):
            return v["id"]

RANGE_JAX = "zubenelgenubi"
def cmd_range():
    R = f"{OUT}/range"
    only = os.environ.get("RANGE_ONLY")
    def go(name, text, voice, style=None):
        if only and name not in only.split(","): return
        try: p = tts("range_" + name + SUF, text, voice, style)
        except Quota: raise
        except Exception as e: print("skip", name, e); return
        _mp3(p, f"{R}/{name}{SUF}.mp3")
    ss = [
     ("whisper", "Don't move. They're right outside the door, and they can hear everything.", "whispering, a real whisper, breathy, close to the microphone"),
     ("shout", "GET DOWN! Everybody get down, NOW!", "shouting at the top of his voice, panicked, urgent"),
     ("laugh_midline", "I told him the ship was haunted, and the best part is <laugh> he actually believed me <laugh> for three whole days.", "amused, barely holding back laughter"),
     ("sigh", "<sigh> Eleven minutes late. Of course we are. <sigh> Fine. Fine, let's just get it over with.", "weary, resigned"),
     ("crying", "I just... I just wanted them to come home. <sob> That's all. That's all I ever wanted.", "crying through the words, voice breaking, tearful and shaky"),
     ("sarcastic_deadpan", "Oh, wonderful. A crater that doesn't exist. This is exactly what I hoped for today.", "sarcastic, completely deadpan, flat delivery"),
    ]
    for n, t, s in ss: go(n, t, RANGE_JAX, s)
    L = "Good evening. I am the new navigator, and I have been told the coffee on this ship is a crime."
    # accents: A = native-language library voice reading English; B = English voice + accent direction (docs advise against B)
    go("indian_english_voice", L, "en-in-podcaster-6")
    go("indian_english_direction", L, RANGE_JAX, "speaking with a clear, natural Indian English accent")
    go("british_rp_voice", L, "en-gb-advisor-8")
    go("british_rp_direction", L, RANGE_JAX, "speaking in clear British Received Pronunciation")
    foreign = {"mexican_spanish": ("es-419", "Mexican Spanish"), "arabic": ("ar-eg", "Arabic"),
               "korean": ("ko-KR", "Korean"), "japanese": ("ja-JP", "Japanese")}
    for n, (lc, desc) in foreign.items():
        lcx = "ar-EG" if lc == "ar-eg" else lc
        v = pick(lcx, "male") or pick(lcx)
        go(f"{n}_accent_voice", L, v)
        go(f"{n}_accent_direction", L, RANGE_JAX, f"speaking English with a light, natural {desc} accent, respectful, not exaggerated")

def cmd_consistency():
    for k in range(3):
        tts(f"consist_{k}{SUF}", TEXT[0], CAST["JAX"], STYLE[0])

if __name__ == "__main__":
    {"perline": cmd_perline, "alt": cmd_alt, "multi": cmd_multi, "range": cmd_range, "consistency": cmd_consistency, "voices": lambda: print(len(vlist()))}[sys.argv[1]]()
