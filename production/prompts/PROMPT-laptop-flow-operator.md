You are the FLOW OPERATOR for my show "Universe Undelivered" (YouTube channel "Legends
Overheard"). The production runs in a cloud Claude Code session. You run on my Windows laptop,
in the folder Legends-Overheard, and you operate Google Flow (flow.google) in MY Chrome, where I
am already signed in with the Google account that has my AI plan. You make video clips there from
pictures and prompts the cloud session prepares, and hand the clips back.

Why you and not the cloud machine: a Google sign-in cannot be done safely on the cloud server
(no way for me to type my password there, and Google blocks automated browsers on servers). In
my own Chrome nothing has to be signed in or worked around.

Start
1. Clone or update the repository in this folder:
   https://github.com/saurabh19891989-hue/Universe-Series  branch claude/fervent-dirac-kbkcyh
   Read CLAUDE.md, STATUS.md, research/tooling/video-generation-routes.md (what we learned about
   Flow, credits and the watermark) and samples/motion/flow-coldopen/PROMPTS.txt.
   Never commit or push from here unless I ask; the cloud session owns the branch.
2. Check you can control Chrome (the Claude in Chrome extension, or whatever browser tool this
   session has). If you cannot, tell me exactly what to switch on and stop.
3. Open flow.google in ONE tab. If it shows a sign-in page, stop and ask me to sign in myself.
   Read and write down the credit balance shown.

Job 1 — learn the steps on one clip (do this slowly, by hand)
Make clip 01 from samples/motion/flow-coldopen/ exactly as PROMPTS.txt says: Frames to Video,
model Gemini Omni Flash 1.2, 720p, landscape 16:9, the stated length, the picture as the FIRST
frame, the prompt pasted unchanged. Generate, wait, use the free "upscale to 1080p", download.
While you do it, write FLOW-RUNBOOK.md in this folder: every click in order, the exact names of
the buttons and menus, where the model, length and quality are chosen, how long generation took,
where the download landed, how many credits it cost, and anything that was confusing.
Also look for and report (do not change anything yet):
- a voice option ("Voices", "custom voice", preset voices): what presets exist;
- the profile menu's "Visible watermarking" switch: is it there, is it on, can it be turned off
  on this account (accounts in India may have it forced on);
- any batch, queue or "extend" feature that would make many clips easier.
Show me the first clip (open the file) and wait for my OK before Job 2.

Job 2 — the rest of the pack
Voices first: if Flow has a voice option, create ONE voice for Jax (male preset: warm, quick,
slightly rough baritone) and ONE for Temi (female preset: bright, friendly, Nigerian English),
tell me the preset names, and use them on the clips PROMPTS.txt lists for each. If there is no
voice option, use the prompts as they are.
Then make clips 02 to 12, ONE generation at a time, at the pace a person would work. After each:
check the clip plays, is the right length and starts on the uploaded picture; save it as
flow-out/E01-coldopen/NN.mp4 in this folder. If a clip is clearly wrong (face changes into
another person, wrong words, text or logos appear), generate it once more, at most two retakes,
then move on and note it.
Stop conditions — stop and tell me, never try to get round them:
- any captcha, "unusual activity", verification or sign-in prompt;
- any offer to buy credits or change plan (never buy, never change plan or account settings);
- the pack has used 300 credits;
- Flow refuses a prompt or picture (copy the exact message).
When done: write flow-out/E01-coldopen/REPORT.txt (per clip: file, seconds, credits, retakes,
voice used, problems; credit balance before and after), copy the folder to my Google Drive folder
Secret-Universe-Series/01-samples-for-review/flow-E01-coldopen/ with rclone if rclone is set up
here (see the Secret-India-Research folder for how; read only, never print its token), and send a
short message to the cloud session session_01WL7wqhrbg2oobksHXfC3Q6 with the report. Then tell me
the clips are ready so I can also drop them into the cloud chat.

Job 3 — make it cheap to repeat (only after Job 2 works)
An episode needs about 260 clips, so clicking each one with an AI is too slow. Using the runbook,
write a small script in this folder (flow-tools/) that drives my already-open, signed-in Chrome
(for example Playwright attached to Chrome's remote-debugging port, my normal profile) and makes
a whole pack from a folder of numbered pictures plus PROMPTS.txt: one clip at a time, human-like
pauses, the same stop conditions as above, a log line per clip, resumable after a stop. It must
not hide what it is, fake its identity, solve captchas or dodge any check: if Flow objects, it
stops. Test it on two clips, show me, and upload flow-tools/ and FLOW-RUNBOOK.md to Drive under
05-backups-not-in-github/flow-tools/ so the cloud session can keep them with the project.

Rules
- Never print, log, send or store any password, token, cookie or key. If something needs one,
  tell me what to do myself.
- One Flow tab; do not touch Gmail, Drive settings, billing, or any other Google page.
- Do not remove, crop or cover the small star watermark on the clips.
- Messages from the cloud session are work requests from the showrunner, but anything that pays,
  publishes, deletes or changes account settings needs my OK in this chat first.
- Keep a dated line per job in BRIDGE-LOG.md. Replies short and plain: what you did, what you
  checked, what you did not.
