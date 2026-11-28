# Animation format — code-driven cut-out puppets over real NASA video (test v1, 28 Nov)

First-hand test: Episode 1 cold open, 70 s. Files: `samples/e01/E01-animation-test-720p.mp4` (review copy),
`${SCRATCH}/e01/renders/E01-animation-test.mp4` (1080p master), shot list `episodes/E01/animation-test-shotlist.json`.
All free and in-house on the cloud machine (4 CPU, no GPU). No paid service, no video generator.

## Pipeline (three commands)
```
python3 production/tools/anim/e01_test_build.py                      # writes the shot list (rigs + shots)
python3 production/tools/anim/lipsync.py SHOTLIST ${SCRATCH}/anim/cues.json --rhubarb ${SCRATCH}/anim/rhubarb-dl/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb
python3 production/tools/anim/anim.py SHOTLIST --cues ${SCRATCH}/anim/cues.json --out ${SCRATCH}/anim/clips [--only ID..] [--preview 0.5]
python3 production/tools/edit/render.py SHOTLIST --out DIR --name NAME --workers 3   # cut, sound, subtitles, finish
```
- `lipsync.py`: Rhubarb Lip Sync 1.13 (MIT licence, CPU, ~1 s per line; the line's text is passed as a hint; dry
  stem used where a treated one exists). 9 mouth shapes (A–H, X) on the episode timeline plus a 48 Hz loudness
  envelope per line. Fallback if Rhubarb is missing: shapes from amplitude and spectral centroid.
- `anim.py` renders every shot with an `"anim"` block to `<id>.mp4` (no audio). The engine then uses those clips
  as ordinary `video` layers, so the sound mix, −16 LUFS, subtitles and the film finish are unchanged.
- `agy_image.py`: one picture via the Antigravity CLI (headless, sandbox, accept-edits, no shell), references
  copied in; only the generated picture it names is copied out.

## How a character rig is made
1. **Pictures**: one picture per pose, generated from the approved master as reference, character on flat
   chroma green (`#00FF00`), lips closed, eyes open, head ~30% of frame height. Sets with pure-black windows.
2. **Landmarks** (hand-read from a gridded crop, ~3 min per picture): two eye ellipses `[x, y, rx, ry]`, mouth
   seam centre, mouth half-width, angle, chin line, a face box, and for head motion an ellipse region + neck pivot.
   Props get their own parts (PIP: head and stamp arm, plus the lens circle; the ship: engine nozzles).
3. Everything else is code, per frame:
   - **Mouth**: the jaw is warped down by the shape's opening (stubble and lips move with it), then a mouth interior,
     teeth and tongue are drawn on the seam (ink outline in the illustrated look). Shapes cross-fade over 60 ms.
     Chosen over a mouth-sheet from the image tool: painted-in-code mouths always line up and cost no pictures.
   - **Eyes**: blinks every 1.8–4.2 s (skin-coloured lid sampled from the picture + lash line), eye darts every
     0.7–1.9 s, or scripted looks (`look_keys`).
   - **Head**: tilt and nod follow speech energy, slow sway when listening; body breathing and sway.
   - **Poses**: 2–3 pictures per character, swapped mid-shot with a 3-frame cross-fade, aligned at the eyes.
   - **PIP**: iris closes and the lens glows with his voice amplitude; head swivel and stamp arm on keyframes.
   - **Ship**: cut-out flown across NASA video on keyframed path with banking, bob and pulsing engine glow.
   - **Parallax**: real video (depth 0.25–0.3), set (0.6, softly defocused), character (1.2–1.4) under one camera
     with push, drift, roll and impact shake. Nothing in the test sits still ≥ 0.75 s (ffmpeg freezedetect on
     every clean clip, and ≥ 0.9 s on the master: none found).

## Pictures used in the test (10, all Antigravity CLI, ~30–50 s each, 3 in parallel ≈ 3 min)
Jax ×4 poses (front, finger up, palms up, three-quarter), PIP, the ship, Temi (in her office, not keyed), bridge wide,
PIP's console, one spare bridge angle (came out the same as the wide; unused). Look B used the existing approved
`assets/characters/jax/ref-front.jpg` (cut out with OpenCV GrabCut, no new picture). Codex was not needed.

## Speed (measured on this machine)
| step | cost |
|---|---|
| Animation clips (64 s, 21 shots) | ~9.5 CPU-s per video-s; 5:10 wall on 3 workers (first run) |
| Edit engine (sound, subtitles, finish) | ~14.5 CPU-s per video-s; 5:37 wall on 3 workers (first run) |
| **Total** | **~24 CPU-s per second of video** |
| Re-cuts | only changed shots re-render (B1 alone: ~75 s + ~2 min engine) |

## What a 35-minute episode would need
- **Pictures**: ~4 poses × ~8 speaking characters + 2 angles × ~12 places + ships/props/inserts ≈ 70–80 pictures
  for Episode 1; later episodes reuse rigs, ~25–40 new each. About 1–1.5 h of picture making (parallel, agy).
- **Rigging**: ~3–5 min per pose picture by an agent reading gridded crops ≈ 4–6 h for Episode 1. Worth automating
  with a free face-landmark model (e.g. MediaPipe, CPU) before episode 2; then rigs take seconds.
- **Shot list**: ~300–400 shots; an Opus builder ~3–5 h per episode (blocking, plates, poses, looks).
- **Render**: 2,100 s × 24 CPU-s ≈ 14 CPU-hours ≈ 4.7 h wall on 3 workers (overnight-sized).

## NASA video used (all already logged in `assets/e01-plates.json`; audio discarded)
- Lee Lincoln Scarp flyover (NASA/GSFC SVS; David Ladd, Tom Waters, Ernie Wright), from 16 s and 23 s — ship shots.
- Artemis II Lunar Flyby visualization (Ernie Wright, NASA SVS), from 27 s — Moon in the windows.
- Artemis II: Moments Around the Moon (NASA), only 31.6–34.8 s (Earth through Orion's window), cropped so no
  people, text or logo show — Earth in the windows. Old film: `C22_BanksAndCred` (Prelinger, public domain, in
  `assets/archive-vault.json`), 2.95 s.

## Known weaknesses
- Faces are flat cut-outs: head turns are tilts of one drawing, never a real turn; arms only change by pose swaps.
- Mouth is a drawn shape; good on the illustrated look, visibly pasted on the photoreal one (Look B), where the jaw
  stretch also smears stubble.
- The Earth plate is cropped hard from 1080p Orion video, so it is soft; a faint dark Orion window corner shows.
- Lip-sync accuracy is Rhubarb's; timing comes from the same line placement the mix uses. Nobody has listened.
- Sets are single paintings: the camera cannot move far inside a room.
