# Image pipeline — how pictures are made for Secret Universe

Decided by the owner on 27 Nov 2026: **photoreal images are generated through OpenAI's Codex
CLI on the owner's ChatGPT Pro subscription.** No API key, no per-image charge. Any agent
making images follows this file. Do not ask the owner to repeat these instructions.

## 1. One-time setup per cloud session

**Short version:** run `bash production/tools/setup/codex_setup.sh`. It installs Codex if needed
and, if not logged in, prints the link and one-time code to give the owner. The manual steps
below are what it does.

The login lives only on the cloud machine and is lost when the machine is recycled.

```bash
npm install -g @openai/codex
```

```bash
mkdir -p ~/.codex && grep -q cli_auth_credentials_store ~/.codex/config.toml 2>/dev/null || echo 'cli_auth_credentials_store = "file"' >> ~/.codex/config.toml
```

```bash
codex login --device-auth
```

The last command prints a link and a one-time code (valid 15 minutes). Give both to the owner;
they open the link in a browser signed in to ChatGPT Pro and enter the code. Check with
`codex login status` (expect "Logged in using ChatGPT"). Never set `OPENAI_API_KEY`: that would
switch to paid API billing. Never copy `~/.codex/auth.json` anywhere.

## 2. Making one image

Always work in a scratch folder outside the repo (Codex is an agent that can run commands):

```bash
codex exec --skip-git-repo-check -s workspace-write -i REFERENCE_1.png -i REFERENCE_2.png "INSTRUCTION" > run.log 2>&1
```

Instruction template:

> Use your built-in image generation tool to generate exactly ONE image, landscape 16:9, and
> save it in the current directory as NAME.png. Do not write any code, do not use Python or any
> drawing library, do not use the fallback CLI/API mode, and do not generate more than one
> image. Image 1 is the reference for CHARACTER: keep the same face, hair, age and costume
> exactly. Image prompt: STYLE LINE + SHOT DESCRIPTION. After saving, reply with the file path
> and nothing else.

- The original is saved under `~/.codex/generated_images/`; copy it if NAME.png is missing.
- Measured: about 56 s per image, 1672x941, about 24k tokens per run.
- Wrapper script (logs every run): `production/tools/look/codex_image.py`.
- At most 4 jobs in parallel (owner raised it from 2 on 27 Nov).

**Style line (every prompt):** Photorealistic cinematic film still, 35mm, shallow depth of
field, practical lighting, natural skin texture, muted teal-and-amber grade, worn practical
costumes, no logos, no readable text, looks like a frame from a live-action science fiction
film, not an illustration, not CGI.

## 3. Characters must never change — the character library

- Every recurring character has ONE approved master image and a locked written description in
  `canon/CHARACTER-LOCKS.md`. The owner approves each face once ("casting"). After that the
  face is never regenerated from text alone.
- Masters and approved reference shots are kept in git: `assets/characters/<id>/master.jpg`
  plus `ref-01.jpg ...` (front, three-quarter, profile, helmet, full body). JPG quality 92,
  under 1.5 MB each. They are also copied to Google Drive `Secret-Universe-Series`.
- **Every** new image of a recurring character is generated with that character's master (and
  where useful one more approved reference) passed with `-i`, plus the locked description.
- Sets, the ship and props work the same way: `assets/sets/<id>/master.jpg`, `assets/ship/`,
  `assets/props/pip/`.
- A new image is accepted only after an agent has looked at it next to the master and judged
  face, hair, age and costume the same. Rejected images are deleted, not kept "just in case".
- Mouth and blink variants for a shot are made as edits of the approved shot, not new images.

## 3a. What the 30-image test showed (27 Nov, `samples/look-codex/`)
- One reference image keeps a character recognisably the same across expression, angle,
  lighting, helmet, full body and two-person shots. Profiles and very small faces drift a
  little: check them hardest.
- About 55 s and about 12k tokens per image; two-reference shots about 130 s. No refusals.
- **Real footage must be composited by us**, never by the model: asked to put a NASA photo in
  the window, the model redrew the Moon. Generate sets with pure-black windows and insert the
  real plate ourselves (`production/tools/look/composite_window.py`).
- **Mouth and blink:** an "identical image, mouth open" edit re-renders the whole frame, so
  cutting between frames would shimmer. Paste only the mouth or eye region onto the original
  with a soft edge (see `edit-talk-loop-patched.mp4`).
- The model tends to make women look 5–10 years older than written; say the age firmly.
- Pass the prompt on stdin in the wrapper; `-i` can swallow a prompt given as an argument.

## 4. Usage limit
The remaining allowance can be read (read-only) from the newest
`~/.codex/sessions/**/rollout-*.jsonl`, field `rate_limits` (5-hour and weekly percentages and
reset times). Measured: about 0.43 points of the 5-hour window per image, so roughly 230
images per window; the weekly counter moves about 2 points per 30 images. Check before and
after every batch and write both numbers in the usage log.


Image runs draw on the plan's Codex allowance. If a run fails with a usage-limit, rate-limit
or quota message: stop all generation at once, do not retry, record the exact message in
`STATUS.md`, and tell the owner — the owner resets it. Log every run in the episode's
`usage-log.json` (purpose, seconds, tokens, success).

## 5. Rules of the road (from OpenAI's pages, read 27 Nov 2026 — `research/tooling/openai-terms.md`)
The quotes were collected through a summarising fetch tool; re-check the live pages before relying on wording.
- **Ownership:** the Terms say the user owns the output. No separate commercial-use clause and
  no AI-disclosure duty was found, but output must never be presented as human-made. Our
  "what was real" end note and YouTube's synthetic-content tick cover this.
- **People:** no photoreal likeness of real people. Invented characters and public-domain
  figures are fine. Prompts must never name an actor or real person.
- **Marking:** images carry C2PA metadata and an invisible watermark; no visible watermark.
- **Scripted use:** `codex exec` in scripts is a documented mode, and device-code login is
  documented (beta) for trusted private machines, one login per machine. The Terms also forbid
  "automatically or programmatically extract[ing] data or Output"; OpenAI has not said how
  that applies to image batches. This is the main risk to the owner's account. Keep volumes
  moderate, at most 4 jobs at once, no retry loops, and never share the login.
- **Limits:** Pro has no five-hour limit; weekly limits may apply and no number is published.
  Images count against the same allowance. To make sure nothing is ever charged, the owner
  keeps auto top-up / auto reload OFF and buys no credits. Usage page:
  chatgpt.com/codex/settings/usage. No official way to read the remaining allowance from a script.
- **Chat window:** no permitted way to drive it from a script; a browser robot on chatgpt.com
  would breach the Terms. Not used.
- **Video:** nothing reachable from Codex (its animation feature makes GIFs). Not solved.

## 6. Fallbacks if the Codex route stops working
1. Cloudflare Workers AI free allowance with FLUX.2 klein 4B (Apache-2.0, accepts reference
   images) — `research/tooling/free-photoreal-routes.md`. Untested.
2. Kaggle free GPU notebooks with the same open model. Untested.
3. AI Horde (free, slow, faces drift) — tested, only good for one-off portraits.
Paid Google routes were tested and rejected by the owner (credit cannot be used).
