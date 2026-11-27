"""A1 MAIN TITLE - "Secret Universe" theme (original).

Key: D minor (Aeolian with a harmonic-minor C# cadence) - dark but heroic, and the
     open D/A strings make the low ostinato ring.
Tempo: 120 BPM 4/4 - a brisk 'courier on a deadline' pulse; 28 bars ~ 56 s + tail.
Form: intro (sitar call + ostinato) | A theme on horns | A' theme on trumpets/violins
      with full percussion | 4-bar build | tag + final chord.
Colour instrument: sitar (GM sitar sample) with pitch-bend glides (a nod to meend),
      playing a D-minor-pentatonic call. It's a colour, not a raga performance.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("A1-main-title", bpm=120, seed=11, rit=(104, 112, 92))
B = c.bar

# tracks: key, program, vol, pan, reverb
c.track("cello", GM["cello"], 105, 50, 50)
c.track("bass", GM["contrabass"], 100, 60, 45)
c.track("viola", GM["viola"], 85, 78, 55)
c.track("pad", GM["strings"], 90, 64, 80)
c.track("vln", GM["strings2"], 95, 40, 75)
c.track("horn", GM["horn"], 108, 70, 80)
c.track("tpt", GM["trumpet"], 92, 56, 80)
c.track("lowbr", GM["trombone"], 98, 74, 70)
c.track("tuba", GM["tuba"], 95, 64, 60)
c.track("choir", GM["choir"], 80, 64, 100)
c.track("sitar", GM["sitar"], 96, 90, 85)
c.track("taiko", GM["taiko"], 115, 64, 70)
c.track("timp", GM["timpani"], 110, 64, 70)
c.track("drums", 0, 100, 64, 60, drums=True)

# ---- harmony ------------------------------------------------------------
# chord: (bass note, ostinato root, upper pad voicing, chord tones for ostinato)
CH = {
    "Dm": ("D2", "D3", ["A3", "D4", "F4"], ["D3", "A3", "D4", "F3"]),
    "C":  ("C2", "C3", ["G3", "C4", "E4"], ["C3", "G3", "C4", "E3"]),
    "F":  ("F2", "F3", ["A3", "C4", "F4"], ["F2", "C3", "F3", "A2"]),
    "Bb": ("Bb1", "Bb2", ["Bb3", "D4", "F4"], ["Bb2", "F3", "Bb3", "D3"]),
    "Gm": ("G1", "G2", ["G3", "Bb3", "D4"], ["G2", "D3", "G3", "Bb2"]),
    "A":  ("A1", "A2", ["A3", "C#4", "E4"], ["A2", "E3", "A3", "C#3"]),
    "Asus": ("A1", "A2", ["A3", "D4", "E4"], ["A2", "E3", "A3", "D3"]),
}
THEME_H = ["Dm", "C", "Dm", "F", "Bb", "C", ("Gm", "A"), "Dm"]

# 3+3+2 accented sixteenth ostinato: index into chord tones [R,5,8,3]
OST = [0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 1, 0, 0, 1, 3, 1]
ACC = {0, 3, 6, 8, 11, 14}


def ostinato(bar, chord, base_vel, key="cello", oct=0, beats=4):
    tones = [pitch(n) + oct for n in CH[chord][3]]
    for i in range(int(beats * 4)):
        v = base_vel + (22 if i in ACC else 0)
        c.note(key, tones[OST[i % 16]], B(bar) + i * 0.25, 0.25, v, legato=0.6)


def harmony_bar(bar, ch, pad_vel=None, bass_vel=None, lowbr_vel=None, ost_vel=None,
                viola=False, choir_vel=None):
    parts = ch if isinstance(ch, tuple) else (ch,)
    span = 4 / len(parts)
    for j, name in enumerate(parts):
        b = B(bar) + j * span
        bass, _, pad, _ = CH[name]
        if pad_vel:
            c.chord("pad", pad, b, span, pad_vel)
        if choir_vel:
            c.chord("choir", [pitch(p) + 12 for p in pad[1:]], b, span, choir_vel)
        if bass_vel:
            c.note("bass", bass, b, span, bass_vel, legato=0.98)
        if lowbr_vel:
            c.chord("lowbr", [pitch(bass) + 12, pitch(CH[name][2][0])], b, span, lowbr_vel)
            c.note("tuba", bass, b, span, lowbr_vel - 8)
        if ost_vel:
            ostinato(bar, name, ost_vel, beats=4) if len(parts) == 1 else None
            if len(parts) > 1:
                tones = [pitch(n) for n in CH[name][3]]
                for i in range(int(span * 4)):
                    k = j * int(span * 4) + i
                    c.note("cello", tones[OST[k]], b + i * 0.25, 0.25,
                           ost_vel + (22 if k in ACC else 0), legato=0.6)
                    if viola:
                        c.note("viola", tones[OST[k]] + 12, b + i * 0.25, 0.25,
                               ost_vel - 12 + (18 if k in ACC else 0), legato=0.6)
        if viola and len(parts) == 1:
            ostinato(bar, name, ost_vel - 12, key="viola", oct=12)


THEME = ("D5:q A4:q D5:e E5:e F5:q | E5:h. C5:q | D5:q A4:q D5:e E5:e F5:e G5:e | A5:h. r:q | "
         "Bb5:q A5:q G5:q F5:q | G5:q F5:q E5:h | F5:q E5:q D5:q C#5:q | D5:w")


def arch(f):          # phrase shape: rise to 60 % then relax
    return int(14 * (1 - abs(f - 0.6) / 0.6)) - 6


# ---- INTRO bars 1-4 -------------------------------------------------------
for bar in range(1, 5):
    ostinato(bar, "Dm", 38 + bar * 6)
    c.note("bass", "D2", B(bar), 4, 55 + bar * 5)
    c.note("timp", "D2", B(bar), 1, 50 + bar * 8)
    c.note("timp", "A1", B(bar) + 2.5, 1, 40 + bar * 6)
c.chord("pad", ["A3", "D4"], 0, 16, 60)
c.swell("pad", 0, 16, 40, 100)
c.seq("sitar", "r:q D4:e A4:e ~C5:q A4:e G4:e | A4:h. r:q", 0, 88)
c.bend("sitar", 4.0, 4.35, -200, 0)          # meend glide G -> A
c.seq("sitar", "r:q D4:e A4:e ~C5:e D5:e C5:e A4:e | G4:q F4:q D4:h", 8, 92)
c.bend("sitar", 12.0, 12.3, 150, 0)
c.bend("sitar", 14.0, 14.4, 200, 0)          # slide down into D
for bar in (3, 4):
    c.note("taiko", "C2", B(bar), 1, 70)
    c.note("taiko", "C2", B(bar) + 2.5, 1, 55)
c.hit("crash", B(4) + 2, 35, 2)               # soft cymbal swell into A
c.hit("crash", B(4) + 3, 60, 1)

# ---- A: theme on horns, bars 5-12 ----------------------------------------
for i, ch in enumerate(THEME_H):
    bar = 5 + i
    harmony_bar(bar, ch, pad_vel=62 + i * 2, bass_vel=72, ost_vel=55 + i * 2)
    c.note("timp", CH[ch if isinstance(ch, str) else ch[0]][0], B(bar), 1, 70)
    c.note("taiko", "C2", B(bar), 1, 78)
    c.note("taiko", "C2", B(bar) + 1.5, 0.5, 58)
    c.note("taiko", "C2", B(bar) + 2, 1, 70)
c.seq("horn", THEME, B(5), 88, transpose=-12, legato=0.97, curve=arch)
c.swell("horn", B(5), B(13), 95, 120)
# sitar answers in the gap of bar 8 (theme holds A)
c.seq("sitar", "r:h D5:e C5:e A4:q", B(8), 80)

# ---- A': full statement, bars 13-20 --------------------------------------
c.hit("crash", B(13), 105, 3)
c.note("taiko", "F1", B(13), 2, 120)
for i, ch in enumerate(THEME_H):
    bar = 13 + i
    harmony_bar(bar, ch, pad_vel=84, bass_vel=92, lowbr_vel=80 + i * 2, ost_vel=68,
                viola=True, choir_vel=62 + i * 3)
    for b, v in ((0, 118), (1.5, 82), (2, 104), (3, 86), (3.5, 98)):
        c.note("taiko", "C2", B(bar) + b, 0.5, v)
    c.hit("kick2", B(bar), 100)
    c.hit("kick2", B(bar) + 2, 90)
    c.hit("tom_lo", B(bar) + 3.5, 70)
    c.note("timp", CH[ch if isinstance(ch, str) else ch[0]][0], B(bar), 1, 92)
c.seq("tpt", THEME, B(13), 96, legato=0.95, curve=arch)
c.seq("vln", THEME, B(13), 92, legato=1.0, curve=arch)
c.seq("horn", THEME, B(13), 96, transpose=-12, legato=0.97, curve=arch)
c.seq("sitar", "r:h A5:e G5:e ~F5:e D5:e", B(16), 92)
c.bend("sitar", B(16) + 3, B(16) + 3.4, -200, 0)

# ---- BUILD bars 21-24 -----------------------------------------------------
BUILD = ["Bb", "C", "Bb", "Asus"]
for i, ch in enumerate(BUILD):
    bar = 21 + i
    harmony_bar(bar, ch, pad_vel=88 + i * 4, bass_vel=96, lowbr_vel=0, ost_vel=74 + i * 4,
                viola=True, choir_vel=70 + i * 8)
    bass = CH[ch][0]
    for b in (0, 1.5, 3):                 # 3+3+2 brass stabs
        c.chord("lowbr", [pitch(bass) + 12, pitch(bass) + 19], B(bar) + b, 0.6, 92 + i * 6)
        c.chord("horn", CH[ch][2], B(bar) + b, 0.6, 90 + i * 6)
        c.note("tuba", bass, B(bar) + b, 0.6, 92 + i * 6)
        c.note("taiko", "C2", B(bar) + b, 0.5, 105 + i * 5)
    c.hit("kick2", B(bar), 105)
c.chord("horn", ["A3", "C#4", "E4"], B(24) + 3, 1, 110)    # sus resolves to major on beat 4
c.seq("vln", "D5:h F5:h | E5:h G5:h | F5:h Bb5:h | A5:h. C#6:q", B(21), 82,
      legato=1.0, curve=lambda f: int(30 * f))
c.swell("vln", B(21), B(25), 80, 127)
for i in range(64):                       # timpani roll crescendo, D-A
    c.note("timp", "A1" if i < 48 else "A1", B(21) + i * 0.25, 0.25, 45 + i, legato=0.9)
c.hit("crash", B(24) + 2, 50, 2)
c.hit("crash", B(24) + 3, 80, 1)

# ---- TAG bars 25-28 -------------------------------------------------------
TAG = "D5:q A4:q D5:e E5:e F5:q | G5:q F5:q E5:q C#5:q | D5:w | r:w"
c.hit("crash", B(25), 115, 4)
c.hit("crash2", B(27), 120, 4)
for bar, ch in ((25, "Dm"), (26, ("Gm", "A")), (27, "Dm")):
    harmony_bar(bar, ch, pad_vel=100, bass_vel=100, lowbr_vel=100, ost_vel=80 if bar < 27 else 0,
                viola=bar < 27, choir_vel=96)
    for b, v in ((0, 124), (1.5, 90), (2, 110), (3, 95), (3.5, 105)) if bar < 27 else ((0, 127),):
        c.note("taiko", "C2", B(bar) + b, 0.5, v)
c.note("taiko", "F1", B(27), 4, 127)
c.note("timp", "D2", B(27), 4, 120)
c.seq("tpt", TAG, B(25), 110, legato=0.95)
c.seq("vln", TAG, B(25), 108, legato=1.0)
c.seq("horn", TAG, B(25), 110, transpose=-12, legato=0.97)
c.chord("pad", ["D3", "A3", "D4", "F4", "A4"], B(27), 8, 96)
c.chord("choir", ["D4", "A4", "D5"], B(27), 7, 90)
c.swell("pad", B(27), B(29), 127, 60)
c.swell("choir", B(27), B(29), 127, 50)
c.note("bass", "D1", B(27), 8, 100)
c.note("cello", "D2", B(27), 8, 95)
# sitar has the last word, floating over the held chord
c.seq("sitar", "r:h D5:e A4:e ~D5:q", B(28) - 4 + 4, 84)

# remove the placeholder note (GM kit has no reverse cymbal)
c.tracks["drums"].notes = [n for n in c.tracks["drums"].notes if n.pitch != 119]

if __name__ == "__main__":
    c.render(tail=4.5, gain=0.45)
