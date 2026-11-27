# Free photoreal routes (researched 27 Nov 2026)

Method: official pages fetched with WebFetch (a small model summarises each page; quotes are as returned). NOT VERIFIED = could not open or page lacked the fact.

## PART 1 - Free GPU compute

| Service | Free allowance | Card? | Headless | Terms / notes |
|---|---|---|---|---|
| Kaggle Notebooks | NOT VERIFIED officially (docs pages returned title only). Secondary sources (Paperspace blog, https://blog.paperspace.com/gradient-vs-kaggle-2022/): ~30 GPU h/week, P100 16 GB or 2xT4, 12 h sessions. | No (phone verify for internet - NOT VERIFIED) | kaggle CLI. Token: `KAGGLE_API_TOKEN` env var or `~/.kaggle/access_token` (https://raw.githubusercontent.com/Kaggle/kaggle-api/main/docs/README.md). `kernels push` flags and `enable_internet` metadata: NOT VERIFIED (kernels.md not opened). | Kaggle ToS on commercial use/automation: NOT VERIFIED (page empty). |
| Google Colab free | Not published: "Colab does not publish these limits"; free "access to expensive resources like GPUs is heavily restricted"; max 12 h. | No | No official API. FAQ restricts "Bypassing the notebook interface to work mainly through a web UI... especially content generation" and lists "creating deepfakes". Treat as NOT suitable for headless batch. | https://research.google.com/colaboratory/faq.html ; commercial use not addressed, points to paid options. Pricing page returned 403. |
| Modal | Starter "$30 / month free credits" (https://modal.com/pricing). T4 $0.000164/s, L4 $0.000222/s, A10 $0.000306/s, L40S $0.000542/s, A100-40 $0.000583/s. So $30 = ~50 h T4 or ~15 h L40S/month. | Official page silent; third parties conflict. NOT VERIFIED | Python SDK + CLI; token ID/secret. Best fit for scripts. | Commercial/generative terms: NOT VERIFIED. |
| Lightning AI | Free: 30 credits to start, "up to 50 free GPU hours" interruptible; no monthly renewal listed; credits expire after 12 months; no card, phone number required; 2 concurrent GPUs, 1 GPU per Studio, A100/H100 4 h sessions (https://lightning.ai/pricing). | No | SDK/CLI: NOT VERIFIED | Terms NOT VERIFIED. One-time pool, not recurring. |
| Hugging Face ZeroGPU | Free 5 min/day, PRO 40 min/day, unauthenticated 2 min; half RTX Pro 6000 Blackwell 48 GB; "Included daily quota resets exactly 24 hours after your first GPU usage" (https://huggingface.co/docs/hub/spaces-zerogpu). PRO extra: $1 per 10 min. | No (PRO is paid) | Call someone's ZeroGPU Space via gradio_client with HF token (token usage for quota - standard documented behaviour, page for gradio_client NOT opened). Or host own Space (free: up to 2 ZeroGPU Spaces, account >30 days). | Per-Space licences apply. Inference Providers: Free users "None" monthly credits; PRO $2.00 (https://huggingface.co/docs/inference-providers/pricing). |
| Cloudflare Workers AI | "10,000 Neurons per day at no charge", resets 00:00 UTC (https://developers.cloudflare.com/workers-ai/platform/pricing/). Models: flux-1-schnell, flux-2-dev, flux-2-klein-4b ($0.000287 / 512 output tile = 26.05 neurons/tile), flux-2-klein-9b (1,363.64 neurons first MP). | Free plan without card: NOT VERIFIED | REST + API token; limit 720 req/min for text-to-image (https://developers.cloudflare.com/workers-ai/platform/limits/). Reference images supported (klein-4b "supports generating images based on reference images"; max count NOT VERIFIED). | My arithmetic: klein-4b 1024x1024 = 4 output tiles = ~104 neurons => ~95 images/day text-only; each 1024 reference adds 4 x 5.37 = ~21.5 neurons (1 ref: ~79/day, 2 refs: ~68/day). Terms link to BFL ToS (https://bfl.ai/legal/terms-of-service - NOT opened). klein-9b/dev weights are non-commercial; hosted-service commercial right NOT VERIFIED. |
| Together / Fireworks / Replicate / fal | Together pricing page: no free image models listed. Replicate: no free credits on pricing page (flux-schnell $3.00 per 1,000 images). fal: "New users receive free credits, and a free tier is available" (amount NOT VERIFIED), FLUX.1 schnell $0.003/MP. Fireworks: NOT VERIFIED. | - | API | One-time credits at best; not a recurring free route. |
| GCP $300 Welcome credit | Free Trial blocks GPUs: "Add GPUs to your VM instances" is among actions you can't take; "You can't request a quota increase"; "Your $300 credit can't pay for Gemini API in AI Studio costs, or for generative AI partner models offered as a managed API." (https://docs.cloud.google.com/free/docs/free-cloud-features). Upgrading to paid removes these restrictions (then GPUs are billed, credit may still apply - NOT VERIFIED). | Yes | gcloud | CPU-only VM pricing/Spot: NOT VERIFIED. Free-tier e2-micro only (useless for diffusion). |
| Oracle Always Free | Page returned 403. NOT VERIFIED (commonly CPU Ampere A1 only - from memory, unverified). | | | |
| Studio Lab (AWS) | Still described free, no card, GPU up to 4 h per session, ~1 GPU session/day (secondary: DataCamp June 2025; AWS docs via search). Interactive only, no API. | No | No | Weak for batch. |
| Paperspace/Saturn | NOT VERIFIED | | | |

### Google AI Pro developer benefit
- https://developers.google.com/program/plans-and-pricing: "$10 GenAI and Cloud monthly credit" (Pro $10, Ultra 5x $40, Ultra 20x $100). Plans page (https://one.google.com/about/google-ai-plans/): "$10 in monthly Google Cloud credits from Google Developer Program".
- Claim (https://developers.google.com/profile/help/benefits): subscribe, go to https://me.developers.google.com/benefits, "Select a billing account from the drop-down and apply the credit." Needs a personal Google Account (@gmail.com), a Developer Program profile, and billing.accounts.redeemPromotion IAM role on a billing account. "Only the primary plan subscriber can use these credits." Expire after a year. Countries: not stated on any page (NOT VERIFIED). Not appearing may simply mean it has not been claimed/billing account not linked.
- Via AI Studio (https://blog.google/innovation-and-ai/technology/developers-tools/google-cloud-credits-gdp-ai-studio/): "Using the Gemini API with Cloud billing requires a $5 minimum prepayment and balance before you can draw down promotional credits." So the $10 is not free-no-card API access to image models.
- The $300 trial credit cannot pay for Gemini API; the Pro credit can ("Gemini API, Google AI Studio, Firebase"), but needs a paid billing setup and the $5 prepay. This is paid-model access, not free open-model compute; owner said no ongoing fees.

## PART 2 - Open models

| Model | Licence (quote) | Size / VRAM | Reference / edit | Notes |
|---|---|---|---|---|
| FLUX.2 [klein] 4B | "licensed under the ... Apache 2.0" (https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | ~13 GB; 4 steps | "supports multi-reference editing" | Best fit for a 16 GB GPU. Speed on T4/P100: NOT VERIFIED (one user: 768x512 4-step ~19 s on 24 GB A10G). |
| FLUX.2 [klein] 9B | "falls under the FLUX Non-Commercial License" | ~29 GB | multi-reference | Not usable commercially as self-hosted weights; too big for T4. |
| FLUX.2 [dev] | "falls under the FLUX Non-Commercial License"; licence file 2(d): "You may use Output for any purpose (including for commercial purposes)" but 2(b): "only access, use, Distribute, or create Derivatives of the FLUX Model... for Non-Commercial Purposes"; 1(c) excludes "revenue-generating activity". (https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md) | 32B; 4-bit on RTX 4090 | character/object/style reference | Running it for a monetised channel is a legal grey area; do not rely on it. Get legal view or avoid. |
| FLUX.1 schnell | "Apache 2.0 ... personal, scientific, and commercial purposes" | 12B | text-only | Cannot hold a face. |
| FLUX.1 Kontext dev | "FLUX.1 [dev] Non-Commercial License"; card also says outputs may be used commercially (same ambiguity) | 12B | in-context character reference | Same grey area as FLUX.2 dev. |
| Qwen-Image-Edit-2511 | "Qwen-Image is licensed under Apache 2.0" (https://huggingface.co/Qwen/Qwen-Image-Edit-2511) | 20B BF16; VRAM NOT VERIFIED (needs heavy quantisation for 16 GB) | multi-image input, identity preservation | Strong but heavy. |
| HiDream-I1 | transformers "MIT License"; text encoders (Llama 3.1 8B) carry own licence | 17B | HiDream-E1.1 instruction editing | Heavy. |
| Z-Image-Turbo | Apache-2.0 (https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) | "fits comfortably within 16G VRAM", 8 NFE | text-only; Z-Image-Edit "To be released" on that card (may be outdated) | Photoreal quality good, no reference. Useful for sets/backgrounds. |
| SDXL + IP-Adapter-FaceID | "released exclusively for research purposes and is not intended for commercial use"; relies on InsightFace | - | face ID | AVOID for commercial. |
| InstantID | code Apache; "both manual-downloading and auto-downloading face models from insightface are for non-commercial research purposes only"; checkpoints research-limited | - | face ID | AVOID. |
| PuLID-FLUX | repo labelled Apache-2.0; page silent on insightface/commercial; runs on 16 GB (FP8). Sits on FLUX.1 dev (non-commercial) and, in typical use, InsightFace | 16 GB | face ID | Licence chain unclear; NOT VERIFIED. |
| insightface | code MIT; "pretrained models ... non-commercial research purposes only"; commercial licensing via contact@insightface.ai (https://github.com/deepinsight/insightface) | | | Any pipeline using buffalo_l/antelopev2 weights is non-commercial. |
| Character LoRA training | NOT VERIFIED (time/tools on T4 not researched) | | | |

Video:
- Wan2.2: "licensed under the Apache 2.0 License". I2V-A14B needs "at least 80GB VRAM"; TI2V-5B "can generate a 5-second 720P video in under 9 minutes on a single consumer-grade GPU" (https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B). 16 GB feasibility NOT VERIFIED.
- LTX-2: Community licence; $10M annual revenue threshold: "Entities with annual revenues of at least $10,000,000 ... are required to obtain a paid commercial use license" (via search summary of the licence text, https://ltx.io/model/license - page itself not opened). Under that, free commercial use. 19B; needs offload on small GPUs; makes audio too.
- HunyuanVideo-I2V: licence excludes "the territory of the European Union, United Kingdom and South Korea"; 60 GB minimum for 720p. Not for us.
- CogVideoX-5b-I2V: CogVideoX licence; commercial use requires registration, free below 1 million visits/month; ~5 GB with offload (A100 test) (https://huggingface.co/zai-org/CogVideoX-5b-I2V). Lower quality.

Lip-sync / talking head:
- MuseTalk: code "MIT"; model "available for any purpose, even commercially"; 4 GB laptop tested, 30fps+ on V100. Check whisper/dwpose/S3FD component licences. Mouth-region only; 256px face crop, soft quality.
- LatentSync: Apache-2.0; v1.5 8 GB, v1.6 18 GB inference.
- Wav2Lip: "can only be used for personal/research/non-commercial purposes" - NO.
- SadTalker: README: "updated to Apache 2.0" - VRAM not stated; quality dated.
- InfiniteTalk: Apache 2.0; image+audio to video; fp8 and low-VRAM flags; Wan-based so heavy.
- EchoMimic v2: Apache-2.0; tested on V100 16 GB.
- Hallo/Hallo3: Hallo3 repo shows MIT but says derived from CogVideoX-5B licence; NOT VERIFIED.

## PART 3 - Recommendation

1. Route A (best): Cloudflare Workers AI, FLUX.2 klein 4B (Apache weights) via REST, 10,000 neurons/day. ~70-95 images/day with 1-2 references (my arithmetic above) so ~430 images in ~5-7 days, then ~1 episode's 50-100 images per day. Setup: free Cloudflare account, create an API token scoped to Workers AI, store as network secret (host api.cloudflare.com, Authorization header) so the token never sits in files; account ID as env var. Risks: free plan card requirement NOT VERIFIED; allocation could change; hosted-terms (BFL ToS) not read; moderation; consistency depends on klein reference quality. Test in one hour: 1 character sheet + 3 reference-based shots, check face match across 10 shots.
2. Route B: Kaggle Notebook (P100/T4 ~30 h/week, unverified) running FLUX.2 klein 4B (diffusers) or Z-Image-Turbo, driven by `kaggle kernels push` with KAGGLE_API_TOKEN as env var/secret on kaggle.com host. Largest free quota; also hosts LatentSync/MuseTalk lip-sync and CogVideoX/LTX-2 video. Risks: phone verification, internet on/off, queue, automation tolerance in ToS NOT VERIFIED, no live output (poll and download). Test: push a kernel that loads klein 4B, makes 4 images, writes to output; time it.
3. Route C: Modal Starter $30/month (~50 T4 hours or ~15 L40S hours) for burst work: video (LTX-2 / Wan TI2V-5B), LoRA training, lipsync. Cleanest API. Risk: card/abuse policy NOT VERIFIED; credits expire monthly.
Skip: Colab (automation/content-generation restricted), GCP trial (GPU blocked), HF ZeroGPU as primary (5 min/day, quota shared, depends on third-party Spaces).

Honest gaps vs paid model: free routes give 4B-class reference editing, not Nano Banana-grade identity locking; expect to need character LoRA or manual rejection of ~30-50% of shots; video and lip-sync at hero quality are slow and small; free-service terms for monetised/generative batch jobs are mostly unread. Avoid InsightFace-based pipelines (non-commercial).

Handing a token over: network secret for a host injects an HTTP header (good for Cloudflare, Hugging Face, Modal API calls via HTTPS); Kaggle CLI needs the token as an environment variable KAGGLE_API_TOKEN (owner-entered).

## NOT VERIFIED list
Kaggle official quota/ToS/metadata; Colab pricing; Modal card requirement and ToS; Lightning ToS and API; Cloudflare free-plan card, reference limit, hosted commercial terms; Fireworks/Together free credits; Oracle; Paperspace; GCP CPU/Spot prices; Google Pro credit countries; LoRA training times; model speeds on T4/P100; Qwen-Image-Edit VRAM; LTX-2 licence text opened directly; Hallo licence.
