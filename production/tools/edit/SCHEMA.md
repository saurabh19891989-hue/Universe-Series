# Edit engine — shot list schema (v1)

One command:

```
python production/tools/edit/render.py SHOTLIST.json --out DIR [--only SHOT_ID ...] [--workers 3]
       [--name NAME] [--review small.mp4] [--stills 3.0,8.0 --stills-dir DIR] [--preview 0.1,0.9] [--force]
```

- `--preview F,...` writes graded JPG frames of each shot (or the `--only` shots) at shot-local
  fractions to `DIR/preview` and stops. Use it for look checks: no encode.
- Re-running only re-renders shots whose hash changed (shot JSON, engine code, the files it reads,
  the speech envelope it reacts to). `--only` forces those shots. Segments: `DIR/segments/`.
- Output: `DIR/NAME.mp4` (1920x1080, 24 fps, H.264 high, CRF 18, yuv420p, AAC 192k 48 kHz stereo),
  `DIR/NAME.srt` (never burned in), `DIR/NAME.log.json` (render speed, placeholders, sync table,
  loudness, credits).
- Needs: python3 with numpy, opencv, pillow, scipy, soundfile; ffmpeg. Max 3 workers on the shared
  machine; encoders run `nice`, single-threaded.

Paths may use `${REPO}` and `${SCRATCH}` (set in `vars`). Coordinates are **normalised to the
base layer** (0..1 of its width and height) unless stated.

## Top level

| field | meaning |
|---|---|
| `name`, `episode`, `unit` | labels; `name` is the output file stem |
| `vars` | path variables, e.g. `{"SCRATCH": "/tmp/.../scratchpad"}` |
| `output` | `width`, `height`, `fps`, `crf`, `preset`, `letterbox` (null = full 16:9, the default) |
| `finish` | film finish, applied once per frame after compositing: `grain` (0.02), `halation` (0.45), `weave_px` (0.45), `vignette` (0.38), `saturation` (0.88), `split_tone` (1 = the muted teal-and-amber look), `pre_gain`, `black_lift` |
| `dialogue` | `timing_sheet` (lines.csv), `file`, `scene`, `source_wav` (table-read act file to slice), `stems_dir` (final stems `<line_id>.wav` win over slices), `skip_kinds` (narration, sting), `offset_s`, `gain_db`, `overrides` {line_id: {`start_s` \| `shift_s`, `gain_db`, `skip`}} |
| `music`, `sfx` | global cues (absolute `start_s`), see Cues |
| `duck` | `music_db` (-12), `sfx_db` (-5): gain under dialogue (keyframed: attack 60 ms, release 450 ms) |
| `loudness` | `integrated` (-16 LUFS), `true_peak_ceiling` (-2.0 dBTP; result is checked < -1.5) |
| `credits` | strings collected into the log with each shot's `credits` |
| `shots` | ordered list; cut points are frame-exact from cumulative `duration_s` |

**Line ids** are `<scene>-<NN>`: NN is the 1-based row of that scene in `lines.csv`, narration rows
included, so ids never shift when narration is dropped. Lines are placed at their timing-sheet
time minus the scene's first row time, plus `offset_s`.

## Shot

| field | meaning |
|---|---|
| `id`, `scene`, `note` | labels |
| `duration_s` | length |
| `type` | REAL_FOOTAGE / SET_STILL / CHARACTER_STILL / TWO_SHOT / INSERT / DATA_VISUAL / TITLE / BLACK (informational; behaviour comes from layers) |
| `camera` | see Camera |
| `layers` | first = base (still / video / solid / gfx); then cutout, screen, text layers |
| `lights` | animated practicals, see Lights |
| `focus` | depth-masked rack focus |
| `grade` | per-shot override of any `finish` field, e.g. `{"exposure": -0.2, "saturation": 0.8}` |
| `motion_blur` | `[{"t0","t1","px","dir":"h"|"v"}]` for whips and impacts |
| `in`, `out` | `{"type": "cut"|"fade", "dur": s}` (fade = to/from black) |
| `audio` | `lines` (ids expected to START in this shot: checked, warned in the log), `music`, `sfx` cues with `at` = seconds from shot start |
| `credits` | credit lines for footage used |

## Camera

`{"from": {cx, cy, zoom, rot}, "to": {...}, "ease": "inout", "start_s", "end_s", "drift": {"amp_px", "period_s", "rot_deg"}, "shake": [{"at", "amp_px", "decay_s", "hz"}]}`
or `{"keys": [{t, cx, cy, zoom, rot, ease}], ...}`.

- `cx, cy` = frame centre on the base layer; `zoom` 1 = base fills the frame (cover).
- Zoom interpolates in log space (constant perceived speed); default ease is smootherstep (no
  velocity jump at either end). Sub-pixel Lanczos warps, so no stair-step jitter.
- Push-in = zoom up; pull-out = zoom down; pan = cx change; hold = from == to plus `drift`.
- Moves the eye reads as calm: 3–8% zoom over 3 s. Over 15% in under 2 s reads as a punch-in.

## Layers

**Base still / video**: `{"kind": "still"|"video", "src", "crop": [x0,y0,x1,y1], "flip", "blur", "grade": {exposure (stops), gain [r,g,b], gamma, lift, sat}, "relight": [shape...], "window": {...}, "in_s", "speed"}`

Relight shapes: `{"shape": "ellipse", x, y, rx, ry}` / `{"shape": "rect", "rect"}` /
`{"shape": "polygon", "points"}` with `gain_in`, `gain_out` (number or rgb), `feather` (fraction of
width) or `feather_px`.

**Window** (composite a plate behind glass):
`{"key": "black"|"white", "thresh", "region": [x0,y0,x1,y1], "feather_px", "grow_px", "close_px", "max_regions", "glass_keep", "reflection", "plate": {...}}`

- The mask is found automatically: pixels near pure black (or blown white) in `region`, biggest
  connected area, holes filled, edge grown 1 px under the frame and feathered.
- `plate`: `src` (still or video), `x, y` (where the plate centre sits on the base), `scale`
  (plate width / base width), `rot`, `crop`, `flip`, `depth` (parallax, 0.3 = far), `blur`,
  `drift` {dx, dy, dzoom, drot over the shot}, `level` {black (crushed to 0), gamma, gain, tint}.
  A dark glass lifts the plate's black to the glass level; video plates loop.
- Black key: the base's glass pixels are screen-blended back on top (reflections stay on top);
  `reflection` adds a faint mirrored interior + sheen. White key: soft luma edge, so backlit hair
  keeps its glow.

**Cutout** (2.5D parallax): `{"kind": "cutout", "src", "mask": shape | "mask_src": png, "depth": 1.3, "place": {x, y, scale}, "fill_behind": true}`.
Depth 1 moves with the base; >1 nearer (moves more); <1 farther. `fill_behind` inpaints the base
under a cutout taken from the same still, so the parallax never reveals a double.

**Screen**: `{"kind": "screen", "src": clip_or_image, "gfx": {...placeholder...}, "quad": [[x,y]x4 clockwise from top-left], "res": [w,h], "spill", "treat": {scanlines, bloom, glass_black, tint, flicker}}`.
If `src` exists (data-visual agent's clip in `${SCRATCH}/e01/datavis/`), it plays; otherwise the
built-in placeholder `gfx` renders and the log says PLACEHOLDER. Placeholders: `bank_call`
(`temi`, `logo_until`, `freeze` [[t0,t1]], `freeze_t`), `readouts` (`labels`, `drop_at`), `report`
and `job` (typed `lines`, `cps`, `type_start`, `stamp_at`, `stamp`), `cargo` (`src`, `crop`).

**Text**: `{"kind": "text", "text", "size", "y", "t0", "t1", "fade_in", "fade_out", "track_from", "track_to", "track_s", "glow", "glow_color", "sub", "font"}` (output pixel space).

## Lights (base coordinates, applied before the camera)

| type | fields |
|---|---|
| `lens` | `x, y, r, color, on_at, on_dur, off_at, off_level, idle, env` (speaker name: brightness follows that speaker's speech envelope), `env_gain, glow_r, glow_gain, spill {r, off}` |
| `led` | small practical: `x, y, r, color, on_at, off_at, off_dur` |
| `die` / `revive` | `regions: [{rect, at}]`, `to` (dead level, 0.14), `dur` (stutter time), `desat` |
| `flicker` | `rect, depth, rate_hz, emissive_only` (only bright saturated pixels move) |
| `flash` | `at, dur, gain` |

## Focus

`{"regions": [shape + "depth"], "default_depth": 1.0, "from", "to", "t0", "t1", "strength", "ease"}` —
blur radius = |depth − focus| × strength (max sigma 9), blended from a blur stack.

## Cues

`{"id", "src", "start_s" | "at", "gain_db", "duck": true, "fade_in", "fade_out", "trim_s", "loop_s", "placeholder": "chime|shopbell|thunk|powerdown|click|blip|engine_cough|roomtone"}` —
when `src` is missing the placeholder sound is synthesised and logged. Effects default to
`${SCRATCH}/e01/sfx/<id>.wav`, so dropping the final file there replaces the placeholder on the next run.
