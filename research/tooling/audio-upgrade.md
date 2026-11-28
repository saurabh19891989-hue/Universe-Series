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

---

# Stage 1 (28 Nov, after the owner heard reel 1)

Reel 2 is in `samples/audio/upgrade2-28nov/` (ORDER.txt). Nobody has listened to it. Sources now
follow the showrunner's ruling: anything free whose terms do not forbid published music, plus our own
synthesis. We do not rip from recordings or use non-commercial packs.

## World instruments: what we have
Every instrument below is **synthesised in our own code** (`production/tools/music/worldsynth.py`).
There are no outside samples, so there is no licence question. I did not search for sample packs
this stage: synthesis got every requested instrument made inside the time box.

**Plucked and struck strings** (a string model with per-note pitch slides):
- **Sitar:** bright pluck, a buzzing curved-bridge (jawari) model, and sympathetic strings tuned to the raga.
- **Veena:** deeper and softer buzz, long sustain, made for gamaka.
- **Tanpura:** heaviest buzz with a long ring. `tanpura()` plays the Pa–Sa–Sa–Sa(low) cycle.
- **Santoor:** hammered, three slightly detuned courses, bright and long.
- **Koto:** plectrum, bends.
- **Kora:** soft thumb pluck.
- **Oud:** fretless and warm, damped at note end.

**Wind and bowed** (harmonic additive engine with breath or bow noise, vibrato and body resonances,
following any pitch curve):
- **Bansuri:** breath noise tied to the note, plus an attack chiff.
- **Shehnai:** also stands for nadaswaram; bright and nasal.
- **Duduk:** dark reed.
- **Erhu:** nasal, wide vibrato.
- **Sarangi:** vocal resonances plus sympathetic resonance.

**Drums** (modal synthesis, one stroke per key):
- **Tabla:** bols na, tin/tun, ta, te/ti, re, ke/ki, ge, ghe with pitch rise, dha, dhin. The right
  drum has harmonic modes (as its loaded head gives); the left drum is low with a palm glide.
- **Mridangam** and **dholak:** the same engine with a larger bass glide.
- **Djembe:** bass, tone and slap.
- **Talking drum:** pitch follows the bend curve.

**Idiomatic sequencing:**
- `theka()` plays real thekas (teental 16, keherwa 8, dadra 6, rupak 7). The sam is accented,
  strokes vary in level, ghost "ke" strokes are added, and a tirakita fill leads into sam.
- `meend()` slides into a note; `gamaka()` shakes a held note.

**Checked by measurement only:**
- **Pitch:** autocorrelation gives 261.4–261.6 Hz for C4 and 329.2–329.8 Hz for E4 on every melodic
  model. Sarangi's reading is pulled off by its sympathetic resonance.
- **Brightness over time:** plucked spectral centroid falls from 2.3–4.3 kHz in the attack to
  1.1–2.1 kHz later, i.e. the tone darkens as the note rings.
- **Cost:** under 0.3 s of CPU per instrument for a 5 s phrase. No NaNs.
- **Transient spikes:** santoor and drum spikes are soft-limited to about 20 dB above the note body.

**Not checked:** whether any of them sounds like the real instrument. This is the biggest risk, and
the owner should judge it.

- **Bug found and fixed:** `sfzr.py` applied the first pitch-bend value to every note before it.
  Any v2/v3 sampled part whose first bend came after its first notes played those notes off-pitch.
  Reel 1's Mira motif had its first two notes a whole tone flat (re-rendered in reel 2, file 01).
  The v2 A4/A5 flute/shakuhachi parts may have the same fault if they were rendered with VPO.
  FluidSynth (v1) was never affected. Bends now follow MIDI behaviour: zero before the first event,
  then each value holds until the next.

## Composition
All in `production/tools/music/s2_pieces.py`.
- **Mira on Indian instruments (19 s).**
- **Indian instruments piece (34 s):**
  - D, Kalyani/Yaman colour;
  - alap on sitar over tanpura;
  - a gat on bansuri over teental;
  - sitar–bansuri question and answer;
  - a santoor run;
  - a three-fold tihai landing on sam.
- **Baron's heart theme (63 s):**
  - E minor 3/4, with a hummable 8-bar tune: a rising fifth, then a falling line;
  - duduk first, then violins with a solo-cello counter-line and celesta;
  - the coda turns to E major.
  - Measured under quiet dialogue: with the music 8 LU below Baron lines at −23 LUFS, the voice is
    11.7–15.4 dB clear of the music in 1–4 kHz. The old M08 rim cue under the same lines gives 1.3–2.9 dB.
- **Cannonball cutaway (20 s):**
  - an 18th-century march (fife, trumpets, horns, snare, timpani);
  - at 8.6 s a stall, a trombone slide down, a tripped snare and a beat of nothing;
  - at 10.2 s recovery a semitone up;
  - the hit at 18.8 s. Move the stall to the picture's "changed cannonballs" frame.
- **Main theme as a piece (76 s):**
  - intro, then A;
  - a new B tune with a cello counter-melody, in contrary motion;
  - the lift;
  - A′ with the B counter-melody on flute over the hook, so both tunes sound together;
  - tag.
  - Tabla keherwa and santoor give it an Indian colour inside the orchestra.
- **Customs sparring (28 s):**
  - Jax's motif and Mira's motif (moved into Jax's key) trade phrases, then overlap, then run in
    counterpoint;
  - one-beat jabs back and forth;
  - a truce on one shared note, then the stamp.

Render time (shared machine): 5–11 s for the 18–34 s world pieces; about 0.75–0.9 CPU-s per second
for the orchestral pieces (heart theme 44 s for 63 s; main theme 57 s for 76 s).

## Effects with what we have (`production/tools/sfx/fx3.py`)
- **Variation:** `vary()` shifts pitch (±60 cents) and time, gain and a slight EQ tilt, so repeats are
  never identical.
- **Transient shaper.**
- **Sub thump:** pitched, with a 2nd harmonic so phones still hint at it.
- **Distance placement:** level, top-end loss, narrower image.
- **Stamp:**
  - layers: real rubber stamp, our heavy thunk, real desk bang (low-passed), sub, and a little ink "tack";
  - shaped and varied per use.
  - Two variations measured: 39–53 % of the energy below 60 Hz, 39–51 % in 60–250 Hz.
- **Landing, felt only (vacuum rule):**
  - layers: our felt thud, sub boom, hull groan (pitch-varied), low debris rattle;
  - double low-pass at 1.8 kHz. Measured: 0.0 % of the energy above 2 kHz and 85 % below 60 Hz,
    so it will be close to inaudible on a phone (by design; owner to say).
- **Suit radio:**
  - steep 480 Hz–2.9 kHz band-limit, a 1.8 kHz radio peak, light grit;
  - helmet: two close reflections at 2.5 ms and 4 ms with a 1.1 kHz resonance;
  - 4:1 compression, click on and off, and a short squelch tail;
  - breathing and suit-fan bed with faint open-channel hiss, and nothing from outside.
  - Measured: 70 % of the radio line's energy in 0.5–3 kHz.
- **Low-gravity steps in a suit:**
  - real steps slowed and pitched about 5 semitones down, muffled below 1.1 kHz, with a 140 Hz boot body;
  - a suit-cloth swish 0.32 s before each contact (the bound), at a 0.9 s cadence.
- **Demo:** `fx3.py OUT.wav LINE.wav` (reel 2 file 08).

## mix3 chain as the default for new scenes
- **`edit/audio.py`:** a shot list with `"mix_version": 3` gets the dialogue chain per speaker
  (high-pass, EQ, 3:1 compressor, de-esser, make-up to the line's own loudness) and band ducking by
  default. Without the key, the old path is unchanged; both were tested.
- **`SCHEMA.md`:** says new shot lists set `"mix_version": 3`.
- **Toon scenes:** keep using `sfx/mix3.py` for placement, room and foley plans.
- **Builder:** the shot-list builder agents should write `"mix_version": 3` from now on.
