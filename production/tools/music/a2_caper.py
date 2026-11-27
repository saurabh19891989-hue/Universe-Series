"""A2 COMEDY / CAPER - "Eleven Minutes Late" (original).

Key: E minor with chromatic approach notes and a sly C7 (bVI7) - the bassoon sits
     well there and the pizzicato open E/B strings ring.
Tempo: 132 BPM 4/4, staccato, ~37 s. Tiptoe pizzicato bass, bassoon theme, clarinet
     takes it up an octave, hand percussion (woodblocks, shaker, bongos, claves, triangle).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("A2-comedy-caper", bpm=132, seed=22, rit=(76, 80, 110))
B = c.bar
c.track("pizzB", GM["pizz"], 110, 58, 40)
c.track("pizzU", GM["pizz"], 82, 84, 45)
c.track("bsn", GM["bassoon"], 112, 54, 45)
c.track("clar", GM["clarinet"], 100, 76, 50)
c.track("glock", GM["glock"], 70, 90, 60)
c.track("drums", 0, 92, 64, 35, drums=True)

H = ["Em", "Em", "Am", "B7", "Em", "C7", "B7", "Em"]
ROOT = {"Em": "E2", "Am": "A2", "B7": "B1", "C7": "C2"}
FIFTH = {"Em": "B2", "Am": "E2", "B7": "F#2", "C7": "G2"}
UPPER = {"Em": ["G3", "B3"], "Am": ["A3", "C4"], "B7": ["A3", "D#4"], "C7": ["Bb3", "E4"]}


def bass_bar(bar, ch, nxt, vel=88):
    r, f = pitch(ROOT[ch]), pitch(FIFTH[ch])
    nr = pitch(ROOT[nxt])
    approach = nr - 1 if nr - 1 != r else nr + 1      # chromatic lower neighbour into next root
    for b, p, v in ((0, r, vel), (1, f, vel - 14), (2, r + 12, vel - 6), (3, approach, vel - 10)):
        c.note("pizzB", p, B(bar) + b, 0.5, v, legato=0.5)


def offbeats(bar, ch, key="pizzU", vel=62):
    for b in (1.5, 3.5):
        c.chord(key, UPPER[ch], B(bar) + b, 0.25, vel, legato=0.5)


THEME = ("E3:e r:e G3:e r:e A3:e A#3:e B3:q | r:e B3:e C4:e B3:e A#3:e B3:e G3:q | "
         "A3:e r:e C4:e r:e E4:e D#4:e E4:q | D#4:e r:e F#3:e A3:e B3:q. r:e | "
         "E3:e r:e G3:e r:e A3:e A#3:e B3:q | r:e C4:e E4:e G4:e Bb3:q r:q | "
         "A3:e G3:e F#3:e A3:e G3:e F#3:e D#3:q | E3:e r:e r:q B2:e r:e E3:e r:e")

# intro: tick-tock woodblocks + tiptoe bass, bars 1-2
for bar in (1, 2):
    bass_bar(bar, "Em", "Em", 70 + bar * 6)
    for b in range(4):
        c.hit("wood_hi" if b % 2 == 0 else "wood_lo", B(bar) + b, 70)
c.note("glock", "B5", B(2) + 3.5, 0.5, 70)

# A: bassoon theme, bars 3-10
for i, ch in enumerate(H):
    bar = 3 + i
    bass_bar(bar, ch, H[(i + 1) % 8], 86)
    offbeats(bar, ch)
    for k in range(8):
        c.hit("shaker", B(bar) + k * 0.5, 52 + (14 if k % 2 else 0), 0.25)
    c.hit("wood_hi", B(bar), 72)
    c.hit("claves", B(bar) + 2.5, 60)
c.seq("bsn", THEME, B(3), 92, legato=0.55,
      curve=lambda f: int(10 * f))
c.hit("tri", B(10), 70, 1)

# B: clarinet takes the tune up an octave; bassoon does offbeat 'oom-pah'; bongos, bars 11-18
for i, ch in enumerate(H):
    bar = 11 + i
    bass_bar(bar, ch, H[(i + 1) % 8], 94)
    offbeats(bar, ch, "bsn", 70)
    offbeats(bar, ch, "pizzU", 66)
    for b, d, v in ((0, "bongo_lo", 86), (0.5, "bongo_hi", 60), (1.5, "bongo_hi", 78),
                    (2, "bongo_lo", 80), (2.75, "bongo_hi", 58), (3, "bongo_hi", 74),
                    (3.5, "bongo_lo", 66)):
        c.hit(d, B(bar) + b, v)
    for k in range(8):
        c.hit("shaker", B(bar) + k * 0.5, 56 + (16 if k % 2 else 0), 0.25)
    if i % 2 == 0:
        c.hit("tri", B(bar), 58, 1)
c.seq("clar", THEME, B(11), 96, transpose=12, legato=0.6, curve=lambda f: int(12 * f))
# glockenspiel winks at the cheeky C7 and the cadence
c.seq("glock", "r:e C6:e E6:e G6:e r:h", B(16), 64)
c.seq("glock", "r:h r:e B5:e E6:q", B(18), 66)

# tag bars 19-20: the sneak... and the button
c.seq("bsn", "E3:e r:e G3:e r:e A3:e A#3:e B3:e r:e", B(19), 100, legato=0.5)
c.seq("clar", "E4:e r:e G4:e r:e A4:e A#4:e B4:e r:e", B(19), 96, legato=0.5)
c.seq("pizzB", "E2:e r:e G2:e r:e A2:e A#2:e B2:e r:e", B(19), 96, legato=0.5)
c.hit("wood_hi", B(20), 70)
c.hit("wood_lo", B(20) + 1, 64)
c.seq("pizzB", "r:h r:e B1:e E2:e r:e", B(20), 104, legato=0.5)
c.seq("bsn", "r:h r:e B2:e E2:e r:e", B(20), 104, legato=0.45)
c.chord("pizzU", ["E3", "B3", "G4"], B(20) + 3, 0.5, 96, legato=0.5)
c.note("glock", "E6", B(20) + 3, 1, 84)
c.hit("bongo_hi", B(20) + 3, 92)

if __name__ == "__main__":
    c.render(tail=3.0, gain=0.5)
