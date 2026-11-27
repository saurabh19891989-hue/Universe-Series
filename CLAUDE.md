# Secret Universe — project rules

Original YouTube fiction series. Real space footage is the set; the story, characters and
score are ours. 30–40 minute episodes; first test is Season 1 = 10 episodes.

## Start here
1. Read `STATUS.md` (where we are, what is waiting on the owner).
2. Read `canon/SERIES-BIBLE.md`, `canon/season-01.md`, `canon/WRITERS-RULEBOOK.md`.
3. For an episode, read `episodes/ENN/WHERE-I-STOPPED.md` before doing anything.
State lives on disk, never only in a chat. Update `STATUS.md` when a milestone lands.

## Owner's standing preferences
- Replies short and plain: say what was checked and what was not.
- Fast-paced, never boring; balance of comedy, drama, romance, action. All references
  (Goodfellas, Guardians, British comedy, Zimmer, Ilaiyaraaja) are guidelines — improvise.
- Free tools or in-house work only for ongoing production (owner, 27 Nov). No paid
  subscriptions or per-episode API costs. Temporary credits may be used only as a one-time
  booster, never as something the pipeline depends on.
- Photoreal look: people, ships and sets must look real, to match the NASA footage. Cast must
  look global (no more than one core character per country).
- Stories mix at least three sources from at least two cultures per episode; inspiration only.
- Guests may be picked by the showrunner. Characters come from all over the world.
- Nothing is published or uploaded without the owner's sign-off.

## Agent hierarchy
| Tier | Model | Does |
|---|---|---|
| Showrunner (main session) | Fable | Talks to owner, rulings, canon, final look/listen checks, approvals |
| Writers and builders | Opus | Outlines, scripts, punch-up, scoring, art direction, one builder per episode |
| Independent critics | Opus | Pacing, continuity, rights, science, QA — never the agent that wrote the thing |
| Mechanical | Sonnet | Downloads, manifests, credits, subtitles, render scripts, benchmarks |

- Builders stop and ask the showrunner for a ruling before expensive or irreversible steps.
- Every script and every finished episode gets an independent second-agent review.
- Agents cannot hear audio. Never call audio "good"; send the owner a listening reel.
- Subagents do not run git; the main session commits.

## Hard rules
- Rights: guest characters must be public domain (see `research/characters/`). No modern
  copyrighted characters, no look-alikes of film/TV designs, no copied dialogue or music.
- Living religions: deities and worshipped figures are never comic characters. Owner decides
  any reverent appearance.
- Footage: only assets logged in `assets/` with source URL, exact credit and licence. Strip
  original audio. No NASA/ESA logos on fictional things; no implied endorsement.
- Honesty on screen: fiction is fiction. Each episode ends with a short "what was real" note.
- Secrets never go in the repo, the chat, or environment variables set by an agent.
- Heavy compute runs as scripts on the cloud machine; keep watchers to one loop, no leaks.
- Large media never goes in git. Models, caches and renders live outside the repo; finished
  files go to Google Drive.

## Where things are
- `canon/` bible, season plans, canon ledger, writers' rulebook
- `research/` v0.1 baseline, character bank, locations, tooling
- `assets/` footage manifests and credits
- `production/` tools and tests; `samples/` small review samples
- `episodes/ENN/` brief, outline, script, shotlist, review, credits, WHERE-I-STOPPED.md
- Google Drive (owner's alumni.iitd account): folder `Secret-Universe-Series`
  id `1b128WbDC7xrUCYKpxGzg6PyYXZ_s4Z98`; subfolders `01-samples-for-review`
  (`1nONmvgycQCzwYwPkZwBzElXSnHrqFmN2`), `02-episodes` (`15smuw3a-OWq7rsEOB5aiJq4kQUT7ecQ8`),
  `03-channel-kit` (`11vWxvyusNLGXtmJ90D6HAV1sH_lXo7OP`).
- Git: develop on branch `claude/fervent-dirac-kbkcyh`.
