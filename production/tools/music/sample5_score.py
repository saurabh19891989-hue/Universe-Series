"""E01 SAMPLE 5 (2:42) - the score, written against episodes/E01/sample5-shotlist.json (frozen timeline).

All cues use Cue(bpm=60), so ONE BEAT = ONE SECOND of picture time: every note is placed at its absolute
picture time (minus the cue's own start). Musical tempo inside a passage comes from at(c, key, melody,
t0, spb): the melody string's beats are scaled by `spb` seconds per beat.

Cues (rendered by sample5_mix.py with v3mix, placed at `start`):
  A   0.0 - 77.0   customs desk: Jax/Mira motifs trading; air before punchlines; held note on the
                   almost-smile; dead stop + stamp at 48.048; deflated tag; Noakes' dry bassoon; the board's
                   mock-hymn; the Baron's far-off fanfare (foreshadows the march); closed-eyes sting; card turn
  B1  77.0 - 109.5 the rim: stillness (pad + harp only) until "Tell me one"; then the duduk's first cell;
                   the Ochakov build into the cannon
  CUT 109.47-129.9 the cannonball march (hits: jump 110.73, astride 112.25, doubts 115.9 stall, the other
                   ball 121.7-123.1, changed 125.2 slide, swap 125.7 recovery, held note out at 128.21,
                   'rode it home' quote at 130.07)
  B2  129.4-162.441 laugh support swell; thinning from "Did it happen?"; TRUE SILENCE 144.945-147.945;
                   the heart phrase once for the promise landing on B (unresolved) at 156.3, held to the end
All melodies are ours (HOOK/JAX/MIRA from s1_themes, HEART from s2_pieces, the march from s2_pieces).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, pitch, parse  # noqa: E402
import worldsynth as W  # noqa: E402
from s2_pieces import HEART, SYN  # noqa: E402

END = 162.441


def at(c, key, s, t0, spb, vel=80, transpose=0, legato=0.92, off=0.0):
    """Lay a melody string at absolute time t0 (seconds) with `spb` seconds per notated beat."""
    t = t0
    for p, d, slur in parse(s):
        if p is not None:
            c.note(key, p + transpose, t - off, d * spb, vel, legato=1.05 if slur else legato)
        t += d * spb
    return t


def tr(c, names, drums=()):
    for n in names:
        c.track(n, 0)
    for n in drums:
        c.track(n, 0, drums=True)


# ============================================================ PART A (0 - 77 s)
def cue_A():
    c = Cue("S5-A-customs", bpm=60, seed=5101)
    tr(c, ["cl", "bansuri", "guitar", "bass", "santoor", "tabla", "vibes", "bsn", "tuba", "vc", "cb", "vla",
           "hn", "tbn", "picc", "cel", "harp", "vln1"], drums=["perc", "snare"])
    sw = 60 / 116          # Jax's swing tempo (s per beat)
    # 0-2.6 establish: Mira's clock, very soft, stops for "Next." (air)
    for k, p in enumerate(("F5", "G5", "A5", "C6", "A5")):
        c.note("santoor", p, 0.3 + k * 0.45, 0.45, 38, legato=1.0)
    # 7.24-9.44 the walk pass: Jax's head on clarinet over guitar swing, pizz on the steps
    steps = [7.45 + k * 0.5 for k in range(17)]          # 7.45 ... 15.45 (walk pass + tracking)
    for i, t in enumerate(steps[:5]):
        c.note("bass", ["D2", "A2", "D3", "C3", "A2"][i], t, 0.45, 70, legato=0.5)
    at(c, "cl", "D5:q A4:u D5:t E5:u F5:t ~E5:q", 7.3, sw, 78)
    for k in range(4):
        c.chord("guitar", ["D3", "A3", "C4", "F4"], 7.3 + k * sw * 1, 0.4, 56 if k % 2 == 0 else 46, roll=0.012)
    # 9.54-15.86 Mira reads (her line leads): only a soft pizz on Jax's steps + a guitar every other bar
    for i, t in enumerate(steps[5:]):
        c.note("bass", ["D2", "A2"][i % 2], t, 0.4, 50, legato=0.4)
    c.note("vibes", "A5", 15.86, 1.2, 52)                  # the smile switched on
    # 16.76-24.44 the aunt: fragments only in the gaps
    at(c, "bansuri", "C6:e A5:e", 18.42, 0.25, 58)          # (tiny, before her flat line)
    c.note("bsn", "D2", 20.05, 0.5, 70, legato=0.5)         # the blink: plop
    c.note("santoor", "F5", 21.55, 0.25, 46); c.note("santoor", "F5", 21.8, 0.25, 40)   # unmoved: tick tick
    # 24.65-32.85 Jax's pitch: his motif low under him (clarinet low, guitar), sparkle on 'Section twelve'
    for k in range(int((32.6 - 24.7) / (2 * sw))):
        t0 = 24.7 + k * 2 * sw
        c.chord("guitar", ["D3", "A3", "C4", "F4"] if k % 2 == 0 else ["G2", "D3", "F3", "B3"], t0, 0.4, 48, roll=0.015)
        c.note("bass", "D2" if k % 2 == 0 else "G1", t0, 0.5, 58, legato=0.5)
    at(c, "cl", "D4:q A3:u D4:t E4:u F4:t ~E4:h", 26.2, sw, 62)
    c.seq("glock", "", 0) if False else None
    c.note("vibes", "D6", 29.4, 0.5, 54); c.note("vibes", "A6", 29.65, 0.8, 50)
    # 33.15 'There are nine sections.' - dead stop at 33.0. 34.82-35.67: air. 35.67 his retort: nothing.
    # 37.35-38.45 the almost-smile: ONE held note (Mira's), soft, cut as she pulls the keyboard
    c.note("bansuri", "A5", 37.35, 1.1, 50, legato=1.0)
    c.bend("bansuri", 37.35, 37.6, -100, 0)
    # 38.45-46.85 the empty record: a low mystery hold (her interest), then her quiet line
    c.chord("vla", ["D3", "Eb3"], 38.45, 4.0, 34, legato=1.0)
    c.note("cb", "D2", 38.45, 8.4, 34, legato=1.0)
    for k, p in enumerate(("C6", "A5", "F5", "D5")):         # the screen scrolls into nothing
        c.note("cel", p, 38.5 + k * 0.35, 0.35, 34)
    c.chord("vla", ["D3", "F3", "A3"], 42.45, 4.4, 34, legato=1.0)
    # 46.85-48.0 THE LOOK: both motifs at once, tiny, warm; dead stop at 48.0 for the stamp
    at(c, "bansuri", "G5:e A5:e C6:q", 46.9, 0.45, 58)
    at(c, "cl", "D4:e A3:e D4:e E4:e", 47.0, 0.24, 50)
    c.swell("bansuri", 46.9, 48.0, 80, 110)
    # 49.93-51.5 Jax goes: the deflated tag (his head, descending, then a bassoon plop)
    at(c, "cl", "A4:e F4:e D4:q", 50.0, 0.4, 62)
    c.note("bsn", "A1", 51.1, 0.5, 66, legato=0.5)
    # 51.53-54.5 the notebook: Mira's clock on santoor, very soft (her obsession)
    for k, p in enumerate(("F5", "G5", "A5", "C6", "A5", "G5")):
        c.note("santoor", p, 51.7 + k * 0.45, 0.45, 36, legato=1.0)
    # 54.5-65.7 Noakes: dry - a tired bassoon line and a tuba floor, woodblock like a civil-service clock
    at(c, "bsn", "C3:h B2:h | A2:h. r:q", 54.6, 0.6, 52)
    c.note("tuba", "F1", 54.6, 3.6, 40, legato=1.0)
    for k in range(10):
        c.note("perc", 76, 55.0 + k * 1.0, 0.2, 34)
    c.note("bsn", "E3", 61.65, 0.35, 56, legato=0.8); c.note("bsn", "C3", 62.0, 0.5, 50, legato=0.8)   # the sigh
    at(c, "bsn", "A2:h G2:h | F2:w", 62.5, 0.75, 46)
    # 65.71 the board (with love): a mock-hymn chord on horns + trombone, held soft under his prayer
    c.chord("hn", ["F3", "A3", "C4"], 65.71, 5.0, 50, legato=1.0)
    c.chord("tbn", ["F2", "C3"], 65.71, 5.0, 46, legato=1.0)
    c.swell("hn", 65.71, 70.6, 90, 60)
    # 71.07 the Baron, far off: a tiny fife-and-snare flourish of HIS march (foreshadowing), distant
    at(c, "picc", "D5:e A4:e D5:e F#5:e A5:q", 71.25, 0.22, 60)
    for k in range(6):
        c.note("snare", 60, 71.2 + k * 0.11, 0.1, 30 + k * 3)
    # 73.0 Noakes closes his eyes: the sting - a low, resigned minor chord and one celesta 'ting'
    c.chord("vc", ["D2", "A2", "F3"], 73.0, 1.8, 54, legato=1.0)
    c.chord("bsn", ["D2", "F2"], 73.0, 1.8, 48, legato=1.0)
    c.note("cel", "F6", 73.05, 1.5, 44)
    # 75.0-77.0 the card: comedy -> stillness: a slow harp descent, then one high violin E that becomes
    # the rim's stillness
    for k, p in enumerate(("A5", "F5", "D5", "A4", "E4")):
        c.note("harp", p, 75.0 + k * 0.28, 0.8, 46 - k * 2, legato=1.4)
    c.note("vln1", "E6", 75.9, 2.6, 34, legato=1.0)
    c.swell("vln1", 75.9, 77.5, 60, 30)
    mix = {
        "cl": dict(inst="cl", lvl=-22, pan=-0.3, width=0.4, depth="mid", send=0.3, group="melody"),
        "bansuri": SYN("bansuri", lvl=-23, pan=0.3, width=0.4, depth="mid", send=0.35, group="melody"),
        "guitar": dict(inst="guitar", lvl=-26, pan=-0.4, width=0.5, depth="mid", send=0.2, group="rhythm"),
        "bass": dict(inst="pizz", lvl=-25, pan=-0.05, width=0.4, depth="mid", send=0.2, group="bass"),
        "santoor": SYN("santoor", lvl=-29, pan=0.45, width=0.6, depth="mid", send=0.35, group="rhythm"),
        "tabla": SYN("tabla", tonic="D4", lvl=-28, pan=0.35, width=0.5, depth="front", send=0.2, group="rhythm"),
        "vibes": dict(inst="vibes", lvl=-28, pan=0.0, width=0.6, depth="mid", send=0.45, group="melody"),
        "bsn": dict(inst="bsn", lvl=-24, pan=0.2, width=0.4, depth="mid", send=0.3, group="melody"),
        "tuba": dict(inst="tuba", lvl=-28, pan=0.1, width=0.4, depth="back", send=0.3, group="bass"),
        "vc": dict(inst="vc", lvl=-26, pan=0.3, width=0.7, depth="mid", send=0.4, group="harmony"),
        "cb": dict(inst="cb", lvl=-30, pan=0.4, width=0.5, depth="back", send=0.4, group="bass"),
        "vla": dict(inst="vla", lvl=-30, pan=0.1, width=0.8, depth="mid", send=0.45, group="harmony"),
        "hn": dict(inst="hn", lvl=-27, pan=-0.2, width=0.6, depth="back", send=0.5, group="harmony"),
        "tbn": dict(inst="tbn", lvl=-29, pan=0.2, width=0.5, depth="back", send=0.5, group="harmony"),
        "picc": dict(inst="picc", lvl=-30, pan=-0.55, width=0.3, depth="back", send=0.7, group="melody"),
        "cel": dict(inst="celesta", lvl=-29, pan=0.3, width=0.5, depth="mid", send=0.45, group="melody"),
        "harp": dict(inst="harp3", lvl=-27, pan=0.35, width=0.6, depth="mid", send=0.5, group="harmony"),
        "vln1": dict(inst="vln1", lvl=-31, pan=-0.2, width=0.8, depth="back", send=0.6, group="harmony"),
        "perc": dict(lvl=-33, pan=-0.3, width=0.4, depth="mid", send=0.3, group="rhythm", kit={76: "wood"}),
        "snare": dict(inst="snare3", lvl=-33, pan=-0.55, width=0.3, depth="back", send=0.7, group="rhythm"),
    }
    # the almost-smile held note and the look need the tabla? no - Part A keeps tabla out (Mira's colour is the
    # santoor and bansuri here); the empty track renders silent.
    return c, mix, dict(start=0.0, dur=77.6, hall="Scala Milan Opera Hall", target=-18.0, fade_s=0.6)


# ============================================================ PART B1 (77 - 109.47)
def cue_B1():
    c = Cue("S5-B1-rim", bpm=60, seed=5102)
    off = 77.0
    tr(c, ["vla", "vln1", "cb", "harp", "duduk", "vc", "timp", "hn"], drums=["snare"])
    # 77-98.9 stillness, no melody, no feeling yet: a very soft open fifth (E-B) high and low, harp
    # harmonics one at a time
    c.chord("vla", ["E4", "B4"], 77.4 - off, 22.0, 30, legato=1.0)
    c.note("cb", "E2", 78.0 - off, 21.0, 28, legato=1.0)
    for t, p in ((79.0, "B5"), (84.0, "E6"), (90.0, "B5"), (95.5, "F#6")):
        c.note("harp", p, t - off, 2.0, 34, legato=1.4)
    # 99.53 after "Tell me one." - the Baron opens up: the duduk's first cell (rising fifth), held
    at(c, "duduk", "B3:q E4:q B4:h.", 99.6, 0.9, 62, off=off)
    c.bend("duduk", 99.6 + 1.8 - off, 99.6 + 2.15 - off, -200, 0)
    c.chord("vla", ["E3", "G3", "B3"], 99.6 - off, 7.0, 34, legato=1.0)
    # 100.2-109.4 Ochakov: a distant military hint builds: snare taps, timpani, horns rising, to the cannon
    for k in range(int((109.3 - 103.0) / 0.268)):
        c.note("snare", 60, 103.0 + k * 0.268 - off, 0.1, 22 + int(k * 1.3))
    c.note("cb", "B1", 103.0 - off, 6.4, 34, legato=1.0)
    c.swell("cb", 103.0 - off, 109.4 - off, 60, 110)
    for k, t in enumerate((106.9, 107.7, 108.3, 108.8, 109.1)):
        c.note("timp", "B1" if k < 3 else "D2", t - off, 0.3, 50 + k * 8)
    c.chord("hn", ["B2", "F#3"], 107.2 - off, 2.2, 44, legato=1.0)
    c.swell("hn", 107.2 - off, 109.4 - off, 50, 115)
    mix = {"vla": dict(inst="vla", lvl=-33, pan=0.1, width=1.0, depth="back", send=0.6, group="harmony"),
           "vln1": dict(inst="vln1", lvl=-33, pan=-0.3, width=0.9, depth="back", send=0.6, group="harmony"),
           "cb": dict(inst="cb", lvl=-32, pan=0.3, width=0.6, depth="back", send=0.5, group="bass"),
           "harp": dict(inst="harp3", lvl=-30, pan=0.4, width=0.6, depth="mid", send=0.6, group="harmony"),
           "duduk": SYN("duduk", lvl=-24, pan=-0.05, width=0.4, depth="front", send=0.5, group="melody"),
           "vc": dict(inst="vc", lvl=-30, pan=0.3, width=0.7, depth="mid", send=0.5, group="harmony"),
           "timp": dict(inst="timp", lvl=-27, pan=0.0, width=0.6, depth="back", send=0.5, group="percussion"),
           "hn": dict(inst="hn", lvl=-28, pan=-0.3, width=0.6, depth="back", send=0.55, group="harmony"),
           "snare": dict(inst="snare3", lvl=-34, pan=0.2, width=0.4, depth="back", send=0.5, group="percussion")}
    return c, mix, dict(start=off, dur=109.47 - off + 0.05, hall="Musikvereinsaal", target=-22.0, fade_s=0.0)


# ============================================================ CUTAWAY (109.47 - 132.2)
MARCH = ("D5:q. A4:e D5:e F#5:e A5:q | B5:q A5:e F#5:e D5:q A4:q | "
         "G5:q. F#5:e E5:e D5:e C#5:q | D5:e E5:e F#5:e G5:e A5:h")


def cue_CUT():
    c = Cue("S5-CUT-cannonball", bpm=60, seed=5103)
    off = 109.47
    tr(c, ["picc", "tpt", "hn", "tbn", "bsn", "pizz", "timp", "vln1", "vla", "vc", "cb", "shehnai"],
       drums=["kit", "frame"])
    q = 60 / 112
    T = lambda s_: s_ - off  # noqa: E731
    # 109.47 the cannon fires: tutti low hit + bass drum + cymbal
    for t_, ps, v in (("timp", ["D2"], 115), ("cb", ["D1", "D2"], 104), ("tbn", ["D2", "A2"], 100), ("vc", ["D2"], 100)):
        c.chord(t_, ps, 0.0, 0.8, v, legato=0.8)
    c.note("kit", 36, 0.0, 0.5, 120); c.note("kit", 49, 0.0, 2, 100)
    # 109.6-110.73 he runs and JUMPS: a string scale up landing on 110.73
    for k, p in enumerate(("D4", "E4", "F#4", "G4", "A4", "B4", "C#5", "D5", "E5", "F#5")):
        c.note("vln1", p, T(109.62) + k * (1.08 / 10), 0.1, 70 + k * 3, legato=0.9)
    c.note("vln1", "A5", T(110.73), 1.0, 100, legato=0.9)
    c.note("kit", 38, T(110.73), 0.3, 96); c.chord("hn", ["D4", "A4"], T(110.73), 0.6, 92, legato=0.8)
    # 111.4-112.25 a snare roll into 'astride'
    for k in range(7):
        c.note("kit", 38, T(111.45) + k * 0.11, 0.1, 50 + k * 5)
    # 112.25-115.9 the march, astride (the tune on piccolo + trumpet; gallop in the low strings)
    t_end = at(c, "picc", MARCH.split(" | ")[0] + " | " + MARCH.split(" | ")[1], 112.25, q, 84, off=off)
    at(c, "tpt", MARCH.split(" | ")[0] + " | " + MARCH.split(" | ")[1], 112.25, q, 80, transpose=-12, off=off)
    b = 112.25
    while b < 115.8:
        c.note("vc", "D3", T(b), q * 0.5, 72, legato=0.6); c.note("vc", "D3", T(b + q * 0.75), q * 0.25, 60, legato=0.6)
        c.note("cb", "D2", T(b), q * 0.5, 74, legato=0.6)
        c.note("kit", 38, T(b), 0.1, 58); c.note("kit", 38, T(b + q * 0.5), 0.1, 44)
        b += q
    c.chord("hn", ["D4", "F#4", "A4"], T(112.25 + q), q * 0.5, 70, legato=0.6)
    c.chord("hn", ["D4", "G4", "B4"], T(112.25 + 5 * q), q * 0.5, 70, legato=0.6)
    # 115.9 DOUBTS: the march stalls on a high A; the snare stops; then a hesitant minor pizz + bassoon
    c.note("picc", "A5", T(115.9), 1.2, 84, legato=1.0); c.note("tpt", "A4", T(115.9), 1.2, 76, legato=1.0)
    c.bend("picc", T(116.4), T(117.1), 0, -100)
    for k in range(9):
        c.note("pizz", ["D3", "F3", "A3", "F3"][k % 4], T(117.2) + k * 0.42, 0.3, 50, legato=0.5)
    at(c, "bsn", "A2:q Bb2:q A2:q G2:q | F2:h E2:h", 117.3, 0.46, 58, off=off)
    c.chord("vla", ["D3", "F3"], T(117.2), 3.7, 34, legato=1.0)
    # 121.08-123.1 the other ball passes, going the other way: the 'other side' on shehnai and frame drum,
    # a descending figure panned across the stage
    at(c, "shehnai", "A5:s G#5:s F5:s E5:s D5:s C#5:s Bb4:s A4:s", 121.7, 0.36, 76, off=off)
    for k in range(6):
        c.note("frame", 41 if k % 3 == 0 else 43, T(121.7) + k * 0.24, 0.2, 70)
    c.bend("picc", T(123.0), T(123.05), -100, 0)
    # 124.88 'changed' -> 125.2 the stumble: trombone slides down, stick clicks, a beat of nothing
    c.note("tbn", "A2", T(124.9), 0.85, 86, legato=1.0)
    c.bend("tbn", T(125.0), T(125.55), 0, -200)
    c.note("kit", 37, T(125.25), 0.1, 70); c.note("kit", 37, T(125.42), 0.1, 50)
    c.bend("tbn", T(125.6), T(125.65), -200, 0)
    # 125.7 the swap lands: recovery UP a semitone (Eb), tutti and prouder, the tune to 128.0
    full = MARCH.split(" | ")[0] + " | " + MARCH.split(" | ")[3]
    at(c, "picc", full, 125.7, q * 0.62, 96, transpose=1, off=off)
    at(c, "tpt", full, 125.7, q * 0.62, 92, transpose=-11, off=off)
    at(c, "hn", full, 125.7, q * 0.62, 84, transpose=-11, off=off)
    b = 125.7
    while b < 127.95:
        c.note("tbn", pitch("D2") + 1, T(b), q * 0.3, 88, legato=0.6)
        c.note("cb", pitch("D2") + 1, T(b), q * 0.3, 84, legato=0.6)
        c.note("kit", 38, T(b), 0.1, 66); c.note("kit", 38, T(b + q * 0.31), 0.1, 52)
        b += q * 0.62
    c.note("kit", 49, T(125.7), 1.5, 92); c.note("timp", pitch("D2") + 1, T(125.7), 0.5, 100)
    # 128.0-129.5 out of the cutaway on a HELD note (horn + violins Eb5 -> into the rim, fading under Jax)
    c.note("vln1", "D#5", T(128.0), 2.6, 70, legato=1.0); c.note("hn", "D#4", T(128.0), 2.0, 64, legato=1.0)
    c.swell("vln1", T(128.0), T(130.4), 100, 20); c.swell("hn", T(128.0), T(130.0), 100, 10)
    # 130.07-132.0 'rode it home' insert: a tiny distant quote of the march on the piccolo
    at(c, "picc", "D5:e A4:e D5:e F#5:e A5:q", 130.1, 0.2, 54, transpose=1, off=off)
    mix = {"picc": dict(inst="picc", lvl=-22, pan=-0.2, width=0.4, depth="mid", send=0.3, group="melody"),
           "tpt": dict(inst="tpt", lvl=-21, pan=0.15, width=0.5, depth="back", send=0.35, group="melody"),
           "hn": dict(inst="hn", lvl=-23, pan=-0.35, width=0.6, depth="back", send=0.4, group="harmony"),
           "tbn": dict(inst="tbn", lvl=-22, pan=0.3, width=0.5, depth="back", send=0.35, group="bass"),
           "bsn": dict(inst="bsn", lvl=-24, pan=0.25, width=0.4, depth="mid", send=0.3, group="melody"),
           "pizz": dict(inst="pizz", lvl=-26, pan=-0.25, width=0.8, depth="mid", send=0.3, group="harmony"),
           "timp": dict(inst="timp", lvl=-22, pan=0.0, width=0.6, depth="back", send=0.4, group="percussion"),
           "vln1": dict(inst="vln1", lvl=-22, pan=-0.45, width=0.8, depth="mid", send=0.45, group="melody"),
           "vla": dict(inst="vla", lvl=-28, pan=0.1, width=0.8, depth="mid", send=0.45, group="harmony"),
           "vc": dict(inst="vc", lvl=-24, pan=0.35, width=0.7, depth="mid", send=0.35, group="bass"),
           "cb": dict(inst="cb", lvl=-24, pan=0.45, width=0.5, depth="back", send=0.35, group="bass"),
           "shehnai": SYN("shehnai", lvl=-24, pan=0.5, width=0.4, depth="mid", send=0.35, group="melody"),
           "kit": dict(lvl=-24, pan=0.05, width=0.6, depth="mid", send=0.3, group="percussion",
                       kit={36: "kick", 38: "snare", 37: "stick", 49: "cym"}),
           "frame": dict(lvl=-27, pan=0.5, width=0.4, depth="mid", send=0.3, group="percussion",
                         kit={41: "frame_lo", 43: "frame_hi"})}
    return c, mix, dict(start=off, dur=132.4 - off, hall="Scala Milan Opera Hall", target=-17.0, fade_s=0.4)


# ============================================================ PART B2 (133 - 162.441)
def cue_B2():
    c = Cue("S5-B2-heart", bpm=60, seed=5104)
    off = 133.0
    tr(c, ["vla", "vc", "cb", "harp", "vln1", "vln2", "duduk", "vc_solo"])
    # 136.3-138.3 support Jax's laugh: a warm E-major swell (strings + harp) that holds it up
    c.chord("vla", ["E3", "G#3", "B3"], 136.2 - off, 2.6, 46, legato=1.0)
    c.chord("vc", ["E2", "B2"], 136.2 - off, 2.6, 44, legato=1.0)
    c.swell("vla", 136.2 - off, 137.4 - off, 50, 105); c.swell("vla", 137.4 - off, 138.9 - off, 105, 40)
    c.seq("harp", "", 0) if False else None
    for k, p in enumerate(("E4", "G#4", "B4", "E5")):
        c.note("harp", p, 136.6 - off + k * 0.18, 1.2, 44, legato=1.4)
    # 138.2-141.4 'You listened to the end': the solo cello, the rising fifth only (B E B), soft
    at(c, "vc_solo", "B2:q E3:q B3:h", 138.4, 0.8, 54, off=off)
    c.note("cb", "E2", 138.4 - off, 3.2, 30, legato=1.0)
    # 141.72 'Did it happen?' - thin to almost nothing: one high violin E, pp, ending before the silence
    c.note("vln1", "E5", 141.6 - off, 3.2, 30, legato=1.0)
    c.swell("vln1", 141.6 - off, 144.8 - off, 70, 20)
    # 144.945-147.945 TRUE SILENCE (no score at all)
    # 147.95 the promise: the heart's hummable phrase ONCE, plainly, solo duduk over a low E; it lands on the
    # B (unresolved) as 'You lie like a man...' begins (156.3); then the B held over a C chord - no answer
    spb = (156.30 - 147.95) / 9.0          # 3 bars of 3/4 = 9 beats until the B
    at(c, "duduk", "B3:q E4:q B4:q | A4:h G4:q | F#4:q G4:q A4:q | B4:h.", 147.95, spb, 70, legato=1.0, off=off)
    c.bend("duduk", 147.95 + 2 * spb - off, 147.95 + 2 * spb + 0.35 - off, -200, 0)
    c.note("cb", "E2", 148.0 - off, 8.2, 32, legato=1.0)
    c.note("vla", "E3", 148.0 - off, 8.2, 30, legato=1.0)
    c.chord("vln2", ["C4", "E4", "G4"], 156.3 - off, END - 156.3, 32, legato=1.0)    # C under B: Cmaj7, open
    c.note("vln1", "B4", 156.3 - off, END - 156.3, 36, legato=1.0)
    c.note("cb", "C2", 156.3 - off, END - 156.3, 30, legato=1.0)
    c.swell("vln1", 156.3 - off, 159.3 - off, 60, 75); c.swell("vln2", 156.3 - off, 159.3 - off, 60, 75)
    mix = {"vla": dict(inst="vla", lvl=-30, pan=0.1, width=1.0, depth="mid", send=0.6, group="harmony"),
           "vc": dict(inst="vc", lvl=-31, pan=0.3, width=0.8, depth="mid", send=0.55, group="harmony"),
           "cb": dict(inst="cb", lvl=-33, pan=0.3, width=0.6, depth="back", send=0.5, group="bass"),
           "harp": dict(inst="harp3", lvl=-29, pan=0.4, width=0.6, depth="mid", send=0.6, group="harmony"),
           "vln1": dict(inst="vln1", lvl=-30, pan=-0.3, width=0.9, depth="back", send=0.6, group="harmony"),
           "vln2": dict(inst="vln2", lvl=-32, pan=-0.1, width=0.9, depth="back", send=0.6, group="harmony"),
           "duduk": SYN("duduk", lvl=-24, pan=-0.05, width=0.4, depth="front", send=0.5, group="melody"),
           "vc_solo": dict(inst="vc_solo", lvl=-27, pan=0.2, width=0.4, depth="mid", send=0.5, group="melody")}
    return c, mix, dict(start=off, dur=END - off, hall="Musikvereinsaal", target=-21.0, fade_s=1.2)


ALL = dict(A=cue_A, B1=cue_B1, CUT=cue_CUT, B2=cue_B2)
