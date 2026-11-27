# Paid tooling options: cost to upgrade from free tools

All figures "checked 2026-11-27" against the URL shown in each row. A blank or "NOT VERIFIED" means the page did not load, showed no price (JS-rendered, "$-" placeholders), or returned 403. Nothing below was filled from memory. Prices change; the pages marked "Black Friday" or "through Dec 31, 2026" are promotional.

**Production assumptions (from brief):** 1 episode = 33,000 characters of dialogue (about 5,500 words, about 37 min of speech) across 6-8 voices; about 25 min music in about 20 cues; 60-100 illustrations; optional 20 hero shots x 5 s = 100 s video; optional lip-sync on 10 min. 10 episodes in 2.5 months = **4 episodes/month**. I assume **1.5x generation overhead** on voice (retakes) and about **2x** on images and video (rejected tries). These multipliers are my assumptions, not sourced.

**FX rate:** 1 USD = 92.45 INR (frankfurter.dev, ECB data dated 2026-11-26; https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR, checked 2026-11-27).

---

## a) Voices

| Service | Plan / price | What it includes | Commercial / monetised YouTube | Source (checked 2026-11-27) |
|---|---|---|---|---|
| ElevenLabs | Free $0 (10k credits); Starter $6/mo ($1 first month); Creator $22/mo (121k); Pro $99 (600k); Scale $299 (1.8M); Business $990 (6M) | 1 credit = 1 character for most models; 0.5 credit/char via API for Turbo, Flash, v3 Conversational. Extra audio approx $0.20/min (Starter) to $0.17/min (Pro+). Models named on page: Eleven v4, v3, Multilingual v2, Turbo, Flash | Starter and above yes. Free: "Not listed" on page | https://elevenlabs.io/pricing |
| ElevenLabs API | Per 1K characters: v3 $0.08 (multi-speaker dialogue, 5,000-char request limit); Multilingual v2 $0.08; Flash/Turbo $0.04 | Music API $0.15/min, 5-min max per generation. No separate price listed for voice design or text-to-dialogue | Music: commercial licence needs Starter or higher | https://elevenlabs.io/pricing/api |
| Google Gemini TTS | `gemini-3.8-flash-tts`: audio out $9/1M tokens through 2026-12-31, then $18; `gemini-3.8-flash-lite-tts` $6 then $12. Audio = 25 tokens/s. Free tier "free of charge" | Per episode: about 2,200 s x 25 = 55k tokens, about $0.50 (until 31 Dec) or $1.00 (after) per take | Paid tier: terms page not read. Free-tier commercial terms NOT VERIFIED | https://aistudio.google.com/docs/pricing |
| OpenAI TTS | `gpt-4o-mini-tts`: text in $0.60/1M, audio out $12/1M tokens. Page marks model and snapshots **Deprecated** | 2,000-token input cap | Not stated on page | https://developers.openai.com/api/docs/models/gpt-4o-mini-tts |
| Azure Speech (official version of edge-tts voices) | Neural TTS free tier F0: 0.5M chars/month. Paid per 1M chars: **price not shown** (page prints "$-") | en-IN Neural HD: Diya, Meera, Aarti, Arjun, Neerja, Lavanya (DragonHD). Standard en-IN: Aarav, Aashi, Ananya, Kavya, Kunal, Rehaan, Prabhat, Neerja, Arjun, Aarti plus Indic variants | Not read (NOT VERIFIED) | https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/ ; voices: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts |
| Cartesia | Free $0 (20K credits); Pro $5 (100K); Startup $49 (1.25M); Scale $299 (8M). 1 credit/char (Sonic), about 750-800 credits/min. Overage $65/$45/$38 per 1M | Instant voice cloning on Pro | Pro and above list a commercial licence; Free does not | https://cartesia.ai/pricing |
| Fish Audio | Free (8,000 credits, 500 chars/generation); Plus $11/mo annual ($15 monthly), 250k credits; Pro $75/mo annual ($100 monthly), 2M credits. About 600-625 credits per minute | Voice Design on Plus. API billed pay-as-you-go, rate NOT shown | Plus/Pro allowed. Free: page contradicts itself (feature list says yes, FAQ says personal only), so treat as no | https://fish.audio/pricing/ |
| Hume | Page loaded was an evaluation/Decision-API page with no TTS pricing | NOT VERIFIED | NOT VERIFIED | https://hume.ai/pricing |
| Resemble | Page returned detection/identity pricing only, no TTS pricing | NOT VERIFIED | NOT VERIFIED | https://www.resemble.ai/pricing/ |
| PlayHT | Not fetched | NOT VERIFIED | NOT VERIFIED | n/a |
| Open: Chatterbox (Resemble), Kokoro | Free, self-hosted | Licences from Hugging Face model cards: ResembleAI/chatterbox = MIT; hexgrad/Kokoro-82M = Apache-2.0 | Yes (permissive licences) | https://huggingface.co/api/models/ResembleAI/chatterbox |

**Indian-English / accented English:** Verified only for Azure (list of 6 HD plus about 14 standard en-IN voices, above). ElevenLabs, Gemini, Cartesia and Fish accent coverage was not checked on their pages (NOT VERIFIED); audition them with a sample script before subscribing. Note: Azure's per-character price could not be read, so Azure is excluded from the tier arithmetic.

**ElevenLabs credit arithmetic (estimate):** 33,000 chars = 33,000 credits per clean pass; with 1.5x retakes = 49,500. Creator (121k) covers about 2.4 episodes/month; 4 episodes need about 198,000 credits.

---

## b) Music

| Service | Price | Commercial rights / caveats | Source (checked 2026-11-27) |
|---|---|---|---|
| Suno | Free: 50 credits/day, no downloads, **no commercial rights**. Pro $8 (annual billing; $10 monthly shown), 2,500 credits, **20 downloads/mo**. Premier $24 ($30), 10,000 credits, **60 downloads/mo**. Platinum $100 ($120), 15,000 credits, 120 downloads/mo | Help centre: free plan "Suno is the owner of the songs", non-commercial only; Pro/Premier "you own the songs". "May not be eligible for copyright protection" because US law protects human authorship. Third-party blogs (unverified) say upgrading is not retroactive and that Content ID can still flag AI tracks | https://suno.com/pricing ; https://help.suno.com/en/articles/2746945 |
| ElevenLabs Music | $0.15/min via API, 5-min max per generation | Commercial licence needs Starter or higher | https://elevenlabs.io/pricing/api |
| Google Lyria (Gemini API) | Lyria 3.5 full song $0.08; Lyria 3 Clip (30 s) $0.04; Lyria 3 Pro full song $0.08. No free tier | Commercial terms NOT VERIFIED. SynthID watermark presence not checked | https://aistudio.google.com/docs/pricing |
| Udio | Page text empty | NOT VERIFIED | https://www.udio.com/pricing |
| Stable Audio | Page text empty | NOT VERIFIED | https://stableaudio.com/pricing |
| Epidemic Sound | Prices not rendered; plans Creator, Pro, Enterprise, Business; "no additional cost when you publish or monetize" | Per-plan YouTube terms NOT VERIFIED | https://www.epidemicsound.com/pricing/ |
| Artlist | Music plan prices not on that page. AI plans (images/video) $11.99, $23.99, $59.99 /mo annual | Licence for YouTube monetisation NOT VERIFIED | https://artlist.io/pricing |
| Soundstripe | Page failed to load | NOT VERIFIED | https://soundstripe.com/pricing |
| Open: ACE-Step v1 3.5B | Free, self-hosted | Apache-2.0 (HF model card) | https://huggingface.co/api/models/ACE-Step/ACE-Step-v1-3.5B |

**Content ID / ownership caveat:** Suno's own help page says AI songs may not be copyrightable. Because no copyright exists to register, do not register the tracks with a distributor or Content ID service; a false claim against your own audio is the main risk. Keep the generation logs and plan receipts as evidence of licence.

**Cost per episode (estimate):** Suno needs about 20 cues/episode x 4 = 80 downloads/month, which exceeds even Premier (60). Lyria 3.5: 20 cues x 3 tries x $0.08 = $4.80. ElevenLabs Music: 25 min x $0.15 x 2 tries = $7.50.

---

## c) Images (consistent characters)

| Service | Price | Commercial | Source (checked 2026-11-27) |
|---|---|---|---|
| Gemini `gemini-nano-banana-2.1` | $0.0336 (1K), $0.0504 (2K), $0.113 (4K) per image. No free tier | Terms not read | https://aistudio.google.com/docs/pricing |
| Gemini `gemini-3.1-flash-image` | $0.045 (0.5K), $0.067 (1K), $0.101 (2K), $0.151 (4K) | same | same |
| Gemini `gemini-3-pro-image` | $0.134 (1K/2K), $0.24 (4K) | same | same |
| `gemini-2.5-flash-image` | $0.039; deprecated, shutdown 2027-03-15 | same | same |
| Black Forest Labs API | Kontext [pro] $0.04/img, [max] $0.08/img. FLUX.2 [pro] $0.03 first MP; [klein] 4B $0.014 first MP; reference images extra (e.g. klein $0.001/MP). FLUX 3 Image $0.048 at 1K | Pay-as-you-go API. Open-weight self-hosting needs Builder/Platform/Professional tier (price not shown). FLUX.1-Kontext-dev licence on HF = "other" (not a standard open licence) | https://bfl.ai/pricing |
| Runway API (resale) | Gen-4 Image $0.05 (720p)/$0.08 (1080p); Turbo $0.02; Nano Banana 2.1 $0.04/$0.06/$0.12; Ideogram 4.5 $0.01-$0.25; GPT Image 2 $0.01-$0.41 | Terms not read | https://docs.dev.runwayml.com/guides/pricing/ |
| OpenAI `gpt-image-2` | Token pricing $8 in / $30 out per 1M image tokens; model page says **deprecated**; per-image figure not shown | NOT VERIFIED | https://developers.openai.com/api/docs/pricing |
| Midjourney | Basic $8, Standard $24, Pro $48, Mega $96 /mo (annual; $10/$30/$60/$120 monthly). 3.3/15/30/60 fast hrs | "You own" outputs, commercial use allowed with exceptions in ToS. No API listed | https://www.midjourney.com/pricing |
| Recraft | Plan prices not shown | Free-plan images "not licensed for commercial use" | https://www.recraft.ai/pricing |
| Ideogram, Leonardo | HTTP 403 | NOT VERIFIED | n/a |

**Free tier usable commercially?** None verified. Gemini images: no free tier. Recraft free: not commercial. BFL: API is paid. Self-hosted FLUX.1-schnell is Apache-2.0 (HF card, https://huggingface.co/api/models/black-forest-labs/FLUX.1-schnell), which is the only verified commercially free image route.

---

## d) Image-to-video (hero shots)

| Service | Price per second | Notes | Source (checked 2026-11-27) |
|---|---|---|---|
| Runway Gen-4 Turbo | $0.05 | via Runway API, 1 credit = $0.01 | https://docs.dev.runwayml.com/guides/pricing/ |
| Runway Gen-4.5 | $0.12 | same | same |
| Kling 3.0 Standard / Pro (via Runway) | $0.09 / $0.12 no audio; $0.13 / $0.17 with audio; 4K $0.43 | Kling direct page returned no figures | same |
| Veo 3.1 / Fast (via Runway) | $0.20-$0.40 / $0.10-$0.15 | **Google's own Veo 3.1 preview models are shut down in the Gemini API (2026-10-22)**; page recommends `gemini-omni-1.2-flash` (3-15 s, native audio; price not shown) | same; https://aistudio.google.com/docs/video |
| Wan 3.0 (via Runway) | $0.05 (480p), $0.10 (720p), $0.20 (1080p) | | same |
| Seedance 2.0 (via Runway) | $0.14 (480p) to $0.40 (1080p) | | same |
| Luma Ray3.2 | credits only: 5 s clip = 20 credits (360p) to 400 (1080p); USD per credit not shown; commercial rights not stated | | https://lumalabs.ai/api/pricing |
| Sora, Hailuo/MiniMax | not fetched | NOT VERIFIED | n/a |
| Open: Wan2.2-I2V-A14B, Wan2.1 | self-hosted | Apache-2.0 (HF cards) | https://huggingface.co/api/models/Wan-AI/Wan2.2-I2V-A14B |

Max length/resolution and commercial rights per vendor were mostly not on the pages read; treat as NOT VERIFIED except where noted.

---

## e) Lip-sync / talking characters

| Tool | Price | Licence / commercial | Source (checked 2026-11-27) |
|---|---|---|---|
| Runway Act-Two | $0.05/s (API). 10 min = 600 s = $30 per clean pass | Terms not read | https://docs.dev.runwayml.com/guides/pricing/ |
| HeyGen | Free $0 (3 watermarked videos, 1 min); Creator $29/mo ($24 annual), 600 credits; Pro $49; Business $149 | Per-plan commercial rights not stated; avatar-oriented, not for illustrated characters | https://www.heygen.com/pricing |
| Hedra | Play plan prices not on page; API is a prepaid USD wallet; GPU H100 $3.00/hr, RTX 4090 $0.89/hr | NOT VERIFIED | https://www.hedra.com/pricing |
| MuseTalk (open) | free | MIT (HF card) | https://huggingface.co/api/models/TMElyralab/MuseTalk |
| LatentSync 1.5 / 1.6 (open) | free | OpenRAIL++ on HF cards (use-based restrictions; read before commercial use) | https://huggingface.co/api/models/ByteDance/LatentSync-1.6 |
| Wav2Lip (open) | free | Licence NOT VERIFIED (GitHub API was blocked in this session) | n/a |

---

## f) Rent a GPU

| Provider | 24 GB class | 48 GB class | Source (checked 2026-11-27) |
|---|---|---|---|
| RunPod | RTX 4090 $0.34/hr community, $0.89 secure; L4 $0.44/$0.69; RTX A5000 $0.16/$0.27 | RTX A6000 $0.33/$0.69; L40S $0.79/$1.09 | https://www.runpod.io/pricing |
| Lambda | A10 $1.29/hr | A6000 $1.09/hr (L40S not listed) | https://lambda.com/pricing |
| Modal (per second) | L4 $0.000222/s = $0.80/hr; A10 $0.000306/s = $1.10/hr | L40S $0.000542/s = $1.95/hr. Starter plan $30/mo free credits | https://modal.com/pricing |
| Replicate (reference) | | L40S $0.000975/s = $3.51/hr | https://replicate.com/pricing |
| Vast.ai | live grid, no figures captured | NOT VERIFIED | https://vast.ai/pricing |

Hourly conversions are my arithmetic (per-second x 3,600).

**Commercially licensed open models (from HF cards):** FLUX.1-schnell Apache-2.0; Wan2.2-I2V-A14B and Wan2.1-I2V-14B Apache-2.0; Chatterbox MIT; Kokoro Apache-2.0; ACE-Step v1 3.5B Apache-2.0; MuseTalk MIT. Not freely commercial: FLUX.1-Kontext-dev ("other"), LTX-Video ("other"), LatentSync (OpenRAIL++).

**Throughput:** I did not benchmark or find sourced throughput numbers. For planning I assume (unverified, test first) 4 GPU-hours/episode for music, 2-3 for lip-sync on a 24 GB card at $0.34/hr community pricing; video generation on Wan needs far more time and is not budgeted. Community-cloud instances can be interrupted.

---

## Budget tiers (ESTIMATES; 4 episodes/month; INR at 92.45)

### LEAN: all stills, TTS and open models, no paid video
| Item | Arithmetic (per episode) | USD |
|---|---|---|
| Voices: Gemini 3.8 flash TTS | 55,000 tokens x 1.5 retakes = 82,500 x $18/1M (post-2026 rate) | 1.49 (plus about 0.01 text input) = 1.50 |
| Music: ACE-Step on RunPod 4090 community | 4 h x $0.34 | 1.36 |
| Images: nano-banana-2.1, 1K | 100 images x 2 tries x $0.0336 | 6.72 |
| Lip-sync: MuseTalk on RunPod 4090 | 2 h x $0.34 | 0.68 |
| Hero shots | none (pan/zoom on stills) | 0 |
| **Per episode** | | **10.26 = INR 949** |
| **Per month** | 4 x 10.26 | **41.04 = INR 3,794** |

### BALANCED: ElevenLabs voices, Lyria music, Gen-4 Turbo hero shots
| Item | Arithmetic | USD |
|---|---|---|
| Voices: ElevenLabs Creator | $22 + overage: need 198,000 credits, have 121,000, shortfall 77,000. At assumed 900 chars/min = 86 min x $0.18/min = about 15.4 | 37.4 per month |
| Music: Lyria 3.5 (per ep) | 20 cues x 3 x $0.08 | 4.80 |
| Images: nano-banana-2.1, 2K (per ep) | 200 x $0.0504 | 10.08 |
| Hero shots: Gen-4 Turbo (per ep) | 100 s x 2 tries x $0.05 | 10.00 |
| Lip-sync: MuseTalk 4090 (per ep) | 3 h x $0.34 | 1.02 |
| **Per month** | 4 x (4.80+10.08+10.00+1.02) = 103.60; + 37.40 | **141.00 = INR 13,035** |
| **Per episode (average)** | 141.00 / 4 | **35.25 = INR 3,259** |

### PREMIUM: ElevenLabs Pro, two music engines, Kling Pro, Act-Two lip-sync
| Item | Arithmetic | USD |
|---|---|---|
| Voices: ElevenLabs Pro | flat, 600k credits cover 198k | 99 per month |
| Music (per ep) | ElevenLabs Music 25 min x $0.15 x 2 = 7.50; Lyria 4.80 | 12.30 |
| Images: gemini-3-pro-image (per ep) | 150 x $0.134 | 20.10 |
| Hero shots: Kling 3.0 Pro no audio via Runway (per ep) | 100 s x 2 x $0.12 | 24.00 |
| Lip-sync: Act-Two (per ep) | 600 s x 1.5 x $0.05 | 45.00 |
| **Per month** | 4 x 101.40 = 405.60; + 99 | **504.60 = INR 46,649** |
| **Per episode (average)** | 504.60 / 4 | **126.15 = INR 11,663** |

Not included: taxes (GST), payment FX fees, stock-footage music libraries, rejected-take overheads beyond the multipliers above, any plan whose price could not be read. Audio-in-video from Kling/Veo is excluded (no audio assumed).

**Biggest single upgrade for the least money:** voices. Dialogue carries a 35-minute show, and the jump from a free/default TTS to ElevenLabs Creator (about $22/mo, about $37/mo at 4 episodes) is the largest audible change per dollar, especially with v3 multi-speaker dialogue. A cheaper test: the $0.0336 images and $1.50 Gemini TTS in LEAN already cover most of the show, so audition ElevenLabs' free 10k credits against Gemini TTS and Azure en-IN on one scene before paying. Caveat: I could not verify accent quality, so that audition decides it. The second-best value is the music step: Lyria at $4.80/episode versus Suno, which cannot cover 80 downloads/month on any plan below Platinum.
