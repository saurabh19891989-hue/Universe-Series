#!/usr/bin/env python3
"""SAMPLE 5 stage 2b pictures (Codex, 4 at once). usage: s5b_jobs.py wave1|wave2|wave3|NAME...
Outputs SCRATCH/cx/s5/<name>.png. Style = approved variant B. Face sets are EDITS of a base picture."""
import subprocess, sys, concurrent.futures as cf
sys.path.insert(0, "/home/user/Universe-Series/production/tools/toon")
from s5_pictures import STY, CHAR, M, CX
from s5_jobs import GREEN, EDIT, MOUTH, EYES
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
O = f"{S}/cx/s5"
st = STY["B"]
JR = [M["jax"], f"{O}/jax_B.png", f"{O}/J5_cu.png"]
MR = [M["mira"], f"{O}/mira_B.png", f"{O}/M5_cu.png"]
BR = [M["baron"], f"{O}/baron_B.png"]
NR = [f"{R}/assets/characters/noakes/master.jpg"]
jc = f"CHARACTER: {CHAR['jax']} Exactly the design of reference images 2 and 3 (same face, hair, stubble, jacket)."
mc = f"CHARACTER: {CHAR['mira']} Exactly the design of reference images 2 and 3 (same face, hair, braid, suit)."
NOAKES = ("Superintendent Noakes, the same man as reference image 1, kept recognisable: English man aged 55, tall and stooped, "
          "tired kind long face, thinning grey hair, heavy-lidded patient eyes, a decent rule-bound official; neat grey-blue customs "
          "uniform jacket with plain brass buttons and NO real-world insignia, a lanyard with a blank card.")
KNEE_J = ("FRAMING: knee-up (from the top of the hair down to just above the knees, legs cut by the bottom edge), head about 20% "
          "of the frame height, top of hair 6% below the top edge, figure centred. Body turned three-quarters toward the RIGHT, "
          "talking to someone on the right. Hands fully inside the frame.")
KNEE_M = ("FRAMING: from the top of her head down to mid-thigh (thighs cut by the bottom edge), head about 22% of the frame "
          "height, top of hair 6% below the top edge, figure centred. Body turned three-quarters toward the LEFT. She stands behind "
          "a counter that is NOT drawn: her hands work at waist height. Hands fully inside the frame.")
FC = "Mouth closed unless stated. Both eyes open."
J = lambda pose: (f"{st}\n{jc}\n{KNEE_J}\nPOSE: {pose}\n{FC}\n{GREEN}", JR)
Mi = lambda pose: (f"{st}\n{mc}\n{KNEE_M}\nPOSE: {pose}\n{FC}\n{GREEN}", MR)
FRONT = ("FRAMING: chest-up close shot, the head about 45% of the frame height, top of hair 6% below the top edge, head centred, "
         "facing the viewer almost straight on (a slight turn), looking just past the camera.")
ENG = ("STYLE: an original hand-engraved storybook illustration: fine black cross-hatched line engraving on warm cream paper, "
       "with a few flat washes of vermilion red and gold only, theatrical 18th-century tall-tale energy, our own design, matching "
       "reference image 3 exactly in style. No text.")
YB = ("the Baron as a YOUNG MAN of about 30: magnificent, dashing hussar officer, the same face family as reference images 1-2 "
      "but young, a splendid dark moustache with upturned tips, black tricorn hat, red hussar jacket with gold frogging, white "
      "breeches, tall black boots")
CWR = [M["baron"], f"{O}/baron_B.png", f"{O}/S5_cutaway.png"]
CWG = ("BACKGROUND: completely flat uniform pure chroma-key green (#00FF00) around the subject, no paper texture outside the "
       "subject, no other objects.")
SUIT_J = ("He wears a white-and-burnt-orange pressure suit with a metal neck ring and a CLEAR glass bubble helmet; the glass "
          "is perfectly transparent, his whole face fully visible and unobstructed, only a thin soft highlight at the very edge.")
SUIT_B = ("He wears a patched grey pressure suit under his moth-eaten red cavalry coat, a metal neck ring and a CLEAR glass "
          "bubble helmet; his black tricorn hat is strapped ABSURDLY ON TOP of the outside of the glass dome with a buckled "
          "strap; the glass is perfectly transparent, his whole face and enormous white moustache fully visible, only a thin "
          "soft highlight at the very edge.")
JOBS = {
 # ---------- wave 1
 "J5_front": (f"{st}\n{jc}\n{FRONT}\nExpression: easy charming half-smile, mouth CLOSED, brows relaxed.\n{GREEN}", JR),
 "M5_front": (f"{st}\n{mc}\n{FRONT}\nExpression: cool, composed, faintly amused, mouth CLOSED, brows relaxed.\n{GREEN}", MR),
 "J5_cu_shout": (EDIT.format(what="the mouth and eyebrows", desc="shouting: mouth wide open, jaw dropped, eyebrows raised high. Keep the head in exactly the same place and size."), [f"{O}/J5_cu.png"]),
 "M5_cu_shout": (EDIT.format(what="the mouth and eyebrows", desc="shouting: mouth wide open, jaw dropped, eyebrows raised high. Keep the head in exactly the same place and size."), [f"{O}/M5_cu.png"]),
 "J5_cu_brow_up2": (EDIT.format(what="ONLY the two eyebrows", desc="both eyebrows lifted a little higher in mild surprise. The head, face outline, eyes, hair and everything else stay pixel-identical: do not move, turn, tilt or rescale the head."), [f"{O}/J5_cu.png"]),
 "M5_cu_brow_up2": (EDIT.format(what="ONLY the two eyebrows", desc="both eyebrows lifted a little higher in mild surprise. The head, face outline, eyes, hair and everything else stay pixel-identical: do not move, turn, tilt or rescale the head."), [f"{O}/M5_cu.png"]),
 "M5_cu_blink2": (EDIT.format(what="ONLY the eyelids", desc="both eyes closed in a soft relaxed blink, both upper lids fully down with the lashes resting on the cheek; nothing else changes."), [f"{O}/M5_cu.png"]),
 "Jk_elbow": J("leaning sideways with his right elbow resting on an invisible counter top at waist height to his right, full charm, warm crooked smile, the other hand on his hip."),
 "Jk_point": J("a wounded mock-offended finger-point toward the right, eyebrows up, mouth closed."),
 "Jk_far": J("pointing far off into the distance over his shoulder toward the left with his thumb, without a blink, deadpan straight face."),
 "Jk_finger": J("one finger raised beside his face making a clever point, little flourish, sly confident look to the right."),
 "Jk_whisper": J("leaning in toward the right, one hand raised beside his mouth as if sharing a secret, eyebrows lifted, confidential."),
 "Jk_shrug": J("easy shrug, palms up at chest height, relaxed grin with mouth closed."),
 "Jk_listen": J("standing, weight on one leg, one hand in his jacket pocket, listening with a charming half-smile toward the right."),
 "Jk_salute": J("turning away to leave toward the LEFT, looking back over his shoulder to the right, giving a casual two-finger salute from his brow, half-smile."),
 "J5_walkA": (f"{st}\n{jc}\nWALK-CYCLE MODEL SHEET, part 1 of 2: SIX full-body drawings in one row, left to right, all exactly the same size and standing on the same ground line, every one walking toward the RIGHT in side three-quarter view: a relaxed confident swaggering stroll like he owns the place. They are drawings 1-6 of a 12-drawing cycle and cover ONE step: 1 right heel touches down in front (left foot behind on its toes), 2 down (weight sinks onto the right foot, knee bends), 3 passing (left leg swings past the right), 4 up (rising on the right foot, left knee lifted forward), 5 reaching (left leg stretching forward), 6 just before the left heel touches down. Arms swing opposite to the legs. Figures about 66% of the frame height, evenly spaced with clear gaps, NOT overlapping. Mouth closed.\n{GREEN}", JR),
 "J5_walkknee": (f"{st}\n{jc}\nWALK MODEL SHEET, knee-up: SIX drawings of him in one row, each framed from the top of the hair to just above the knees, all the same size and height, walking toward the RIGHT in three-quarter view, a confident easy stroll: the body bobs (drawings 1 and 4 lowest, 2-3 and 5-6 higher), arms swing opposite each other with a full swing, shoulders loose, a relaxed smile. Evenly spaced, NOT overlapping, each fully inside the frame.\n{GREEN}", JR),
 "Mk_stamp": Mi("stamping a paper on the counter with a rubber stamp in her right hand, eyes down on the papers, patient, not looking up."),
 "Mk_form": Mi("holding up a paper form toward the left with one hand and tapping a line on it with the other index finger, deadpan look to the left."),
 "Mk_over": Mi("holding a paper form at chest height and looking over the top of it toward the left, deadpan, one eyebrow slightly down."),
 "Mk_type": Mi("both hands on a small keyboard on the counter, eyes on a screen to her right, concentrating, interested."),
 "Mk_look": Mi("standing still, looking toward the left with a long, curious, slightly softened look, lips closed, the hint of a smile she is suppressing."),
 "Mk_stampup": Mi("winding up: a brass rubber stamp raised high above her shoulder in her right hand, eyes narrowed, lips pressed."),
 "Mk_slam": Mi("slamming the brass rubber stamp down onto the counter at waist height, body leaning forward over it, satisfied."),
 "Mk_write": Mi("writing in a battered paper notebook held on the counter, pen in her right hand, eyes down on the page, absorbed."),
 "N5_sheet": (f"{st}\nCHARACTER: {NOAKES}\nCHARACTER DESIGN SHEET on a plain flat light grey background: on the LEFT a full-body drawing standing, body turned three-quarters toward the right; on the RIGHT a large head-and-shoulders close-up, three-quarters toward the right, mouth closed, weary kind look. Same costume in both. No text.", NR),
 "B5_scale": (f"{st}\nCHARACTER: {CHAR['baron']}\nFRAMING: full body, whole figure inside the frame, figure fills 86% of the frame height.\nPOSE: standing very straight on a small platform (a cargo scale), chest out, chin up, up on his toes trying to look taller, arms stiff at his sides.\n{GREEN}", BR),
 "B5_arms": (f"{st}\nCHARACTER: {CHAR['baron']}\nFRAMING: full body, whole figure inside the frame, figure fills 86% of the frame height.\nPOSE: standing on a small platform (a cargo scale), throwing both arms up in outrage, mouth hidden by the moustache, eyebrows furious.\n{GREEN}", BR),
 "JS_sheet": (f"{st}\nCHARACTER: {CHAR['jax']} {SUIT_J}\nCHARACTER DESIGN SHEET on a plain flat light grey background: LEFT full body standing in the suit and helmet, three-quarters toward the right; RIGHT a large head-and-shoulders close-up inside the clear helmet, three-quarters toward the right, mouth closed. No text.", JR),
 "BS_sheet": (f"{st}\nCHARACTER: {CHAR['baron']} {SUIT_B}\nCHARACTER DESIGN SHEET on a plain flat light grey background: LEFT full body standing in the suit and helmet, three-quarters toward the left; RIGHT a large head-and-shoulders close-up inside the clear helmet with the tricorn strapped on top, three-quarters toward the left, mouth hidden by the moustache. No text.", BR),
 "S5_wide2": (f"{st}\nSET (no people): the same Rim Port customs hall as reference image 1, a CLOSER wide view: on the RIGHT half, close to camera, Mira's tall wooden customs counter with brass trim (a high desk; its top edge a clean straight line at about 55% of the frame height, the space behind it empty), a small brass lamp and a tray of papers on it. Behind, the enormous window wall; the window glass is COMPLETELY PURE FLAT BLACK (#000000), nothing in it. On the LEFT the long hall recedes far into the distance with rows of empty orange benches and, at the far end, a tiny cargo scale platform. Warm cream and teal tiles, warm lamps, bright and colourful.", [f"{O}/S5_hall.png"]),
 "S5_rock": (f"{st}\nSUBJECT: a big flat-topped grey lunar boulder, sunlit from the left with a crisp dark shadow side, fine regolith dust on top, wide enough for two people to sit on side by side; seen from slightly below.\n{GREEN}", [f"{O}/S5_hall.png"]),
 "CW_bg": (f"{ENG}\nSCENE (no people): a wide panoramic paper-theatre backdrop: a black starry sky with the blue Earth, below it the grey cratered Moon, and far off on the plain a star-shaped fortress with a crescent banner and an army's tents on the near field. Leave the upper middle sky open.", CWR),
 "CW_cannon": (f"{ENG}\nSUBJECT: a great bronze cannon on a wooden carriage, three-quarter view pointing up to the RIGHT, firing: a huge billowing smoke cloud and flash at the muzzle.\n{CWG}", CWR),
 "CW_leap": (f"{ENG}\nSUBJECT: {YB}, leaping through the air onto a flying black cannonball that is heading to the RIGHT, one leg swinging over it, arms out, tricorn on.\n{CWG}", CWR),
 "CW_ride": (f"{ENG}\nSUBJECT: {YB}, sitting astride a flying black cannonball like riding a horse, heading to the RIGHT, one hand on the ball, the other raised, proud and dashing, a little smoke trail behind.\n{CWG}", CWR),
 "CW_doubt": (f"{ENG}\nSUBJECT: {YB}, astride a flying black cannonball heading to the RIGHT, looking down with sudden doubt, a hand on his chin, eyebrows knitted.\n{CWG}", CWR),
 "CW_crouch": (f"{ENG}\nSUBJECT: {YB}, crouching on top of a flying black cannonball heading to the RIGHT, coiled to spring, eyes on something coming from the right, holding his hat on.\n{CWG}", CWR),
 "CW_jump": (f"{ENG}\nSUBJECT: {YB}, in mid-air between two things, body stretched in a heroic leap toward the LEFT, coat tails flying, his tricorn hat has come off and floats above his head.\n{CWG}", CWR),
 "CW_land": (f"{ENG}\nSUBJECT: {YB}, standing gracefully on top of a flying black cannonball heading to the LEFT, making a deep courtly bow with his tricorn swept off in one hand.\n{CWG}", CWR),
 "CW_ball": (f"{ENG}\nSUBJECT: a single black iron cannonball flying to the LEFT with engraved speed lines and a small smoke trail.\n{CWG}", CWR),
 "CW_hat": (f"{ENG}\nSUBJECT: a single black tricorn hat with gold trim, tumbling in the air.\n{CWG}", CWR),
}
# ---------- wave 2 (needs wave 1)
W2 = {}
for who, base in (("J5_front", JR), ("M5_front", MR)):
    b = f"{O}/{who}.png"
    for k, d in MOUTH.items(): W2[f"{who}_{k}"] = (EDIT.format(what="the mouth", desc=d + ". Keep the head in exactly the same place and size."), [b])
    W2[f"{who}_blink"] = (EDIT.format(what="ONLY the eyelids", desc="both eyes closed in a relaxed blink; nothing else changes."), [b])
    W2[f"{who}_brow_skeptic"] = (EDIT.format(what="the eyebrows and eyelids", desc="one eyebrow arched high, the other slightly lowered, lids half lowered: a dry sceptical look; head unchanged."), [b])
NS = [f"{O}/N5_sheet.png"] + NR
W2["N5_lean"] = (f"{st}\nCHARACTER: {NOAKES} Exactly the design of reference image 1.\nFRAMING: from the top of his head down to the waist, head about 26% of the frame height, figure centred. POSE: bending down and forward toward the LEFT to look at something on a desk below, hands clasped behind his back, soft pained expression, mouth closed.\n{GREEN}", NS)
W2["N5_board"] = (f"{st}\nCHARACTER: {NOAKES} Exactly the design of reference image 1.\nFRAMING: from the top of his head down to the waist, head about 26% of the frame height, figure centred. POSE: standing, looking up and to the left at something high on a wall with something like love, hands clasped in front, mouth closed.\n{GREEN}", NS)
JSR = [f"{O}/JS_sheet.png", f"{O}/J5_cu.png"]; BSR = [f"{O}/BS_sheet.png", f"{O}/baron_B.png"]
W2["JS_cu"] = (f"{st}\nCHARACTER: {CHAR['jax']} {SUIT_J} Exactly the design of reference image 1.\nFRAMING: chest-up close shot inside the helmet, the head about 40% of the frame height, the whole helmet inside the frame, head three-quarters toward the RIGHT, looking right. Mouth closed, both eyes open.\n{GREEN}", JSR)
W2["BS_cu"] = (f"{st}\nCHARACTER: {CHAR['baron']} {SUIT_B} Exactly the design of reference image 1.\nFRAMING: chest-up close shot inside the helmet, the head about 36% of the frame height, the whole helmet AND the tricorn on top inside the frame, head three-quarters toward the LEFT, looking left. Mouth hidden by the moustache, both eyes open, gentle.\n{GREEN}", BSR)
W2["JS_seat"] = (f"{st}\nCHARACTER: {CHAR['jax']} {SUIT_J} Exactly the design of reference image 1.\nFRAMING: full body, sitting on an invisible seat at knee height (the seat is not drawn), whole figure inside the frame filling 80% of its height, body three-quarters toward the RIGHT, hands resting on his knees.\n{GREEN}", JSR)
W2["BS_seat"] = (f"{st}\nCHARACTER: {CHAR['baron']} {SUIT_B} Exactly the design of reference image 1.\nFRAMING: full body, sitting on an invisible seat at knee height (the seat is not drawn), whole figure inside the frame filling 80% of its height, body three-quarters toward the LEFT, one gloved hand raised as if telling a story.\n{GREEN}", BSR)
W2["Jk_inb_point"] = (f"{st}\n{jc}\n{KNEE_J}\nPOSE: an IN-BETWEEN drawing exactly halfway between reference image 1 (leaning on his elbow) and reference image 2 (pointing): the arm halfway up, the body halfway turned.\n{FC}\n{GREEN}", [f"{O}/Jk_elbow.png", f"{O}/Jk_point.png", M["jax"]])
W2["Jk_inb_finger"] = (f"{st}\n{jc}\n{KNEE_J}\nPOSE: an IN-BETWEEN drawing exactly halfway between reference image 1 (pointing far off) and reference image 2 (finger raised): the hand travelling up and forward.\n{FC}\n{GREEN}", [f"{O}/Jk_far.png", f"{O}/Jk_finger.png", M["jax"]])
W2["Mk_inb_up"] = (f"{st}\n{mc}\n{KNEE_M}\nPOSE: an IN-BETWEEN drawing exactly halfway between reference image 1 (looking) and reference image 2 (stamp raised high): her right hand lifting the brass stamp to shoulder height.\n{FC}\n{GREEN}", [f"{O}/Mk_look.png", f"{O}/Mk_stampup.png", M["mira"]])
W2["J5_walkB"] = ("Reference image 1 is a six-drawing walk-cycle model sheet. Make an IDENTICAL sheet in the same style, same size, same positions, same ground line, same character and colours, but showing drawings 7-12 of the cycle: the SAME six poses with the LEFT and RIGHT legs swapped and the arms swapped (the opposite leg forward in each drawing), so that together the two sheets form one continuous 12-drawing walk. Flat green background. No text.", [f"{O}/J5_walkA.png", f"{O}/jax_B.png"])
# ---------- wave 3 (needs wave 2)
W3 = {}
for b in ("N5_lean", "JS_cu"):
    for k, d in MOUTH.items(): W3[f"{b}_{k}"] = (EDIT.format(what="the mouth", desc=d + ". Keep the head in exactly the same place and size."), [f"{O}/{b}.png"])
W3["N5_lean_blink"] = (EDIT.format(what="ONLY the eyelids", desc="both eyes gently closed, a weary man closing his eyes; nothing else changes."), [f"{O}/N5_lean.png"])
W3["N5_board_blink"] = (EDIT.format(what="ONLY the eyelids", desc="both eyes gently closed; nothing else changes."), [f"{O}/N5_board.png"])
W3["JS_cu_blink"] = (EDIT.format(what="ONLY the eyelids", desc="both eyes closed in a relaxed blink; nothing else changes."), [f"{O}/JS_cu.png"])
W3["JS_laugh"] = (EDIT.format(what="the head and face", desc="he laughs for real: head tipped back inside the helmet, eyes squeezed shut, big open laugh showing teeth, shoulders lifted; the inside of the glass slightly fogged at the bottom. Keep the suit, helmet ring and framing the same."), [f"{O}/JS_cu.png"])
BM = {"A": "the moustache pressed flat, lips together underneath (hidden)", "C": "the jaw dropped a little so the bottom of the moustache lifts and a dark gap of open mouth shows just below it",
      "D": "the jaw dropped wide so the big moustache lifts and a wide dark open mouth shows clearly below it", "E": "a rounded open mouth showing below the lifted moustache, as when saying OH",
      "F": "lips pushed into a small round pucker peeking under the moustache, as when saying OO", "smile": "a delighted grin that lifts the moustache ends upward, cheeks bunched"}
for k, d in BM.items(): W3[f"BS_cu_{k}"] = (EDIT.format(what="the mouth and moustache", desc=d + ". Keep the head, helmet and tricorn exactly in place."), [f"{O}/BS_cu.png"])
W3["BS_cu_blink"] = (EDIT.format(what="ONLY the eyelids", desc="both eyes closed in a relaxed blink; nothing else changes."), [f"{O}/BS_cu.png"])
W3["BS_cu_brow_up"] = (EDIT.format(what="ONLY the bushy white eyebrows", desc="eyebrows shot up high in genuine surprise; nothing else moves."), [f"{O}/BS_cu.png"])
ALL = {**JOBS, **W2, **W3}
def run(n):
    b, refs = ALL[n]
    cmd = ["python3", f"{R}/production/tools/look/codex_image.py", "s5", n, b, "--no-style", "--purpose", "sample 5 stage 2b"]
    for r in refs: cmd += ["-i", r]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return n, p.returncode, (p.stdout or p.stderr)[-250:]
if __name__ == "__main__":
    a = sys.argv[1:]
    sel = list(JOBS) if a == ["wave1"] else list(W2) if a == ["wave2"] else list(W3) if a == ["wave3"] else a
    with cf.ThreadPoolExecutor(4) as ex:
        for n, rc, out in ex.map(run, sel):
            print(n, rc, out.replace("\n", " ")[:200], flush=True)
            if rc == 3: print("LIMIT", n, flush=True)
