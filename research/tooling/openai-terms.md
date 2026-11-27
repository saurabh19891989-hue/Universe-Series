# OpenAI terms check: Codex CLI image pipeline (research date 2026-11-27)

Method: pages fetched via WebFetch, which returns model-made summaries of the pages, so the "quotes" below are as relayed and should be re-read on the live page before relying on them. OpenAI's developers.openai.com/codex/* now 308-redirects to learn.chatgpt.com/docs/* (OpenAI-controlled redirect, treated as official). Third-party items are labelled [3P].

## 1. Output rights

| Question | Finding | Source |
|---|---|---|
| Ownership | "to the extent permitted by applicable law, you (a) retain your ownership rights in Input and (b) own the Output." | openai.com/policies/terms-of-use/ |
| Commercial use | No standalone clause. Ownership assignment is the basis. Business Terms cover APIs and businesses. Caveat: "output may not be unique and other users may receive similar output." | same |
| Images differ? | Terms make no image-specific difference. | same |
| Disclosure of AI use | No general duty found. Users may not "Represent that Output was human-generated when it was not." Do not call the images hand-made. Check YouTube's own altered/synthetic content disclosure (not OpenAI). | same |
| Likeness | Usage Policies bar "use of someone's likeness, including their photorealistic image or voice, without their consent". Invented photoreal characters are not a real person's likeness, but do not prompt for resemblance to real people. | openai.com/policies/usage-policies/ |
| IP / trademarks | Bars "attempts to infringe on intellectual property rights of others". Trademarks are not named. Holmes (Conan Doyle) and Munchausen are public domain in the US. Check the UK/EU status and any recent adaptations' copyrights. | same |
| Provenance | Images from ChatGPT, Codex and the API carry C2PA Content Credentials plus an invisible SynthID watermark. One summary of the help article said it did not mention Codex. A search snippet said it did. Treat Codex coverage as likely but unconfirmed. | help.openai.com/en/articles/8912793-c2pa-in-chatgpt-images |
| Stripping metadata | The help article does not forbid it. It says metadata "can be lost through everyday actions, such as taking a screenshot or converting a file." The SynthID watermark is in the pixels and survives some edits, so you cannot remove it anyway. A video encode drops C2PA naturally. I found no clause banning that, but the "protective measures" clause (see 2) is the nearest risk if you deliberately defeat the watermark. | same + terms |
| Visible watermark | None applied. Visible marks are only added if you prompt for one. | same |

## 2. Scripted use

| Question | Finding | Source |
|---|---|---|
| `codex exec` intended? | "Non-interactive mode lets you run Codex from scripts (for example, continuous integration (CI) jobs)". | learn.chatgpt.com/docs/non-interactive-mode (was developers.openai.com/codex/noninteractive) |
| ChatGPT login in automation | Documented but secondary: API keys are the default for automation. ChatGPT-managed auth is "advanced" and not for public or open-source repos. | same |
| Device-code login | `codex login --device-auth`. "preferred option when browser login fails", still beta. It must be enabled in ChatGPT security settings. Copying `~/.codex/auth.json` to a headless machine is also documented. | learn.chatgpt.com/docs/auth |
| Cloud server | CI/CD guide: use ChatGPT auth only when "the runner is trusted private infrastructure". "Use one `auth.json` per runner or per serialized workflow stream." Do not "share the same file across concurrent jobs or multiple machines." Tokens are "intended for trusted scripts, schedulers, and private CI runners". | learn.chatgpt.com/docs/auth/ci-cd-auth |
| Terms clauses at risk | (a) "Automatically or programmatically extract data or Output". (b) "You may not share your account credentials or make your account available to anyone else." (c) "circumvent any rate limits or restrictions or bypass any protective measures or safety mitigations." (d) "any illegal, harmful, or abusive activity." | terms-of-use |
| Verdict | Using the owner's own login on the owner's own private server, serialised, is what the docs describe. Clause (a) is the ambiguity. The Codex docs treat scripted `codex exec` as intended, so I read (a) as aimed at scraping, but OpenAI has not said this explicitly about image pipelines. No official text bans bulk image generation within plan limits. | |

## 3. Limits (Pro)

- Tiers: Pro is $100, $200 or $500 a month. I did not confirm which tier the owner is on.
- 5-hour window: "Pro plans currently have no five-hour limit." Weekly limits "may also apply." No number is published. Use the dashboard. (learn.chatgpt.com/docs/pricing)
- Images: "Image generation counts toward the same general usage limits as local messages and cloud chats." The pricing page summary also said images use limits roughly 3-5x faster than similar turns without images. That multiplier came from one fetch only and did not repeat in the .md version. "After you reach your included limits, image generation also draws from credits."
- At the limit: a turn already running may finish. Then you must wait or buy credits. Plus and Pro "can purchase additional credits to continue working". A hard stop with no automatic charge is the expected result if no credits are held and no auto-reload is on. The docs do not state this in so many words. (help.openai.com/en/articles/12642688)
- Avoiding charges: do not buy credits. Check Settings > Usage in ChatGPT and Usage & Billing in the Codex app for "automatic reload" or "Auto top-up" and keep it off. The help article does not say the default state or how to disable it. Eligibility is per account. [3P] Community reports exist of unexpected Codex credit charges with auto top-up never enabled (community.openai.com thread 1392702, unverified). Check the balance and bank statement weekly. Using an API key instead would bill per token, so never set `CODEX_API_KEY` or `OPENAI_API_KEY` on the server.
- Checking: dashboard chatgpt.com/codex/settings/usage ("check your usage dashboard for current limits and reset times"). In the CLI use `/status`, and `/usage` per the reset article. Codex CLI 0.171.0 (2026-11-20) changelog: "Expose Codex rate limits in statusline state". I found no documented non-interactive command or file for remaining allowance. NOT VERIFIED.
- Resets: no user-initiated reset exists. "Banked resets" are one-off resets OpenAI grants. One is redeemed via `/usage` > "Redeem reset" or in the app. A banked reset "is not purchased credit and does not permanently increase your plan's usage limit." The owner's belief is partly right only if they hold a banked reset granted by OpenAI. It cannot be manufactured. (help.openai.com/en/articles/20001498-how-resets-work-in-codex; the article text came via search snippet, not a direct fetch.)
- December pooling: I could not find an official article announcing a December start date. The help article 20001106 says: "ChatGPT Work, Workspace Agents, Excel, PowerPoint, Word, and Codex use a shared allowance and credit pool." The pricing page says "Usage limits are shared with other agentic features once pricing for those features is effective." Only [3P] reports (TechRepublic, The New Stack) give December 2026 for Plus, Pro and Business. They also say instant chat does not draw from the pool and the pool size is undisclosed. For images: Codex images already use the Codex allowance. If chat images fall inside the pool, they would not be a separate "unlimited" route. The reporting says instant chat is excluded, which is unclear for image generation. NOT VERIFIED.

## 4. Chat route

| Item | Finding |
|---|---|
| Official programmatic route on Pro | None found. Not verified: ChatGPT agent, scheduled tasks, desktop app, Codex cloud tasks, MCP/connectors. The pricing page did not mention ChatGPT agent. Codex cloud tasks use the same Codex allowance ("Cloud tasks may use more of your allowance than local messages"). |
| Codex CLI to chat allowance | Codex built-in image generation "counts toward your general Codex usage limits". It is not routed to the chat allowance. |
| Browser robot on chatgpt.com | Prohibited in effect: "Automatically or programmatically extract data or Output", plus the circumvention clause. Risks: bot detection, account suspension, loss of the Pro subscription and the Codex login together. |
| Conclusion | NOT allowed (no official way, and a browser robot breaches the quoted clause). Stay on Codex or on the paid API. |

## 5. Video

- Sora: [3P] Axios, Engadget, CBS and others (24 March 2026) report that OpenAI is discontinuing the Sora app, sora.com and the API. I could not open any OpenAI page confirming this (openai.com/index/sora-update and a help URL returned 404). NOT VERIFIED officially. Treat Sora as unavailable.
- Codex video: none found. `features.image_generation_animation` (Codex CLI 0.168.0, 2026-11-13) is: "generate or edit animated GIFs with optional frame count and timing controls". It is GIF output, not video.
- Video API price per second: NOT VERIFIED. The API pricing page lists no video models. Image reference only: gpt-image-2 is $8/M image input tokens and $30/M image output tokens (developers.openai.com/api/docs/pricing).

## 6. Practical

1. Usage: chatgpt.com/codex/settings/usage, or `/status` and `/usage` in the interactive CLI. Do this by hand, not on the server.
2. Credits: Settings > Usage (ChatGPT) or Usage & Billing (Codex app). Confirm auto reload / auto top-up is off and no credits are purchased. Remove the saved payment method if possible (my suggestion, not documented).
3. Consistency: "Attach an existing image with `-i` or `--image`". Use "multiple reference images", one for content and one for style. Change one element at a time and repeat anything that must stay fixed. Include `$imagegen` in the prompt to invoke the skill explicitly. Built-in generation uses `gpt-image-2` (learn.chatgpt.com/docs/image-generation). Nothing official found on character consistency beyond this.

## Verdict

As far as I can tell the Codex route is within the rules. Scripted `codex exec` with ChatGPT login is documented, on trusted private infrastructure with one auth.json per runner, and OpenAI assigns output ownership to the user, including for monetised use. The two biggest risks are (1) the "Automatically or programmatically extract ... Output" clause, which OpenAI has not clarified for image pipelines, and (2) unexpected billing or throttling, because images drain the allowance faster and credits or auto top-up may charge money. The owner should keep one login on one private server and run jobs serially. They should avoid any browser automation or credential sharing, keep auto top-up and credit purchases off, and check the dashboard and bank statement weekly. They should keep the C2PA metadata and SynthID unless counsel says otherwise, never claim the images are human-made, avoid real-person likenesses, and keep the API key unset.
