# TOON format — flat 2D puppet rig over real NASA video (TEST 3, 28 Nov)

Sample: `samples/e01/E01-toon-test-720p.mp4` (E01 scene 3, the customs desk, lines 1–17, plus
a 7 s exterior landing). Full 1080p: `${SCRATCH}/e01/renders/E01-toon-test.mp4`.
Code: `production/tools/toon/`. Pose-and-timing file: `episodes/E01/toon-test-shotlist.json`
(written by `build_e01_desk.py`). Plates log: `assets/toon-test-plates.json`.

## How a rig is made (what was chosen and why)
Hybrid: **picture-made head, code-made everything else.**
- The picture tool draws a head model sheet: front + three-quarter, flat colour, on white,
  with **no eyes, brows or mouth** (it obeyed this both times). `cut_parts.py` cuts the two
  heads out (flood fill of the white background). Hair, skin, nose, ears, stubble come from
  the picture, so the look stays the locked character.
- Eyes (whites, iris, pupil that moves, lids that blink and half-close, lash line), 4+ brow
  states (raise, inner tilt, one-brow-up asymmetry, any mix) and 9 mouth shapes (Rhubarb
  A–H + X) are drawn in code on the head, in the head's own pixel coordinates, in matching
  line colour/weight. Because they are code, they never drift and need no extra pictures.
- Body is vector shapes in code (`rig.py`, Skia): torso with pockets/zip/patches/belt and one
  shadow tone, upper/lower arm with elbow, 5 hand shapes (open, fist, point, holding the form,
  holding the stamp), hips, thigh/shin with 2-bone IK knees, boots. Pivots at shoulder,
  elbow, wrist, hip, knee, neck. Colours sampled from the design picture.
- Why not cut limbs out of a parts sheet: generated parts never line up at the joints and
  come back at different sizes; code limbs join cleanly at every angle and cost no pictures.
- Head turn: two drawn angles (front, three-quarter) swapped on a key, with a small squash.
  The three-quarter was consistent with the front in both cases. No profile or back yet.
- Secondary motion (deterministic, so any frame renders alone): breathing, idle sway, head
  micro-tilt, random blinks, eye darts, Mira's braid (7 linked segments that lag the body),
  the brass loupe swinging on its chain, jacket hem lag. Talking adds nothing yet beyond the
  mouth (talk-nod is wired but off).
- A rig file per character: `production/tools/toon/rigs/<id>.json` (proportions, colours,
  costume details, and the eye/brow/mouth/pivot coordinates on each head picture).

**Per character:** 2 pictures (head sheet; one full-body design for colours and the
approval sheet) + about 20–30 minutes of hand work to place eyes/brows/mouth/pivot and set
costume colours, once the engine exists. A set: 1 picture with the window painted pure
black, plus a desk/foreground polygon. Ship: 1 side-view picture.

## How a scene is posed and timed
- Dialogue starts come from `episodes/E01/dialogue-conform.json`; mouths come from
  **Rhubarb Lip Sync 1.13** (run on our final stems with the script text,
  `${SCRATCH}/toon/lips/*.json`; about 2.7 s CPU per line).
- Every pose channel is a key list `[time, value, ease, duration]`: `sh0/el0/sh1/el1`
  (shoulder/elbow, degrees), `hand0/1`, `lean`, `crouch`, `shrug`, `tilt`, `squash`, `turn`,
  `look_x/y`, `lid`, `brow`, `brow_tilt`, `brow_asym`. Eases: io, out, in, **back**
  (overshoot), **snap** (overshoot + settle), step. Anticipation = a small key the wrong way
  just before the move.
- Walks: give start/end x, time and number of cycles; feet are planted by construction (the
  stance foot is fixed on the floor, the other swings in an arc), with body bob and arm swing.
- Camera per shot: keyed centre/zoom on the painted set, handheld drift, shake on impacts.
- Real video: window plates are keyed into the black glass with parallax; exteriors are the
  plate full-screen with the cartoon prop on top. Cartoon-on-live-action is sold by a rim light
  in the plate's light colour, soft contact shadows, dust, engine glow, one shared grade and
  grain over everything.
- Posing this 49 s scene by hand-typed keys took about 25 minutes (first time, including
  deciding the acting). Expect 15–25 min of keying per minute of dialogue scene once used to it.

## Render speed (this machine, 4 CPU, no GPU)
Measured on the full 56 s test (1344 frames, 1080p, 2 workers, machine shared with other agents):
**30.5 CPU-seconds per second of video** for drawing + compositing (Python/NumPy/Skia, plus
x264 encode on top), **17.5 s wall per second of video** with 2 workers (16.3 min for 56 s).
Single still: about 1.3 s. Lip sync (Rhubarb): ~45 s wall for 17 lines with 2 jobs.

## A 35-minute episode would need
- Rigs: 6–8 characters per episode (5 regulars reused every week + 2–3 guests). Regulars are
  built once; each guest about 2 pictures and half an hour.
- Sets: 6–10 painted sets per episode (1 picture each, more if a set needs a second angle).
  Ship: one side view already; add a three-quarter and a rear view (3 pictures) for variety.
- Pictures per episode: about 15–25 (guests, sets, a few props). Well inside one day's limit.
- Pose work: the slow part. 35 min ≈ 25–30 min of dialogue scenes → roughly 8–12 hours of
  keying for one person/agent at this quality, less with reusable gesture presets (point,
  shrug, lean-in, double-take) — the next thing to build.
- Render: 35 min ≈ 2,100 s × 30.5 ≈ 18 CPU-hours → about 10 hours wall
  on 2 workers, about 5–6 hours on all 4 cores. Overnight per episode; parts can re-render
  alone (frames are independent). The code is unoptimised Python: most time is full-frame
  NumPy compositing, which could be cut 3–5x (crop to character boxes, fewer float passes).
- Audio as now (stems, score, effects, measured to −16 LUFS; a human must listen).

## Known gaps (what keeps this below broadcast cartoon)
- Bodies are simple tubes: no clothing folds, elbows/knees bend like rubber hoses; hands are
  basic and the same size at every angle; no overlapping fingers.
- Only two head angles; no profile, no back view, no up/down head tilt drawings.
- Mouth shapes are generic code shapes, not drawn per character; no tongue/teeth acting.
- Walks are mechanically correct but uniform (no personality, no foot roll).
- Acting is keyed by hand with few poses per line; broadcast shows have many more held
  poses and squash-and-stretch on the head.
- The set picture is soft when the camera zooms past about 2x (it is a 1376 px picture).
