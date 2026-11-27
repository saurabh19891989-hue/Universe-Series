"""A1 MAIN TITLE - full 90-second version (original), developed from the approved A1.

Form (120 BPM, 4/4, 1 bar = 2 s):
  bars 1-4   intro: sitar call over the 3+3+2 ostinato (D minor)
  bars 5-12  A   : theme on horns
  bars 13-20 A'  : theme on trumpets + violins + horns, taiko
  bars 21-28 B   : contrast - relative major (F), lighter: pizzicato + harp eighths, a new
                   lyrical counter-tune on violins + flute, sitar answers, no taiko
  bars 29-32 build: C | D | C | B -> pivot to E minor (up a whole tone = 'lift')
  bars 33-40 FINAL: the tune in E minor, everything, choir
  bars 41-44 tag + last chord, sitar has the last word
Key: D minor -> F major (B) -> E minor (final statement), so the last tune sits higher
     and brighter than the first. Tempo stays 120 for the whole piece.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sulib import Cue, GM, pitch

c = Cue("A1-main-title-full-90", bpm=120, seed=111, rit=(168, 176, 96))
B = c.bar
c.track("cello", GM["cello"], 105, 50, 50)
c.track("bass", GM["contrabass"], 100, 60, 45)
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
c.track("pizz", GM["pizz"], 90, 80, 60)
c.track("harp", GM["harp"], 85, 30, 80)
c.track("flute", GM["flute"], 90, 50, 85)
c.track("drums", 0, 100, 64, 60, drums=True)

CH = {
    "Dm": ("D2", ["A3", "D4", "F4"], ["D3", "A3", "D4", "F3"]),
    "C": ("C2", ["G3", "C4", "E4"], ["C3", "G3", "C4", "E3"]),
    "F": ("F2", ["A3", "C4", "F4"], ["F2", "C3", "F3", "A2"]),
    "Bb": ("Bb1", ["Bb3", "D4", "F4"], ["Bb2", "F3", "Bb3", "D3"]),
    "Gm": ("G1", ["G3", "Bb3", "D4"], ["G2", "D3", "G3", "Bb2"]),
    "A": ("A1", ["A3", "C#4", "E4"], ["A2", "E3", "A3", "C#3"]),
    "D": ("D2", ["A3", "D4", "F#4"], ["D3", "A3", "D4", "F#3"]),
    "B": ("B1", ["B3", "D#4", "F#4"], ["B2", "F#3", "B3", "D#3"]),
    "Bsus": ("B1", ["B3", "E4", "F#4"], ["B2", "F#3", "B3", "E3"]),
    "C/E": ("E2", ["G3", "C4", "E4"], ["E2", "G2", "C3", "E3"]),
    "F/A": ("A1", ["A3", "C4", "F4"], ["A2", "C3", "F3", "A3"]),
    "Csus": ("C2", ["G3", "C4", "F4"], ["C3", "G3", "C4", "F3"]),
}
THEME_H = ["Dm", "C", "Dm", "F", "Bb", "C", ("Gm", "A"), "Dm"]
OST = [0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 1, 0, 0, 1, 3, 1]
ACC = {0, 3, 6, 8, 11, 14}
THEME = ("D5:q A4:q D5:e E5:e F5:q | E5:h. C5:q | D5:q A4:q D5:e E5:e F5:e G5:e | A5:h. r:q | "
         "Bb5:q A5:q G5:q F5:q | G5:q F5:q E5:h | F5:q E5:q D5:q C#5:q | D5:w")


def arch(f):
    return int(14 * (1 - abs(f - 0.6) / 0.6)) - 6


def bar_harm(bar, ch, tr=0, pad=None, bass=None, lowbr=None, ost=None, viola=False, choir=None):
    parts = ch if isinstance(ch, tuple) else (ch,)
    span = 4 / len(parts)
    for j, name in enumerate(parts):
        b = B(bar) + j * span
        bs, up, tones = CH[name]
        if pad:
            c.chord("pad", [pitch(p) + tr for p in up], b, span, pad)
        if choir:
            c.chord("choir", [pitch(p) + 12 + tr for p in up[1:]], b, span, choir)
        if bass:
            c.note("bass", pitch(bs) + tr, b, span, bass, legato=0.98)
        if lowbr:
            c.chord("lowbr", [pitch(bs) + 12 + tr, pitch(up[0]) + tr], b, span, lowbr)
            c.note("tuba", pitch(bs) + tr, b, span, lowbr - 8)
        if ost:
            t = [pitch(p) + tr for p in tones]
            for i in range(int(span * 4)):
                k = j * int(span * 4) + i
                c.note("cello", t[OST[k]], b + i * 0.25, 0.25, ost + (22 if k in ACC else 0), legato=0.6)
                if viola:
                    c.note("cello", t[OST[k]] + 12,   # violas double an octave up (shares the track: 15-channel limit)
                        b + i * 0.25, 0.25, ost - 12 + (18 if k in ACC else 0), legato=0.6)


def taiko_bar(bar, scale=1.0):
    for b, v in ((0, 118), (1.5, 82), (2, 104), (3, 86), (3.5, 98)):
        c.note("taiko", "C2", B(bar) + b, 0.5, int(v * scale))


# ---- intro 1-4
for bar in range(1, 5):
    bar_harm(bar, "Dm", ost=38 + bar * 6)
    c.note("bass", "D2", B(bar), 4, 55 + bar * 5)
    c.note("timp", "D2", B(bar), 1, 50 + bar * 8)
    c.note("timp", "A1", B(bar) + 2.5, 1, 40 + bar * 6)
c.chord("pad", ["A3", "D4"], 0, 16, 60)
c.swell("pad", 0, 16, 40, 100)
c.seq("sitar", "r:q D4:e A4:e ~C5:q A4:e G4:e | A4:h. r:q", 0, 88)
c.bend("sitar", 4.0, 4.35, -200, 0)
c.seq("sitar", "r:q D4:e A4:e ~C5:e D5:e C5:e A4:e | G4:q F4:q D4:h", 8, 92)
c.bend("sitar", 12.0, 12.3, 150, 0)
c.bend("sitar", 14.0, 14.4, 200, 0)
for bar in (3, 4):
    c.note("taiko", "C2", B(bar), 1, 70)
    c.note("taiko", "C2", B(bar) + 2.5, 1, 55)
c.hit("crash", B(4) + 3, 60, 1)

# ---- A 5-12: horns
for i, ch in enumerate(THEME_H):
    bar = 5 + i
    bar_harm(bar, ch, pad=62 + i * 2, bass=72, ost=55 + i * 2)
    c.note("timp", CH[ch if isinstance(ch, str) else ch[0]][0], B(bar), 1, 70)
    for b, v in ((0, 78), (1.5, 58), (2, 70)):
        c.note("taiko", "C2", B(bar) + b, 0.5, v)
c.seq("horn", THEME, B(5), 88, transpose=-12, legato=0.97, curve=arch)
c.swell("horn", B(5), B(13), 95, 120)
c.seq("sitar", "r:h D5:e C5:e A4:q", B(8), 80)

# ---- A' 13-20: full
c.hit("crash", B(13), 105, 3)
for i, ch in enumerate(THEME_H):
    bar = 13 + i
    bar_harm(bar, ch, pad=84, bass=92, lowbr=80 + i * 2, ost=68, viola=True, choir=60 + i * 2)
    taiko_bar(bar)
    c.hit("kick2", B(bar), 100)
    c.note("timp", CH[ch if isinstance(ch, str) else ch[0]][0], B(bar), 1, 92)
c.seq("tpt", THEME, B(13), 96, legato=0.95, curve=arch)
c.seq("vln", THEME, B(13), 92, legato=1.0, curve=arch)
c.seq("horn", THEME, B(13), 96, transpose=-12, legato=0.97, curve=arch)
c.seq("sitar", "r:h A5:e G5:e ~F5:e D5:e", B(16), 92)
c.bend("sitar", B(16) + 3, B(16) + 3.4, -200, 0)
c.hit("crash", B(20) + 2, 60, 2)

# ---- B 21-28: contrast in F major, lighter texture
B_H = ["F", "C/E", "Dm", "Bb", "F/A", "Gm", "C", "Csus"]
B_TUNE = ("A5:h. G5:e F5:e | G5:h E5:h | F5:q. E5:e D5:q A4:q | Bb4:h. C5:q | "
          "A4:q C5:q F5:q A5:q | G5:h. F5:e G5:e | A5:q G5:q E5:q C5:q | D5:h E5:h")
for i, ch in enumerate(B_H):
    bar = 21 + i
    bs, up, tones = CH[ch]
    c.chord("pad", up, B(bar), 4, 58)
    c.note("bass", bs, B(bar), 4, 62)
    t = [pitch(p) for p in tones]
    for k, idx in enumerate([0, 1, 2, 3, 2, 1, 2, 3]):       # pizzicato eighths
        c.note("pizz", t[idx] + 12, B(bar) + k * 0.5, 0.5, 60 + (12 if k % 4 == 0 else 0), legato=0.5)
    for k, p in enumerate(up + [pitch(up[1]) + 12]):          # harp ripple on 1
        c.note("harp", p, B(bar) + k * 0.25, 2, 56)
    c.chord("horn", [pitch(p) - 12 for p in up[1:]], B(bar), 4, 50)
c.swell("pad", B(21), B(29), 70, 95)
c.seq("vln", B_TUNE, B(21), 80, legato=1.0, curve=arch)
c.seq("flute", B_TUNE, B(21), 72, legato=1.0, curve=arch)
for bar, phr in ((22, "r:h. ~C6:e A5:e"), (24, "r:h F5:e G5:e ~A5:q"), (26, "r:h. D6:e C6:e")):
    c.seq("sitar", phr, B(bar), 78)
c.bend("sitar", B(24) + 3, B(24) + 3.3, -200, 0)
c.hit("tri", B(21), 50, 1)
c.hit("tri", B(25), 50, 1)

# ---- build 29-32: pivot to E minor
BUILD = ["C", "D", "C", "Bsus"]
for i, ch in enumerate(BUILD):
    bar = 29 + i
    bar_harm(bar, ch, pad=86 + i * 4, bass=94, ost=72 + i * 4, viola=True, choir=66 + i * 8)
    bs = CH[ch][0]
    for b in (0, 1.5, 3):
        c.chord("lowbr", [pitch(bs) + 12, pitch(bs) + 19], B(bar) + b, 0.6, 90 + i * 6)
        c.chord("horn", CH[ch][1], B(bar) + b, 0.6, 88 + i * 6)
        c.note("tuba", bs, B(bar) + b, 0.6, 90 + i * 6)
        c.note("taiko", "C2", B(bar) + b, 0.5, 100 + i * 6)
    c.hit("kick2", B(bar), 104)
c.chord("horn", ["B3", "D#4", "F#4"], B(32) + 3, 1, 112)
c.seq("vln", "E5:h G5:h | F#5:h A5:h | G5:h C6:h | B5:h. D#6:q", B(29), 82,
      legato=1.0, curve=lambda f: int(30 * f))
c.swell("vln", B(29), B(33), 80, 127)
for i in range(64):
    c.note("timp", "B1", B(29) + i * 0.25, 0.25, 45 + i, legato=0.9)
c.hit("crash", B(32) + 3, 80, 1)

# ---- FINAL 33-40: the tune in E minor (+2), everything
c.hit("crash", B(33), 118, 4)
c.note("taiko", "F1", B(33), 2, 124)
for i, ch in enumerate(THEME_H):
    bar = 33 + i
    bar_harm(bar, ch, tr=2, pad=100, bass=100, lowbr=96, ost=78, viola=True, choir=88)
    taiko_bar(bar, 1.05)
    c.hit("kick2", B(bar), 110)
    c.hit("kick2", B(bar) + 2, 96)
    c.note("timp", pitch(CH[ch if isinstance(ch, str) else ch[0]][0]) + 2, B(bar), 1, 104)
c.seq("tpt", THEME, B(33), 108, transpose=2, legato=0.95, curve=arch)
c.seq("vln", THEME, B(33), 106, transpose=2, legato=1.0, curve=arch)
c.seq("flute", THEME, B(33), 90, transpose=14, legato=1.0, curve=arch)
c.seq("horn", THEME, B(33), 110, transpose=-10, legato=0.97, curve=arch)
c.seq("sitar", "r:h B5:e A5:e ~G5:e E5:e", B(36), 96)
c.hit("crash", B(37), 100, 3)

# ---- TAG 41-44
TAG = "E5:q B4:q E5:e F#5:e G5:q | A5:q G5:q F#5:q D#5:q | E5:w | r:w"
c.hit("crash", B(41), 112, 4)
c.hit("crash2", B(43), 122, 4)
for bar, ch in ((41, "Dm"), (42, ("Gm", "A")), (43, "Dm")):
    bar_harm(bar, ch, tr=2, pad=104, bass=104, lowbr=104, ost=82 if bar < 43 else 0,
             viola=bar < 43, choir=98)
    if bar < 43:
        taiko_bar(bar, 1.08)
c.note("taiko", "F1", B(43), 4, 127)
c.note("timp", "E2", B(43), 4, 122)
c.seq("tpt", TAG, B(41), 112, legato=0.95)
c.seq("vln", TAG, B(41), 110, legato=1.0)
c.seq("horn", TAG, B(41), 112, transpose=-12, legato=0.97)
c.chord("pad", ["E3", "B3", "E4", "G4", "B4"], B(43), 8, 98)
c.chord("choir", ["E4", "B4", "E5"], B(43), 7, 92)
c.swell("pad", B(43), B(45), 127, 60)
c.swell("choir", B(43), B(45), 127, 50)
c.note("bass", "E1", B(43), 8, 100)
c.note("cello", "E2", B(43), 8, 96)
c.seq("sitar", "r:h E5:e B4:e ~E5:q", B(44), 86)

if __name__ == "__main__":
    c.render(tail=3.5, gain=0.45)
