# STATUS — Secret Universe

Last updated: 2026-11-27 (session 1)

## Done
- v0.1 research saved in `research/v0.1/`.
- Owner decisions (27 Nov): free tools first, then cost of paid; showrunner picks guests;
  storage on Google Drive (alumni.iitd account); music is global, references are guidelines;
  story may be improvised freely; owner creates the YouTube channel.
- Drive folder `Secret-Universe-Series` created with 3 subfolders (ids in CLAUDE.md).
- Drafted: `canon/SERIES-BIBLE.md` v1.0, `canon/season-01.md` (10 episodes),
  `canon/WRITERS-RULEBOOK.md`, `CLAUDE.md`, `production/tests/TEST-BRIEF.md`.

## Owner decisions on samples
- Music (27 Nov): composed-by-us route approved (A1, A4, A5 liked). AI-generated music rejected; dropped.
- Audio (27 Nov): ElevenLabs NOT needed. All audio is made in-house: composed score, our own
  sound effects, and voices from the free engines under test (Gemini voices on the Google credit
  remain an option if the owner wants them after hearing the free samples).
- Owner has a Google Cloud
  account with $300 credit on the saurabh19891989 gmail account for Gemini voices and Nano Banana images.
- Laptop link approved; laptop folder `Secret-India-Research` listed but not yet offered to cloud sessions.

- Look (27 Nov): owner rejected BOTH still-B (vector) and still-C (ink art). Direction is
  photoreal people, ships and sets that match the real footage. Cast must look global, not
  mostly Indian. Free image routes judged too slow and inconsistent to rely on.
- Stories (27 Nov): mix several real literary and mythic sources from different cultures per
  episode, read from the original texts; inspiration, never scene-by-scene copying.
- Gemini: the AI Studio key's project is on the free tier (image quota zero); owner is sorting
  out how to use the $300 Google Cloud credit. Voices work on the free tier.

- Audio (27 Nov, later): owner listened; voices "pretty good for now" and said to continue with
  the A1–A5 composed music direction. Showrunner's reading: free voices (Kokoro / Pocket TTS)
  are acceptable as the working voices; Gemini voices stay as the upgrade under test.
- Episode 1: outline approved by showrunner with changes; full script being written
  (`episodes/E01/`).

- TOOLS RULE (27 Nov, final for now): free tools or in-house work ONLY for ongoing production.
  No paid subscriptions or per-episode API spend. The $300 Google credit is temporary and must
  not become a dependency; at most a one-time booster (e.g. building a reusable image library)
  if a test shows it can be spent at all. Gemini voices and Nano Banana are therefore not the
  production route. Voices: Kokoro (local, Apache-2.0). Music and sound: composed in-house.
  Pictures: open models we run ourselves or free community services.

- TOOLS DECISION REOPENED (27 Nov, latest): owner will decide between free-only, one-time use of
  the $300 credit, or ongoing spend AFTER seeing the Vertex photoreal test
  (`samples/look-vertex/`). Vertex AI works on project project-6153920b-b099-4ae9-b90 with a
  1-hour access token from the owner's laptop (network secret on aiplatform.googleapis.com;
  send header x-goog-user-project). Whether it bills the credit is unconfirmed.
- Episode 1: script-v3 (critic fixes applied) awaiting showrunner read, then table-read.

- Vertex photoreal test (27 Nov): 7 images made (test + 6 crew portraits), all photoreal;
  Jax held the same face when the first image was passed as reference. Then Google refused
  with HTTP 403 "Access requires an eligible paid billing account in a supported region" —
  the trial-credit account is not enough. Not tested: consistency across many shots,
  mouth/blink edits, sets, ship, two-shots. Library estimate: ~430 images, ~$22 one-time.
  Owner to decide: free-only / fix billing and use credit or pay / ongoing spend.
- Episode 1: showrunner read script-v3 in full and approved it for the table-read.
  Table-read audio (Kokoro) being built in `samples/tableread/E01/`.

- Google credit, settled (27 Nov, from the owner's billing console): the Welcome credit started
  on 27 Nov 2026, so Vertex AI is excluded from it (rule for trials started on or after 16 Nov
  2026); AI Studio is excluded too. The credit cannot pay for Gemini images or voices by any
  route. The 7 test images (~$0.35 estimate) may post as a real charge; nothing shows yet.
  No further Vertex or paid Gemini calls without the owner's say-so. The credit may still be
  usable for ordinary Google Cloud machines (untested idea: rent a large CPU machine there to
  run open image models faster).
- Owner wants to see the free photoreal round (`samples/look-real/`) before deciding on tools.

- IMAGE ROUTE UNDER TEST (27 Nov, latest): OpenAI Codex CLI 0.172.0 installed on the cloud
  machine and logged in with the owner's ChatGPT Pro subscription by device code (login lives
  only on this machine; redo with `codex login --device-auth` in a new session). Built-in image
  generation (`codex exec`, reference images via `-i`) made a photoreal Jax in 56 s with no API
  charge; it draws on the plan's Codex allowance. Character test running, capped at 40 images:
  `samples/look-codex/`. OpenAI terms on scripted use and commercial use NOT yet read.
- Free alternatives researched: Cloudflare Workers AI (FLUX.2 klein 4B, Apache-2.0, reference
  images, ~70–95 free images/day), Kaggle, Modal. See `research/tooling/free-photoreal-routes.md`.

- CODEX IMAGE ROUTE CONFIRMED (27 Nov): owner chose it. 30-image test: photoreal, and one
  reference keeps a character consistent. Runbook: `production/IMAGE-PIPELINE.md`; looks:
  `canon/CHARACTER-LOCKS.md` (8 masters at TEST status, awaiting the owner's casting approval).
  Weekly Codex allowance was 88% used before the test and 90% after; it resets 2 Dec 17:30 UTC
  (owner says they can reset it). Login automation: one-tap device login per session for now.
- Episode 1 table-read delivered to the owner (31:36, `samples/tableread/E01/`); awaiting feedback.

- CAST APPROVED (27 Nov): owner approved Jax, Baron, Chichikov, Seo, Oyuna and PIP — masters
  LOCKED in `assets/`. Mira and Lucía to be redone younger. Owner: prioritise Episode 1 but
  keep building the whole library; owner resets the Codex allowance when a limit is hit.
- Running: library builder (`assets/`, `samples/library/`) and Episode 1 shot list
  (`episodes/E01/shotlist.json`). New session: run `bash production/tools/setup/codex_setup.sh`.

- PARALLEL PRODUCTION (27 Nov, owner asked for speed) — ten jobs running:
  | Job | Output |
  |---|---|
  | Image library (Codex; Ep 1 first, then whole cast) | `assets/`, `samples/library/` |
  | Ep 1 shot list | `episodes/E01/shotlist.json` |
  | Edit engine + cold open render | `production/tools/edit/`, `samples/e01/` |
  | Ep 1 data visuals (screens, map, title) | `production/tools/datavis/`, `samples/e01/datavis/` |
  | Ep 1 NASA plates download + credits | `assets/e01-plates.json` |
  | Ep 1 score cues | `samples/e01/music/` |
  | Ep 1 sound effects | `samples/e01/sfx/` |
  | Ep 1 final dialogue stems (recast for distinct voices) | `episodes/E01/dialogue-conform.json`, `samples/e01/dialogue/` |
  | Ep 2 outline (stops for showrunner ruling) | `episodes/E02/outline.md` |
  | Channel launch kit (names, copy, trailer script) | `channel/CHANNEL-KIT.md` |
  Shared large media: scratchpad `e01/` (plates, datavis, sfx, music, dialogue, renders) — not in git.
  Drive: approved masters in `04-locked-cast-masters` (id 1UR4BaNbE6KNyXL6oktr1-oJrzqZ5DW63).

- STORAGE FACTS (27 Nov): GitHub holds everything in the repo (text, tools, approved image
  JPGs, small samples). Lost when the cloud machine is recycled: everything under the
  scratchpad (installed tools, sample libraries, NASA plates, WAV masters, per-line audio,
  renders, PNG originals) and the Codex login — all rebuildable from scripts except AI images,
  which is why approved images are committed as JPG. The Drive connector refuses files over
  10 MB, so large media needs rclone (owner authorises once; token entered by the owner as an
  environment variable; works from the next session) or the laptop. Owner raised the Codex
  parallel limit to 4 jobs.

- Episode 2 (27 Nov): outline approved by showrunner with rulings (Baron stays in the Valley;
  Kaguya pays the bank, crew owe her an impossible task; "You've worn one before" kept; PIP
  loses the oldest parcel label; the moon-lady reference cut to a wordless voice). Full script
  being written: `episodes/E02/script.md`. Then punch-up, critic, revision as for Episode 1.
- Episode 1 shot list: 484 shots, 35:13, 177 new image jobs; being rebuilt with rulings
  (full 16:9, act-break footage bumpers, five mouth patches) and a prioritised
  `episodes/E01/image-jobs.json`. New Mira/Lucía and three Ep 1 faces sent to owner for approval.
- Channel kit done: `channel/CHANNEL-KIT.md` (recommended name "Secret Universe Series").

- Episode 1 stills (27 Nov): shot list rebuilt — 487 shots, 35:31, 192 image jobs (53 / 89 / 50
  by priority) in `episodes/E01/image-jobs.json`. Stills runner started (2 Codex jobs; library
  builder capped at 2, stops after Episode 1 sets and props). Stills are kept in git as JPG
  (`episodes/E01/stills/`, log `stills-log.json`) because AI images cannot be regenerated
  identically. Mira/Lucía jobs run last pending the owner's approval of their new masters.

- OWNER DIRECTION 27 Nov (evening): (1) more, more interesting channel names — being generated
  (`channel/NAME-OPTIONS.md`); (2) speed above all — owner asked for 20 episodes live tonight;
  showrunner told the owner plainly this is not possible and gave real numbers; scripts for
  episodes 2–5 are being written in parallel; (3) no AI-disclosure wording in episodes,
  descriptions or channel copy — removed. SHOWRUNNER POSITION: YouTube's own "altered or
  synthetic content" upload setting is a declaration to YouTube about realistic-looking
  synthetic footage; the showrunner will not tick "no" on the owner's behalf and has told the
  owner so; the owner decides at upload; (4) Sun Wukong ruling accepted; (5) varied, colourful
  places, not mostly the ship; (6) Noakes, Temi, Mamani approved and LOCKED; Mira and Lucía to
  be redone again, more glamorous, Lucía slimmer — three candidates each being made;
  (7) brighter pictures — style line revised in the image runbook.
- LAPTOP: not connected. `DESKTOP-TUA5BIM` still does not offer any folder to cloud sessions,
  so rclone on the laptop cannot be used from here.
- Sound effects for Episode 1 done: 112 synthesised effects, index and mixing note in
  `samples/e01/sfx/`, generators in `production/tools/sfx/`.

- CAST COMPLETE FOR EPISODE 1 (27 Nov, late): owner chose Mira candidate 3 and Lucía candidate 2
  — LOCKED as masters (older versions kept in `old-v2/`); their reference sets are being rebuilt.
  Owner agreed that YouTube's own synthetic-content setting is answered truthfully at upload.
  Channel/series name still to be chosen by the owner from `channel/NAME-OPTIONS.md`.

- **CODEX USAGE LIMIT HIT (27 Nov, ~16:35 UTC).** Exact message: "You've hit your usage limit.
  Upgrade to Pro, visit https://chatgpt.com/settings/usage to purchase more credits or try
  again at 7:25 PM." 5-hour window resets 19:25 UTC; WEEKLY allowance at 99%, resets 2 Dec
  17:30 UTC. All image generation stopped; owner informed and will reset. To resume: library
  builder (finish Mira/Lucía reference sets from the new masters, then write the line
  MIRA-LUCIA-REFS-READY in `assets/LIBRARY-INDEX.md`; Arakawa master; customs crawler; Lucía
  suit from new master) and the Episode 1 stills runner (`episodes/E01/stills-log.json` says
  which jobs remain). Library so far: 91 accepted images; steps 1–5 done; Idris, Voss, Cass
  PROPOSED (need owner approval; Idris looks too close to Jax); 13 bright set versions made.

- NAMES DECIDED (27 Nov): channel **Legends Overheard**, show **Universe Undelivered**. Title
  card being remade. Owner is creating the YouTube channel with another agent
  (`production/prompts/PROMPT-youtube-channel-agent.md`) and starting a laptop bridge session
  (`production/prompts/PROMPT-laptop-bridge-session.md`) that will message this session.
  Do NOT call request_computer_folder: it would cut this session's link to the owner's other
  sessions, and the laptop offers no folder to cloud sessions anyway.
- Codex allowance reset by the owner (27 Nov, ~16:50 UTC); library builder and stills runner resumed.
- Episode 1 NASA plates: 34 usable (7 videos, 27 stills) in scratchpad `e01/plates/`, manifest
  `assets/e01-plates.json`; 8 SVS items blocked (403) — to be fetched by the laptop bridge.

- CODEX LIMIT RULE CHANGED (27 Nov, late): next time the limit is hit, wait for the time it
  shows and resume automatically; do not ask the owner to reset.

- MODEL OVERRIDE (27 Nov night): owner asked to prioritise Fable for all new agents until
  Saturday 07:30 India time (assumed), then return to the Opus/Sonnet hierarchy. A scheduled
  reminder fires at that time.
- Scripts: E01 final; E02 with critic; E03, E04, E05 in punch-up; E06–E09 being drafted (Fable).

- **CODEX IMAGE LIMIT HIT AGAIN (Fri 27 Nov 17:15 UTC)** — a separate 24-HOUR IMAGE limit:
  `usage_limit_reached`, `limit_window_minutes: 1440`, resets **Sat 28 Nov 14:52 UTC**. The
  error reports `plan_type: "plus"` — the owner should check the Codex login is on the Pro
  account. Per the owner's rule we WAIT; a wake-up is scheduled for 14:57 UTC to resume.
  5-hour was 65% and weekly 10% at the stop, so the daily image cap is the binding limit:
  roughly 150–170 images per 24 hours observed. Wrapper `codex_image.py` now detects it.
- Episode 1 stills: 65 of 192 accepted — ALL 53 priority-1 (cold open and Act 1) done;
  12 of 89 priority-2; 0 of 50 priority-3. Sheets: `samples/e01/stills/sheet-01..03.jpg`.
  Watch-list: Mira's ink-stained fingers read as purple nail tips (J019, J022, J044); Lucía has
  forearm tattoos in J016 that are not in her master; Mira's suit plate J061 has bare hands;
  `mira/ref-glass-screen.jpg` shows a crowd.
- Scripts (Fri night): E01 final; E02 in revision; E03, E04, E05 with critics; E06–E09 being drafted.

- Library builder also stopped on the 24-hour image limit (17:15 UTC Fri). Since the reset it
  accepted 57 images: Mira/Lucía reference sets complete; customs crawler; window fixes;
  Arakawa ×2, Idris ×2 (sheet `samples/library/approve-cast-2.jpg`); Seo/Oyuna angles;
  expressions for Jax, Mira, Lucía, Baron; Episode 2 PROPOSED cast and five places
  (`samples/library/approve-e02.jpg`). Still to make for Episode 2 after the reset: shuttle
  wreck (exterior, cockpit), Steadfast bridge, Valley's edge, and props (feather robe, forged
  branch, invoice, flasks, jars of sighs, docket, envelope, Seo's photo, Voss letter, drone).
  Owner to pick: Arakawa, Idris, Kaguya, Astolfo; approve Voss, Cass, Episode 2 places.

- EDIT ENGINE DONE (Fri 27 Nov night): `production/tools/edit/` (render.py, SCHEMA.md). Cold open
  v1 rendered (86 s; review copy `samples/e01/E01-coldopen-v1-review.mp4`, sent to owner) —
  a proof made before final stills/stems existed. Measured ~19 CPU-seconds per second of video:
  a 35-minute episode is about 3.7 h on 3 free cores. Master would be ~6 GB per episode.
  Now running: Act 1 assembly from the real shot list, stills, stems, score, sfx, datavis
  (`episodes/E01/act1-edit.json`, review parts in scratchpad `e01/renders/review/`).
- Data visuals done (`production/tools/datavis/`); bank logo being replaced (the yellow smiley
  is a protected mark). Laser map uses real LOLA data (PGDA product 78).
- Disk: cleared old look-test models; ~33 GB free.

- CAST AND EPISODE 2 LOOK APPROVED (Fri 27 Nov night): owner chose Kaguya 1, Astolfo 2, Arakawa 2,
  Idris 2; approved Voss and Cass; approved the five Episode 2 places. All LOCKED in
  `canon/CHARACTER-LOCKS.md` and `assets/`. To do when images resume: brighter Voss from his
  master; mask scenery out of Idris's and the bareheaded Baron's windows; reference sets for
  Idris, Arakawa, Kaguya, Astolfo.

## Research sprint results
| Job | Status | Output |
|---|---|---|
| Character bank | Done: 140 legends with rights and care notes | `research/characters/` |
| Footage audit | Done: 376 assets, 288 verified; SVS clips unverified | `assets/candidates.json`, `research/locations/` |
| Free voices | Done; owner chose Gemini voices instead | `samples/voices/` |
| Free music | Done; composed route approved; v2 upgrade running | `samples/music/` |
| Free look | Done; ink-art style (still-C) is the target, vector humans rejected by showrunner | `samples/look/` |
| Paid costs, upload, Drive | Done | `research/tooling/` |
| Gemini voices test | Running | `samples/voices/gemini/` |
| Nano Banana character test | Running | `samples/look-gemini/` |

Gemini API key is saved as a network secret on the Default environment
(host generativelanguage.googleapis.com, header x-goog-api-key; send a placeholder value).

## Next
1. Reconcile bible and season 1 with character-bank rights and footage verdicts.
2. Showrunner looks at look-test images; owner listens to voice and music samples.
3. Owner approves or redirects: premise, cast, look, sound, free vs paid.
4. Episode 1: outline → ruling → script → punch-up → critic → table-read for owner.

## Waiting on the owner
- Read the premise in `canon/SERIES-BIBLE.md` sections 1 and 6 (the Jax secret) and say yes/no.
- Listen/look at samples when they land.
- Create the YouTube channel (kit to follow in Drive `03-channel-kit`).

## Not yet solved
- Moving multi-GB finished videos from the cloud machine to Drive (connector handles small
  files only; rclone needs a one-time authorisation). See `research/tooling/` when it lands.
- Upload route to YouTube (API from server vs Chrome on the laptop as on Secret India).

## 27 Nov, evening (later)
- **Episode 2 script LOCKED** (`episodes/E02/script-v3.md`, 4,072 spoken words, about 35:40).
  Showrunner read all dialogue. Dialogue audio and shot list are being built.
- **Episode 5 critic back** (ready after fixes); rulings recorded at the end of
  `canon/season-01.md` (READ stamps, label one, Ilse, gates, Lupin's favour); revision to v3 running.
- **Episode 7 first draft done**; punch-up running. Episodes 6, 8, 9 drafts and critics on 3, 4 running.
- **Episode 1 production dialogue done** (voices only, 27:13): four review MP3s sent to the owner
  in chat and in `samples/e01/dialogue/`. Nobody has listened yet. Bank is now "Brindlelark" with
  our own lark logo (name web-searched only, no trademark-register check).
- **Six new locked masters** (kaguya, astolfo, arakawa, idris, voss, cass) copied to Drive
  `04-locked-cast-masters`.
- **Drive connector limit is now about 3 MB per file** from this session (was 10 MB). Three of the
  four dialogue MP3s (parts 1, 2, 4) did not upload; part 3 did. New review audio is cut into
  parts under 2.9 MB.

## 27 Nov, late evening — FORMAT UNDER REVIEW (owner)
- **Owner rejected the stills-only format** after the cold open: he wants real moving video —
  moving people, moving pictures, vibrant moving space footage — "real movie like". He asked for a
  new one-minute sample to judge BEFORE other picture/edit work continues. Stopped: Episode 1
  Act 1 stills assembly, Episode 2 shot list (both built on the stills format). Scripts continue.
- **Model use:** back to the normal hierarchy now (owner). No subagents on Fable.
- Motion routes checked from this machine: Codex has no video feature (animation flag is "under
  development", off). Free Hugging Face video spaces (LTX-2.5, LTX-2.3, Wan 2.2 image-to-video)
  are reachable but the anonymous allowance is used up; a free Hugging Face token is needed.
  25 real NASA videos are already on disk (Artemis I/II, LRO) for moving space footage.
- **Moving video works (27 Nov, ~17:52 UTC).** Owner saved a free Hugging Face token (network
  secret for host `lightricks-ltx-2-5.hf.space`, Default environment). `scratchpad/motion/i2v.py`
  turns an approved still into a 5-second 1472x832 moving clip in about 31 s with the open model
  LTX-2.5; first test `samples/motion/test1-jax-moving.mp4` (Jax bites and chews; face holds;
  black window stays black). Daily allowance on the free token is small and not yet measured.
  A builder is remaking the Episode 1 cold open with every shot moving, plus real NASA video.
- **Free allowance measured (27 Nov, 17:58 UTC): one 5-s clip per day.** The next call was refused
  ("272s requested vs. 105s left ... Try again in 23:53:41", reset ~17:52 UTC 28 Nov). Max 5 s per
  clip. Interim cut `E01-coldopen-v2-motion` moves only where real NASA video, the one Jax clip and
  the animated screens are; the other shots are still stills (marked `motion_pending`). The 10
  remaining clips are queued in `scratchpad/mv/gen_queue.sh`; details `production/MOTION-PIPELINE.md`.
  Needs a showrunner/owner ruling on how to get ~10 clips per episode (see that file).
- First drafts of Episodes 6, 8, 9 and the Episode 4 critic review are on disk. Next writing
  steps (punch-ups 6/8/9, revisions 3/4, finale) wait until the owner has judged the new sample;
  they run on Opus.
- **Owner's verdict on cold open v2 (27 Nov night):** frozen shots do not work at all; the LTX
  clip is not smooth or natural enough; none of the five routes offered is acceptable; check the
  Gemini route (subscription, like Codex). Research is in
  `research/tooling/video-generation-routes.md`. Waiting on the owner: run the six-clip test in
  Google Flow (`samples/motion/flow-test/`), and decide on the Antigravity CLI login test.
- **Antigravity CLI test done (27 Nov, 18:50 UTC):** signed in on the owner's Google AI Pro plan.
  No video capability (confirmed directly). It does make pictures from a reference
  (`samples/look-agy/`), a possible second picture route beside Codex. Details in
  `research/tooling/video-generation-routes.md`. Owner is making the six Flow test clips himself.
- **Flow/Omni test clips received and checked by frames (27 Nov night):** quality is the first
  that meets the owner's "real movie" bar: natural motion, faces hold, lip-sync works with Omni's
  own voice. Visible star watermark is forced for India accounts. Next: owner runs the 12-clip
  cold open pack (`samples/motion/flow-coldopen/`); showrunner cuts the full moving cold open.
  Decision after that: Google AI Ultra plan and who operates Flow. Results in
  `research/tooling/video-generation-routes.md`.
- **Flow automation (27 Nov night):** owner wants Flow automated. Not possible safely on the cloud
  machine (no safe Google sign-in here). Route: laptop Claude session operating Flow in the
  owner's own Chrome — prompt in `production/prompts/PROMPT-laptop-flow-operator.md`. Waiting on
  the owner to start that session and paste the prompt.

## 28 Nov — owner's new direction: free, in-house, archive footage
- Owner: paid video costs too much. Make videos free, with maximum work in-house (story, script,
  dialogue, screenplay) and footage from archives. He supplied a research memo (hybrid paid
  routing by shot class; and a free "archive comedy-drama" format with a comm card showing the
  speaker's portrait and a waveform) and two mock-up clips (made with a video generator, so they
  show the layout idea, not real archive film).
- Asked for: (1) a check of the memo's cost figures; (2) a first 5-minute sample in the free
  archive format, to see and hear, before deciding the route.
- Running: price check (Sonnet) → `research/tooling/cost-research-check.md`; sample builder
  (Opus) → `samples/e01/E01-archive-sample-*.mp4`, notes in `production/ARCHIVE-FORMAT.md`,
  footage log in `assets/archive-vault.json`.
- Showrunner's direction for the format: every episode is "PIP's file on the case"; archive
  clips are exhibits with PIP's dry filing slates; 4:3 film sits in PIP's Archive Viewer; real
  NASA video full-screen; the six Omni clips we already own appear as ship-camera feeds.
- Flow automation on the laptop and all paid-video questions are parked until the owner has
  judged this sample.

- **Done (28 Nov):** price check committed. Archive sample built: 4:52 of Episode 1 (cold open,
  title, scenes 1–5), `samples/e01/E01-archive-sample-720p.mp4` (27 MB) and `-480p.mp4` (11 MB);
  shot list `episodes/E01/archive-sample-shotlist.json`. On screen: 181 s old film in the
  viewer (52 cuts, 23 films), 49 s animated screens, 23 s ship-camera clips, 19 s NASA video,
  20 s titles. Vault: 36 films, 2.7 GB, all public domain by their own metadata (Prelinger) or
  US pre-1931 (Library of Congress), logged with source, sha256 and ranges used. Loudness
  −16.3 LUFS. Showrunner checked: contact sheet, frames, licence log, no frozen stretch over
  1.5 s except the sources slate. NOT checked: sound (nobody has listened), full playback.
- Known weaknesses: ~60% is black-and-white film in a box; our cast never acts on screen (still
  portraits on cards only); little colour; some slates too short to read; ship clips repeat.
- **Waiting on owner:** watch and listen to the sample, then choose the route.

## 28 Nov (evening IST) — owner rejects the archive format; animation route under test
- Owner: archive sample "doesn't sound that interesting" (60% black-and-white in a box, cast
  never acts). New idea from the owner: real NASA video as the main background, animated scenes
  and the ship on top of it, more animated ship screens, old films only in between. Asked
  whether animation can be made in-house on our machine.
- Machine check (14:15 UTC): container restarted (uptime 2 min) but the disk is intact: Codex
  CLI logged in, Antigravity CLI logged in, scratchpad 25 GB (707 dialogue stems, renders,
  36-film vault, voice model), repo clean. No new logins or installs needed.
- Running: (1) Opus builder — 60–75 s animated test of the Episode 1 cold open, cut-out
  characters with lip-sync from our stems over real NASA video, two looks (illustrated main,
  one photoreal cut-out shot) → `samples/e01/E01-animation-test-720p.mp4`, notes
  `production/ANIMATION-FORMAT.md`. (2) Sonnet benchmark — can a free, commercially usable
  model make a photoreal face talk on CPU → `research/tooling/cpu-talking-face-benchmark.md`.
- The scheduled "resume Codex stills" reminder was deleted: no large stills run until the
  format is decided. Codex daily limit resets ~14:52 UTC 28 Nov; still to confirm whether the
  login is on the Pro plan (the limit error said "plus").
- **Owner decision (28 Nov):** cast become animation characters, in whatever original style
  works best with our in-house tools; real NASA video is the main background. CLAUDE.md
  updated; the photoreal rule is retired. References he gave (prime-time flat 2D cartoon
  comedy) are for the class of animation, not designs to copy.
- Third test started (Opus): flat 2D cartoon look, full puppet rigs (limbs, walk cycle, 7+
  mouth shapes, head turn), a two-character Episode 1 scene over real NASA video →
  `samples/e01/E01-toon-test-720p.mp4`, notes `production/TOON-FORMAT.md`.
- To do once a look is chosen: redraw the 17 locked masters in that look and re-lock them.
- **Test 2 result (photoreal talking face on CPU): not usable.** MuseTalk v1.5 ran, but took
  144 s of compute per second of video (2 threads, machine shared), 7.6 GB RAM; mouth barely
  moves, lower face blurred and no longer Jax; rest of picture frozen. Licence of its training
  data and two helper weights not settled, so review-only. 20 min of talk = ~48 h per episode.
  Only MuseTalk was tried. Record: `research/tooling/cpu-talking-face-benchmark.md`. This
  closes the photoreal in-house route; animation tests 1 and 3 still running.
- **Test 1 landed (painted look):** 70 s cold open, `samples/e01/E01-animation-test-720p.mp4`
  (11 MB). Cut-out Jax, Temi and PIP with lip-sync from our stems (Rhubarb, 9 mouth shapes
  painted in code), blinks, pose swaps; painted ship over NASA lunar video; Moon/Earth video in
  windows (~47 of 70 s NASA). 40.6–51.0 s is the photoreal cut-out comparison. 10 pictures, all
  via Antigravity. Render ~24 CPU-s per second of video (35 min ≈ 4.7 h on 3 workers).
  Showrunner checked: contact sheet, frames, mouth close-ups (mouth moves, but opens small),
  no frozen stretch except the title. NOT checked: sound, sync by ear. Weakness: motion-comic
  feel — heads tilt but do not turn, arms change by whole-pose swap, no walking. Sent to owner.
  Notes: `production/ANIMATION-FORMAT.md`. Test 3 (flat cartoon, full rigs) still running.
- **Test 3 landed (flat cartoon, full puppet rigs):** 56 s, E01 customs-desk scene (Jax and
  Mira) plus a 7 s ship landing, `samples/e01/E01-toon-test-720p.mp4` (11 MB); designs next to
  masters in `samples/e01/E01-toon-characters.jpg`. Heads from pictures (front + three-quarter,
  no features); eyes, brows, 9 mouth shapes, arms, hands, legs drawn and driven in code; walk
  cycle, head turn, reaction beat, stamp slam. NASA video in view all 56 s (new plate logged in
  `assets/toon-test-plates.json`). 7 pictures. Render 30.5 CPU-s per second (unoptimised).
  Showrunner checked: contact sheet, 2 full frames, design sheet, no frozen stretch. NOT
  checked: sound, playback. Showrunner's view from frames: bodies and hands are crude (tube
  limbs), likeness to the masters is weak, pale patch on the desk; the picture tool's own
  full-body designs look far better than the code-drawn bodies. Notes `production/TOON-FORMAT.md`.
- Picture tools: Codex limit message names plan "plus" (not Pro), daily window reset 14:52 UTC,
  working again after reset. Antigravity picture quota ran out ~15:30 UTC (reset in ~4 h 40 m).
- **Waiting on owner:** watch tests 1 and 3, pick the look/direction. Showrunner's proposal:
  combine them — test 1's richer art with test 3's jointed, moving bodies, rigs cut from
  picture-made full-body designs.
- **Owner (28 Nov, after tests 1 and 3):** combine them — test 1's art with test 3's moving,
  walking bodies and real locations — and make the next test. Codex is on a Plus plan (owner
  confirmed), with plenty of allowance: use it freely, more pictures if they smooth the motion.
  CLAUDE.md updated. Test 4 (combined) started with the test 3 builder.
- **Owner (28 Nov, later):** keep building the test; because the picture will sit below
  photoreal video, audio (voices, music, tunes, sound) and story/scenes must be raised hard.
  Study the best and most-shared scenes in cinema, TV and online video; take inspiration from
  how they work; fit into our larger story. Longer video or full episode decided after the test.
- Started in parallel (all Opus): (a) scene study → `research/story/scene-study.md`,
  `canon/SCENE-PLAYBOOK.md` (proposal), audits `episodes/E01|E02/playbook-audit.md`, incl. a
  recommendation on episode length for animation; (b) voice bake-off of expressive open
  voice models on CPU, licence-clean → listening reel `samples/voices/bakeoff-28nov/`, notes
  `research/tooling/voice-upgrade.md`; (c) music and sound upgrade (better instruments, main
  theme and motifs, real effects, mix) → reel `samples/audio/upgrade-28nov/`, notes
  `research/tooling/audio-upgrade.md`, sources `assets/audio-sources.json`.
  Test 4 (combined animation) still building. Only the owner can judge the audio reels.
- **Scene study landed (28 Nov):** `research/story/scene-study.md` (53 entries, each claim
  marked checked-by-search or from-memory), `canon/SCENE-PLAYBOOK.md` (PROPOSAL, 29 scene
  engines, set-piece rule: 3 signature scenes per episode with one cut as a 30–60 s short;
  opening and re-hook rules), audits `episodes/E01|E02/playbook-audit.md` (5 upgrades each;
  both scripts were staged for no-lip-sync photoreal — backs of heads, hidden mouths — and
  should be restaged now that puppets lip-sync). Showcase scene proposed: E01 scene 21 (the
  cannonball story on the rim). Showrunner skimmed the playbook (parts 1 start, 2–5), has not
  read the study or audits in full.
- **Owner decisions pending from it:** episode length (writer recommends 22–26 min in two
  halves; or keep ~35 and release in two parts; or test E01 whole); whether to reopen locked
  E01/E02 for the upgrades. Showrunner rulings pending: Lucía's ribbon to Seo in ep 10; a
  Seo–Mattias scene in Season 2.
