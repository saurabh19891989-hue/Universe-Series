"""A3 TENSION / BETRAYAL - "Address Withdrawn" (original).

Key: C Phrygian/minor (the flat 2nd, Db, rubs against C) with a tritone F# for dread.
Tempo: 60 BPM 4/4 - so the ticking motif is literally one tick per second; 13 bars ~ 52 s.
Layers: woodblock clock tick, pitched pizzicato tick motif, contrabass/timpani
     'lub-dub' heartbeat, tremolo-string cluster that swells, and a BETRAYAL motif
     (C - F# - G - Ab - G: the main-title head bent around a tritone) passed from
     cello to horn to full strings. Ends on a hard cut.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM

c = Cue("A3-tension-betrayal", bpm=60, seed=33)
B = c.bar
c.track("trem", GM["trem"], 100, 64, 90)
c.track("bass", GM["contrabass"], 110, 60, 60)
c.track("cello", GM["cello"], 105, 48, 70)
c.track("horn", GM["horn"], 100, 74, 90)
c.track("tick", GM["pizz"], 70, 96, 70)
c.track("celesta", GM["celesta"], 60, 30, 90)
c.track("lowbr", GM["trombone"], 90, 70, 80)
c.track("timp", GM["timpani"], 105, 64, 70)
c.track("vln", GM["strings"], 92, 40, 90)
c.track("drums", 0, 90, 64, 50, drums=True)

END = B(13)          # hard cut point
# clock: tick-tock every beat, all the way
for b in range(int(END)):
    c.hit("wood_hi" if b % 2 == 0 else "wood_lo", b, 52 + int(b * 0.6), 0.2)

# heartbeat lub-dub, getting stronger and (from bar 9) twice per bar
for bar in range(1, 13):
    reps = (0, 2) if bar >= 9 else (0,)
    for r in reps:
        v = 50 + bar * 5
        c.note("bass", "C2", B(bar) + r, 0.5, v, legato=0.7)
        c.note("bass", "C2", B(bar) + r + 0.75, 0.5, v - 15, legato=0.7)
        c.note("timp", "C2", B(bar) + r, 0.5, v - 10)

# tremolo cluster swells: C/Db, then G/Ab added, then F# (tritone) - slow dread
c.chord("trem", ["C3", "Db3"], 0, 16, 70)
c.swell("trem", 0, 16, 30, 100)
c.chord("trem", ["G3", "Ab3"], B(5), 16, 72)
c.chord("trem", ["C3", "Db3", "F#4"], B(9), 16, 84)
c.swell("trem", B(5), B(9), 60, 90)
c.swell("trem", B(9), B(13), 80, 127)

# pitched tick motif (pizzicato, then celesta doubling) from bar 3
for bar in range(3, 13):
    for k, p in enumerate(["G5", "G5", "G5", "Ab5"] * 2):
        c.note("tick", p, B(bar) + k * 0.5, 0.25, 50 + bar * 3 + (10 if k % 4 == 0 else 0), legato=0.4)
    if bar >= 7:
        c.note("celesta", "G6" if bar % 2 else "Ab6", B(bar), 1, 48 + bar * 2)

BETRAY = "C4:q. F#3:e G3:q Ab3:q | G3:w"
c.seq("cello", BETRAY, B(3), 78, transpose=-12, legato=1.0)
c.swell("cello", B(3), B(5), 70, 110)
c.seq("horn", BETRAY, B(7), 82, legato=1.0)
c.swell("horn", B(7), B(9), 80, 120)
# full strings + low brass, forte, rising a semitone higher each time (Db)
c.seq("vln", BETRAY, B(10), 96, transpose=12, legato=1.0)
c.seq("cello", BETRAY, B(10), 100, transpose=-12, legato=1.0)
c.seq("lowbr", "C3:q. F#2:e G2:q Ab2:q | G2:w", B(10), 92, legato=1.0)
c.seq("vln", "Db5:q. G4:e Ab4:q A4:q | Ab4:h. r:q", B(12), 104, transpose=0, legato=1.0)
c.seq("horn", "Db4:q. G3:e Ab3:q A3:q", B(12), 100, legato=1.0)
c.chord("lowbr", ["C2", "Db3", "G3"], B(12), 4, 100)
for i in range(16):                                   # timpani roll into the cut
    c.note("timp", "C2", B(12) + i * 0.25, 0.25, 60 + i * 4)
c.hit("crash", B(12) + 2, 40, 2)

# hard cut: everything ends at END, then one last tick in the silence
for inst in c.pm.instruments:
    cut = c.t(END)
    inst.notes = [n for n in inst.notes if n.start < cut]
    for n in inst.notes:
        n.end = min(n.end, cut)
c.hit("wood_hi", END + 1, 70, 0.2)
c.note("bass", "C1", END + 1, 1, 60)

if __name__ == "__main__":
    c.render(tail=3.0, gain=0.5)
