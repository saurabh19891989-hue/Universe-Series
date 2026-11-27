"""A4 EMOTIONAL - "The People In It" (original; Mira's theme).

Key: F major - warm and flute-friendly; melody built mostly on the major pentatonic
     (Mohanam: F G A C D), with Kalyani's raised 4th (B natural = Lydian colour) in
     the string interlude. Inspired by the *approach* of Ilaiyaraaja (melodic bass
     counter-lines, flute with slides and grace notes, a string interlude that answers
     the tune), not by any specific song.
Tempo: 72 BPM 4/4, gentle 3+3+2 hand-drum lilt; 17 bars ~ 58 s with the closing ritardando.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("A4-emotional", bpm=72, seed=44, rit=(60, 68, 56))
B = c.bar
c.track("flute", GM["flute"], 108, 70, 85)
c.track("vln", GM["strings"], 92, 44, 90)
c.track("vsolo", GM["violin"], 96, 52, 90)
c.track("pad", GM["strings2"], 78, 64, 95)
c.track("cello", GM["cello"], 100, 82, 80)
c.track("gtr", GM["nylon"], 86, 30, 70)
c.track("harp", GM["harp"], 80, 96, 90)
c.track("drums", 0, 70, 64, 50, drums=True)

PAD = {"F": ["A3", "C4", "F4"], "Dm": ["A3", "D4", "F4"], "Bb": ["Bb3", "D4", "F4"],
       "C": ["G3", "C4", "E4"], "Am": ["A3", "C4", "E4"], "Gm": ["G3", "Bb3", "D4"],
       "Fadd9": ["A3", "C4", "G4"]}
ARP = {"F": ["F2", "C3", "F3", "A3"], "Dm": ["D2", "A2", "D3", "F3"],
       "Bb": ["Bb1", "F2", "Bb2", "D3"], "C": ["C2", "G2", "C3", "E3"],
       "Am": ["A1", "E2", "A2", "C3"], "Gm": ["G1", "D2", "G2", "Bb2"],
       "Fadd9": ["F2", "C3", "G3", "A3"]}


def accomp(bar, chords, vel=60, perc=True):
    span = 4 / len(chords)
    for j, ch in enumerate(chords):
        b0 = B(bar) + j * span
        c.chord("pad", PAD[ch], b0, span, vel - 8)
        a = [pitch(p) + 12 for p in ARP[ch]]
        pat = [0, 1, 2, 3, 2, 1, 2, 3]
        for k in range(int(span * 2)):
            c.note("gtr", a[pat[k % 8]], b0 + k * 0.5, 0.9, vel - (0 if k % 4 == 0 else 10), legato=1.0)
    if perc:   # soft hand-drum lilt (3+3+2), a hint of a tabla/mridangam feel, not an imitation
        for b, d, v in ((0, "conga_lo", 46), (0.75, "conga_mute", 30), (1.5, "conga_hi", 38),
                        (2, "conga_lo", 40), (2.75, "conga_mute", 28), (3, "conga_hi", 36),
                        (3.5, "conga_mute", 30)):
            c.hit(d, B(bar) + b, v)


# --- intro bars 1-2: flute 'alaap'-like opening with slides, over a held F
c.chord("pad", ["F3", "C4", "A4"], 0, 8, 54)
c.swell("pad", 0, 8, 50, 90)
c.note("cello", "F2", 0, 8, 60)
c.seq("harp", "F3:e C4:e F4:e A4:e C5:e F5:e A5:q", 0, 52)
c.seq("flute", "r:h ~C5:q ~D5:q | ~F5:h. ~D5:e C5:e", 0, 66, legato=1.05)
c.bend("flute", 3.0, 3.35, -120, 0)          # slide up into D
c.bend("flute", 4.0, 4.5, -200, 0)           # slide up into F (from D, approximated)

MEL1 = ("C5:q. A4:e C5:e D5:e F5:q | D5:h. r:e C5:e | D5:q. C5:e D5:e F5:e G5:q | "
        "G5:h. r:e A5:e | A5:q. G5:e F5:e D5:e C5:q | D5:e C5:e A4:q ~G4:h | "
        "A4:q. C5:e D5:e F5:e D5:q | C5:q. A4:e G4:q F4:q")
HARM1 = [["F"], ["Dm"], ["Bb"], ["C"], ["Dm"], ["Bb", "C"], ["Am", "Dm"], ["Bb", "C"]]
CELLO1 = ("F2:h E2:h | D2:q E2:q F2:q A2:q | Bb2:h A2:q G2:q | C3:q Bb2:q A2:q G2:q | "
          "D3:h C3:h | Bb2:h C3:h | A2:h D3:h | Bb2:h C3:h")

# --- A: bars 3-10, flute melody
for i, ch in enumerate(HARM1):
    accomp(3 + i, ch, 60 + i)
c.seq("flute", MEL1, B(3), 80, legato=0.98,
      curve=lambda f: int(12 * (1 - abs(f - 0.55) / 0.55)) - 4)
c.seq("cello", CELLO1, B(3), 68, legato=1.0)
# grace-note/slide ornaments on held notes (gamaka-ish approximations)
for b, cents in ((B(4), -150), (B(6), -200), (B(5) + 3, -100), (B(8) + 2, 120)):
    c.bend("flute", b, b + 0.3, cents, 0)

# --- interlude bars 11-12: strings answer with a run (raised 4th B natural = Kalyani colour)
accomp(11, ["F"], 64, perc=False)
accomp(12, ["C"], 64, perc=False)
c.seq("vln", "C6:s B5:s A5:s G5:s F5:s E5:s D5:s C5:s B4:s C5:s D5:s E5:s ~F5:q", B(11), 74,
      transpose=0, legato=1.0, curve=lambda f: int(16 * f))
c.seq("vln", "r:e ~E5:e ~G5:q", B(11) + 3, 80)
c.seq("flute", "G5:e A5:e C6:q ~A5:h", B(12), 78)
c.bend("flute", B(12) + 2, B(12) + 2.4, 180, 0)
c.seq("harp", "C4:s E4:s G4:s C5:s E5:s G5:s C6:q.", B(12) + 2, 50)

# --- A': bars 13-16 violins take the tune, flute descant; bar 17 resolves
HARM2 = [["F"], ["Dm"], ["Am", "Dm"], ["Bb", "C"], ["Fadd9"]]
MEL2 = ("C5:q. A4:e C5:e D5:e F5:q | D5:h. r:e C5:e | "
        "A4:q. C5:e D5:e F5:e D5:q | C5:q. A4:e ~G4:q ~A4:q | ~F4:w")
for i, ch in enumerate(HARM2):
    accomp(13 + i, ch, 66 + min(i, 3) * 3, perc=i < 4)
c.seq("vsolo", MEL2, B(13), 84, transpose=12, legato=1.0,
      curve=lambda f: int(10 * (1 - abs(f - 0.5) / 0.5)))
c.seq("vln", MEL2, B(13), 70, legato=1.0)
c.seq("flute", "F6:w | D6:w | C6:h A5:h | G5:h ~A5:h | A5:w", B(13), 58, legato=1.0)
c.seq("cello", "F2:h E2:h | D2:q E2:q F2:q A2:q | "
      "A2:h D3:h | Bb2:h C3:h | F2:w", B(13), 72, legato=1.0)
c.swell("vln", B(13), B(16), 80, 115)  # bars 16-17 = cadence under the ritardando
c.swell("vln", B(17), B(18), 115, 50)
c.swell("pad", B(17), B(18), 100, 40)
c.seq("harp", "F3:e C4:e G4:e A4:e C5:e G5:e A5:q", B(19) - 8, 50)

if __name__ == "__main__":
    c.render(tail=4.0, gain=0.5)
