"""SAMPLE 5 staging (picture side of the FROZEN timeline episodes/E01/sample5-shotlist.json).
Per shot: camera and who is where; per character: pose keys [t, pose] on absolute time, brow keys.
Times are taken from the frozen line placements through L(id) / E(id) so nothing in the sound moves."""
import json
R = "/home/user/Universe-Series"
SL = json.load(open(f"{R}/episodes/E01/sample5-shotlist.json"))
_L = {l["id"]: l for l in SL["dialogue"]}
def L(i, f=0.0): return round(_L[i]["start_s"] + f * _L[i]["dur"], 3)
def E(i): return round(_L[i]["start_s"] + _L[i]["dur"], 3)
SH = {s["id"]: s for s in SL["shots"]}
def T0(i): return SH[i]["start_s"]
def T1(i): return SH[i]["end_s"]
GAG = {g["what"]: g["at_s"] for g in SL["gags"]}
STAMP = GAG["the stamp THUNK"]

# ---------------------------------------------------------------- pose keys (absolute time)
JAX = [  # Part A
 [0, "J5_stop"], [T0("A03"), "walkknee"], [L("3-04", 0.93), "Jk_elbow"],
 [L("3-07"), "Jk_inb_point"], [L("3-07") + 0.09, "Jk_point"], [E("3-07") + 0.3, "Jk_elbow"],
 [L("3-09"), "Jk_far"], [L("3-09", 0.48), "Jk_whisper"],
 [L("3-11", 0.55), "Jk_inb_finger"], [L("3-11", 0.55) + 0.09, "Jk_finger"],
 [L("3-13"), "Jk_whisper"], [E("3-13") + 0.4, "Jk_listen"], [L("3-19"), "Jk_shrug"], [E("3-19") + 0.3, "Jk_listen"],
 [STAMP - 0.02, "Jk_listen"], [STAMP + 0.9, "Jk_salute"],
]
MIRA = [
 [0, "Mk_stamp"], [L("3-04") - 0.1, "Mk_over"], [L("3-08"), "Mk_form"], [E("3-08") + 0.3, "Mk_over"],
 [L("3-12"), "Mk_over"], [T0("A10"), "Mk_look"], [T0("A11"), "Mk_type"], [L("3-20") - 0.2, "Mk_look"],
 [STAMP - 0.5, "Mk_inb_up"], [STAMP - 0.42, "Mk_stampup"], [STAMP - 0.04, "Mk_slam"], [L("3-24") + 0.5, "Mk_over"],
 [T0("A15"), "Mk_write"],
]
NOAKES = [[0, "N5_lean"], [T0("A17"), "N5_board"], [T0("A18"), "N5_board"], [T0("A20"), "N5_lean"]]
# close-up / front choices: which picture set plays in each close-up shot
CU = {"A05": "M5_cu", "A07": "M5_cu", "A10": "M5_cu", "A12": "M5_front", "A06": "J5_cu", "A08": "J5_front", "A13": "J5_cu"}
# brow / expression keys per close-up (absolute time, key, amount)
BROW = {
 "A05": [[L("3-06"), "brow_frown", 0.6]],
 "A07": [[L("3-08", 0.5), "brow_skeptic", 0.7]],
 "A08": [[L("3-09", 0.05), "brow_up", 0.8], [L("3-11", 0.7), "brow_skeptic", 0.0]],
 "A10": [[T0("A10") + 0.35, "smile", 0.35], [T0("A10") + 0.75, "smile", 0.0]],   # the almost-smile: corner twitch, suppressed
 "A12": [[L("3-18"), "brow_up", 0.5]],
 "A13": [[L("3-19"), "smile", 0.0]],
}
BARON_CU = {"B02", "B05", "B08", "B12", "B13", "B15"}
JAX_CU = {"B03", "B07", "B09", "B14", "B16"}
LAUGH = (L("21-LAUGH") - 0.05, E("21-LAUGH") + 0.25)
SILENCE = (SL["silences"][0]["at_s"], SL["silences"][0]["at_s"] + SL["silences"][0]["dur_s"])
CUT = {b["beat"]: b["at_s"] for b in SL["cutaway_beats"]}
