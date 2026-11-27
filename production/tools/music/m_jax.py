"""MOTIF - JAX (original). Restless, charming; a tune that never quite resolves.

Key: D Dorian (B natural), the main title's home note, so he 'belongs' to the show.
Idea: every phrase starts with the main-title head (D-A-D-E-F) and wanders off before
     it can finish it: a man who has forgotten his own name. The last note is E over
     Bbmaj7(#11): a question, not a cadence.
Tempo: 104 BPM swing (2:1 eighths), 9 bars ~ 21 s. Clarinet, nylon guitar, walking
     pizzicato bass, brushed snare / cross-stick.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("M1-jax-motif", bpm=104, seed=201, rit=(28, 36, 84))
B = c.bar
c.track("clar", GM["clarinet"], 110, 70, 60)
c.track("gtr", GM["nylon"], 90, 40, 50)
c.track("pizzB", GM["pizz"], 105, 60, 40)
c.track("pad", GM["strings"], 70, 64, 80)
c.track("drums", 0, 80, 64, 40, drums=True)

MEL = ("D5:q A4:u D5:t E5:u F5:t ~E5:q | r:u D5:t C5:u A4:t B4:q. r:e | "
       "D5:q A4:u D5:t E5:u F5:t G5:u A5:t | Bb5:q. A5:e ~E5:h | "
       "r:u F5:t D5:u Bb4:t C5:u D5:t F5:u E5:t | D5:h. r:q | "
       "D5:q A4:u D5:t E5:u F5:t G5:q | ~E5:w | r:w")
c.seq("clar", MEL, 0, 84, legato=0.95, curve=lambda f: int(10 * (1 - abs(f - 0.45) / 0.55)))
c.bend("clar", B(8), B(8) + 0.5, -60, 0)            # a little scoop into the last E

CH = [("Dm9", ["F3", "A3", "C4", "E4"]), ("G13", ["F3", "B3", "E4"]), ("Dm9", ["F3", "A3", "C4", "E4"]),
      ("Gm9", ["F3", "Bb3", "D4", "A4"]), ("Bbmaj7", ["A3", "D4", "F4"]), ("A7sus", ["G3", "D4", "E4"]),
      ("Dm9", ["F3", "A3", "C4", "E4"]), ("Bbmaj7#11", ["A3", "D4", "E4", "F4"]), ("Bbmaj7#11", ["A3", "D4", "E4", "F4"])]
WALK = ["D2 F2 A2 C3", "B2 G2 F2 E2", "D2 F2 A2 C3", "Bb2 G2 F2 E2", "Bb1 D2 F2 A2",
        "A1 D2 E2 G2", "D2 F2 A2 B2", "Bb1", "Bb1"]
for i, (name, v) in enumerate(CH):
    bar = 1 + i
    # guitar: swung off-beat comping ('and' of 2, and 4), last bars let ring
    if i < 7:
        c.chord("gtr", v, B(bar) + 1 + 2 / 3, 0.4, 62, roll=0.012)
        c.chord("gtr", v, B(bar) + 3, 0.9, 58, roll=0.012)
    else:
        c.chord("gtr", v, B(bar), 4, 60, roll=0.05)
    notes = WALK[i].split()
    if len(notes) == 4:
        for k, p in enumerate(notes):
            c.note("pizzB", p, B(bar) + k, 1, 84 - (k % 2) * 8, legato=0.6)
    else:
        c.note("pizzB", notes[0], B(bar), 2, 80, legato=0.6)
    c.chord("pad", v, B(bar), 4, 40)
    # brushes: cross-stick on 2 and 4, swung pedal hat
    if i < 8:
        for b in (1, 3):
            c.hit("rim", B(bar) + b, 46)
        for b in range(4):
            c.hit("hatp", B(bar) + b, 34)
            c.hit("hatp", B(bar) + b + 2 / 3, 26)
c.swell("pad", B(1), B(10), 70, 40)

if __name__ == "__main__":
    c.render(tail=3.0, gain=0.5)
