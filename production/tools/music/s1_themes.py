"""UNIVERSE UNDELIVERED - Season 1 theme package (v3 sound). All melodies are ours.

Cues (each returns (Cue, mix, meta); render with render_v3.py):
  main_theme()     ~55 s  the full main theme: intro ostinato, A (hook), B (lift), A' (tutti), tag
  title_sting()     15 s  the hook as a brass-led title card, rising sequence, button
  end_card()       ~20 s  the hook, slow and warm: piano, flute, strings (end card / 'what was real')
  jax_motif()      ~15 s  JAX: D Dorian swing head that never finishes (guitar, clarinet, darbuka)
  mira_motif()     ~15 s  MIRA: Sa-Re-Ga-Pa-Dha on F (Mohanam colour), flute with meend slides, kalimba clock
  pip_motif()      ~15 s  PIP: a tiny C-major postal march, piccolo/xylophone, woodblock, the stamp
  customs_scene()   56 s  new underscore for the E01 customs-desk toon test (times = shot list)

The show material, so every composer-agent reuses the same cells:
  HOOK   D5 A4 D5 E5 F5 | E5 D5 C5 D5         (grows from the approved A1 head D-A-D-E-F)
  LIFT   D6 C6 A5 | Bb5 A5 F5 | G5 A5 Bb5 A5   (B section: the romance / wonder colour)
  SHIP   3+3+2 ostinato on D (marimba / pizz / kalimba)
  JAX, MIRA, PIP as e01_score.py (unchanged cells, new orchestration and development)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch  # noqa: E402

HOOK_A = "D5:q. A4:e D5:e E5:e F5:q | E5:q D5:e C5:e D5:h"
HOOK_B = "F5:q. C5:e F5:e G5:e A5:q | G5:q F5:e E5:e F5:h"
HOOK_C = "Bb5:q A5:e G5:e A5:q F5:q | G5:q F5:e E5:e D5:q C5:q"
HOOK_D = "D5:q. A4:e D5:e E5:e F5:q | E5:e F5:e E5:e C#5:e D5:h"
THEME_A = " | ".join([HOOK_A, HOOK_B, HOOK_C, HOOK_D])
LIFT = "D6:h C6:q A5:q | Bb5:h A5:q F5:q | G5:q. A5:e Bb5:q A5:q | A5:h. r:q"
# chords per bar for THEME_A (root, upper voicing)
CH_A = [("D2", ["D3", "A3", "F4"]), ("C2", ["C3", "G3", "E4"]), ("F2", ["F3", "C4", "A4"]), ("C2", ["C3", "G3", "E4"]),
        ("Bb1", ["Bb2", "F3", "D4"]), ("G1", ["G2", "D3", "Bb3"]), ("D2", ["D3", "A3", "F4"]), ("A1", ["A2", "E3", "C#4"])]
CH_B = [("Bb1", ["Bb2", "F3", "D4"]), ("F2", ["F3", "C4", "A4"]), ("G1", ["G2", "D3", "Bb3"]), ("A1", ["A2", "E3", "C#4"])]
JAX = "D5:q A4:u D5:t E5:u F5:t ~E5:q | r:u D5:t C5:u A4:t B4:q. r:e"
MIRA = "G5:e A5:e C6:q ~A5:h | G5:q. F5:e Eb5:q ~D5:q | C5:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | ~C5:h F5:h"
PIP = "C6:e E6:e G6:e E6:e | C6:q G5:q | A5:e B5:e C6:e D6:e | E6:q C6:q"


def S(c, sec):
    return sec * c.bpm / 60.0


def tracks(c, names):
    for t in names:
        c.track(t, GM.get(t, 0))


def ship_ostinato(c, key, bar0, nbars, root="D4", fifth="A4", vel=56, bpb=4):
    """3+3+2 eighths: x..x..x. on root / fifth / octave"""
    r, f = pitch(root), pitch(fifth)
    for b in range(nbars):
        for i, (off, p) in enumerate(((0, r), (1.5, f), (3.0, r + 12))):
            c.note(key, p, c.bar(bar0 + b) + off, 0.5, vel + (8 if i == 0 else 0), legato=0.6)
            c.note(key, p + (7 if p == r else 5), c.bar(bar0 + b) + off + 0.5, 0.5, vel - 14, legato=0.5)


def hand_groove(c, key, bar0, nbars, vel=70, fill_last=True):
    """darbuka/frame-drum style groove (GM notes mapped to VCSL by kit): dum . tek ka | dum dum tek ."""
    pat = [(0, 36, 0), (1.0, 38, -14), (1.5, 37, -24), (2.0, 36, -6), (2.5, 36, -16), (3.0, 38, -10), (3.5, 37, -22)]
    for b in range(nbars):
        for off, note, dv in pat:
            c.note(key, note, c.bar(bar0 + b) + off, 0.25, vel + dv)
        if fill_last and b == nbars - 1:
            for k in range(4):
                c.note(key, 37, c.bar(bar0 + b) + 3 + k * 0.25, 0.2, vel - 20 + k * 6)


HAND_KIT = {36: "darb_dum", 38: "darb_tek", 37: "darb_ka", 39: "darb_slap", 41: "frame_lo", 43: "frame_hi"}


# ============================================================ MAIN THEME
def main_theme():
    c = Cue("S1-main-theme-v3", bpm=104, seed=3101)
    tracks(c, ["fl", "vln_solo", "vln1", "vln2", "vla", "vc", "cb", "hn", "tpt", "tbn", "timp", "harp", "piano",
               "marimba", "cym"])
    c.track("hand", 0, drums=True)
    B = c.bar
    # 1-2 intro: the ship ostinato, low pedal, hand drum enters bar 2
    ship_ostinato(c, "marimba", 1, 24 - 2)
    c.note("cb", "D2", B(1), 8, 58, legato=1.0); c.note("vc", "D3", B(1), 8, 52, legato=1.0)
    c.swell("vc", B(1), B(3), 60, 100)
    hand_groove(c, "hand", 2, 1, 62)
    # 3-10 A: flute + solo violin (octave), harp arpeggios, strings pad, bass moves
    c.seq("fl", THEME_A, B(3), 84, transpose=12, legato=0.95)
    c.seq("vln_solo", THEME_A, B(3), 80, legato=1.0)
    for i, (r, up) in enumerate(CH_A):
        b = B(3 + i)
        c.chord("vla", up, b, 4, 50, legato=1.0)
        c.note("cb", r, b, 2.5, 60, legato=0.95); c.note("cb", pitch(r) + 7, b + 2.5, 1.5, 52, legato=0.9)
        arp = [pitch(x) for x in up] + [pitch(up[0]) + 12, pitch(up[1]) + 12]
        for k, p in enumerate(arp + arp[-2:0:-1][:2]):
            c.note("harp", p, b + k * 0.5, 0.5, 48 + (8 if k == 0 else 0), legato=1.4)
    hand_groove(c, "hand", 3, 8, 64)
    # flute answer (fills between phrases, the 'BGM' warmth): little runs at bars 4, 6, 8 ends
    c.bend("fl", B(3) - 0.25, B(3), -150, 0)          # meend into the first note
    # 11-14 B: lift, violins take the tune, horns counter-line, cymbal swell into A'
    c.seq("vln1", LIFT, B(11), 86, legato=1.0)
    c.seq("vln2", LIFT, B(11), 74, transpose=-12, legato=1.0)
    c.seq("hn", "F4:w | F4:h C4:h | D4:h. E4:q | E4:h C#4:h", B(11), 68, legato=1.0)
    c.seq("fl", "r:h r:e A5:e Bb5:e C6:e | D6:q r:q r:h | r:w | r:h E6:e D6:e C#6:e A5:e", B(11), 66)
    for i, (r, up) in enumerate(CH_B):
        c.chord("vla", up, B(11 + i), 4, 56, legato=1.0)
        c.note("cb", r, B(11 + i), 4, 62, legato=1.0)
        c.note("vc", pitch(r) + 12, B(11 + i), 4, 58, legato=1.0)
        c.chord("piano", [pitch(x) + 12 for x in up], B(11 + i), 1.5, 52, roll=0.02)
        c.chord("piano", [pitch(x) + 12 for x in up], B(11 + i) + 2.5, 1.5, 44, roll=0.02)
    hand_groove(c, "hand", 11, 4, 70)
    c.swell("vln1", B(11), B(15), 80, 118)
    c.note("cym", 59, B(14), 4, 70)               # swell
    c.note("timp", "A2", B(14) + 2, 2, 70); c.note("timp", "A2", B(14) + 3, 0.5, 80); c.note("timp", "A2", B(14) + 3.5, 0.5, 90)
    # 15-22 A': tutti - strings + horns tune, trumpets on the second half, low brass roots
    c.seq("vln1", THEME_A, B(15), 96, legato=1.0)
    c.seq("vln2", THEME_A, B(15), 88, transpose=-12, legato=1.0)
    c.seq("hn", THEME_A, B(15), 84, transpose=-12, legato=1.0)
    c.seq("tpt", " | ".join([HOOK_C, HOOK_D]), B(19), 82, legato=0.95)
    c.seq("fl", "r:w | r:w | r:h. A5:e C6:e | D6:w | r:w | r:w | r:w | r:w", B(15), 70)
    for i, (r, up) in enumerate(CH_A):
        b = B(15 + i)
        c.chord("vla", up, b, 4, 64, legato=1.0)
        c.note("tbn", pitch(r) + 12, b, 3.5, 72, legato=0.95)
        c.note("cb", r, b, 2.5, 72, legato=0.95); c.note("cb", pitch(r) + 7, b + 2.5, 1.5, 62, legato=0.9)
        c.note("vc", pitch(r) + 12, b, 4, 66, legato=1.0)
        c.note("timp", "D2" if r[0] in "DBG" else "A2", b, 1, 62 if i % 2 else 74)
        c.chord("piano", [pitch(x) + 12 for x in up], b, 1, 62, roll=0.015)
        c.chord("piano", [pitch(x) + 12 for x in up], b + 1.5, 1, 52, roll=0.015)
        c.chord("piano", [pitch(x) + 12 for x in up], b + 3, 1, 56, roll=0.015)
    c.note("cym", 49, B(15), 3, 76)
    hand_groove(c, "hand", 15, 8, 74)
    # 23-24 tag: piano + marimba alone play the head, a held D, final hit
    c.seq("piano", "D5:q. A4:e D5:e E5:e F5:q | r:q r:e A4:e D5:q r:q", B(23), 70)
    c.chord("vla", ["D3", "A3", "F4"], B(23), 4, 40, legato=1.0)
    for t, ps, v in (("vln1", ["D5", "A5"], 92), ("hn", ["D4", "A4"], 86), ("tbn", ["D3"], 86), ("cb", ["D2"], 90),
                     ("timp", ["D2"], 100), ("tpt", ["D5"], 80)):
        c.chord(t, ps, B(24) + 2, 1.5 if t != "timp" else 1, v, legato=0.7)
    c.note("cym", 49, B(24) + 2, 3, 90)
    mix = {
        "fl": dict(inst="fl", lvl=-21, pan=-0.25, width=0.4, depth="mid", send=0.45, group="melody"),
        "vln_solo": dict(inst="vln_solo", lvl=-22, pan=-0.1, width=0.4, depth="front", send=0.4, group="melody"),
        "vln1": dict(inst="vln1", lvl=-20, pan=-0.45, width=0.8, depth="mid", send=0.45, group="melody"),
        "vln2": dict(inst="vln2", lvl=-23, pan=-0.15, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vla": dict(inst="vla", lvl=-26, pan=0.15, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vc": dict(inst="vc", lvl=-24, pan=0.4, width=0.7, depth="mid", send=0.4, group="harmony"),
        "cb": dict(inst="cb", lvl=-24, pan=0.5, width=0.5, depth="back", send=0.35, group="bass"),
        "hn": dict(inst="hn", lvl=-22, pan=-0.3, width=0.6, depth="back", send=0.55, group="melody"),
        "tpt": dict(inst="tpt", lvl=-23, pan=0.2, width=0.5, depth="back", send=0.5, group="melody"),
        "tbn": dict(inst="tbn", lvl=-25, pan=0.3, width=0.5, depth="back", send=0.5, group="bass"),
        "timp": dict(inst="timp", lvl=-24, pan=0.0, width=0.6, depth="back", send=0.5, group="percussion"),
        "cym": dict(gm=False, inst="cym", lvl=-30, pan=0.1, width=0.9, depth="back", send=0.5, group="percussion"),
        "harp": dict(inst="harp3", lvl=-26, pan=0.45, width=0.6, depth="mid", send=0.4, group="harmony"),
        "piano": dict(inst="piano", lvl=-24, pan=0.1, width=0.9, depth="mid", send=0.3, group="harmony"),
        "marimba": dict(inst="marimba", lvl=-27, pan=0.35, width=0.6, depth="mid", send=0.3, group="rhythm"),
        "hand": dict(lvl=-27, pan=-0.2, width=0.5, depth="front", send=0.25, group="rhythm", kit=HAND_KIT),
    }
    meta = dict(id="S1-MT", title="Main theme (v3)", duration=round(c.t(c.bar(25)) + 2.5, 2), hall="Musikvereinsaal",
                target=-16.0, key="D minor / F, 104 BPM",
                hits=[[0, "ship ostinato"], [round(c.t(B(3)), 2), "A: hook (flute + solo violin)"],
                      [round(c.t(B(11)), 2), "B: lift (violins), horns"], [round(c.t(B(15)), 2), "A': tutti"],
                      [round(c.t(B(23)), 2), "tag: piano head"], [round(c.t(B(24) + 2), 2), "final hit"]])
    # the cymbal track uses VPO cymbals; GM 59/49 -> VPO keys (as v2's DRUM_MAP)
    for n in c.tracks["cym"].notes:
        n.pitch = 69 if n.pitch == 59 else 66
    return c, mix, meta


# ============================================================ TITLE STING (15 s)
def title_sting():
    c = Cue("S1-title-sting-15s-v3", bpm=128, seed=3102)
    tracks(c, ["hn", "tpt", "tbn", "vln1", "vln2", "vla", "vc", "cb", "timp", "marimba", "piano", "cym", "fl"])
    c.track("kit", 0, drums=True)
    B = c.bar
    ship_ostinato(c, "marimba", 1, 6, vel=64)
    for b in range(1, 7):
        c.note("kit", 36, B(b), 0.5, 84); c.note("kit", 36, B(b) + 1.5, 0.5, 70); c.note("kit", 38, B(b) + 1, 0.5, 70)
        c.note("kit", 38, B(b) + 3, 0.5, 78)
        for k in range(8):
            c.note("kit", 42, B(b) + k * 0.5, 0.25, 40 + (14 if k % 2 == 0 else 0))
    # bar 1-2: hook on horns + trumpets; strings ostinato 16ths on D
    c.seq("hn", HOOK_A, B(1), 92, transpose=-12, legato=0.95)
    c.seq("tpt", HOOK_A, B(1), 86, legato=0.9)
    c.seq("hn", HOOK_B, B(3), 96, transpose=-12, legato=0.95)
    c.seq("tpt", HOOK_B, B(3), 90, legato=0.9)
    for b in range(1, 7):
        for k in range(16):
            c.note("vla", "D4" if b < 5 else "A4", B(b) + k * 0.25, 0.25, 60 + (12 if k % 4 == 0 else 0), legato=0.6)
    # bars 5-6: rising sequence to the top, cymbal swell
    c.seq("vln1", "Bb5:q A5:e G5:e A5:q F5:q | G5:e A5:e Bb5:e C6:e C#6:e D6:e E6:e F6:e", B(5), 98, legato=0.95)
    c.seq("vln2", "Bb4:q A4:e G4:e A4:q F4:q | G4:e A4:e Bb4:e C5:e C#5:e D5:e E5:e F5:e", B(5), 90, legato=0.95)
    c.seq("tbn", "Bb2:h G2:h | A2:w", B(5), 90, legato=0.95)
    c.seq("cb", "D2:w | F2:w | F2:w | C2:w | Bb1:h G1:h | A1:w", B(1), 80, legato=0.95)
    c.seq("vc", "D3:w | F3:w | F3:w | C3:w | Bb2:h G2:h | A2:w", B(1), 74, legato=0.95)
    c.note("cym", 69, B(6), 4, 86)
    for k in range(8):
        c.note("timp", "A2", B(6) + k * 0.5, 0.5, 60 + k * 6)
    # bar 7: the button - D minor hit, then the head's 'D-A-D' as a wink on piano + flute
    for t, ps, v in (("hn", ["D4", "F4", "A4"], 104), ("tpt", ["D5", "A5"], 100), ("tbn", ["D3", "A3"], 100),
                     ("vln1", ["D6"], 100), ("vln2", ["A5"], 96), ("vla", ["F4"], 96), ("vc", ["D3"], 100),
                     ("cb", ["D2"], 104), ("timp", ["D2"], 112), ("piano", ["D2", "D3", "A3", "F4"], 100)):
        c.chord(t, ps, B(7), 1.5 if t != "timp" else 1, v, legato=0.8)
    c.note("cym", 66, B(7), 4, 100)
    c.note("kit", 36, B(7), 0.5, 110)
    c.seq("fl", "r:h. D6:e A5:e | D6:q r:q", B(7), 80)
    c.seq("piano", "r:h. D5:e A4:e | D5:q r:q", B(7), 76)
    mix = {
        "hn": dict(inst="hn", lvl=-19, pan=-0.3, width=0.6, depth="back", send=0.45, group="melody"),
        "tpt": dict(inst="tpt", lvl=-20, pan=0.15, width=0.5, depth="back", send=0.45, group="melody"),
        "tbn": dict(inst="tbn", lvl=-22, pan=0.3, width=0.5, depth="back", send=0.45, group="bass"),
        "vln1": dict(inst="vln1", lvl=-20, pan=-0.45, width=0.8, depth="mid", send=0.4, group="melody"),
        "vln2": dict(inst="vln2", lvl=-22, pan=-0.15, width=0.8, depth="mid", send=0.4, group="harmony"),
        "vla": dict(inst="vla", lvl=-23, pan=0.15, width=0.8, depth="mid", send=0.35, group="rhythm"),
        "vc": dict(inst="vc", lvl=-22, pan=0.4, width=0.7, depth="mid", send=0.35, group="bass"),
        "cb": dict(inst="cb", lvl=-22, pan=0.5, width=0.5, depth="back", send=0.3, group="bass"),
        "timp": dict(inst="timp", lvl=-21, pan=0.0, width=0.6, depth="back", send=0.45, group="percussion"),
        "cym": dict(inst="cym", lvl=-27, pan=0.1, width=0.9, depth="back", send=0.45, group="percussion"),
        "marimba": dict(inst="marimba", lvl=-25, pan=0.35, width=0.6, depth="mid", send=0.25, group="rhythm"),
        "piano": dict(inst="piano", lvl=-22, pan=0.05, width=0.9, depth="mid", send=0.3, group="harmony"),
        "fl": dict(inst="fl", lvl=-22, pan=-0.2, width=0.4, depth="mid", send=0.4, group="melody"),
        "kit": dict(lvl=-25, pan=0.0, width=0.8, depth="mid", send=0.2, group="percussion", kit={42: "hat_c"}),
    }
    for n in c.tracks["cym"].notes:
        n.pitch = {69: 69, 66: 66}.get(n.pitch, 66)
    meta = dict(id="S1-TS", title="Title sting 15 s (v3)", duration=15.0, hall="Scala Milan Opera Hall", target=-15.0,
                key="D minor, 128 BPM", hits=[[0, "hook"], [round(c.t(B(5)), 2), "rise"], [round(c.t(B(7)), 2), "button hit"]])
    return c, mix, meta


# ============================================================ END CARD (~20 s)
def end_card():
    c = Cue("S1-end-card-v3", bpm=80, seed=3103)
    tracks(c, ["piano", "fl", "vln1", "vla", "vc", "cb", "harp"])
    B = c.bar
    c.seq("piano", HOOK_A + " | " + HOOK_D, B(1), 66, legato=1.0)
    c.seq("fl", "r:w | r:h A5:q C6:q | D6:h. C6:q | A5:w", B(1), 62)
    c.bend("fl", B(2) + 1.85, B(2) + 2, -120, 0)
    for i, (r, up) in enumerate([CH_A[0], CH_A[1], CH_A[6], CH_A[7]]):
        c.chord("vla", up, B(1 + i), 4, 44, legato=1.0)
        c.note("cb", r, B(1 + i), 4, 48, legato=1.0)
        c.chord("piano", [pitch(x) for x in up[1:]], B(1 + i), 2, 40, roll=0.03)
    c.chord("vln1", ["D5", "F5", "A5"], B(5), 4, 50, legato=1.0)
    c.chord("vla", ["D4", "A4"], B(5), 4, 44, legato=1.0)
    c.note("cb", "D2", B(5), 4, 48, legato=1.0)
    c.seq("harp", "D4:e A4:e D5:e F5:e A5:e D6:e r:q", B(5), 54)
    c.seq("piano", "r:h D6:q. r:e", B(5), 56)
    c.swell("vln1", B(5), B(6), 90, 30)
    mix = {"piano": dict(inst="piano", lvl=-20, pan=0.0, width=0.9, depth="front", send=0.35, group="melody"),
           "fl": dict(inst="fl", lvl=-24, pan=-0.3, width=0.4, depth="mid", send=0.5, group="melody"),
           "vln1": dict(inst="vln1", lvl=-27, pan=-0.4, width=0.8, depth="mid", send=0.5, group="harmony"),
           "vla": dict(inst="vla", lvl=-28, pan=0.2, width=0.8, depth="mid", send=0.5, group="harmony"),
           "vc": dict(inst="vc", lvl=-28, pan=0.35, width=0.7, depth="mid", send=0.45, group="harmony"),
           "cb": dict(inst="cb", lvl=-28, pan=0.45, width=0.5, depth="back", send=0.4, group="bass"),
           "harp": dict(inst="harp3", lvl=-26, pan=0.4, width=0.6, depth="mid", send=0.45, group="harmony")}
    meta = dict(id="S1-EC", title="End card (v3)", duration=round(c.t(B(6)) + 2.0, 2), hall="Musikvereinsaal",
                target=-18.0, key="D minor, 80 BPM", hits=[])
    return c, mix, meta


# ============================================================ JAX (~15 s)
def jax_motif():
    c = Cue("S1-motif-jax-v3", bpm=116, seed=3104)
    tracks(c, ["cl", "tpt_solo", "guitar", "bass", "vibes"])
    c.track("perc", 0, drums=True)
    B = c.bar
    CH = [["D3", "A3", "C4", "F4"], ["G2", "D3", "F3", "B3"], ["D3", "A3", "C4", "F4"], ["A2", "E3", "G3", "C#4"]]
    RT = ["D2", "G1", "D2", "A1"]
    for b in range(1, 8):
        ch = CH[(b - 1) % 4]
        for off, v in ((0, 70), (1 + 2 / 3, 56), (2, 66), (3 + 2 / 3, 58)):     # swung comp
            c.chord("guitar", ch, B(b) + off, 0.6, v, roll=0.015, legato=0.8)
        for k, off in enumerate((0, 1, 2, 3)):                                   # walking-ish pizz bass
            p = pitch(RT[(b - 1) % 4]) + [0, 7, 12, 10][k]
            c.note("bass", p, B(b) + off, 1, 72 - k * 3, legato=0.6)
        for off, nt, v in ((0, 36, 70), (1 + 2 / 3, 37, 44), (2, 38, 60), (3, 37, 40), (3 + 2 / 3, 37, 52)):
            c.note("perc", nt, B(b) + off, 0.25, v)
    c.seq("cl", JAX, B(2), 82, legato=0.9)
    c.seq("tpt_solo", JAX, B(4), 78, legato=0.85)                 # answered higher, cockier
    c.seq("cl", "D5:q A4:u D5:t E5:u F5:t G5:u A5:t | r:w", B(6), 86, legato=0.9)   # ...and again it doesn't finish
    c.seq("vibes", "r:h. A5:u C6:t | r:w", B(3), 60)
    c.note("perc", 39, B(7) + 1, 0.3, 90)                          # wink: soft slapstick
    c.note("vibes", "E6", B(7) + 1, 1.5, 58)
    mix = {"cl": dict(inst="cl", lvl=-20, pan=-0.2, width=0.4, depth="front", send=0.3, group="melody"),
           "tpt_solo": dict(inst="tpt_solo", lvl=-21, pan=0.2, width=0.4, depth="mid", send=0.35, group="melody"),
           "guitar": dict(inst="guitar", lvl=-22, pan=0.35, width=0.5, depth="front", send=0.2, group="rhythm"),
           "bass": dict(inst="pizz", lvl=-22, pan=0.0, width=0.4, depth="mid", send=0.2, group="bass"),
           "vibes": dict(inst="vibes", lvl=-27, pan=-0.4, width=0.6, depth="mid", send=0.4, group="melody"),
           "perc": dict(lvl=-26, pan=-0.3, width=0.5, depth="front", send=0.2, group="rhythm",
                        kit={36: "darb_dum", 38: "darb_tek", 37: "darb_ka", 39: "slap_soft"})}
    meta = dict(id="S1-JAX", title="Jax motif sketch (v3)", duration=round(c.t(B(8)) + 1.5, 2),
                hall="Scala Milan Opera Hall", target=-17.0, key="D Dorian swing, 116 BPM", hits=[])
    return c, mix, meta


# ============================================================ MIRA (~15 s)
def mira_motif():
    c = Cue("S1-motif-mira-v3", bpm=72, seed=3105)
    tracks(c, ["fl", "kalimba", "harp", "vc", "vla", "vln_solo"])
    B = c.bar
    # drone (tanpura-like open fifths on F, re-plucked on the harp), a clockwork kalimba figure
    for b in range(1, 6):
        c.chord("vla", ["F3", "C4"], B(b), 4, 46, legato=1.0)
        for k, p in enumerate(("C4", "F4", "F4", "F3")):
            c.note("harp", p, B(b) + k, 1, 42 + (8 if k == 0 else 0), legato=1.5)
        for k, p in enumerate(("F5", "G5", "A5", "C6", "A5", "G5", "F5", "D5")):
            c.note("kalimba", p, B(b) + k * 0.5, 0.5, 40 + (10 if k % 4 == 0 else 0), legato=1.2)
    c.note("vc", "F2", B(1), 20, 50, legato=1.0)
    c.seq("fl", MIRA, B(1) + 0.5, 78, legato=1.0)
    # meend: slides into the long notes (bansuri-like ornament on the flute)
    for bt in (B(1) + 1.5, B(2) + 2.5, B(4) + 3.5):
        c.bend("fl", bt - 0.2, bt + 0.05, -200, 0)
    c.seq("vln_solo", "r:w | r:w | r:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | C5:h F5:h", B(1), 64, legato=1.0)
    c.swell("vln_solo", B(3), B(6), 70, 30)
    mix = {"fl": dict(inst="fl", lvl=-20, pan=-0.15, width=0.4, depth="front", send=0.45, group="melody"),
           "kalimba": dict(inst="kalimba", lvl=-28, pan=0.35, width=0.5, depth="mid", send=0.35, group="rhythm"),
           "harp": dict(inst="harp3", lvl=-28, pan=0.4, width=0.6, depth="mid", send=0.45, group="harmony"),
           "vc": dict(inst="vc_solo", lvl=-28, pan=0.3, width=0.5, depth="back", send=0.5, group="bass"),
           "vla": dict(inst="vla", lvl=-29, pan=-0.3, width=0.8, depth="back", send=0.5, group="harmony"),
           "vln_solo": dict(inst="vln_solo", lvl=-24, pan=0.15, width=0.4, depth="mid", send=0.5, group="melody")}
    meta = dict(id="S1-MIRA", title="Mira motif sketch (v3)", duration=round(c.t(B(6)) + 1.5, 2),
                hall="Musikvereinsaal", target=-18.0, key="F (Sa Re Ga Pa Dha + flat-3 colour), 72 BPM", hits=[])
    return c, mix, meta


# ============================================================ PIP (~15 s)
def pip_motif():
    c = Cue("S1-motif-pip-v3", bpm=112, seed=3106)
    tracks(c, ["picc", "xylo", "bsn", "tuba", "glock"])
    c.track("perc", 0, drums=True)
    c.track("stamp", 0, drums=True)
    B = c.bar
    for b in range(1, 8):                     # oom-pah: tuba on 1 and 3, bassoon chords on 2 and 4
        root = ["C2", "G1", "C2", "G1", "F1", "G1", "C2"][b - 1]
        c.note("tuba", root, B(b), 1, 74, legato=0.5); c.note("tuba", pitch(root) + 7, B(b) + 2, 1, 66, legato=0.5)
        c.chord("bsn", [pitch(root) + 24, pitch(root) + 28] if root != "G1" else [pitch(root) + 24, pitch(root) + 29],
                B(b) + 1, 0.5, 58, legato=0.5)
        c.chord("bsn", [pitch(root) + 24, pitch(root) + 28] if root != "G1" else [pitch(root) + 24, pitch(root) + 29],
                B(b) + 3, 0.5, 54, legato=0.5)
        for k in range(4):
            c.note("perc", 76 if k % 2 == 0 else 77, B(b) + k, 0.25, 60 if k % 2 == 0 else 46)   # woodblock tick-tock
        c.note("perc", 38, B(b) + 3.5, 0.25, 34)                                                  # snare tap
    c.seq("picc", PIP + " | " + PIP.replace("E6:q C6:q", "D6:q G5:q"), B(2), 74, transpose=-12, legato=0.7)
    c.seq("xylo", PIP + " | " + PIP.replace("E6:q C6:q", "D6:q G5:q"), B(2), 70, transpose=-12, legato=0.5)
    c.seq("glock", "r:w | r:w | r:w | r:w | r:w | C7:q r:q r:h", B(2), 50)
    # the stamp: everything stops on beat 1 of bar 8, one slapstick + a tuba low C, then a toy-whistle query
    c.note("stamp", 39, B(8), 0.3, 110)
    c.note("tuba", "C1", B(8), 0.5, 90, legato=0.5)
    c.note("stamp", 60, B(8) + 1.5, 0.5, 70)
    mix = {"picc": dict(inst="picc", lvl=-23, pan=-0.2, width=0.4, depth="mid", send=0.3, group="melody"),
           "xylo": dict(inst="xylo", lvl=-23, pan=0.25, width=0.5, depth="mid", send=0.3, group="melody"),
           "bsn": dict(inst="bsn", lvl=-25, pan=0.3, width=0.4, depth="mid", send=0.25, group="harmony"),
           "tuba": dict(inst="tuba", lvl=-22, pan=0.0, width=0.4, depth="back", send=0.3, group="bass"),
           "glock": dict(inst="glock3", lvl=-28, pan=-0.35, width=0.5, depth="back", send=0.4, group="melody"),
           "perc": dict(lvl=-24, pan=0.1, width=0.5, depth="front", send=0.2, group="rhythm",
                        kit={76: "wood", 77: "wood2", 38: "taps"}),
           "stamp": dict(gain=-6, pan=0.0, width=0.4, depth="front", send=0.25, group="rhythm",
                         kit={39: "slap", 60: "whistle_short"})}
    meta = dict(id="S1-PIP", title="PIP motif sketch (v3)", duration=round(c.t(B(9)) + 1.0, 2),
                hall="Scala Milan Opera Hall", target=-17.0, key="C major march, 112 BPM", hits=[])
    return c, mix, meta


# ============================================================ E01 CUSTOMS DESK (toon test, 56 s)
def customs_scene():
    """Times are the toon-test shot list (episodes/E01/toon-test-shotlist.json): landing 0-6.45, 'Next.' 7.0,
    walk 10.8-14.2, the parcel read 11.2-17.5, the aunt 17.8-24.4, 'flexibility' 24.6, 'cartographer' 29.4,
    'Section twelve' 33.2, 'nine sections' 37.0, 'exclusive' 38.9, Mira's look 40.85, 'anything true' 42.4,
    'four hours' 48.3, 'in bursts' 50.8, stamp 52.98, out 56.0.
    Rules: silence before punchlines, music stops ON the topper, buttons after the laugh line, motifs only."""
    c = Cue("E01-customs-scene-v3", bpm=120, seed=3107)       # 120 BPM: 1 beat = 0.5 s, easy to hit times
    tracks(c, ["hn", "tpt", "vln1", "vla", "vc", "cb", "timp", "cel", "pizz", "cl", "guitar", "bsn", "vibes",
               "fl", "harp", "vln_solo", "piano", "cym"])
    c.track("perc", 0, drums=True)
    T = lambda s_: S(c, s_)
    # 0-6.45 landing: the HOOK on horns over a held D chord, cymbal swell to touchdown, cut on the snap
    c.seq("hn", "D4:q. A3:e D4:e E4:e F4:q | E4:q D4:e C4:e D4:h", T(0.4), 82, legato=1.0)
    c.chord("vla", ["D3", "A3", "F4"], T(0.2), T(6.2), 58, legato=1.0)
    c.note("cb", "D2", T(0.2), T(6.2), 60, legato=1.0)
    c.swell("vla", T(0.2), T(6.2), 60, 112)
    c.note("cym", 69, T(4.4), T(2.0), 70)
    c.chord("vln1", ["A4", "D5", "A5"], T(4.2), T(2.2), 70, legato=1.0)
    for t, ps, v in (("timp", ["D2"], 100), ("cb", ["D2"], 96), ("vc", ["D2", "D3"], 96), ("pizz", ["D2", "A2", "D3"], 100)):
        c.chord(t, ps, T(6.45), 0.5, v, legato=0.6)
    # 7.0-10.8: nothing ('Next.' / 'There's no one else here.' / 'It's procedure. Next.') - silence is the joke
    # 10.8-14.2: the walk to the desk, 3.5 steps a cycle: pizz + bassoon tiptoe on Jax's head, very light
    steps = [10.8 + i * (3.4 / 7) for i in range(7)]
    for i, t in enumerate(steps):
        c.note("pizz", ["D3", "A2", "D3", "E3", "F3", "E3", "D3"][i], T(t), 0.5, 58, legato=0.4)
    c.seq("bsn", "D3:q A2:u D3:t E3:u F3:t", T(10.85), 56, legato=0.5)
    # 11.2-17.5: Mira reads the parcel: a celesta clock (MIRA cell, ticking) over a low string hold
    c.chord("vla", ["F3", "C4"], T(14.3), T(3.6), 38, legato=1.0)
    for k, p in enumerate(("F5", "G5", "A5", "C6", "A5", "G5", "F5", "G5")):
        c.note("cel", p, T(14.4) + k * 0.5, 0.5, 40, legato=0.8)
    c.note("cel", "D5", T(17.0), 0.5, 46)       # 'Seized' lands under a lower tick
    # 17.8-24.4: the aunt - dry. Button after 'next of kin: none.' (24.41): one low bassoon plop + pizz
    c.note("bsn", "D2", T(24.45), 0.5, 76, legato=0.5); c.note("pizz", "D2", T(24.45), 0.5, 70, legato=0.4)
    # 24.6-29.1: 'flexibility' - Jax turns on the charm: guitar swing + clarinet head, soft, under him
    for b in range(4):
        t0 = T(24.7) + b * 2
        for off, v in ((0, 58), (2 / 3 + 0.0, 0), (1, 50), (1 + 2 / 3, 44)):
            if v:
                c.chord("guitar", ["D3", "A3", "C4", "F4"] if b % 2 == 0 else ["G2", "D3", "F3", "B3"], t0 + off, 0.5, v,
                        roll=0.015, legato=0.8)
    c.seq("cl", "r:h r:q D5:q | A4:u D5:t E5:u F5:t ~E5:q r:q", T(24.7), 64, legato=0.85)
    # 29.43 'I'm a cartographer.' - music stops dead on her first word (the guitar is cut by the end of the notes)
    c.note("vibes", "A5", T(33.0), 1.5, 52)   # tiny 'ding' after 'where things actually are'
    # 33.2-36.7: 'Section twelve' - Jax doubles down: the head on cornet, cocky, walking bass
    for i in range(7):
        c.note("pizz", ["D2", "A2", "D3", "C3", "Bb2", "A2", "D2"][i], T(33.3) + i, 1, 64, legato=0.5)
        c.chord("guitar", ["D3", "A3", "C4", "F4"], T(33.3) + i + 2 / 3, 0.4, 50, roll=0.012, legato=0.7)
    c.seq("tpt", "D5:q A4:u D5:t E5:u F5:t G5:q", T(33.4), 70, legato=0.85)
    # 37.03 'There are nine sections.' - everything stops at 37.0 (the notes above end by 36.9)
    # 40.58 after 'so exclusive': the cornet ta-da, then Mira's look (40.85): a single flat vibraslap? No -
    # one dry woodblock and a falling bassoon: the deflation on her face
    c.seq("tpt", "A4:e D5:e F#5:e A5:e", T(40.62), 80, legato=0.7)
    c.note("bsn", "A2", T(41.25), 1, 70, legato=0.6)           # ...and her look lets the air out of it
    c.note("bsn", "F2", T(41.75), 0.5, 60, legato=0.6)
    # 42.38-50.6 'Anything true...?' - the warm turn: MIRA on solo violin, harp, piano; then the clock of
    # 'four hours' (48.3) on low strings and timpani heartbeat
    c.chord("vla", ["F3", "A3", "C4"], T(42.4), T(5.8), 40, legato=1.0)
    c.note("cb", "F2", T(42.4), T(5.8), 40, legato=1.0)
    c.seq("harp", "F3:e C4:e F4:e A4:e C5:e F5:e r:q", T(42.4), 46)
    c.seq("vln_solo", "G5:e A5:e C6:q ~A5:h | G5:q. F5:e Eb5:q ~D5:q", T(43.0), 56, legato=1.0)
    c.bend("vln_solo", T(43.0) + 0.85, T(43.0) + 1.05, -100, 0)
    c.chord("piano", ["F3", "C4", "A4"], T(46.8), 2, 40, roll=0.04)
    c.chord("vc", ["D3", "A3"], T(48.3), T(4.5), 46, legato=1.0)
    c.note("cb", "D2", T(48.3), T(4.5), 50, legato=1.0)
    c.swell("vc", T(48.3), T(52.9), 70, 110)
    for k in range(9):
        c.note("timp", "D2", T(48.4) + k * 1.0, 0.5, 44 + k * 3)
    # 52.98 the stamp: tutti hit on the slam, then 53.6 the head on cornet + guitar strum = the button
    for t, ps, v in (("timp", ["D2"], 110), ("cb", ["D2"], 100), ("vc", ["D2", "D3"], 100),
                     ("hn", ["D3", "A3", "D4"], 100), ("vln1", ["D5", "A5"], 96)):
        c.chord(t, ps, T(52.98), 0.5, v, legato=0.6)
    c.seq("tpt", "A4:e D5:e r:e F#5:e ~A5:h", T(53.6), 86, legato=0.7)
    c.chord("guitar", ["D3", "A3", "D4", "F#4"], T(54.6), 1.2, 96, roll=0.01)
    c.note("pizz", "D2", T(54.6), 0.5, 96, legato=0.5)
    c.note("perc", 38, T(54.6), 0.3, 66)
    for n in c.tracks["cym"].notes:
        n.pitch = 69
    mix = {
        "hn": dict(inst="hn", lvl=-21, pan=-0.3, width=0.6, depth="back", send=0.45, group="melody"),
        "tpt": dict(inst="tpt_solo", lvl=-22, pan=0.15, width=0.4, depth="mid", send=0.3, group="melody"),
        "vln1": dict(inst="vln1", lvl=-24, pan=-0.45, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vla": dict(inst="vla", lvl=-26, pan=0.15, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vc": dict(inst="vc", lvl=-25, pan=0.4, width=0.7, depth="mid", send=0.4, group="harmony"),
        "cb": dict(inst="cb", lvl=-26, pan=0.5, width=0.5, depth="back", send=0.35, group="bass"),
        "timp": dict(inst="timp", lvl=-24, pan=0.0, width=0.6, depth="back", send=0.45, group="percussion"),
        "cel": dict(inst="celesta", lvl=-29, pan=0.35, width=0.5, depth="mid", send=0.4, group="melody"),
        "pizz": dict(inst="pizz", lvl=-25, pan=0.1, width=0.6, depth="mid", send=0.25, group="rhythm"),
        "cl": dict(inst="cl", lvl=-25, pan=-0.2, width=0.4, depth="mid", send=0.3, group="melody"),
        "guitar": dict(inst="guitar", lvl=-25, pan=0.35, width=0.5, depth="front", send=0.2, group="rhythm"),
        "bsn": dict(inst="bsn", lvl=-24, pan=0.25, width=0.4, depth="mid", send=0.25, group="melody"),
        "vibes": dict(inst="vibes", lvl=-28, pan=-0.35, width=0.5, depth="mid", send=0.45, group="melody"),
        "harp": dict(inst="harp3", lvl=-27, pan=0.45, width=0.6, depth="mid", send=0.45, group="harmony"),
        "vln_solo": dict(inst="vln_solo", lvl=-24, pan=-0.1, width=0.4, depth="front", send=0.45, group="melody"),
        "piano": dict(inst="piano", lvl=-27, pan=0.05, width=0.9, depth="mid", send=0.35, group="harmony"),
        "cym": dict(inst="cym", lvl=-30, pan=0.1, width=0.9, depth="back", send=0.45, group="percussion"),
        "perc": dict(lvl=-27, pan=-0.2, width=0.5, depth="front", send=0.2, group="rhythm",
                     kit={76: "wood", 38: "stick"}),
    }
    meta = dict(id="E01-CUSTOMS-V3", title="E01 customs desk underscore (v3)", duration=56.0, hall="Scala Milan Opera Hall",
                target=-18.0, key="D minor / F", hits=[[6.45, "touchdown hit"], [24.45, "plop button"],
                                                        [40.62, "ta-da, deflated by her look"], [52.98, "stamp hit"], [53.6, "head button"]],
                stops=[[7.0, 10.8], [17.8, 24.4], [29.43, 33.0], [36.9, 40.6]])
    return c, mix, meta


ALL = dict(main_theme=main_theme, title_sting=title_sting, end_card=end_card, jax=jax_motif, mira=mira_motif,
           pip=pip_motif, customs=customs_scene)
