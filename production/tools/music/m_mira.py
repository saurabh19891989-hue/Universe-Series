"""MOTIF - MIRA (original). Precise, warm underneath; Bengali colour.

Key: F (Sa = F). The tune is built on Sa Re Ga Pa Dha (F G A C D) with komal Ni
     (Eb) as colour, in the long-breathed, falling shape of Bengali bhatiyali (river
     boat-song) melodies - an inspiration, not a quotation, and not a raga performance.
Precision: a steady celesta sixteenth 'clockwork' (her instruments and maps).
Warmth: bansuri-like flute with meend-style slides; a solo cello answers with slides
     the way an esraj might; strings hold a Sa-Pa (F-C) drone in place of a tanpura.
     The phrase resolves exactly on Sa: unlike Jax, she always lands.
Tempo: 66 BPM 4/4, 6 bars ~ 22 s. It shares A4's pentatonic world.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("M2-mira-motif", bpm=66, seed=202, rit=(20, 24, 54))
B = c.bar
c.track("flute", GM["flute"], 110, 70, 80)
c.track("cello", GM["cello"], 95, 84, 75)
c.track("drone", GM["strings"], 80, 64, 90)
c.track("pad", GM["strings2"], 75, 50, 90)
c.track("celesta", GM["celesta"], 70, 30, 70)
c.track("harp", GM["harp"], 70, 96, 80)

# drone Sa-Pa the whole way
c.chord("drone", ["F2", "C3", "F3"], 0, 24, 58)
c.swell("drone", 0, 4, 60, 95)
c.swell("drone", 20, 26, 95, 50)

MEL = ("r:h C6:q. ~A5:e | G5:e A5:e C6:q ~A5:h | G5:q. F5:e Eb5:q ~D5:q | "
       "C5:h. D5:e F5:e | G5:q. A5:e G5:e F5:e D5:q | ~C5:h F5:h")
c.seq("flute", MEL, 0, 80, legato=1.0, curve=lambda f: int(12 * (1 - abs(f - 0.5) / 0.5)) - 3)
c.bend("flute", 3.5, 3.9, -200, 0)        # meend up into A
c.bend("flute", B(2) + 2, B(2) + 2.4, 200, 0)  # slide down onto A
c.bend("flute", B(3) + 3, B(3) + 3.5, 200, 0)  # glide down into D
c.bend("flute", B(6), B(6) + 0.5, -200, 0)     # lift into C
# esraj-like answer on solo cello in bar 4 and the cadence
c.seq("cello", "r:w | r:w | r:w | r:h A3:q ~C4:q | D4:h. r:q | r:h F3:h", 0, 70, legato=1.0)
c.bend("cello", B(4) + 3, B(4) + 3.5, -200, 0)

HARM = [["F3", "A3", "C4"], ["F3", "A3", "C4"], ["Eb3", "G3", "Bb3"], ["D3", "F3", "A3"],
        ["D3", "F3", "Bb3"], ["F3", "A3", "C4"]]
for i, v in enumerate(HARM):
    c.chord("pad", [pitch(p) + 12 for p in v], B(1 + i), 4, 50)
    # clockwork: celesta sixteenths, quiet and exact (no swing, tiny velocity variation)
    pat = [pitch(v[0]) + 24, pitch(v[2]) + 24, pitch(v[1]) + 24, pitch(v[2]) + 24]
    for k in range(16 if i < 5 else 8):
        c.note("celesta", pat[k % 4], B(1 + i) + k * 0.25, 0.25, 40 + (8 if k % 4 == 0 else 0), legato=0.5)
c.seq("harp", "F3:s C4:s F4:s A4:s C5:s F5:s A5:s C6:q.", B(6) + 2, 52)

if __name__ == "__main__":
    c.render(tail=3.5, gain=0.5)
