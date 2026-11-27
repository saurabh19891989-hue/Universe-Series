# E01 sound effects: mixing note

Nobody has listened to any of this. Levels are objective suggestions to be set by ear.

## The vacuum rule (the creative law of this episode)
Exteriors have NO sound. In scenes 9, 21, 24, 26, 29 (and the glimpses in 8, 23) there is no engine,
no footstep, no wheel, no cable, no hatchet, no ramp heard from outside. What may be heard:
- the suit: `suit_fan_breath_*_loop` (the one steady sound of every exterior shot), radio clicks, hiss;
- the cab or ship air: `rover_cabin_hum_*`, creaks, heater, frost, headlamp switch, trunk, airlock;
- the structure: files marked `conducted_vacuum_rule: true` in sfx-index.json are low-passed so they
  read as felt through the hull and seat (grapple thunk and tension groan, line parting, landing thud,
  lift-off, clamp, engine). Their energy above 2 kHz is under 3%, checked by the build script.
- Scene 9 knock and the held arc in 29 have no score and no effects at all. Silence is the joke.
- Do not add reverb to anything outdoors. Hall reverb (`customs_hall_reverb_tail_ir.wav`) is for hall dialogue only.

## Levels relative to dialogue (dialogue at -16 LUFS integrated)
Every file is exported at -6 dBFS peak, so it is far too loud as it stands. `sfx-index.json` carries,
per file, `mix.gain_db_to_apply` (the gain that puts it at the suggested level). Rule of thumb:

| Class | Suggested level in the mix | Examples |
|---|---|---|
| Room tones, beds (loops) | 18 to 24 dB under dialogue (-34 to -40 LUFS) | bridge, cargo hold, hall, inn |
| Suit fan/breath loops | about 22 dB under (-38 LUFS); duck a further 3 dB during radio speech | suit_fan_breath_* |
| PIP lens glow bed | -42 LUFS, keyed up 3 to 4 dB when he speaks | pip_lens_glow_bed_loop |
| Open-channel hiss | -44 LUFS, under the filtered voice | radio_open_channel_hiss_loop |
| Dead air (1.3 s) | -52 LUFS, barely there: it must read as an open line, not as silence | earth_call_dead_air_1p3s |
| Prop one-shots (stamps, relays, clicks, bells) | peaks 8 to 12 dB under dialogue peaks | pip_stamp_*, relay clicks |
| Story hits (stamp THUNK for SEIZED, padlock open, knocks, line snap) | peaks 6 to 9 dB under dialogue peaks | |
| Conducted hull effects | peaks about 8 dB under dialogue peaks, but low-end heavy: check on a small speaker | grapple_*, liftoff, landing |
| Klaxon | -30 LUFS bed; never above dialogue; it is alarming by pattern, not by level | klaxon_seal_the_port_loop |
| Smash cut to MAIN TITLE | peak at 0 to -3 dB (it is the loudest thing in the episode) | smash_cut_main_title_hit |
| Interface ticks and blips | peaks 10 to 14 dB under dialogue peaks | ui_* |

## Radio voices
Use `radio-voice-presets.json` (ffmpeg and sox chains with their measured response) or the two IR files.
Suit radio is narrow (about 500 Hz to 2.7 kHz at -6 dB), open channel is wider, the cab is dry.
Bracket every radio line with `radio_click_on` and `radio_click_off`. `radio_private_channel_click`
is the distinct sound for scene 21 only.

## Loops
All loop files are exact: play with no crossfade. Pulsed loops (klaxon, clock, hold tone) have a
beat that falls where the loop restarts by design. Tonal beds use whole numbers of cycles, noise beds
use an internal equal-power crossfade; checked by joining the file to itself and measuring the step.

## Known gaps
- `earth_call_dead_air_1p3s` and the room tones are only convincing in context.
- Footsteps are one pattern; the bounding in 23 and 29 is not made (those are on-screen silences or in-suit).
- No horn tune (music department). The post-horn effects here are only tick, drip and crack.
