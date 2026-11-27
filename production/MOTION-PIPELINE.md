# Motion pipeline — making a moving shot (v0, 27 Nov)

Owner (27 Nov): "we need moving things like a video, moving people, moving images ... use vibrant
videos of space footage ... real movie like cinematic video." Every shot must move. Three sources:

1. **Real NASA video** (moving space), from `assets/e01-plates.json`, only inside its `usable_ranges`.
2. **Image-to-video clips** made from an accepted still (faces stay as the still).
3. **Animated screens** from the data-visual agent (`${SCRATCH}/e01/datavis/`).

## 1. Image-to-video (LTX-2.5 space on Hugging Face, free ZeroGPU tier)

```
S=/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad
$S/motion/v/bin/python $S/motion/i2v.py --img STILL.jpg --prompt "..." --dur 5 --out $S/motion/out/NAME_raw.mp4 [--seed 7]
```
Wrapper used here: `$S/mv/gen.sh NAME STILL DUR SEED "PROMPT"` — runs one call, logs to `$S/mv/gen.log`,
strips the generated audio (`ffmpeg -an -c:v copy`) and writes a 6-frame sheet to `$S/mv/sheets/NAME.jpg`
to read before accepting. Never set, print or look for the token (the proxy injects it).

- Output: 1472x832, 24 fps, H.264, about 30 s per clip; starts exactly on the still.
- **Maximum `--dur` is 5** ("Value 6.0 is greater than maximum value 5.0"; rejected before any GPU use).
- Prompt recipe: the motion in order, plainly (who moves, what they do, what the camera does, what the
  light does), then "Photorealistic live-action film footage, natural human motion, the face stays exactly
  the same, no new people, no text." Any still with a black window/monitor that gets keyed adds
  "Locked-off camera, the window stays pure black." For non-speaking moments of a face add "lips stay closed".
- What worked (test `t1_jax`, from j004): bite, chew, eyes down to the sandwich; face consistent for 5 s;
  hands intact; the black window stayed black and keys cleanly frame by frame.
- Chewing moves the mouth: never put such a clip under that character's own dialogue (house rule).

### Allowance actually obtained — the blocker
- 27 Nov: **1 clip per day** (the test). The next call (5 s, 1472x832) was refused at 17:58 UTC:
  `You have exceeded your free ZeroGPU quota (272s requested vs. 105s left). Try again in 23:53:41.
  Subscribe to Hugging Face PRO to get 40 min of ZeroGPU quota a day`
  → reset about **17:52 UTC, 28 Nov**.
- A 5-s clip books 272 GPU-seconds. The free tier cannot make the ~10 clips one cold open needs per day.
  A shorter/smaller request (e.g. `--dur 3 --w 960 --h 544`) may book less: untested, try first after reset.
- Options for the showrunner/owner (not decided here): a paid HF PRO month (40 min/day ≈ 8 clips/day) only as
  a one-time booster; whether the owner's existing ChatGPT Pro (Sora video) can be used like the Codex stills;
  or spreading ~1–3 clips per day across days.

### Queue ready for the reset
`$S/mv/gen_queue.sh` holds the 10 remaining clips in priority order with their prompts and target shots
(PIP lens, bridge wide, over-the-shoulder monitor, eyes ECU, stamp, lens swivel, PIP/Jax two-shot,
half-smile, listen, coffee). It runs one call at a time and stops at the first refusal. Every shot in
`episodes/E01/coldopen-motion-shotlist.json` that is still a still carries `motion_pending`.

## 2. Using a clip in the edit engine
Base layer `{"kind": "video", "src": ".../NAME.mp4", "in_s": 0.0, "speed": 1.0, "loop": false, "grade": {...}}`.
Use the first or last part via `in_s`; slow to no less than 0.8x. 1472 → 1920 is a 1.30x scale (cubic warp
plus the finish sharpening); for a close-up generate from a close-up still, never crop deep.

**Engine change (27 Nov)** — `production/tools/edit/engine.py`, `Shot._video_window_mask`: on a `video`
base the black window key is recomputed on every frame, limited to the first frame's glass grown by
`track_px` (24 px) and blended with the previous mask by `smooth` (0.35), so a head crossing the window
occludes the NASA plate and the edge does not boil. Stills are unchanged (`per_frame: false` turns it off).

## 3. NASA video used in E01-coldopen-v2-motion
Pre-cut to 1920x1080, 24 fps, no audio (lanczos) in `$S/mv/plates/`:

| file | source range | use | credit line (from `assets/e01-plates.json`) |
|---|---|---|---|
| nasa_moonlimb.mp4 | jsc2026m000089 56.50–57.88 s | opening | NASA (Artemis II); library metadata gives no further credit |
| nasa_terrain.mp4 | jsc2026m000089 59.78–61.16 s (0.72x) | opening | NASA (Artemis II); library metadata gives no further credit |
| nasa_crater.mp4 | GSFC_20130306_Moons_m11218_Shadowed 41.9–43.7 s | "crater" line | Dan Gallagher, Chris Smith (NASA/GSFC) |
| nasa_a2.mp4 | a2_flyby_1min_2160p30 26–46 s | Moon in the windows, main title | NASA's Scientific Visualization Studio/Ernie Wright |

jsc2026 is MARGINAL in the manifest: only the two clean Moon-only passages are used (no crew, no logos,
no MET banners). a2_flyby and the crater clip are NASA visualisations built from LRO data — the "what was
real" note should say so.

Grade for vibrancy: per-layer `{"exposure": 0.25, "gain": [1.04,1,0.95], "sat": 1.25}` on real footage,
plates `level.gain 1.15`, warm tint; global finish saturation 0.88 → 1.02. Checked on frames: no clipping
on the Moon highlights.
