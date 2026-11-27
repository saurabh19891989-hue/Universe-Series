#!/usr/bin/env python3
"""Assemble labelled JPG contact sheets for samples/look from scratch outputs.
Usage: make_sheets.py SCRATCH_ART_DIR OUT_DIR"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ART, OUT = sys.argv[1], sys.argv[2]
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 24)
FS = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 20)
BG = (14, 24, 50); CR = (242, 231, 207); OR = (208, 96, 31)


def sheet(cells, cell_h, title, out, cols=None, q=86):
    """cells: list of (path_or_img, label). Scales every cell to cell_h tall."""
    ims = []
    for p, lab in cells:
        im = p if isinstance(p, Image.Image) else Image.open(os.path.join(ART, p))
        if im.mode == "RGBA":
            b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im); im = b
        im = im.convert("RGB")
        im = im.resize((int(im.width * cell_h / im.height), cell_h), Image.LANCZOS)
        ims.append((im, lab))
    cols = cols or len(ims)
    rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
    W = max(sum(i.width for i, _ in r) + 12 * (len(r) + 1) for r in rows)
    H = 64 + len(rows) * (cell_h + 48)
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    d.text((14, 18), title, font=F, fill=OR)
    y = 64
    for r in rows:
        x = 12
        for im, lab in r:
            c.paste(im, (x, y)); d.text((x + 4, y + cell_h + 10), lab, font=FS, fill=CR); x += im.width + 12
        y += cell_h + 48
    c.save(os.path.join(OUT, out), quality=q)
    print(out, c.size, os.path.getsize(os.path.join(OUT, out)) // 1024, "KB")


os.makedirs(OUT, exist_ok=True)
sheet([("r1/pol_JAX.jpg", "Jax"), ("r1/pol_MIRA.jpg", "Mira"), ("r1/pol_PIP.jpg", "PIP"), ("r1/pol_BAR.jpg", "Baron")], 420,
      "ROUTE 1a  Pollinations anonymous endpoint (model: Sana, max ~886x665, forced watermark) ~4 s/image", "r1-pollinations-sheet.jpg", cols=2)
sheet([("r1/hz_JAX.webp", "Jax"), ("r1/hz_MIRA.webp", "Mira"), ("r1/hz_PIP.webp", "PIP (1st try)"), ("r1/hz_BAR.webp", "Baron"),
       ("r1/hz_pip2.webp", "PIP (2nd prompt)"), ("r1/hz_mira_close.webp", "Mira close-up (used in shot C)")], 480,
      "ROUTE 1b  AI Horde anonymous, FLUX.1-schnell fp8, 4 steps, 1024x768 - 8 to 12 min queue per image", "r1-horde-flux-sheet.jpg", cols=3)
sheet([("r1/hzc_jax_neutra.webp", "neutral"), ("r1/hzc_jax_laughi.webp", "laughing"), ("r1/hzc_jax_angry.webp", "angry"), ("r1/hzc_jax_worrie.webp", "'worried'")], 460,
      "CONSISTENCY  Horde FLUX schnell, same seed (1234) + identical character descriptor, only the expression words change", "r1-horde-jax-consistency.jpg")
sheet([("r2/ds_jax.png", "Jax"), ("r2/ds_mira.png", "Mira"), ("r2/ds_pip.png", "PIP"), ("r2/ds_baron.png", "Baron")], 600,
      "ROUTE 2  Local CPU: DreamShaper 8 (SD1.5) + LCM-LoRA, 5 steps, 512x768 - 77 to 187 s/image on the shared 4-core CPU", "r2-local-sheet.jpg")
ex = ["laugh", "angry", "worried", "smirk"]
sheet([(f"r2/jax_seed_{e}.png", f"seed only: {e}") for e in ex] + [(f"r2/jax_ipa_{e}.png", f"IP-Adapter Plus 0.55: {e}") for e in ex] + [("r2/jax_face_ref.png", "face reference crop")] + [(f"r2/jax_face_{e}.png", f"IP-Adapter Plus-Face 0.4: {e}") for e in ex[:3]], 400,
      "CONSISTENCY  Local SD1.5: row 1 same seed + descriptor; row 2 + IP-Adapter Plus on full Jax image; row 3 IP-Adapter Plus-Face on face crop", "r2-jax-consistency.jpg", cols=4)
up = Image.open(os.path.join(ART, "up/mira_x4.png"))
cut = Image.open(os.path.join(ART, "up/mira_cut2.png"))
teal = Image.new("RGBA", cut.size, (30, 140, 138, 255)); teal.alpha_composite(cut)
src = Image.open(os.path.join(ART, "r1/hz_mira_close.webp")).convert("RGB")
sheet([(src.crop((275, 225, 475, 425)).resize((800, 800), Image.NEAREST), "source 768px (nearest x4)"),
       (up.crop((1100, 900, 1900, 1700)), "Real-ESRGAN anime_6B x4 (CPU, 202 s)"),
       (teal.convert("RGB"), "rembg isnet + halo key-out, on teal")], 560,
      "ROUTE 2 finishing  CPU upscale 768x1024 -> 3072x4096 and alpha cut-out", "r2-upscale-cutout.jpg")
sheet([("r3/jax_expressions.png", "")], 560, "ROUTE 3  Code-built Jax rig: smirk / worried / angry", "r3-jax-expressions.jpg")
sheet([("r3/jax_visemes.png", "")], 560, "ROUTE 3  Jax 8 mouth shapes (rest, AI, E, O / U, MBP, FV, L)", "r3-jax-visemes.jpg")
sheet([("r3/pip_expressions.png", "")], 520, "ROUTE 3  Code-built PIP rig: officious / alarmed / disapproving", "r3-pip-expressions.jpg")
sheet([("r3/pip_visemes.png", "")], 560, "ROUTE 3  PIP 'mouth': voice grille + dial needle (8 states)", "r3-pip-visemes.jpg")
