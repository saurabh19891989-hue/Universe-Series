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
