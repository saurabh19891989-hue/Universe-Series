# Audio upgrade test (28 Nov 2026)

Music and sound builder (Opus). Agents cannot hear: everything below is measurement or reading of
the score. Nobody has listened to any of the new files. Listening reel:
`samples/audio/upgrade-28nov/` (ORDER.txt says what plays when).

## 1. Diagnosis of what we had (measured)

Tool: `production/tools/music/audiometer.py` (BS.1770 loudness, true peak, loudness range, band
energy shares, stereo correlation, tail). Scene analysis rebuilt the toon-test buses from its shot list.

**The customs-desk toon test mix (`samples/e01/E01-toon-test-720p.mp4`, 56 s)**

| Measure | Value | What a listener would likely notice (hypothesis) |
|---|---|---|
| Score present | 4.4 s of 56 s (7.9 %): 8.2 s of M02 over the landing, 3 s button at 53 s | The 45 s dialogue scene has **no music at all**. It may feel like a radio play in an empty room. |
| Effects events | 6 in 56 s (engine, spindown, room tone, one pre-made footstep pattern, one paper rustle, the stamp) | No cloth or hand foley for the gestures, so the puppets may feel weightless and "pasted on". |
| Room tone | 41 % of its energy below 60 Hz | Phone speakers play almost nothing below ~150 Hz, so on a phone the room tone vanishes and the gaps between lines go dead. |
| Stereo | correlation 0.963, side-to-mid −17 dB | Almost mono. Fine on a phone, flat on headphones. |
| Spectrum | centroid 596 Hz; 83 % of the energy is below 1 kHz; 8.4 % in 1–4 kHz | Heavy in the low-mids and dull overall. |
| Dialogue | dry stems with no EQ, compression or room. Jax's stem has 37 % of its energy in 60–250 Hz. Line loudness is already even (spread 1.0 LU). | The voices do not sit in the customs hall; Jax may sound boomy on headphones. |
| Intelligibility | 1–4 kHz dialogue-to-bed ratio: median 22.7 dB, minimum 12.3 dB | Clear, but only because nothing plays under the voices. |
| Master | −16.1 LUFS, −1.4 dBTP, LRA 4.5 LU | On target. The −1.4 dBTP is just over our −1.5 rule. |

**The engine (`production/tools/edit/audio.py`, and `toon/mix_audio.py` used for test 3)**
- Ducking is broadband only: the whole score drops 10–12 dB under speech, taking its body and top with it.
- No dialogue chain: no high-pass, EQ, de-esser, compressor or placement. Optional per-line convolution reverb exists in the conform path.
- Loudness normalisation and true-peak limiting are present and work. `mix_audio.py` uses a tanh soft clip, not a limiter.

**The Episode 1 score (23 cues, `e01_score.py`, rendered by `v2mix.py`)**
- Instruments: 28 presets. Pizzicato is in 20 of 23 cues, celesta in 11, harpsichord in 8. There is no piano and no hand percussion, and there are no world instruments in E01 (sitar appears only in A1). The guitar is a General MIDI soundfont (FluidR3), and the drums are partly General MIDI.
- Room: one synthetic noise "hall" for every cue (fully decorrelated noise, RT60 1.2–2.8 s). M02 has stereo correlation 0.04, which is very wide and diffuse. Hypothesis: it sounds like "reverb" rather than a room, and it smears.
- Bus: sox compand, about 2:1 above −22 dBFS, on every cue. Loudness range is 2–7 LU on most cues.
- Top end: the cues have 0.4–1.4 % of their energy above 4 kHz. The VPO samples themselves have about 0.1 %, so this is mostly the library's dark recordings, not our processing. Hypothesis: the score sounds dull or "behind a curtain", most of all on phones.
- Melody: the motifs are present but rarely restated as a tune. Only 64 of 666 distinct four-interval figures recur across cues. Melodic note density is 8–40 notes per minute in most dramatic cues. Hypothesis: there is no single tune a viewer leaves humming.

## 2. What was tested

### a. Instruments and room (tested, used)
| Library | Licence (read myself) | Result |
|---|---|---|
| **VCSL**, Versilian Community Sample Library (sfz branch) | CC0, from the README: "you can do whatever you want with these sounds (even make commercial software), no royalties, no credit" | Fetched about 1.8 GB by sparse git checkout. All 30 SFZs I picked parse in our `sfzr.py` with 0 missing samples. It gives us a Kawai grand, marimba, vibes, xylophone, glockenspiel, kalimba, concert harp, darbuka, frame drum, cajon, conga, bongos, a drum kit, cymbals and comedy percussion (slapstick, flexatone, ratchet, vibraslap, guiro, toy whistle). Balafon, dan tranh and folk harp are fetched but not used yet. |
| **FreePats Spanish classical guitar** (SFZ) | CC0 (readme.txt and the web page) | Replaces the FluidR3 General MIDI guitar. It has one velocity layer and no round robins. |
| **Voxengo IM Reverbs** impulse responses | "royalty-free for any purpose, including commercial usage"; the files may not be sold or redistributed | Musikvereinsaal (T30 ≈ 1.5 s) and Scala Milan Opera Hall (≈ 1.0 s) for the score; Masonic Lodge (0.5 s) for the customs-hall dialogue. The IRs are fairly correlated left/right (0.59–0.68), so the room return is widened 1.5× in mid/side. |
| Not found | — | No free, commercially clean tabla, sitar, veena, mridangam, bansuri, erhu, duduk, kora or oud sample set that is licence-checked. Workarounds: flute with meend (pitch slides) for Mira, darbuka and frame drum for the hand-drum role, harp drone in place of a tanpura. |
| Not reachable | — | OpenAIR IR library (its TLS certificate had expired on 28 Nov; not bypassed). |

New code: `v3mix.py` (palette, orchestral seating, measured room, gentle bus) and `dsp.py` (RBJ EQ,
compressor, de-esser, band ducking, convolution, placement, true-peak limiter, loudness).
`v2mix.py` and `e01_render.py` are untouched, so every existing cue renders exactly as before.

**A/B, E01 C1 caper, first 40 s, same notes** (reel files 01 and 02, both at −17.5 LUFS):

| | v2 (current) | v3 |
|---|---|---|
| Loudness range | 4.1 LU | 5.8 LU (less squashed bus) |
| Crest factor | 15.9 dB | 17.5 dB |
| Stereo correlation | 0.67 | 0.78 (after room widening; 0.84 before it) |
| Centroid | 662 Hz | 734 Hz |
| Render time | — | 32–35 s for 40 s of audio (shared machine) |

Note: v3 is still less wide than v2. The v2 hall is pure decorrelated noise; v3 uses a measured room,
which is narrower, and the samples themselves are close to mono. The 1.5× room widening helped
(correlation 0.84 → 0.78). The theme and sting measure wide anyway (correlation 0.28 and 0.37).

### b. Composition (written in code, rendered)
`production/tools/music/s1_themes.py` holds the season material: a HOOK (D A D E F | E D C D, grown from
the approved A1 head), a LIFT (B section), the 3+3+2 ship ostinato, and the JAX, MIRA and PIP cells.
- **Main theme** (58 s, 104 BPM): ship ostinato intro → A: the hook on flute + solo violin, with harp
  arpeggios, hand drum and a moving bass → B: the lift on violins with a horn counter-line → A′: tutti
  with trumpets, trombones, timpani and piano → tag: the head alone on piano, then the final hit.
  The flute has slides into the notes (meend) for warmth.
- **Title sting** (15 s): the hook on horns and trumpets over the ostinato and a kit groove, a rising string run, a hit, and a piano/flute "D-A-D" wink.
- **End card** (17 s): the hook slow on piano, with flute, strings and harp.
- **Motifs** (16–18 s each): JAX (Dorian swing, clarinet then cornet, nylon guitar, darbuka; the tune
  never finishes and ends on a soft slapstick), MIRA (Sa-Re-Ga-Pa-Dha on F, flute with meend, kalimba
  "clock", harp drone), PIP (a C-major postal march: piccolo + xylophone, tuba/bassoon oom-pah,
  woodblock tick-tock, slapstick stamp, toy-whistle query).
- **Customs-desk underscore** (56 s, 120 BPM so one beat = 0.5 s) uses comedy timing on purpose:
  - Silence under "Next / no one else here / procedure".
  - A light pizzicato mickey-mouse on Jax's seven steps.
  - Mira's clock on celesta under the parcel read.
  - A bassoon "plop" button after "next of kin: none".
  - Guitar and clarinet swing under the charm line, cut dead on "I'm a cartographer".
  - The cornet head on "Section twelve", stopped dead for "There are nine sections".
  - A cornet ta-da deflated by bassoon on Mira's look.
  - The Mira motif warm on solo violin for "anything true", then a timpani heartbeat for "four hours".
  - A tutti hit on the stamp, then the head as the button.

### c. Music-generation models (not re-tested this session)
- **ACE-Step 1.5**: MIT licence on the code and weights. It was already tested on this machine:
  about 3 min 15 s of CPU per 30 s of audio (about 6.5 min per minute) after a memory patch. The
  owner rejected those AI cues, and they were deleted.
- **MusicGen**: CC-BY-NC weights, excluded.
- **Stable Audio Open**: community licence capped at $1 M revenue, with registration; not used.

Honest view: no generator gives us recurring, editable themes that we own as notes, so it is not
worth the CPU under contention. No licence-clean, CPU-viable route to a theme song with vocals was
found. The stretch goal is not attempted.

### d. Sound design
- `production/tools/sfx/fetch_freesound_cc0.py` reads each Freesound page and refuses the file unless
  the page's licence link is CC0 1.0. It downloads the public HQ preview (lossy, about 128–192 kbps;
  the original WAV needs a login) and logs URL, author, title and licence.
- 15 files fetched, 10 used: room tones (large interior with AC, empty hallway), fluorescent hum,
  shoe footsteps (cut into single steps at their onsets), cloth movement, paper rustle and shuffle,
  a rubber stamp, a desk bang, and a swish.
- Layered with our synthesised hall tone, paper slip and heavy stamp.
- Comedy sounds are ours: real VCSL percussion played in the score (slapstick, woodblock, flexatone
  and so on). There are no library "cartoon" effects.

### e. Mix and master: `production/tools/sfx/mix3.py` (new scene mixer)
- **Dialogue chain, per speaker:** high-pass (Jax 95 Hz, Mira 110 Hz), low-mid cut, presence lift,
  air shelf, 3:1 compressor, de-esser, then make-up to −23 LUFS per line.
- **Placement and room:** each voice is panned by the puppet's on-screen x (it follows Jax's walk,
  scale 0.3). Customs-hall room: Masonic Lodge IR at −15 dB, high-passed, from the cut-in.
- **Effects:** steps and cloth follow the character and are sent to the same room.
- **Ducking:** the music is ducked by speech presence: −9 dB in 0.9–4.5 kHz and −4 dB outside that band.
- **Master:** −16 LUFS with a true-peak limiter at −1.7 dBTP.
- **Engine:** `edit/audio.py` gets an opt-in `"duck": {"mode": "band"}` (tested both ways; without
  `mode` nothing changes).

**Customs scene, before vs after (reel 08 and 09)**

| | Before | After |
|---|---|---|
| Score present | 7.9 % | 77.8 % |
| 1–4 kHz dialogue-to-bed, median / minimum | 22.7 / 12.3 dB | 23.8 / 11.8 dB |
| Stereo correlation | 0.963 | 0.819 |
| Centroid | 596 Hz | 709 Hz |
| Energy below 60 Hz | 6.7 % | 3.2 % |
| 1–4 kHz energy share | 8.4 % | 12.2 % |
| Integrated loudness / true peak | −16.1 LUFS / −1.4 dBTP | −16.1 LUFS / −1.7 dBTP |
| Mix time | — | about 9 s |

Short-term loudness (3 s windows) in the after mix: the landing runs −12 to −14 against about −17 for
the dialogue, so the landing is 3–5 dB louder than the talk. Check that by ear. The 1–4 kHz ratio stays
the same as before even though music now plays under 78 % of the scene. The lowest lines are 3-11 and
3-14/15 (music under "Section twelve" and "anything true"), at about 12–14 dB.

## 3. What the owner should listen for
- **01 vs 02:** do the guitar and percussion sound like real players, or more synthetic? Is the room
  better or worse? Is v3 too narrow?
- **03:** is the hook hummable after one play? Is the B-section lift warm, and is the tutti big enough?
- **04:** does the sting read as a title card in 15 s?
- **05–07:** do the motifs fit the characters?
- **08 vs 09:**
  - Do the voices now sit in a hall, or sound processed?
  - Is the music too busy under the jokes?
  - Do the silences land?
  - Are the footsteps in time with the walk?
  - Is the stamp satisfying?
- **Phone check:** listen on a phone speaker as well as on headphones.

## 4. Recommendation: the audio pipeline for an episode
**Automated (scripts, no judgement):**
- dialogue chain and placement from the shot list;
- per-room IR from a location table;
- room tone and hum beds per location;
- foley placement from rig keys (walk cycles → steps; arm keys → cloth);
- band ducking, loudness and true peak;
- measurements and the intelligibility table per line;
- review MP3s.

**The composer-agent writes per episode:**
- about 12–20 cues as functions in `eNN_score.py` that reuse the season cells (HOOK, LIFT, SHIP, JAX,
  MIRA, PIP, plus guest motifs), timed against the dialogue conform: stops, buttons, silence before
  punchlines;
- a mix plan per scene (which real effects, the levels relative to dialogue).

A separate Opus critic checks pacing and the measurement table.

**Compute (measured here, shared 4-core machine):**
- v3 score render: about 1.1 CPU-s per second of music (58 s theme in 56–67 s; 40 s caper in 32–35 s;
  15 s sting in 16–18 s).
- Scene mix: about 0.16 s per second.
- A 35-minute episode with about 25 minutes of score is about 30 min of score render plus about
  6 min of mixing, as scripts on one core.

**Library plan for a 10-episode season:**
- one main theme (58 s), title sting (15 s) and end card (17 s);
- 6–8 character motifs (Jax, Mira, PIP, Temi, the ship, the Baron, recurring guests), each written in
  4 moods (comic, warm, tense, triumphant) as 15–30 s stems = about 30 reusable cues;
- about 10 utility beds (wonder, caper, tension, chase, sad, exterior pad);
- about 40 buttons and stings (2–4 s);
- per episode, 8–12 bespoke cues for the episode's guest story and set pieces.

About 80 reusable assets cover roughly half of each episode's underscore.

**Next steps, in order of likely value:**
1. Owner listens to the reel and picks the direction.
2. Port `mix3.py`'s chain into the episode engine and make it the default for new shot lists.
3. Fetch the original WAVs of the chosen Freesound effects (needs a free account; owner decision) to replace the lossy previews.
4. Build a small per-location room-tone set.
5. Search again for licence-clean Indian, Chinese and West African instrument samples (or record or
   commission them once, as an owned asset).
6. Widen the v3 stage after listening.

## Files
- **Code:**
  - `production/tools/music/`: `v3mix.py`, `dsp.py`, `s1_themes.py`, `render_v3.py`, `audiometer.py`, `ab_caper_v3.py`, `fetch_libs_v3.sh`
  - `production/tools/sfx/`: `mix3.py`, `fetch_freesound_cc0.py`, `fetch_fx_e01.sh`, `plans/e01_customs_plan.py`
  - `production/tools/edit/audio.py`: opt-in band duck
- **Sources and licences:** `assets/audio-sources.json`.
- **Masters (WAV, 48 kHz, 24-bit):** scratchpad `audio2/out/`.
