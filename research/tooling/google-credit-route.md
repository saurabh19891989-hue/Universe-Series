# Google credit route for Gemini image + TTS (checked 2026-11-27)

All quotes come from pages fetched on 2026-11-27. The fetch tool summarises pages, so some quotes are as the tool returned them.

## 1. Can the $300 Welcome credit be spent?

| Target | Answer | Source and quote |
|---|---|---|
| (a) Gemini Developer API / AI Studio | NO | https://aistudio.google.com/docs/billing : "the Google Cloud Welcome credit or free trial credit can't be used towards the Gemini API or AI Studio." Also "Gemini API usage costs are specifically excluded from the $300 Google Cloud Free Trial". Prepay: "The minimum purchase is $5." |
| (b) Vertex AI (now "Gemini platform"/"Agent Platform") | CONDITIONAL, and likely NO for the owner if they upgrade now | https://docs.cloud.google.com/free/docs/free-cloud-features : "The $300 credit can't pay for Gemini platform (formerly known as Gemini Enterprise Agent Platform, Vertex AI) services" "if you sign up for a free trial or upgrade to a paid account on or after November 16, 2026." The page mentions no exception for older accounts. |

Free-trial terms, same page:
- "preloaded with $300 in free Welcome credit which is valid for 90 days".
- "You keep any unused credit until it expires 90 days from the Free Trial signup"; upgrading ends the trial and you are billed beyond the credit.
- "While your billing account is a non-billable Free trial account, you can't ... Request a quota increase." (also no GPUs, Marketplace).
- "You can't access or use the $300 credit for a generative AI partner model that is offered as a managed API".

Reading: the Nov 16, 2026 cutoff reads as a sign-up/upgrade date. Two possible readings: (i) an account that signed up before Nov 16 and has not upgraded keeps Vertex eligibility; (ii) an upgrade after Nov 16 loses it. The page does not say which. UNCERTAIN. The owner's sign-up date is unknown. Check Billing > Overview: if the credit shows in the trial and the account is still "Free trial", try Vertex, but do NOT click "Activate/Upgrade" until confirmed.

NOT VERIFIED: the Vertex pricing page (https://cloud.google.com/vertex-ai/generative-ai/pricing) returned only a title in the fetch, so no Vertex prices and no Vertex-pricing credit note were read. I did not find a statement on whether a free-trial (non-billable) account can call Vertex image/TTS models, or about per-model quota there.

## 2. Models on Vertex vs AI Studio

| Model | Vertex ID / regions (source) | AI Studio paid price (https://aistudio.google.com/docs/pricing) |
|---|---|---|
| Gemini 3.1 Flash Image | `gemini-3.1-flash-image`; `global`, multi-region `us`, `eu` (docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-flash-image) | "$0.067 per 1K image", $0.101 2K, $0.151 4K, $0.045 0.5K. Free tier "Not available". |
| Gemini 3 Pro Image | `gemini-3-pro-image`; `global` only (.../models/gemini/3-pro-image) | "$0.134 per 1K/2K image", $0.24 4K |
| `gemini-nano-banana-2.1` | NOT VERIFIED on Vertex. AI Studio pricing lists "Gemini Nano Banana 2.1" with free tier "Not available". | price NOT VERIFIED |
| Gemini TTS | `gemini-3.1-flash-tts-preview` (global only), `gemini-2.5-flash-tts`, `gemini-2.5-flash-lite-preview-tts`, `gemini-2.5-pro-tts` (global plus US/EU regions) (https://docs.cloud.google.com/text-to-speech/docs/gemini-tts) | 3.1 Flash TTS Preview $1.00/M in, $20.00/M out; 3.8 Flash TTS $0.50/$9.00 until 2026-12-31. TTS free tier "Free of charge". |

Vertex prices: NOT VERIFIED (page did not load). Do not assume they match AI Studio.

## 3. Auth for Vertex from a headless server with a static-header proxy

(a) Vertex API key / express mode (exists, per https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview):
- Eligibility: "Agent Platform is available in express mode for developers with a `@gmail.com` Google Account."
- Header: "Pass your API key in the `x-goog-api-key` HTTP header." The `?key=` query parameter is available if headers cannot be set.
- Host: global endpoint, no project or location: `https://aiplatform.googleapis.com/v1/publishers/google/models/MODEL_ID:generateContent`.
- Models: the page's table lists `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-2.5-flash-image` (image generation). No TTS models are in the list (per the fetch summary), so TTS via express mode is NOT confirmed. Use AI Studio for TTS, which already works.
- Free tier: "During the 90 day limit of the free tier for new Google Cloud users"; 2.5 models are capped at 10 requests per minute; Gemini 3 limits are dynamic.
- Billing: "If you are an existing Google Cloud user or after enabling billing, the 90 day free tier is removed." "You can increase your quota limits at any time by enabling billing." "After enabling billing, you pay only for what you use." https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys : "If you are an existing Google Cloud user, you can link your existing billing account to get an API key immediately". The pages do not say whether the credit is applied, so that is NOT VERIFIED; the credit exclusion above is the controlling text.
- Express mode is not limited to brand-new users (existing users can link billing). Whether express mode in free tier is the only free path is as quoted above.

(b) Service-account JSON key plus google-auth: works, but needs OAuth token refresh by the client. A header-injecting proxy cannot do this unless the key file is on the server. The key file is a secret held on the server. The docs page said only that the Agent Platform User role (`roles/aiplatform.user`) is needed for standard keys or ADC. Creating a key file is a security risk. Not simplest.

(c) `gcloud auth print-access-token`: "By default, service account access tokens expire after one hour" and user tokens "automatically expire after one hour" (https://docs.cloud.google.com/docs/authentication/token-types). Unsuitable for a static header.

Simplest method: API key in `x-goog-api-key`. The call shapes below are built from the documented endpoint and header; the body fields are from Google's general generateContent format, not copied from a quoted example. Mark as NOT VERIFIED until tested once.

Image (express mode):
```
POST https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-image:generateContent
x-goog-api-key: <KEY>
Content-Type: application/json
{"contents":[{"role":"user","parts":[{"text":"A red fox, flat illustration"}]}],
 "generationConfig":{"responseModalities":["TEXT","IMAGE"]}}
```
Image data returns in `candidates[0].content.parts[].inlineData.data` (base64).

TTS (standard Vertex form, shown at https://docs.cloud.google.com/text-to-speech/docs/gemini-tts with a Bearer token, project and location in the path):
```
POST https://aiplatform.googleapis.com/v1beta1/projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3.1-flash-tts-preview:generateContent
Authorization: Bearer <token>      (docs example; whether x-goog-api-key works for this path is NOT VERIFIED)
{"contents":{"role":"user","parts":{"text":"..."}},
 "generation_config":{"speech_config":{"language_code":"en-in","voice_config":{"prebuilt_voice_config":{"voice_name":"Kore"}}}}}
```
"In Vertex AI API, the output is PCM 16bit 24k audio data, and doesn't have WAV headers."

## 4. Just enable billing on the AI Studio project (https://aistudio.google.com/docs/billing)

| Item | Finding |
|---|---|
| Minimum prepay | "The minimum purchase is $5. The maximum amount of credits you can prepay for is $5,000." |
| Prepaid vs post-paid | Prepay credits; "unused credits expire after 12 months and are non-refundable"; they apply only to Gemini API. At zero balance "all API keys in all projects linked to that billing account will stop working simultaneously." That is a hard stop. Whether a post-paid option also exists is NOT VERIFIED. |
| Tier | Tier 1 needs "Set up and link an active billing account"; $250 spend cap. Tier 2: "Paid $100 + 3 days"; $2,000 cap. Image models: free tier "Not available", so any paid tier (Tier 1) is required. |
| Image rate limits, Tier 1 | NOT VERIFIED. https://aistudio.google.com/docs/rate-limits gave no per-model numbers; they are shown in the AI Studio console rate-limit page, which is not publicly readable. |
| Spend cap | "Monthly usage caps are enforced for the Gemini API at the billing account level." After the tier limit, "service is paused for all projects linked to that billing account until the start of the next billing cycle." Project-level caps are experimental and overage is possible (about 10 minutes of billing latency). A prepaid balance is itself a cap. Cloud Billing budget alerts: NOT VERIFIED. |

## 5. Click path (non-engineer)

Cheapest route that could use the $300: Vertex express-mode key, only if the credit is still eligible.

1. Open https://console.cloud.google.com signed in as the Gmail account. Menu > Billing > Overview. Note: is it "Free trial", is the $300 shown, and when does it expire? Do not click Activate/Upgrade.
2. Open https://console.cloud.google.com/vertex-ai (Agent Platform) and choose the express-mode "Get API key"/"Sign up" option. If it asks to enable billing, stop and see step 6.
3. Copy the key once into the secrets field in step 5, not into chat.
4. On the Credentials page, restrict the key to the Vertex AI API (aiplatform.googleapis.com).
5. In this environment's settings, add a network secret: host `aiplatform.googleapis.com`, header name `x-goog-api-key`, value = the key.
6. If Vertex refuses calls or says billing/credit is not allowed: fall back to AI Studio. Billing > Gemini API > Prepay, buy $5-$20, keep the existing AI Studio key. No credit is used on this path.
7. Billing > Budgets & alerts: create a budget of a few dollars with email alerts.

Hand to the server: only the injected header on the host `aiplatform.googleapis.com`. The code sends a dummy value or none. The real key stays in network-secrets settings.

## 6. Recommendation

The cheapest reliable route is a $5-$20 AI Studio prepay: it costs a small amount of real money, is a hard stop at zero, and works for both image and TTS with the existing key. It does not use the $300, which Google states cannot be used on AI Studio. The $300 may still pay for Vertex express-mode image calls, but only if the account signed up before 16 Nov 2026 and has not upgraded since. The docs do not say whether express mode is billed against the credit, whether a free-trial account may call image models, or whether TTS works with a key there. Also uncertain: Vertex prices, Tier 1 image rate limits, and the `gemini-nano-banana-2.1` model ID on Vertex. Test with one image call under a small budget alert before depending on it.
