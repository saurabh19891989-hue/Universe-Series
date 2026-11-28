"""v3 render: the same sulib MIDI, a wider palette, a real (measured-IR) room and an orchestral stage.

What changes against v2 (v2mix.py stays as it was; every v2 cue still renders the old way):
  * palette: VPO 3 orchestra (as v2) + Versilian Community Sample Library (CC0: Kawai grand, marimba,
    vibraphone, xylophone, balafon, kalimba, dan tranh, folk/concert harp, darbuka, frame drum, cajon,
    conga, bongos, drum kit pieces, comedy percussion: slapstick, flexatone, ratchet, vibraslap, guiro,
    toy train whistle...) + FreePats Spanish classical guitar (CC0) instead of the FluidR3 GM guitar.
  * stage: each track has a seat - pan + image width (mid/side) + depth (front/mid/back: a few ms of
    delay, less top end, more early reflections), instead of a balance knob on a full-width stem.
  * room: early reflections and late tail from a measured hall impulse (Voxengo IM Reverbs, free for
    commercial use) replace the synthetic noise hall; the tail is pre-delayed per depth.
  * bus: gentle (1.5:1) glue compression above the cue's own average instead of sox compand 2:1,
    a small low-mid dip and an air shelf, then loudness to target with a true-peak limiter.
  * kits: GM drum notes map to VCSL pieces (KIT3); unmapped notes fall back to GeneralUser GS as v2.

render(pm_or_cue, mix, length_s, out_wav, hall="Musikvereinsaal", target=-16) -> (stereo, stems)
mix spec per track: inst=<preset> | gm=True(program, sf2) , lvl (active-RMS dBFS), gain, pan (-1..1),
  width (0..1.2, default 0.6 for solos / 0.9 sections), depth front|mid|back, send (hall 0..1),
  release, vel, kit (dict GM-note -> (preset, key)) for drum tracks, group (stem group name).
"""
import copy
import os

import numpy as np
import pretty_midi

import dsp
import sfzr
import v2mix

SR = sfzr.SR
A2 = os.environ.get("SU_AUDIO2", "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/"
                    "scratchpad/audio2/libs")
VCSL = os.environ.get("SU_VCSL", os.path.join(A2, "vcsl"))
FREEPATS = os.environ.get("SU_FREEPATS", os.path.join(A2, "freepats"))
IRDIR = os.environ.get("SU_IR", os.path.join(A2, "voxengo"))

I_ = "Idiophones/Struck Idiophones/"
M_ = "Membranophones/Struck Membranophones/"
# name -> (sfz path relative to its library root, library, gain dB)
PRESETS3 = {
    "piano": ("Chordophones/Zithers/Grand Piano, Kawai.sfz", "vcsl", 0),
    "marimba": (I_ + "Marimba.sfz", "vcsl", 0),
    "vibes": (I_ + "Vibraphone - Soft Mallets.sfz", "vcsl", 0),
    "xylo": (I_ + "Xylophone - Hard Mallets.sfz", "vcsl", 0),
    "balafon": (I_ + "Balafon - Traditional Mallet.sfz", "vcsl", 0),
    "glock3": (I_ + "Glockenspiel.sfz", "vcsl", 0),
    "kalimba": ("Idiophones/Plucked Idiophones/Kalimba, Kenya.sfz", "vcsl", 0),
    "dantranh": ("Chordophones/Zithers/Dan Tranh - Normal.sfz", "vcsl", 0),
    "folkharp": ("Chordophones/Composite Chordophones/Folk Harp.sfz", "vcsl", 0),
    "harp3": ("Chordophones/Composite Chordophones/Concert Harp.sfz", "vcsl", 0),
    "guitar": ("SpanishClassicalGuitar-SFZ-20190618/SpanishClassicalGuitar-20190618.sfz", "freepats", 0),
    # percussion (keys: see KEYS below)
    "darbuka": (M_ + "Darbuka.sfz", "vcsl", 0), "frame": (M_ + "Frame Drum.sfz", "vcsl", 0),
    "cajon": (I_ + "Cajon.sfz", "vcsl", 0), "conga": (M_ + "Conga.sfz", "vcsl", 0),
    "bongos": (M_ + "Bongos.sfz", "vcsl", 0), "snare3": (M_ + "Snare Drum, Modern 1.sfz", "vcsl", 0),
    "hat3": (I_ + "Hi-Hat Cymbal.sfz", "vcsl", 0), "kick3": (M_ + "Bass Drum 1.sfz", "vcsl", 0),
    "tom3": (M_ + "Tom 1.sfz", "vcsl", 0), "suscym": (I_ + "Suspended Cymbal 1.sfz", "vcsl", 0),
    "tri3": (I_ + "Triangles.sfz", "vcsl", 0), "shaker": (I_ + "Shaker, Small.sfz", "vcsl", 0),
    "wood": (I_ + "Woodblock.sfz", "vcsl", 0), "slapstick": (I_ + "Slapstick.sfz", "vcsl", 0),
    "flexatone": (I_ + "Flexatone.sfz", "vcsl", 0), "ratchet": (I_ + "Ratchet.sfz", "vcsl", 0),
    "vibraslap": (I_ + "Vibraslap.sfz", "vcsl", 0), "guiro": (I_ + "Guiro.sfz", "vcsl", 0),
    "claves": (I_ + "Claves.sfz", "vcsl", 0), "fingercym": (I_ + "Finger Cymbals.sfz", "vcsl", 0),
    "handbells": (I_ + "Hand Bells, Nepalese.sfz", "vcsl", 0), "marktree": (I_ + "Mark Trees.sfz", "vcsl", 0),
    "whistle": ("Aerophones/Edge-blown Aerophones/Train Whistle, Toy.sfz", "vcsl", 0),
}
# named keys for the percussion presets (VCSL layout, checked by listing the SFZ regions)
KEYS = dict(
    snare=("snare3", 60), snare_side=("snare3", 61), snare_roll=("snare3", 62), stick=("snare3", 64),
    taps=("snare3", 65), hat_c=("hat3", 42), hat_loose=("hat3", 43), hat_pedal=("hat3", 44), hat_o=("hat3", 46),
    kick=("kick3", 60), tom_rim=("tom3", 61), tom=("tom3", 62), tom_roll=("tom3", 63),
    cym_bow=("suscym", 61), cym_swell2=("suscym", 65), cym_swell4=("suscym", 66), cym=("suscym", 68),
    cym_bell=("suscym", 69), cym_roll=("suscym", 71), tri=("tri3", 65), tri_m=("tri3", 67), tri_roll=("tri3", 63),
    shk_roll=("shaker", 60), shk_dn=("shaker", 62), shk_up=("shaker", 63), shk_hi=("shaker", 64),
    darb_dum=("darbuka", 60), darb_tek=("darbuka", 62), darb_ka=("darbuka", 63), darb_slap=("darbuka", 64),
    frame_lo=("frame", 61), frame_hand=("frame", 60), frame_hi=("frame", 64), frame_mute=("frame", 65),
    cajon_bass=("cajon", 60), cajon_slap=("cajon", 62), cajon_mid=("cajon", 61),
    conga_open=("conga", 61), conga_mute=("conga", 60), quinto=("conga", 63), tumba=("conga", 65),
    bongo_hi=("bongos", 60), bongo_lo=("bongos", 63), bongo_mute=("bongos", 61),
    wood=("wood", 60), wood2=("wood", 61), slap=("slapstick", 60), slap_soft=("slapstick", 61),
    flex_fast=("flexatone", 61), flex_long=("flexatone", 62), flex_slap=("flexatone", 64), flex=("flexatone", 66),
    ratchet=("ratchet", 61), ratchet_slow=("ratchet", 62), vibraslap=("vibraslap", 60),
    guiro=("guiro", 62), guiro_hit=("guiro", 61), clave=("claves", 60), fingercym=("fingercym", 60),
    bell1=("handbells", 60), bell2=("handbells", 61), bell3=("handbells", 62),
    chimes_up=("marktree", 60), chimes_dn=("marktree", 61), chimes=("marktree", 63),
    whistle_fall=("whistle", 61), whistle_short=("whistle", 63), whistle_double=("whistle", 60),
)
# GM drum note -> VCSL piece, for re-rendering v2 cues on the new kit
KIT3 = {35: "kick", 36: "kick", 38: "snare", 40: "snare", 37: "stick", 42: "hat_c", 44: "hat_pedal",
        46: "hat_o", 41: "tom", 45: "tom", 47: "tom", 50: "tom", 49: "cym", 57: "cym", 51: "cym_bow",
        52: "cym", 59: "cym_swell2", 81: "tri", 80: "tri_m", 82: "shk_dn", 70: "shk_up", 69: "shk_hi",
        54: "shk_dn", 75: "clave", 76: "wood", 77: "wood2", 60: "bongo_hi", 61: "bongo_lo", 62: "conga_mute",
        63: "conga_open", 64: "tumba", 39: "slap_soft"}
DEPTH = {"front": dict(delay=0.0, hs=0.0, er=0.18, pre=0.012),
         "mid": dict(delay=0.004, hs=-1.5, er=0.30, pre=0.018),
         "back": dict(delay=0.009, hs=-3.0, er=0.42, pre=0.024)}

_I3 = {}


def inst3(name):
    if name in PRESETS3:
        if name not in _I3:
            rel, lib, g = PRESETS3[name]
            root = VCSL if lib == "vcsl" else FREEPATS
            _I3[name] = sfzr.Instrument(os.path.join(root, rel), None, 0, g)
        return _I3[name]
    return v2mix.inst(name)


_IR = {}


def hall_ir(name):
    if name not in _IR:
        ir = dsp.load_ir(os.path.join(IRDIR, name + ".wav"))
        _IR[name] = (dsp.early(ir, 80), dsp.late(ir, 60), dsp.rt60(ir))
    return _IR[name]


def _drum_stem(pmi, spec, length, n, k):
    kit = dict(KIT3); kit.update(spec.get("kit", {}))
    by = {}
    rest = copy.deepcopy(pmi); rest.notes = []
    for nt in pmi.notes:
        piece = kit.get(nt.pitch)
        if piece and piece in KEYS:
            pr, key = KEYS[piece]
            nn = copy.copy(nt); nn.pitch = key
            by.setdefault(pr, []).append(nn)
        else:
            rest.notes.append(nt)
    y = np.zeros((n, 2), np.float32)
    for pr, notes in by.items():
        tmp = pretty_midi.Instrument(0, name=pr); tmp.notes = notes
        tmp.control_changes = [c for c in pmi.control_changes if c.number in (7, 11)]
        s = sfzr.render_track(inst3(pr), tmp, length, seed=k)
        y[:min(n, len(s))] += s[:n] * dsp.db(spec.get("piece_gain", {}).get(pr, 0.0))
    if rest.notes:
        y += v2mix.gm_stem(rest, length)[:n] * 10 ** (spec.get("gm_gain", -4) / 20)
    return y


def render_stems(pm, mix, length):
    n = int(length * SR) + SR
    stems = {}
    for k, pmi in enumerate(pm.instruments):
        spec = mix.get(pmi.name, {"gm": True})
        if pmi.is_drum:
            y = _drum_stem(pmi, spec, length, n, k)
        elif spec.get("gm"):
            y = v2mix.gm_stem(pmi, length, program=spec.get("program"), bank=spec.get("bank", 0))[:n]
        else:
            s = sfzr.render_track(inst3(spec["inst"]), pmi, length, seed=k, release=spec.get("release"),
                                  vel_scale=spec.get("vel", 1.0))
            y = np.zeros((n, 2), np.float32); y[:min(n, len(s))] = s[:n]
        if len(y) < n:
            y = np.concatenate([y, np.zeros((n - len(y), 2), np.float32)])
        if not np.any(y):
            stems[pmi.name] = y; continue
        if "lvl" in spec:
            y = y * 10 ** ((spec["lvl"] - v2mix.active_rms_db(y)) / 20)
        stems[pmi.name] = y * dsp.db(spec.get("gain", 0))
    return stems


def stage_and_room(stems, mix, hall="Musikvereinsaal", wet=1.0, dry_only=False):
    n = max(len(s) for s in stems.values())
    er_ir, late_ir, _ = hall_ir(hall)
    dry = np.zeros((n, 2), np.float32)
    er_in = {d: np.zeros((n, 2), np.float32) for d in DEPTH}
    late_in = {d: np.zeros((n, 2), np.float32) for d in DEPTH}
    staged = {}
    for name, y in stems.items():
        spec = mix.get(name, {})
        dep = DEPTH[spec.get("depth", "mid")]
        y = dsp.place(y, spec.get("pan", 0.0), spec.get("width", 0.7))
        if dep["hs"]:
            y = dsp.eq(y, [("hs", 6500, 0.7, dep["hs"])])
        d = int(dep["delay"] * SR)
        if d:
            y = np.concatenate([np.zeros((d, 2), np.float32), y[:-d]])
        staged[name] = y
        dry += y
        snd = spec.get("send", 0.3)
        er_in[spec.get("depth", "mid")] += y * dep["er"] * (0.5 + snd)
        late_in[spec.get("depth", "mid")] += y * snd
    if dry_only:
        return dry, staged
    room = np.zeros((n, 2), np.float32)
    for dname, dep in DEPTH.items():
        if np.any(er_in[dname]):
            room += dsp.convolve(er_in[dname], er_ir, dep["pre"] * 0.3)
        if np.any(late_in[dname]):
            room += dsp.convolve(late_in[dname], late_ir, dep["pre"]) * 0.8
    # measured IRs are fairly correlated L/R (Scala 0.68, Musikverein 0.59): widen the room return only
    return dry + dsp.width(room, ROOM_WIDTH) * wet, staged


ROOM_WIDTH = 1.5
BUS3 = [("hp", 28, 0.7), ("peak", 280, 0.9, -1.2), ("peak", 3200, 0.8, +0.8), ("hs", 9500, 0.7, +2.0)]


def bus3(x, target=-16.0, glue=True):
    y = dsp.eq(x, BUS3)
    if glue:
        lvl = 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
        y = dsp.compressor(y, thr_db=lvl + 5, ratio=1.5, attack_s=0.03, release_s=0.25, knee_db=8)
    return dsp.normalise(y, target, -1.5)


def render(pm, mix, length, hall="Musikvereinsaal", target=-16.0, wet=1.0, fade_s=1.5):
    if hasattr(pm, "pm"):
        pm = pm.pm
    if pm.get_end_time() > length:      # render an excerpt: drop notes that start after the end
        pm = copy.deepcopy(pm)
        for i in pm.instruments:
            i.notes = [x for x in i.notes if x.start < length - 0.05]
    stems = render_stems(pm, mix, length)
    mixed, staged = stage_and_room(stems, mix, hall, wet)
    mixed = mixed[:int(length * SR)]
    f = int(fade_s * SR)
    if f:
        mixed[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None] ** 2
    return bus3(mixed, target), staged
