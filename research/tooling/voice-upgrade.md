# Voice upgrade: expressive open TTS on our CPU (bake-off, 28 Nov 2026)

**Nobody has listened to any of this audio. Agents cannot hear.** Every statement below about
"acting" is either what a model's controls claim to do or what rough numbers show (pitch movement,
loudness movement, voiced fraction, speed, word accuracy, speaker similarity). The owner's ear decides.
Licence notes are a careful reading, not legal advice.

Reel: `samples/voices/bakeoff-28nov/` (3 MP3 parts, 2.1 / 1.7 / 2.5 MB; `ORDER.txt` says what plays when;
`casting-clips/`; raw numbers in `numbers/`). Scripts: `production/tools/voice/bakeoff_*.py`,
`qwen_design_casting.py`, test lines `bakeoff_lines.json`. Venvs, models and per-take WAVs live in the
scratchpad (`voice2/`), not in git.

Machine: 4 cores (Xeon with AVX-512/AMX-bf16), 15 GB RAM, no GPU. During the first runs another agent's
4-process video render was on the box (load 7-8); later runs saw load 3-4. Thread counts are given per number.

## 1. Short answer
- **Best fit found: Chatterbox-Turbo (MIT code and weights), each character pinned to one fixed ~10 s
  reference clip.** It is the only licence-clean engine tested that has real acting controls (inline
  `[laugh] [chuckle] [sigh] [gasp] [whispering] [angry] [sarcastic] [happy] [surprised] [fear] [dramatic] [crying]`...)
  AND keeps one voice per character across lines, at a speed that fits an episode:
  **2.05 s of compute per second of audio with 4 threads on a quiet machine, 4.1 s with 2 threads while
  video was rendering.** About **1.2 h per full pass of a 35-min episode** (≈2,100 s of dialogue) on the
  whole machine, ~2.4 h if it shares the box with a render.
- **Where the reference voice comes from (owner's ear decides):**
  (a) our current Kokoro voices (keeps today's cast; the Turbo takes stay close to the Kokoro voice,
  similarity 0.78-0.91), or (b) new voices **designed from a written description with Qwen3-TTS
  VoiceDesign (Apache-2.0)**, rendered once as a casting clip, which gives us accents Kokoro does not have
  (Bengali-English Mira, Nigerian-English Temi intended; not verified by ear).
- **Kokoro stays** for bit parts, crowd lines and anything flat, and as the fallback (0.27 s per second).
- Not recommended: Qwen VoiceDesign line-by-line (voice changes from line to line), Orpheus (too slow:
  14-20 s per second, and runs long), Supertonic (fast, but its weights licence requires a
  "machine-generated" disclaimer on published content, which clashes with the owner's rule).

## 2. Research pass (what exists, Nov 2026)
Sources: model cards and READMEs where reachable, plus comparison pages ([BentoML](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models),
[yaps.ai licence round-up](https://www.yaps.ai/blog/best-local-tts-models), [OpenSpeech](https://www.openspeech.dev/),
[quantised CPU TTS notes](https://ocdevel.com/blog/20260711-quantized-cpu-tts)). Third-party claims are marked.

| Model | Code / weights licence | Size | Acting controls | CPU practicality here | Verdict |
|---|---|---|---|---|---|
| **Chatterbox-Turbo** (Resemble AI) | MIT / MIT ([GitHub](https://github.com/resemble-ai/chatterbox), [HF](https://huggingface.co/ResembleAI/chatterbox-turbo)). Every output carries Resemble's inaudible Perth watermark. Third-party report: Resemble retired Chatterbox commercially Aug 2026, repo kept as archive (not verified) | 350M | 19 inline tags incl. laugh, chuckle, sigh, gasp, whispering, angry, sarcastic, fear, crying; zero-shot voice from a reference clip | **Tested: RTF 2.05 (4 thr), 4.1 (2 thr)**, 6.3 GB RSS | **Use for leads** |
| Chatterbox (original 0.5B) | MIT / MIT | 500M | exaggeration + cfg knobs, no tags | 27 Nov probe: RTF ~90 (py3.13, fp32 patches, load 8-9). Not retested | maybe retest; Turbo is the one with tags |
| Chatterbox Nano | MIT (card) | 110M | Turbo-style, English | vendor: 3x real time on 8 CPU threads. HF repo is gated (needs a logged-in click-through); community ONNX/GGUF copies exist | **next test** (could be 5-10x faster) |
| **Qwen3-TTS** (Alibaba) | Apache-2.0 / Apache-2.0 ([GitHub](https://github.com/QwenLM/Qwen3-TTS), [HF](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)) | 0.6B, 1.7B | VoiceDesign: voice from a text description; CustomVoice: 9 presets + style instruction in words; Base: cloning | **Tested 1.7B VoiceDesign bf16: RTF 6.6 (2 thr)**; 0.6B CustomVoice probe: RTF 13-23 (3 thr, load 8). Community C/int8 runtime claims RTF ~3 on 4 vCPU (not tried) | **use for casting clips only** |
| Supertonic 3 (Supertone) | MIT code / **OpenRAIL-M weights** ([HF](https://huggingface.co/Supertone/supertonic-3)): Attachment A(e) bars publishing output "without expressly and intelligibly disclaiming that the content is machine generated" | ~99M | 10 presets, `<laugh> <breath> <sigh>`, speed | **Tested: RTF 0.82 (2 thr, load 8)** | **not cleared** (disclaimer clause vs owner's no-AI-wording rule) |
| Orpheus 3B (Canopy Labs) | Apache-2.0 card, but a Llama 3.2 3B fine-tune, so the Llama 3.2 Community Licence also applies ("Built with Llama" attribution, Meta use policy) | 3B (Q4_K_M GGUF 2 GB) | 8 US stock voices, `<laugh> <chuckle> <sigh> <gasp> <groan> <yawn>`... | **Tested: RTF 14-20 (3 thr), 22-39 (2 thr)**; needed a context-size patch (default ran out of RAM) | too slow; licence not settled |
| Kokoro-82M | Apache-2.0 | 82M | speed only | RTF 0.27 | keep for bit parts |
| Kyutai Pocket TTS | CC-BY 4.0 (+ prohibited-use terms) | 100M | none | real time on CPU (27 Nov test) | no acting controls |
| MOSS-TTS Nano (OpenMOSS) | Apache-2.0 reported (upstream LICENSE not seen) | 100M | cloning; expressiveness unknown | third-party: RTF 0.23 on CPU | next test, unverified |
| Dia / Dia2 (Nari Labs) | Apache-2.0 | 1.6B / 1-2B | `(laughs) (sighs)`, two-speaker dialogue | GPU-oriented; CPU "planned". Not run (Orpheus 3B already 15-20x slower than real time here) | skip for now |
| Zonos v0.1 | Apache-2.0 | 1.6B | emotion sliders, rate, pitch | 6 GB+ VRAM class; not run | skip |
| Sesame CSM-1B | Apache-2.0 (needs gated Llama tokenizer) | 1B | conversational context | GPU-oriented; not run | skip |
| Parler-TTS | Apache-2.0 | 880M | voice and style from a description | not run | possible alt. to Qwen for design |
| CosyVoice 3 | Apache-2.0 | 0.5B | instruction control | not run | possible later |
| VibeVoice (Microsoft) | MIT, but Microsoft pulled the long-form code (Sep 2025), research framing | 1.5B | 4-speaker long form | not run | not settled |
| IndexTTS-2 / 2.5 (bilibili) | bilibili model licence with commercial conditions | 0.8-1B | best-in-class emotion vectors | not run | not settled / no |
| Higgs Audio v2 / Higgs TTS 2 | weights research + non-commercial | 3B | very expressive | — | **no** |
| F5-TTS, Fish S2 Pro, XTTS-v2, Spark-TTS, OmniVoice, ChatTTS | non-commercial weights | — | — | — | **no** |
| Bark (Suno) | MIT | 1.5B | laughs, sighs, music | slow, old (2023) | skip |

Performance-on-top tools (not tested this pass): **Chatterbox VC** (MIT, same package) converts a spoken
guide performance into a target voice. That would allow a human "guide read" for the hardest lines; only
with the performer's consent, and the output voice must be our designed or stock voice, never a real
person's. Seed-VC (GPL-3 code, weights licence not settled), RVC (MIT code, training data of base models
not settled), OpenVoice v2 (MIT, timbre only, no prosody). Quantised builds: the community Qwen3-TTS
C runtime (int8) and Chatterbox Nano ONNX/GGUF are the two that could matter; Orpheus Q4 GGUF was
tested and is still too slow.

## 3. Bake-off
**Test script** (`bakeoff_lines.json`, E01 script-v3): L1 Jax fast panic ("Temi! Hi! I'm about to make a
payment—"), L2 Pip deadpan ("She is in Lagos. You are arguing with the past."), L3 Mira put-down ("Your
record isn't late, Captain. It's blank."), L4 Jax shout ("Go! I'll get the ramp!"), L5 Mira whisper ("It
prefers her."), L6 Jax laugh ("Read it to me. Slowly. I want to enjoy my name."), L7 Jax warm ("You gave
up your job for us."), L8 Temi call-centre greeting. Two takes of L1, L4, L5, L6. Each line has a written
direction; each engine got it in its own controls (exact text per take in `numbers/timings-*.json`).

**Engines in the reel:** Kokoro (current production stem) · Supertonic 3 · Qwen3 VoiceDesign (description +
note per line) · Chatterbox-Turbo with Kokoro-stem references · Chatterbox-Turbo with Qwen-designed
references · Orpheus 3B Q4.

### Speed and memory
| Engine | Threads | Load avg | Compute s per audio s (wall) | CPU-s per audio s | Peak RAM |
|---|---|---|---|---|---|
| Kokoro (27 Nov) | 4 | 6-9 | 0.27 | — | <1 GB |
| Supertonic 3 | 2 | 7-8 | 0.82 | 1.6 | 0.5 GB |
| Chatterbox-Turbo, Kokoro refs | 2 | 3-4 | 4.12 | 7.8 | 6.3 GB |
| Chatterbox-Turbo, designed refs | 2 | 3-5 | 4.61 | 8.1 | 6.3 GB |
| Chatterbox-Turbo (one line, twice) | 4 | 1-2 | **2.05** | — | 6.3 GB |
| Qwen3 1.7B VoiceDesign (bf16) | 2 | 3-4 | 6.64 | 12.6 | 5.4 GB |
| Qwen3 0.6B CustomVoice (speed probe) | 3 | 8 | 13-23 | — | 3.1 GB (bf16) / 5.8 GB (fp32) |
| Orpheus 3B Q4_K_M | 3 (L1-L2 at 2) | 3-5 | 19.7 overall (14.2 best) | 49 | 4.3 GB |

### Numbers per engine (means over all takes)
Kokoro row = the 8 production stems. "within-sim" = speaker-embedding cosine similarity between a
character's takes (Chatterbox's GE2E speaker encoder; same person usually > ~0.75). "char separation" =
1 − mean similarity to other characters (higher = characters more distinct).

| Engine | Takes | Mean WER | Pitch range (semitones) | Pitch movement (st. dev.) | Loudness movement (dB s.d.) | Voiced fraction | Words/s | Jax within-sim | Mira within-sim | Char separation | Clipped samples |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kokoro | 8 | 0.031 | 11.2 | 3.5 | 8.0 | 0.72 | 4.02 | 0.82 | 0.76 | 0.46 | 0 |
| Supertonic 3 | 12 | 0.151 | 13.1 | 4.9 | 8.9 | 0.50 | 3.07 | 0.83 | 0.88 | 0.41 | 0 |
| Qwen3 VoiceDesign | 12 | 0.092 | 10.4 | 3.3 | 8.8 | 0.60 | 2.84 | **0.64** | **0.62** | 0.40 | 0 |
| Chatterbox, Kokoro refs | 12 | 0.065 | 19.6 | 5.8 | 8.3 | 0.57 | 3.06 | 0.84 | 0.81 | 0.44 | 0 |
| Chatterbox, designed refs | 12 | **0.049** | **23.5** | **8.8** | 8.9 | 0.58 | 2.98 | 0.84 | 0.84 | 0.41 | 0 |
| Orpheus 3B Q4 | 11 | 0.049 | 16.4 | 5.5 | 9.0 | 0.54 | **1.95** | 0.78 | 0.81 | 0.32 | 0 |

What the numbers show (and do not):
- **Pitch movement:** both Chatterbox variants move pitch 1.7-2.5x more than Kokoro on the same lines.
  That fits "more intonation", but pitch tracking also jumps on laughs, breaths and rough voice, so it is
  not proof of better acting. Qwen per-line design moves pitch no more than Kokoro.
- **Consistency:** Qwen VoiceDesign re-invents the voice every line (Jax 95-348 Hz median across lines,
  takes only 0.51-0.85 similar to its own casting clip). Rendering one designed clip and cloning it with
  Chatterbox fixes that: 0.78-0.91 similar to the designed clip, within-character 0.84. Chatterbox with
  Kokoro refs stays 0.78-0.91 similar to the Kokoro voice.
- **Speed of delivery:** no candidate spoke the panic line faster than Kokoro (Kokoro 4.7 words/s;
  Chatterbox 2.2-3.4; Qwen 2.7-3.4). Turbo has no speed knob; fast lines will need a post time-stretch
  (rubberband/atempo) or punctuation tricks. Orpheus is slow and runs long (9.1 s for the 2-second L1,
  9.3 s for L6: extra sounds or silence; up to 1 s of lead/trail).
- **Whisper (L5):** a real whisper is mostly unvoiced. No take dropped below 0.45 voiced fraction
  (Kokoro 0.77, Chatterbox `[whispering]` 0.48-0.86). So the numbers do not show a true whisper from any
  engine; maybe a breathy, quiet read. Ear check needed. Loudness is normalised in the reel.
- **Shout (L4):** Chatterbox shout takes are not brighter than Kokoro (spectral centroid 860-1070 Hz vs
  1380), which is unlike real shouting. Qwen's shout takes are brighter and higher (≈1940 Hz, 236-320 Hz
  pitch) but in a different voice. Ear check needed.
- **Laugh (L6):** Chatterbox takes are 1.4-2.1 s longer than Kokoro's 2.6 s with the same words (Whisper
  hears no extra words), consistent with an inserted chuckle/laugh or pauses. Supertonic's `<laugh>`
  adds ~0.4 s. Ear check needed.
- **Word accuracy (faster-whisper small int8, per line, same normalisation as `wer.py`):** most errors are
  the name **"Temi"** (Kokoro "Tell me", Chatterbox "Tammy/Timmy", Qwen "Temmie/To me", Orpheus "Teni") and
  "She is"→"She's". Supertonic read tags aloud ("It prefers her sigh"; `<breath>` → "Hmm") and turned the
  capitalised "GO!" into "Joe". Qwen once said "He prefers her" and "She's unlike us" for "She is in Lagos".
  We need a pronunciation respelling for character names whatever engine we pick.
- No clipping anywhere. Peaks ≤ −2 dBFS.
- Pip's Kokoro stems carry the baked-in small-speaker band-limit, so the Chatterbox Pip clone inherits it.

## 4. Recommendation
**Engine mix**
- Leads and anyone with an acting beat (Jax, Mira, Pip, Lucía, Baron, Temi, the guest of the week):
  **Chatterbox-Turbo**, one fixed reference per character, tags written by the writer.
- Bit parts, announcements, crowd, flat procedural lines: **Kokoro** as today.
- **Qwen3-TTS VoiceDesign** only to *make* new casting clips from a description (one-off, ~1-2 min each).
- Owner choice for the reference: keep the Kokoro voices (continuity with what exists) or switch leads
  to designed voices (accents). Both are in the reel and in `casting-clips/`.

**Cost of a 35-min episode (~700 lines, ≈2,100 s of dialogue; E01 was 531 lines / 1,596 s)**
- One Chatterbox pass, whole machine (4 threads, one process): 2,100 × 2.05 ≈ **72 min**.
  Sharing the machine with a render (2 threads): 2,100 × 4.1 ≈ **2.4 h**.
- Realistic plan: 2 takes for the ~40 % of lines with an acting note, 1 take for the rest → ×1.4 →
  **≈1.7 h quiet machine / ≈3.4 h shared**, plus ~10 min of automatic checks (Whisper + numbers). Kokoro
  lines are negligible. RAM: one Turbo process needs ~6.3 GB, so run one process, not two, beside a render.
- CPU-time view: ≈7.8 CPU-s per audio-s → ≈4.5 CPU-hours per single pass.

**Casting (one voice per character, never drifting)**
1. Pick or design the voice: a Kokoro stock voice, or a Qwen VoiceDesign description we wrote (never a
   description of a real person or existing character; no cloning of real recordings).
2. Render one ~10 s neutral casting clip; owner approves it by ear; it becomes the locked voice master
   (like the picture masters): stored with its text, seed, engine versions and a checksum
   (e.g. `production/voices/<CHAR>.wav` + `voices.json`; small files).
3. Every line of that character, every episode, clones that same clip with the same pinned engine version.
4. Drift check per take: speaker similarity to the master ≥ 0.75 (our takes were 0.78-0.91) or re-render.

**Voice-direction pass on a script**
- The writer adds a short direction to every line with performance in it, in a fixed form, e.g.
  `JAX [fear] pace=fast level=normal — "Temi! Hi! I'm about to make a payment—"` and
  `MIRA [whispering] level=quiet — "It prefers her."`; flat lines get nothing and go to Kokoro.
- A builder turns notes into tags (one or two tags, at the start or exactly where the laugh/sigh goes) and
  renders 2-3 takes of each noted line (fixed seeds, so any take can be re-made).
- Numbers pick the shortlist: WER ≤ 0.1 after name respelling, duration within the scene's timing, no
  long lead/trail (> 0.5 s) or runaway length, speaker similarity ≥ 0.75, no clipping; then pitch/loudness
  movement as a tie-break. Fast lines get a time-stretch to the target pace.
- The owner listens to a short reel of only the noted lines (≈60-120 per episode, best take first, one
  alternate) and swaps any by ear. Agents never call a take "good".

**Next tests worth doing (cheap):** Chatterbox Nano (needs one HF click-through by the owner, or the
community ONNX copy) for 5-10x speed; Qwen3-TTS int8 C runtime; a post time-stretch on fast lines; a
whisper post-chain (formant-preserving breathy filter) if the ear says `[whispering]` is not a whisper.

## 5. What was checked and what was not
- Checked: licences on the model cards/READMEs named above; per-take compute time, threads, load, RAM;
  Whisper word accuracy; duration, words/s, pitch range and movement, loudness movement, voiced
  fraction, brightness, clipping, lead/trail silence; speaker similarity within and across characters;
  reel loudness (parts measure −21.4 to −22.4 LUFS integrated including slates and gaps, clips −20 LUFS,
  peaks −1.7 to −1.9 dBFS).
- Not checked: **any listening**; whether laughs/whispers/shouts actually happen; accents of the designed
  voices; whether the speaker-similarity encoder (trained on ordinary speech) is fair on shouting and
  whispering; the reported Resemble retirement; Chatterbox's Perth watermark package licence in detail
  (it ships inside the MIT package); Chatterbox Nano, Dia, Zonos, CSM, Parler, CosyVoice, MOSS, any
  voice-conversion tool (not run).
- Not settled: Orpheus (Llama 3.2 licence terms); Supertonic (disclaimer clause — treated as not cleared);
  VibeVoice, IndexTTS-2, Seed-VC/RVC weights.
- Orpheus line 1 has one take only (second stopped to save time). Supertonic/Qwen-probe times were taken
  under heavy load from the video render, so they are pessimistic.
