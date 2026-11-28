# Universe Undelivered — project brief

Written 28 Nov 2026 for the owner's own research into video options. Everything here is from
the project's files. Prices and product facts were found by web search on 27 Nov 2026 and were
not verified by buying anything.

## 1. What we are making

- **Show:** *Universe Undelivered*. **YouTube channel:** *Legends Overheard*.
- An original fiction series set in the real solar system. Premise: Earth's legends were never
  made up, they were overheard. The heroes of old stories are real people living out in space,
  and someone is deleting them from the official map. A broke courier ship, *The Unscheduled*,
  keeps getting pulled into their stories while delivering one mysterious parcel.
- **Tone:** fast, funny, dramatic, big-hearted. Comedy, drama, romance and action in balance.
- **Guests:** public-domain characters from world literature and legend, mixed from at least
  three sources and two cultures per episode (Baron Munchausen, Princess Kaguya, Don Quixote,
  Nasreddin, Arsène Lupin, Scheherazade, Icarus, Anansi, Sun Wukong, Sherlock Holmes, Nemo).
- **Crew (global cast):** Jax Vale (captain), Dr Mira Sen (cartographer), Lucía Ortega
  (engineer), PIP (ship's computer, a brass postal-audit machine), Han Seo-yeon (pilot and
  secret spy), Idris al-Rahhal (navigator), Oyuna Tseren (memoriser).
- **Episode length:** 30–40 minutes. **First test:** Season 1 = 10 episodes. Long-term idea:
  100–150 episodes.
- **Look:** photoreal people, ships and sets, bright and colourful, many different places per
  episode, matched to real NASA footage of space.

## 2. Rules the owner has set

- Pictures and video must look like a real film. Still or frozen shots are not acceptable.
- Faces must never change: every character, set and prop has one approved master picture, and
  every new picture or clip starts from it.
- Prefer subscriptions the owner already has over pay-per-use. Free or in-house for everything
  else (voices, music, sound, editing).
- No AI-disclosure wording in episodes or descriptions; YouTube's own "altered or synthetic
  content" question is answered truthfully.
- Nothing is published without the owner's sign-off.
- Rights: public-domain guests only; no copied film designs, dialogue or music; no deity or
  worshipped figure as a comic character; NASA footage only with logged credits.

## 3. What exists today

| Area | State |
|---|---|
| Series bible, season plan, writers' rulebook | Done (`canon/`) |
| Scripts | Ep 1 and 2 final and locked. Ep 5 final draft written, not yet read by the showrunner. Ep 3 and 4 reviewed, revisions pending. Ep 7 second draft. Ep 6, 8, 9 first drafts. Ep 10 not started. |
| Cast and sets | 17 characters and 5 Episode 2 sets have approved master pictures (`assets/`, `canon/CHARACTER-LOCKS.md`) |
| Pictures | Made through the Codex command-line tool on the ChatGPT Pro plan; about 150 pictures a day. Episode 1 has 65 accepted stills. A second route (Google's Antigravity command-line tool on the Google AI Pro plan) made one good test picture. |
| Voices | Free in-house voices (Kokoro). Episode 1 dialogue finished, 27 minutes. Nobody has listened to it yet. |
| Music and sound | Our own composed score and synthesised sound effects |
| Real footage | 25 NASA videos and many NASA stills downloaded, with credits logged |
| Editing | Our own edit engine: shot list in, finished 1080p video with sound out |
| Channel | Name chosen; channel not created yet |

## 4. How an episode is made

1. Script: outline → draft → comedy punch-up → independent review → revision → lock.
2. Shot list: every shot with its length, who speaks, what picture or footage it needs.
3. Pictures: one still per shot, made from the approved masters.
4. **Video: each still becomes a moving clip (this is the unsolved step — section 5).**
5. Sound: dialogue, music, effects.
6. Edit: clips, real NASA video, screens and titles assembled; "what was real" note at the end.
7. Owner reviews; upload.

## 5. The open problem: moving video

### What was tried

| Attempt | Result |
|---|---|
| Stills with camera moves | Rejected by the owner: frozen, not a film |
| Open model LTX-2.5 on Hugging Face (free) | Real motion, face held, but the owner found it not smooth or natural enough. Free allowance = 1 clip a day |
| **Google Gemini Omni Flash 1.2 in the Flow website** (owner's AI Pro plan) | Six 8-second clips from our stills. Natural motion, faces held, lip-sync works with the voice Omni generates. First result that meets the bar. |
| Google Antigravity command-line tool (signed in on AI Pro) | Confirmed: no video capability. It does make pictures. |
| OpenAI | No video product: Sora closed in April 2026 |

### What we learned about Omni in Flow

- Cost: 3 credits per second at 720p (an 8-second clip = 24 credits); 1 credit per second at
  360p. Upgrade to 1080p is free for clips up to 10 seconds.
- Credits: AI Pro 1,000 a month; Ultra $100 = 10,000; Ultra $200 = 25,000; plus 50 free a day.
  Extra credits: $25 for 2,500, $200 for 20,000 (one cent a credit).
- A small see-through star watermark sits bottom right on every clip. Google's help page says it
  is automatic for accounts in India, apparently with an exception for the top Ultra plan (not
  confirmed).
- Omni makes the voice itself. Not yet tested: whether a character keeps the same voice from
  clip to clip (Flow is said to have preset voices).
- Only reachable through the Flow website on a subscription, or through Google's pay-per-use API
  (about $0.07–0.10 a second). No command-line route on a subscription.

### How much video we need

- One 35-minute episode ≈ 2,500 seconds of generated video (about 80% of screen time, with
  retakes) ≈ 315 eight-second clips.
- Owner's target: 1–2 videos every day → 25,000 to 150,000 seconds a month, depending on
  whether a "video" is a full episode or a 12-minute part of one.

### Prices found so far (per episode of 2,500 generated seconds)

| Route | Per episode | Notes |
|---|---|---|
| Flow + extra credits, Omni 720p | about $75 | Best quality seen; runs through a website |
| Flow, Omni 360p + free 1080p upgrade | about $25 | Quality not tested |
| Omni by API | $175–250 | Fully automatic from our server |
| Cheaper APIs (Wan 2.6 flash, Veo 3.1 Lite) | $60–125 | Not tested; mostly no voice |
| "Unlimited" subscriptions (Luma, Hailuo, others) | $30–95 a month | Slow queues and caps; website only |
| Rented graphics cards + open model | $5–15 (guess) | No limits; lower quality; days of setup |

### What a video service must do for us (checklist for research)

1. **Start from our own picture** (image-to-video, first frame), ideally with extra reference
   pictures, so faces stay the same.
2. **Natural, smooth human motion**; the face must not drift within a clip.
3. Clips of **6–10 seconds or longer, 16:9, at least 720p** (1080p preferred), 24 fps.
4. **Speech with lip-sync**, and either the same voice for a character in every clip, or the
   ability to use our own recorded voice.
5. **Can be run without clicking a website**: an API or command-line tool, or terms that allow
   automating the website.
6. **Price per second at our volume** (25,000–150,000 seconds a month) and whether a flat
   subscription really covers it.
7. **Speed**: how many clips can run at once; queue times on cheaper tiers.
8. **Watermark**: is there a visible one, and on which plans.
9. **Rights**: commercial use on a monetised YouTube channel allowed.
10. **Content rules**: accepts photoreal fictional people (some services block realistic faces).

### Names worth checking

Google Gemini Omni / Veo (Flow, Gemini API, Vertex), ByteDance Seedance (Dreamina, CapCut),
Kuaishou Kling, Runway, Luma, MiniMax Hailuo, Alibaba Wan, Lightricks LTX, Pika, xAI Grok
Imagine, Midjourney video, Adobe Firefly; resellers such as fal.ai and Replicate; open models
that can run on rented graphics cards (Wan 2.2 / 2.5, LTX-2.5, HunyuanVideo, MiniMax H3).

## 6. Other open points

- Claude usage: every script and every clip check costs usage; a full episode a day is far
  more than the current plan has covered.
- Review: someone must watch what is made; 35–70 new minutes a day is hard to check.
- YouTube: a new channel posting long generated videos every day risks its rules on
  mass-produced content.
- Moving large files between the cloud machine and Google Drive is not solved (the connector
  takes about 3 MB per file).
- Owner has not yet given feedback on the Episode 1 dialogue audio or music.

## 7. Where things are

- Code and documents: GitHub repository `Universe-Series`, branch `claude/fervent-dirac-kbkcyh`.
- Running log: `STATUS.md`. Video research in full: `research/tooling/video-generation-routes.md`.
- Samples: `samples/` in the repository; Google Drive folder `Secret-Universe-Series`.
