"""MOTIF - PIP (original). A very small, very correct march.

Key: C major (the 'correct' key), strictly diatonic, four 4-bar phrases with a textbook
     half cadence (bar 8) and perfect cadence (bars 14-16).
Tempo: 116 BPM in 2/4, 16 bars ~ 17 s. Tiny forces: piccolo + glockenspiel tune,
     bassoon 'oom', pizzicato 'pah', a side drum played very quietly, triangle on the
     cadence - and after a correct pause, one rubber-stamp hit (bass drum + pizz chord).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("M3-pip-motif", bpm=116, beats_per_bar=2, seed=203)
B = c.bar
c.track("picc", GM["piccolo"], 100, 70, 50)
c.track("glock", GM["glock"], 80, 80, 55)
c.track("bsn", GM["bassoon"], 105, 54, 40)
c.track("pizz", GM["pizz"], 95, 60, 45)
c.track("drums", 0, 85, 64, 40, drums=True)

A = ("C6:e E6:e G6:e E6:e | C6:q G5:q | A5:e B5:e C6:e D6:e | E6:q C6:q | "
     "F6:e E6:e D6:e C6:e | B5:e A5:e G5:q | A5:e B5:e C6:e D6:e | D6:q r:q | ")
A2 = ("C6:e E6:e G6:e E6:e | C6:q G5:q | A5:e B5:e C6:e D6:e | E6:q C6:q | "
      "F6:e E6:e D6:e C6:e | B5:e D6:e G6:e B5:e | C6:q r:e G5:e | C6:q r:q")
TUNE = A + A2
c.seq("picc", TUNE, 0, 80, legato=0.55)
c.seq("glock", TUNE, 0, 58, legato=0.5)

H = ["C", "C", "F", "C", "F", "G", "F", "G", "C", "C", "F", "C", "F", "G7", "C", "C"]
ROOT = {"C": "C3", "F": "F2", "G": "G2", "G7": "G2"}
UP = {"C": ["E4", "G4", "C5"], "F": ["F4", "A4", "C5"], "G": ["D4", "G4", "B4"], "G7": ["F4", "G4", "B4"]}
for i, ch in enumerate(H):
    bar = 1 + i
    c.note("bsn", ROOT[ch], B(bar), 1, 76, legato=0.4)        # oom
    c.chord("pizz", UP[ch], B(bar) + 1, 0.5, 60, legato=0.4)  # pah
    # side drum, very small: tap on 1, a neat pair on 2
    c.hit("snare", B(bar), 40)
    if i % 4 != 3:
        c.hit("snare", B(bar) + 1, 30)
        c.hit("snare", B(bar) + 1.5, 28)
c.hit("tri", B(8), 48, 1)
c.hit("tri", B(16), 56, 1)
# the rubber stamp: after one correct, silent beat
STAMP = B(17) + 1
c.hit("kick2", STAMP, 92, 1)
c.hit("wood_lo", STAMP, 80)
c.chord("pizz", ["C3", "G3", "E4", "C5"], STAMP, 0.5, 100, legato=0.4)
c.note("bsn", "C2", STAMP, 0.5, 96, legato=0.4)

if __name__ == "__main__":
    c.render(tail=2.5, gain=0.5)
