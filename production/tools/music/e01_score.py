"""SECRET UNIVERSE - Episode 1 "The Parcel Nobody Ordered": the score (original).

Every cue is a function that builds a sulib.Cue (MIDI) and returns it with its metadata:
exact duration, key, tempo, hit points, silences that must be digitally silent, loop
points, motifs used and the mix table (preset per track + stem group). e01_render.py
renders them with the approved v2 sound (VPO SFZ orchestra + GeneralUser GS colours).

Show motifs reused here (all ours):
  MAIN   main-title head D-A-D-E-F (A1), 3+3+2 ostinato
  JAX    D Dorian swing, the head that never finishes (M1)
  MIRA   Sa-Re-Ga-Pa-Dha on F, celesta clockwork (M2)
  PIP    tiny C-major march + rubber stamp (M3)
New in E01:
  CHICHIKOV  a small clockwork waltz in B minor, one bar a beat short
  BARON      18th-century march in D for harpsichord / natural horns / timpani that goes
             wrong; under it the SAD TUNE (B minor, 8 bars)
  POST HORN  a postilion's march on the natural notes of a Bb horn
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch  # noqa: E402

THEME_HEAD = "D5:q A4:q D5:e E5:e F5:q | E5:h. C5:q"
THEME = ("D5:q A4:q D5:e E5:e F5:q | E5:h. C5:q | D5:q A4:q D5:e E5:e F5:e G5:e | A5:h. r:q | "
         "Bb5:q A5:q G5:q F5:q | G5:q F5:q E5:h | F5:q E5:q D5:q C#5:q | D5:w")
JAX = "D5:q A4:u D5:t E5:u F5:t ~E5:q | r:u D5:t C5:u A4:t B4:q. r:e"
MIRA = "G5:e A5:e C6:q ~A5:h | G5:q. F5:e Eb5:q ~D5:q | C5:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | ~C5:h F5:h"
PIP = "C6:e E6:e G6:e E6:e | C6:q G5:q | A5:e B5:e C6:e D6:e | E6:q C6:q"
SAD = ("F#4:h. E4:q | D4:q E4:q F#4:q B4:q | A4:h G4:q F#4:q | E4:h C#4:h | "
       "D4:h. C#4:q | B3:q C#4:q D4:q G4:q | F#4:h E4:q C#4:q | B3:w")
SAD_H = [["B2", "D3", "F#3"], ["G2", "B2", "D3"], ["E2", "G2", "B2"], ["F#2", "A#2", "C#3"],
         ["B2", "D3", "F#3"], ["G2", "B2", "D3"], ["E2", "G2", "B2"], ["B2", "D3", "F#3"]]
CHICH = ("F#5:q. E5:e D5:q | E5:q D5:q B4:q | C#5:q D5:q E5:q | D5:h. | "
         "B5:q. A5:e G5:q | G5:q F#5:q E5:q | A#4:q B4:q C#5:q | B4:h")     # last bar is 2/4: a beat short
CHICH_H = [("B2", ["D4", "F#4"]), ("G2", ["E4", "B4"]), ("F#2", ["E4", "A#4"]), ("B2", ["D4", "F#4"]),
           ("G2", ["D4", "G4"]), ("E2", ["E4", "G4"]), ("F#2", ["C#4", "E4"]), ("B2", ["D4", "F#4"])]
MARCH = ("D5:q. D5:e F#5:q. F#5:e | A5:h F#5:q D5:q | E5:q. E5:e G5:q. E5:e | F#5:q D5:q A4:h | "
         "B5:q. B5:e A5:q G5:q | F#5:q E5:q D5:q | E5:q. F#5:e G5:q C5:q | D5:h r:h")
# bar 6 is 3/4 (a bar too short); bar 7 ends on C natural (the wrong note) instead of C#
MARCH_BARS = [4, 4, 4, 4, 4, 3, 4, 4]
MARCH_H = [("D2", ["F#3", "A3", "D4"]), ("D2", ["F#3", "A3", "D4"]), ("A1", ["E3", "A3", "C#4"]),
           ("D2", ["F#3", "A3", "D4"]), ("G2", ["G3", "B3", "D4"]), ("A1", ["F#3", "A3", "D4"]),
           ("A1", ["E3", "G3", "C#4"]), ("D2", ["F#3", "A3", "D4"])]
POSTHORN = ("F4:q Bb4:e D5:q Bb4:e | F5:q. D5:q. | Bb4:q D5:e F5:q D5:e | Bb4:q. F4:q. | "
            "D5:q D5:e D5:q F5:e | Bb5:q. F5:q. | D5:q Bb4:e F4:q D5:e | Bb4:q. r:q.")


def S(c, sec):
    """seconds -> beats (constant tempo part of a cue)."""
    return sec * c.bpm / 60.0


def bars_to_beats(bars):
    out, b = [], 0.0
    for n in bars:
        out.append(b)
        b += n
    return out, b


# ============================================================ 1 COLD OPEN
def cold_open():
    c = Cue("E01-M01-cold-open", bpm=112, seed=1001)
    for t, p, v, pan, rv in (("pizzB", GM["pizz"], 105, 60, 40), ("bsn", GM["bassoon"], 105, 54, 40),
                             ("clar", GM["clarinet"], 100, 70, 50), ("low", GM["cello"], 95, 64, 50),
                             ("cel", GM["celesta"], 80, 40, 60), ("picc", GM["piccolo"], 90, 76, 50),
                             ("glock", GM["glock"], 80, 80, 55), ("pad", GM["strings"], 80, 64, 70),
                             ("timp", GM["timpani"], 100, 64, 60)):
        c.track(t, p, v, pan, rv)
    c.track("drums", 0, 90, 64, 40, drums=True)
    T = lambda s: S(c, s)
    # 0.6 s: PIP's lens - one celesta note in the black
    c.note("cel", "A5", T(0.6), 1.5, 52)
    # 3.4-9.0: sly walk (pizz bass + woodblock) under bassoon quoting the theme head, staccato
    walk = ["D2", "F2", "A2", "C3", "B2", "A2", "G2", "F2", "E2", "G2", "A2", "C#3"]
    b0 = T(3.4)
    for i in range(int((T(40.6) - b0))):
        bb = b0 + i
        if bb > T(40.6):
            break
        # systems die one by one: thin the walk out over time
        if T(20) < bb < T(28) and i % 2:
            continue
        if bb >= T(28) and i % 2:
            continue
        c.note("pizzB", walk[i % len(walk)], bb, 1, 80 if bb < T(20) else 66, legato=0.5)
        if bb < T(28):
            c.hit("wood_hi" if i % 2 == 0 else "wood_lo", bb, 54 if bb < T(20) else 40, 0.2)
    c.seq("bsn", "D3:e r:e A2:e r:e D3:e E3:e F3:e r:e | E3:e r:e r:q C3:e r:e r:q", b0, 72, legato=0.45)
    # 9.0 HIT engine dies: low cello D, power-down glide
    c.note("low", "D3", T(8.95), T(1.2), 92, legato=1.0)
    c.bend("low", T(9.0), T(10.0), 0, -200)
    c.note("timp", "D2", T(9.0), 1, 70)
    c.hit("kick2", T(9.0), 64)
    # clarinet answers between lines
    c.seq("clar", JAX.split("|")[0], T(10.2), 62, legato=0.9)
    # 13.2 HIT coffee light goes out: a celesta blip that sags
    c.note("cel", "E6", T(13.2), 0.75, 70)
    # 17-40: Temi section - thin, hold-music-polite, dying: sustained pad that loses notes
    pad = [("D4", 17.0, 23.0), ("F4", 17.0, 28.0), ("A4", 17.0, 34.0), ("C5", 17.0, 39.5)]
    for p, a, e in pad:
        c.note("pad", p, T(a), T(e - a), 44, legato=1.0)
    c.swell("pad", T(17), T(40.6), 90, 40)
    c.seq("clar", "r:h. A4:e B4:e | C5:q. A4:e r:h", T(30.5), 56, legato=0.8)
    # 40.95 HIT the shop-door bell (sound effect): the music has already stopped at 40.6
    # 41.8-48.5: the job - PIP's tiny march, transposed to D, very quiet
    c.seq("picc", "D6:e F#6:e A6:e F#6:e | D6:q A5:q | B5:e C#6:e D6:e E6:e | F#6:q r:q", T(41.9), 58, legato=0.5)
    c.seq("glock", "D6:e F#6:e A6:e F#6:e | D6:q A5:q", T(41.9), 44, legato=0.5)
    for k in range(4):
        c.note("bsn", "D3" if k % 2 == 0 else "A2", T(41.9) + 2 * k, 0.5, 60, legato=0.4)
    # "The fee is-" 48.6: everything stops; 49.6 "Exactly what we owe": low strings swell (uh-oh)
    c.chord("low", ["D2", "A2"], T(49.6), T(2.4), 60, legato=1.0)
    c.swell("low", T(49.6), T(52.0), 40, 100)
    # 52.1-55.9 "Take it take it...": pizz repeated D, accelerating and growing
    t = 52.15
    k = 0
    while t < 55.85:
        c.note("pizzB", "D3", T(t), 0.25, 60 + k * 3, legato=0.4)
        t += max(0.16, 0.42 - k * 0.03)
        k += 1
    # 56.0 HIT the "Take it" stamp: bass drum + pizz chord + bassoon, PIP's rubber stamp
    c.hit("kick2", T(56.0), 96, 1)
    c.hit("wood_lo", T(56.0), 80)
    c.chord("pizzB", ["D2", "A2", "F3", "D4"], T(56.0), 0.5, 108, legato=0.4)
    c.note("bsn", "D2", T(56.0), 0.5, 100, legato=0.4)
    # 56.3-60.4 PIP files his report: one ticking note; 60.4-61.7 true silence
    for s_ in (57.0, 58.0, 59.0, 60.0):
        c.hit("wood_hi", T(s_), 30, 0.2)
    # 61.7 HIT the engine coughs back: low swell + Jax's motif, warmer
    c.chord("low", ["D2", "A2", "D3"], T(61.7), T(3.0), 70, legato=1.0)
    c.swell("low", T(61.7), T(64.7), 30, 100)
    c.note("timp", "A1", T(61.7), 1, 60)
    c.seq("clar", JAX + " | D5:q A4:u D5:t E5:u F5:t G5:q | ~E5:h r:h", T(63.2), 72, legato=0.95)
    for i in range(int(T(74.0) - T(63.2))):
        c.note("pizzB", walk[i % 8], T(63.2) + i, 1, 70, legato=0.5)
        if i % 2:
            c.hit("rim", T(63.2) + i, 40)
    # 74.5 BUTTON: staccato D, then out (title sting follows at ~75.9)
    c.chord("pizzB", ["D2", "D3", "A3"], T(74.5), 0.5, 104, legato=0.4)
    c.note("bsn", "D2", T(74.5), 0.5, 96, legato=0.4)
    c.hit("wood_hi", T(74.5), 76)
    mix = {
        "pizzB": dict(inst="pizz", lvl=-22, pan=0.15, send=0.2, group="harmony"),
        "bsn": dict(inst="bsn", lvl=-23, pan=-0.2, send=0.2, group="melody"),
        "clar": dict(inst="cl", lvl=-21, pan=-0.1, send=0.25, group="melody"),
        "low": dict(inst="vc", lvl=-25, pan=0.25, send=0.3, group="harmony"),
        "cel": dict(inst="celesta", lvl=-27, pan=-0.4, send=0.35, group="melody"),
        "picc": dict(inst="picc", lvl=-26, pan=0.2, send=0.25, group="melody"),
        "glock": dict(inst="glock", lvl=-31, pan=0.35, send=0.25, group="melody"),
        "pad": dict(inst="vln2", lvl=-31, pan=-0.2, send=0.45, group="harmony"),
        "timp": dict(inst="timp", lvl=-27, pan=0, send=0.3, group="percussion"),
        "drums": dict(lvl=-30, pan=0.05, send=0.2, group="percussion"),
    }
    meta = dict(id="M01", title="Cold open - the repossession", scenes=["0"], duration=77.0,
                key="D Dorian / D minor (PIP's march in D)", tempo="112 BPM 4/4, swing in the Jax section",
                hits=[[0.6, "PIP's lens (celesta)"], [9.0, "engine dies (cello power-down glide)"],
                      [13.2, "coffee light goes out (celesta blip)"],
                      [40.95, "shop-door bell = job arrives (music stops at 40.6, bell is SFX)"],
                      [56.0, "\"Take it\" - PIP's stamp (bass drum + pizz chord)"],
                      [61.7, "engine coughs back (low swell, Jax motif)"],
                      [74.5, "button into the title sting (sting starts ~75.9)"]],
                silences=[[40.6, 41.85], [60.4, 61.7]],
                motifs=["JAX", "MAIN head (bassoon)", "PIP (in D)"], loud=-18.0, rt60=1.6, end="fade")
    return c, mix, meta


# ============================================================ 2 APPROACH
def approach():
    c = Cue("E01-M02-approach", bpm=72, seed=1002)
    for t, p in (("vln", GM["strings"]), ("vla", GM["strings2"]), ("vc", GM["cello"]), ("cb", GM["contrabass"]),
                 ("hn", GM["horn"]), ("harp", GM["harp"]), ("cel", GM["celesta"]), ("trem", GM["trem"])):
        c.track(t, p)
    B = c.bar
    # bars 1-5 wonder: D Lydian (G#), high strings, harp, horn with the theme head in major
    for bar, ch in ((1, ["D4", "A4", "E5"]), (2, ["D4", "A4", "F#5"]), (3, ["E4", "G#4", "D5"]),
                    (4, ["D4", "A4", "F#5"]), (5, ["E4", "G#4", "B4"])):
        c.chord("vla", ch, B(bar), 4, 50)
        c.note("cb", "D2", B(bar), 4, 46)
        c.seq("harp", "D3:e A3:e E4:e F#4:e A4:e E5:e F#5:e A5:e", B(bar), 46)
    c.swell("vla", 0, B(6), 50, 100)
    c.seq("hn", "D4:h A3:q D4:e E4:e | F#4:w | E4:h. G#4:q | A4:w", B(2), 66, legato=1.0)
    # bars 4-8: the address loses its letters - a celesta figure loses its last notes
    FIG = ["D6", "A5", "F#6", "E6", "A5", "G#5", "B5", "E6"]
    for k, n_keep in enumerate((8, 7, 6, 4, 1)):     # HATCHET -> HATCH -> HAT -> SILVER -> THE
        for i in range(n_keep):
            c.note("cel", FIG[i], B(4) + k * 2.5 + i * 0.25, 0.25, 52, legato=0.6)
    # bars 6-13 unease: D minor -> Bb/D -> Eb/D (the flat 2nd), tremolo creeps in
    for bar, ch in ((6, ["D4", "F4", "A4"]), (7, ["D4", "F4", "A4"]), (8, ["D4", "F4", "Bb4"]),
                    (9, ["D4", "F4", "Bb4"]), (10, ["Eb4", "G4", "Bb4"]), (11, ["Eb4", "G4", "Bb4"]),
                    (12, ["D4", "Eb4", "A4"]), (13, ["D4", "Eb4", "A4"])):
        c.chord("vla", ch, B(bar), 4, 48)
        c.note("cb", "D2", B(bar), 4, 50)
    c.chord("trem", ["D3", "Eb3"], B(8), 4 * 6, 50)
    c.swell("trem", B(8), B(14), 30, 90)
    # Mamani's "withdrawn" (~32-44 s): the betrayal turn D-G#-A-Bb-A in cellos, quiet
    c.seq("vc", "D3:q. G#2:e A2:q Bb2:q | A2:w", B(10), 62, legato=1.0)
    c.seq("vln", "r:w | r:h A5:h | Bb5:w | A5:w", B(11), 46, legato=1.0)
    # bars 14-19: settles into a question: open D-A with Eb above, then thins away
    for bar in range(14, 19):
        c.chord("vla", ["D4", "A4"], B(bar), 4, 44)
        c.note("cb", "D2", B(bar), 4, 40)
    c.note("vln", "Eb5", B(15), 12, 40, legato=1.0)
    c.swell("vla", B(14), B(19), 90, 30)
    c.swell("vln", B(15), B(19), 80, 20)
    c.note("cel", "D6", B(17), 2, 40)
    c.note("cel", "Eb6", B(18), 2, 34)
    mix = {
        "vln": dict(inst="vln1", lvl=-26, pan=-0.4, send=0.55, group="melody"),
        "vla": dict(inst="vln2", lvl=-25, pan=-0.1, send=0.5, group="harmony"),
        "vc": dict(inst="vc", lvl=-25, pan=0.3, send=0.4, group="melody"),
        "cb": dict(inst="cb", lvl=-29, pan=0.3, send=0.35, group="harmony"),
        "hn": dict(inst="hn", lvl=-23, pan=-0.2, send=0.55, group="melody"),
        "harp": dict(inst="harp", lvl=-26, pan=0.45, send=0.45, group="harmony"),
        "cel": dict(inst="celesta", lvl=-25, pan=-0.35, send=0.4, group="melody"),
        "trem": dict(inst="trem", lvl=-31, pan=0.1, send=0.5, group="harmony"),
    }
    meta = dict(id="M02", title="Approach to the pole", scenes=["2"], duration=66.0,
                key="D Lydian (wonder) -> D minor -> Eb over D (unease)", tempo="72 BPM 4/4",
                hits=[[10.0, "address starts losing letters: the celesta figure drops notes (stages at 10.0, 12.1, 14.2, 16.2, 18.3)"],
                      [16.7, "tonality darkens (D minor)"], [33.3, "betrayal turn in cellos (under Mamani)"],
                      [46.7, "settles to the open question chord"]],
                silences=[], motifs=["MAIN head in major (horn)", "betrayal turn (from A3)"], loud=-19.0,
                rt60=2.8, end="fade")
    return c, mix, meta


# ============================================================ 3 CHICHIKOV
CH_MIX = {
    "box": dict(gm=True, program=10, lvl=-21, pan=-0.15, send=0.35, group="melody"),          # GU GS Music Box
    "mand": dict(gm=True, program=25, bank=16, lvl=-25, pan=0.35, send=0.3, group="melody"),   # GU GS Mandolin (balalaika-like tremolo)
    "pizz": dict(inst="pizz", lvl=-25, pan=0.2, send=0.3, group="harmony"),
    "chords": dict(inst="pizz", lvl=-29, pan=-0.3, send=0.3, group="harmony"),
    "cl": dict(inst="cl", lvl=-28, pan=0.1, send=0.4, group="melody"),
    "cel": dict(inst="celesta", lvl=-28, pan=-0.4, send=0.4, group="melody"),
}


def _waltz_bar(c, b, root, up, beats=3, vel=62):
    c.note("pizz", root, b, 1, vel, legato=0.5)
    for k in range(1, beats):
        c.chord("chords", up, b + k, 1, vel - 14, legato=0.4)


def _chich_tracks(c):
    for t, p in (("box", 10), ("mand", 25), ("pizz", GM["pizz"]), ("chords", GM["pizz"]),
                 ("cl", GM["clarinet"]), ("cel", GM["celesta"])):
        c.track(t, p)


def chichikov_statement():
    c = Cue("E01-M03a-chichikov-motif-20s", bpm=126, beats_per_bar=3, seed=1003, rit=(32, 38, 96))
    _chich_tracks(c)
    lens = [3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3]
    starts, total = bars_to_beats(lens)
    c.seq("box", CHICH, 0, 70, legato=0.9)
    c.bend("box", starts[3] + 0.3, starts[3] + 1.2, 0, -30)      # the held D sags 30 cents: slightly wrong
    c.bend("box", starts[4], starts[4] + 0.05, -30, 0)
    c.seq("box", "F#5:q. E5:e D5:q | E5:q D5:q B4:q | C#5:q D5:q E5:q | ~D5:h. | B4:h.", starts[8], 64, legato=0.9)
    # balalaika-like tremolo (mandolin) a third below in the repeat
    for bi, (p, d) in enumerate((("D5", 3), ("B4", 3), ("A#4", 3), ("B4", 3))):
        b = starts[8 + bi]
        k = 0
        while k * 0.25 < d - 0.1:
            c.note("mand", p, b + k * 0.25, 0.25, 50 + (6 if k % 4 == 0 else 0), legato=0.9)
            k += 1
    for i, L in enumerate(lens):
        root, up = CHICH_H[i % 8] if i < 8 else CHICH_H[i - 8] if i < 12 else CHICH_H[0]
        _waltz_bar(c, starts[i], root, up, beats=L)
    meta = dict(id="M03a", title="Chichikov's motif - statement", scenes=["5", "12", "16", "31"], duration=20.0,
                key="B minor", tempo="126 BPM 3/4 (bar 8 is 2/4: a beat short), ritardando at the end",
                hits=[[0.0, "first note"], [round(starts[7] * 60 / 126, 2), "the short bar"]],
                silences=[], motifs=["CHICHIKOV"], loud=-19.0, rt60=2.0, end="fade")
    return c, CH_MIX, meta


def chichikov_underscore():
    c = Cue("E01-M03b-chichikov-underscore-45s", bpm=120, beats_per_bar=3, seed=1004, rit=(80, 90, 96))
    _chich_tracks(c)
    lens = [3] * 7 + [2] + [3] * 7 + [2] + [3] * 13
    starts, total = bars_to_beats(lens)
    for i, L in enumerate(lens):
        root, up = CHICH_H[i % 8]
        _waltz_bar(c, starts[i], root, up, beats=L, vel=52)
    # fragments only: first phrase on music box, very quiet; second phrase on celesta
    c.seq("box", "F#5:q. E5:e D5:q | E5:q D5:q B4:q | C#5:q D5:q E5:q | ~D5:h.", starts[4], 56, legato=0.9)
    c.bend("box", starts[7] + 0.3, starts[7] + 1.0, 0, -30)
    c.seq("cel", "B5:q. A5:e G5:q | G5:q F#5:q E5:q | A#4:q B4:q C#5:q | B4:h", starts[12], 50, legato=0.9)
    # clarinet: a long, low, courteous counter-line (very soft)
    c.seq("cl", "F#4:h. | E4:h. | D4:h. | C#4:h. | B3:h. | D4:h. | E4:h. | F#4:h.", starts[16], 46, legato=1.0)
    for bi in range(4):                                   # mandolin tremolo, long notes
        b = starts[20 + bi]
        for k in range(12):
            c.note("mand", ["F#4", "E4", "D4", "C#4"][bi], b + k * 0.25, 0.25, 40, legato=0.9)
    c.seq("box", "F#5:q. E5:e D5:q | E5:q D5:q B4:q", starts[25], 46, legato=0.9)
    meta = dict(id="M03b", title="Chichikov's motif - underscore", scenes=["5", "12", "16", "25"], duration=45.0,
                key="B minor", tempo="120 BPM 3/4 (two short bars)", hits=[], silences=[],
                motifs=["CHICHIKOV"], loud=-21.0, rt60=2.0, end="fade")
    return c, CH_MIX, meta


# ============================================================ 4 BARON
BARON_MIX = {
    "hpsi": dict(gm=True, program=6, lvl=-21, pan=-0.2, send=0.3, group="melody"),             # GU GS Harpsichord
    "hpsi2": dict(gm=True, program=6, bank=8, lvl=-29, pan=0.3, send=0.3, detune=24, group="harmony"),  # coupled, 24 c sharp
    "hn": dict(inst="hn", lvl=-22, pan=0.2, send=0.45, group="melody"),
    "vln": dict(inst="vln1", lvl=-25, pan=-0.4, send=0.4, group="melody"),
    "vc": dict(inst="vc", lvl=-24, pan=0.35, send=0.4, group="melody"),
    "cb": dict(inst="cb", lvl=-28, pan=0.3, send=0.3, group="harmony"),
    "timp": dict(inst="timp", lvl=-25, pan=0, send=0.35, group="percussion"),
    "vc_solo": dict(inst="vc_solo", lvl=-20, pan=0.05, send=0.45, group="melody"),
}


def _baron_tracks(c, names):
    progs = dict(hpsi=6, hpsi2=6, hn=GM["horn"], vln=GM["strings"], vc=GM["cello"], cb=GM["contrabass"],
                 timp=GM["timpani"], vc_solo=GM["cello"])
    for n in names:
        c.track(n, progs[n])


def _march(c, start, vel=80, hpsi2=True, nbars=8):
    starts, total = bars_to_beats(MARCH_BARS[:nbars])
    c.seq("hpsi", " | ".join(MARCH.split(" | ")[:nbars]), start, vel, legato=0.85)
    for i, (bass, up) in enumerate(MARCH_H[:nbars]):
        b = start + starts[i]
        L = MARCH_BARS[i]
        for k in range(L):                     # continuo: bass on every beat, chord on 1 and 3
            c.note("hpsi", pitch(bass) + 12, b + k, 1, vel - 12, legato=0.7)
            if k in (0, 2):
                c.chord("hpsi", up, b + k, 1, vel - 18, legato=0.7)
                if hpsi2:
                    c.chord("hpsi2", up, b + k, 1, vel - 22, legato=0.7)
    return total


def baron_grand():
    c = Cue("E01-M04a-baron-theme-grand-30s", bpm=104, seed=1005, rit=(44, 50, 92))
    _baron_tracks(c, ["hpsi", "hpsi2", "hn", "vln", "vc", "cb", "timp"])
    tot = _march(c, 0, 86)
    c.seq("vln", MARCH, 0, 78, legato=0.8)
    # natural horns in D: only harmonic-series notes (D4 F#4 A4 D5 E5 F#5)
    HN = ("D4:q. D4:e F#4:q. F#4:e | A4:h F#4:q D4:q | E5:q. E5:e A4:q. A4:e | F#4:q D4:q A3:h | "
          "D5:q. D5:e A4:q A4:q | F#4:q E5:q D5:q | E5:q. F#5:e E5:q A4:q | D4:h r:h")
    c.seq("hn", HN, 0, 84, legato=0.85)
    starts, _ = bars_to_beats(MARCH_BARS)
    for i, (bass, up) in enumerate(MARCH_H):
        c.note("cb", bass, starts[i], MARCH_BARS[i], 70)
        t_ = "D2" if bass in ("D2", "G2") else "A1"
        c.note("timp", t_, starts[i], 1, 86)
        c.note("timp", t_, starts[i] + 0.75, 0.25, 60)
        c.note("timp", t_, starts[i] + 1, 1, 72)
    # second strain (bars 9-12): the march again, louder, and UNDER it the sad tune (cellos)
    _march(c, tot, 92, nbars=4)
    c.seq("vln", "D5:q. D5:e F#5:q. F#5:e | A5:h F#5:q D5:q | E5:q. E5:e G5:q. E5:e | D5:w", tot, 84, legato=0.8)
    c.seq("hn", "D4:q. D4:e F#4:q. F#4:e | A4:h F#4:q D4:q | E5:q. E5:e A4:q. A4:e | D5:w", tot, 92, legato=0.85)
    c.seq("vc", "F#3:h. E3:q | D3:q E3:q F#3:q B3:q | A3:h G3:q F#3:q | E3:h D3:h", tot, 82, legato=1.0)
    for k in range(4):
        c.note("timp", "D2" if k != 2 else "A1", tot + k * 4, 1, 92)
    # end chord with a timpani roll
    for i in range(12):
        c.note("timp", "D2", tot + 16 + i * 0.25, 0.25, 60 + i * 4)
    c.chord("hn", ["D4", "F#4", "A4", "D5"], tot + 16, 3, 96)
    c.chord("hpsi", ["D3", "A3", "D4", "F#4", "A4", "D5"], tot + 16, 3, 90, roll=0.03)
    c.note("cb", "D2", tot + 16, 3, 80)
    meta = dict(id="M04a", title="The Baron's theme - grand", scenes=["3", "6", "10", "11"], duration=30.0,
                key="D major (march); sad tune B minor underneath", tempo="104 BPM 4/4; bar 6 is 3/4 (a bar too short)",
                hits=[[0.0, "march starts"], [round(starts[5] * 60 / 104, 2), "the short bar"],
                      [round(starts[6] * 60 / 104 + 3 * 60 / 104, 2), "the wrong note (C natural)"],
                      [round(tot * 60 / 104, 2), "second strain; sad tune enters in cellos"]],
                silences=[], motifs=["BARON march", "SAD TUNE"], loud=-16.0, rt60=2.2, end="fade")
    return c, BARON_MIX, meta


def baron_threadbare():
    c = Cue("E01-M04b-baron-theme-threadbare-40s", bpm=84, seed=1006, rit=(40, 48, 66))
    _baron_tracks(c, ["hpsi", "hpsi2"])
    # solo harpsichord, slower, more wrong: a stuck repeated note, a missing beat, a gap
    BAD = ("D5:q. D5:e F#5:q. F#5:e | A5:h F#5:q D5:q | E5:q. E5:e G5:q. E5:e | F#5:q D5:q A4:h | "
           "B5:q. B5:e B5:e B5:e A5:q | F#5:q E5:q | r:h | E5:q. F#5:e G5:q C5:q | D5:h r:h")
    lens = [4, 4, 4, 4, 4, 2, 2, 4, 4]
    c.seq("hpsi", BAD, 0, 74, legato=0.85)
    starts, tot = bars_to_beats(lens)
    harm = [MARCH_H[0], MARCH_H[1], MARCH_H[2], MARCH_H[3], MARCH_H[4], MARCH_H[5], None, MARCH_H[6], MARCH_H[7]]
    for i, hb in enumerate(harm):
        if hb is None:
            continue
        bass, up = hb
        for k in range(lens[i]):
            c.note("hpsi", pitch(bass) + 12, starts[i] + k, 1, 60, legato=0.7)
            if k == 0:
                c.chord("hpsi2", up, starts[i], 2, 50, legato=0.7)
    # then the sad tune, first half, right hand alone, thin
    c.seq("hpsi", SAD.split("|")[0] + "|" + SAD.split("|")[1] + "|" + SAD.split("|")[2] + "|" + SAD.split("|")[3]
          .replace("C#4:h", "C#4:h"), tot, 62, transpose=12, legato=0.9)
    for i in range(4):
        c.chord("hpsi2", [pitch(p) + 12 for p in SAD_H[i]], tot + i * 4, 4, 40, legato=0.9)
    meta = dict(id="M04b", title="The Baron's theme - threadbare (solo harpsichord)", scenes=["14", "20", "22"],
                duration=40.0, key="D major -> B minor", tempo="84 BPM 4/4 with a stuck note, a short bar and a gap",
                hits=[[round(starts[4] * 60 / 84, 2), "stuck repeated B"], [round(starts[6] * 60 / 84, 2), "the gap"],
                      [round(tot * 60 / 84, 2), "sad tune (right hand alone)"]],
                silences=[], motifs=["BARON march", "SAD TUNE"], loud=-20.0, rt60=1.8, end="fade")
    return c, BARON_MIX, meta


def baron_sad_tune():
    c = Cue("E01-M04c-baron-sad-tune-cello-45s", bpm=52, seed=1007, rit=(30, 36, 46))
    _baron_tracks(c, ["vc_solo"])
    c.seq("vc_solo", SAD + " | ~B3:w", 0, 74, transpose=-12, legato=1.0,
          curve=lambda f: int(14 * (1 - abs(f - 0.55) / 0.55)) - 4)
    for b, c0 in ((0, -40), (12, -30), (20, -40)):          # small expressive scoops
        c.bend("vc_solo", b, b + 0.4, c0, 0)
    meta = dict(id="M04c", title="The Baron's sad tune - solo cello", scenes=["14", "21", "29"], duration=45.0,
                key="B minor", tempo="52 BPM 4/4, slowing to 44", hits=[], silences=[],
                motifs=["SAD TUNE"], loud=-20.0, rt60=2.4, end="fade")
    return c, BARON_MIX, meta


# ============================================================ 5 INVENTORY MONTAGE
def inventory():
    c = Cue("E01-M05-inventory-montage", bpm=132, seed=1008)
    for t, p in (("hpsi", 6), ("hpsi2", 6), ("bsn", GM["bassoon"]), ("pizz", GM["pizz"]),
                 ("cel", GM["celesta"]), ("glock", GM["glock"])):
        c.track(t, p)
    c.track("drums", 0, drums=True)
    B = c.bar
    keys = [0, 5, 0, 7, -3, 0]            # D, G, D, A, B (minor colour), D
    phr = ["D5:e F#5:e A5:e F#5:e D5:e A4:e D5:q | E5:e G5:e B5:e G5:e E5:q C5:q",   # C natural: wrong
           "F#5:q. F#5:e A5:e F#5:e D5:q | B5:q A5:q G5:q F#5:q"]
    for blk in range(6):
        b0 = B(1 + blk * 5)
        tr = keys[blk]
        # HIT on the block downbeat: the stamp (bass drum + pizz chord + harpsichord cluster)
        c.hit("kick2", b0, 92, 1)
        c.chord("pizz", [pitch("D2") + tr, pitch("A2") + tr, pitch("D3") + tr], b0, 0.5, 100, legato=0.4)
        c.chord("hpsi", [pitch(p) + tr for p in ("D4", "E4", "F#4", "A4")], b0, 1, 90, legato=0.6)
        # 4 bars: the march motif on harpsichord (layered with a 24-cent-sharp double), bassoon oom-pah
        c.seq("hpsi", phr[blk % 2] + " | " + phr[(blk + 1) % 2], b0 + 1, 82, transpose=tr, legato=0.6)
        c.seq("hpsi2", phr[blk % 2] + " | " + phr[(blk + 1) % 2], b0 + 1, 62, transpose=tr, legato=0.6)
        for k in range(16):
            c.note("bsn", pitch("D3") + tr if k % 2 == 0 else pitch("A2") + tr, b0 + 1 + k, 0.5, 66, legato=0.4)
            c.hit("wood_hi" if k % 2 else "wood_lo", b0 + 1 + k, 44, 0.2)
        # Mira's tags: celesta clockwork answer in the 5th bar of each block
        c.seq("cel", "C6:s A5:s F5:s A5:s C6:s A5:s F5:s A5:s G5:e A5:e C6:q", b0 + 17, 54, transpose=tr, legato=0.5)
        c.note("glock", pitch("A6") + tr, b0 + 19.5, 0.5, 50)
    # end button at 54.55: one stamp and out
    end = B(31)
    c.hit("kick2", end, 96, 1)
    c.chord("pizz", ["D2", "A2", "D3", "F#3"], end, 0.5, 106, legato=0.4)
    c.chord("hpsi", ["D3", "A3", "D4", "F4"], end, 1, 90, legato=0.6)       # a minor 3rd: wrong to the last
    mix = {
        "hpsi": dict(gm=True, program=6, lvl=-20, pan=-0.2, send=0.25, group="melody"),
        "hpsi2": dict(gm=True, program=6, bank=8, lvl=-27, pan=0.3, send=0.25, detune=24, group="melody"),
        "bsn": dict(inst="bsn", lvl=-25, pan=0.2, send=0.2, group="harmony"),
        "pizz": dict(inst="pizz", lvl=-24, pan=-0.1, send=0.25, group="harmony"),
        "cel": dict(inst="celesta", lvl=-26, pan=-0.4, send=0.3, group="melody"),
        "glock": dict(inst="glock", lvl=-30, pan=0.4, send=0.3, group="melody"),
        "drums": dict(lvl=-27, pan=0, send=0.2, group="percussion"),
    }
    spb = 60 / 132
    meta = dict(id="M05", title="The inventory montage (the harpsichord that has gone wrong)", scenes=["13"],
                duration=55.0, key="D major, moving D-G-D-A-B-D per block", tempo="132 BPM 4/4, 5-bar blocks",
                hits=[[round(B(1 + k * 5) * spb, 2), f"stamp hit {k + 1} (cut point)"] for k in range(6)] +
                     [[round(end * spb, 2), "end button"]],
                silences=[], motifs=["BARON march (harpsichord)", "MIRA clockwork (celesta)"], loud=-17.0,
                rt60=1.6, end="fade")
    return c, mix, meta


# ============================================================ 6 POST HORN (diegetic, dry)
def post_horn():
    c = Cue("E01-M06-frozen-post-horn", bpm=80, seed=1009)
    c.track("horn", GM["trumpet"])
    T = lambda s: S(c, s)
    # 0.4 a crack: a split, scooped blip; then stuck notes that fail
    c.note("horn", "Bb4", T(0.4), T(0.12), 96, human=False, legato=1.0)
    c.bend("horn", T(0.4), T(0.52), -180, -60)
    for s_, p, d in ((1.6, "F4", 0.18), (2.3, "F4", 0.12), (3.6, "Bb4", 0.35), (4.6, "Bb4", 0.2),
                     (5.1, "D5", 0.15), (6.4, "F4", 0.5)):
        c.note("horn", p, T(s_), T(d), 70, human=False, legato=1.0)
    c.bend("horn", T(1.6), T(6.9), -90, -60)               # very flat while frozen
    # 7.5-29: the postilion's march (6/8), drifting up toward pitch as it thaws
    tune_start = T(7.5)
    end_b = c.seq("horn", POSTHORN.replace(" | Bb4:q. r:q.", ""), tune_start, 84, legato=0.8)
    c.bend("horn", tune_start, end_b, -55, -12)
    # it stumbles: a hesitation, a wrong partial, then the last note cracks and sags
    t = end_b + 0.6
    c.note("horn", "D5", t, 0.5, 70, legato=1.0)
    c.note("horn", "F5", t + 0.9, 0.3, 64, legato=1.0)
    c.note("horn", "Bb4", t + 2.0, 2.4, 74, legato=1.0)
    c.bend("horn", t, t + 2.0, -12, -12)
    c.bend("horn", t + 2.0, t + 4.4, -20, -60)
    # one last try at the opening call: it gets two notes in and the third cracks and sags
    t2 = t + 6.0
    c.note("horn", "F4", t2, 0.5, 70, legato=1.0)
    c.note("horn", "Bb4", t2 + 0.6, 0.4, 70, legato=1.0)
    c.note("horn", "D5", t2 + 1.2, 2.6, 66, legato=1.0)
    c.bend("horn", t2, t2 + 1.2, -15, -15)
    c.bend("horn", t2 + 1.25, t2 + 1.35, -170, -30)       # the crack
    c.bend("horn", t2 + 1.4, t2 + 3.8, -30, -190)         # and the sag
    mix = {"horn": dict(inst="tpt_solo", lvl=-18, pan=0.0, send=0.08, group="melody")}
    meta = dict(id="M06", title="The frozen post horn (diegetic: plays in the cold store)", scenes=["15"],
                duration=35.0, key="Bb (natural notes of a Bb post horn: F4 Bb4 D5 F5 Bb5)",
                tempo="free, then 80 BPM (quarter) in 6/8", hits=[[0.4, "the crack"], [1.6, "stuck notes"],
                                                    [7.5, "the march begins"],
                                                    [round((t + 2.0) * 60 / 80, 2), "the march stumbles to its last note"],
                                                    [round((t2 + 1.25) * 60 / 80, 2), "one more try: cracks and sags"]],
                silences=[], motifs=["POST HORN march"], loud=-18.0, rt60=0.35, end="fade",
                note="dry and close: no orchestra, a 0.35 s tiny-room tail only")
    return c, mix, meta


# ============================================================ 7 THE OFFER
def offer(seconds):
    nb = int(seconds // 4)
    c = Cue(f"E01-M07-offer-{seconds}s", bpm=60, seed=1010 + seconds)
    for t, p in (("tick", GM["pizz"]), ("cb", GM["contrabass"]), ("hi", GM["strings"]),
                 ("mid", GM["strings2"]), ("cel", GM["celesta"]), ("box", 10)):
        c.track(t, p)
    c.track("drums", 0, drums=True)
    B = c.bar
    for b in range(nb * 4):                 # the clock: one tick per second, tock on even seconds
        c.hit("wood_hi" if b % 2 == 0 else "wood_lo", b, 36 + int(10 * b / (nb * 4)), 0.2)
    for bar in range(1, nb + 1):
        f = (bar - 1) / max(1, nb - 1)
        c.note("cb", "B1", B(bar), 0.5, 44 + int(16 * f), legato=0.7)           # low pulse, lub
        c.note("cb", "B1", B(bar) + 0.75, 0.5, 34 + int(14 * f), legato=0.7)    # dub
        if bar >= 3:     # pitched tick: B B B C - toward six o'clock, never louder than mp
            for k, p in enumerate(["B5", "B5", "B5", "C6"] * 2):
                c.note("tick", p, B(bar) + k * 0.5, 0.25, 36 + int(18 * f) + (6 if k % 4 == 0 else 0), legato=0.4)
    # tightening, not louder: the cluster gains a note every few bars (B, +C, +F#, +F)
    layers = [("hi", "B5", 1), ("hi", "C6", int(nb * 0.3) + 1), ("mid", "F#4", int(nb * 0.5) + 1),
              ("mid", "F4", int(nb * 0.75) + 1)]
    for trk, p, start in layers:
        c.note(trk, p, B(start), (nb + 1 - start) * 4 - 0.5, 40, legato=1.0)
    c.swell("hi", 0, B(nb + 1), 60, 90)
    c.swell("mid", 0, B(nb + 1), 60, 85)
    # Chichikov's waltz, bent into 4/4 and slightly flat, in fragments on the music box
    for k, bar in enumerate(range(4, nb, 5)):
        c.seq("box", "F#5:q. E5:e D5:q E5:q | D5:h. r:q", B(bar), 44, legato=0.9)
        c.bend("box", B(bar), B(bar) + 0.1, -25, -25)
    c.note("cel", "B6", B(nb + 1) - 1, 1, 40)
    mix = {
        "tick": dict(inst="pizz", lvl=-29, pan=0.35, send=0.3, group="percussion"),
        "cb": dict(inst="cb", lvl=-27, pan=0.1, send=0.3, group="harmony"),
        "hi": dict(inst="vln1", lvl=-30, pan=-0.4, send=0.5, group="harmony"),
        "mid": dict(inst="vla", lvl=-31, pan=0.2, send=0.5, group="harmony"),
        "cel": dict(inst="celesta", lvl=-31, pan=-0.3, send=0.4, group="melody"),
        "box": dict(gm=True, program=10, lvl=-27, pan=-0.2, send=0.4, group="melody"),
        "drums": dict(lvl=-31, pan=0.05, send=0.25, group="percussion"),
    }
    meta = dict(id="M07a" if seconds == 60 else "M07b", title=f"The offer / Both or neither ({seconds} s)",
                scenes=["16", "18-19", "22"], duration=float(seconds), key="B minor / B Phrygian (C) with F# and F",
                tempo="60 BPM 4/4 (one tick per second)",
                hits=[[0.0, "clock starts"], [8.0, "pitched tick enters"]] +
                     [[float(B(s_) ), f"cluster gains a note"] for _, _, s_ in layers[1:]],
                silences=[], motifs=["CHICHIKOV (bent, music box)", "clock (from A3)"], loud=-22.0, rt60=2.4,
                end="fade")
    return c, mix, meta


# ============================================================ 8 THE RIM (scene 21)
def rim():
    c = Cue("E01-M08-the-rim", bpm=60, seed=1012)
    for t, p in (("held", GM["violin"]), ("hn", GM["horn"]), ("vc_solo", GM["cello"]), ("pad", GM["strings"]),
                 ("low", GM["cello"]), ("harp", GM["harp"]), ("pizz", GM["pizz"])):
        c.track(t, p)
    # A 2-32 s (loop 4-30): one held violin F#5, re-bowed every ~8 s; far horn: sad tune bars 1-2
    for s_ in (2.0, 9.5, 17.0, 24.5):
        c.note("held", "F#5", s_, 8.3, 34, legato=1.0)
    c.swell("held", 0, 32, 70, 100)
    c.seq("hn", "F#4:h. E4:q | D4:q E4:q F#4:q B4:q | A4:w", 14.0, 46, legato=1.0)
    # 32-34 deliberate silence
    # B 34-74 (loop 38-70): the cannonball - warmth: D major, low strings + harp + a pizz gallop
    WARM = [("D3", ["F#3", "A3", "D4"]), ("B2", ["F#3", "B3", "D4"]), ("G2", ["G3", "B3", "D4"]),
            ("A2", ["E3", "A3", "C#4"])] * 2 + [("D3", ["F#3", "A3", "D4"]), ("G2", ["G3", "B3", "E4"])]
    for i, (r, up) in enumerate(WARM):
        b = 34 + i * 4
        c.chord("pad", up, b, 4, 40 + min(i, 5) * 3, legato=1.0)
        c.note("low", r, b, 4, 46, legato=1.0)
        c.seq("harp", " ".join(f"{p}:e" for p in (up + [up[1], up[2]])[:4]) + " r:h", b, 40)
        if 3 <= i <= 7:   # the ride: a soft 6/8-like pizz gallop
            for k in range(8):
                c.note("pizz", r if k % 3 == 0 else up[0], b + k * 0.5, 0.3, 38 + (8 if k % 3 == 0 else 0), legato=0.4)
    c.swell("pad", 34, 74, 50, 95)
    c.swell("pad", 70, 74, 95, 0)
    c.seq("hn", "A4:h. G4:q | F#4:q G4:q A4:q D5:q | C#5:h B4:q A4:q | A4:w", 50.0, 50, legato=1.0)
    # 74-77 deliberate silence (the three seconds after "You are the audience")
    # C 77-130 (loop 82-118): the promise and the hatchet - held string returns, sad tune on solo cello
    for s_ in (77.0, 85.0, 93.0, 101.0, 109.0, 117.0):
        c.note("held", "F#5", s_, 8.4, 32, legato=1.0)
    c.seq("vc_solo", SAD, 82.0, 66, transpose=-12, legato=1.0)
    for i, ch in enumerate(SAD_H):
        c.chord("pad", [pitch(p) + 12 for p in ch], 82.0 + i * 4, 4, 34, legato=1.0)
    c.chord("pad", ["D4", "F#4", "A4"], 114.0, 14, 34, legato=1.0)
    c.note("low", "D3", 114.0, 14, 40, legato=1.0)
    c.swell("pad", 114, 130, 90, 10)
    c.swell("held", 114, 130, 100, 20)
    mix = {
        "held": dict(inst="vln_solo", lvl=-28, pan=-0.2, send=0.5, group="harmony"),
        "hn": dict(inst="hn", lvl=-26, pan=0.3, send=0.7, group="melody"),
        "vc_solo": dict(inst="vc_solo", lvl=-23, pan=0.05, send=0.45, group="melody"),
        "pad": dict(inst="vln2", lvl=-30, pan=-0.1, send=0.55, group="harmony"),
        "low": dict(inst="vc", lvl=-30, pan=0.25, send=0.4, group="harmony"),
        "harp": dict(inst="harp", lvl=-30, pan=0.4, send=0.5, group="harmony"),
        "pizz": dict(inst="pizz", lvl=-32, pan=-0.3, send=0.35, group="percussion"),
    }
    meta = dict(id="M08", title="The rim - the heart of the episode", scenes=["21"], duration=130.0,
                key="B minor (sad tune) with a D-major warm middle", tempo="free (60 BPM grid)",
                hits=[[2.0, "held string F#5 begins"], [14.0, "far horn: sad tune fragment"],
                      [34.0, "the cannonball story: warmth enters"], [77.0, "held string returns"],
                      [82.0, "sad tune complete on solo cello"], [114.0, "D major: the hatchet / 'it might do something'"]],
                silences=[[32.0, 34.0], [74.0, 77.0]],
                loops=[[4.0, 30.0, "A: held string bed"], [38.0, 70.0, "B: cannonball warmth"],
                       [82.0, 114.0, "C: sad tune over held string (8 bars of 4 s)"]],
                motifs=["SAD TUNE (horn, cello)"], loud=-23.0, rt60=3.0, end="fade")
    return c, mix, meta


# ============================================================ 9 THE CHASE
def chase():
    c = Cue("E01-M09-chase", bpm=148, seed=1013)
    for t, p in (("ost", GM["cello"]), ("vla", GM["viola"]), ("cb", GM["contrabass"]), ("held", GM["strings"]),
                 ("hn", GM["horn"]), ("tpt", GM["trumpet"]), ("bsn", GM["bassoon"]), ("cl", GM["clarinet"]),
                 ("timp", GM["timpani"]), ("pizz", GM["pizz"])):
        c.track(t, p)
    c.track("drums", 0, drums=True)
    T = lambda s: S(c, s)
    OST = [0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 1, 0, 0, 1, 3, 1]
    ACC = {0, 3, 6, 8, 11, 14}
    CH = [["D3", "A3", "D4", "F3"], ["C3", "G3", "C4", "E3"], ["Bb2", "F3", "Bb3", "D3"], ["A2", "E3", "A3", "C#3"]]

    def ost_until(b0, b1, vel):
        b = b0
        i = 0
        while b < b1 - 0.01:
            tones = CH[(i // 16) % 4]
            k = i % 16
            c.note("ost", tones[OST[k]], b, 0.25, vel + (20 if k in ACC else 0), legato=0.5)
            if k in ACC:
                c.note("cb", pitch(tones[0]) - 12, b, 0.25, vel, legato=0.5)
            b += 0.25
            i += 1

    # 0-20.9: propulsive, dry, witty
    ost_until(0, T(20.9), 62)
    for k in range(int(T(20.9) // 4)):
        c.note("timp", "D2" if k % 2 == 0 else "A1", k * 4, 1, 70)
        c.hit("snare", k * 4 + 3.5, 40)
        c.hit("wood_hi", k * 4 + 1.5, 46, 0.2)
    c.seq("bsn", "D3:e r:e A2:e r:e D3:e E3:e F3:e r:e", T(4.0), 74, legato=0.45)        # "two behind"
    c.seq("cl", "A4:e r:e D5:e r:e E5:e F5:e E5:q", T(8.0), 70, legato=0.5)
    c.seq("tpt", "D5:e r:e D5:e r:e F5:q r:q", T(11.5), 70, legato=0.4)                     # the card: "Pull over"
    c.seq("pizz", "A4:q F4:h", T(18.2), 70, legato=0.5)                                      # "please" - a sigh
    # 21.0-31.5: ONE held note while the rover hangs (10.5 s), everything else stops
    c.note("held", "A5", T(21.0), T(10.5), 56, legato=1.0, human=False)
    c.swell("held", T(21.0), T(31.5), 70, 100)
    # 31.5 landing in silence, then the score resumes: the Baron's march fragment, heroic and absurd
    ost_until(T(32.0), T(56.6), 58)
    c.seq("hn", "D4:q. D4:e F#4:q. F#4:e | A4:h F#4:q D4:q | E4:q. E4:e A4:q. A4:e | D4:h r:h", T(33.0), 74, legato=0.8)
    c.seq("tpt", "r:w | r:w | r:w | r:h A4:q D5:q | F5:h E5:h", T(33.0), 62, legato=0.7)
    for k in range(int((T(56.6) - T(32.0)) // 4)):
        c.note("timp", "D2", T(32.0) + k * 4, 1, 66)
        c.hit("snare", T(32.0) + k * 4 + 2, 36)
    c.seq("bsn", "D3:e r:e A2:e r:e D3:e E3:e F3:e r:e | E3:e r:e r:q C3:e r:e r:q", T(46.0), 70, legato=0.45)  # PIP's "still asking nicely"
    c.chord("pizz", ["D3", "A3", "D4"], T(56.6), 0.5, 90, legato=0.4)
    # 56.7-60.0: silence (the third crawler slides across the road)
    mix = {
        "ost": dict(inst="vc", lvl=-21, pan=0.25, send=0.12, group="harmony"),
        "vla": dict(inst="vla", lvl=-28, pan=0.1, send=0.12, group="harmony"),
        "cb": dict(inst="cb", lvl=-26, pan=0.3, send=0.1, group="harmony"),
        "held": dict(inst="vln1", lvl=-22, pan=-0.2, send=0.25, group="melody"),
        "hn": dict(inst="hn", lvl=-22, pan=-0.2, send=0.2, group="melody"),
        "tpt": dict(inst="tpt", lvl=-25, pan=0.2, send=0.15, group="melody"),
        "bsn": dict(inst="bsn", lvl=-23, pan=-0.3, send=0.1, group="melody"),
        "cl": dict(inst="cl", lvl=-23, pan=0.3, send=0.1, group="melody"),
        "timp": dict(inst="timp", lvl=-24, pan=0, send=0.15, group="percussion"),
        "pizz": dict(inst="pizz", lvl=-24, pan=-0.1, send=0.12, group="harmony"),
        "drums": dict(lvl=-28, pan=0.1, send=0.1, group="percussion"),
    }
    meta = dict(id="M09", title="The chase (no exterior sound: the score carries it)", scenes=["24"], duration=60.0,
                key="D minor", tempo="148 BPM 4/4, 3+3+2 ostinato",
                hits=[[11.5, "the card: 'Pull over' (trumpet)"], [18.2, "'please' (pizz sigh)"],
                      [21.0, "rover leaves the road: ONE held note A5 begins"],
                      [31.5, "held note ends (10.5 s): landing in silence"], [32.0, "score resumes"],
                      [33.0, "Baron's march fragment (horns) under his speech"], [56.6, "last button"]],
                silences=[[56.9, 60.0]], held_note=[21.0, 31.5, "A5, first violins, single note"],
                motifs=["MAIN ostinato", "JAX head (bassoon/clarinet)", "BARON march (horns)"], loud=-17.0,
                rt60=1.0, end="hard")
    return c, mix, meta


# ============================================================ 10 THE DARK FLOOR
def dark_floor():
    c = Cue("E01-M10-dark-floor", bpm=66, seed=1014, rit=(88, 99, 54))
    for t, p in (("cb", GM["contrabass"]), ("timp", GM["timpani"]), ("fl", GM["flute"]), ("cel", GM["celesta"]),
                 ("pad", GM["strings"]), ("harp", GM["harp"]), ("vc", GM["cello"])):
        c.track(t, p)
    T = lambda s: S(c, s)
    # 0-18: near silence, low pulse on F (Mira's Sa): soft heartbeat every ~1.8 s
    b = T(1.0)
    while b < T(84):
        f = min(1.0, b / T(40))
        c.note("cb", "F1", b, 0.6, 34 + int(12 * f), legato=0.8)
        if b < T(20):
            c.note("timp", "F2", b, 0.5, 30)
        b += 2.0
    # 18.5: Mira's voice brings in a single clear line: her motif on flute
    c.seq("fl", "r:h C6:q. ~A5:e | " + MIRA, T(18.5), 74, legato=1.0)
    c.bend("fl", T(18.5) + 3.5, T(18.5) + 3.9, -200, 0)
    # 30-: the laser map blooms: celesta clockwork, harp, then strings warm underneath
    HARM = [["F3", "A3", "C4"], ["F3", "A3", "C4"], ["Eb3", "G3", "Bb3"], ["D3", "F3", "A3"],
            ["D3", "F3", "Bb3"], ["F3", "A3", "C4"]] * 2
    for i, v in enumerate(HARM):
        b0 = T(30.0) + i * 4
        if b0 > T(84):
            break
        pat = [pitch(v[0]) + 24, pitch(v[2]) + 24, pitch(v[1]) + 24, pitch(v[2]) + 24]
        for k in range(16):
            c.note("cel", pat[k % 4], b0 + k * 0.25, 0.25, 34 + min(i, 6) * 2 + (6 if k % 4 == 0 else 0), legato=0.5)
        if i >= 2:
            c.chord("pad", [pitch(p) + 12 for p in v], b0, 4, 34 + min(i, 8) * 3, legato=1.0)
        if i >= 4:
            c.seq("harp", " ".join(f"{p}:e" for p in v + [v[1], v[2], v[0], v[1], v[2]]), b0, 40)
    # 54: Noakes cuts in - the line dips; 56.5 Mira carries on: flute again, higher and surer
    c.seq("fl", "G5:e A5:e C6:q ~A5:h | G5:q. A5:e C6:q D6:q | ~C6:w", T(57.0), 76, legato=1.0)
    c.seq("vc", "F3:h. G3:q | A3:h C4:h | Bb3:h A3:h | F3:w", T(60.0), 56, legato=1.0)
    # 73.5 "Madam, you are a wonder": F major opens, flute holds high C
    c.chord("pad", ["F4", "A4", "C5", "F5"], T(74.0), T(15.0), 54, legato=1.0)
    c.note("fl", "C6", T(76.0), T(10), 60, legato=1.0)
    c.seq("harp", "F3:s C4:s F4:s A4:s C5:s F5:s A5:s C6:q.", T(74.0), 50)
    c.swell("pad", T(80), T(90), 100, 30)
    c.swell("fl", T(80), T(88), 100, 40)
    mix = {
        "cb": dict(inst="cb", lvl=-27, pan=0.1, send=0.4, group="percussion"),
        "timp": dict(inst="timp", lvl=-32, pan=0, send=0.4, group="percussion"),
        "fl": dict(inst="fl", lvl=-20, pan=0.05, send=0.45, group="melody"),
        "cel": dict(inst="celesta", lvl=-29, pan=-0.4, send=0.35, group="harmony"),
        "pad": dict(inst="vln2", lvl=-29, pan=-0.1, send=0.55, group="harmony"),
        "harp": dict(inst="harp", lvl=-29, pan=0.45, send=0.45, group="harmony"),
        "vc": dict(inst="vc_solo", lvl=-25, pan=0.3, send=0.45, group="melody"),
    }
    meta = dict(id="M10", title="The dark floor - Mira's voice brings the map", scenes=["26", "27"], duration=90.0,
                key="F (Mira's Sa), Eb colour, ends F major", tempo="66 BPM 4/4, easing at the end",
                hits=[[1.0, "low pulse on F starts"], [18.5, "Mira's line enters (flute)"],
                      [30.0, "the laser map blooms: celesta clockwork"], [57.0, "Mira again, surer (after Noakes)"],
                      [74.0, "'Madam, you are a wonder': F major opens"]],
                silences=[], motifs=["MIRA (flute, celesta clockwork)"], loud=-21.0, rt60=2.6, end="fade")
    return c, mix, meta


# ============================================================ 11 THE THROW
def throw():
    c = Cue("E01-M11-the-throw", bpm=132, seed=1015)
    for t, p in (("ost", GM["cello"]), ("cb", GM["contrabass"]), ("vln", GM["strings"]), ("hn", GM["horn"]),
                 ("timp", GM["timpani"]), ("glock", GM["glock"]), ("pizz", GM["pizz"]), ("pad", GM["strings2"])):
        c.track(t, p)
    T = lambda s: S(c, s)
    # 0-10.0 build: ostinato + rising violins + horns, crescendo, then a dead stop at exactly 10.0
    b = 0.0
    i = 0
    OST = [0, 0, 1, 0, 0, 1, 0, 2]
    tones = [["D3", "A3", "D4"], ["Bb2", "F3", "Bb3"], ["C3", "G3", "C4"], ["A2", "E3", "A3"]]
    while b < T(10.0) - 0.26:
        tt = tones[int(b // 4) % 4]
        c.note("ost", tt[OST[i % 8]], b, 0.25, 60 + int(30 * b / T(10)), legato=0.5)
        b += 0.25
        i += 1
    for k in range(int(T(10.0) // 4) + 1):
        if k * 4 < T(10.0):
            c.note("cb", ["D2", "Bb1", "C2", "A1"][k % 4], k * 4, min(4, T(10.0) - k * 4), 70, legato=1.0)
            c.note("timp", "D2" if k % 2 == 0 else "A1", k * 4, 1, 70 + k * 8)
    c.seq("vln", "D5:h E5:h | F5:h G5:h | A5:h Bb5:h | C6:h C#6:q.", 0, 70, legato=1.0, curve=lambda f: int(30 * f))
    c.seq("hn", "D4:w | Bb3:w | C4:w | A3:h. A3:e", 0, 70, legato=1.0, curve=lambda f: int(30 * f))
    for i_ in range(12):
        c.note("timp", "A1", T(8.2) + i_ * 0.25, 0.25, 70 + i_ * 4)
    # 10.0-22.0: twelve seconds of total silence (enforced digitally by the renderer)
    # 22.0-30.0 release: a warm D major breath, and the glint going on over the rim
    c.chord("pad", ["D4", "F#4", "A4", "D5"], T(22.0), T(7.0), 56, legato=1.0)
    c.swell("pad", T(22.0), T(24.0), 20, 100)
    c.swell("pad", T(27.0), T(30.0), 100, 20)
    c.chord("hn", ["D3", "A3", "F#4"], T(22.3), T(5.0), 54, legato=1.0)
    c.note("cb", "D2", T(22.0), T(6.5), 48, legato=1.0)
    c.seq("glock", "D6:s F#6:s A6:s D7:s F#7:e", T(23.2), 50)
    c.chord("pizz", ["D3", "A3", "F#4"], T(26.4), 0.5, 70, legato=0.4)      # "Darts."
    mix = {
        "ost": dict(inst="vc", lvl=-21, pan=0.25, send=0.2, group="harmony"),
        "cb": dict(inst="cb", lvl=-26, pan=0.3, send=0.2, group="harmony"),
        "vln": dict(inst="vln1", lvl=-21, pan=-0.4, send=0.3, group="melody"),
        "hn": dict(inst="hn", lvl=-22, pan=-0.1, send=0.35, group="melody"),
        "timp": dict(inst="timp", lvl=-23, pan=0, send=0.25, group="percussion"),
        "glock": dict(inst="glock", lvl=-28, pan=0.4, send=0.4, group="melody"),
        "pizz": dict(inst="pizz", lvl=-25, pan=-0.2, send=0.3, group="harmony"),
        "pad": dict(inst="vln2", lvl=-24, pan=0, send=0.5, group="harmony"),
    }
    meta = dict(id="M11", title="The throw (12 s of silence in the middle)", scenes=["29"], duration=30.0,
                key="D minor build -> D major release", tempo="132 BPM 4/4",
                hits=[[10.0, "dead stop: silence begins (hatchet leaves Jax's hand)"],
                      [22.0, "release: warm D major"], [23.2, "the glint over the rim (glock)"],
                      [26.4, "'Darts.' (pizz button)"]],
                silences=[[10.0, 22.0]], motifs=["MAIN ostinato"], loud=-18.0, rt60=2.0, end="fade",
                stop_cut=10.0)
    return c, mix, meta


# ============================================================ 12a FAR SIDE / AFTERWARDS
def far_side():
    c = Cue("E01-M12a-far-side-afterwards", bpm=56, seed=1016, rit=(84, 93.3, 46))
    for t, p in (("cb", GM["contrabass"]), ("cl", GM["clarinet"]), ("harp", GM["harp"]), ("pad", GM["strings"]),
                 ("vc", GM["cello"]), ("fl", GM["flute"]), ("picc", GM["piccolo"]), ("glock", GM["glock"]),
                 ("pizz", GM["pizz"]), ("vln", GM["strings2"])):
        c.track(t, p)
    T = lambda s: S(c, s)
    # 0-13.4: one low D under Temi, cut off as Earth sets; 13.4-17.0 the long silence
    c.note("cb", "D2", T(0.5), T(12.5), 40, legato=1.0)
    c.swell("cb", T(0.5), T(13.4), 90, 40)
    # 17-45: the main theme, small and tired: solo clarinet at half speed, harp, soft strings
    c.seq("cl", "D5:h A4:h | D5:q E5:q F5:h | E5:w | r:h C5:h", T(17.5), 64, legato=1.0)
    for i, ch in enumerate([["D3", "A3", "F4"], ["D3", "A3", "F4"], ["C3", "G3", "E4"], ["C3", "G3", "E4"],
                            ["Bb2", "F3", "D4"], ["A2", "E3", "C#4"]]):
        b0 = T(17.5) + i * 4
        c.chord("pad", ch, b0, 4, 40, legato=1.0)
        c.seq("harp", " ".join(f"{p}:e" for p in ch + ch[1:] + ch[:1]) + " r:h", b0, 40)
    # 45-52: Mira, "a coordinate": her motif's first bar on flute
    c.seq("fl", "G5:e A5:e C6:q ~A5:h", T(46.5), 56, legato=1.0)
    # 53.0: the coffee machine light comes on (glock ding) + PIP's tiny march, two bars, in D
    c.note("glock", "A6", T(53.0), 1, 64)
    c.seq("picc", "D6:e F#6:e A6:e F#6:e | D6:q A5:q", T(54.2), 50, legato=0.5)
    c.seq("pizz", "D3:q A3:q D3:q A3:q", T(54.2), 46, legato=0.4)
    # 61.4-62.8: the beat of silence after "It prefers her"
    # 62.8-83: PIP's report: pizz walk + clarinet Jax fragment, soft
    walk = ["D3", "F3", "A3", "C4", "B3", "A3", "G3", "F3"]
    for k in range(int(T(83.0) - T(62.8))):
        c.note("pizz", walk[k % 8], T(62.8) + k, 1, 44, legato=0.5)
    c.seq("cl", "r:w | " + JAX.split("|")[0], T(62.8), 54, legato=0.9)
    # 84-100: Jax's V.O. - the theme on strings, warm and small; ends on a quiet D major
    c.seq("vln", "D5:q A4:q D5:e E5:e F#5:q | E5:h. C#5:q | D5:w", T(84.0), 58, legato=1.0)
    c.chord("pad", ["D3", "A3", "F#4"], T(84.0), 4, 44, legato=1.0)
    c.chord("pad", ["A2", "E3", "C#4"], T(84.0) + 4, 4, 44, legato=1.0)
    c.chord("pad", ["D3", "A3", "F#4", "D5"], T(84.0) + 8, 6, 44, legato=1.0)
    c.note("vc", "D3", T(84.0), 14, 46, legato=1.0)
    c.swell("pad", T(92), T(100), 100, 30)
    mix = {
        "cb": dict(inst="cb", lvl=-29, pan=0.2, send=0.4, group="harmony"),
        "cl": dict(inst="cl", lvl=-21, pan=-0.1, send=0.4, group="melody"),
        "harp": dict(inst="harp", lvl=-28, pan=0.4, send=0.45, group="harmony"),
        "pad": dict(inst="vln2", lvl=-29, pan=-0.2, send=0.5, group="harmony"),
        "vc": dict(inst="vc", lvl=-28, pan=0.3, send=0.4, group="harmony"),
        "fl": dict(inst="fl", lvl=-24, pan=0.1, send=0.45, group="melody"),
        "picc": dict(inst="picc", lvl=-27, pan=0.25, send=0.3, group="melody"),
        "glock": dict(inst="glock", lvl=-27, pan=0.35, send=0.35, group="percussion"),
        "pizz": dict(inst="pizz", lvl=-28, pan=-0.3, send=0.3, group="harmony"),
        "vln": dict(inst="vln1", lvl=-23, pan=-0.35, send=0.5, group="melody"),
    }
    meta = dict(id="M12a", title="Far side / afterwards (bridge)", scenes=["30"], duration=100.0,
                key="D minor -> D major", tempo="56 BPM 4/4 (half-time theme), easing at the end",
                hits=[[13.4, "Temi cut off: music stops"], [17.5, "main theme, small (clarinet)"],
                      [46.5, "Mira's motif fragment"], [53.0, "coffee light comes on (glock)"],
                      [54.2, "PIP's march fragment"], [84.0, "Jax V.O.: theme on strings"]],
                silences=[[13.4, 17.0], [61.4, 62.8]], motifs=["MAIN", "MIRA", "PIP", "JAX"], loud=-21.0,
                rt60=2.6, end="fade")
    return c, mix, meta


# ============================================================ 12b TAG
def tag():
    c = Cue("E01-M12b-tag", bpm=126, beats_per_bar=3, seed=1017)
    _chich_tracks(c)
    for t, p in (("cl2", GM["clarinet"]), ("gtr", GM["nylon"]), ("walk", GM["pizz"]), ("pad", GM["strings"])):
        c.track(t, p)
    T = lambda s: S(c, s)
    # 0-8.6: Chichikov's motif, first phrase, music box + waltz (he speaks into the recorder)
    lens = [3, 3, 3, 3, 3, 2]
    starts, tot = bars_to_beats(lens)
    c.seq("box", "F#5:q. E5:e D5:q | E5:q D5:q B4:q | C#5:q D5:q E5:q | D5:h. | B4:h. | r:h", T(0.6), 62, legato=0.9)
    c.bend("box", T(0.6) + starts[3] + 0.3, T(0.6) + starts[3] + 1.4, 0, -30)
    for i, L in enumerate(lens[:5]):
        root, up = CHICH_H[[0, 1, 2, 0, 0][i]]
        _waltz_bar(c, T(0.6) + starts[i], root, up, beats=L, vel=52)
    # 9.0-15.0: silence - padlock clicks (~9.5), stove lights (~11), three knocks (~12.5-14.5): all SFX
    # 15.0-42.6: PIP reads the warrant - Jax's motif, light (clarinet, nylon guitar, pizz walk)
    c2 = 126 / 3   # bars per minute (3/4)
    jx = T(15.0)
    walk = ["D2", "F2", "A2", "C3", "B2", "G2", "F2", "E2"]
    k = 0
    while jx + k < T(42.4):
        c.note("walk", walk[k % 8], jx + k * 1.0, 1, 50, legato=0.5)
        if k % 3 == 1:
            c.chord("gtr", ["F3", "A3", "C4", "E4"], jx + k * 1.0, 1, 40, roll=0.012)
        k += 1
    c.seq("cl2", "D5:q A4:u D5:t E5:u F5:t ~E5:h r:h", T(19.0), 56, legato=0.95)
    c.seq("cl2", "D5:q A4:u D5:t E5:u F5:t G5:u A5:t Bb5:h r:h", T(31.0), 58, legato=0.95)
    # 42.6: the field refreshes to "nobody": unresolved Bbmaj7(#11), E on top; hard cut at 45.0
    c.chord("pad", ["Bb2", "A3", "D4", "E4"], T(42.6), T(2.6), 54, legato=1.0)
    c.note("cl2", "E5", T(42.6), T(2.6), 56, legato=1.0)
    c.chord("gtr", ["Bb2", "F3", "A3", "D4", "E4"], T(42.6), T(2.4), 50, roll=0.02)
    mix = dict(CH_MIX)
    mix.update({
        "cl2": dict(inst="cl", lvl=-22, pan=-0.1, send=0.3, group="melody"),
        "gtr": dict(gm=True, sf2="fluidr3", lvl=-28, pan=0.35, send=0.25, group="harmony"),
        "walk": dict(inst="pizz", lvl=-27, pan=0.15, send=0.2, group="harmony"),
        "pad": dict(inst="vln2", lvl=-26, pan=-0.2, send=0.4, group="harmony"),
    })
    meta = dict(id="M12b", title="Tag - Chichikov, the knocks, nobody", scenes=["31"], duration=45.0,
                key="B minor (Chichikov) -> D Dorian (Jax) -> Bbmaj7(#11) unresolved",
                tempo="126 BPM 3/4 then Jax's swing over the same pulse",
                hits=[[0.6, "Chichikov's motif"], [9.0, "silence: padlock (~9.5) and stove (~11) are SFX"],
                      [12.5, "three knocks (SFX), still silent"], [15.0, "Jax's motif under PIP's reading"],
                      [42.6, "'nobody': unresolved chord"], [45.0, "hard cut to black"]],
                silences=[[8.8, 15.0]], motifs=["CHICHIKOV", "JAX"], loud=-20.0, rt60=1.8, end="hard")
    return c, mix, meta


# ============================================================ 13 END NOTE bed
def end_note():
    c = Cue("E01-M13-what-was-real-bed", bpm=88, seed=1018)
    for t, p in (("harp", GM["harp"]), ("cel", GM["celesta"]), ("pizz", GM["pizz"]), ("pad", GM["strings"]),
                 ("fl", GM["flute"])):
        c.track(t, p)
    B = c.bar
    # light, under speech: E minor / G major pulse, the main-theme head in E on flute (soft)
    prog = [["E3", "B3", "G4"], ["C3", "G3", "E4"], ["G2", "D3", "B3"], ["D3", "A3", "F#4"]] * 4
    for i, ch in enumerate(prog[:14]):
        b0 = B(1 + i)
        c.seq("harp", " ".join(f"{p}:e" for p in ch + ch[1:] + [ch[0], ch[2], ch[1]]), b0, 40)
        c.chord("pad", ch, b0, 4, 34, legato=1.0)
        c.note("pizz", ch[0], b0, 1, 44, legato=0.5)
        c.note("pizz", ch[1], b0 + 2, 1, 38, legato=0.5)
    c.seq("fl", "E5:q B4:q E5:e F#5:e G5:q | F#5:h. D5:q", B(5), 48, legato=1.0)
    c.seq("cel", "E6:q B5:q E6:e F#6:e G6:q | A6:h. r:q", B(11), 40, legato=0.8)
    # bar 15 (38.2 s): hands over to the 5-s end sting (E minor) - a held B as the dominant link
    c.chord("pad", ["B2", "F#3", "D#4"], B(15), 2.5, 34, legato=1.0)
    mix = {
        "harp": dict(inst="harp", lvl=-25, pan=0.35, send=0.4, group="harmony"),
        "cel": dict(inst="celesta", lvl=-29, pan=-0.35, send=0.4, group="melody"),
        "pizz": dict(inst="pizz", lvl=-29, pan=-0.15, send=0.3, group="percussion"),
        "pad": dict(inst="vln2", lvl=-31, pan=0, send=0.5, group="harmony"),
        "fl": dict(inst="fl", lvl=-26, pan=0.1, send=0.45, group="melody"),
    }
    meta = dict(id="M13", title="'What was real' bed (into the 5-s end sting)", scenes=["WWR"], duration=40.0,
                key="E minor / G major, ends on B (dominant) into the E-minor end sting",
                tempo="88 BPM 4/4", hits=[[10.9, "theme head on flute (soft)"], [38.2, "dominant link into the end sting"]],
                silences=[], motifs=["MAIN head (in E)"], loud=-22.0, rt60=2.2, end="fade",
                append_sting="A1-endcard-sting-5s")
    return c, mix, meta


CUES = [cold_open, approach, chichikov_statement, chichikov_underscore, baron_grand, baron_threadbare,
        baron_sad_tune, inventory, post_horn, lambda: offer(60), lambda: offer(90), rim, chase, dark_floor,
        throw, far_side, tag, end_note]
