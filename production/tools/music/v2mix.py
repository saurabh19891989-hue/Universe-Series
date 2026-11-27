"""v2 render: MIDI from sulib cues -> per-track stems -> hall reverb -> master.

Orchestra: Virtual Playing Orchestra 3 SFZ (SSO / VSCO-2 CE / No Budget Orchestra /
Iowa samples) rendered by sfzr.py. World colours (sitar, koto, shakuhachi, taiko,
nylon guitar, choir) and leftover GM drums: GeneralUser GS v2 SoundFont via FluidSynth,
rendered dry, one stem per track, then sent through the same hall.
"""
import os
import subprocess
import tempfile
import copy

import numpy as np
import pretty_midi

import sfzr
import sulib

SCR = sulib.SCRATCH
VPO = os.environ.get("SU_VPO", os.path.join(SCR, "libs/vpo_dl/x/Virtual-Playing-Orchestra3"))
GUGS = os.environ.get("SU_GUGS", os.path.join(SCR, "libs/gugs/GeneralUser-GS.sf2"))
V2_DIR = os.path.join(sulib.OUT_DIR, "v2")
SR = sfzr.SR


def P(rel):
    return os.path.join(VPO, rel)


# name -> (long sfz, short sfz, short threshold s, gain dB)
PRESETS = {
    "vln1": ("Strings/1st-violin-SEC-sustain.sfz", "Strings/1st-violin-SEC-staccato.sfz", 0.25, 0),
    "vln2": ("Strings/2nd-violin-SEC-sustain.sfz", "Strings/2nd-violin-SEC-staccato.sfz", 0.25, 0),
    "vla": ("Strings/viola-SEC-sustain.sfz", "Strings/viola-SEC-staccato.sfz", 0.25, 0),
    "vc": ("Strings/cello-SEC-sustain.sfz", "Strings/cello-SEC-staccato.sfz", 0.25, 0),
    "cb": ("Strings/bass-SEC-sustain.sfz", "Strings/bass-SEC-staccato.sfz", 0.25, 0),
    "vln_solo": ("Strings/1st-violin-SOLO-sustain.sfz", "Strings/1st-violin-SOLO-staccato.sfz", 0.2, 0),
    "vc_solo": ("Strings/cello-SOLO-sustain.sfz", "Strings/cello-SOLO-staccato.sfz", 0.2, 0),
    "pizz": ("Strings/all-strings-SEC-pizzicato.sfz", None, 0, 0),
    "trem": ("Strings/all-strings-SEC-tremolo.sfz", None, 0, 0),
    "harp": ("Strings/harp-sustain.sfz", None, 0, 0),
    "hn": ("Brass/french-horn-SEC-sustain.sfz", "Brass/french-horn-SEC-staccato.sfz", 0.3, 0),
    "tpt": ("Brass/trumpet-SEC-sustain.sfz", "Brass/trumpet-SEC-staccato.sfz", 0.3, 0),
    "tpt_solo": ("Brass/trumpet-SOLO-sustain.sfz", "Brass/trumpet-SOLO-staccato.sfz", 0.3, 0),
    "tbn": ("Brass/trombone-SEC-sustain.sfz", "Brass/trombone-SEC-staccato.sfz", 0.3, 0),
    "tuba": ("Brass/tuba-SOLO-sustain.sfz", "Brass/tuba-SOLO-staccato.sfz", 0.3, 0),
    "fl": ("Woodwinds/flute-SOLO-sustain.sfz", "Woodwinds/flute-SOLO-staccato.sfz", 0.18, 0),
    "picc": ("Woodwinds/piccolo-SOLO-sustain.sfz", "Woodwinds/piccolo-SOLO-staccato.sfz", 0.25, 0),
    "ob": ("Woodwinds/oboe-SOLO-sustain.sfz", "Woodwinds/oboe-SOLO-staccato.sfz", 0.2, 0),
    "cl": ("Woodwinds/clarinet-SOLO-sustain.sfz", "Woodwinds/clarinet-SOLO-staccato.sfz", 0.22, 0),
    "bsn": ("Woodwinds/bassoon-SOLO-sustain.sfz", "Woodwinds/bassoon-SOLO-staccato.sfz", 0.22, 0),
    "timp": ("Percussion/timpani-hit.sfz", None, 0, 0),
    "celesta": ("Keys/celesta.sfz", None, 0, 0),
    "glock": ("Percussion/glockenspiel.sfz", None, 0, 0),
    "cym": ("Percussion/cymbals.sfz", None, 0, 0),
    "bd": ("Percussion/bassdrum.sfz", None, 0, 0),
    "misc": ("Percussion/misc.sfz", None, 0, 0),
    "snare": ("Percussion/snare.sfz", None, 0, 0),
}

# GM drum note -> (VPO preset, key). Unlisted drum notes fall back to GeneralUser GS.
DRUM_MAP = {35: ("bd", 38), 36: ("bd", 36), 41: ("bd", 36), 45: ("bd", 36), 49: ("cym", 66), 57: ("cym", 66),
            52: ("cym", 68), 81: ("misc", 45), 80: ("misc", 44), 54: ("misc", 54), 56: ("misc", 56),
            62: ("misc", 63), 63: ("misc", 62), 64: ("misc", 64), 60: ("misc", 60), 61: ("misc", 61),
            38: ("snare", 50), 59: ("cym", 69)}

_INST = {}


def inst(name):
    if name not in _INST:
        lo, sh, th, g = PRESETS[name]
        _INST[name] = sfzr.Instrument(P(lo), P(sh) if sh else None, th, g)
    return _INST[name]


def active_rms_db(y, frame=0.05, window=30.0):
    """RMS (dB) over the frames where the stem is actually playing."""
    m = y.mean(axis=1)
    f = int(frame * SR)
    k = len(m) // f
    if k == 0:
        return -120.0
    p = (m[:k * f].reshape(k, f) ** 2).mean(axis=1) + 1e-12
    db = 10 * np.log10(p)
    act = p[db > db.max() - window]
    return float(10 * np.log10(act.mean()))


def gm_stem(pm_inst, length, gain=0.6, program=None, sf2=None, bank=0):
    """Render one GM track dry with GeneralUser GS (FluidSynth)."""
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    i = copy.deepcopy(pm_inst)
    if program is not None:
        i.program = program
    i.control_changes = [c for c in i.control_changes if c.number not in (91, 93, 10)]
    i.control_changes.append(pretty_midi.ControlChange(10, 64, 0))
    pm.instruments.append(i)
    with tempfile.TemporaryDirectory(dir=SCR) as td:
        mid, wav = os.path.join(td, "t.mid"), os.path.join(td, "t.wav")
        pm.write(mid)
        if bank:   # GS bank variation (e.g. 16/25 Mandolin, 8/6 Coupled Harpsichord)
            import mido
            mf = mido.MidiFile(mid)
            for tr in mf.tracks:
                for idx, msg in enumerate(tr):
                    if msg.type == "program_change":
                        tr.insert(idx, mido.Message("control_change", channel=msg.channel, control=0,
                                                    value=bank, time=msg.time))
                        msg.time = 0
                        break
            mf.save(mid)
        subprocess.run(["fluidsynth", "-ni", "-q", "-g", str(gain), "-r", str(SR), "-F", wav,
                        "-o", "synth.reverb.active=0", "-o", "synth.chorus.active=0",
                        "-o", "synth.polyphony=256", sf2 or GUGS, mid], check=True)
        x, _ = sfzr.sf.read(wav, dtype="float32", always_2d=True)
    n = int(length * SR) + SR
    out = np.zeros((n, 2), np.float32)
    out[:min(n, len(x))] = x[:n]
    return out


def render_cue(mid_path, mix, name, tail=4.0, rt60=2.6, sub_dir=V2_DIR, dialogue=False,
               stems_out=False, loud=-16.0):
    """mix: {track: dict(inst=preset | gm=True [program], gain=dB, pan=-1..1, send=0..1,
             release=s, vel=scale)}. Tracks not in mix use GM fallback."""
    pm = pretty_midi.PrettyMIDI(mid_path)
    length = pm.get_end_time() + tail
    stems, sends, mixbus = build_mix(pm, mix, length, rt60)
    os.makedirs(sub_dir, exist_ok=True)
    raw = os.path.join(SCR, name + "-v2-mix.wav")
    peak = np.abs(mixbus).max() + 1e-9
    sfzr.write_wav(raw, mixbus / peak * 0.5)
    outs = {}
    outs["main"] = finish(raw, os.path.join(sub_dir, name + ".mp3"), length, loud=loud)
    if dialogue:
        outs["dialogue"] = finish(raw, os.path.join(sub_dir, name + "-under-dialogue.mp3"), length,
                                  dialogue=True, loud=-20.0)
    if stems_out:
        for k2, y in stems.items():
            sfzr.write_wav(os.path.join(SCR, f"{name}-stem-{k2}.wav"), y / peak * 0.5)
    return outs, raw


BUS = ["highpass", "30", "equalizer", "250", "1.0q", "-1.5", "treble", "+1.5", "9000",
       "compand", "0.03,0.3", "6:-70,-70,-22,-22,0,-11", "0", "-60", "0.05"]
# dialogue-safe: clear the low end and carve the 1-4 kHz speech-intelligibility band
DIALOGUE = ["highpass", "-2", "120", "bass", "-4", "180", "equalizer", "1400", "1.2q", "-4",
            "equalizer", "2600", "0.9q", "-7", "equalizer", "4000", "1.5q", "-3",
            "compand", "0.03,0.3", "6:-70,-70,-24,-24,0,-14", "0", "-60", "0.05"]


def finish(raw, mp3, length, dialogue=False, loud=-16.0):
    fx = raw.replace(".wav", "-dlg-fx.wav" if dialogue else "-fx.wav")
    subprocess.run(["sox", "-q", raw, fx, "trim", "0", f"{length:.2f}"] + (DIALOGUE if dialogue else BUS) +
                   ["fade", "t", "0.01", f"{length:.2f}", "2.0"], check=True)
    sulib.master(fx, mp3, target=loud)
    jpg = os.path.join(os.path.dirname(mp3), "spectrograms", os.path.basename(mp3)[:-4] + ".jpg")
    st = sulib.analyse(mp3, jpg)
    os.remove(fx)
    return mp3, st


def build_mix(pm, mix, length, rt60=2.6):
    """Render every track to a stem, then sum dry + one shared hall. Returns (stems, sends, mixbus)."""
    n = int(length * SR) + SR
    dry = np.zeros((n, 2), np.float32)
    wet_in = np.zeros((n, 2), np.float32)
    stems, sends = {}, {}
    for k, pmi in enumerate(pm.instruments):
        spec = mix.get(pmi.name, {"gm": True})
        if spec.get("detune"):    # constant detune in cents (e.g. a harpsichord gone wrong)
            pmi = copy.deepcopy(pmi)
            off = spec["detune"] / 200.0 * 8191
            pmi.pitch_bends = [pretty_midi.PitchBend(int(off), 0.0)] + [
                pretty_midi.PitchBend(int(max(-8192, min(8191, b.pitch + off))), b.time) for b in pmi.pitch_bends]
        if pmi.is_drum:
            # split drum notes between VPO percussion and GU GS kit
            by_preset = {}
            rest = copy.deepcopy(pmi)
            rest.notes = []
            for nt in pmi.notes:
                if nt.pitch in DRUM_MAP and not spec.get("all_gm"):
                    pr, key = DRUM_MAP[nt.pitch]
                    nn = copy.copy(nt)
                    nn.pitch = key
                    by_preset.setdefault(pr, []).append(nn)
                else:
                    rest.notes.append(nt)
            y = np.zeros((n, 2), np.float32)
            for pr, notes in by_preset.items():
                tmp = pretty_midi.Instrument(0, name=pr)
                tmp.notes = notes
                tmp.control_changes = [c for c in pmi.control_changes if c.number in (7, 11)]
                s = sfzr.render_track(inst(pr), tmp, length, seed=k)
                y[:min(n, len(s))] += s[:n]
            if rest.notes:
                y += gm_stem(rest, length)[:n] * 10 ** (spec.get("gm_gain", -4) / 20)
        elif spec.get("gm"):
            y = gm_stem(pmi, length, program=spec.get("program"), bank=spec.get("bank", 0),
                       sf2=sulib.SF2 if spec.get("sf2") == "fluidr3" else None)[:n]
        else:
            s = sfzr.render_track(inst(spec["inst"]), pmi, length, seed=k,
                                  release=spec.get("release"), vel_scale=spec.get("vel", 1.0))
            y = np.zeros((n, 2), np.float32)
            y[:min(n, len(s))] = s[:n]
        if "lvl" in spec:          # auto-balance: active-RMS target in dBFS (pre-master)
            y = y * 10 ** ((spec["lvl"] - active_rms_db(y)) / 20)
        y = sfzr.pan_stereo(y * 10 ** (spec.get("gain", 0) / 20), spec.get("pan", 0))
        stems[pmi.name] = y
        dry += y
        wet_in += y * spec.get("send", 0.3)
        sends[pmi.name] = spec.get("send", 0.3)
    wet = sfzr.reverb(wet_in, rt60=rt60) if rt60 > 0 else np.zeros_like(wet_in)
    mixbus = dry + wet * 0.9
    return stems, sends, mixbus
