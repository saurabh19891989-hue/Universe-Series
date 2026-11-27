#!/usr/bin/env python3
"""Table-read audio from a screenplay (Kokoro, local, CPU).

One command:
  <venv>/bin/python tableread.py SCRIPT.md [--out DIR] [--work DIR] [--narration FILE.json]
                                 [--casting FILE.json] [--stings DIR] [--only-act N]

Reads dialogue from fenced blocks (cue / (parenthetical) / dialogue), a slate before each
"### N · LOCATION" unit, act titles, a short narrator beat table (JSON), applies respellings
and radio/voice filters, assembles four act files (cold open + act 1 | act 2 | act 3 |
act 4 + tag + "what was real"), loudness-normalises each to -16 LUFS / TP < -1.5 dB, and writes
casting.json, timings.json and lines.csv. Synthesised lines are cached under WORK/cache.
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tr_parse import parse, lines_of

SR = 44100
KOKORO_DIR = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice/models/kokoro"
STINGS = "/home/user/Universe-Series/samples/music/v2"

# ---------------------------------------------------------------- casting
CAST = {
 "JAX":      dict(voice="am_puck",   lang="en-us", speed=1.08, pitch=1.0,  note="American male, quick, warm (as earlier report)"),
 "PIP":      dict(voice="bm_george", lang="en-gb", speed=1.05, pitch=1.0,  filt="highpass=f=250,lowpass=f=4500", note="British male, clipped; small-speaker band limit 250-4500 Hz"),
 "BARON":    dict(voice="bm_fable",  lang="en-gb", speed=0.91, pitch=0.93, note="older, theatrical; slowed 9%, pitched down about 7% (rubberband)"),
 "MIRA":     dict(voice="bf_emma",   lang="en-gb", speed=0.95, pitch=1.0,  note="British female, dry and precise; no accent hack"),
 "LUCÍA":    dict(voice="af_heart",  lang="en-us", speed=1.08, pitch=0.98, note="warmer American female, blunt and energetic"),
 "CHICHIKOV":dict(voice="bm_lewis",  lang="en-gb", speed=0.92, pitch=1.0,  gain=-1.5, note="lowest British male, unhurried and soft; slowed 8%"),
 "NOAKES":   dict(voice="bm_daniel", lang="en-gb", speed=1.12, pitch=1.06, note="British male, faster, pitched up 6% so older/anxious and apart from Baron"),
 "TEMI":     dict(voice="af_sky",    lang="en-us", speed=1.08, pitch=1.04, note="bright female"),
 "MAMANI":   dict(voice="am_eric",   lang="en-us", speed=0.95, pitch=0.97, note="calm male"),
 "NARRATOR": dict(voice="af_nicole", lang="en-us", speed=0.93, pitch=1.0,  gain=-3.5, note="neutral quiet slate/action-beat voice"),
}
ALIASES = {"JAX VALE": "JAX", "DR MIRA SEN": "MIRA", "LUCIA": "LUCÍA", "OFFICER MAMANI": "MAMANI", "TEMI ADEYEMI": "TEMI"}

RADIO = "highpass=f=300,lowpass=f=3400,acompressor=threshold=0.05:ratio=3:attack=5:release=80"
SUIT = "highpass=f=400,lowpass=f=2800,acompressor=threshold=0.04:ratio=4:attack=4:release=60"
MUFFLE = "lowpass=f=2200"

# ---------------------------------------------------------------- respelling
RESPELL = [
 (r"\bOczakow\b", "Ochakoff"), (r"\bpost-chaise\b", "post shayz"), (r"\bPost-chaise\b", "Post shayz"),
 (r"\bPOST-CHAISE\b", "post shayz"), (r"\bHieronymus\b", "Heer-onimus"),
 (r"\bChichikov\b", "Cheechikoff"), (r"\bN-O-A-K-E-S\b", "N. O. A. K. E. S."),
 (r"\b4471-C\b", "four, four, seven, one, C"), (r"\bMunchausen\b", "Munchowzen"),
 (r"\bLucía\b", "Looseea"), (r"\bLUCÍA\b", "Looseea"), (r"\bPIP\b", "Pip"), (r"\bNASA\b", "Nasa"),
 (r"\bDr\b\.?", "Doctor"), (r"\bMr\b\.?", "Mister"), (r"\bMrs\b\.?", "Missus"),
 (r"\bSeñorita\b", "Senyorita"), (r"\bun-seize\b", "un seize"), (r"\bNoakes\b", "Noaks"),
]
def respell(t):
    t = t.replace("*", "").replace("’", "'")
    for a, b in RESPELL: t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()

NUM = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {20: "twenty", 30: "thirty", 40: "forty"}
def numword(n):
    if n < 20: return NUM[n]
    t, o = divmod(n, 10)
    return TENS[t * 10] + ("-" + NUM[o] if o else "")

# ---------------------------------------------------------------- delivery from cue + parentheticals
def cue_info(cue):
    base = re.split(r"\s*\(", cue, maxsplit=1)[0].strip()
    tags = [x.upper() for x in re.findall(r"\(([^)]*)\)", cue)]
    base = ALIASES.get(base, base)
    return base, tags

def delivery(base, tags, parens, unit_num):
    d = dict(speed=1.0, gain=0.0, pre=0.0, filt=None, noise=False, closer=False, os=False)
    p = " ".join(x.strip("()").lower() for x in parens)
    if "V.O." in tags:
        if base == "JAX": d["closer"] = True; d["speed"] *= 0.94
        elif unit_num != "WWR": d["filt"] = RADIO; d["noise"] = True
        else: d["closer"] = True
    if "O.S." in tags: d["os"] = True; d["gain"] -= 2.5
    if re.search(r"suit radio", p): d["filt"] = SUIT; d["noise"] = True
    elif re.search(r"\bradio\b", p) or (re.search(r"\bwrist\b", p) and "into his wrist" not in p):
        d["filt"] = RADIO; d["noise"] = True
    if "crackling" in p: d["noise"] = True; d["gain"] -= 1
    if re.search(r"open mic|headset", p): d["filt"] = d["filt"] or RADIO
    if re.search(r"inside the machine|covering the mouthpiece|distant|from the back", p): d["filt"] = d["filt"] or MUFFLE; d["gain"] -= 2.5
    if re.search(r"very quietly", p): d["speed"] *= 0.85; d["gain"] -= 7
    elif re.search(r"quiet|softly|quieter|a breath|gently", p): d["speed"] *= 0.88; d["gain"] -= 4
    if re.search(r"fast, one breath", p): d["speed"] *= 1.3
    if re.search(r"\ba beat\b", p): d["pre"] = max(d["pre"], 0.8)
    if re.search(r"\ba breath\b", p): d["pre"] = max(d["pre"], 0.45)
    if re.search(r"wondering|helpless|fighting it|appalled|looking at his own hands|reading|settling", p): d["speed"] *= 0.94
    if re.search(r"delighted|surprised", p): d["speed"] *= 1.04
    return d

PAUSE_RE = re.compile(r"^(Silence|Nothing|A beat|A long silence|A small silence|A real pause|A silence|Jax says nothing)\b")
def action_pause(text):
    if re.search(r"point three seconds", text): return 1.3
    if PAUSE_RE.match(text):
        if re.search(r"long|full second|small silence|real pause", text[:60]): return 1.0
        if text.startswith("Jax says nothing"): return 0.6
        return 0.8
    return 0.0

# ---------------------------------------------------------------- audio helpers
def ff_filter(x24, chain):
    """x24: float32 mono at 24k -> float32 at SR, through ffmpeg filter chain."""
    af = (chain + "," if chain else "") + f"aresample={SR}"
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-",
                        "-af", af, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=x24.astype("<f4").tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").copy()

def trim(x, thr=0.004, keep=0.03):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x[:int(SR * 0.05)]
    a = max(0, idx[0] - int(keep * SR)); b = min(len(x), idx[-1] + int(keep * SR) + 1)
    return x[a:b]

def rms_db(x):
    act = x[np.abs(x) > 0.004]
    return 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-9) if len(act) else -60

def sil(sec): return np.zeros(int(round(sec * SR)), dtype="float32")

def decode(path, sr=SR):
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ar", str(sr), "-ac", "1", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").copy()

def loud(x, sr=SR):
    """integrated LUFS and true peak (dBTP) of float array via ffmpeg ebur128."""
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], input=x.astype("<f4").tobytes(), capture_output=True)
    t = p.stderr.decode()
    last = t[t.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", last).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", last).group(1))
    return I, tp

# ---------------------------------------------------------------- synthesis with cache
class Synth:
    def __init__(self, work):
        from kokoro_onnx import Kokoro
        self.k = Kokoro(f"{KOKORO_DIR}/kokoro-v1.0.onnx", f"{KOKORO_DIR}/voices-v1.0.bin")
        self.cache = os.path.join(work, "cache"); os.makedirs(self.cache, exist_ok=True)
        self.voices = set(self.k.get_voices()); self.calls = 0; self.hits = 0
    def __call__(self, text, voice, speed, lang):
        key = hashlib.sha1(f"{voice}|{speed:.3f}|{lang}|{text}".encode()).hexdigest()[:20]
        p = os.path.join(self.cache, key + ".wav")
        if os.path.exists(p):
            self.hits += 1; x, _ = sf.read(p, dtype="float32"); return x
        s, sr = self.k.create(text, voice=voice, speed=float(speed), lang=lang)
        assert sr == 24000
        x = np.asarray(s, dtype="float32"); sf.write(p, x, sr); self.calls += 1; return x

# ---------------------------------------------------------------- main assembly
TARGET_RMS = -20.0
def render_line(synth, cast, role, text, d, rng, tag_extra=""):
    c = cast[role]
    speed = min(max(c["speed"] * d["speed"], 0.55), 1.6)
    x = synth(text, c["voice"], speed, c["lang"])
    chains = []
    if c.get("pitch", 1.0) != 1.0: chains.append(f"rubberband=pitch={c['pitch']}")
    if d["closer"]: chains.append("highpass=f=90,equalizer=f=3200:t=q:w=1:g=2.5,acompressor=threshold=0.06:ratio=2.5:attack=8:release=100")
    if c.get("filt"): chains.append(c["filt"])
    if d["filt"]: chains.append(d["filt"])
    if d["os"]: chains.append("lowpass=f=6000")
    y = ff_filter(x, ",".join(chains))
    y = trim(y)
    g = TARGET_RMS - rms_db(y) + c.get("gain", 0) + d["gain"] + (1.5 if d["closer"] else 0)
    y = (y * 10 ** (g / 20)).astype("float32")
    if d["noise"]:  # touch of radio hiss, 40 dB under the line
        n = rng.standard_normal(len(y) + int(0.1 * SR)).astype("float32") * 10 ** ((rms_db(y) - 40) / 20)
        n = np.convolve(n, np.ones(3) / 3, mode="same").astype("float32")
        y = np.concatenate([y, np.zeros(int(0.1 * SR), dtype="float32")]); y = y + n[:len(y)]
    return y

def title_case_loc(t):
    t = t.replace("*", "")
    t = re.sub(r"\s*[—/]\s*", ", ", t).strip().lower()
    return t[0].upper() + t[1:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("--out", default="/home/user/Universe-Series/samples/tableread/E01")
    ap.add_argument("--work", default="/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/tableread")
    ap.add_argument("--narration"); ap.add_argument("--casting"); ap.add_argument("--stings", default=STINGS)
    ap.add_argument("--prefix", default="E01-tableread"); ap.add_argument("--bitrate", default="72k")
    ap.add_argument("--max-narration-share", type=float, default=0.12)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.work, exist_ok=True)
    cast = {k: dict(v) for k, v in CAST.items()}
    if a.casting:
        for k, v in json.load(open(a.casting)).items(): cast.setdefault(k, {}).update(v)
    narr_path = a.narration
    if not narr_path:
        m = re.search(r"/(E\d+)/", os.path.abspath(a.script))
        cand = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"tableread_narration_{m.group(1)}.json") if m else None
        narr_path = cand if cand and os.path.exists(cand) else None
    beats = json.load(open(narr_path))["beats"] if narr_path else []
    units = parse(a.script)
    synth = Synth(a.work); rng = np.random.default_rng(7)
    for r, c in cast.items():
        assert c["voice"] in synth.voices, (r, c["voice"])

    # act grouping -> output file index
    def file_of(u):
        if u["act"] == "COLD OPEN": return 1
        m = re.match(r"ACT (\w+)", u["act"])
        if m: return {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4}[m.group(1)]
        return 4  # TAG, WHAT WAS REAL
    FILE_NAMES = {1: "1-cold-open-and-act1", 2: "2-act2", 3: "3-act3", 4: "4-act4-and-tag"}
    acts = {i: [] for i in (1, 2, 3, 4)}   # list of np arrays
    cursor = {i: 0 for i in acts}          # samples
    rows = []; unit_rows = []; warnings = []
    used_beats = set()
    sting_title = decode(os.path.join(a.stings, "A1-title-sting-10s.mp3"))
    sting_end = decode(os.path.join(a.stings, "A1-endcard-sting-5s.mp3"))
    stg = lambda s: (s * 10 ** ((-21 - rms_db(s)) / 20)).astype("float32")  # stings sit about 1 dB under speech RMS
    sting_title, sting_end = stg(sting_title), stg(sting_end)

    def emit(fi, arr): acts[fi].append(arr); cursor[fi] += len(arr)
    first_unit_of_file = {}
    for ui, u in enumerate(units):
        fi = file_of(u)
        t_unit_start = cursor[fi]
        if fi in first_unit_of_file or acts[fi]:
            emit(fi, sil(1.2))
            t_unit_start = cursor[fi]
        first_unit_of_file.setdefault(fi, u["num"])
        spoken_words = 0; narr_words = 0; narr_sec = 0.0; spoken_sec = 0.0
        prev = None   # ("line", base, words, endsdash) | ("narr",) | ("act", pause)
        def put(arr, kind, speaker, tags, script_text, spoken_text, gap_before):
            nonlocal spoken_words, narr_words, narr_sec, spoken_sec
            if gap_before > 0: emit(fi, sil(gap_before))
            start = cursor[fi] / SR; emit(fi, arr); dur = len(arr) / SR
            rows.append(dict(file=FILE_NAMES[fi], scene=u["num"], speaker=speaker, tags=" ".join(tags), kind=kind,
                             start_s=round(start, 2), duration_s=round(dur, 2), script_text=script_text, spoken_text=spoken_text))
            if kind == "dialogue": spoken_words += len(script_text.split()); spoken_sec += dur
            else: narr_words += len(spoken_text.split()); narr_sec += dur
        def narrate(text, gap):
            d = delivery("NARRATOR", [], [], u["num"])
            put(render_line(synth, cast, "NARRATOR", respell(text), d, rng), "narration", "NARRATOR", [], text, respell(text), gap)
        # act title + slate
        if u.get("act_title"):
            n, title = u["act_title"]; narrate(f"Act {n.lower()}. {title}.", 0.0); prev = ("narr",)
        elif u["act"] == "TAG" and u["num"] != "WWR":
            narrate("Tag.", 0.0); prev = ("narr",)
        if u["num"] == "WWR": slate = "What was real."
        elif u["num"] == "0": slate = f"Cold open. {title_case_loc(u['title'])}."
        elif "–" in u["num"]:
            x, y = u["num"].split("–"); slate = f"Scenes {numword(int(x))} and {numword(int(y))}. {title_case_loc(u['title'])}."
        else: slate = f"Scene {numword(int(u['num']))}. {title_case_loc(u['title'])}."
        narrate(slate, 0.45 if prev else 0.0); prev = ("narr",)
        items = lines_of(u)
        for it in items:
            if it["kind"] == "action":
                # narrator beats
                hit = [(i, b) for i, b in enumerate(beats) if b[0] == u["num"] and re.search(b[1], it["text"])]
                for i, b in hit:
                    used_beats.add(i)
                    narrate(b[2], 0.35 if prev and prev[0] == "line" else 0.3); prev = ("narr",)
                pz = action_pause(it["text"])
                if pz:
                    emit(fi, sil(pz)); prev = ("pause",)
                elif not hit and prev and prev[0] == "line":
                    prev = ("act",)
                continue
            base, tags = cue_info(it["cue"])
            if base not in cast:
                warnings.append(f"unit {u['num']} line {it['line']}: unknown speaker {base!r}, using MAMANI voice"); role = "MAMANI"
            else: role = base
            d = delivery(base, tags, it["parens"], u["num"])
            spoken = respell(it["text"])
            arr = render_line(synth, cast, role, spoken, d, rng)
            # gap before
            if prev is None: gap = 0.0
            elif prev[0] == "line":
                _, pb, pw, pdash = prev
                if pb == base: gap = 0.25
                elif pdash and it["text"].startswith(("—", "-")): gap = 0.18
                elif pw >= 18: gap = 0.5
                elif pw >= 9: gap = 0.33
                else: gap = 0.2
            elif prev[0] == "act": gap = 0.35
            elif prev[0] == "narr": gap = 0.35
            else: gap = 0.2
            gap = max(gap, d["pre"]) if prev is not None else d["pre"]
            if prev and prev[0] in ("pause",): gap = max(d["pre"], 0.1)
            put(arr, "dialogue", base, tags + [p.strip("()") for p in it["parens"]], it["text"], spoken, gap)
            prev = ("line", base, len(it["text"].split()), it["text"].rstrip().endswith(("—", "-")))
        t_unit_end = cursor[fi]
        unit_rows.append(dict(scene=u["num"], title=u["title"], file=FILE_NAMES[fi], act=u["act"],
                              start_in_file_s=round(t_unit_start / SR, 2), duration_s=round((t_unit_end - t_unit_start) / SR, 2),
                              spoken_words=spoken_words, target_s=u["target"], narration_words=narr_words,
                              narration_s=round(narr_sec, 2), speech_s=round(spoken_sec, 2)))
        if u["num"] == "0":  # MAIN TITLE after the cold open
            narrate("Main title.", 0.6)
            emit(fi, sil(0.4)); t0 = cursor[fi]; emit(fi, sting_title)
            unit_rows[-1]["note"] = "duration ends at the last cold-open line; 'Main title.' slate and 10 s sting follow"
            rows.append(dict(file=FILE_NAMES[fi], scene="0", speaker="MUSIC", tags="", kind="sting", start_s=round(t0 / SR, 2),
                             duration_s=round(len(sting_title) / SR, 2), script_text="MAIN TITLE", spoken_text="[A1-title-sting-10s.mp3]"))
    # end sting
    emit(4, sil(0.8)); t0 = cursor[4]; emit(4, sting_end)
    rows.append(dict(file=FILE_NAMES[4], scene="end", speaker="MUSIC", tags="", kind="sting", start_s=round(t0 / SR, 2),
                     duration_s=round(len(sting_end) / SR, 2), script_text="END", spoken_text="[A1-endcard-sting-5s.mp3]"))
    for i, b in enumerate(beats):
        if i not in used_beats: warnings.append(f"narration beat never matched: {b[:2]}")

    # ---- loudness + encode
    report = {}
    for fi in (1, 2, 3, 4):
        x = np.concatenate(acts[fi]).astype("float32")
        wav = os.path.join(a.work, f"act{fi}.wav"); sf.write(wav, x, SR, subtype="FLOAT")
        mp3 = os.path.join(a.out, f"{a.prefix}-{FILE_NAMES[fi]}.mp3")
        tp_t = -1.9; gain_trim = 0.0
        for attempt in range(6):
            m = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af", f"loudnorm=I=-16:TP={tp_t}:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
            j = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
            ln = (f"loudnorm=I=-16:TP={tp_t}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
                  f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
            af = ln + (f",volume={gain_trim}dB" if gain_trim else "")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", af, "-ar", str(SR), "-ac", "1",
                            "-c:a", "libmp3lame", "-abr", "1", "-b:a", a.bitrate, mp3], check=True)
            y = decode(mp3)
            I, tp = loud(y)
            if tp <= -1.5 and abs(I + 16) <= 0.6: break
            if tp > -1.5: gain_trim -= (tp + 1.5) + 0.3
            else: gain_trim += (-16 - I) * 0.5
        size = os.path.getsize(mp3)
        report[fi] = dict(file=os.path.basename(mp3), duration_s=round(len(y) / SR, 2), size_mb=round(size / 1e6, 3),
                          integrated_lufs=I, true_peak_dbtp=tp, sample_peak_dbfs=round(20 * np.log10(np.max(np.abs(y)) + 1e-9), 2),
                          clipped_samples=int(np.sum(np.abs(y) >= 0.999)), bitrate_kbps=round(size * 8 / (len(y) / SR) / 1000, 1),
                          attempts=attempt + 1)
    # ---- outputs
    with open(os.path.join(a.out, "lines.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"engine": "kokoro-onnx 0.6.1 (Kokoro-82M v1.0, Apache-2.0), CPU", "cast": cast, "respellings": RESPELL,
               "filters": dict(radio=RADIO, suit_radio=SUIT, muffle=MUFFLE, jax_vo="highpass 90, +2.5 dB at 3.2 kHz, mild compression, +1.5 dB, speed x0.94"),
               "narration_table": os.path.basename(narr_path) if narr_path else None},
              open(os.path.join(a.out, "casting.json"), "w"), indent=1, ensure_ascii=False)
    tot = dict(spoken_words=0, duration_s=0, target_s=0)
    per_file = {}
    for fi in (1, 2, 3, 4):
        us = [r for r in unit_rows if r["file"] == FILE_NAMES[fi]]
        per_file[FILE_NAMES[fi]] = dict(duration_s=report[fi]["duration_s"], unit_duration_sum_s=round(sum(r["duration_s"] for r in us), 2),
                                        spoken_words=sum(r["spoken_words"] for r in us), target_s=sum(r["target_s"] or 0 for r in us),
                                        narration_s=round(sum(r["narration_s"] for r in us), 2), **{k: report[fi][k] for k in ("integrated_lufs", "true_peak_dbtp", "size_mb")})
    all_dur = sum(r["duration_s"] for r in report.values())
    narr_total = sum(r["duration_s"] for r in rows if r["kind"] == "narration")
    # global start = file offset + start in file
    off = 0; offs = {}
    for fi in (1, 2, 3, 4): offs[FILE_NAMES[fi]] = off; off += report[fi]["duration_s"]
    for r in unit_rows: r["start_global_s"] = round(offs[r["file"]] + r["start_in_file_s"], 2); r["delta_vs_target_s"] = round(r["duration_s"] - (r["target_s"] or 0), 2)
    json.dump(dict(scenes=unit_rows, per_file=per_file,
                   totals=dict(duration_s=round(all_dur, 2), duration_mmss=f"{int(all_dur // 60)}:{int(all_dur % 60):02d}",
                               spoken_words=sum(r["spoken_words"] for r in unit_rows),
                               target_s_sum=sum(r["target_s"] or 0 for r in unit_rows), narration_s=round(narr_total, 2),
                               narration_share=round(narr_total / all_dur, 4), stings_s=15.0, note="targets exclude the 10 s title; audio includes 15 s stings, slates, 1.2 s scene gaps"),
                   loudness=report, warnings=warnings),
              open(os.path.join(a.out, "timings.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(totals=dict(duration_s=round(all_dur, 1), narration_share=round(narr_total / all_dur, 4)), loudness=report, warnings=warnings, synth_calls=synth.calls, cache_hits=synth.hits), indent=1))

if __name__ == "__main__":
    main()
