"""MOTIF - VOSS (original). Gracious and cold: a waltz that is slightly too slow.

Key: A minor with a Neapolitan Bb and a final open fifth (no third = no warmth).
Link to the show: the waltz opens with E - A# - B - C - B, i.e. the betrayal motif
     (C-F#-G-Ab-G from A3) re-dressed as a courtly turn - Voss is where betrayal lives.
Tempo: 3/4 at 132 BPM (a Viennese waltz runs ~170-180), easing to 110 at the end,
     so it feels elegant but a touch heavy and deliberate. 16 bars ~ 23 s.
Strings oom-pah-pah (cello/bass on 1, viola + 2nd violins on 2 and 3), 1st violins
     with the tune, celesta doubling it an octave up for the chill, one soft horn.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("M4-voss-motif", bpm=132, beats_per_bar=3, seed=204, rit=(39, 48, 110))
B = c.bar
c.track("vln", GM["strings"], 100, 44, 80)
c.track("celesta", GM["celesta"], 70, 30, 85)
c.track("cello", GM["cello"], 100, 80, 70)
c.track("bass", GM["contrabass"], 95, 64, 60)
c.track("chords", GM["strings2"], 85, 70, 75)
c.track("horn", GM["horn"], 85, 56, 85)
c.track("harp", GM["harp"], 70, 96, 80)

MEL = ("E5:h A#4:q | B4:q C5:q B4:q | A4:h. | r:q E5:q F5:q | E5:h D#5:q | E5:q B5:q A5:q | "
       "G#5:h. | r:h E5:q | F5:h E5:q | D5:q C5:q Bb4:q | A4:h G#4:q | A4:h. | "
       "E5:h A#4:q | B4:q C5:q B4:q | A4:h. | r:h.")
c.seq("vln", MEL, 0, 84, legato=1.0, curve=lambda f: int(10 * (1 - abs(f - 0.4) / 0.6)) - 4)
c.seq("celesta", "E5:h A#4:q | B4:q C5:q B4:q | A4:h.", B(13), 60, transpose=12, legato=0.9)
c.seq("celesta", "E6:h A#5:q | B5:q C6:q B5:q", 0, 46, legato=0.9)

H = ["Am", "E7b9", "Am", "Dm/F", "E", "Am", "E", "E7", "Dm", "Bb", "E7", "Am", "Am", "E7b9", "Fmaj7", "A5"]
BASS = {"Am": "A2", "E7b9": "G#2", "Dm/F": "F2", "E": "E2", "E7": "E2", "Dm": "D2", "Bb": "Bb1",
        "Fmaj7": "F2", "A5": "A1"}
UP = {"Am": ["A3", "C4", "E4"], "E7b9": ["D4", "F4", "B4"], "Dm/F": ["A3", "D4", "F4"], "E": ["G#3", "B3", "E4"],
      "E7": ["G#3", "D4", "E4"], "Dm": ["A3", "D4", "F4"], "Bb": ["Bb3", "D4", "F4"], "Fmaj7": ["A3", "C4", "E4"],
      "A5": ["E3", "A3", "E4"]}
for i, ch in enumerate(H):
    bar = 1 + i
    if ch == "A5":                                   # hollow open fifth, held
        c.note("bass", "A1", B(bar), 3, 70)
        c.chord("cello", ["A2", "E3"], B(bar), 3, 64)
        c.note("celesta", "E6", B(bar), 3, 50)
        c.seq("harp", "A2:e E3:e A3:e E4:e A4:e E5:e", B(bar), 46)
        continue
    c.note("cello", BASS[ch], B(bar), 1, 72, legato=0.55)
    c.note("bass", pitch(BASS[ch]) - 12, B(bar), 1, 66, legato=0.55)
    for b in (1, 2):
        c.chord("chords", UP[ch], B(bar) + b, 1, 52 if b == 1 else 46, legato=0.45)
c.chord("horn", ["E3", "A3"], B(1), 9, 46)
c.chord("horn", ["D3", "F3"], B(9), 6, 48)
c.chord("horn", ["E3", "G#3"], B(11), 3, 50)

if __name__ == "__main__":
    c.render(tail=3.5, gain=0.5)
