"""sfzr - a small offline SFZ sampler + mixer in numpy (Route A, v2 sound).

Why: sfizz is not packaged for this machine and could not be fetched, so this
renders SFZ instruments (Virtual Playing Orchestra 3 = SSO + VSCO-2 CE + No Budget
Orchestra + Iowa samples) directly from MIDI written by sulib.

Supported SFZ subset (enough for VPO 3 non-keyswitch patches):
  <control> default_path, <global>/<master>/<group>/<region> inheritance, #include,
  sample, key/lokey/hikey, pitch_keycenter, lovel/hivel, tune, transpose, volume,
  pan, amp_veltrack, amp_random, pitch_random, delay, delay_random, offset,
  ampeg_delay/attack/hold/decay/sustain/release (+ vel2attack, vel2release),
  seq_length/seq_position (round robin), loop_mode (one_shot / loop_continuous
  using the WAV 'smpl' loop), xfin/xfout key + velocity crossfades,
  trigger=release regions are skipped. Unknown opcodes are ignored.
Extras: articulation switching by note length (short -> staccato patch), pitch-bend
  (time-varying resampling), CC7/CC11 gain curves, an auto crossfade-loop for long
  notes on unlooped sustains, and a synthetic stereo hall (convolution).
"""
import os
import re
import struct
import random
import functools

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
NOTE_RE = re.compile(r"^([a-gA-G])([#b]?)(-?\d+)$")
NOTE_OFS = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def key_num(v):
    v = str(v).strip()
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    m = NOTE_RE.match(v)
    if not m:
        raise ValueError(v)
    n, acc, octv = m.groups()
    return NOTE_OFS[n.lower()] + (1 if acc == "#" else -1 if acc == "b" else 0) + (int(octv) + 1) * 12


# ---------------------------------------------------------------- parsing
def _read_lines(path, seen=None):
    seen = seen or set()
    base = os.path.dirname(path)
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.split("//")[0].strip()
            if not line:
                continue
            m = re.match(r'#include\s+"([^"]+)"', line)
            if m:
                inc = os.path.normpath(os.path.join(base, m.group(1).replace("\\", "/")))
                if inc not in seen and os.path.exists(inc):
                    seen.add(inc)
                    out += _read_lines(inc, seen)
                continue
            if line.startswith("#"):
                continue
            out.append(line)
    return out


@functools.lru_cache(maxsize=None)
def parse_sfz(path):
    """Return list of region dicts (opcodes merged from headers)."""
    base = os.path.dirname(path)
    levels = {"control": {}, "global": {}, "master": {}, "group": {}}
    regions, cur, cur_hdr = [], None, None
    order = ["control", "global", "master", "group"]

    def flush():
        if cur_hdr == "region" and cur is not None:
            r = {}
            for lv in order:
                r.update(levels[lv])
            r.update(cur)
            if "sample" in r and r.get("trigger", "attack") == "attack":
                regions.append(r)

    for line in _read_lines(path):
        # split into header tokens and opcode text
        parts = re.split(r"(<[a-z]+>)", line)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            hm = re.fullmatch(r"<([a-z]+)>", part)
            if hm:
                flush()
                cur_hdr = hm.group(1)
                if cur_hdr in levels:
                    idx = order.index(cur_hdr)
                    for lv in order[idx:]:
                        levels[lv] = {}
                    cur = levels[cur_hdr]
                elif cur_hdr == "region":
                    cur = {}
                else:
                    cur = {}
                continue
            if cur is None:
                continue
            # 'sample=' may contain spaces: take the rest of the text
            if "sample=" in part:
                pre, samp = part.split("sample=", 1)
                for kv in pre.split():
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        cur[k] = v
                # the sample path runs until another opcode 'xxx=' appears
                m = re.search(r"\s+[a-z_0-9]+=", samp)
                if m:
                    rest = samp[m.start():]
                    samp = samp[:m.start()]
                    for kv in rest.split():
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            cur[k] = v
                cur["sample"] = samp.strip()
            else:
                for kv in part.split():
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        cur[k] = v
    flush()
    out = []
    for r in regions:
        dp = r.get("default_path", "")
        sp = (dp + r["sample"]).replace("\\", "/")
        r = dict(r)
        r["_path"] = os.path.normpath(os.path.join(base, sp))
        if "key" in r:
            k = key_num(r["key"])
            r.setdefault("lokey", k)
            r.setdefault("hikey", k)
            r.setdefault("pitch_keycenter", k)
        r["_lokey"] = key_num(r.get("lokey", 0))
        r["_hikey"] = key_num(r.get("hikey", 127))
        r["_center"] = key_num(r.get("pitch_keycenter", 60))
        r["_lovel"] = int(r.get("lovel", 0))
        r["_hivel"] = int(r.get("hivel", 127))
        out.append(r)
    return out


# ---------------------------------------------------------------- samples
def _smpl_loop(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        i = data.find(b"smpl")
        if i < 0:
            return None
        n_loops = struct.unpack("<I", data[i + 36:i + 40])[0]
        if n_loops < 1:
            return None
        ls, le = struct.unpack("<II", data[i + 52:i + 60])
        return int(ls), int(le)
    except Exception:
        return None


@functools.lru_cache(maxsize=4096)
def load_sample(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2].copy(), sr, _smpl_loop(path)


def auto_loop(x, sr, xf=0.12):
    """Crossfade-loop the second half of an unlooped sustain (for long notes)."""
    n = len(x)
    ls, le = int(n * 0.45), int(n - sr * 0.35)
    f = int(sr * xf)
    if le - ls < 3 * f:
        return None, None
    y = x.copy()
    ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
    # blend the end of the loop into the material just before loop start
    y[le - f:le] = x[le - f:le] * (1 - ramp) + x[ls - f:ls] * ramp
    return y, (ls, le)


# ---------------------------------------------------------------- instrument
class Instrument:
    """One or more SFZ patches; `short` patch used for notes shorter than `short_s`."""

    def __init__(self, long_sfz, short_sfz=None, short_s=0.22, gain_db=0.0, transpose=0):
        self.long = parse_sfz(long_sfz)
        self.short = parse_sfz(short_sfz) if short_sfz else None
        self.short_s = short_s
        self.gain = 10 ** (gain_db / 20)
        self.transpose = transpose
        self.rr = {}

    def regions_for(self, key, vel, dur):
        regs = self.short if (self.short and dur < self.short_s) else self.long
        cand = [r for r in regs if r["_lokey"] <= key <= r["_hikey"] and r["_lovel"] <= vel <= r["_hivel"]]
        if not cand:   # nearest key fallback
            cand = sorted(regs, key=lambda r: min(abs(r["_lokey"] - key), abs(r["_hikey"] - key)))[:1]
        seqs = [r for r in cand if "seq_length" in r]
        if seqs:
            L = int(seqs[0]["seq_length"])
            c = self.rr.get((id(regs), key), 0)
            self.rr[(id(regs), key)] = c + 1
            pos = c % L + 1
            cand = [r for r in cand if int(r.get("seq_position", 1)) == pos] or cand[:1]
        return cand


def _f(r, k, d=0.0):
    try:
        return float(r.get(k, d))
    except ValueError:
        return d


def _xfade_gain(r, key, vel):
    g = 1.0
    for lo, hi, val, up in (("xfin_lokey", "xfin_hikey", key, True), ("xfout_lokey", "xfout_hikey", key, False),
                            ("xfin_lovel", "xfin_hivel", vel, True), ("xfout_lovel", "xfout_hivel", vel, False)):
        if lo in r and hi in r:
            a = key_num(r[lo]) if "key" in lo else int(r[lo])
            b = key_num(r[hi]) if "key" in hi else int(r[hi])
            if b > a:
                t = min(1.0, max(0.0, (val - a) / (b - a)))
                t = t if up else 1 - t
                g *= np.sqrt(t)   # power crossfade
    return g


def render_note(inst, key, vel, start, dur, bend_fn, rng, extra_release=None):
    """Return (start_sample, stereo array) for one note."""
    out = None
    for r in inst.regions_for(key, vel, dur):
        x, ssr, loop = load_sample(r["_path"])
        semis = key + inst.transpose - r["_center"] + _f(r, "transpose") + _f(r, "tune") / 100.0
        semis += rng.uniform(-1, 1) * _f(r, "pitch_random") / 100.0
        delay = _f(r, "delay") + _f(r, "ampeg_delay") + rng.uniform(0, _f(r, "delay_random"))
        att = max(0.002, _f(r, "ampeg_attack", 0.002) + _f(r, "ampeg_vel2attack") * vel / 127)
        hold = _f(r, "ampeg_hold")
        dec = _f(r, "ampeg_decay")
        sus = _f(r, "ampeg_sustain", 100.0) / 100.0
        rel = max(0.03, _f(r, "ampeg_release", 0.05) + _f(r, "ampeg_vel2release") * vel / 127)
        if extra_release:
            rel = max(rel, extra_release)
        one_shot = r.get("loop_mode") == "one_shot"
        mode = r.get("loop_mode")
        if mode is None:
            mode = "loop_continuous" if loop else "no_loop"
        lp = None
        if mode in ("loop_continuous", "loop_sustain") and loop and loop[1] > loop[0] + 100:
            lp = loop
        total = (dur + rel) if not one_shot else None
        base_ratio = ssr / SR
        n_out = int((total if total else (len(x) / ssr) / (2 ** (semis / 12))) * SR) + 1
        if not one_shot and lp is None:
            need = (dur + rel) * SR * (2 ** (semis / 12)) * base_ratio + _f(r, "offset")
            if need > len(x):
                y, lpp = auto_loop(x, ssr)
                if lpp:
                    x, lp = y, lpp
        t = np.arange(n_out) / SR
        bend = bend_fn(start + delay + t) if bend_fn else 0.0
        ratio = base_ratio * 2 ** ((semis + bend / 100.0) / 12)
        pos = _f(r, "offset") + np.concatenate([[0.0], np.cumsum(ratio[:-1] if np.ndim(ratio) else
                                                                  np.full(n_out - 1, ratio))])
        if lp:
            ls, le = lp
            over = pos > le
            if over.any():
                pos[over] = ls + np.mod(pos[over] - ls, le - ls)
        valid = pos < len(x) - 1
        pos = pos[valid]
        if len(pos) < 8:
            continue
        i0 = pos.astype(np.int64)
        fr = (pos - i0).astype(np.float32)[:, None]
        y = x[i0] * (1 - fr) + x[i0 + 1] * fr
        n = len(y)
        # amplitude envelope
        env = np.ones(n, dtype=np.float32)
        a = int(att * SR)
        env[:min(a, n)] = np.linspace(0, 1, min(a, n), dtype=np.float32) if a else 1
        h = a + int(hold * SR)
        if dec > 0 and h < n:
            d = int(dec * SR)
            seg = np.arange(min(d, n - h))
            env[h:h + len(seg)] = 1 - (1 - sus) * seg / max(1, d)
            env[h + len(seg):] = sus
        if not one_shot:
            off = int(dur * SR)
            if off < n:
                lvl = env[off]
                rs = np.arange(n - off)
                env[off:] = lvl * np.exp(-rs / (rel * SR / 4.6))   # -40 dB at 'rel'
        y = y * env[:, None]
        # gain: volume, velocity, random, xfades, pan
        vt = _f(r, "amp_veltrack", 100.0) / 100.0
        vel_db = 20 * np.log10(max(vel, 1) / 127.0) * 2 * vt
        g_db = _f(r, "volume") + vel_db + rng.uniform(-1, 1) * _f(r, "amp_random")
        g = 10 ** (g_db / 20) * _xfade_gain(r, key, vel) * inst.gain
        pan = _f(r, "pan") / 100.0
        y = y * g
        if pan:
            y[:, 0] *= np.sqrt((1 - pan) / 2) * np.sqrt(2)
            y[:, 1] *= np.sqrt((1 + pan) / 2) * np.sqrt(2)
        d0 = int(delay * SR)
        if d0:
            y = np.concatenate([np.zeros((d0, 2), np.float32), y])
        if out is None:
            out = y
        else:
            m = max(len(out), len(y))
            o = np.zeros((m, 2), np.float32)
            o[:len(out)] += out
            o[:len(y)] += y
            out = o
    return out


# ---------------------------------------------------------------- tracks
def curve_fn(events, default, total):
    """events: [(time, value)] -> vectorised step-with-ramp function."""
    if not events:
        return lambda t: np.full(np.shape(t), default, dtype=np.float32)
    ts = np.array([e[0] for e in events])
    vs = np.array([e[1] for e in events], dtype=np.float32)
    return lambda t: np.interp(t, ts, vs, left=vs[0], right=vs[-1]).astype(np.float32)


def render_track(inst, pm_inst, length_s, seed=0, release=None, vel_scale=1.0):
    rng = random.Random(seed)
    buf = np.zeros((int(length_s * SR) + SR, 2), np.float32)
    bends = [(b.time, b.pitch / 8191 * 200.0) for b in pm_inst.pitch_bends]
    bend_fn = curve_fn(bends, 0.0, length_s) if bends else None
    for n in sorted(pm_inst.notes, key=lambda n: n.start):
        v = int(min(127, max(1, n.velocity * vel_scale)))
        y = render_note(inst, n.pitch, v, n.start, n.end - n.start, bend_fn, rng, release)
        if y is None:
            continue
        s = int(n.start * SR)
        e = min(len(buf), s + len(y))
        buf[s:e] += y[:e - s]
    # CC7 * CC11 gain curve
    t = np.arange(len(buf)) / SR
    cc7 = [(c.time, c.value) for c in pm_inst.control_changes if c.number == 7]
    cc11 = [(c.time, c.value) for c in pm_inst.control_changes if c.number == 11]
    g = (curve_fn(cc7, 100, length_s)(t) / 127.0) ** 2 * (curve_fn(cc11, 127, length_s)(t) / 127.0) ** 2
    return buf * g[:, None]


def pan_stereo(x, pan):
    """pan: -1..1, constant-power, applied to a stereo stem (balance)."""
    if not pan:
        return x
    l = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    r = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    return x * np.array([min(1, l), min(1, r)], np.float32)


# ---------------------------------------------------------------- reverb
@functools.lru_cache(maxsize=4)
def hall_ir(rt60=2.6, predelay=0.022, seed=3, size=1.0):
    """Synthetic stereo hall IR: sparse early reflections + band-dependent decaying noise."""
    rng = np.random.default_rng(seed)
    n = int((rt60 * 1.2 + predelay) * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    # late field: 4 bands, highs decay faster
    bands = [(20, 250, 1.15), (250, 1500, 1.0), (1500, 5000, 0.72), (5000, 16000, 0.45)]
    for lo, hi, k in bands:
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        for ch in range(2):
            noise = sosfilt(sos, rng.standard_normal(n)).astype(np.float32)
            ir[:, ch] += noise * np.exp(-6.91 * t / (rt60 * k))
    onset = np.clip((t - predelay) / 0.04, 0, 1) ** 2
    ir *= onset[:, None]
    # early reflections
    for _ in range(18):
        d = predelay + rng.uniform(0.005, 0.08) * size
        a = rng.uniform(0.2, 0.6) * np.exp(-d * 12)
        ir[int(d * SR), rng.integers(0, 2)] += a
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True))
    return ir


def reverb(x, rt60=2.6, predelay=0.022):
    ir = hall_ir(rt60, predelay)
    y = np.stack([fftconvolve(x[:, 0], ir[:, 0]), fftconvolve(x[:, 1], ir[:, 1])], axis=1)
    return y[:len(x)].astype(np.float32)


def write_wav(path, x):
    sf.write(path, x, SR, subtype="FLOAT")
