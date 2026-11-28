# E01 sample 5 (2:42): cue sheet and mix measurements

Score, effects and final mix for `episodes/E01/sample5-shotlist.json` (frozen, 162.441 s). Nobody has
listened to it. The agent that made it cannot hear, so every number here is a measurement.

**Files**
- Master: scratchpad `audio2/out3/sample5-mix.wav`. 48 kHz, 24-bit stereo, 7,797,168 samples
  (162.441 s, the shot list's exact length), starting at picture zero.
- Stems in the same folder: `sample5-stem-music.wav`, `-effects.wav`, `-dialogue.wav`.
- Review copies in `samples/audio/sample5/`:
  - `sample5-mix.mp3` (128 kbps, 2.6 MB);
  - `sample5-stem-music-only.mp3` and `sample5-stem-effects-only.mp3` (96 kbps, 1.9 MB each).

**Rebuild** (about 40 s for the cues and 50 s for the mix on the shared machine):
1. `python3 production/tools/music/render_sample5.py SCRATCH/audio2/out3`
2. `python3 production/tools/sfx/sample5_mix.py SCRATCH/audio2/out3 SCRATCH/audio2/out3`

**Code**
- Score: `production/tools/music/sample5_score.py`. One beat = one second, so every note sits at its picture time.
- Mix: `production/tools/sfx/sample5_mix.py`.
- Instruments:
  - VPO 3 orchestra and VCSL percussion (licences in `assets/audio-sources.json`);
  - FreePats guitar;
  - our synthesised bansuri, santoor, duduk and shehnai (`worldsynth.py`).
- Rooms: Voxengo Scala / Musikverein IRs for the score, Masonic Lodge for the customs hall.
- No new outside sources.

## Cue sheet
Themes: JAX = Jax's swing head (D Dorian); MIRA = the Sa-Re-Ga-Pa-Dha cell and her santoor "clock"; HEART = the Baron's heart theme (E minor); MARCH = the Baron's cannonball march; HOOK = main theme.

| In | Out | Cue | What plays | Theme |
|---|---|---|---|---|
| 0.30 | 2.40 | A-1 establish | santoor clock, 5 notes, very soft; out before "Next." | MIRA |
| 2.60 | 7.24 | — | **no music** (air for "Next / no one else here / procedure") | |
| 7.30 | 9.45 | A-2 walk | clarinet head + guitar swing; pizz on Jax's first 5 steps | JAX |
| 9.95 | 15.45 | A-3 reading | only a soft pizz on his steps (her line leads) | JAX (pulse) |
| 15.86 | 17.0 | A-4 smile on | one vibes note | |
| 18.42 / 20.05 / 21.55 | — | A-5 gap stabs | bansuri 2-note (her), bassoon plop (his blink), santoor tick-tick (unmoved) | MIRA / JAX |
| 24.70 | 32.60 | A-6 the pitch | guitar + pizz swing low under him; clarinet head (low); vibes sparkle on "Section twelve" (29.4) | JAX |
| 33.00 | 35.60 | **dead stop** | music hard out (air before and after "nine sections") | |
| 37.35 | 38.45 | A-7 almost-smile | ONE held bansuri A, soft (a slide up into it); cut as she pulls the keyboard | MIRA |
| 38.45 | 46.85 | A-8 the blank record | low viola D/Eb hold, celesta falling into nothing (the screen), then a soft D-minor hold under her line | (mystery) |
| 46.90 | 47.97 | A-9 the look | both motifs at once: bansuri MIRA over clarinet JAX, tiny swell | MIRA × JAX |
| 47.97 | 49.95 | **dead stop** | music hard out for the stamp | |
| 49.95 | 51.60 | A-10 exit tag | clarinet falls A–F–D, bassoon low A plop: deflated | JAX |
| 51.70 | 54.40 | A-11 notebook | santoor clock, very soft | MIRA |
| 54.60 | 65.70 | A-12 Noakes | dry: tired bassoon line, tuba floor, woodblock ticking each second; bassoon "sigh" at 61.65 | (Noakes colour) |
| 65.71 | 70.70 | A-13 the board | a mock-hymn F-major chord on horns + trombone, held under his prayer | |
| 71.20 | 72.30 | A-14 Baron button | far-off fife + snare flourish: the first bar of MARCH, distant | MARCH (foreshadow) |
| 73.00 | 74.80 | A-15 closed eyes | low D-minor chord (cellos, bassoon) + one celesta F | |
| 75.00 | 77.50 | CARD | harp descends A–F–D–A–E, one high violin E fades into the rim | |
| 77.40 | 98.90 | B1-1 stillness | open fifth E–B (violas) + low E; four lone harp notes. No melody, no feeling yet | |
| 99.60 | 103.0 | B1-2 "Tell me one" | duduk: the rising cell B–E–B (slide into the top B), E-minor hold | HEART (first cell) |
| 103.0 | 109.45 | B1-3 Ochakov | distant snare taps growing, double-bass swell, timpani, horns rising to the cannon | MARCH (approach) |
| 109.47 | 110.70 | CUT-1 the cannon | tutti low hit, bass drum, crash; string run up | |
| 110.73 | — | CUT-2 jump | lands on a high A with snare + horns | |
| 112.25 | 115.85 | CUT-3 astride | MARCH on piccolo + trumpet, gallop in low strings, snare | MARCH |
| 115.90 | 121.00 | CUT-4 doubts | stall on high A, piccolo sags; hesitant minor pizz, bassoon, viola hold | MARCH (stalled) |
| 121.70 | 123.10 | CUT-5 the other ball | shehnai runs down (the other side), frame drum, panned right | |
| 124.90 | 125.65 | CUT-6 changed | trombone slides down a whole tone; stick clicks; a beat of nothing | |
| 125.70 | 128.00 | CUT-7 recovery | MARCH up a semitone (Eb), tutti, crash + timpani | MARCH |
| 128.00 | 130.40 | CUT-8 out | held Eb (violins + horn) carries back to the rim, fading under "You changed cannonballs" | |
| 130.10 | 131.20 | CUT-9 "rode it home" | tiny distant piccolo quote of MARCH | MARCH |
| 136.20 | 138.90 | B2-1 laugh | warm E-major swell (violas, cellos) + harp arpeggio under Jax's laugh | |
| 138.40 | 141.60 | B2-2 "listened to the end" | solo cello: the rising cell B–E–B, soft | HEART (cell) |
| 141.60 | 144.80 | B2-3 thin | one high violin E, pp, fading | |
| 144.945 | 147.945 | **TRUE SILENCE** | score and effects at digital zero; only the suit breathing, 8 dB lower than the rest of Part B | |
| 147.95 | 156.30 | B2-4 the promise | duduk alone plays the HEART phrase once, plainly (B E B / A G / F# G A / B), over a low E | HEART (the hummable phrase) |
| 156.30 | 162.441 | B2-5 no answer | the duduk lands on B, held by the violins over a C chord (unresolved Cmaj7); fades over the last 1.2 s; no button | |

**Effects.**
- **Part A, customs hall** (all in the Masonic Lodge room):
  - hall room tone: two real CC0 beds, our synth hall tone and a fluorescent hum, high-passed so phones get some of it;
  - distant cargo-scale beeps round the Baron (0.35, 1.25, 2.05, 70.2);
  - Mira's small paper stamps (2.75, 5.95) and paper;
  - 17 steps on the walk (7.45–15.45: left to right on the pass, centre on the tracking shot);
  - cloth on 15 gestures; elbow knock 15.88;
  - screen flicker and scroll ticks 38.45;
  - **THE STAMP 48.048**: the layered stamp (real rubber stamp + our heavy thunk + real desk bang + sub + ink tack) plus a camera-bump sub thump;
  - 4 exit steps receding left (50.1–51.45);
  - drawer 51.45; pen 51.7–54.4 and again 73.1–75;
  - Noakes' cloth (54.5) and sigh (61.6);
  - board: three flaps (65.75–66.22), then a slow tick (67–70).
- **Part B, vacuum: nothing from outside.**
  - Suit breathing bed (Jax, with the Baron's lower) from 77.0, about −44 LUFS before the master.
  - Private-channel click 80.198.
  - A squelch tail after every radio line.
  - Cloth felt inside the suit (low-passed) at 85.5, 100.2, 101.6, 133.6, 136.55 and 153.5.
  - The radio stems were not treated again.

## Mix
- **Dialogue chain.**
  - Part A: the v3 chain on the untreated stems (per-speaker EQ, 3:1 compression, de-esser), each line at −23 LUFS before the master, then the customs-hall room at −15 dB.
  - The Baron's far-off line gets a +6 dB room send for distance.
  - Part B radio stems and the laugh: level only. The laugh sits 3 dB under the other lines.
- **Placement.** Close-ups are centred. Two-shots: Jax −0.3, Mira +0.3. Noakes shots: Noakes −0.15, Mira +0.2. Wide: Mira +0.25, Jax −0.2. Rim two-shot: Baron −0.12, Jax +0.12.
- **Ducking.** The music is ducked by the speech: −9 dB in 0.9–4.5 kHz and −4 dB elsewhere. In the cutaway (109.47–128.25) it ducks deeper (−13 / −7) so the march speaks in the gaps.
- **Clarity fix.** Every line under 10.5 dB speech-band clarity had the music pulled down around it, re-measured until it passed:

  | Line | Music pulled down |
  |---|---|
  | 3-11 | 5.4 dB |
  | 3-25 | 6.2 dB |
  | 21-12 | 3.6 dB |
  | Laugh | 6.8 dB |
  | 21-20 | 1.8 dB |
  | 21-28 | 1.2 dB |

**Measured on the WAV master**

| Measure | Value |
|---|---|
| Integrated loudness | −16.0 LUFS (ffmpeg EBU R128 and pyloudnorm agree) |
| True peak | −2.2 dBTP |
| Part A / Part B | −16.3 / −15.9 LUFS |
| Stems | music −21.6, effects −32.9, dialogue −16.2 LUFS |
| Silence window 144.945–147.945 | score and effects digital zero; total −47.8 dBFS RMS (breathing only) |
| Last 50 ms | peak −56.9 dBFS |

Review MP3: it decodes about 0.5 dB quieter (−16.5 LUFS); the master is the reference.

**Speech-band clarity per line** (dialogue vs everything else, 1–4 kHz, dB; minimum 10.5). This is
the band a phone speaker reproduces; no separate phone-speaker simulation was run.

| Line | Start | Who | Text | dB | Music pulled down (dB) |
|---|---|---|---|---|---|
| 3-01 | 2.60 | mira | Next. | 16.1 | |
| 3-02 | 4.13 | jax | There's no one else here. | 25.2 | |
| 3-03 | 5.52 | mira | It's procedure. Next. | 26.3 | |
| 3-04 | 9.54 | mira | Parcel, one. Sealed… | 23.6 | |
| 3-05 | 16.76 | jax | Here's my situation. My aunt— | 15.6 | |
| 3-06 | 18.55 | mira | You don't have an aunt. | 14.1 | |
| 3-07 | 20.64 | jax | You don't know that. | 20.9 | |
| 3-08 | 22.11 | mira | Your form says next of kin: none. | 17.5 | |
| 3-09 | 24.64 | jax | She's very distant. Look… | 13.2 | |
| 3-11 | 29.38 | jax | Then you'll appreciate the Lunar Courier Exemption… | 10.9 | 5.4 |
| 3-12 | 33.15 | mira | There are nine sections. | 27.0 | |
| 3-13 | 35.67 | jax | Which is why twelve is so exclusive. | 23.8 | |
| 3-18 | 40.05 | mira | Your record starts seven years ago. | 16.1 | |
| 3-19 | 42.57 | jax | Late bloomer. | 13.3 | |
| 3-20 | 44.21 | mira | Your record isn't late, Captain. It's blank. | 14.8 | |
| 3-24 | 48.70 | mira | Holding bay. | 24.9 | |
| 4-04 | 55.52 | noakes | You were struck off… | 13.3 | |
| 4-05 | 60.44 | mira | It is wrong. | 19.2 | |
| 4-06 | 62.45 | noakes | It's official… | 14.7 | |
| 4-07 | 66.81 | noakes | One more complaint… | 12.4 | |
| 3-25 | 71.07 | baron | I used to be taller! | 10.5 | 6.2 |
| 21-01 | 80.90 | baron | There it is… | 13.0 | |
| 21-02 | 85.50 | baron | Sign, Captain. | 14.7 | |
| 21-03 | 86.92 | jax | You'd be a show… | 14.5 | |
| 21-04 | 88.80 | baron | A tidy Baron… | 13.2 | |
| 21-05 | 92.87 | baron | I have seen the thin ones… | 12.3 | |
| 21-06 | 98.88 | jax | Tell me one. | 13.2 | |
| 21-10 | 100.22 | baron | Ochakov… | 12.2 | |
| 21-11 | 107.16 | baron | So I stood by our biggest cannon… | 12.7 | |
| 21-12 | 111.51 | jax | On it. | 10.7 | 3.6 |
| 21-13 | 112.25 | baron | Astride. Like a horse, but rounder. | 11.2 | |
| 21-14 | 114.70 | baron | Halfway across, I had doubts… | 13.1 | |
| 21-15 | 121.08 | baron | So when a ball came past… | 16.9 | |
| 21-16 | 128.31 | jax | You changed cannonballs. | 11.9 | |
| 21-17 | 129.63 | baron | In mid-air. And rode it home… | 16.4 | |
| 21-18 | 133.59 | baron | I rode it there… | 17.9 | |
| 21-LAUGH | 136.55 | jax | (laughs) | 10.8 | 6.8 |
| 21-19 | 138.19 | baron | There. You listened to the end… | 15.5 | |
| 21-20 | 141.72 | jax | Did it happen? | 10.7 | 1.8 |
| 21-21 | 142.72 | baron | It's happening now. You are the audience. | 18.8 | |
| 21-22 | 147.94 | baron | If ever you need me… | 16.6 | |
| 21-26 | 153.88 | baron | You lie well, Captain. | 16.1 | |
| 21-27 | 155.51 | jax | Thanks. | 11.3 | |
| 21-28 | 156.32 | baron | You lie like a man… | 10.8 | 1.2 |

**Music level by passage** (music stem, dBFS RMS, after the master gain):

| Passage | dBFS RMS |
|---|---|
| establish | −25 |
| gap 2.7–7.2 | −64 (none) |
| walk | −17 |
| reading | −29 |
| pitch | −27 |
| dead stop 33.2–35.6 | below −57 |
| almost-smile | about −26 (5 dB pulled down after the first measurement) |
| look | −21 |
| Noakes | −26 |
| hymn | −22 |
| card | −19 |
| rim stillness | −28 |
| Ochakov | −25 |
| cutaway | −24 (the swap gap −18) |
| laugh | −29 |
| "Did it happen" | −36 |
| silence | digital zero |
| promise | −26 |
| final hold | −22 |

## Not checked / listen for
- **Nothing here has been heard.**
- **Synthesised instruments** (bansuri, santoor, duduk, shehnai): if they sound fake, swap to VPO
  flute/oboe and VCSL vibes. They are one setting per track in `sample5_score.py`.
- **The laugh** had to be pulled down 6.8 dB around itself to pass the clarity rule, so the supporting
  swell is quieter than planned. Check that the laugh is not exposed.
- **The cutaway:** does the march land the jump (110.73), the stall (115.9) and the swap
  (125.2 → 125.7) against the picture? Is the Baron clear over it?
- **The silence:** do the 3 s read as intended with only faint breathing?
- **The ending:** do the promise phrase and the unresolved B over C land, or does the ending feel cut off?
- **The Baron's far-off "I used to be taller!"** is the faintest-measured line (10.5 dB).
