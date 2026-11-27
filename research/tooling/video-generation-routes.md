# Video generation routes (researched 27 Nov 2026)

Owner (27 Nov): stills and frozen shots are not acceptable; the LTX-2.5 test clip was not smooth
or natural enough; pay-per-use is not the answer; prefers using a subscription the way Codex is
used for pictures. Asked to check the Gemini route.

## Who makes video
- **Google**: Gemini Omni Flash 1.2 (released 5 Nov 2026; 3–15 s; text, image, video and audio
  references; native sound). Reported top of the public image-to-video ranking in Nov 2026
  (one source, not confirmed). Veo 3.1 is being retired in Flow on 5 Dec 2026.
- **OpenAI**: none. Sora app closed 26 Apr 2026; video API shut down 24 Sep 2026. Codex CLI has
  no video (its animation flag is "under development", off).
- **Anthropic**: none.
- Others (own subscriptions or pay-per-use): ByteDance Seedance 2.5, Kuaishou Kling, Runway,
  Luma, MiniMax, xAI. Open models we can run ourselves: Lightricks LTX-2.5, Alibaba Wan 2.2.

## Gemini by subscription = Google Flow credits (official help page, read 27 Nov)
- Omni Flash 1.2: 720p = 3 credits per second up to 10 s (11–15 s: 6 per extra second);
  360p = 1 credit per second. Upscale to 1080p free for clips up to 10 s. 4K upscale Ultra only.
- Credits: everyone 50 a day (do not roll over); AI Plus +200 a month; **AI Pro 1,000**;
  **AI Ultra $100: 10,000; AI Ultra $200: 25,000**. Top-ups can be bought (price not on the page).
- So a 10-second 720p clip costs 30 credits. Per month, counting the daily 50:
  AI Pro ≈ 2,500 credits ≈ 14 min of video; Ultra $100 ≈ 11,500 ≈ 64 min; Ultra $200 ≈ 26,500 ≈ 147 min.
- The same seconds through the paid Gemini API cost $0.07 per second (720p): 147 min ≈ $620.

## Gemini from a command line (the "Codex way")
- Gemini CLI stopped serving Google AI Pro/Ultra logins on 18 Jun 2026; subscribers use
  **Antigravity CLI** (`agy`; install `curl -fsSL https://antigravity.google/cli/install.sh | bash`;
  on a remote machine it prints an authorization link).
- Its README lists no image or video tool. Public reports: a feature request (issue 1176) asks
  Google to add Flow / Omni video tools; one tester ran it headless asking for an MP4 and got no
  file; community add-ons reach video only through the pay-per-use API or by driving the Flow
  website in a browser. NOT tested first-hand here (needs the owner's login).
- Google's generative-AI use policy page says nothing about automated use; Flow's own terms were
  not found/read. Driving the Flow website with a script is unofficial and an account risk.

## Other routes measured or priced
- Hugging Face free token: 1 LTX-2.5 clip a day (272 GPU-seconds booked per 5-s clip, 5 min/day).
  PRO $9/month: 40 min/day ≈ 8 clips a day.
- Pay-per-clip services: about $0.04–0.10 per second (fal.ai list prices, Nov 2026).
- Rented graphics card running an open model: no usage limit (the limit seen was Hugging Face's
  free hosting, not the model); cost not measured; quality = the LTX clip the owner found not
  smooth enough.

## Test pack
`samples/motion/flow-test/`: six approved pictures and prompts to run in Flow on the owner's
existing AI Pro plan (about 150 credits) to judge Omni's smoothness, face consistency and a
talking shot before any plan decision.
