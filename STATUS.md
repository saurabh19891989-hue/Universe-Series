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
