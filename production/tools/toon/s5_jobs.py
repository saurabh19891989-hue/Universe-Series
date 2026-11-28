"""Second-stage SAMPLE 5 jobs, after the design pick (variant B for everyone).
Bases (poses, close-ups, set, walk sheet) use the master + the chosen design sheet as references;
face sets are EDITS of the close-up base (same picture, one change) so they can be pasted back
seamlessly by s5_faces.py."""
GREEN = ("BACKGROUND: completely flat, uniform, pure chroma-key green (#00FF00) behind the subject, no shadow, no floor, "
         "no other objects.")
EDIT = ("Reference image 1 is the approved picture. Make an IDENTICAL copy of it: same character, same pose, same framing, "
        "same position and size in the frame, same lighting and colours, same flat green background. Change ONLY {what}: {desc} "
        "Everything else (head position, hair, eyes and brows unless named, clothes, background) must stay exactly the same.")
MOUTH = {
 "A": "lips pressed firmly together, as when saying M, B or P",
 "B": "lips slightly parted with the teeth together and visible, as when saying S or T",
 "C": "mouth open in a relaxed medium shape, upper teeth visible, as when saying EH",
 "D": "mouth wide open, jaw dropped, upper teeth and the tongue visible inside, as when saying AH",
 "E": "mouth open in a rounded shape, as when saying OH",
 "F": "lips pushed forward into a small round pucker, as when saying OO or W",
 "G": "upper teeth resting on the lower lip, as when saying F or V",
 "H": "mouth open with the tip of the tongue touching behind the upper teeth, as when saying L",
 "smile": "a big warm open smile showing the upper teeth",
}
EYES = {
 "blink": ("the eyes", "both eyes fully closed in a relaxed blink (eyelids down), brows unchanged."),
 "brow_up": ("the eyebrows", "both eyebrows raised high in surprise; eyes and mouth unchanged."),
 "brow_frown": ("the eyebrows", "eyebrows drawn down and together in a frown; eyes and mouth unchanged."),
 "brow_skeptic": ("the eyebrows and eyelids", "one eyebrow arched high, the other slightly lowered, eyelids half lowered: a dry "
                  "sceptical look; mouth unchanged."),
}
def jobs(J, STY, CHAR, M, OUT):
    st = STY["B"]; out = {}
    JD, MD = f"{OUT}/jax_B.png", f"{OUT}/mira_B.png"
    jref, mref = [M["jax"], JD], [M["mira"], MD]
    jc = f"CHARACTER: {CHAR['jax']} Exactly the design of reference image 2."
    mc = f"CHARACTER: {CHAR['mira']} Exactly the design of reference image 2."
    out["J5_walk"] = (f"{st}\n{jc}\nWALK-CYCLE MODEL SHEET: EIGHT full-body drawings of him in one row, left to right, all exactly the "
                      "same size and standing on the same ground line, every one walking toward the RIGHT in side three-quarter view: a "
                      "relaxed confident swaggering stroll, like he owns the place, shoulders loose, arm swing. Order: 1 right heel "
                      "contact, 2 down, 3 passing, 4 up, 5 left heel contact, 6 down, 7 passing, 8 up. Drawings evenly spaced, NOT "
                      f"overlapping, each fully inside the frame, figures fill 85% of the frame height. Mouth closed.\n{GREEN}", jref)
    full = ("FRAMING: full body from the top of the hair to the soles of the boots, whole figure inside the frame, figure fills 86% "
            "of the frame height, centred.")
    out["J5_stop"] = (f"{st}\n{jc}\n{full}\nPOSE: has just stopped walking, standing, body turned three-quarters toward the RIGHT, weight "
                      f"settling on the back foot, arms relaxed, confident half-smile, mouth closed.\n{GREEN}", jref)
    out["J5_lean"] = (f"{st}\n{jc}\n{full}\nPOSE: leaning sideways with his right forearm resting on an invisible counter top at waist "
                      "height on the RIGHT side of him (the counter is not drawn), body turned toward the right, other hand on his "
                      f"hip, charming confident look to the right, mouth closed.\n{GREEN}", jref)
    cu = ("FRAMING: chest-up close shot, the head about 45% of the frame height, top of hair 6% below the top edge, the head "
          "horizontally centred, body turned three-quarters toward the {side}, looking toward the {side}.")
    out["J5_cu"] = (f"{st}\n{jc}\n{cu.format(side='RIGHT')}\nExpression: confident charming half-smile, mouth CLOSED, both eyes open, "
                    f"brows relaxed.\n{GREEN}", jref)
    out["M5_idle"] = (f"{st}\n{mc}\nFRAMING: from the top of her head down to mid-thigh (thighs cut by the bottom edge), head about "
                      "22% of the frame height, centred. POSE: standing, body turned three-quarters toward the LEFT, both forearms "
                      f"resting forward at waist height as if on a counter, cool deadpan look to the left, mouth closed.\n{GREEN}", mref)
    out["M5_cu"] = (f"{st}\n{mc}\n{cu.format(side='LEFT')}\nExpression: cool, composed, faintly amused, mouth CLOSED, both eyes open, "
                    f"brows relaxed.\n{GREEN}", mref)
    for who in ("J5_cu", "M5_cu"):
        base = f"{OUT}/{who}.png"
        for k, d in MOUTH.items():
            out[f"{who}_{k}"] = (EDIT.format(what="the mouth", desc=d + "."), [base])
        for k, (w, d) in EYES.items():
            out[f"{who}_{k}"] = (EDIT.format(what=w, desc=d), [base])
    out["S5_hall"] = (f"{st}\nSET (no people): the Rim Port customs hall on the Moon in this animated style, camera straight on at "
                      "standing eye height. The whole back wall is one enormous window with slim brass frame bars; the window glass is "
                      "COMPLETELY PURE FLAT BLACK (#000000), nothing in it. Clean warm cream and teal tiled floor filling the lower "
                      "40%, empty orange-red benches far left, a long wooden customs counter with brass trim on the right third with a "
                      "clean straight top edge and a clear top. Warm lamps on the side walls. Bright and colourful.",
                      [f"/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/cx/toon4/set_wide.png"])
    out["S5_cutaway"] = ("STYLE: an original hand-engraved storybook illustration: fine black cross-hatched line engraving on warm "
                         "cream paper, with a few flat washes of vermilion red and gold only, theatrical 18th-century tall-tale "
                         "energy, our own design. No text.\nSCENE: the Baron (the old gentleman of reference image 1: enormous white "
                         "moustache, black tricorn, red cavalry coat over a patched grey pressure suit) sits astride a flying "
                         "cannonball high above the grey cratered Moon with the blue Earth in a black starry sky, waving his hat, "
                         "while a second cannonball streaks past in the other direction which he is about to leap onto. Comic, "
                         "grand, lovable.", [M["baron"], f"{OUT}/baron_B.png"])
    return out
