"""SECRET UNIVERSE - tiny score-as-code library (Route A).

Write notes in beats, get a humanised General-MIDI file, render it with
FluidSynth + FluidR3_GM (MIT licence), then master with sox/ffmpeg to
MP3 192k at about -16 LUFS, plus a small spectrogram JPG and a stats file.

Notation for melody strings (used by Cue.seq):
    "D5:q A4:q D5:e E5:e F5:q | E5:h. r:q"
  pitch:duration, r = rest, '|' is only a visual bar line.
  w=4 h=2 q=1 e=1/2 s=1/4 t=1/3 (triplet eighth) x=1/6, trailing '.' = dotted.
  A '~' prefix on a token (e.g. "~E5:q") makes it slur-legato (overlap).
"""
import os
import random
import subprocess
import json

import pretty_midi

SF2 = os.environ.get("SU_SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
SCRATCH = os.environ.get(
    "SU_SCRATCH",
    "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/music",
)
REPO = "/home/user/Universe-Series"
OUT_DIR = os.path.join(REPO, "samples", "music")
MIDI_DIR = os.path.join(OUT_DIR, "midi")

DUR = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25, "t": 1 / 3, "x": 1 / 6}

# General MIDI programs (0-indexed) we use
GM = dict(piano=0, harpsichord=6, celesta=8, glock=9, marimba=12, nylon=24,
          violin=40, viola=41, cello=42, contrabass=43, trem=44, pizz=45,
          harp=46, timpani=47, strings=48, strings2=49, choir=52, ohit=55,
          trumpet=56, trombone=57, tuba=58, horn=60, brass=61, oboe=68,
          ehorn=69, bassoon=70, clarinet=71, piccolo=72, flute=73,
          recorder=74, panflute=75, shakuhachi=77, whistle=78, sitar=104,
          banjo=105, shamisen=106, koto=107, kalimba=108, shanai=111,
          taiko=116, melotom=117, revcym=119, accordion=21, tuba2=58)

# GM drum-kit note numbers (channel 10)
DR = dict(kick=36, kick2=35, snare=38, rim=37, clap=39, hatc=42, hatp=44,
          hato=46, crash=49, ride=51, china=52, tamb=54, splash=55, cow=56,
          crash2=57, bongo_hi=60, bongo_lo=61, conga_mute=62, conga_hi=63,
          conga_lo=64, timb_hi=65, timb_lo=66, agogo_hi=67, agogo_lo=68,
          cabasa=69, maracas=70, claves=75, wood_hi=76, wood_lo=77,
          cuica_mute=78, cuica=79, tri_mute=80, tri=81, shaker=82,
          tom_lo=45, tom_mid=47, tom_hi=50, floor=41)


def pitch(name):
    return pretty_midi.note_name_to_number(name)


def parse(s):
    """Yield (pitch|None, dur_beats, slur) from a melody string."""
    for tok in s.split():
        if tok == "|":
            continue
        slur = tok.startswith("~")
        tok = tok.lstrip("~")
        p, d = tok.split(":")
        dots = d.count(".")
        base = DUR[d.rstrip(".")]
        dur = base * (1.5 if dots == 1 else 1.75 if dots == 2 else 1.0)
        yield (None if p == "r" else pitch(p)), dur, slur


class Cue:
    def __init__(self, name, bpm, beats_per_bar=4, seed=1, rit=None):
        """rit = (start_beat, end_beat, final_bpm): linear ritardando."""
        self.name, self.bpm, self.bpb = name, bpm, beats_per_bar
        self.rng = random.Random(seed)
        self.pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        self.tracks = {}
        self.rit = rit
        self.next_ch = 0

    # ---- time -------------------------------------------------------
    def t(self, beat):
        """Beat -> seconds, honouring an optional linear ritardando."""
        spb = 60.0 / self.bpm
        if not self.rit or beat <= self.rit[0]:
            return beat * spb
        b0, b1, bpm1 = self.rit
        base = b0 * spb
        # integrate 60/bpm(b) with bpm linear from self.bpm to bpm1 over b0..b1
        n = 64
        span = min(beat, b1) - b0
        acc = 0.0
        for i in range(n):
            x = b0 + span * (i + 0.5) / n
            bpm = self.bpm + (bpm1 - self.bpm) * (x - b0) / (b1 - b0)
            acc += (60.0 / bpm) * span / n
        if beat > b1:
            acc += (beat - b1) * 60.0 / bpm1
        return base + acc

    def bar(self, n):
        """1-based bar number -> beat."""
        return (n - 1) * self.bpb

    # ---- tracks -----------------------------------------------------
    def track(self, key, program, vol=100, pan=64, reverb=60, chorus=0, drums=False):
        if drums:
            ch = 9
        else:
            ch = self.next_ch
            self.next_ch += 1
            if self.next_ch == 9:
                self.next_ch = 10
        inst = pretty_midi.Instrument(program=0 if drums else program, is_drum=drums, name=key)
        inst._su_channel = ch
        self.pm.instruments.append(inst)
        self.tracks[key] = inst
        for cc, v in ((7, vol), (10, pan), (91, reverb), (93, chorus), (11, 127)):
            inst.control_changes.append(pretty_midi.ControlChange(cc, v, 0.0))
        return inst

    # ---- notes ------------------------------------------------------
    def note(self, key, p, beat, dur, vel=80, human=True, legato=0.92):
        inst = self.tracks[key]
        if isinstance(p, str):
            p = pitch(p)
        jitter = self.rng.gauss(0, 0.009) if human else 0.0
        s = max(0.0, self.t(beat) + jitter)
        e = self.t(beat + dur * legato)
        if e <= s + 0.02:
            e = s + 0.05
        v = int(max(1, min(127, vel + (self.rng.randint(-5, 5) if human else 0))))
        inst.notes.append(pretty_midi.Note(velocity=v, pitch=int(p), start=s, end=e))

    def chord(self, key, ps, beat, dur, vel=75, roll=0.0, legato=0.97):
        for i, p in enumerate(ps):
            self.note(key, p, beat + i * roll, dur - i * roll, vel, legato=legato)

    def seq(self, key, s, beat, vel=80, transpose=0, legato=0.92, curve=None):
        """Lay a melody string; curve(frac)->velocity offset for phrase shape.
        Returns beat after the last token."""
        items = list(parse(s))
        total = sum(d for _, d, _ in items) or 1
        b = beat
        for p, d, slur in items:
            if p is not None:
                off = curve((b - beat) / total) if curve else 0
                self.note(key, p + transpose, b, d, vel + off,
                          legato=1.05 if slur else legato)
            b += d
        return b

    def hit(self, drum, beat, vel=90, dur=0.25, key="drums"):
        self.note(key, DR[drum] if isinstance(drum, str) else drum, beat, dur, vel)

    # ---- controllers -----------------------------------------------
    def cc_ramp(self, key, cc, b0, b1, v0, v1, steps=24):
        inst = self.tracks[key]
        for i in range(steps + 1):
            f = i / steps
            inst.control_changes.append(pretty_midi.ControlChange(
                cc, int(round(v0 + (v1 - v0) * f)), self.t(b0 + (b1 - b0) * f)))

    def swell(self, key, b0, b1, v0, v1):
        self.cc_ramp(key, 11, b0, b1, v0, v1)

    def bend(self, key, b0, b1, c0, c1, steps=12):
        """Pitch-bend glide in cents (GM default range +/-200 cents)."""
        inst = self.tracks[key]
        for i in range(steps + 1):
            f = i / steps
            cents = c0 + (c1 - c0) * f
            inst.pitch_bends.append(pretty_midi.PitchBend(
                int(max(-8192, min(8191, cents / 200.0 * 8191))), self.t(b0 + (b1 - b0) * f)))

    # ---- output -----------------------------------------------------
    def write_midi(self):
        os.makedirs(MIDI_DIR, exist_ok=True)
        path = os.path.join(MIDI_DIR, self.name + ".mid")
        for inst in self.pm.instruments:
            inst.control_changes.sort(key=lambda c: c.time)
            inst.pitch_bends.sort(key=lambda c: c.time)
        self.pm.write(path)
        fix_channels(path, [i._su_channel for i in self.pm.instruments])
        return path

    def render(self, tail=4.0, gain=0.5, sox_fx=None, keep_wav=False):
        mid = self.write_midi()
        os.makedirs(SCRATCH, exist_ok=True)
        raw = os.path.join(SCRATCH, self.name + "-raw.wav")
        fx = os.path.join(SCRATCH, self.name + "-fx.wav")
        mp3 = os.path.join(OUT_DIR, self.name + ".mp3")
        subprocess.run([
            "fluidsynth", "-ni", "-q", "-g", str(gain), "-r", "48000", "-F", raw,
            "-o", "synth.reverb.room-size=0.85", "-o", "synth.reverb.damp=0.35",
            "-o", "synth.reverb.width=1.0", "-o", "synth.reverb.level=0.75",
            "-o", "synth.polyphony=512", SF2, mid], check=True)
        dur = self.pm.get_end_time() + tail
        # space + tone: hall reverb, gentle low-cut, small low-mid dip, air shelf, glue compression
        chain = sox_fx or ["highpass", "28", "equalizer", "300", "1.2q", "-2",
                           "treble", "+2", "8000", "reverb", "35", "45", "90", "100", "15",
                           "compand", "0.02,0.25", "6:-40,-30,-12,-10,0,-6", "-2", "-60", "0.05"]
        subprocess.run(["sox", "-q", raw, fx, "trim", "0", f"{dur:.2f}"] + chain +
                       ["fade", "t", "0.02", f"{dur:.2f}", "2.5"], check=True)
        master(fx, mp3)
        stats = analyse(mp3, os.path.join(OUT_DIR, "spectrograms", self.name + ".jpg"))
        if not keep_wav:
            for p in (raw,):
                os.remove(p)
        print(json.dumps({self.name: stats}, indent=1))
        return mp3, stats


def fix_channels(path, channels):
    """pretty_midi assigns channels itself; force ours so CCs map 1:1."""
    import mido
    mf = mido.MidiFile(path)
    # track 0 is tempo/meta, instrument tracks follow in order
    for tr, ch in zip(mf.tracks[1:], channels):
        for msg in tr:
            if hasattr(msg, "channel"):
                msg.channel = ch
    mf.save(path)


def master(wav, mp3, target=-16.0):
    """Two-pass EBU R128 loudnorm to target LUFS, -1.5 dBTP, MP3 192k."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af",
                        f"loudnorm=I={target}:TP=-1.5:LRA=14:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    m = json.loads(txt)
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=14:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav,
                    "-af", af + ",aresample=48000", "-ar", "48000", "-c:a", "libmp3lame",
                    "-b:a", "192k", mp3], check=True)


def analyse(mp3, jpg):
    """Objective checks: loudness, true peak, clipping count, duration, band balance."""
    os.makedirs(os.path.dirname(jpg), exist_ok=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp3, "-af",
                        "ebur128=peak=true,astats=measure_overall=Peak_level+RMS_level+Number_of_clipped_samples+Flat_factor:measure_perchannel=none",
                        "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr
    out = {}
    summ = err[err.rfind("Summary:"):]
    for line in summ.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            out["lufs_I"] = float(line.split()[1])
        elif line.startswith("LRA:"):
            out["LRA"] = float(line.split()[1])
        elif line.startswith("Peak:"):
            out["true_peak_dBTP"] = float(line.split()[1])
    for line in err.splitlines():
        if "Overall" in line:
            continue
        for k in ("Peak level dB", "RMS level dB", "Number of clipped samples"):
            if k in line and "] " in line:
                out[k] = line.split(":")[-1].strip()
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", mp3], capture_output=True, text=True)
    out["duration_s"] = round(float(p.stdout.strip()), 2)
    out["bands_dB"] = band_balance(mp3)
    png = jpg[:-4] + ".png"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", mp3,
                    "-lavfi", "showspectrumpic=s=800x300:legend=1:scale=log:fscale=log",
                    png], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", png,
                    "-q:v", "5", jpg], check=True)
    os.remove(png)
    return out


def band_balance(mp3):
    """RMS energy (dB, relative to total) in sub/low/mid/high/air bands."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar",
                        "24000", "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / 24000)
    tot = X.sum() + 1e-12
    bands = {"sub<60": (0, 60), "low60-250": (60, 250), "mid250-2k": (250, 2000),
             "hi2k-6k": (2000, 6000), "air>6k": (6000, 12000)}
    return {k: round(10 * float(np.log10(X[(f >= a) & (f < b)].sum() / tot + 1e-12)), 1)
            for k, (a, b) in bands.items()}
