#!/usr/bin/env python3
"""Production dialogue stems from a screenplay (Kokoro, local CPU). No narration.

  <venv>/bin/python dialogue_stems.py SCRIPT.md --cast voice-cast.json --out DIALOGUE_DIR
        --conform dialogue-conform.json --review REVIEW_DIR [--work WORK]

Per script chunk (long speeches split at sentence ends): a DRY 48 kHz mono 24-bit WAV and, where the script
puts the voice through a device/space, a TREATED WAV. Writes per-scene dialogue tracks (treated where present,
plus a dry version), the conform sheet, and per-act review MP3s + lines.csv for the WER check.
Written silences are separate dead air in the conform/timeline, never baked into stems.
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tr_parse import parse, lines_of

SR = 48000
TARGET_RMS = -20.0      # dBFS RMS of active samples: the common dialogue level
PEAK_CAP = -2.0         # dBFS: a stem is scaled down if its sample peak would exceed this
NAMES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "names_choice.json")

# ------------------------------------------------------------------ respelling
def respell_rules():
    n = dict(oczakow="Ochakoff", mira="Meera", noakes="Noaks")
    if os.path.exists(NAMES_FILE): n.update(json.load(open(NAMES_FILE)))
    return [(r"\bOczakow\b", n["oczakow"]), (r"\bpost-chaise\b", "post shayz"), (r"\bPost-chaise\b", "Post shayz"),
            (r"\bHieronymus\b", "Heer-onimus"), (r"\bChichikov\b", "Cheechikoff"), (r"\bN-O-A-K-E-S\b", "N. O. A. K. E. S."),
            (r"\b4471-C\b", "four, four, seven, one, C"), (r"\bMunchausen\b", "Munchowzen"),
            (r"\bLucía\b", "Looseea"), (r"\bPIP\b", "Pip"), (r"\bNASA\b", "Nasa"),
            (r"\bDr\b\.?", "Doctor"), (r"\bMr\b\.?", "Mister"), (r"\bSeñorita\b", "Senyorita"), (r"\bun-seize\b", "un seize"),
            (r"(?i)\bNoakes\b", n["noakes"]), (r"(?i)\bMira\b", n["mira"])]
def respell(t, rules):
    t = t.replace("*", "").replace("’", "'")
    for a, b in rules: t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()

# ------------------------------------------------------------------ chunking
def sentences(t):
    out, cur = [], []
    for w in t.split():
        cur.append(w)
        if re.search(r"[.!?][\"”')]*$", w) and not re.match(r"^[A-Z]\.$", w) and not w.endswith("..."):
            out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    return out
def chunk(t, fast=False):
    if fast or len(t.split()) <= 22: return [t]
    ss = sentences(t); ch, acc = [], []
    for s in ss:
        acc.append(s)
        if sum(len(x.split()) for x in acc) >= 12: ch.append(" ".join(acc)); acc = []
    if acc:
        if ch and sum(len(x.split()) for x in acc) < 5: ch[-1] += " " + " ".join(acc)
        else: ch.append(" ".join(acc))
    return ch

# ------------------------------------------------------------------ delivery + treatment decisions
def cue_info(cue):
    base = re.split(r"\s*\(", cue, maxsplit=1)[0].strip()
    return {"LUCIA": "LUCÍA"}.get(base, base), [x.upper() for x in re.findall(r"\(([^)]*)\)", cue)]

def delivery(parens):
    p = " ".join(x.strip("()").lower() for x in parens)
    d = dict(speed=1.0, gain=0.0, pre=0.0, dark=False, fast=False, notes=[])
    if re.search(r"very quietly", p): d.update(speed=0.85, gain=-7.0, dark=True); d["notes"].append("very quietly")
    elif re.search(r"quiet|softly|quieter|to herself|a breath|gently", p): d.update(speed=0.88, gain=-4.0, dark=True); d["notes"].append("quiet/soft")
    if re.search(r"to himself", p): d.update(speed=0.92, gain=-3.0, dark=True); d["notes"].append("to himself")
    if re.search(r"fast, one breath", p): d["speed"] = 1.3; d["fast"] = True; d["notes"].append("fast, one breath")
    if re.search(r"\ba beat\b", p): d["pre"] = 0.8; d["notes"].append("a beat (0.8 s separate pause)")
    if re.search(r"\ba breath\b", p): d["pre"] = max(d["pre"], 0.45)
    if re.search(r"wondering|helpless|fighting it|appalled|looking at his own hands|settling", p): d["speed"] *= 0.94
    if re.search(r"grand|magnificent", p): d["speed"] *= 0.95
    if re.search(r"delighted|surprised", p): d["speed"] *= 1.05
    if re.search(r"into his wrist", p): d["gain"] -= 2.0
    return d

# scene-level device context for V.O./O.S. cues that carry no explicit parenthetical on every line
SCENE_TREAT = {
 ("0", "TEMI"): "bank_call", ("1", "LUCÍA"): "inside_machine", ("1", "PIP"): "wrist", ("2", "MAMANI"): "radio",
 ("3", "BARON"): "far_shout", ("5", "LUCÍA"): "wrist", ("5", "PIP"): "wrist", ("7", "PIP"): "wrist", ("9", "MIRA"): "suit_radio",
 ("9", "BARON"): "suit_radio", ("11", "PIP"): "wrist", ("15", "PIP"): "wrist", ("16", "PIP"): "wrist", ("24", "PIP"): "wrist",
 ("27", "PIP"): "wrist_crackle", ("27", "MIRA"): "open_channel", ("27", "NOAKES"): "open_channel",
 ("29", "JAX"): "suit_radio", ("29", "LUCÍA"): "suit_radio", ("29", "BARON"): "suit_radio", ("29", "PIP"): "radio", ("29", "MIRA"): "radio",
 ("30", "TEMI"): "bank_call", ("21", "JAX"): "suit_radio", ("21", "BARON"): "suit_radio",
}
ONLY_VO_OS = {("3", "BARON"), ("1", "LUCÍA"), ("1", "PIP"), ("5", "LUCÍA"), ("5", "PIP"), ("7", "PIP"), ("11", "PIP"), ("15", "PIP"), ("16", "PIP"),
              ("24", "PIP"), ("27", "PIP"), ("27", "MIRA"), ("27", "NOAKES"), ("2", "MAMANI"), ("9", "MIRA"), ("9", "BARON"), ("0", "TEMI"), ("30", "TEMI")}
def treatment(scene, base, tags, parens):
    p = " ".join(x.strip("()").lower() for x in parens)
    if "V.O." in tags and base == "JAX": return "jax_vo_dry"
    if re.search(r"distant", p): return "far_shout"
    if re.search(r"inside the machine", p): return "inside_machine"
    if re.search(r"covering the mouthpiece", p): return "headset_muffled"
    if re.search(r"into the headset", p): return "headset"
    if re.search(r"open mic", p): return "open_channel"
    if re.search(r"from the back", p): return "distance_light"
    if re.search(r"wrist, crackling", p): return "wrist_crackle"
    if re.search(r"suit radio", p): return "suit_radio"
    if re.search(r"hold speaker|wrist", p) and "into his wrist" not in p: return "wrist"
    if re.search(r"\bradio\b", p): return "suit_radio" if scene in ("29",) and base in ("JAX", "LUCÍA", "BARON") else "radio"
    k = (scene, base)
    if k in SCENE_TREAT:
        if k in ONLY_VO_OS and not ({"V.O.", "O.S."} & set(tags)): return None
        return SCENE_TREAT[k]
    if scene == "WWR": return None
    return None

TREAT = {  # name: (ffmpeg chain, hiss dB under line or None, crackle, level offset dB, description)
 "radio": ("highpass=f=300,lowpass=f=3400,acompressor=threshold=0.04:ratio=4:attack=3:release=60:makeup=2,asoftclip=type=tanh:threshold=0.5", -38, False, -1.0, "band-pass 300-3400 Hz, compression, mild tanh distortion, light hiss"),
 "suit_radio": ("highpass=f=420,lowpass=f=2700,acompressor=threshold=0.03:ratio=5:attack=3:release=50:makeup=3,asoftclip=type=tanh:threshold=0.4,aecho=0.8:0.5:6:0.3", -34, False, -1.5, "narrow 420-2700 Hz, heavy compression, distortion, tiny helmet echo, hiss"),
 "wrist": ("highpass=f=380,lowpass=f=3800,equalizer=f=1500:t=q:w=1.5:g=4,acompressor=threshold=0.04:ratio=4:attack=3:release=60:makeup=2,asoftclip=type=tanh:threshold=0.5", -42, False, -2.0, "small wrist speaker 380-3800 Hz, 1.5 kHz honk, compression, distortion"),
 "wrist_crackle": ("highpass=f=380,lowpass=f=3800,equalizer=f=1500:t=q:w=1.5:g=4,acompressor=threshold=0.04:ratio=4:attack=3:release=60:makeup=2,asoftclip=type=tanh:threshold=0.4", -32, True, -2.5, "wrist speaker plus hiss and random crackle pops"),
 "bank_call": ("highpass=f=330,lowpass=f=3300,acompressor=threshold=0.03:ratio=6:attack=2:release=50:makeup=3,asoftclip=type=tanh:threshold=0.45", -40, False, 0.0, "telephone 330-3300 Hz, heavy compression, soft clip"),
 "open_channel": ("highpass=f=250,lowpass=f=4800,acompressor=threshold=0.05:ratio=3:attack=4:release=70:makeup=2,asoftclip=type=tanh:threshold=0.6", -32, False, -1.0, "wider 250-4800 Hz with more hiss"),
 "headset": ("highpass=f=250,lowpass=f=5000,acompressor=threshold=0.05:ratio=3:attack=4:release=70:makeup=1,asoftclip=type=tanh:threshold=0.7", -46, False, -1.0, "headset mic 250-5000 Hz, compression"),
 "headset_muffled": ("highpass=f=150,lowpass=f=1500", None, False, -8.0, "hand over mouthpiece: low-passed 1.5 kHz, -8 dB"),
 "inside_machine": ("highpass=f=140,lowpass=f=2000,aecho=0.7:0.6:23|41:0.4|0.3", None, False, -3.0, "inside reactor housing: 140-2000 Hz plus metallic short echoes"),
 "far_shout": ("lowpass=f=4000,aecho=0.6:0.5:85|170:0.35|0.2", None, False, -7.0, "far down a hall: low-passed 4 kHz, hall echoes, -7 dB"),
 "distance_light": ("lowpass=f=5500,aecho=0.8:0.7:45:0.2", None, False, -4.0, "across the room: low-passed 5.5 kHz, light room echo, -4 dB"),
}
JAX_VO_EQ = "highpass=f=90,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1:g=2.5,acompressor=threshold=0.06:ratio=2.5:attack=8:release=100"
DARK = "highshelf=f=3500:g=-4"
PAUSE_RE = re.compile(r"^(Silence|Nothing|A beat|A long silence|A small silence|A real pause|A silence)\b")

def action_silence(scene, text):
    """Exact dead air from written silences. Returns (seconds, label) or None."""
    if re.search(r"point three seconds", text): return 1.3, "Earth delay, 1.3 s"
    if re.search(r"A full second", text): return 1.0, "written: a full second of nothing"
    if scene == "25" and re.search(r"Nothing\.?$|^Nothing", text): return 1.3, "Earth delay wait, 1.3 s (scene 25)"
    if PAUSE_RE.match(text):
        return (1.0 if re.search(r"long|small silence|real pause", text[:60]) else 0.8), "written silence"
    if text.startswith("Jax says nothing"): return 0.6, "written silence"
    return None

# ------------------------------------------------------------------ audio helpers
def ff(x, in_sr, chain, out_sr=SR):
    af = (chain + "," if chain else "") + f"aresample={out_sr}"
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(in_sr), "-ac", "1", "-i", "-", "-af", af,
                        "-f", "f32le", "-ar", str(out_sr), "-ac", "1", "-"], input=x.astype("<f4").tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").copy()
def trim(x, thr=0.004, keep=0.02):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x[:int(SR * 0.05)]
    return x[max(0, idx[0] - int(keep * SR)): min(len(x), idx[-1] + int(keep * SR) + 1)]
def rms_db(x):
    a = x[np.abs(x) > 0.004]
    return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9) if len(a) else -60.0
def level(x, offset_db):
    g = TARGET_RMS + offset_db - rms_db(x); y = x * 10 ** (g / 20)
    pk = 20 * np.log10(np.max(np.abs(y)) + 1e-9); capped = False
    if pk > PEAK_CAP: y = y * 10 ** ((PEAK_CAP - pk) / 20); capped = True
    return y.astype("float32"), round(float(g), 2), capped
def fade_out(x, ms):
    n = int(SR * ms / 1000); x = x.copy(); x[-n:] *= np.linspace(1, 0, n) ** 1.5; return x
def sil(s): return np.zeros(int(round(s * SR)), dtype="float32")

class Synth:
    def __init__(self, work):
        from kokoro_onnx import Kokoro
        KD = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice/models/kokoro"
        self.k = Kokoro(f"{KD}/kokoro-v1.0.onnx", f"{KD}/voices-v1.0.bin"); self.c = os.path.join(work, "cache"); os.makedirs(self.c, exist_ok=True); self.n = 0
    def __call__(self, text, voice, speed, lang):
        p = os.path.join(self.c, hashlib.sha1(f"{voice}|{speed:.3f}|{lang}|{text}".encode()).hexdigest()[:20] + ".wav")
        if os.path.exists(p): return sf.read(p, dtype="float32")[0]
        s, sr = self.k.create(text, voice=voice, speed=float(speed), lang=lang); x = np.asarray(s, dtype="float32"); sf.write(p, x, sr); self.n += 1; return x

def loud(x, sr=SR):
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=x.astype("<f4").tobytes(), capture_output=True)
    t = p.stderr.decode(); t = t[t.rfind("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", t).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", t).group(1))
def decode(path):
    return np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"], capture_output=True, check=True).stdout, dtype="<f4").copy()

def scene_tag(num):
    n = num.replace("–", "-")
    return "S" + (n if (n == "WWR" or "-" in n) else n.zfill(2))
def ascii_name(b): return b.replace("Í", "I")

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("script"); ap.add_argument("--cast", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--conform", required=True); ap.add_argument("--review", required=True)
    ap.add_argument("--work", default="/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/work")
    ap.add_argument("--ep", default="E01"); ap.add_argument("--bitrate", default="72k"); a = ap.parse_args()
    for d in (a.out, a.review, a.work): os.makedirs(d, exist_ok=True)
    castj = json.load(open(a.cast)); cast = castj["cast"]; rules = respell_rules()
    synth = Synth(a.work); rng = np.random.default_rng(11)
    units = parse(a.script)
    def act_of(u):
        if u["act"] == "COLD OPEN": return 1
        m = re.match(r"ACT (\w+)", u["act"]); return {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4}[m.group(1)] if m else 4
    ACTN = {1: "1-cold-open-and-act1", 2: "2-act2", 3: "3-act3", 4: "4-act4-and-tag"}
    conform = dict(scenes=[]); rows = []; ep_cursor = 0.0; scene_tracks = {}; level_stats = []; words_total = 0; alnum_total = 0
    for u in units:
        stag = scene_tag(u["num"]); items = lines_of(u); events = []   # events: ("line", rec) / ("sil", seconds,label)
        idx = 0; prev = None
        for it in items:
            if it["kind"] == "action":
                s = action_silence(u["num"], it["text"])
                if s: events.append(("sil", s[0], s[1], it["text"][:70]));
                continue
            base, tags = cue_info(it["cue"]); role = base if base in cast else "MAMANI"
            dl = delivery(it["parens"]); tr = treatment(u["num"], base, tags, it["parens"])
            vo_jax = tr == "jax_vo_dry"
            written = it["text"]; words_total += len(written.split()); alnum_total += len([t for t in written.split() if re.search(r"[A-Za-z0-9]", t)])
            fast_text = written
            if dl["fast"]: fast_text = re.sub(r"[,;:.](?=\s)", "", written)
            parts = chunk(written if not dl["fast"] else fast_text, fast=dl["fast"])
            for pi, part in enumerate(parts):
                idx += 1; c = cast[role]
                spoken = respell(part, rules)
                spd = c["speed"] * dl["speed"] * (0.94 if vo_jax else 1.0)
                x = synth(spoken, c["voice"], min(max(spd, 0.55), 1.7), c["lang"])
                chain = []
                if abs(c["pitch"] - 1) > 1e-6: chain.append(f"rubberband=pitch={c['pitch']}:formant={c['formant']}")
                if c.get("band"): chain.append("highpass=f=250,lowpass=f=4500")
                if vo_jax: chain.append(JAX_VO_EQ)
                if dl["dark"]: chain.append(DARK)
                y = trim(ff(x, 24000, ",".join(chain)))
                interrupted = part.rstrip().endswith("—")
                if interrupted:
                    cut = int(0.07 * SR); y = fade_out(y[:-cut] if len(y) > cut * 3 else y, 40)
                off = dl["gain"] + (1.5 if vo_jax else 0.0)
                dry, g, capped = level(y, off)
                nm = f"{a.ep}_{stag}_L{idx:03d}_{ascii_name(base)}"
                sf.write(os.path.join(a.out, nm + ".wav"), dry, SR, subtype="PCM_24")
                rec = dict(scene=u["num"], index=idx, speaker=base, cue=it["cue"], parentheticals=it["parens"], script_line=it["line"],
                           text_written=part, text_spoken=spoken, file_dry=nm + ".wav", file_treated=None, duration_s=round(len(dry) / SR, 3),
                           treatment=None, treatment_note=None, delivery=dl["notes"], level_offset_db=round(off, 1), applied_gain_db=g,
                           peak_capped=capped, interrupted_tail_trimmed=interrupted, voice=c["voice"], speed_used=round(spd, 3),
                           split_part=f"{pi + 1}/{len(parts)}", pre_beat=dl["pre"] if pi == 0 else 0.0)
                out_arr = dry
                if tr and tr != "jax_vo_dry":
                    chn, hiss, crack, toff, desc = TREAT[tr]
                    z = ff(dry, SR, chn, SR)
                    z = trim(z)
                    if hiss is not None or crack:
                        base_rms = rms_db(z)
                        n = rng.standard_normal(len(z) + int(0.05 * SR)).astype("float32") * 10 ** (((base_rms + (hiss or -34)) - 0) / 20)
                        n = np.convolve(n, np.ones(3) / 3, mode="same").astype("float32"); z = np.concatenate([z, np.zeros(int(0.05 * SR), dtype="float32")]) + n[:len(z) + int(0.05 * SR)]
                    if crack:
                        for pos in rng.integers(0, len(z), size=max(2, len(z) // 9000)):
                            L = int(rng.integers(20, 90)); z[pos:pos + L] += (rng.standard_normal(min(L, len(z) - pos)) * 10 ** ((base_rms - 8) / 20)).astype("float32")
                    treated, g2, cap2 = level(z, off + toff)
                    tn = nm + "_treated.wav"; sf.write(os.path.join(a.out, tn), treated, SR, subtype="PCM_24")
                    rec.update(file_treated=tn, treatment=tr, treatment_note=desc, treated_offset_db=toff, treated_peak_capped=cap2); out_arr = treated
                elif vo_jax: rec.update(treatment="jax_vo_dry", treatment_note="Jax V.O.: dry/close, speed x0.94, EQ +1.5 dB 180 Hz, +2.5 dB 3.2 kHz, mild compression, +1.5 dB level")
                rec["_dry"] = dry; rec["_out"] = out_arr
                level_stats.append((nm, rms_db(dry), float(20 * np.log10(np.max(np.abs(dry)) + 1e-9)), off))
                events.append(("line", rec))
        # ---------------- timeline for this scene
        recs = []; sil_events = []
        T = np.zeros(1, dtype="float32"); Td = np.zeros(1, dtype="float32")
        def put(T, arr, start):
            end = start + len(arr)
            if end > len(T): T = np.concatenate([T, np.zeros(end - len(T), dtype="float32")])
            T[start:end] += arr; return T
        prev_end = 0; since = 0.0; prevline = None; sil_since = False
        for ev in events:
            if ev[0] == "sil":
                sil_events.append(dict(duration_s=ev[1], label=ev[2], script_text=ev[3], after_index=prevline["index"] if prevline else 0,
                                       start_in_scene_s=round(prev_end / SR + since, 3)))
                since += ev[1]; sil_since = True; continue
            r = ev[1]; w = len(r["text_written"].split()); partn = int(r["split_part"].split("/")[0])
            if prevline is None: gap = 0.0
            else:
                pw = len(prevline["text_written"].split()); same = prevline["speaker"] == r["speaker"]
                if sil_since: gap = 0.15
                elif prevline["interrupted_tail_trimmed"] and not same: gap = -0.11
                elif prevline["interrupted_tail_trimmed"]: gap = 0.2
                elif partn > 1: gap = 0.30
                elif same: gap = 0.25
                elif pw <= 3 and w <= 3: gap = 0.12
                elif pw >= 18: gap = 0.5
                elif pw >= 9: gap = 0.33
                else: gap = 0.2
            if r["pre_beat"]: gap = max(gap, r["pre_beat"])
            since += gap; start = max(0, prev_end + int(round(since * SR)))
            r["pause_before_s"] = round(since, 3)
            if prevline is not None: prevline["pause_after_s"] = round(since, 3)
            r["start_in_scene_s"] = round(start / SR, 3); r["end_in_scene_s"] = round((start + len(r["_out"])) / SR, 3)
            T = put(T, r["_out"], start); Td = put(Td, r["_dry"], start)
            prev_end = start + len(r["_out"]); since = 0.0; sil_since = False; prevline = r; recs.append(r)
        if sil_since and prevline is not None: prevline["pause_after_s"] = round(since, 3)
        if sil_since: T = np.concatenate([T, sil(since)]); Td = np.concatenate([Td, sil(since)])
        for r in recs: r.setdefault("pause_after_s", 0.0)
        dur = len(T) / SR
        sf.write(os.path.join(a.out, f"{a.ep}_{stag}_dialogue.wav"), T, SR, subtype="PCM_24")
        sf.write(os.path.join(a.out, f"{a.ep}_{stag}_dialogue_dry.wav"), Td, SR, subtype="PCM_24")
        scene_tracks[u["num"]] = (T, act_of(u))
        spoken_words = sum(len(r["text_written"].split()) for r in recs)
        conform["scenes"].append(dict(scene=u["num"], title=u["title"], act=u["act"], target_s=u["target"], dialogue_duration_s=round(dur, 3),
                                      delta_vs_target_s=round(dur - (u["target"] or 0), 2), spoken_words=spoken_words, lines=[], dead_air=sil_events,
                                      scene_start_in_episode_s=round(ep_cursor, 3), scene_track=f"{a.ep}_{stag}_dialogue.wav", scene_track_dry=f"{a.ep}_{stag}_dialogue_dry.wav"))
        for r in recs:
            r["start_in_episode_s"] = round(ep_cursor + r["start_in_scene_s"], 3); r["end_in_episode_s"] = round(ep_cursor + r["end_in_scene_s"], 3)
            r.pop("_dry"); r.pop("_out"); conform["scenes"][-1]["lines"].append(r)
        ep_cursor += dur + 1.2
    # ---------------- review MP3s per act (treated tracks, 1.2 s between scenes, -16 LUFS, limiter)
    def limit(x, ceil):
        lim = 10 ** (ceil / 20)
        return np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"alimiter=limit={lim:.4f}:attack=3:release=60:level=0",
                                             "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"], input=x.astype("<f4").tobytes(), capture_output=True, check=True).stdout, dtype="<f4").copy()
    loudness = {}; act_off = {}
    for fi in (1, 2, 3, 4):
        parts = []; off = 0.0
        for sc in conform["scenes"]:
            T, ai = scene_tracks[sc["scene"]]
            if ai != fi: continue
            if parts: parts.append(sil(1.2)); off += 1.2
            sc["start_in_act_file_s"] = round(off, 3); sc["act_file"] = ACTN[fi]; parts.append(T); off += len(T) / SR
        x = np.concatenate(parts); I0, _ = loud(x); g = -16 - I0; ceil = -3.8; mp3 = os.path.join(a.review, f"{a.ep}-dialogue-{ACTN[fi]}.mp3")
        for outer in range(5):
            for _ in range(4):
                y = limit((x * 10 ** (g / 20)).astype("float32"), ceil); Ip, _ = loud(y)
                if abs(Ip + 16) <= 0.12: break
                g += -16 - Ip
            wp = os.path.join(a.work, f"act{fi}.wav"); sf.write(wp, y, SR, subtype="FLOAT")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wp, "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-abr", "1", "-b:a", a.bitrate, mp3], check=True)
            d = decode(mp3); I, tp = loud(d)
            if tp > -1.6: ceil -= (tp + 1.6 + 0.1)
            elif abs(I + 16) > 0.25: g += -16 - I
            else: break
        loudness[ACTN[fi]] = dict(file=os.path.basename(mp3), duration_s=round(len(d) / SR, 2), size_mb=round(os.path.getsize(mp3) / 1e6, 3), integrated_lufs=round(I, 1),
                                  true_peak_dbtp=round(tp, 1), clipped_samples=int(np.sum(np.abs(d) >= 0.999)), act_offset_gain_db=round(g, 2))
        act_off[fi] = loudness[ACTN[fi]]
    with open(os.path.join(a.review, "lines.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["file", "scene", "speaker", "kind", "start_s", "duration_s", "script_text", "spoken_text"])
        for sc in conform["scenes"]:
            for r in sc["lines"]:
                w.writerow([sc["act_file"], sc["scene"], r["speaker"], "dialogue", round(sc["start_in_act_file_s"] + r["start_in_scene_s"], 2), r["duration_s"], r["text_written"], r["text_spoken"]])
    # ---------------- conform sheet
    treat_counts = {}
    for sc in conform["scenes"]:
        for r in sc["lines"]:
            if r["treatment"]: treat_counts[r["treatment"]] = treat_counts.get(r["treatment"], 0) + 1
    ll = np.array([[s[1], s[2]] for s in level_stats])
    conform.update(meta=dict(episode=a.ep, sample_rate=SR, format="WAV mono 24-bit PCM", cast_file=os.path.basename(a.cast), spoken_words_written=words_total,
                             spoken_words_alnum=alnum_total, lines_total=sum(len(s["lines"]) for s in conform["scenes"]), dialogue_total_s_incl_internal_pauses=round(sum(s["dialogue_duration_s"] for s in conform["scenes"]), 2),
                             episode_timeline_s_with_1p2s_scene_gaps_no_stings=round(ep_cursor - 1.2, 2), target_sum_s=sum(s["target_s"] or 0 for s in conform["scenes"]),
                             note="Stems contain no silence. pause_before/after are recommended gaps; negative pause_before = start this stem that many seconds early over the interrupted line. dead_air entries are exact written silences (1.3 s Earth delay etc.). Title sting (10 s) and end sting are not in this timeline.",
                             level_policy=dict(target_active_rms_dbfs=TARGET_RMS, peak_cap_dbfs=PEAK_CAP, offsets_db={"normal": 0, "quiet/softly/to herself/quieter/a breath": -4, "very quietly": -7, "to himself": -3, "into his wrist": -2, "jax_vo": "+1.5"},
                                               treated_offsets_db={k: v[3] for k, v in TREAT.items()}),
                             treatments=treat_counts, treatment_chains={k: dict(chain=v[0], hiss_db_under_line=v[1], crackle=v[2], desc=v[4]) for k, v in TREAT.items()},
                             stem_level_stats=dict(dry_rms_dbfs_min=float(ll[:, 0].min()), dry_rms_dbfs_max=float(ll[:, 0].max()), dry_peak_dbfs_max=float(ll[:, 1].max()), stems=len(ll)),
                             review_mp3=loudness))
    json.dump(conform, open(a.conform, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(conform["meta"], indent=1, ensure_ascii=False)); print("synth calls", synth.n)

if __name__ == "__main__": main()
