#!/usr/bin/env python3
"""Screens the edit needs that the data-visual set does not have yet, drawn with the data-visual
library (same amber terminal look as PIP's reports) so they sit beside the real clips.

  python3 production/tools/edit/make_extra_visuals.py [OUT_DIR]

Writes: edit_jobcard_typing.mp4 (the job card types on; FEE stays blank, cursor blinking),
edit_jobcard_fee.mp4 (the same card with the fee filled in: 182,417.36 = the lien on the ship),
edit_control_feed.mp4 + edit_control_feed_matte.png (Rim Port control radio-video frame; the
officer's still goes through the matte in the edit). Temporary: replace with data-visual clips.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "datavis"))
import dvlib
from dvlib import W, H, canvas, text, font, typed, mul, tlen, ClipSpec

AMBER = (255, 178, 46)
TEAL = (110, 230, 200)
FEE = "182,417.36"
ROWS = [("ONE PARCEL", 2.2), ("SEALED · PREPAID", 3.0), ("TO  SHACKLETON CRATER", 4.1), ("BY  18:00", 5.3)]


def _card(t, fee_shown, static=False):
    img, d = canvas()
    A = AMBER
    d.rounded_rectangle([60, 60, W - 60, H - 60], radius=26, outline=mul(A, 0.55), width=3)
    fs = font("vt323", 40)
    text(d, (110, 100), "PIP // POSTAL AUDIT UNIT", fs, mul(A, 0.75), track=4)
    text(d, (W - 110, 100), "JOB BOARD · DIRECT POST", fs, mul(A, 0.55), "ra", track=4)
    d.line([(100, 160), (W - 100, 160)], fill=mul(A, 0.4), width=2)
    f = font("vt323", 96)
    fh = font("vt323", 64)
    head = "NEW JOB — POSTED TO US DIRECTLY"
    text(d, (110, 200), head if static else typed(head, t, 0.6, 40), fh, mul(A, 0.8))
    y = 300
    for s, t0 in ROWS:
        text(d, (110, y), s if static else typed(s, t, t0, 34), f, A)
        y += 112
    lab = "FEE  "
    t_fee = 6.3
    shown = lab if static else typed(lab, t, t_fee, 30)
    text(d, (110, y), shown, f, A)
    x = 110 + tlen(f, lab)
    if fee_shown:
        text(d, (x, y), FEE, f, (255, 222, 150))
    elif (static or t > t_fee + 0.3) and int(t * 2.2) % 2 == 0:
        d.rectangle([x + 4, y + 16, x + 44, y + 84], fill=A)
    text(d, (110, H - 130), "SENDER: —        PREPAID: YES", font("vt323", 38), mul(A, 0.55), track=4)
    return img


def _feed(t, i, alpha=False):
    img, d = canvas()
    C = TEAL
    d.rounded_rectangle([60, 60, W - 60, H - 60], radius=22, outline=mul(C, 0.5), width=3)
    fs = font("sharetech", 40)
    text(d, (110, 96), "RIM PORT CONTROL", fs, mul(C, 0.9), track=5)
    text(d, (W - 110, 96), "APPROACH · CH 9", fs, mul(C, 0.6), "ra", track=5)
    d.line([(100, 158), (W - 100, 158)], fill=mul(C, 0.4), width=2)
    x0, y0, x1, y1 = FEED_BOX
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=mul(C, 0.7), width=3)
    d.rectangle([x0, y0, x1, y1], fill=(16, 30, 30))
    if int(t * 1.6) % 2 == 0:
        d.ellipse([x0 + 24, y0 + 24, x0 + 48, y0 + 48], fill=(255, 80, 70))
    text(d, (x0 + 62, y0 + 16), "VOICE + PICTURE", font("sharetech", 34), (235, 240, 235))
    fr = font("sharetech", 44)
    text(d, (x1 + 60, y0 + 10), "OFFICER", font("sharetech", 30), mul(C, 0.6), track=4)
    text(d, (x1 + 60, y0 + 54), "I. MAMANI", fr, C)
    text(d, (x1 + 60, y0 + 190), "BAY", font("sharetech", 30), mul(C, 0.6), track=4)
    text(d, (x1 + 60, y0 + 234), "NINE", fr, C)
    text(d, (x1 + 60, y0 + 370), "HOLD", font("sharetech", 30), mul(C, 0.6), track=4)
    text(d, (x1 + 60, y0 + 414), "SEALED", fr, (255, 190, 90) if int(t * 2) % 2 == 0 else mul(C, 0.8))
    text(d, (110, H - 128), "ATLAS NOTICE 14:02 — DESTINATION WITHDRAWN", font("sharetech", 36), mul(C, 0.6), track=3)
    return img


FEED_BOX = (110, 200, 1250, 880)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/work/ed/dv"
    os.makedirs(out, exist_ok=True)
    specs = [
        ClipSpec("edit_jobcard_typing", 12.0, lambda t, i, alpha=False: _card(t, False), "amber", alpha=False, prores=False),
        ClipSpec("edit_jobcard_fee", 8.0, lambda t, i, alpha=False: _card(t, True, static=True), "amber", alpha=False, prores=False),
        ClipSpec("edit_control_feed", 10.0, _feed, "teal", alpha=False, prores=False, matte=[FEED_BOX]),
    ]
    for s in specs:
        dvlib.render(s, out)
        print("wrote", s.name)


if __name__ == "__main__":
    main()
