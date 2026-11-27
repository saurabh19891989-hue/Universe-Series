#!/usr/bin/env python3
"""WER of a 3-minute sample from each table-read act file (faster-whisper small, int8, CPU).
Usage: python tableread_check.py OUT_DIR [--model small] [--minutes 3]
Reference = lines.csv rows fully inside the window (dialogue as in the script; narration as read).
Reports WER vs the script wording, and WER vs the respelled text actually sent to the TTS,
plus the list of word-level errors so mangled names can be read off."""
import argparse, csv, json, os, re, subprocess, sys
import numpy as np, jiwer
from faster_whisper import WhisperModel

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def n2w(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + n2w(n % 100))
    return n2w(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + n2w(n % 1000))
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
def norm(t):
    t = t.lower().replace("’", "'").replace("—", " ").replace("-", " ")
    t = re.sub(r"(\d+),(\d{3})", r"\1\2", t)
    t = re.sub(r"(\d+)(st|nd|rd|th)\b", lambda m: n2w(int(m.group(1))) + ("th" if False else ""), t)
    t = re.sub(r"\d+", lambda m: n2w(int(m.group())), t)
    t = re.sub(r"[^a-z' ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--model", default="small"); ap.add_argument("--minutes", type=float, default=3)
    ap.add_argument("--whisper-dir", default="/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice/whisper")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(a.out, "lines.csv"), encoding="utf-8")))
    m = WhisperModel(a.model, device="cpu", compute_type="int8", download_root=a.whisper_dir)
    W = a.minutes * 60; res = {}
    for f in sorted(set(r["file"] for r in rows)):
        rs = [r for r in rows if r["file"] == f]
        mp3 = os.path.join(a.out, [x for x in os.listdir(a.out) if x.endswith(f + ".mp3")][0])
        total = max(float(r["start_s"]) + float(r["duration_s"]) for r in rs)
        stings = [(float(r["start_s"]), float(r["start_s"]) + float(r["duration_s"])) for r in rs if r["kind"] == "sting"]
        # window starts at a line start roughly 1/3 into the file, avoiding stings
        cands = [float(r["start_s"]) for r in rs if r["kind"] != "sting" and float(r["start_s"]) > total * 0.3]
        w0 = next((c for c in cands if all(c + W <= s0 or c >= s1 for s0, s1 in stings) and c + W <= total), None)
        if w0 is None: w0 = max(0, total - W - 1)
        sel = [r for r in rs if r["kind"] != "sting" and float(r["start_s"]) >= w0 and float(r["start_s"]) + float(r["duration_s"]) <= w0 + W]
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(w0), "-t", str(W), "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
        segs, _ = m.transcribe(np.frombuffer(raw, dtype=np.float32), language="en", beam_size=5)
        hyp = norm(" ".join(s.text for s in segs))
        out = dict(window=[round(w0, 1), round(w0 + W, 1)], lines_in_window=len(sel))
        for label, key in (("wer_vs_script_text", "script_text"), ("wer_vs_spoken_respelling", "spoken_text")):
            ref = norm(" ".join((r["script_text"] if r["kind"] == "dialogue" else r["spoken_text"]) if key == "script_text" else r["spoken_text"] for r in sel))
            o = jiwer.process_words(ref, hyp); out[label] = round(o.wer, 4)
            if key == "script_text":
                rw, hw = ref.split(), hyp.split(); errs = []
                for ch in o.alignments[0]:
                    if ch.type != "equal":
                        errs.append(f"{ch.type}: '{' '.join(rw[ch.ref_start_idx:ch.ref_end_idx])}' -> '{' '.join(hw[ch.hyp_start_idx:ch.hyp_end_idx])}'")
                out["errors_vs_script_text"] = errs; out["ref_words"] = len(rw); out["counts"] = dict(sub=o.substitutions, ins=o.insertions, dele=o.deletions)
        res[f] = out; print(f, json.dumps({k: v for k, v in out.items() if k != "errors_vs_script_text"}), flush=True)
        for e in out["errors_vs_script_text"]: print("   ", e)
    json.dump(res, open(os.path.join(a.out, "wer_check.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
