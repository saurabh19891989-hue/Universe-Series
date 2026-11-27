"""A5 GLOBAL FLAVOUR - "Urashima's Return" (original), for a guest legend from Japan
(Urashima Taro, the fisherman who returned from the Dragon Palace to find centuries gone
- a natural time-dilation story for a space show).

Tradition: Japanese hogaku colours in a cinematic fusion (not a traditional piece).
Scale: miyako-bushi / 'in' scale on D (D Eb G A Bb), the scale of koto hirajoshi tuning.
Koto: tuned hirajoshi on D (strings 1-13: D4 G3 A3 Bb3 D4 Eb4 G4 A4 Bb4 D5 Eb5 G5 A5);
      only those pitches are used, including sararin-style sweeps across the strings.
Shakuhachi: melody with pitch-bend approximations of meri/kari bends and suri slides.
Taiko: nagado-daiko 'don' strokes plus rim 'ka' and a higher drum standing in for shime-daiko;
      rhythms are simplified kumi-daiko-style patterns written for this cue.
Strings pad underneath for the cinematic fusion. Samples: FluidR3_GM koto/shakuhachi/taiko,
which are General-MIDI approximations, not authentic instrument recordings.
Tempo: 80 BPM 4/4; 15 bars ~ 45 s.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("A5-global-japan-urashima", bpm=80, seed=55, rit=(52, 60, 60))
B = c.bar
c.track("shaku", GM["shakuhachi"], 110, 58, 95)
c.track("koto", GM["koto"], 104, 82, 80)
c.track("pad", GM["strings"], 80, 64, 100)
c.track("bass", GM["contrabass"], 90, 64, 70)
c.track("taiko", GM["taiko"], 118, 60, 70)
c.track("shime", GM["taiko"], 80, 76, 60)
c.track("drums", 0, 80, 64, 50, drums=True)

KOTO = ["D4", "G3", "A3", "Bb3", "D4", "Eb4", "G4", "A4", "Bb4", "D5", "Eb5", "G5", "A5"]
SWEEP = sorted(set(KOTO[1:]), key=pitch)


def sararin(beat, vel=70, down=False, step=1 / 12):
    notes = SWEEP[::-1] if down else SWEEP
    for i, p in enumerate(notes):
        c.note("koto", p, beat + i * step, 2.0, vel + i * (1 if not down else -1), legato=1.0)


def taiko_bar(bar, level):
    if level == 1:
        pat = [(0, 100), (2, 80), (2.5, 70)]
        ka = [1, 3]
    else:
        pat = [(0, 122), (0.5, 80), (1, 100), (2, 118), (2.5, 84), (2.75, 78), (3, 108), (3.5, 96)]
        ka = [1.5, 3.25]
    for b, v in pat:
        c.note("taiko", "C2", B(bar) + b, 0.5, v)
    for b in ka:
        c.hit("rim", B(bar) + b, 70 if level == 1 else 88)
    if level == 2:
        for k in range(8):
            c.note("shime", "G3", B(bar) + k * 0.5, 0.25, 60 + (20 if k % 2 == 0 else 0))


# --- bars 1-2: koto alone, sweep then a phrase
sararin(0, 66)
c.seq("koto", "r:h D4:e A4:e Bb4:e A4:e | G4:q D4:q ~Eb4:q D4:q", 0, 74)
c.chord("pad", ["D3", "A3"], 0, 8, 50)
c.swell("pad", 0, 8, 40, 80)

PADS = [["D3", "A3"], ["G3", "Bb3", "D4"], ["Eb3", "G3", "Bb3"], ["D3", "A3", "D4"]]
BASS = ["D2", "G1", "Eb2", "D2"]
A = "A4:h. ~Bb4:e A4:e | G4:h Eb4:q D4:q | D4:q. G4:e A4:q Bb4:q | A4:w"
Bm = "D5:h. Eb5:e D5:e | Bb4:h A4:q G4:q | A4:q. Bb4:e D5:q Eb5:q | D5:w"
C = "G5:h. A5:e G5:e | Eb5:h D5:q Bb4:q | A4:q. Bb4:e D5:q Eb5:q | ~D5:w"

# --- bars 3-6: shakuhachi melody, koto answers
c.seq("shaku", A, B(3), 78, legato=1.0, curve=lambda f: int(10 * (1 - abs(f - 0.4) / 0.6)))
for b, c0 in ((B(3), -180), (B(4), -100), (B(6), -150)):   # meri-style bend up into the note
    c.bend("shaku", b, b + 0.6, c0, 0)
c.seq("koto", "r:w | r:h. Bb4:e A4:e | r:w | r:h D5:e Eb5:e D5:q", B(3), 66)
for i in range(4):
    c.chord("pad", PADS[i], B(3 + i), 4, 56)
    c.note("bass", BASS[i], B(3 + i), 4, 50)
c.note("taiko", "C2", B(5), 1, 90)

# --- bars 7-10: taiko enters, koto ostinato, melody up
for i in range(4):
    bar = 7 + i
    taiko_bar(bar, 1)
    c.seq("koto", "D4:e A4:e Bb4:e A4:e D5:e A4:e Bb4:e A4:e", B(bar), 62 + i * 3, legato=0.9)
    c.chord("pad", PADS[i], B(bar), 4, 64)
    c.note("bass", BASS[i], B(bar), 4, 64)
c.seq("shaku", Bm, B(7), 88, legato=1.0)
c.bend("shaku", B(7), B(7) + 0.5, -200, 0)
c.bend("shaku", B(10), B(10) + 0.8, -100, 0)
c.swell("pad", B(7), B(11), 70, 105)

# --- bars 11-14: climax with full taiko, sweeps
c.note("taiko", "F1", B(11), 2, 127)
sararin(B(11), 84)
for i in range(4):
    bar = 11 + i
    taiko_bar(bar, 2)
    c.seq("koto", "D5:e A4:e Bb4:e A4:e Eb5:e A4:e Bb4:e A4:e", B(bar), 72 + i * 3, legato=0.9)
    c.chord("pad", [pitch(p) + 12 for p in PADS[i]], B(bar), 4, 80)
    c.note("bass", BASS[i], B(bar), 4, 80)
c.seq("shaku", C, B(11), 100, legato=1.0)
c.bend("shaku", B(11), B(11) + 0.5, -200, 0)
c.bend("shaku", B(14), B(14) + 1.0, -150, 0)

# --- bar 15: final stroke, downward sweep, ring
c.note("taiko", "F1", B(15), 4, 127)
c.note("taiko", "C2", B(15), 1, 120)
c.hit("rim", B(15) + 0.5, 90)
sararin(B(15), 80, down=True)
c.chord("pad", ["D3", "A3", "D4", "A4"], B(15), 4, 80)
c.swell("pad", B(15), B(16), 110, 30)
c.note("bass", "D2", B(15), 4, 80)

if __name__ == "__main__":
    c.render(tail=4.0, gain=0.5)
