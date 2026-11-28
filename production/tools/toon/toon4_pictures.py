#!/usr/bin/env python3
"""TEST 4 pictures (painted graphic-novel look, pose library). Codex CLI via
production/tools/look/codex_image.py, up to 4 at once. Outputs: SCRATCH/cx/toon4/<name>.png
usage: toon4_pictures.py name [name ...] | all | batch1 | batch2
Exit early and print LIMIT if Codex reports a usage limit.
"""
import subprocess, sys, json, concurrent.futures as cf
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
CX = f"{R}/production/tools/look/codex_image.py"
JM, MM = f"{R}/assets/characters/jax/master.jpg", f"{R}/assets/characters/mira/master.jpg"
JD, MD = f"{S}/cx/toon4/J_idle.png", f"{S}/cx/toon4/M_neutral.png"   # approved design refs (batch 1)

STYLE = ("STYLE: a bright, rich painted animation keyframe in a graphic-novel style: clean confident shapes, crisp dark ink "
         "outlines, smooth cel shading with soft painted gradients, saturated vivid colour, warm golden key light with a cool "
         "teal rim light, cinematic and glamorous, like a frame from a high-end hand-painted animated feature film. Original "
         "design. Not photoreal, not 3D CGI. No text, no letters, no logos, no watermark.")
GREEN = ("BACKGROUND: completely flat, uniform, pure chroma-key green (#00FF00) filling everything behind the subject, no "
         "shadow, no floor, no gradient, no other objects.")
JAX = ("CHARACTER: the same man as the reference image(s), kept exactly recognisable: Jax Vale, Mediterranean Greek man, late "
       "30s, olive skin, dark curly hair greying slightly at the temples, stubble, weathered handsome film-star face with a "
       "crooked half-smile, same nose, brows and face shape; scuffed burnt-orange flight jacket with many pockets over a grey "
       "t-shirt, dark harness straps, dark brown work trousers, heavy brown boots. Same costume in every picture.")
MIRA = ("CHARACTER: the same woman as the reference image(s), kept exactly recognisable: Dr Mira Sen, Bengali Indian woman, "
        "aged 32 (young, not older), strikingly beautiful film-star face, warm brown skin, large dark intelligent eyes, long dark "
        "braid over her right shoulder, ink-stained fingers; fitted indigo flight suit with tan shoulder patches, a brass loupe on "
        "a chain round her neck. Glamorous but tasteful. Same costume in every picture.")
FULL = ("FRAMING: full body from the top of the hair to the soles of the boots, the whole figure inside the frame, figure "
        "fills 88% of the frame height, top of hair 6% below the top edge, boots 6% above the bottom edge, figure centred "
        "horizontally. Body and head turned three-quarters toward the RIGHT of the frame, as if facing someone standing to "
        "the right. Arms and hands fully inside the frame, never touching the edges.")
KNEE = ("FRAMING: from the top of her head down to mid-thigh (the thighs are cut by the bottom edge), head about 24% of the "
        "frame height, top of hair 7% below the top edge, figure centred horizontally. Body and head turned three-quarters "
        "toward the LEFT of the frame, talking to someone standing to the left. Arms and hands fully inside the frame.")
FACE_C = "Mouth: lips gently closed (not open, no teeth). Both eyes open and clearly visible."
J = lambda pose, extra="": (f"{STYLE}\n{JAX}\n{FULL}\nPOSE: {pose}\n{extra or FACE_C}\n{GREEN}", [JM, JD])
JKNEE = ("FRAMING: from the top of his head down to mid-thigh (thighs cut by the bottom edge), head about 24% of the frame "
         "height, top of hair 7% below the top edge, figure centred horizontally. Body and head turned three-quarters toward the "
         "RIGHT of the frame, talking to someone standing to the right. Arms and hands fully inside the frame.")
JK = lambda pose, extra="": (f"{STYLE}\n{JAX}\n{JKNEE}\nPOSE: {pose}\n{extra or FACE_C}\n{GREEN}", [JM, JD])
M = lambda pose, extra="", fr=KNEE: (f"{STYLE}\n{MIRA}\n{fr}\nPOSE: {pose}\n{extra or FACE_C}\n{GREEN}", [MM, MD])
JOBS = {
 # batch 1 (master only)
 "J_idle": (f"{STYLE}\n{JAX}\n{FULL}\nPOSE: relaxed standing, weight on one leg, arms hanging loosely at his sides, confident.\n{FACE_C}\n{GREEN}", [JM]),
 "M_neutral": (f"{STYLE}\n{MIRA}\n{KNEE}\nPOSE: standing upright, both forearms resting forward at waist height as if on a counter, calm deadpan look at the person to the left.\n{FACE_C}\n{GREEN}", [MM]),
 "ship": (f"{STYLE}\nSUBJECT: the same spaceship as the reference image, kept in shape and colours (boxy patched cream, mustard, grey and rust-red courier ship, cargo crates in netting, two round tanks, roof railing, antenna and dish, cab windows at the front, four round engine pods on struts): a lived-in working ship of original design. Exact SIDE view, nose pointing to the RIGHT, engines at the left with dark (unlit) nozzles, landing legs folded under the hull. Whole ship inside the frame with a margin of at least 8% on every side.\n{GREEN}", [f"{R}/assets/ship/master.jpg"]),
 "set_wide": (f"{STYLE}\nSET (no people): the Rim Port customs hall on the Moon, as in the reference but in this painted style. Camera straight on at standing eye height. The whole back wall is ONE enormous window divided by a few slim bronze frame bars; the window glass is COMPLETELY PURE FLAT BLACK (#000000) with nothing in it, no stars, no reflections. Floor: clean warm cream and teal tiles with lots of open floor in the lower half for people to walk. Left: two rows of empty orange-red benches and a tall flip-number board. Right third: a long wooden customs counter with a brass trim, its top edge a clean straight horizontal line, counter top completely clear, the space behind it empty. Warm golden lamps on the side walls. Bright, colourful, inviting.", [f"{R}/assets/sets/customs/master-bright.jpg"]),
 # batch 2 (master + design ref)
 "J_sweep": J("standing, his left arm swept out wide to the side away from the body with the open palm up, presenting the empty room, eyebrows raised, amused."),
 "J_shrug": J("big comic shrug: shoulders raised to the ears, both forearms out with open palms up, head tilted, eyebrows up."),
 "J_point": J("standing, leaning slightly forward, his right arm extended straight toward the RIGHT of the frame, index finger pointing at someone, cheeky grin with lips closed."),
 "J_plead": J("leaning in toward the right with a charming conspiratorial look, both hands raised at chest height with open palms, eyebrows lifted, persuasive."),
 "J_finger": J("standing tall, one hand raised beside his shoulder with the index finger pointing straight up, as if making a clever point, eyebrows raised."),
 "J_self": J("leaning back proudly, his right thumb pointing at his own chest, smug confident grin with lips closed."),
 "J_flinch": J("flinching from a sudden loud bang: shoulders hunched up, eyes squeezed shut, both hands raised in front of his chest, knees slightly bent.", "Eyes squeezed shut, mouth a tight grimace with lips closed."),
 "J_walk": (f"{STYLE}\n{JAX}\nWALK-CYCLE MODEL SHEET: SIX full-body drawings of him in a row, left to right, all the same size and on the same ground line, each walking toward the RIGHT in three-quarter view, a confident easy stride with arm swing: 1 right heel contact, 2 down (weight on right), 3 passing, 4 left heel contact, 5 down (weight on left), 6 passing. Drawings evenly spaced and NOT overlapping, each fully inside the frame, figures fill 85% of the frame height. {FACE_C}\n{GREEN}", [JM, JD]),
 "J_cu_finger": (f"{STYLE}\n{JAX}\nFRAMING: waist-up close shot, head about 36% of the frame height, top of hair 6% below the top edge, figure slightly left of centre, body turned three-quarters toward the RIGHT.\nPOSE: one hand raised beside his face with the index finger pointing straight up, making a clever point, eyebrows raised, sly look to the right.\n{FACE_C}\n{GREEN}", [JM, JD]),
 "M_form": M("reading a paper form held up in her right hand at chest height, eyes down on it, faint frown."),
 "M_show": M("holding a paper form up toward the left at shoulder height to show it, deadpan stare to the left, one eyebrow slightly raised."),
 "M_tap": M("pointing down at the counter in front of her with one index finger, firm deadpan look to the left."),
 "M_stamp": M("holding a heavy brass-handled rubber stamp raised at shoulder height in her right hand, cool challenging look to the left."),
 "M_stamp_up": M("winding up: the brass rubber stamp raised high above her head in her right hand, body leaning back, eyes narrowed, determined smile with lips closed."),
 "M_slam": M("slamming the brass rubber stamp down hard on the counter in front of her at waist height, body leaning forward over it, satisfied little smile with lips closed."),
 "M_cu": (f"{STYLE}\n{MIRA}\nFRAMING: chest-up close shot, head about 42% of the frame height, top of hair 6% below the top edge, figure slightly right of centre, body turned three-quarters toward the LEFT.\nPOSE: listening with a cool deadpan look toward the left, eyelids slightly lowered.\n{FACE_C}\n{GREEN}", [MM, MD]),
 "M_cu_look": (f"{STYLE}\n{MIRA}\nFRAMING: chest-up close shot, head about 42% of the frame height, top of hair 6% below the top edge, figure slightly right of centre.\nPOSE: she has turned her face to look straight into the camera, one eyebrow arched high, eyelids half lowered, the tiniest unimpressed smirk with lips closed: a dry comic look at the audience.\nBoth eyes open (half-lidded), clearly visible.\n{GREEN}", [MM, MD]),
 "Jk_listen": JK("standing, listening, weight on one leg, arms relaxed, a confident crooked half-smile toward the right."),
 "Jk_plead": JK("leaning in toward the right with a charming conspiratorial look, both hands raised at chest height with open palms, eyebrows lifted, persuasive."),
 "Jk_point": JK("his right arm extended toward the RIGHT edge of the frame (hand stays inside the frame), index finger pointing at someone, cheeky grin with lips closed."),
 "Jk_self": JK("leaning back proudly, his right thumb pointing at his own chest, smug confident look with lips closed."),
 "Jk_shrug": JK("big comic shrug: shoulders up to the ears, both forearms out with open palms up, sheepish wince-smile with lips closed, eyebrows up."),
 "Jk_flinch": JK("flinching from a sudden loud bang: shoulders hunched up, eyes squeezed shut, both hands raised in front of his chest.", "Eyes squeezed shut, mouth a tight grimace with lips closed."),
 "Jk_startle": JK("startled double-take: eyes wide open, eyebrows shot up, leaning back slightly, hands half raised.", "Eyes wide open, mouth closed."),
 "set_desk": (f"{STYLE}\nSET (no people): a closer view of the same customs hall as reference image 1: the long wooden customs counter with brass trim runs across the lower 30% of the frame from the middle to the right edge, its top edge a clean straight horizontal line, the counter top completely clear; the empty space behind it where an officer stands. The left 40% of the frame is open floor of cream and teal tiles. Behind everything, the enormous window fills the upper 60% of the frame; its glass is COMPLETELY PURE FLAT BLACK (#000000), no stars, no reflections, divided by two slim bronze frame bars. Bright, warm, colourful.", [f"{S}/cx/toon4/set_wide.png"]),
}
BATCH1 = ["J_idle", "M_neutral", "ship", "set_wide"]
def run(n):
    b, refs = JOBS[n]
    cmd = ["python3", CX, "toon4", n, b, "--no-style", "--purpose", "toon test 4 pose library"]
    for r in refs: cmd += ["-i", r]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return n, p.returncode, (p.stdout or p.stderr)[-400:]
if __name__ == "__main__":
    sel = sys.argv[1:]
    if sel == ["batch1"]: sel = BATCH1
    elif sel == ["batch2"]: sel = [k for k in JOBS if k not in BATCH1]
    with cf.ThreadPoolExecutor(4) as ex:
        for n, rc, out in ex.map(run, sel):
            print(n, rc, out.replace("\n", " ")[:300], flush=True)
            if rc == 3: print("LIMIT", n, flush=True)
