"""UNIVERSE UNDELIVERED - stage-2 pieces (28 Nov, v3 sound + worldsynth instruments). All melodies ours.

  mira_world()       ~18 s  Mira's motif on bansuri, santoor, sarangi, tanpura, tabla (keherwa)
  indian_demo()      ~37 s  a short composed piece in D (Kalyani/Yaman colour): alap on sitar over tanpura,
                            a teental gat on bansuri, sitar answers (sawal-jawab), santoor run, tihai to sam
  heart_theme()      ~62 s  THE BARON'S HEART THEME (E01 sc. 21, returns in E10): E minor 3/4, duduk then
                            violins, cello counter-line, celesta stars, ends in E major
  cutaway()           20 s  the Baron rides a cannonball: 18th-c. military swagger, a stumble at 9.6 s
                            (changing cannonballs), recovery up a semitone
  main_theme_full()  ~76 s  the main theme as a piece: intro, A (hook), B (new tune + cello counter-melody),
                            lift, A' tutti with the B counter-melody on top, tag
  customs_sparring() ~30 s  Jax's and Mira's motifs in counterpoint as they spar, a truce note, the stamp

Ornament helpers: meend(c, track, beat, cents) slides INTO the note at `beat` from `cents` away;
gamaka(c, track, beat, beats, depth) oscillates around a held note (Carnatic-style shake).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, pitch  # noqa: E402
import worldsynth as W  # noqa: E402
from s1_themes import HOOK_A, HOOK_B, HOOK_C, HOOK_D, THEME_A, CH_A, LIFT, CH_B, JAX, ship_ostinato  # noqa: E402


def meend(c, key, beat, cents=-200, glide=0.3):
    c.bend(key, beat, beat + glide, cents, 0, steps=10)


def gamaka(c, key, beat, beats, depth=120, rate=3.0):
    """oscillate up to `depth` cents and back, `rate` shakes per beat, returning to 0."""
    n = max(1, int(beats * rate))
    for i in range(n):
        b = beat + i / rate
        c.bend(key, b, b + 0.5 / rate, 0, depth, steps=5)
        c.bend(key, b + 0.5 / rate, b + 1 / rate, depth, 0, steps=5)


def tr(c, names):
    for t in names:
        c.track(t, 0)


SYN = lambda name, **k: dict(synth=name, **k)  # noqa: E731


# ============================================================ MIRA on Indian instruments
MIRA_TUNE = "G5:e A5:e C6:q ~A5:h | G5:q. F5:e Eb5:q ~D5:q | C5:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | ~C5:h F5:h"


def mira_world():
    c = Cue("S2-motif-mira-world", bpm=72, seed=4101)
    tr(c, ["bansuri", "santoor", "sarangi", "tanpura", "tabla"])
    B = c.bar
    W.tanpura(c, "tanpura", 0, 22, sa="F3", cycle=4.0, vel=58)
    for b in range(1, 6):        # santoor clock (Mira's measuring mind), soft
        for k, p in enumerate(("F5", "G5", "A5", "C6", "A5", "G5", "F5", "D5")):
            c.note("santoor", p, B(b) + k * 0.5, 0.5, 40 + (12 if k % 4 == 0 else 0), legato=1.0)
    W.theka(c, "tabla", "keherwa", B(2), 4, matra=0.5, vel=64, fill_last=True)
    c.seq("bansuri", MIRA_TUNE, B(1) + 0.5, 82, legato=1.0)
    meend(c, "bansuri", B(1) + 1.5, -200, 0.35)        # into C6
    meend(c, "bansuri", B(2) + 2.5, -100, 0.3)         # into Eb5 (from D)
    gamaka(c, "bansuri", B(3), 1.5, 90, 3)             # shake on the held C5
    meend(c, "bansuri", B(4) + 3.5, 200, 0.3)          # fall into D5
    c.seq("sarangi", "r:w | r:w | r:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | C5:h F5:h", B(1), 64, legato=1.0)
    meend(c, "sarangi", B(4), -150, 0.4)
    mix = {"bansuri": SYN("bansuri", lvl=-20, pan=-0.15, width=0.4, depth="front", send=0.4, group="melody"),
           "santoor": SYN("santoor", lvl=-29, pan=0.35, width=0.6, depth="mid", send=0.35, group="rhythm"),
           "sarangi": SYN("sarangi", lvl=-25, pan=0.2, width=0.5, depth="mid", send=0.45, group="melody",
                          taraf=["F4", "G4", "A4", "C5", "D5", "F5"]),
           "tanpura": SYN("tanpura", lvl=-29, pan=-0.35, width=0.8, depth="back", send=0.4, group="harmony"),
           "tabla": SYN("tabla", tonic="F4", lvl=-26, pan=0.1, width=0.5, depth="front", send=0.2, group="rhythm")}
    return c, mix, dict(duration=round(c.t(B(6)) + 2.0, 2), hall="Musikvereinsaal", target=-18.0)


# ============================================================ INDIAN INSTRUMENTS DEMO (composed piece)
def indian_demo():
    c = Cue("S2-indian-instruments-piece", bpm=80, seed=4102)
    tr(c, ["tanpura", "sitar", "veena", "bansuri", "santoor", "tabla"])
    W.tanpura(c, "tanpura", 0, 46, sa="D3", cycle=3.0, vel=60)
    # alap (beats 0-10): sitar alone over the drone, slides into each note
    c.seq("sitar", "D4:h ~E4:q F#4:q | ~A4:h. G#4:q | ~A4:w", 0, 74, legato=1.0)
    meend(c, "sitar", 1.0 + 1.0, -200, 0.4); meend(c, "sitar", 4.0, -200, 0.45); meend(c, "sitar", 8.0, -100, 0.5)
    gamaka(c, "sitar", 8.5, 1.2, 100, 2.5)
    c.note("veena", "D2", 0, 6, 70, legato=1.0); c.note("veena", "A2", 6, 4, 62, legato=1.0)
    # gat (beats 10-26): bansuri tune over teental, matra = half a beat (16 matras = 8 beats)
    GAT = ("A4:e B4:e C#5:q B4:e A4:e F#4:q | G#4:e A4:e B4:e C#5:e ~E5:q D5:q | "
           "C#5:e B4:e A4:e G#4:e A4:h | F#4:e G#4:e A4:e B4:e A4:q. r:e")
    c.seq("bansuri", GAT, 10, 84, legato=0.98)
    meend(c, "bansuri", 10 + 4 + 2, -200, 0.25); meend(c, "bansuri", 18 + 2, 100, 0.3)
    gamaka(c, "bansuri", 18 + 2, 1.0, 80, 3)
    W.theka(c, "tabla", "teental", 10, 3, matra=0.5, vel=80, fill_last=True)
    for k in range(4):                         # veena plucks the Sa-Pa on each vibhag
        c.note("veena", "D3" if k % 2 == 0 else "A2", 10 + k * 4, 3.8, 58, legato=1.0)
    # sawal-jawab (26-34): sitar answers, bansuri replies
    c.seq("sitar", "E5:e D5:e C#5:e B4:e C#5:q A4:q", 26, 84, legato=0.95)
    meend(c, "sitar", 28, -200, 0.25)
    c.seq("bansuri", "B4:e C#5:e D5:e E5:e F#5:h", 30, 86, legato=0.98)
    meend(c, "bansuri", 32, -200, 0.3)
    # 34-38: santoor run, sitar doubling an octave down; tabla theka continues (first half of the cycle)
    run = "A4:s B4:s C#5:s E5:s F#5:s E5:s C#5:s B4:s " * 2
    c.seq("santoor", run.strip(), 34, 78, legato=1.0)
    c.seq("sitar", "A3:q C#4:q E4:q F#4:q", 34, 70, legato=0.9)
    for k, bol in enumerate("dha dhin dhin dha dha dhin dhin dha".split()):
        c.note("tabla", W.BOLS[bol], 34 + k * 0.5, 0.5, 80 + (10 if k == 0 else 0))
    # 38-42: tihai - the same phrase three times, the third lands on sam (beat 42) with everyone
    for k, b0 in enumerate((38.0, 39.5, 41.0)):
        for t_ in ("sitar", "bansuri", "santoor"):
            c.seq(t_, "C#5:s B4:s A4:e", b0, 86 + k * 4, legato=0.9)
        for j, s in enumerate(("te", "re", "ki", "ta")):
            c.note("tabla", W.BOLS[s], b0 + j * 0.25, 0.25, 74 + j * 3 + k * 4)
        c.note("tabla", W.BOLS["dha"], b0 + 1.0, 0.5, 92 + k * 5)
    for t_, p in (("sitar", "D5"), ("bansuri", "D5"), ("santoor", "D5"), ("veena", "D3")):
        c.note(t_, p, 42, 3, 100, legato=1.0)
    c.note("tabla", W.BOLS["dha"], 42, 1, 112)
    meend(c, "sitar", 42, -100, 0.3)
    mix = {"tanpura": SYN("tanpura", lvl=-28, pan=-0.4, width=0.8, depth="back", send=0.4, group="harmony"),
           "sitar": SYN("sitar", lvl=-21, pan=0.25, width=0.5, depth="front", send=0.35, group="melody",
                        taraf=["D4", "E4", "F#4", "G#4", "A4", "B4", "C#5", "D5"], taraf_gain=0.3),
           "veena": SYN("veena", lvl=-27, pan=-0.2, width=0.5, depth="mid", send=0.35, group="bass"),
           "bansuri": SYN("bansuri", lvl=-21, pan=-0.2, width=0.4, depth="front", send=0.4, group="melody"),
           "santoor": SYN("santoor", lvl=-25, pan=0.4, width=0.6, depth="mid", send=0.35, group="melody"),
           "tabla": SYN("tabla", tonic="D4", lvl=-23, pan=0.05, width=0.5, depth="front", send=0.2, group="rhythm")}
    return c, mix, dict(duration=round(c.t(45.5), 2), hall="French 18th Century Salon", target=-17.0)


# ============================================================ THE BARON'S HEART THEME
HEART = ("B3:q E4:q B4:q | A4:h G4:q | F#4:q G4:q A4:q | B4:h. | "
         "C5:q B4:q A4:q | G4:h E4:q | F#4:q D4:q F#4:q | E4:h.")
HEART_CH = [("E2", ["E3", "G3", "B3"]), ("A1", ["A2", "C3", "E3"]), ("D2", ["D3", "F#3", "A3"]),
            ("G1", ["G2", "B2", "D3"]), ("C2", ["C3", "E3", "G3"]), ("E2", ["E3", "G3", "B3"]),
            ("B1", ["B2", "D#3", "F#3"]), ("E2", ["E3", "G3", "B3"])]


def heart_theme():
    c = Cue("S2-baron-heart-theme", bpm=66, beats_per_bar=3, seed=4103)
    tr(c, ["harp", "vla", "vc", "cb", "duduk", "vln1", "vln2", "vc_solo", "cel", "hn"])
    B = c.bar

    def pad(bar0, vel=46, cello=True):
        for i, (r, up) in enumerate(HEART_CH):
            b = B(bar0 + i)
            c.chord("vla", up, b, 3, vel, legato=1.0)
            c.note("cb", r, b, 3, vel + 4, legato=1.0)
            for k, p in enumerate([up[0], up[1], up[2], pitch(up[1]) + 12, pitch(up[2]) + 12, pitch(up[1]) + 12]):
                c.note("harp", p, b + k * 0.5, 0.5, 40 + (8 if k == 0 else 0), legato=1.6)
    # 1-2 intro: harp alone on Em, the low E pedal
    for b in (1, 2):
        for k, p in enumerate(("E3", "B3", "E4", "G4", "B4", "G4")):
            c.note("harp", p, B(b) + k * 0.5, 0.5, 44, legato=1.6)
    c.note("cb", "E2", B(1), 6, 40, legato=1.0)
    # 3-10 first statement: duduk (wonder and loss), quiet, midrange - leaves room for dialogue
    pad(3, 42)
    c.seq("duduk", HEART, B(3), 76, legato=1.0)
    meend(c, "duduk", B(3) + 2, -200, 0.4); meend(c, "duduk", B(6), -100, 0.5)
    # 11-18 second statement: violins an octave up, the solo cello answers in the gaps (counter-line),
    # celesta 'stars' on Earth's rise
    pad(11, 50)
    c.seq("vln1", HEART, B(11), 80, transpose=12, legato=1.0)
    c.seq("vln2", HEART, B(11), 66, legato=1.0)
    c.seq("vc_solo", "r:h. | r:q D4:q C4:q | B3:h. | r:q E4:q F#4:q | E4:h. | r:q B3:q C4:q | D#4:h. | r:h.",
          B(11), 64, legato=1.0)
    for k, p in enumerate(("B5", "E6", "G6", "B6", "F#6", "E6", "D#6", "E6")):
        c.note("cel", p, B(11 + k) + 1, 1, 36, legato=1.0)
    c.seq("hn", "r:h. | r:h. | r:h. | D4:h. | E4:h. | E4:h. | D#4:h. | E4:h.", B(11), 56, legato=1.0)
    c.swell("vln1", B(11), B(15), 70, 105); c.swell("vln1", B(15), B(19), 105, 70)
    # 19-22 coda: the first phrase on the solo cello alone, then E MAJOR (wonder wins, a little)
    c.seq("vc_solo", "B3:q E4:q B4:q | A4:h G#4:q | ~B4:h. | ~B4:h.", B(19), 70, legato=1.0)
    meend(c, "vc_solo", B(19) + 2, -200, 0.5)
    c.chord("vla", ["E3", "G#3", "B3"], B(20), 9, 40, legato=1.0)
    c.note("cb", "E2", B(20), 9, 42, legato=1.0)
    c.chord("vln1", ["G#5", "B5", "E6"], B(21), 6, 38, legato=1.0)
    c.seq("harp", "E3:e B3:e E4:e G#4:e B4:e E5:e", B(21), 44)
    c.note("cel", "G#6", B(22), 3, 34)
    mix = {"harp": dict(inst="harp3", lvl=-26, pan=0.4, width=0.6, depth="mid", send=0.5, group="harmony"),
           "vla": dict(inst="vla", lvl=-29, pan=0.1, width=0.9, depth="mid", send=0.55, group="harmony"),
           "vc": dict(inst="vc", lvl=-30, pan=0.35, width=0.8, depth="mid", send=0.5, group="harmony"),
           "cb": dict(inst="cb", lvl=-29, pan=0.45, width=0.5, depth="back", send=0.45, group="bass"),
           "duduk": SYN("duduk", lvl=-21, pan=-0.1, width=0.4, depth="front", send=0.45, group="melody"),
           "vln1": dict(inst="vln1", lvl=-23, pan=-0.45, width=0.8, depth="mid", send=0.55, group="melody"),
           "vln2": dict(inst="vln2", lvl=-27, pan=-0.15, width=0.8, depth="mid", send=0.55, group="harmony"),
           "vc_solo": dict(inst="vc_solo", lvl=-23, pan=0.25, width=0.4, depth="front", send=0.45, group="melody"),
           "cel": dict(inst="celesta", lvl=-31, pan=-0.3, width=0.5, depth="back", send=0.6, group="melody"),
           "hn": dict(inst="hn", lvl=-29, pan=-0.3, width=0.6, depth="back", send=0.6, group="harmony")}
    return c, mix, dict(duration=round(c.t(B(23)) + 3.0, 2), hall="Musikvereinsaal", target=-20.0, fade_s=3.0)


# ============================================================ CUTAWAY: THE CANNONBALL (20 s)
def cutaway():
    c = Cue("S2-baron-cannonball-cutaway", bpm=112, seed=4104)
    tr(c, ["picc", "tpt", "hn", "tbn", "bsn", "pizz", "timp", "snare", "stick", "cym"])
    B = c.bar
    TUNE = ("D5:q. A4:e D5:e F#5:e A5:q | B5:q A5:e F#5:e D5:q A4:q | "
            "G5:q. F#5:e E5:e D5:e C#5:q | D5:e E5:e F#5:e G5:e A5:h")
    c.seq("picc", TUNE, B(1), 88, legato=0.8)
    c.seq("tpt", TUNE, B(1), 84, transpose=-12, legato=0.8)
    H = [("D2", "D3", ["D4", "F#4", "A4"]), ("G2", "D3", ["D4", "G4", "B4"]), ("A2", "E3", ["C#4", "E4", "A4"]),
         ("D2", "A2", ["D4", "F#4", "A4"])]
    for i, (r, f, ch) in enumerate(H):
        b = B(1 + i)
        c.note("tbn", r, b, 1, 82, legato=0.6); c.note("tbn", f, b + 2, 1, 76, legato=0.6)
        c.chord("hn", ch, b + 1, 0.5, 70, legato=0.6); c.chord("hn", ch, b + 3, 0.5, 70, legato=0.6)
        c.note("timp", "D2" if r[0] == "D" else "A2", b, 0.5, 84)
        for k in range(8):                  # snare: 'left-right' eighths with a flam on 1 and a drag on 4
            c.note("snare", 60, b + k * 0.5, 0.25, 52 + (24 if k in (0, 4) else 0))
        c.note("snare", 60, b + 3.75, 0.25, 44); c.note("snare", 60, b + 3.875, 0.125, 40)
    # bar 5 (8.57-9.64 s, 2 beats): the change of cannonballs - everything stalls on a high A, the trombone
    # slides down, the snare trips (two stick clicks), one beat of nothing (9.64-10.18 s)
    c.note("picc", "A5", B(5), 1.5, 90, legato=1.0); c.note("tpt", "A4", B(5), 1.5, 84, legato=1.0)
    c.note("tbn", "A2", B(5), 1.5, 90, legato=1.0)
    c.bend("tbn", B(5) + 0.3, B(5) + 1.5, 0, -200)
    c.bend("picc", B(5) + 0.8, B(5) + 1.5, 0, -120)
    c.note("stick", 64, B(5) + 0.5, 0.25, 70); c.note("stick", 64, B(5) + 0.85, 0.25, 50)
    c.note("cym", 69, B(5) + 1.5, 0.5, 50)          # a lonely bell-of-the-cymbal tink
    # recovery (from beat B(5)+3 = 10.18 s): the tune again, UP a semitone in Eb, tutti and prouder
    c.bend("tbn", B(5) + 2.9, B(5) + 3.0, -200, 0); c.bend("picc", B(5) + 2.9, B(5) + 3.0, -120, 0)
    R = B(5) + 3
    c.seq("picc", TUNE, R, 96, transpose=1, legato=0.8)
    c.seq("tpt", TUNE, R, 92, transpose=-11, legato=0.8)
    c.seq("hn", TUNE, R, 82, transpose=-11, legato=0.9)
    for i, (r, f, ch) in enumerate(H):
        b = R + i * 4
        c.note("tbn", pitch(r) + 1, b, 1, 90, legato=0.6); c.note("tbn", pitch(f) + 1, b + 2, 1, 84, legato=0.6)
        c.chord("bsn", [pitch(x) + 1 - 12 for x in ch], b + 1, 0.5, 70, legato=0.6)
        c.chord("pizz", [pitch(x) + 1 - 12 for x in ch], b + 3, 0.5, 74, legato=0.4)
        c.note("timp", pitch("D2") + 1 if r[0] == "D" else pitch("A2") + 1, b, 0.5, 92)
        for k in range(8):
            c.note("snare", 60, b + k * 0.5, 0.25, 56 + (26 if k in (0, 4) else 0))
    c.note("cym", 68, R, 2, 90)
    end = R + 16
    for t_, ps, v in (("picc", ["D#6"], 100), ("tpt", ["D#5", "A#5"], 100), ("hn", ["D#4", "G4", "A#4"], 96),
                      ("tbn", ["D#3"], 100), ("timp", ["D#2"], 110), ("bsn", ["D#3"], 90)):
        c.chord(t_, ps, end, 1, v, legato=0.7)
    c.note("cym", 68, end, 2, 100)
    mix = {"picc": dict(inst="picc", lvl=-22, pan=-0.2, width=0.4, depth="mid", send=0.3, group="melody"),
           "tpt": dict(inst="tpt", lvl=-21, pan=0.15, width=0.5, depth="back", send=0.35, group="melody"),
           "hn": dict(inst="hn", lvl=-23, pan=-0.35, width=0.6, depth="back", send=0.4, group="harmony"),
           "tbn": dict(inst="tbn", lvl=-22, pan=0.3, width=0.5, depth="back", send=0.35, group="bass"),
           "bsn": dict(inst="bsn", lvl=-26, pan=0.25, width=0.4, depth="mid", send=0.3, group="harmony"),
           "pizz": dict(inst="pizz", lvl=-26, pan=-0.25, width=0.8, depth="mid", send=0.3, group="harmony"),
           "timp": dict(inst="timp", lvl=-22, pan=0.0, width=0.6, depth="back", send=0.4, group="percussion"),
           "snare": dict(inst="snare3", lvl=-24, pan=0.1, width=0.5, depth="mid", send=0.25, group="percussion"),
           "stick": dict(inst="snare3", lvl=-26, pan=0.1, width=0.5, depth="mid", send=0.25, group="percussion"),
           "cym": dict(inst="suscym", lvl=-28, pan=0.15, width=0.9, depth="back", send=0.4, group="percussion")}
    return c, mix, dict(duration=20.0, hall="Scala Milan Opera Hall", target=-16.0, fade_s=0.8,
                        hits=[[0.0, "march"], [8.57, "stall on the high A"], [9.64, "beat of nothing"],
                              [10.18, "recovery in Eb"], [round(c.t(end), 2), "final hit"]])


# ============================================================ MAIN THEME AS A PIECE (A - B - lift - A')
B_TUNE = ("A5:q. G5:e F5:q C5:q | D5:q E5:e F5:e G5:h | Bb5:q. A5:e G5:q F5:q | E5:h. C5:q | "
          "D5:q F5:q Bb5:q A5:q | G5:q. F5:e E5:q D5:q | C#5:q E5:q A5:q G5:q | A5:w")
B_COUNTER = ("F3:h A3:h | C4:h. Bb3:q | G3:h D4:h | C4:w | Bb3:q D4:q F4:h | E4:h D4:h | "
             "C#4:q E4:q G4:h | A3:w")
B_CH = [("F2", ["F3", "A3", "C4"]), ("C2", ["E3", "G3", "C4"]), ("G1", ["G3", "Bb3", "D4"]), ("C2", ["E3", "G3", "C4"]),
        ("Bb1", ["F3", "Bb3", "D4"]), ("G1", ["G3", "Bb3", "D4"]), ("A1", ["E3", "A3", "C#4"]), ("A1", ["E3", "G3", "C#4"])]


def main_theme_full():
    c = Cue("S2-main-theme-full", bpm=104, seed=4105)
    tr(c, ["fl", "vln_solo", "vln1", "vln2", "vla", "vc", "cb", "hn", "tpt", "tbn", "timp", "harp", "piano",
           "marimba", "cym", "tabla", "santoor"])
    B = c.bar
    ship_ostinato(c, "marimba", 1, 10)
    c.note("cb", "D2", B(1), 8, 58, legato=1.0); c.note("vc", "D3", B(1), 8, 52, legato=1.0)
    W.theka(c, "tabla", "keherwa", B(2), 9, matra=0.5, vel=66, fill_last=True)
    # A (3-10)
    c.seq("fl", THEME_A, B(3), 84, transpose=12, legato=0.95)
    c.seq("vln_solo", THEME_A, B(3), 80, legato=1.0)
    meend(c, "fl", B(3), -150, 0.25)
    for i, (r, up) in enumerate(CH_A):
        b = B(3 + i)
        c.chord("vla", up, b, 4, 50, legato=1.0)
        c.note("cb", r, b, 2.5, 60, legato=0.95); c.note("cb", pitch(r) + 7, b + 2.5, 1.5, 52, legato=0.9)
        arp = [pitch(x) for x in up] + [pitch(up[0]) + 12, pitch(up[1]) + 12]
        for k, p in enumerate(arp + arp[-2:0:-1][:2]):
            c.note("harp", p, b + k * 0.5, 0.5, 48 + (8 if k == 0 else 0), legato=1.4)
    # B (11-18): the new tune on violins, the cello counter-melody against it; piano and santoor colour
    c.seq("vln1", B_TUNE, B(11), 86, legato=1.0)
    c.seq("vc", B_COUNTER, B(11), 78, legato=1.0)
    c.seq("santoor", "r:h. C6:e A5:e | r:w | r:h. D6:e Bb5:e | r:w | r:h. F6:e D6:e | r:w | r:h. E6:e C#6:e | r:w",
          B(11), 56)
    for i, (r, up) in enumerate(B_CH):
        b = B(11 + i)
        c.chord("vla", up, b, 4, 52, legato=1.0)
        c.note("cb", r, b, 4, 60, legato=1.0)
        c.chord("piano", [pitch(x) + 12 for x in up], b, 1.5, 50, roll=0.02)
        c.chord("piano", [pitch(x) + 12 for x in up], b + 2, 1.5, 44, roll=0.02)
    c.note("hn", "A3", B(17), 8, 60, legato=1.0)
    # 19-22 lift (as v3), cymbal swell into the tutti
    c.seq("vln1", LIFT, B(19), 88, legato=1.0)
    c.seq("vln2", LIFT, B(19), 76, transpose=-12, legato=1.0)
    c.seq("hn", "F4:w | F4:h C4:h | D4:h. E4:q | E4:h C#4:h", B(19), 70, legato=1.0)
    for i, (r, up) in enumerate(CH_B):
        c.chord("vla", up, B(19 + i), 4, 56, legato=1.0)
        c.note("cb", r, B(19 + i), 4, 62, legato=1.0)
        c.note("vc", pitch(r) + 12, B(19 + i), 4, 58, legato=1.0)
    c.swell("vln1", B(19), B(23), 80, 118)
    c.note("cym", 69, B(22), 4, 70)
    for k, v in ((2, 70), (3, 80), (3.5, 90)):
        c.note("timp", "A2", B(22) + k, 0.5, v)
    # A' (23-30): tutti hook; the B counter-melody comes back on top in the flute = the two tunes together
    c.seq("vln1", THEME_A, B(23), 96, legato=1.0)
    c.seq("vln2", THEME_A, B(23), 88, transpose=-12, legato=1.0)
    c.seq("hn", THEME_A, B(23), 84, transpose=-12, legato=1.0)
    c.seq("tpt", " | ".join([HOOK_C, HOOK_D]), B(27), 82, legato=0.95)
    c.seq("fl", "A5:h C6:h | E6:h. D6:q | C6:h F6:h | E6:w | D6:q F6:q Bb6:q A6:q | G6:h. E6:q | "
                "F6:q E6:q D6:q C#6:q | D6:w", B(23), 74, legato=1.0)
    W.theka(c, "tabla", "keherwa", B(23), 8, matra=0.5, vel=76, fill_last=True)
    for i, (r, up) in enumerate(CH_A):
        b = B(23 + i)
        c.chord("vla", up, b, 4, 64, legato=1.0)
        c.note("tbn", pitch(r) + 12, b, 3.5, 72, legato=0.95)
        c.note("cb", r, b, 2.5, 72, legato=0.95); c.note("cb", pitch(r) + 7, b + 2.5, 1.5, 62, legato=0.9)
        c.note("vc", pitch(r) + 12, b, 4, 66, legato=1.0)
        c.note("timp", "D2" if r[0] in "DBG" else "A2", b, 1, 62 if i % 2 else 74)
        c.chord("piano", [pitch(x) + 12 for x in up], b, 1, 60, roll=0.015)
        c.chord("piano", [pitch(x) + 12 for x in up], b + 1.5, 1, 50, roll=0.015)
    ship_ostinato(c, "marimba", 23, 8, vel=60)
    c.note("cym", 66, B(23), 3, 76)
    # tag (31-32)
    c.seq("piano", "D5:q. A4:e D5:e E5:e F5:q | r:q r:e A4:e D5:q r:q", B(31), 70)
    c.chord("vla", ["D3", "A3", "F4"], B(31), 4, 40, legato=1.0)
    for t_, ps, v in (("vln1", ["D5", "A5"], 92), ("hn", ["D4", "A4"], 86), ("tbn", ["D3"], 86),
                      ("cb", ["D2"], 90), ("timp", ["D2"], 100), ("tpt", ["D5"], 80)):
        c.chord(t_, ps, B(32) + 2, 1.5 if t_ != "timp" else 1, v, legato=0.7)
    c.note("cym", 66, B(32) + 2, 3, 90)
    for n in c.tracks["cym"].notes:
        n.pitch = 69 if n.pitch == 69 else 66
    mix = {
        "fl": dict(inst="fl", lvl=-21, pan=-0.25, width=0.4, depth="mid", send=0.45, group="melody"),
        "vln_solo": dict(inst="vln_solo", lvl=-22, pan=-0.1, width=0.4, depth="front", send=0.4, group="melody"),
        "vln1": dict(inst="vln1", lvl=-20, pan=-0.45, width=0.8, depth="mid", send=0.45, group="melody"),
        "vln2": dict(inst="vln2", lvl=-23, pan=-0.15, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vla": dict(inst="vla", lvl=-26, pan=0.15, width=0.8, depth="mid", send=0.45, group="harmony"),
        "vc": dict(inst="vc", lvl=-22, pan=0.4, width=0.7, depth="mid", send=0.4, group="melody"),
        "cb": dict(inst="cb", lvl=-24, pan=0.5, width=0.5, depth="back", send=0.35, group="bass"),
        "hn": dict(inst="hn", lvl=-22, pan=-0.3, width=0.6, depth="back", send=0.55, group="melody"),
        "tpt": dict(inst="tpt", lvl=-23, pan=0.2, width=0.5, depth="back", send=0.5, group="melody"),
        "tbn": dict(inst="tbn", lvl=-25, pan=0.3, width=0.5, depth="back", send=0.5, group="bass"),
        "timp": dict(inst="timp", lvl=-24, pan=0.0, width=0.6, depth="back", send=0.5, group="percussion"),
        "cym": dict(inst="cym", lvl=-30, pan=0.1, width=0.9, depth="back", send=0.5, group="percussion"),
        "harp": dict(inst="harp3", lvl=-26, pan=0.45, width=0.6, depth="mid", send=0.4, group="harmony"),
        "piano": dict(inst="piano", lvl=-24, pan=0.1, width=0.9, depth="mid", send=0.3, group="harmony"),
        "marimba": dict(inst="marimba", lvl=-28, pan=0.35, width=0.6, depth="mid", send=0.3, group="rhythm"),
        "tabla": SYN("tabla", tonic="D4", lvl=-27, pan=-0.2, width=0.5, depth="front", send=0.25, group="rhythm"),
        "santoor": SYN("santoor", lvl=-27, pan=0.4, width=0.6, depth="mid", send=0.35, group="melody"),
    }
    return c, mix, dict(duration=round(c.t(B(33)) + 2.5, 2), hall="Musikvereinsaal", target=-16.0, fade_s=1.5)


# ============================================================ CUSTOMS DESK: JAX v MIRA (counterpoint)
def customs_sparring():
    c = Cue("S2-customs-sparring", bpm=116, seed=4106)
    tr(c, ["cl", "bansuri", "guitar", "bass", "santoor", "tabla", "vibes"])
    c.track("perc", 0, drums=True)
    c.track("stamp", 0, drums=True)
    B = c.bar
    MIR = "G5:e A5:e C6:q ~A5:h | G5:q. F5:e E5:q ~D5:q"          # Mira's cell, in Jax's key (E natural)
    # 1-2 Jax states his case (his world: guitar swing, pizz walk, darbuka)
    for b in range(1, 3):
        for off, v in ((0, 70), (1 + 2 / 3, 56), (2, 66), (3 + 2 / 3, 58)):
            c.chord("guitar", ["D3", "A3", "C4", "F4"] if b % 2 else ["G2", "D3", "F3", "B3"], B(b) + off, 0.6, v,
                    roll=0.015, legato=0.8)
        for k in range(4):
            c.note("bass", pitch("D2" if b % 2 else "G1") + [0, 7, 12, 10][k], B(b) + k, 1, 72, legato=0.6)
        for off, nt, v in ((0, 36, 70), (2, 38, 60), (3 + 2 / 3, 37, 52)):
            c.note("perc", nt, B(b) + off, 0.25, v)
    c.seq("cl", JAX, B(1), 84, legato=0.9)
    # 3-4 Mira answers in hers: santoor clock, tabla keherwa, the guitar stops
    for k, p in enumerate(("F5", "G5", "A5", "C6", "A5", "G5", "F5", "D5") * 2):
        c.note("santoor", p, B(3) + k * 0.5, 0.5, 46, legato=1.0)
    W.theka(c, "tabla", "keherwa", B(3), 2, matra=0.5, vel=66, fill_last=False)
    c.seq("bansuri", MIR, B(3), 84, legato=1.0)
    meend(c, "bansuri", B(3) + 1, -200, 0.3)
    # 5-6 Jax cuts in before she has finished (bar 4 beat 3): the overlap starts
    c.seq("cl", "D5:q A4:u D5:t E5:u F5:t G5:u A5:t | r:w", B(4) + 2, 88, legato=0.9)
    # 7-10 counterpoint: both tunes at once, his swing under her line; both rhythm sections cross
    for b in range(5, 11):
        for off, v in ((0, 64), (1 + 2 / 3, 50), (2, 60), (3 + 2 / 3, 52)):
            c.chord("guitar", ["D3", "A3", "C4", "F4"] if b % 2 else ["G2", "D3", "F3", "B3"], B(b) + off, 0.5, v,
                    roll=0.015, legato=0.8)
        for k in range(4):
            c.note("bass", pitch("D2" if b % 2 else "G1") + [0, 7, 12, 10][k], B(b) + k, 1, 72, legato=0.6)
        for off, nt, v in ((0, 36, 64), (3 + 2 / 3, 37, 48)):
            c.note("perc", nt, B(b) + off, 0.25, v)
    W.theka(c, "tabla", "keherwa", B(5), 6, matra=0.5, vel=62, fill_last=False)
    c.seq("bansuri", MIR + " | " + MIR.replace("C6:q", "D6:q"), B(6), 82, legato=1.0)
    c.seq("cl", "r:h D4:q A3:u D4:t | E4:u F4:t ~E4:q r:h | r:h D4:q A3:u D4:t | E4:u F4:t G4:u A4:t ~A4:h",
          B(6), 78, legato=0.9)
    meend(c, "bansuri", B(8) + 1, -200, 0.3)
    # 11-12 the argument speeds up: one-beat jabs, alternating
    for k in range(8):
        b = B(11) + k
        if k % 2 == 0:
            c.seq("cl", "D5:e A4:e", b, 86 + k, legato=0.6)
        else:
            c.seq("bansuri", "C6:e A5:e", b, 86 + k, legato=0.8)
        c.note("tabla", W.BOLS["na" if k % 2 else "dha"], b, 0.5, 70 + k * 2)
        c.note("perc", 36, b + 0.5, 0.25, 60 + k * 2)
    # 13: truce - both land on the same A, together; 13.3: the stamp (button)
    c.note("cl", "A4", B(13), 2, 80, legato=1.0); c.note("bansuri", "A5", B(13), 2, 80, legato=1.0)
    meend(c, "bansuri", B(13), -100, 0.4)
    c.chord("guitar", ["D3", "A3", "D4", "F#4"], B(13), 1.5, 70, roll=0.02)
    c.note("vibes", "A5", B(13), 2, 56)
    c.note("stamp", 39, B(13) + 2.5, 0.3, 110)
    c.note("bass", "D2", B(13) + 2.5, 0.5, 96, legato=0.5)
    c.note("tabla", W.BOLS["dha"], B(13) + 2.5, 0.5, 100)
    mix = {"cl": dict(inst="cl", lvl=-20, pan=-0.3, width=0.4, depth="front", send=0.3, group="melody"),
           "bansuri": SYN("bansuri", lvl=-20, pan=0.3, width=0.4, depth="front", send=0.35, group="melody"),
           "guitar": dict(inst="guitar", lvl=-24, pan=-0.4, width=0.5, depth="front", send=0.2, group="rhythm"),
           "bass": dict(inst="pizz", lvl=-23, pan=-0.05, width=0.4, depth="mid", send=0.2, group="bass"),
           "santoor": SYN("santoor", lvl=-28, pan=0.45, width=0.6, depth="mid", send=0.35, group="rhythm"),
           "perc": dict(lvl=-27, pan=-0.35, width=0.5, depth="front", send=0.2, group="rhythm",
                        kit={36: "darb_dum", 38: "darb_tek", 37: "darb_ka"}),
           "tabla": SYN("tabla", tonic="D4", lvl=-26, pan=0.35, width=0.5, depth="front", send=0.2, group="rhythm"),
           "stamp": dict(gain=-4, pan=0.0, width=0.4, depth="front", send=0.25, group="rhythm", kit={39: "slap"}),
           "vibes": dict(inst="vibes", lvl=-27, pan=0.0, width=0.6, depth="mid", send=0.45, group="melody")}
    return c, mix, dict(duration=round(c.t(B(14)) + 1.5, 2), hall="Scala Milan Opera Hall", target=-17.0, fade_s=1.0)


ALL = dict(mira_world=mira_world, indian_demo=indian_demo, heart=heart_theme, cutaway=cutaway,
           main_full=main_theme_full, sparring=customs_sparring)
