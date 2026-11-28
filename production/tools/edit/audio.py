#!/usr/bin/env python3
"""Audio assembly for the edit engine: dialogue from a timing sheet (or finished stems), music and
effects cues with keyframed ducking under dialogue, loudness to -16 LUFS / < -1.5 dBTP, .srt.

All mixing is numpy at 48 kHz stereo float32; ffmpeg decodes inputs and measures loudness.
Placeholder effects (synthesised here) are used only when a cue's file is missing; each is logged.
"""
import csv, json, math, os, re, subprocess
import numpy as np
from scipy.signal import resample_poly

SR = 48000


def decode(path, ch=2, sr=SR):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, ch).copy()


def db(x):
    return 10 ** (x / 20.0)


def fade(x, fi, fo, sr=SR):
    n = len(x)
    a, b = int(fi * sr), int(fo * sr)
    if a > 0:
        x[:min(a, n)] *= np.linspace(0, 1, min(a, n), dtype=np.float32)[:, None]
    if b > 0:
        x[max(0, n - b):] *= np.linspace(1, 0, min(b, n), dtype=np.float32)[:, None]
    return x


def place(bus, clip, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0:
        clip = clip[-i:]; i = 0
    j = min(len(bus), i + len(clip))
    if j > i:
        bus[i:j] += clip[:j - i] * gain


# ------------------------------------------------------------------ placeholder effects
def synth(kind, seed=1):
    rng = np.random.default_rng(seed)
    def env(n, a, d):
        t = np.arange(n) / SR
        return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def tone(f, n, d, a=0.004):
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * f * t) * env(n, a, d)
    if kind == "chime":            # cheerful two-note bank chime
        n = int(0.9 * SR)
        x = np.concatenate([tone(1046.5, n // 3, 0.18) + 0.4 * tone(2093, n // 3, 0.1),
                            tone(1318.5, n, 0.35) + 0.4 * tone(2637, n, 0.15)])
        x *= 0.35
    elif kind == "shopbell":       # soft old shop-door bell
        n = int(1.6 * SR)
        x = sum(a * tone(f, n, d) for f, a, d in ((1530, 1, 0.5), (2490, 0.5, 0.35), (3650, 0.25, 0.2), (4720, 0.12, 0.12)))
        x2 = np.zeros_like(x); k = int(0.13 * SR); x2[k:] = x[:-k] * 0.6
        x = (x + x2) * 0.22
    elif kind == "thunk":          # rubber stamp hitting a desk
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        body = np.sin(2 * np.pi * (95 - 40 * t) * t) * env(n, 0.001, 0.07)
        click = rng.standard_normal(n) * env(n, 0.0005, 0.008)
        x = (body * 0.9 + click * 0.35)
    elif kind == "powerdown":      # a system switching off
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        f = 900 * np.exp(-t * 4)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.18
        x[:200] += rng.standard_normal(200) * 0.3 * np.linspace(1, 0, 200)
    elif kind == "click":
        n = int(0.08 * SR)
        x = rng.standard_normal(n) * env(n, 0.0003, 0.006) * 0.4
    elif kind == "engine_cough":   # starter coughs, catches, settles into a rumble
        n = int(4.0 * SR)
        t = np.arange(n) / SR
        nz = rng.standard_normal(n)
        from scipy.signal import butter, lfilter
        b, a = butter(2, 180 / (SR / 2)); lo = lfilter(b, a, nz)
        lo = lo / (np.abs(lo).max() + 1e-9)
        cough = np.zeros(n)
        for c in (0.0, 0.42, 0.95):
            i = int(c * SR); m = int(0.25 * SR)
            cough[i:i + m] += np.exp(-np.arange(m) / SR / 0.08)
        run = np.clip((t - 1.3) / 0.8, 0, 1) * (1 + 0.15 * np.sin(2 * np.pi * 11 * t))
        x = lo * (cough * 0.9 + run * 0.45) * 0.8 + np.sin(2 * np.pi * 48 * t) * run * 0.12
        x *= np.minimum(1, (n - np.arange(n)) / (0.5 * SR))
    elif kind == "roomtone":       # ship air handling, long loop
        n = int(10 * SR)
        nz = np.cumsum(rng.standard_normal(n)); nz -= np.convolve(nz, np.ones(4800) / 4800, "same")
        t = np.arange(n) / SR
        x = nz / (np.abs(nz).max() + 1e-9) * 0.5 + 0.08 * np.sin(2 * np.pi * 60 * t)
    elif kind == "blip":
        n = int(0.12 * SR)
        x = tone(1760, n, 0.04) * 0.2
    else:
        x = np.zeros(int(0.1 * SR))
    x = np.asarray(x, np.float32)
    return np.stack([x, x], 1)


# ------------------------------------------------------------------ dialogue
def load_dialogue(spec, resolve, log):
    """Lines of one unit from the table-read timing sheet. Line id = '<scene>-<NN>' where NN is the
    1-based row number of that scene in lines.csv (narration rows count, so ids match the sheet)."""
    rows = list(csv.DictReader(open(resolve(spec["timing_sheet"]), encoding="utf-8")))
    rows = [r for r in rows if r["file"] == spec["file"] and r["scene"] == str(spec["scene"])]
    skip = set(spec.get("skip_kinds", ["narration", "sting"]))
    ov = spec.get("overrides", {})
    stems = resolve(spec["stems_dir"]) if spec.get("stems_dir") else None
    src_cache = None
    t_scene = min(float(r["start_s"]) for r in rows)
    out = []
    for n, r in enumerate(rows, 1):
        lid = f"{r['scene']}-{n:02d}"
        o = ov.get(lid, {})
        if r["kind"] in skip or o.get("skip"):
            continue
        st0 = float(r["start_s"]); du = float(r["duration_s"])
        clip = None; src = None
        if stems:
            for ext in (".wav", ".flac", ".mp3"):
                p = os.path.join(stems, lid + ext)
                if os.path.exists(p):
                    clip = decode(p, 1)[:, 0]; src = p
                    break
        if clip is None:
            if src_cache is None:
                src_cache = decode(resolve(spec["source_wav"]), 1)[:, 0]
            pad = spec.get("slice_pad_s", 0.03)
            a = max(0, int((st0 - pad) * SR)); b = int((st0 + du + pad) * SR)
            clip = src_cache[a:b].copy(); src = "table-read slice"
            st0 -= pad
            k = int(0.012 * SR)
            clip[:k] *= np.linspace(0, 1, k); clip[-k:] *= np.linspace(1, 0, k)
        start = st0 - t_scene + spec.get("offset_s", 0.0) + o.get("shift_s", 0.0)
        if "start_s" in o:
            start = o["start_s"]
        clip = clip * db(o.get("gain_db", 0.0))
        out.append(dict(id=lid, speaker=r["speaker"], tags=r["tags"], start=start, dur=len(clip) / SR,
                        text=r["script_text"], audio=clip.astype(np.float32), src=src))
    nstem = sum(1 for x in out if x["src"] != "table-read slice")
    log.append(f"dialogue: {len(out)} lines ({nstem} from final stems, {len(out)-nstem} sliced from the table read"
               + (" - PLACEHOLDER until final stems land)" if nstem < len(out) else ")"))
    return out


def load_conformed(spec, resolve, log):
    """Final stems placed by the converter from the dialogue conform sheet:
    spec["lines"] = [{id, src, start_s, speaker, text, gain_db, reverb_db, reverb_ir}]."""
    out = []; miss = 0
    ir_cache = {}
    for ln in spec["lines"]:
        p = resolve(ln["src"])
        if not os.path.exists(p):
            log.append(f"MISSING dialogue stem {ln['id']} {ln['src']}"); miss += 1
            continue
        clip = decode(p, 1)[:, 0] * db(ln.get("gain_db", 0.0))
        rec = dict(id=ln["id"], speaker=ln["speaker"], tags=ln.get("tags", ""), start=ln["start_s"], dur=len(clip) / SR,
                   text=ln.get("text", ""), audio=clip.astype(np.float32), src=p, sub=ln.get("sub", True),
                   card=ln.get("card", True))
        if ln.get("reverb_db") is not None and ln.get("reverb_ir"):
            ip = resolve(ln["reverb_ir"])
            if ip not in ir_cache:
                ir = decode(ip, 2)
                ir_cache[ip] = ir / (np.sqrt((ir ** 2).sum(0)).max() + 1e-9)
            from scipy.signal import fftconvolve
            ir = ir_cache[ip]
            wet = np.stack([fftconvolve(clip, ir[:, 0]), fftconvolve(clip, ir[:, 1])], 1).astype(np.float32)
            pre = int(ln.get("reverb_predelay_s", 0.02) * SR)
            rec["wet"] = np.concatenate([np.zeros((pre, 2), np.float32), wet]) * db(ln["reverb_db"])
        out.append(rec)
    log.append(f"dialogue: {len(out)} final stems placed from the conform sheet" + (f"; {miss} MISSING" if miss else ""))
    return out


def amplitudes(lines, total_s, rate=96, range_db=30.0):
    """Per-speaker amplitude of the placed stems at `rate` Hz, 0..1 on a log scale (range_db below each
    speaker's 95th percentile). Drives the comm-card waveforms: the bars are the line's real audio."""
    n = int(math.ceil(total_s * rate)) + 1
    hop = SR // rate
    res = {}
    for ln in lines:
        e = res.setdefault(ln["speaker"], np.zeros(n, np.float32))
        x = ln["audio"]; k = len(x) // hop
        if k == 0:
            continue
        rms = np.sqrt((x[:k * hop].reshape(k, hop) ** 2).mean(1) + 1e-12)
        i0 = int(round(ln["start"] * rate))
        j0, j1 = max(0, -i0), min(k, n - i0)
        if j1 > j0:
            e[i0 + j0:i0 + j1] = np.maximum(e[i0 + j0:i0 + j1], rms[j0:j1])
    for spk, e in res.items():
        ref = np.percentile(e[e > 1e-4], 95) if (e > 1e-4).any() else 1
        res[spk] = np.clip(20 * np.log10(e / ref + 1e-9) / range_db + 1, 0, 1).astype(np.float32)
    return res


def envelopes(lines, total_s, fps):
    """Per-speaker speech envelope at the picture frame rate, 0..1 (attack ~30 ms, release ~150 ms)."""
    n = int(math.ceil(total_s * fps)) + 1
    hop = SR // fps
    res = {}
    for ln in lines:
        e = res.setdefault(ln["speaker"], np.zeros(n, np.float32))
        x = ln["audio"]
        k = len(x) // hop
        if k == 0:
            continue
        rms = np.sqrt((x[:k * hop].reshape(k, hop) ** 2).mean(1) + 1e-12)
        i0 = int(round(ln["start"] * fps))
        for j, v in enumerate(rms):
            if 0 <= i0 + j < n:
                e[i0 + j] = max(e[i0 + j], v)
    for spk, e in res.items():
        ref = np.percentile(e[e > 1e-4], 90) if (e > 1e-4).any() else 1
        e = np.clip(20 * np.log10(e / ref + 1e-9) / 24 + 1, 0, 1)   # 24 dB range below the 90th pct
        sm = np.zeros_like(e); v = 0.0
        for i, x in enumerate(e):
            v = v + (x - v) * (0.75 if x > v else 0.25)
            sm[i] = v
        res[spk] = sm
    return res


# ------------------------------------------------------------------ loudness
def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    return float(j["input_i"]), float(j["input_tp"]), float(j["input_lra"])


def tp_limit(x, ceiling_db=-2.0, release_s=0.08):
    """True-peak limiter: gain computed on 4x oversampled peaks, applied with lookahead."""
    up = resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(x)]
    if len(pk) < len(x):
        pk = np.pad(pk, (0, len(x) - len(pk)))
    c = db(ceiling_db)
    need = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    la = int(0.005 * SR)
    # lookahead: min over a window, then smooth release
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1)
    v = 1.0
    # vectorised one-pole release: process in blocks of 64 samples
    B = 64; nb = int(math.ceil(len(g) / B))
    gb = np.pad(g, (0, nb * B - len(g)), constant_values=1).reshape(nb, B).min(1)
    sb = np.empty(nb); rb = 1 - math.exp(-B / (release_s * SR))
    for i in range(nb):
        v = gb[i] if gb[i] < v else v + (gb[i] - v) * rb
        sb[i] = v
    out = np.repeat(sb, B)[:len(g)]
    out = np.minimum(out, g)
    return (x * out[:, None]).astype(np.float32)


def min_window_db(x, win=0.1):
    k = int(win * SR); n = len(x) // k
    r = np.sqrt((x[:n * k].reshape(n, k, -1) ** 2).mean((1, 2)) + 1e-20)
    return round(float(20 * np.log10(r.min())), 1)


def silent_windows(x, win=0.1, thr_db=-90.0):
    """[start, end] spans (s) where the mix is effectively digital silence."""
    k = int(win * SR); n = len(x) // k
    r = 20 * np.log10(np.sqrt((x[:n * k].reshape(n, k, -1) ** 2).mean((1, 2)) + 1e-20))
    out = []; a = None
    for i, v in enumerate(r):
        if v < thr_db and a is None:
            a = i
        if v >= thr_db and a is not None:
            out.append([round(a * win, 1), round(i * win, 1)]); a = None
    if a is not None:
        out.append([round(a * win, 1), round(n * win, 1)])
    return out


def write_wav(path, x):
    import soundfile as sf
    sf.write(path, x, SR, subtype="FLOAT")


# ------------------------------------------------------------------ the mix
def build(spec, shots_timeline, total_s, fps, resolve, workdir, log):
    """Returns dict(wav=path, lines=[...], env={speaker: array}, report={...})."""
    n = int(math.ceil(total_s * SR))
    dlg = np.zeros((n, 2), np.float32); mus = np.zeros((n, 2), np.float32); fx = np.zeros((n, 2), np.float32)
    fx_noduck = np.zeros((n, 2), np.float32)
    dspec = spec.get("dialogue")
    if dspec and dspec.get("lines") is not None:
        lines = load_conformed(dspec, resolve, log)
    else:
        lines = load_dialogue(dspec, resolve, log) if dspec else []
    wet = np.zeros((n, 2), np.float32)
    for ln in lines:
        place(dlg, np.stack([ln["audio"]] * 2, 1), ln["start"], 1.0)
        if ln.get("wet") is not None:
            place(wet, ln["wet"], ln["start"], 1.0)
    dg = db(dspec.get("gain_db", 0)) if dspec else 1.0
    if dspec and dspec.get("anchor_lufs") is not None and lines:
        tmp = os.path.join(workdir, "dlg_only.wav"); write_wav(tmp, dlg)
        I0, _, _ = measure(tmp)
        dg = db(dspec["anchor_lufs"] - I0)
        log.append(f"dialogue bus {I0:.1f} LUFS dry -> anchored at {dspec['anchor_lufs']} LUFS (gain {dspec['anchor_lufs'] - I0:+.1f} dB)")
    dlg *= dg; wet *= dg
    # cues: global lists + per-shot cues (at = seconds from shot start)
    cues = [dict(c, bus="music") for c in spec.get("music", [])] + [dict(c, bus="sfx") for c in spec.get("sfx", [])]
    for sh, st in shots_timeline:
        for c in sh.get("music", []):
            cues.append(dict(c, bus="music", start_s=st + c.get("at", 0.0)))
        for c in sh.get("sfx", []):
            cues.append(dict(c, bus="sfx", start_s=st + c.get("at", 0.0)))
    for i, c in enumerate(cues):
        p = resolve(c["src"]) if c.get("src") else None
        if p and os.path.exists(p):
            x = decode(p)
        elif c.get("placeholder"):
            x = synth(c["placeholder"], seed=i + 1)
            log.append(f"PLACEHOLDER sfx '{c.get('id', c['placeholder'])}' at {c['start_s']:.2f}s"
                       + (f" (expected {c['src']})" if c.get("src") else ""))
        else:
            log.append(f"WARNING missing audio cue {c.get('id')} {c.get('src')}")
            continue
        if c.get("in_s") or c.get("out_s"):
            x = x[int(c.get("in_s", 0.0) * SR):int(c["out_s"] * SR) if c.get("out_s") else None]
        if c.get("loop_s"):
            reps = int(math.ceil(c["loop_s"] * SR / len(x)))
            x = np.concatenate([x] * reps)[:int(c["loop_s"] * SR)]
        if c.get("trim_s"):
            x = x[:int(c["trim_s"] * SR)]
        x = fade(x.copy(), c.get("fade_in", 0.0), c.get("fade_out", 0.0))
        bus = mus if c["bus"] == "music" else (fx if c.get("duck", True) else fx_noduck)
        if c["bus"] == "music" and not c.get("duck", True):
            bus = fx_noduck
        place(bus, x, c["start_s"], db(c.get("gain_db", 0.0)))
    # keyframed ducking from dialogue activity (attack 60 ms, release 450 ms)
    hop = 480
    k = n // hop
    act = np.sqrt((dlg[:k * hop, 0].reshape(k, hop) ** 2).mean(1)) > db(-42)
    g = np.zeros(k, np.float32); v = 0.0
    a_up = 1 - math.exp(-hop / (0.06 * SR)); a_dn = 1 - math.exp(-hop / (0.45 * SR))
    for i in range(k):
        v += (act[i] - v) * (a_up if act[i] > v else a_dn); g[i] = v
    duck = spec.get("duck", {})
    gm = 1 - (1 - db(duck.get("music_db", -12))) * g
    gf = 1 - (1 - db(duck.get("sfx_db", -6))) * g
    gm = np.pad(np.repeat(gm, hop), (0, n - k * hop), mode="edge")[:, None]
    gf = np.pad(np.repeat(gf, hop), (0, n - k * hop), mode="edge")[:, None]
    if duck.get("mode") == "band":
        # opt-in (28 Nov audio upgrade): duck the music deeper in the speech band (speech_db) than
        # outside it (broad_db), so the score keeps its body and air under dialogue. Default stays broadband.
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music"))
        import dsp as _dsp
        key = np.pad(np.repeat(g, hop), (0, n - k * hop), mode="edge").astype(np.float32)
        mus_b, _ = _dsp.band_duck(mus, key, duck.get("speech_db", -9.0), duck.get("broad_db", -4.0),
                                  attack_s=0.01, release_s=0.05)
        gm = 1.0
        mus = mus_b
    mix = dlg + wet + mus * gm + fx * gf + fx_noduck
    buses = {}
    for nm, b in (("dialogue", dlg + wet), ("music", mus * gm), ("effects", fx * gf + fx_noduck)):
        try:
            tp_ = os.path.join(workdir, f"bus_{nm}.wav"); write_wav(tp_, b)
            buses[nm] = round(measure(tp_)[0], 1)
        except Exception:
            buses[nm] = None
    raw = os.path.join(workdir, "mix_raw.wav"); write_wav(raw, mix)
    I, TP, LRA = measure(raw)
    tgt = spec.get("loudness", {}).get("integrated", -16.0)
    ceil = spec.get("loudness", {}).get("true_peak_ceiling", -2.0)
    mix2 = mix * db(tgt - I)
    for it in range(3):
        mix2 = tp_limit(mix2, ceil)
        fin = os.path.join(workdir, "mix.wav"); write_wav(fin, mix2)
        I2, TP2, LRA2 = measure(fin)
        if abs(I2 - tgt) < 0.3 and TP2 < -1.5:
            break
        mix2 = mix2 * db(tgt - I2)
    g_fin = (I2 - I) if I > -70 else 0.0
    rep = dict(raw_lufs=I, final_lufs=I2, final_true_peak_dbtp=TP2, lra=LRA2, duck_music_db=duck.get("music_db", -12),
               bus_lufs_before_master_gain=buses, master_gain_db=round(tgt - I, 2),
               min_level_dbfs_100ms=min_window_db(mix2), digital_silence_windows=silent_windows(mix2))
    env = envelopes(lines, total_s, fps)
    return dict(wav=fin, lines=lines, env=env, report=rep)


def srt(lines, path, max_chars=42):
    def ts(t):
        t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    def wrap(txt):
        words = txt.split(); a = []; cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > max_chars and cur:
                a.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        a.append(cur)
        if len(a) > 2:    # rebalance into two lines
            mid = len(words) // 2
            a = [" ".join(words[:mid]), " ".join(words[mid:])]
        return "\n".join(a)
    out = []
    for i, ln in enumerate(sorted([l for l in lines if l.get("sub", True)], key=lambda x: x["start"]), 1):
        st = ln["start"] + 0.03; en = max(st + 0.8, ln["start"] + ln["dur"] - 0.03)
        out.append(f"{i}\n{ts(st)} --> {ts(en)}\n{wrap(ln['text'].replace('—', '–'))}\n")
    open(path, "w", encoding="utf-8").write("\n".join(out))
