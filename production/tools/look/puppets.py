#!/usr/bin/env python3
"""Route 3: code-built vector cut-out puppets (100% owned artwork).

Each character is a parametric SVG rig rendered with cairosvg, then finished in numpy with
a two-colour rim light (orange key-rim, teal fill-rim) and a soft contact shadow.

State keys (all optional):
  expr   : 'smirk' | 'worried' | 'angry'  (brows, lids, default mouth)
  mouth  : 'rest' | 'AI' | 'E' | 'O' | 'U' | 'MBP' | 'FV' | 'L'   (8 lip-sync visemes)
  blink  : 0..1 (1 = closed)
  look   : (dx, dy) pupil offset in px
  head   : head tilt in degrees
  breathe: 0..1 (torso scale / shoulder rise)
  arm_l, arm_r : arm swing degrees

Usage: puppets.py sheet OUTDIR   -> renders rig parts + expression sheets
"""
import io, math, random, sys
import numpy as np
from PIL import Image, ImageFilter
import cairosvg

NAVY = "#0b1530"; INK = "#0a0f1f"; ORANGE = "#d0601f"; TEAL = "#1e8c8a"; CREAM = "#f2e7cf"

VISEMES = ["rest", "AI", "E", "O", "U", "MBP", "FV", "L"]


def lg(id_, stops, x1=0, y1=0, x2=1, y2=0):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(id_, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


# ---------------------------------------------------------------- JAX ----
SKIN, SKIN_SH, SKIN_HI = "#9a6442", "#5f3923", "#c08860"
HAIR, HAIR_HI = "#17131a", "#3a2c35"
JACKET, JACKET_SH, JACKET_HI = "#c4561c", "#7e2f10", "#ec8a45"

FACE = ("M318,238 C316,282 322,330 336,362 C348,388 372,406 398,410 C426,410 450,392 464,364 "
        "C478,332 484,284 482,238 C470,196 430,176 400,176 C366,176 330,196 318,238 Z")


def jax_mouth(v, expr):
    """Return SVG for mouth at centre (402,366). Crooked: right corner higher."""
    lip = SKIN_SH
    dark = "#2a0f0c"; teeth = CREAM; tongue = "#b4493f"
    if v == "rest":
        if expr == "smirk":
            return (f'<path d="M378,368 C392,374 410,372 430,356" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
                    f'<path d="M427,352 C433,354 434,360 431,363" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        if expr == "angry":
            return f'<path d="M380,370 C394,364 412,364 426,368" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        return f'<path d="M382,372 C394,366 410,366 424,370" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
    if v == "MBP":
        return (f'<path d="M378,366 C392,370 412,370 428,362" fill="none" stroke="{INK}" stroke-width="5.5" stroke-linecap="round"/>'
                f'<path d="M386,374 C398,378 410,378 420,373" fill="none" stroke="{lip}" stroke-width="3" stroke-linecap="round"/>')
    shapes = {
        "AI": ("M376,360 C390,356 414,354 430,352 C428,376 414,392 402,392 C388,392 378,378 376,360 Z", True, True),
        "E": ("M372,362 C390,356 414,354 434,352 C430,368 416,376 402,376 C386,376 376,370 372,362 Z", True, False),
        "O": ("M388,356 C396,350 412,350 418,356 C424,366 420,384 404,386 C390,386 384,368 388,356 Z", False, True),
        "U": ("M394,360 C398,356 408,356 412,360 C414,368 410,374 403,374 C396,374 392,368 394,360 Z", False, False),
        "FV": ("M378,362 C392,358 414,356 430,354 C426,366 414,372 402,372 C390,372 380,368 378,362 Z", True, False),
        "L": ("M378,360 C392,356 414,354 430,352 C428,372 414,384 402,384 C388,384 378,374 378,360 Z", True, True),
    }
    d, show_teeth, show_tongue = shapes[v]
    out = f'<clipPath id="mclip"><path d="{d}"/></clipPath><path d="{d}" fill="{dark}"/>'
    g = '<g clip-path="url(#mclip)">'
    if show_teeth:
        g += f'<rect x="370" y="348" width="70" height="{11 if v != "FV" else 9}" fill="{teeth}"/>'
    if v == "FV":
        g += f'<path d="M376,368 C392,362 414,360 432,358 L432,380 L376,380 Z" fill="{SKIN_HI}"/>'
    if show_tongue:
        g += f'<ellipse cx="404" cy="{392 if v != "L" else 372}" rx="16" ry="{11 if v != "L" else 8}" fill="{tongue}"/>'
    g += "</g>"
    out += g + f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
    # lower-lip shading
    out += f'<path d="M388,{392 if v in ("AI", "L", "O") else 380} q14,6 26,-2" fill="none" stroke="{lip}" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
    return out


def jax_eye(cx, cy, blink, look, expr, side):
    w, h = 22, 10.5
    lx, ly = look
    sq = {"smirk": 0.22 if side == "R" else 0.08, "worried": -0.15, "angry": 0.3}[expr]
    top = cy - h * (1 - max(0, min(1, blink + sq)))
    s = (f'<clipPath id="ec{side}"><path d="M{cx-w},{cy} Q{cx},{cy-h*1.9} {cx+w},{cy-1} Q{cx},{cy+h*1.5} {cx-w},{cy} Z"/></clipPath>'
         f'<path d="M{cx-w},{cy} Q{cx},{cy-h*1.9} {cx+w},{cy-1} Q{cx},{cy+h*1.5} {cx-w},{cy} Z" fill="{CREAM}"/>'
         f'<g clip-path="url(#ec{side})"><circle cx="{cx+lx}" cy="{cy+ly}" r="9.5" fill="#4a2a16"/>'
         f'<circle cx="{cx+lx}" cy="{cy+ly}" r="9.5" fill="none" stroke="#24120a" stroke-width="2"/>'
         f'<circle cx="{cx+lx}" cy="{cy+ly}" r="4" fill="#0a0604"/>'
         f'<circle cx="{cx+lx+3}" cy="{cy+ly-3}" r="2.2" fill="#fff"/>'
         # eyelid (skin) descending for blink / squint
         f'<rect x="{cx-w-2}" y="{cy-h*2.2}" width="{2*w+4}" height="{(top-(cy-h*2.2))+h*0.9}" fill="{SKIN}"/>'
         f'<path d="M{cx-w-2},{cy+h*1.5} L{cx+w+2},{cy+h*1.5} L{cx+w+2},{cy+h*1.6+2} L{cx-w-2},{cy+h*1.6+2} Z" fill="{SKIN}"/></g>')
    # upper lid line follows lid height
    yl = top + h * 0.9 - 1
    if blink > 0.85:
        s += f'<path d="M{cx-w-2},{cy+1} Q{cx},{cy+6} {cx+w+2},{cy}" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    else:
        s += (f'<path d="M{cx-w-3},{cy+1} Q{cx},{min(yl, cy) - 6} {cx+w+3},{cy-2}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
              f'<path d="M{cx-w+4},{cy+h*0.9} Q{cx},{cy+h*1.3} {cx+w-3},{cy+h*0.7}" fill="none" stroke="{SKIN_SH}" stroke-width="2" stroke-linecap="round"/>')
    return s


def jax_brows(expr):
    # (inner_y, outer_y) offsets for L and R
    cfg = {"smirk": ((-2, 0), (-8, -4)), "worried": ((-12, 2), (-12, 2)), "angry": ((10, -4), (10, -4))}[expr]
    (li, lo), (ri, ro) = cfg
    b = 262
    L = f"M346,{b+lo} Q366,{b-10+min(li,lo)} 390,{b+li} L390,{b+li+8} Q368,{b+2+min(li,lo)} 348,{b+lo+7} Z"
    R = f"M412,{b+ri} Q436,{b-10+min(ri,ro)} 458,{b+ro} L456,{b+ro+7} Q434,{b+2+min(ri,ro)} 412,{b+ri+8} Z"
    return f'<path d="{L}" fill="{HAIR}"/><path d="{R}" fill="{HAIR}"/>'


def stubble_dots(seed=3):
    rnd = random.Random(seed)
    out = []
    for _ in range(420):
        x = rnd.uniform(330, 472); y = rnd.uniform(330, 410)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(.7, 1.5):.1f}"/>')
    return "".join(out)


def jax_svg(st):
    expr = st.get("expr", "smirk"); mouth = st.get("mouth", "rest"); blink = st.get("blink", 0)
    look = st.get("look", (0, 0)); tilt = st.get("head", 0); br = st.get("breathe", 0)
    arm_l = st.get("arm_l", 0); arm_r = st.get("arm_r", 0)
    W, H = 800, 1000
    defs = (lg("gSkin", [(0, SKIN_HI), (.45, SKIN), (1, SKIN_SH)])
            + lg("gJacket", [(0, JACKET_HI), (.35, JACKET), (1, JACKET_SH)])
            + lg("gJacketV", [(0, JACKET), (1, "#5c220c")], 0, 0, 0, 1)
            + lg("gTee", [(0, "#2aa5a0"), (1, "#0f4f55")])
            + lg("gHair", [(0, HAIR_HI), (1, HAIR)], 0, 0, 0, 1)
            + f'<clipPath id="faceclip"><path d="{FACE}"/></clipPath>')
    sy = 1 + 0.012 * br
    torso = f'<g transform="translate(400,1000) scale(1,{sy}) translate(-400,-1000) translate(0,{-3*br})">'
    # arms (sleeves) behind torso edge
    def arm(side, ang):
        sx = 238 if side == "L" else 562
        d = (f"M{sx+10},{500} C{sx-40},{520} {sx-58},{640} {sx-62},{760} C{sx-64},{860} {sx-56},{940} {sx-50},{1000} L{sx+22},{1000} C{sx+20},{900} {sx+24},{780} {sx+30},{640} Z"
             if side == "L" else
             f"M{sx-10},{500} C{sx+40},{520} {sx+58},{640} {sx+62},{760} C{sx+64},{860} {sx+56},{940} {sx+50},{1000} L{sx-22},{1000} C{sx-20},{900} {sx-24},{780} {sx-30},{640} Z")
        cuff = (f'<path d="M{sx-56},{880} q46,14 92,0" fill="none" stroke="{JACKET_SH}" stroke-width="5"/>' if side == "L"
                else f'<path d="M{sx-36},{880} q46,14 92,0" fill="none" stroke="{JACKET_SH}" stroke-width="5"/>')
        pocket = (f'<rect x="{sx-50 if side=="L" else sx+6}" y="640" width="44" height="52" rx="5" fill="{JACKET_SH}" opacity=".55"/>'
                  f'<path d="M{sx-52 if side=="L" else sx+4},{640} h48 v14 h-48 z" fill="{JACKET}" stroke="{INK}" stroke-width="3"/>')
        return (f'<g transform="rotate({ang} {sx} 520)"><path d="{d}" fill="url(#gJacket)" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
                f'{pocket}{cuff}'
                f'<path d="M{sx-20},{600} q-14,60 -4,120 M{sx+10},{720} q10,50 0,110" fill="none" stroke="{JACKET_SH}" stroke-width="3" opacity=".8"/></g>')
    body = arm("L", arm_l) + arm("R", -arm_r)
    jacket = ("M250,500 C290,470 340,452 372,446 L428,446 C460,452 510,470 550,500 "
              "C582,560 590,700 600,1000 L200,1000 C210,700 218,560 250,500 Z")
    body += f'<path d="{jacket}" fill="url(#gJacket)" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    # shadow side of jacket (cel)
    body += f'<path d="M470,470 C520,490 552,520 560,560 C580,700 586,860 592,1000 L520,1000 C510,860 500,700 470,470 Z" fill="{JACKET_SH}" opacity=".55"/>'
    # tee V
    body += f'<path d="M362,452 L438,452 L420,600 L400,640 L380,600 Z" fill="url(#gTee)" stroke="{INK}" stroke-width="4"/>'
    # jacket front edges / zipper
    body += (f'<path d="M362,452 C350,560 360,760 372,1000" fill="none" stroke="{INK}" stroke-width="5"/>'
             f'<path d="M438,452 C452,560 446,760 436,1000" fill="none" stroke="{INK}" stroke-width="5"/>'
             f'<path d="M436,470 C448,580 444,760 434,1000" fill="none" stroke="#e9c27a" stroke-width="3" stroke-dasharray="4 5"/>')
    # chest pockets with flaps + buttons (too many pockets)
    for (x, y, w, h) in [(270, 600, 84, 96), (452, 600, 84, 96), (282, 760, 70, 80), (458, 760, 70, 80), (300, 530, 46, 40)]:
        body += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{JACKET_SH}" opacity=".45"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{INK}" stroke-width="3.5"/>'
                 f'<path d="M{x-3},{y} h{w+6} l-6,{h*0.26} h-{w-6} z" fill="{JACKET}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
                 f'<circle cx="{x+w/2}" cy="{y+h*0.2}" r="4" fill="#e0b25a" stroke="{INK}" stroke-width="2"/>')
    # rumple folds
    body += (f'<path d="M260,560 q40,30 80,10 M300,900 q30,-20 60,6 M470,880 q40,-26 90,4 M520,540 q-20,40 -60,40" '
             f'fill="none" stroke="{JACKET_SH}" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
             f'<path d="M262,520 q30,-30 80,-46" fill="none" stroke="{JACKET_HI}" stroke-width="5" stroke-linecap="round" opacity=".8"/>')
    # neck
    neck = (f'<path d="M370,392 L372,460 Q400,476 428,460 L430,392 Z" fill="{SKIN_SH}" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M372,440 Q400,452 428,440" fill="none" stroke="#3d2215" stroke-width="3" opacity=".6"/>')
    # popped collar
    collar = (f'<path d="M372,446 C340,440 300,452 268,482 C292,500 318,520 344,560 C352,520 360,480 380,460 Z" fill="url(#gJacketV)" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
              f'<path d="M428,446 C460,440 500,452 532,482 C508,500 482,520 456,560 C448,520 440,480 420,460 Z" fill="{JACKET_SH}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    torso_svg = torso + body + "</g>"
    # ---- head group
    hx, hy = 400, 410
    head = f'<g transform="rotate({tilt} {hx} {hy}) translate(400,440) scale(1.17) translate(-400,-420)">'
    # back hair
    head += (f'<path d="M300,250 C286,180 330,124 400,120 C476,118 520,170 506,250 C500,290 490,300 484,300 '
             f'L482,240 L318,240 L314,300 C306,296 302,280 300,250 Z" fill="{HAIR}" stroke="{INK}" stroke-width="5"/>')
    # ears
    head += (f'<path d="M322,282 C302,272 298,306 310,322 C316,332 326,332 330,326 Z" fill="{SKIN}" stroke="{INK}" stroke-width="4.5"/>'
             f'<path d="M478,282 C498,272 502,306 490,322 C484,332 474,332 470,326 Z" fill="{SKIN_SH}" stroke="{INK}" stroke-width="4.5"/>')
    # face
    head += f'<path d="{FACE}" fill="url(#gSkin)"/>'
    head += '<g clip-path="url(#faceclip)">'
    # cel shadow on far side + under-brow + cheekbone
    head += (f'<path d="M440,180 C470,230 470,300 452,350 C440,380 420,404 398,412 L500,412 L500,180 Z" fill="{SKIN_SH}" opacity=".55"/>'
             f'<path d="M330,330 C350,350 360,346 372,338" fill="none" stroke="{SKIN_SH}" stroke-width="4" opacity=".6"/>'
             f'<path d="M310,250 C360,262 440,262 490,250 L490,240 L310,240 Z" fill="{SKIN_SH}" opacity=".35"/>')
    # stubble: tone + dots
    head += (f'<path d="M318,330 C340,320 372,346 400,344 C428,346 460,320 484,330 L484,420 L318,420 Z" fill="#3b2216" opacity=".32"/>'
             f'<g fill="#2a160e" opacity=".55">{stubble_dots()}</g>'
             f'<path d="M376,350 C390,346 414,344 430,346 L432,354 C414,352 390,354 376,358 Z" fill="#2a160e" opacity=".35"/>')
    head += "</g>"
    head += f'<path d="{FACE}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    # nose
    head += (f'<path d="M398,292 C396,312 390,326 386,334 C392,342 404,344 414,338" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
             f'<path d="M412,300 C414,316 418,328 416,336" fill="none" stroke="{SKIN_SH}" stroke-width="4" opacity=".8" stroke-linecap="round"/>'
             f'<path d="M398,300 C396,312 394,320 392,326" fill="none" stroke="{SKIN_HI}" stroke-width="3" opacity=".8"/>')
    # eyes, brows, mouth
    head += jax_eye(370, 290, blink, look, expr, "L") + jax_eye(432, 290, blink, look, expr, "R")
    head += jax_brows(expr)
    if expr == "worried":
        head += f'<path d="M392,252 q8,6 16,0" fill="none" stroke="{SKIN_SH}" stroke-width="3"/>'
    if expr == "angry":
        head += f'<path d="M396,262 l4,14 M406,262 l-2,14" stroke="{SKIN_SH}" stroke-width="3"/>'
    head += jax_mouth(mouth, expr)
    # smile line / nasolabial
    head += f'<path d="M372,346 C366,356 366,368 372,378" fill="none" stroke="{SKIN_SH}" stroke-width="3" opacity=".8"/>'
    head += f'<path d="M434,340 C442,350 444,362 438,374" fill="none" stroke="{SKIN_SH}" stroke-width="3" opacity=".8"/>'
    # front messy hair locks
    head += (f'<path d="M312,250 C300,170 360,130 420,136 C470,140 510,176 494,246 C484,222 470,206 452,200 '
             f'C458,222 450,236 444,244 C436,222 420,206 400,204 C404,224 396,240 384,250 C380,230 372,214 356,208 '
             f'C352,232 340,246 326,258 C328,238 324,232 318,230 Z" fill="url(#gHair)" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M352,150 C380,140 420,138 446,150 M372,176 q30,-18 66,-6 M330,196 q14,-24 34,-34" fill="none" stroke="#5a4552" stroke-width="3" stroke-linecap="round" opacity=".9"/>'
             f'<path d="M420,136 C440,118 470,116 484,124 C470,126 458,134 452,142 Z" fill="{HAIR}" stroke="{INK}" stroke-width="4"/>')
    head += "</g>"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{defs}</defs>{torso_svg}{neck}{collar}{head}</svg>')


# ---------------------------------------------------------------- PIP ----
BRASS, BRASS_SH, BRASS_HI = "#b8893a", "#6e4a1a", "#f0cf7e"
ENAMEL, ENAMEL_SH = "#efe4c8", "#b8a888"
AMBER = "#ffb02e"


def pip_svg(st):
    expr = st.get("expr", "smirk"); mouth = st.get("mouth", "rest"); blink = st.get("blink", 0)
    look = st.get("look", (0, 0)); tilt = st.get("head", 0); br = st.get("breathe", 0)
    stamp = st.get("arm_r", 0)
    W, H = 600, 760
    bob = -8 * br
    defs = (lg("gBrass", [(0, BRASS_HI), (.4, BRASS), (1, BRASS_SH)])
            + lg("gBrassV", [(0, BRASS_HI), (.5, BRASS), (1, BRASS_SH)], 0, 0, 0, 1)
            + lg("gEnamel", [(0, "#fffaf0"), (.5, ENAMEL), (1, ENAMEL_SH)])
            + rg("gLens", [(0, "#fff4c0", 1), (.25, AMBER, 1), (.7, "#c25a0a", 1), (1, "#3a1404", 1)], .5, .5, .5, .42, .38)
            + rg("gGlow", [(0, AMBER, .55), (1, AMBER, 0)])
            + rg("gThr", [(0, "#9ff6ee", .9), (.4, TEAL, .5), (1, TEAL, 0)]))
    s = f'<g transform="translate(0,{bob})">'
    # thruster glow under base
    s += f'<ellipse cx="300" cy="640" rx="70" ry="34" fill="url(#gThr)"/>'
    # stamp arm (behind base on right)
    sx, sy = 410, 560
    s += (f'<g transform="rotate({-stamp} {sx} {sy})">'
          f'<path d="M{sx},{sy} L{sx+80},{sy+40}" stroke="{BRASS_SH}" stroke-width="16" stroke-linecap="round"/>'
          f'<path d="M{sx},{sy} L{sx+80},{sy+40}" stroke="url(#gBrass)" stroke-width="10" stroke-linecap="round"/>'
          f'<circle cx="{sx+80}" cy="{sy+40}" r="11" fill="url(#gBrass)" stroke="{INK}" stroke-width="4"/>'
          f'<path d="M{sx+80},{sy+40} L{sx+96},{sy+100}" stroke="url(#gBrass)" stroke-width="10" stroke-linecap="round"/>'
          f'<ellipse cx="{sx+97}" cy="{sy+92}" rx="14" ry="18" fill="#7a3d1c" stroke="{INK}" stroke-width="4"/>'
          f'<rect x="{sx+72}" y="{sy+104}" width="50" height="16" rx="3" fill="{BRASS}" stroke="{INK}" stroke-width="4"/>'
          f'<rect x="{sx+74}" y="{sy+120}" width="46" height="9" fill="#8e1f1f" stroke="{INK}" stroke-width="3"/></g>')
    # base: squat postal-scale cylinder
    s += (f'<path d="M180,520 L180,600 C180,630 420,630 420,600 L420,520 Z" fill="url(#gBrass)" stroke="{INK}" stroke-width="6"/>'
          f'<ellipse cx="300" cy="520" rx="120" ry="30" fill="url(#gBrassV)" stroke="{INK}" stroke-width="6"/>'
          f'<path d="M184,578 C200,604 400,604 416,578" fill="none" stroke="{BRASS_SH}" stroke-width="5"/>')
    # enamel dial face with needle (needle = mood / talk)
    needle = {"smirk": -20, "worried": 40, "angry": -60}[expr] + {"rest": 0, "AI": 25, "E": 15, "O": 20, "U": 8, "MBP": -4, "FV": 10, "L": 14}[mouth]
    s += (f'<circle cx="300" cy="572" r="38" fill="url(#gEnamel)" stroke="{INK}" stroke-width="5"/>'
          + "".join(f'<path d="M{300+30*math.cos(math.radians(a))},{572+30*math.sin(math.radians(a))} L{300+35*math.cos(math.radians(a))},{572+35*math.sin(math.radians(a))}" stroke="{INK}" stroke-width="2.5"/>' for a in range(-200, 21, 22))
          + f'<path d="M300,572 L{300+30*math.cos(math.radians(-90+needle))},{572+30*math.sin(math.radians(-90+needle))}" stroke="#9e1f1f" stroke-width="4" stroke-linecap="round"/>'
          f'<circle cx="300" cy="572" r="5" fill="{INK}"/>')
    # voice grille: 8 visemes as lit slots
    lit = {"rest": 0, "MBP": 1, "U": 2, "FV": 3, "E": 4, "L": 4, "O": 5, "AI": 6}[mouth]
    for i in range(7):
        x = 228 + i * 0 if False else 0
    for i, dx in enumerate([-3, -2, -1, 0, 1, 2, 3]):
        on = abs(dx) < (lit + 1) / 2 and lit > 0
        hgt = 14 - abs(dx) * 2
        col = AMBER if on else "#3a2a18"
        s += f'<rect x="{248+dx*0+ (dx+3)*8 - 4}" y="{604-hgt/2}" width="5" height="{hgt}" rx="2" fill="{col}"/>' if False else ""
    for i, dx in enumerate([-3, -2, -1, 0, 1, 2, 3]):
        on = lit > 0 and abs(dx) <= (lit - 1) / 2 + 0.01
        col = AMBER if on else "#3a2a18"
        hgt = 12 - abs(dx) * 2
        s += f'<rect x="{360 + dx*9 - 2.5}" y="{560-hgt/2}" width="5" height="{hgt}" rx="2" fill="{col}" stroke="{INK}" stroke-width="1"/>'
    s += f'<rect x="327" y="548" width="66" height="24" rx="5" fill="none" stroke="{INK}" stroke-width="3"/>'
    # lamp arm: base -> elbow -> head
    s += (f'<path d="M290,500 L360,370 L300,262" fill="none" stroke="{INK}" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>'
          f'<path d="M290,500 L360,370 L300,262" fill="none" stroke="url(#gBrass)" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>'
          f'<path d="M306,490 L370,378" fill="none" stroke="{BRASS_SH}" stroke-width="3" stroke-dasharray="3 4"/>'
          f'<circle cx="360" cy="370" r="15" fill="url(#gBrass)" stroke="{INK}" stroke-width="5"/><circle cx="360" cy="370" r="5" fill="{INK}"/>'
          f'<circle cx="290" cy="500" r="13" fill="url(#gBrass)" stroke="{INK}" stroke-width="5"/>')
    # head: lamp shade (enamel cone) facing camera, with amber lens
    hx, hy = 290, 230
    s += f'<g transform="rotate({tilt} 300 262)">'
    s += f'<circle cx="{hx}" cy="{hy}" r="130" fill="url(#gGlow)"/>'
    # cone of the lamp shade receding to the upper right, with a brass end-cap
    s += (f'<path d="M{hx-60},{hy-64} L{hx+70},{hy-132} C{hx+104},{hy-128} {hx+124},{hy-96} {hx+122},{hy-62} L{hx+66},{hy+58} Z" '
          f'fill="url(#gEnamel)" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
          f'<path d="M{hx+10},{hy-90} L{hx+92},{hy-120}" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".85"/>'
          f'<ellipse cx="{hx+98}" cy="{hy-100}" rx="22" ry="34" transform="rotate(35 {hx+98} {hy-100})" fill="url(#gBrass)" stroke="{INK}" stroke-width="5"/>')
    s += f'<circle cx="{hx}" cy="{hy}" r="84" fill="url(#gEnamel)" stroke="{INK}" stroke-width="6"/>'
    s += f'<path d="M{hx+40},{hy-70} A84,84 0 0 1 {hx+60},{hy+58}" fill="none" stroke="{ENAMEL_SH}" stroke-width="12" opacity=".8"/>'
    s += f'<path d="M{hx-66},{hy-44} A80,80 0 0 1 {hx-10},{hy-80}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".9"/>'
    # brass bezel
    s += f'<circle cx="{hx}" cy="{hy}" r="62" fill="url(#gBrass)" stroke="{INK}" stroke-width="6"/>'
    s += "".join(f'<circle cx="{hx+55*math.cos(math.radians(a))}" cy="{hy+55*math.sin(math.radians(a))}" r="3" fill="{BRASS_SH}"/>' for a in range(0, 360, 30))
    s += f'<circle cx="{hx}" cy="{hy}" r="46" fill="#1a0c04" stroke="{INK}" stroke-width="4"/>'
    lx, ly = look
    s += (f'<clipPath id="lensclip"><circle cx="{hx}" cy="{hy}" r="44"/></clipPath><g clip-path="url(#lensclip)">'
          f'<circle cx="{hx+lx}" cy="{hy+ly}" r="38" fill="url(#gLens)"/>'
          f'<circle cx="{hx+lx}" cy="{hy+ly}" r="26" fill="none" stroke="#7a2e06" stroke-width="2" opacity=".8"/>'
          f'<circle cx="{hx+lx}" cy="{hy+ly}" r="{9 if expr != "worried" else 6}" fill="#2a0c02"/>'
          f'<circle cx="{hx+lx-12}" cy="{hy+ly-14}" r="7" fill="#fff8e0" opacity=".9"/>'
          f'<circle cx="{hx+lx+10}" cy="{hy+ly+12}" r="3" fill="#fff8e0" opacity=".6"/>')
    # aperture lids (expressions + blink)
    top = {"smirk": 0.42, "worried": 0.0, "angry": 0.55}[expr]
    bot = {"smirk": 0.12, "worried": 0.0, "angry": 0.35}[expr]
    top = top + (1 - top) * blink; bot = bot + (1 - bot) * blink * 0.9
    ang = {"smirk": 6, "worried": -14, "angry": -18}[expr]
    s += (f'<g transform="rotate({ang} {hx} {hy})"><rect x="{hx-60}" y="{hy-60}" width="120" height="{16 + 92*top}" fill="url(#gBrassV)" stroke="{INK}" stroke-width="4"/></g>'
          f'<rect x="{hx-60}" y="{hy+46 - 92*bot}" width="120" height="{20 + 92*bot}" fill="url(#gBrassV)" stroke="{INK}" stroke-width="4"/></g>')
    # visor brow
    vy = {"smirk": -74, "worried": -84, "angry": -66}[expr]
    va = {"smirk": 4, "worried": -12, "angry": 16}[expr]
    s += (f'<g transform="rotate({va} {hx} {hy+vy})"><path d="M{hx-56},{hy+vy} Q{hx},{hy+vy-14} {hx+56},{hy+vy} L{hx+52},{hy+vy+10} Q{hx},{hy+vy} {hx-52},{hy+vy+10} Z" '
          f'fill="url(#gBrass)" stroke="{INK}" stroke-width="4"/></g>')
    s += "</g></g>"
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>{s}</svg>'


# ------------------------------------------------------------- render ----
def _shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[yd, xd] = a[ys, xs]
    return out


def finish(rgba, rim=(1.0, 0.55, 0.22), rim_dir=(1, -0.4), rim_w=9, rim_k=0.9,
           fill=(0.25, 0.85, 0.85), fill_k=0.45):
    """Add rim light from alpha edges. rgba float32 HxWx4 (0..1)."""
    a = rgba[..., 3]
    dx, dy = int(round(-rim_dir[0] * rim_w)), int(round(-rim_dir[1] * rim_w))
    edge = np.clip(a - _shift(a, dx, dy), 0, 1)
    e = Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rim_w * 0.35))
    edge = np.asarray(e, np.float32) / 255 * a
    edge2 = np.clip(a - _shift(a, -dx // 2, -dy // 2), 0, 1)
    e2 = Image.fromarray((edge2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rim_w * 0.3))
    edge2 = np.asarray(e2, np.float32) / 255 * a
    rgb = rgba[..., :3]
    rgb = rgb + edge[..., None] * np.array(rim, np.float32) * rim_k
    rgb = rgb + edge2[..., None] * np.array(fill, np.float32) * fill_k
    rgba = rgba.copy(); rgba[..., :3] = np.clip(rgb, 0, 1)
    return rgba


def render(char, state, scale=1.0, rim=True, **kw):
    svg = jax_svg(state) if char == "jax" else pip_svg(state)
    png = cairosvg.svg2png(bytestring=svg.encode(), scale=scale)
    im = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"), np.float32) / 255
    # un-premultiply is not needed: PIL returns straight alpha from cairo PNG
    if rim:
        im = finish(im, **kw)
    return im


def to_pil(rgba):
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "sheet":
    import os
    from PIL import ImageDraw, ImageFont
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 26)
    bg = (14, 24, 50)
    for char, sz in [("jax", (800, 1000)), ("pip", (600, 760))]:
        # expressions
        sheet = Image.new("RGB", (sz[0] * 3, sz[1] + 60), bg)
        for i, e in enumerate(["smirk", "worried", "angry"]):
            im = to_pil(render(char, {"expr": e, "mouth": "rest" if e != "angry" else "E", "look": (2, 0) if e != "worried" else (-4, 2), "head": {"smirk": -3, "worried": 4, "angry": -1}[e]}))
            sheet.paste(im, (i * sz[0], 0), im)
            ImageDraw.Draw(sheet).text((i * sz[0] + 20, sz[1] + 14), f"{char.upper()} - {e}", font=font, fill=(242, 231, 207))
        sheet.save(f"{out}/{char}_expressions.png")
        # visemes: crop to head area
        crop = (250, 150, 550, 450) if char == "jax" else (150, 100, 450, 640)
        cw, ch = crop[2] - crop[0], crop[3] - crop[1]
        vs = Image.new("RGB", (cw * 4, (ch + 40) * 2), bg)
        for i, v in enumerate(VISEMES):
            im = to_pil(render(char, {"expr": "smirk", "mouth": v})).crop(crop)
            x, y = (i % 4) * cw, (i // 4) * (ch + 40)
            vs.paste(im, (x, y), im)
            ImageDraw.Draw(vs).text((x + 10, y + ch + 6), v, font=font, fill=(242, 231, 207))
        vs.save(f"{out}/{char}_visemes.png")
    print("ok")
