# Free look test — findings (summary)

Written by the main session from the look agent's hand-back, plus the showrunner's own view
of the images. Shared 4-core CPU, no GPU. No audio in the clip.

## Open first
1. `look-test.mp4` (21 s, four shots), then `still-C.jpg` (best look) and `still-B.jpg` (puppet two-shot).
2. `r1-horde-flux-sheet.jpg` and `r1-horde-jax-consistency.jpg` — best free character art and how it drifts.
3. `r2-jax-consistency.jpg` (local reference tests) and `r3-pip-expressions.jpg` (code-built puppet).

## Showrunner's view
- `still-C` (graphic-novel ink art, rim light, defocused NASA plate, grade, letterbox) looks
  genuinely cinematic. This is the style to pursue.
- `still-B` (code-drawn vector Jax) looks like an explainer video, not a premium show. PIP as a
  code-built puppet is charming and can stay that way.
- Mixing the two styles in one film looks like two productions. Pick the ink style for people.

## Routes
| Route | Result |
|---|---|
| AI Horde, FLUX.1-schnell (free, anonymous) | Best art. 8.5–12 min per image in the queue. Same seed + description keeps costume, face drifts. |
| Pollinations (free, anonymous) | Low resolution, forced watermark, unclear terms. Avoid. |
| Hugging Face free | Needs a token; not tested further. |
| Local CPU, DreamShaper 8 + LCM | 34 s per 512 px image when quiet; painterly, weaker. IP-Adapter Plus-Face 0.4 is the best free face lock but mutes expressions. |
| Upscale + cut-out | Real-ESRGAN 4x in ~200 s with crisp lines; rembg cut-out in 16 s. Works. |
| Code puppets | Perfectly consistent, 8 mouth shapes, blinks; PIP good, humans look cheap. |

## Render speed
14.4 s of compute per second of 1080p video on one process. A 35-minute episode is about
8.4 h on one process, about 3 h with 3–4 in parallel; 2–3x faster is possible by caching layers.

## Licences (as reported)
FLUX.1-schnell Apache-2.0; DreamShaper 8 / SD1.5 CreativeML OpenRAIL-M; IP-Adapter Apache-2.0;
Real-ESRGAN BSD-3; rembg MIT; SD-Turbo / SDXL-Turbo non-commercial (excluded). AI Horde and
Pollinations terms text could not be retrieved in full. NASA plates used: art001e002581 and
art001e002160 (Artemis I, credit NASA).

## Weaknesses of the free route
Faces drift between images; no lip-sync on painted art (it stays a motion comic); slow free
queue; hands and poses need retries.

## What would fix them
A character-reference image model (being tested now with Nano Banana on the owner's Google
credit), then lip-sync and image-to-video for hero shots.

Scripts: `production/tools/look/` (hosted_gen, local_gen, upscale_cutout, puppets, cinema, make_sheets).
