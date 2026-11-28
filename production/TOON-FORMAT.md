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

---

# Test 4 — painted pose library on the same scene (28 Nov, evening)

Sample: `samples/e01/E01-toon-test4-720p.mp4`; 1080p `${SCRATCH}/e01/renders/E01-toon-test4.mp4`.
Same scene, stems, mix and timing as test 3, so the two compare directly. Timing file
`episodes/E01/toon-test4-shotlist.json` (written by `build_e01_desk4.py`). Code:
`toon4.py` (renderer), `rigs4.json` + `build_rigs4.py` (landmarks), `toon4_pictures.py`
(every picture prompt), `paintface.py` (a copy of test 1's painted-face engine),
`landmark_sheet.py` (gridded crops for reading landmarks), `mix_audio.py` (unchanged).

## Method chosen: pose library, not a cut-up rig
- **All visible character art is a picture.** Every held pose is one painted picture from the
  Codex CLI, with the master (and the first approved design) as references, on chroma green,
  in test 1's graphic-novel style line. Bodies, hands, clothes and faces all come from these.
- Between poses: snappy pose-to-pose swaps (a hard cut plus a squash-and-settle pop; a 2-frame dissolve was tried and ghosted),
  with keyed lean/squash/overshoot on top. Poses are lined up at the neck, so the head stays
  put while the body changes underneath. In wide shots they are lined up at the feet.
- On top of every pose the face moves: Rhubarb mouths drawn on the painted lips, with jaw
  warp (from test 1, mouths opened 1.9x wider than test 1), blinks, eye darts and head
  tilt/nod that follows speech. Breathing and sway run all the time.
- Walk: one 6-drawing walk-cycle sheet, cut automatically, played as the character
  crosses the floor (about 5.5 drawings a second).
- Why not cut one picture into jointed limbs: the hidden areas under each limb have to be
  invented, the joints never match the painted shading, and the result moves like test 3's
  rubber tubes. Held painted poses look like the masters and read like limited TV animation.
- Sets are paintings (wide hall, closer desk view). The black window is keyed and the NASA
  plate placed behind it. The counter is cut out as a foreground layer, which also hides where
  the knee-up pictures end.
- Exterior: the ship flies a keyed path. After touchdown it is pinned to a patch of ground
  tracked through the NASA plate with optical flow, so it stays landed while the camera flies on.

## Pictures and hand work
- This test: **29 pictures, all Codex, none failed** (Jax 17 incl. a 6-pose walk sheet, of
  which 5 full-body gesture poses went unused after knee-up versions were made; Mira 9; ship 1; sets 2). Codex 5-hour window 18% used after.
- Per character: about 10–15 pose pictures for one scene's acting (idle, 6–8 gestures, 2
  close-ups, a walk sheet). A season's regular would build a library of about 40–60 poses
  reused every week, plus 5–10 new poses per episode.
- Landmarks (eyes, mouth, chin, head ellipse, neck, anchor) are read by eye from gridded
  crops: about 2 minutes per pose, about 50 min for this test's 20 face poses. This is the
  thing to automate next (a free face-landmark model; none was reachable today).
- Hours per character for one scene's library: about 1.5 h (pictures run 4 at a time,
  about 1 min each; most of the time is checking and landmarks).

## Render speed
Measured on the full 56 s (1344 frames, 1080p, 4 workers): **21.3 CPU-seconds per second of
video** (draw + composite; x264 on top). Wall time 6.4–9.9 min for 56 s (7–11 s per second of video).
Pose pictures are cached per worker. Lip sync is reused from test 3.

## A 35-minute episode would need
- Pictures: about 150–250 (6–8 characters × 15–25 poses, plus 15–20 sets/angles, ship and
  props). At roughly 1 min each, 4 at a time, that is about 1–1.5 hours of Codex time. It may
  be more than one day's image limit on a Plus plan (a 24-hour image cap was hit at about
  150–170 on 27 Nov), so plan two days or reuse libraries.
- Landmarks: about 6–8 h by hand per episode at first, mostly a one-time cost for the
  regulars. Automating it is the main saving.
- Posing and timing: about 6–10 h per episode (choosing which held pose plays on which
  line). Faster than test 3 because poses are pictures, not keyed joints.
- Render: 2,100 s × 21.3 ≈ 12.5 CPU-hours → about 3.5–5 hours on 4 cores. One
  overnight run per episode; shots can be re-rendered on their own.

## Known gaps (Test 4)
- Pose swaps are visible as swaps (limited animation): there are no in-betweens.
  Arms jump from pose to pose with a squash pop.
- Walk is 6 drawings (about 5.5 a second): feet slide a little between drawings.
- Small differences between pose pictures (costume details, hair, light) "boil" at each swap.
- Painted mouths are drawn over closed lips; the far-side mouth corner is weak in strong
  three-quarter views.
- Close-ups of the set are softened on purpose (depth of field), because the 1672-px set
  pictures cannot hold a 2x zoom sharply.

---

# Sample 5 — animated redesign, 2:42 sample (28 Nov, night)

Files: `samples/e01/E01-sample5-720p.mp4`, sheet, frames in `samples/e01/sample5-frames/`, designs
`E01-sample5-characters.jpg`; frozen sound timeline `episodes/E01/sample5-shotlist.json`. Code in
`production/tools/toon/`: `s5_pictures.py`, `s5_jobs.py`, `s5b_jobs.py` (every prompt), `s5_landmarks.py`
(automatic face landmarks), `s5_faces.py` (seamless face sets), `s5_transfer.py` (medium-shot lip-sync),
`s5_stage.py` (pose keys on the frozen timeline), `s5_build.py` (renderer), `build_sample5.py`, `s5_animatic.py`.

## Method
- **Look:** variant B (pushed animated style) for every character; approved by the showrunner.
- **Bodies:** pose libraries, one picture per held pose (knee-up for dialogue, full body for walks).
  Pose changes cut on the frame with a squash-and-settle pop; for the big moves a drawn in-between
  picture plays for about 2 frames. Nothing is dissolved or flow-morphed (test 4 and stage 1 ghosted).
- **Faces:** per-character mouth sets made as picture EDITS of the close-up (A–H, smile, shout), plus
  blink and brow keys. `s5_faces.py` lines each edit up to the base, pastes only the changed region,
  colour-matches it on a ring and feathers it: no lip seam. `s5_transfer.py` carries the close-up set
  onto every medium-shot pose (similarity fit on lips/eyes, paste only what changed). Landmarks come from
  MediaPipe Face Landmarker (PyPI, Apache-2.0, CPU), with crop-and-enlarge for small faces; the Baron's
  moustache defeats it, so his two pictures were marked by hand.
- **Walk:** a 12-drawing cycle (two 6-drawing sheets) played on twos; each drawing is placed by the
  measured ground-contact shift so the planted foot stays put. Most walking is the knee-up tracking cheat.
- **Backgrounds:** real NASA video (Earthrise visualisation, logged in `assets/toon-test-plates.json`)
  keyed into the hall window and framed full-screen on its sunlit side for the outer rim.
- **Cutaway:** engraving-style cut-outs (cannon, young Baron in 6 poses, balls, backdrop) in a paper
  theatre: parallax, arcs, shadows, a card proscenium.

## Pictures and time
- This build: about 150 Codex pictures (stage 1: 40; stage 2b: about 110), none refused.
- Per lead character, for a full scene: 1 design, 2 close-up bases, ~12 mouth/eye edits per base,
  8–10 knee-up poses, 2–3 drawn in-betweens, walk sheets = about 40 pictures. A guest: about 15.
- Per finished minute (this sample): about 55 pictures.
- Hours: pictures run 4 at a time at about 45 s each (about 15 min of Codex per 60 pictures); checking,
  landmarks and fixes about 1 h per lead; staging the keys about 30–40 min per minute of scene.

## Render speed
RENDER5_LINE

## A 24-minute episode would need
- Pictures: about 600–900 for the first episode (8 characters, 10 sets, cutaways), then about 300–400
  for later ones as libraries are reused. Several days of a Plus plan's image limit; plan it.
- Staging: about 12–16 h of pose keying per episode; render overnight.
- A human must listen to every line; the laugh in this sample is a TTS stand-in.
