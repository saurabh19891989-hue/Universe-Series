# Free TTS bake-off: report

**Nobody has listened to any of these files.** Agents cannot hear audio. Everything below about quality is inferred from Whisper word error rate (intelligibility only, says nothing about acting, accent or pleasantness), timings and licence reading. Licence notes are not legal advice.

Machine: 4 shared CPU cores, no GPU. Load average was 6-9 from other agents during most runs, so speeds are pessimistic, especially torch engines. Scene = 188 words, 60-80 s of speech. Episode estimate = 5,500 words at the measured real-time factor (RTF = synthesis seconds / audio seconds).

## Comparison table

| Engine | Licence (code / weights / voices) | Monetised YouTube OK? | Voices / accents | Expressive controls | Synth time (scene) / RTF / 35-min episode | WER | Notes |
|---|---|---|---|---|---|---|---|
| **Kokoro-82M** (kokoro-onnx 0.6.1, v1.0 model) | Apache-2.0 code and weights ([HF](https://huggingface.co/hexgrad/Kokoro-82M)) | **Yes** (permissive; no attribution required) | 54 voices: US, GB (am_/af_/bm_/bf_), plus Hindi (hf_/hm_), Italian, Japanese, etc. **No Indian-English voice.** | speed only; punctuation affects pacing; no emotion tags | 16 s / 0.27 / ~0.13 h | 1.1% (alt cast 0.5%) | Mira uses Hindi voice `hf_alpha` reading English text as an accent hack; unheard, may sound odd or wrong. `kokoro_alt` casts bf_emma with no hack. |
| **Piper** (piper-tts 1.8, medium/high voices) | Engine piper1-gpl is GPL-3 (affects redistributing the engine, not audio); each voice has its own dataset licence | **Yes for the cast voices only** (joe CC0; VCTK CC-BY 4.0 needs credit; northern_english_male CC-BY-SA 4.0). **No** for ryan (CC-BY-NC-SA) and hfc_male (BY-NC-SA); unclear for lessac (Blizzard licence) and alan (Mycroft "all rights reserved"). Cards: huggingface.co/rhasspy/piper-voices | en_US and en_GB single voices; VCTK 109 speakers incl. Indian-accented p248 (used for Mira) | length_scale (speed), noise_scale / noise_w (variation) | 6.8 s / 0.11 / ~0.06 h | 2.6% | Fastest. Flat delivery. Misreads "Pip" as "pep" and "nowhere", so very robotic on some words. |
| **Chatterbox** (Resemble AI, MIT; also Turbo) | MIT code and weights ([GitHub](https://github.com/resemble-ai/chatterbox)); embeds Perth watermark | Yes (MIT) in principle | cloned from reference audio; exaggeration/emotion knob | exaggeration, cfg, paralinguistic tags (Turbo) | **FAILED the speed test**: ~275 s per 3 s of audio (RTF ~90) on this box | n/a | ~28 min spent (py3.13 needed float32 and pkg_resources patches). Would need a GPU. Script: `chatterbox_probe.py`. No audio produced. |
| **MeloTTS** (EN, v2) | MIT code and weights ([GitHub](https://github.com/myshell-ai/MeloTTS)) | **Yes** (MIT) | 5 voices: EN-US, EN-BR, **EN_INDIA**, EN-AU, EN-Default (one per accent) | speed only | 199 s / 3.2 / ~1.6 h (inflated by CPU contention) | 2.1% | Only Indian-English voice found among viable engines. Voice genders not verified. |
| **edge-tts** (unofficial Microsoft Edge read-aloud endpoint) | Library GPL-3; voices are Microsoft's service | **NO / unsafe.** No Microsoft permission found for the unofficial endpoint. Microsoft staff say commercial use without a paid Azure subscription may violate their terms and recommend Azure AI Speech ([Q&A](https://learn.microsoft.com/en-us/answers/questions/2088770/are-opensource-edge-tts-free-for-commercial-use), [Q&A 2](https://learn.microsoft.com/en-us/answers/questions/2392491/unofficial-edge-tts-api)); audio output commercial rights are stated for the paid Azure tier ([Azure redistribution Q&A](https://learn.microsoft.com/answers/a/12933078)). Treat as unlicensed, and it can be blocked at any time. | Many neural voices; en-IN (Neerja, Prabhat), en-GB, en-US | rate and pitch only (SSML stripped by service) | 21 s (network) / 0.26 / ~0.17 h | 1.6% | Needs internet. Probably the most natural of the free set, but legally unclear. Paid Azure Speech uses the same voices with proper rights and SSML styles, which would be the licensed way to get them. |
| **Pocket TTS** (Kyutai, 100M) | Weights CC-BY 4.0 (HF card, [GitHub](https://github.com/kyutai-labs/pocket-tts)); voices per source dataset | **Yes with attribution** (cast voices: voice-donations CC0, VCTK CC-BY, voice-zero LibriVox PD). Excluded: cosette (Expresso BY-NC), jean (EARS BY-NC) ([voices licence](https://huggingface.co/kyutai/tts-voices)). Prohibited-use clause: no deception or impersonation. | ~25 preset voices, mostly US/GB; no Indian-English preset, accents unverified. Cloning weights are gated (no token), so only presets used | none found | 50 s / 0.75 / ~0.4 h | **0.5%** | Realtime-capable even on contended CPU. Casting by voice name only; unheard. |
| Parler-TTS mini, StyleTTS2, Zonos, Sesame CSM, Orpheus, Dia, KittenTTS | Parler Apache-2.0; StyleTTS2 MIT code (weights ask for disclosure); Zonos Apache-2.0; CSM Apache-2.0 (needs gated Llama); Orpheus Apache-2.0; Dia Apache-2.0; Kitten Apache-2.0 | Probably yes, unverified | not tested | | **Not run**: all but Kitten are 1-3B models or GPU-oriented, and Chatterbox (0.5B) already showed RTF ~90 here. KittenTTS install failed on dependency (misaki) and the disk filled. | n/a | |
| XTTS-v2 (CPML), F5-TTS (CC-BY-NC weights), Fish-Speech (CC-BY-NC) | non-commercial | **No**, skipped | | | | | |

## Recommended free cast (commercially usable, all unheard)
- **Primary:** `kokoro` cast: Jax = am_puck, Mira = hf_alpha (accent hack, verify by ear) with fallback to `melotts` EN_INDIA clips or Piper VCTK p248, Pip = bm_george, Baron = bm_fable slowed 0.88. Apache-2.0, fast, WER 1.1%.
- **Second opinion:** `pocket-tts` (best WER, CC-BY, credit Kyutai/VCTK in video description).
- Mixing engines per character is fine: Mira from MeloTTS (`melotts/mira.mp3`) or Piper (`piper/mira.mp3`), others from Kokoro. Levels are all -16 LUFS per file.
- Not for monetised use: edge-tts (unless moving to paid Azure Speech).

## Known weaknesses of the free route
- Emotion range is narrow. None of the CPU-feasible engines does real shouting, whispering or laughing. Mira's quiet line was approximated with slower speed only. Chatterbox, which has an emotion control, is impractical on CPU.
- No Indian-English voice in Kokoro; Melo's one voice and Piper's VCTK p248 are low-expressivity.
- Per-line consistency: each line is rendered separately, so prosody can jump between lines. Pip/Baron timbre was not checked by ear.
- Whisper flagged "Munchausen" (rendered "Munchawson"/"munchausen jax"), Piper's "Pip", "nowhere", "shallow", and "I'd" -> "I've" in several engines (maybe whisper's error, not TTS). A pronunciation lexicon or respelling ("Moon-chow-zen") is needed.
- WER is intelligibility only and was measured on full mixed scene with faster-whisper small int8.

## Reproduce
Venvs and models live in the scratchpad (not repo). Scripts in `production/tools/voice/`; shared helpers `common.py` (script, gaps, loudnorm -16 LUFS, MP3 192k, metrics.json); `wer.py` scores all.
- Kokoro: `pip install kokoro-onnx soundfile`; model files from github.com/thewh1teagle/kokoro-onnx releases `model-files-v1.0`; `python kokoro_scene.py`
- Piper: `pip install piper-tts`; voices from huggingface.co/rhasspy/piper-voices; `python piper_scene.py`
- Pocket TTS: `pip install pocket-tts soundfile`; `python pocket_scene.py [jax mira pip baron voice names]`
- MeloTTS (python 3.11): `pip install git+https://github.com/myshell-ai/MeloTTS.git "setuptools<81"`; fixes noted in `melo_scene.py`; `python melo_scene.py`
- edge-tts: `pip install edge-tts`; `python edge_scene.py` (sandbox CA/proxy tweak inside)
- Chatterbox probe: `chatterbox_probe.py ref.wav`
- WER: `pip install faster-whisper jiwer`; `python wer.py [engine ...]`

Outputs per engine in `samples/voices/<engine>/`: `scene.mp3`, `jax.mp3`, `mira.mp3`, `pip.mp3`, `baron.mp3`, `casting.json`, `metrics.json` (timings, WER, word errors).
