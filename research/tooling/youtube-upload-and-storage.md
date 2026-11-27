# YouTube upload, policies, and Drive transfer

All items "checked 2026-11-27" at the URL given. "NOT VERIFIED" means I could not read it on an official page.

---

## a) Uploading with the YouTube Data API v3

### CRITICAL: the "unverified project = private" lock

**Finding: the lock was removed on 2 November 2026 (25 days before this check).** Official revision history, https://developers.google.com/youtube/v3/revision_history (read from the raw page, checked 2026-11-27):

> "November 2, 2026: Videos uploaded through the videos.insert method from unverified API projects are no longer restricted to private viewing mode. This change reverses the policy announced on July 28, 2020, which restricted videos uploaded from unverified API projects created after that date to private viewing mode until the project completed an audit. If you don't specify a value for the status.privacyStatus property in a videos.insert request, the uploaded video's privacy status defaults to public. Certain uploads might default to private based on creator account settings, as explained in the YouTube Help Center."

The old rule it reverses (same page, entry dated July 28, 2020):

> "All videos uploaded using the videos.insert endpoint from unverified API projects created after 28 July 2020 will be restricted to private viewing mode. To lift this restriction, each project must undergo an audit to verify compliance with the Terms of Service. Creators who use an unverified API client to upload video will receive an email explaining that their video is locked as private, and that they can avoid the restriction by using an official or audited client."

Caveats:
- The `videos.insert` reference page (https://developers.google.com/youtube/v3/docs/videos/insert) now says "Videos uploaded from unverified API projects are not restricted to private viewing mode" (summarised by the fetch tool, not a verbatim read). Some mirrors and search snippets still show the old rule, so trust the dated revision-history entry.
- Set `status.privacyStatus` explicitly. Upload as `private` first, check, then flip to public. Account settings can still force private (the 13-17 default is private; adults default to public per https://support.google.com/youtube/answer/57407).
- Audit mechanics (form, duration, whether a locked old video can be switched to public in Studio): **NOT VERIFIED.** The old audit form URL I tried (`/guidelines/audit_form`) returned 404. Third-party blogs claim locked videos could not be unlocked by the owner and had to be re-uploaded; that is unverified and now largely moot. If a video does arrive locked, the practical fallback is re-uploading it. A compliance audit is still required for quota above default (revision history, 1 July 2021 entry) via the Quota Extension Form, https://support.google.com/youtube/contact/yt_api_form.

### Requirements and quotas

| Item | Fact | Source |
|---|---|---|
| Setup | Google Cloud project with YouTube Data API v3 enabled; OAuth consent screen; OAuth client (Desktop app type is simplest for a headless server using a one-off authorisation); refresh token | https://developers.google.com/identity/protocols/oauth2 |
| Scope | `https://www.googleapis.com/auth/youtube.upload` is enough for `videos.insert`. Also accepted: `youtube`, `youtubepartner`, `youtube.force-ssl` | https://developers.google.com/youtube/v3/docs/videos/insert |
| Refresh-token trap | External consent screen in **Testing** status issues refresh tokens that expire in 7 days; publish the app to production ("In production") for a durable token. Limit 100 refresh tokens per account per client ID | https://developers.google.com/identity/protocols/oauth2 |
| Default daily quota | 100 `videos.insert` calls/day (own bucket since 2026-06-01), 100 `search.list`, and 10,000 units/day for everything else. Resets midnight Pacific | https://developers.google.com/youtube/v3/determine_quota_cost |
| Quota cost | `videos.insert`: 1 unit per call from its own bucket (limit 100/day); `thumbnails.set` 50; `captions.insert` 400; `playlistItems.insert` 50 (general 10,000 pool) | same |
| History | 4 Dec 2025: upload cost cut from about 1,600 to about 100 units; 1 Jun 2026: separate `videos.insert` bucket | https://developers.google.com/youtube/v3/revision_history |
| Max file | 256 GB or 12 hours, whichever is less (Help); API reference also says 256 GB | https://support.google.com/youtube/answer/71673 ; insert page |
| Resumable upload | Send POST to `https://www.googleapis.com/upload/youtube/v3/videos` with `uploadType=resumable`; metadata first (headers `X-Upload-Content-Length`, `X-Upload-Content-Type`), then PUT the bytes; resume by querying the upload URL. Chunked upload is "rarely necessary and ... discouraged"; chunk size must be a multiple of 256 KB if used. A 1-3 GB file is fine with a single resumable PUT and retry | https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol |
| Thumbnails | `thumbnails.set`. Needs a phone-verified channel ("Add custom thumbnails" is listed as a verification benefit) | https://support.google.com/youtube/answer/171664 |
| Captions | `captions.insert`, 400 units | quota page |
| Playlists | `playlistItems.insert`, 50 units | quota page |
| AI disclosure flag | `status.containsSyntheticMedia` is settable on `videos.update`; `status.selfDeclaredMadeForKids` likewise | https://developers.google.com/youtube/v3/docs/videos/update |
| Title/description | Title max 100 chars; description max 5,000 | https://support.google.com/youtube/answer/57407 |
| Localised titles | `localizations` part of `videos.update` | update page |
| Audio-language tracks (multi-audio) via API | NOT VERIFIED (not found in the pages read) | n/a |

### Verification and upload limits

- Verification: "To verify your channel, you'll be asked to enter a phone number... Once you've verified your account, you can: Upload videos longer than 15 minutes. Add custom thumbnails. Live stream. Appeal copyright claims." Without it: "By default, you can upload videos that are up to 15 minutes long." So a 30-40 minute episode **requires a phone-verified channel**. https://support.google.com/youtube/answer/171664 and https://support.google.com/youtube/answer/71673
- Daily upload cap: "There's a limit to how many videos a channel can upload each day across desktop, mobile, and YouTube API... Limits may vary by country/region or channel history." No number is published. https://support.google.com/youtube/answer/57407 . New-channel specific limit: NOT VERIFIED; 1-2 uploads/day is unlikely to hit it.

---

## b) Policies that matter

| Topic | Official text (quoted) | Applies to this show | Source |
|---|---|---|---|
| Inauthentic / mass-produced content | Renamed 15 July 2025 from "repetitious content": "includes content that is repetitive or mass-produced." Also: "Not be mass-produced, generic, repetitive, or manipulative. It should be made for the enjoyment or education of viewers." "Generic or repetitive content includes content that looks like it's made with a template, or that may feel repetitive to viewers after watching several videos in a row from the same channel." | Risk: ten near-identical AI-voiced episodes released fast. Mitigate with distinct scripts, original art and score, and human editing | https://support.google.com/youtube/answer/1311392 |
| Synthetic-content disclosure | Must disclose GenAI content that: "Makes a real person appear to say or do something they didn't do. Alters footage of a real event or place. Generates a realistic scene that didn't actually occur. Creates music that's the main focus of the video." Need not disclose: "non-realistic content that's made with AI" with examples including "Using an AI-generated or altered animation ... in a fully animated video" and "Production assistance" (scripts, thumbnails) and "voice or audio repair" | Clearly illustrated characters and AI voices on clearly fictional characters: no label needed. **Caution:** original characters composited over real NASA footage could be read as "alters footage of a real event or place" if the footage looks like documentary and is altered. When in doubt, tick the label; it costs little. Real astronaut voices must not be synthesised | https://support.google.com/youtube/answer/14328491 |
| Made for kids | Child-directed if it "features actors, characters, activities, games, songs, stories, or other subject matter that reflect an intent to target children". Factors include "characters ... that appeal to children, including animated characters or cartoon figures". Listed as not necessarily kids: "Animated content that appeals to everyone"; mature themes are not made for kids | An animated space series for teens/adults should be set "No, not made for kids"; a kids setting disables comments, personalised ads and some features. Self-declaration is set per video (`selfDeclaredMadeForKids`) | https://support.google.com/youtube/answer/9528076 |
| NASA footage | NASA content "may be used without needing explicit permission... NASA content used in a factual manner that does not imply endorsement". "NASA should be acknowledged as the source". Commercial use must not "explicitly or implicitly convey NASA's endorsement". Identifiable persons: using media for commercial purposes "may infringe that person's" rights. Some images are third-party copyrighted and marked | Credit NASA in the description and on screen; do not use NASA logos/"meatball" as branding; avoid clear identifiable astronaut faces in commercial context unless cleared; check each asset for third-party credit | https://www.nasa.gov/nasa-brand-center/images-and-media/ |
| ESA/Hubble | "released under the Creative Commons Attribution 4.0 International license ... provided they are clearly and visibly credited." Credit "must be presented in a clear and readable manner ... with the wording unaltered (for example: 'ESA/Hubble')". "The credit should not be hidden." May not be used to imply endorsement | Put "Credit: ESA/Hubble" (plus exact per-image credit line) in the description and end card | https://esahubble.org/copyright/ |
| YouTube Partner Program thresholds | Either "1,000 subscribers with 4,000 qualified watch hours in the last 12 months" or "1,000 subscribers with 10 million qualified Shorts views in the last 90 days". Private, unlisted and Shorts-feed watch hours don't count toward the 4,000. The page text I read lists only these two routes; lower early-access tiers were not shown, so NOT VERIFIED here | | https://support.google.com/youtube/answer/72851 |

---

## c) Large files from a headless Linux server to Google Drive

| Method | Facts | Verdict | Source |
|---|---|---|---|
| rclone + own OAuth client + `drive.file` scope | Scope `drive.file`: "rclone can read/view/modify only those files and folders it creates"; files appear in the web UI. rclone's shared client_id "is being retired and will stop working during 2026, so creating your own is now strongly recommended." Headless setup: on the server run `rclone config`, answer **n** to the browser question, then run `rclone authorize "drive"` on the owner's own laptop (with a browser) and paste the resulting token into the server's terminal. | **Recommended.** Narrowest practical access; token never enters a chat window | https://rclone.org/drive/ ; https://rclone.org/remote_setup/ |
| Service account | rclone supports it for unattended use (service_account_file). Storage-quota behaviour on personal Drive (service accounts have no quota there; need a Shared Drive or domain delegation) is **NOT VERIFIED** on this pass. Uses a JSON key file, which is a secret to guard | Use only if the owner has Workspace and a Shared Drive | https://rclone.org/drive/ |
| Drive API resumable upload | Direct, but you write and maintain the code; rclone already does this | Not needed | https://developers.google.com/workspace/drive/api/guides/limits |
| Claude Google Drive connector | `create_file` accepts `textContent` or `base64Content` inside the tool call, so the file bytes would pass through the model context; a multi-GB video is **not** feasible. It is fine for text, notes, thumbnails and small assets | Use for documents only | tool schema in this session |

**Limits:** "Google Workspace users can only upload 750 GB per day between My Drive and all shared drives... The maximum file size that users can upload is 5 TB." (https://developers.google.com/workspace/drive/api/guides/limits). rclone calls it an undocumented 750 GiB/day for ordinary accounts and offers `--drive-stop-on-upload-limit`. At 1-3 GB per episode this is irrelevant.

### Recommended simplest safe method
1. Owner creates their own Google Cloud OAuth client (Desktop type) and sets the consent screen to production.
2. On the server: `rclone config`, create remote `gdrive`, `client_id`/`client_secret` entered by the owner in the terminal, scope `drive.file`, answer "n" to auto-browser.
3. On the owner's laptop: `rclone authorize "drive" "<client_id>" "<client_secret>"`; paste the printed token into the server prompt (never into chat).
4. Upload: `rclone copy episode01.mp4 gdrive:Universe-Series/ --drive-chunk-size 128M --progress`.
5. Rotate by revoking the app at https://myaccount.google.com/permissions if the server is ever compromised. The same pattern (owner pastes once into the server shell, token stored in `~/.config/rclone/rclone.conf`, chmod 600) applies to YouTube's refresh token; keep both out of git.

Because `drive.file` only sees files rclone created, it cannot read the rest of the owner's Drive.
