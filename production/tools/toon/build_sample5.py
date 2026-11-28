#!/usr/bin/env python3
"""SAMPLE 5 (stage 2a): lock the sound timeline.
Writes episodes/E01/sample5-shotlist.json (shots, absolute line placements, poses/business per line,
silences, cutaway beats, gags/buttons; "mix_version": 3) and SCRATCH/s5/sample5-dialogue-guide.wav
(dialogue only, 48 kHz, on that timeline). Script: episodes/E01/script-v4.md scenes 3 and 13;
dialogue = the final v3 stems in SCRATCH/e01/dialogue (map: episodes/E01/dialogue-conform.json).
Built as a list of events; each line starts `gap` seconds after the previous event ends.
"""
import json, numpy as np, soundfile as sf
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
conf = json.load(open(f"{R}/episodes/E01/dialogue-conform.json"))
LN = {}
for sc in conf["scenes"]:
    for l in sc["lines"]:
        LN[f"{sc['scene']}-{l['index']:02d}"] = l
def stem(lid):
    l = LN[lid]; f = l["file_treated"] or l["file_dry"]
    return f"{S}/e01/dialogue/{f}", l["speaker"].lower(), l["text_spoken"]
NEW = {"21-LAUGH": (f"{S}/s5/newlines/E01_S21_LAUGH_JAX_v1.wav", "jax", "(laughs)")}

# event list: ("L", line_id, gap_before, shot, business) | ("B", seconds, shot, what) | ("SHOT", id, kind, desc)
A = [
 ("SHOT", "A01", "wide", "WIDE: the vast customs hall; Mira high behind her counter in the warm lamp pool; real NASA lunar surface + Earth fill the great window; far down the hall a tiny Baron on a cargo scale, a drone weighing him"),
 ("B", 2.6, "establish: hall breathes; drone beeps round the tiny Baron"),
 ("L", "3-01", 0.0, "Mira, not looking up, stamping papers"),
 ("B", 0.7, "Jax (foreground, back to camera then turning) looks round the empty hall: left, right"),
 ("L", "3-02", 0.1, "Jax: open-hand sweep at the empty benches"),
 ("L", "3-03", 0.3, "Mira stamps something, patient; eyes still down"),
 ("SHOT", "A02", "walk_full", "FULL-BODY WALK, one short clean pass: Jax strolls in toward the counter like he owns the place (drawn cycle on twos, heels pinned)"),
 ("B", 2.2, "walk pass across frame left to right"),
 ("SHOT", "A03", "walk_track", "KNEE-UP TRACKING: Jax walking, bob + arm swing, background slides; Mira's reading as voice-over"),
 ("L", "3-04", 0.1, "Mira O.S., reading quick and dry; Jax arrives and sets his elbow on the counter on 'Seized'"),
 ("B", 0.6, "Jax settles the elbow, smile switched on"),
 ("SHOT", "A04", "two_shot", "TWO-SHOT across the counter, Mira high (right), Jax low (left), hall + window behind"),
 ("L", "3-05", 0.3, "Jax: elbow on counter, full charm, leans in"),
 ("SHOT", "A05", "cu_mira", "MCU MIRA (warm hall behind), flat"),
 ("L", "3-06", 0.15, "Mira: flat, one brow down; doesn't look up from the form"),
 ("B", 0.5, "Jax: a blink, recalculating"),
 ("SHOT", "A06", "cu_jax", "MCU JAX (reverse three-quarter)"),
 ("L", "3-07", 0.15, "Jax: a wounded finger-point at her"),
 ("B", 0.4, "Mira: unmoved"),
 ("SHOT", "A07", "cu_mira", "MCU MIRA"),
 ("L", "3-08", 0.2, "Mira holds up his own form, taps the line"),
 ("SHOT", "A08", "cu_jax", "MCU JAX"),
 ("L", "3-09", 0.2, "Jax: 'very distant' — points far off without a blink; 'Look—' leans in confidential"),
 ("L", "3-11", 0.25, "Jax: finger up, 'Section twelve' with a little flourish"),
 ("SHOT", "A09", "two_shot", "TWO-SHOT"),
 ("L", "3-12", 0.3, "Mira: deadpan, looks at him over the form"),
 ("B", 0.6, "Jax: does not blink"),
 ("L", "3-13", 0.25, "Jax: confidential half-whisper, eyebrows"),
 ("SHOT", "A10", "cu_mira", "MCU MIRA: the almost-smile (anticipation, mouth corner twitches, suppressed)"),
 ("B", 1.1, "GAG BEAT: she almost smiles. Doesn't. Pulls the keyboard over"),
 ("SHOT", "A11", "insert", "INSERT: her screen: VALE, JAX. MASTER, COURIER CLASS. The record begins seven years ago; above it the fields are empty"),
 ("B", 1.6, "screen scrolls up into empty fields"),
 ("SHOT", "A12", "cu_mira", "MCU MIRA, slower, interested now"),
 ("L", "3-18", 0.0, "Mira, slower; eyes come up to him"),
 ("SHOT", "A13", "cu_jax", "MCU JAX"),
 ("L", "3-19", 0.2, "Jax: shrug, easy grin"),
 ("B", 0.6, "Mira studies him"),
 ("SHOT", "A14", "two_shot", "TWO-SHOT"),
 ("L", "3-20", 0.3, "Mira: quiet, holding his look"),
 ("B", 1.2, "THE LOOK: she looks one beat longer; he notices; she notices him noticing"),
 ("B", 0.5, "GAG/BUTTON: she stamps. THUNK. SEIZED (camera bump)"),
 ("L", "3-24", 0.15, "Mira: brisk, back to business"),
 ("B", 1.6, "Jax goes (exits frame left with a two-finger salute)"),
 ("SHOT", "A15", "insert", "INSERT: Mira's battered notebook from her drawer: page after page of addresses, OWNER: —; she writes 41. THE SILVER HATCHET. OWNER: —"),
 ("B", 3.0, "pen writes the entry"),
 ("B", 0.8, "Noakes' shadow falls across the page; he bends in"),
 ("SHOT", "A16", "two_shot_noakes", "MS: Noakes bends into frame behind Mira, tall, tired; looks at the notebook like a cigarette"),
 ("L", "4-04", 0.2, "Noakes: soft, pained"),
 ("L", "4-05", 0.3, "Mira: doesn't turn round"),
 ("B", 0.5, "Noakes sighs"),
 ("L", "4-06", 0.3, "Noakes: kindly, as if to a child"),
 ("SHOT", "A17", "insert", "INSERT: the board: RIM PORT CUSTOMS — DAYS WITHOUT INCIDENT: 1,094"),
 ("B", 1.0, "Noakes looks up at the board with something like love"),
 ("SHOT", "A18", "two_shot_noakes", "MS Noakes + Mira"),
 ("L", "4-07", 0.1, "Noakes: a prayer, eyes on the board"),
 ("SHOT", "A19", "wide", "WIDE: far down the hall the tiny man on the scale throws up his arms"),
 ("L", "3-25", 0.4, "BUTTON: the Baron, distant, outraged, echoing"),
 ("SHOT", "A20", "two_shot_noakes", "MS Noakes closes his eyes"),
 ("B", 2.0, "BUTTON: Noakes closes his eyes; Mira's pen keeps writing"),
]
TITLE = [("SHOT", "T01", "title", "TIME-CUT CARD: 'LATER — THE OUTER RIM' over the real Earth plate"), ("B", 2.0, "title")]
B = [
 ("SHOT", "B01", "rim_wide", "WIDE: two suited figures on a boulder at the edge of the world, clear bubble helmets, the tricorn strapped on top of the Baron's dome; real NASA Earth low on the lunar horizon fills the frame"),
 ("B", 3.2, "establish; low-gravity stillness; suit fans"),
 ("B", 0.5, "SFX: private-channel click"),
 ("SHOT", "B02", "rim_baron", "MCU BARON inside his helmet, Earth reflected in the glass"),
 ("L", "21-01", 0.2, "Baron: gentle, looking at Earth"),
 ("L", "21-02", 0.3, "Baron: plainly, turning to Jax"),
 ("SHOT", "B03", "rim_jax", "MCU JAX inside his helmet"),
 ("L", "21-03", 0.25, "Jax: flat, eyes on Earth"),
 ("SHOT", "B04", "rim_two", "TWO-SHOT side by side on the boulder, Earth between them"),
 ("L", "21-04", 0.3, "Baron: patient"),
 ("L", "21-05", 0.3, "Baron: the thin ones in waiting rooms (v3 stem of the v4 beat)"),
 ("B", 0.6, "Jax, after a moment"),
 ("L", "21-06", 0.0, "Jax: 'Tell me one.'"),
 ("SHOT", "B05", "rim_baron", "MCU BARON: genuinely surprised, then settling, delighted, the voice opening up"),
 ("B", 0.7, "REACTION: the Baron's eyebrows go up behind the glass; moustache lifts"),
 ("L", "21-10", 0.0, "Baron: Ochakov — hands begin to draw the fortress in the air"),
 ("L", "21-11", 0.3, "Baron: '...and when it fired, I jumped on the ball' — CUTAWAY starts on 'when it fired'"),
 ("SHOT", "B06", "cutaway", "CUTAWAY (engraving style, paper theatre, the younger magnificent Baron): fortress, great cannon fires, he leaps astride the ball"),
 ("L", "21-12", 0.15, "Jax V.O., laughing already (stays on cutaway)"),
 ("L", "21-13", 0.2, "Baron V.O., deadly serious: astride, like a horse but rounder (cutaway: riding pose)"),
 ("L", "21-14", 0.3, "Baron V.O.: doubts (cutaway: he looks down at the fortress, gallows sketch in a thought)"),
 ("L", "21-15", 0.3, "Baron V.O.: 'when a ball came past from their side' (cutaway: the other ball approaches) — 'I changed' (the swap)"),
 ("B", 3.0, "CUTAWAY GAG, no words: he hops from one ball to the other like changing trams, lifts his hat to the Turks"),
 ("SHOT", "B07", "rim_jax", "MCU JAX, delighted, disbelieving"),
 ("L", "21-16", 0.1, "Jax"),
 ("SHOT", "B08", "rim_baron", "MCU BARON with dignity"),
 ("L", "21-17", 0.2, "Baron: 'In mid-air. And rode it home.' (2 s cutaway insert: riding the second ball home) 'Earth says I rode one there and back.'"),
 ("L", "21-18", 0.25, "Baron: the punchline, a tiny bow of the helmet"),
 ("SHOT", "B09", "rim_jax", "MCU JAX: the real laugh, head back inside the helmet"),
 ("L", "21-LAUGH", 0.2, "Jax laughs in spite of himself (NEW Kokoro line, needs listening)"),
 ("SHOT", "B10", "rim_two", "TWO-SHOT"),
 ("L", "21-19", 0.3, "Baron: quiet, pleased"),
 ("L", "21-20", 0.35, "Jax: still smiling"),
 ("L", "21-21", 0.3, "Baron: simply"),
 ("SHOT", "B11", "rim_earth", "THE REAL EARTH, low on the horizon, the two small figures in silhouette at frame edge"),
 ("B", 3.0, "SILENCE: three full seconds; neither moves (suit fans only)"),
 ("SHOT", "B12", "rim_baron", "MCU BARON, lightly, so it can be taken as a joke"),
 ("L", "21-22", 0.0, "Baron: the promise"),
 ("SHOT", "B13", "rim_baron", "MCU BARON: helmet turns, Earth sits in the reflection on his glass"),
 ("L", "21-26", 0.4, "Baron: warm"),
 ("SHOT", "B14", "rim_jax", "MCU JAX"),
 ("L", "21-27", 0.15, "Jax: light"),
 ("SHOT", "B15", "rim_baron", "MCU BARON, gently, looking right at him"),
 ("L", "21-28", 0.3, "Baron"),
 ("SHOT", "B16", "rim_jax", "MCU JAX: no answer ready; Earth shifts a hair"),
 ("B", 3.2, "HOLD: nothing on the channel; fade out"),
]

def build(events, t0, part):
    shots, lines, beats = [], [], []; t = t0; cur = None
    for ev in events:
        if ev[0] == "SHOT":
            if cur: cur["end_s"] = round(t, 3); shots.append(cur)
            cur = {"id": ev[1], "part": part, "kind": ev[2], "desc": ev[3], "start_s": round(t, 3), "business": []}
        elif ev[0] == "B":
            beats.append({"at_s": round(t, 3), "dur_s": ev[1], "what": ev[2], "shot": cur["id"]})
            cur["business"].append({"at_s": round(t, 3), "what": ev[2]}); t += ev[1]
        else:
            lid, gap, what = ev[1], ev[2], ev[3]
            f, who, text = NEW[lid] if lid in NEW else stem(lid)
            t += gap; d = sf.info(f).duration
            lines.append({"id": lid, "who": who, "start_s": round(t, 3), "dur": round(d, 3), "text": text, "src": f,
                          "shot": cur["id"], "business": what, "new_line": lid in NEW})
            cur["business"].append({"at_s": round(t, 3), "what": what}); t += d
    cur["end_s"] = round(t, 3); shots.append(cur)
    return shots, lines, beats, t

shA, lnA, bA, tA = build(A, 0.0, "A")
shT, _, bT, tT = build(TITLE, tA, "title")
shB, lnB, bB, tB = build(B, tT, "B")
lines = lnA + lnB
cut = [b for b in bB if b["shot"] in ("B06",)]
cutaway_beats = []
def at(lid, frac=0.0):
    l = [x for x in lines if x["id"] == lid][0]; return round(l["start_s"] + frac * l["dur"], 2)
cutaway_beats = [
  {"beat": "cutaway starts: 'when it fired'", "at_s": at("21-11", 0.55)},
  {"beat": "jumps on the ball", "at_s": at("21-11", 0.85)},
  {"beat": "astride, like a horse but rounder", "at_s": at("21-13")},
  {"beat": "doubts", "at_s": at("21-14")},
  {"beat": "the other ball passes", "at_s": at("21-15", 0.15)},
  {"beat": "changed (the swap, mid-air)", "at_s": at("21-15", 0.92)},
  {"beat": "hat to the Turks, wordless gag", "at_s": at("21-15", 1.0) + 0.3},
  {"beat": "cutaway ends", "at_s": [s for s in shB if s["id"] == "B06"][0]["end_s"]},
  {"beat": "rode it home (2 s insert inside B08)", "at_s": at("21-17", 0.12)}]
# the cutaway cuts in mid-line, on "when it fired"
for i, sh in enumerate(shB):
    if sh["id"] == "B06":
        t_in = cutaway_beats[0]["at_s"]; shB[i - 1]["end_s"] = t_in; sh["start_s"] = t_in
        for l in lines:
            if l["id"] == "21-11": l["shot"] = "B05 -> B06 (cut on 'when it fired')"
gags = [{"what": "the stamp THUNK", "at_s": [b for b in bA if b["what"].startswith("GAG/BUTTON")][0]["at_s"]},
        {"what": "the almost-smile", "at_s": [b for b in bA if b["what"].startswith("GAG BEAT")][0]["at_s"]},
        {"what": "Baron, distant: 'I used to be taller!'", "at_s": at("3-25")},
        {"what": "Noakes closes his eyes", "at_s": [b for b in bA if b["what"].startswith("BUTTON: Noakes")][0]["at_s"]},
        {"what": "Jax's real laugh", "at_s": at("21-LAUGH")}]
silence = [b for b in bB if b["what"].startswith("SILENCE")][0]
SL = {"name": "E01-sample5", "episode": "E01", "mix_version": 3,
      "note": "SAMPLE 5 sound timeline (stage 2a, frozen after hand-back). Part A = v4 scene 3 (customs desk, with Noakes), Part B = v4 scene 13 (outer rim, cannonball). Built by production/tools/toon/build_sample5.py.",
      "vars": {"SCRATCH": S, "REPO": R}, "duration_s": round(tB, 3),
      "parts": {"A": [0.0, round(tA, 3)], "title": [round(tA, 3), round(tT, 3)], "B": [round(tT, 3), round(tB, 3)]},
      "dialogue": lines, "shots": shA + shT + shB, "beats": bA + bT + bB,
      "silences": [{"at_s": silence["at_s"], "dur_s": silence["dur_s"], "what": "three seconds on the real Earth after 'You are the audience.'"}],
      "cutaway_beats": cutaway_beats, "gags": gags,
      "sfx_cues": [{"what": "customs stamp THUNK", "at_s": gags[0]["at_s"], "src": "${SCRATCH}/e01/sfx/customs_desk_stamp_heavy_a.wav"},
                   {"what": "private channel click", "at_s": [b for b in bB if "click" in b["what"]][0]["at_s"], "src": "${SCRATCH}/e01/sfx/radio_private_channel_click.wav"}],
      "loudness": {"integrated": -16.0, "true_peak_ceiling": -2.0},
      "radio": "Part B lines are the suit-radio treated stems already (file_treated); the new laugh was given the same narrow-band treatment."}
json.dump(SL, open(f"{R}/episodes/E01/sample5-shotlist.json", "w"), indent=1)
# dialogue guide
SR = 48000; N = int((tB + 0.5) * SR); mix = np.zeros(N)
for l in lines:
    a, sr = sf.read(l["src"], always_2d=True); a = a.mean(1)
    if sr != SR:
        from scipy.signal import resample_poly; a = resample_poly(a, SR, sr)
    s = int(l["start_s"] * SR); mix[s:s + len(a)] += a[:N - s]
pk = np.abs(mix).max(); mix = mix / pk * 0.7 if pk > 0.7 else mix
sf.write(f"{S}/s5/sample5-dialogue-guide.wav", mix.astype(np.float32), SR, subtype="PCM_24")
print("A", round(tA, 1), "title", round(tT - tA, 1), "B", round(tB - tT, 1), "total", round(tB, 1), "lines", len(lines))
