# Free music test — findings (summary)

Written by the main session from the music agent's hand-back. The agent's longer report
(15-track library shortlist with URLs, full licence table) was not saved to disk; ask for a
re-run of the library survey if it is needed. Nobody has listened to these files.

## What was made
| File | Route | Notes |
|---|---|---|
| `A1-main-title.mp3` (61 s) | Composed as code, rendered with free samples | D minor, 120 BPM, sitar as colour; builds from -25 to -14 LUFS |
| `A2-comedy-caper.mp3` (40 s) | Composed | Pizzicato / woodwind caper |
| `A3-tension-betrayal.mp3` (53 s) | Composed | 60 BPM, one tick per second |
| `A4-emotional.mp3` (62 s) | Composed | Mohanam and Kalyani colours |
| `A5-global-japan-urashima.mp3` (50 s) | Composed | Koto in hirajoshi tuning, shakuhachi, taiko |
| `C1-ai-acestep-main-title.mp3` (30 s) | AI model run on our CPU | ACE-Step 1.5; measures dull above 2–6 kHz |
| `C2-ai-acestep-caper.mp3` (25 s) | AI model run on our CPU | Same |

All at about -16 LUFS, no clipping. A1 and A5 are bass-heavy and need high-passing under dialogue.
MIDI is in `midi/`; scripts in `production/tools/music/`; `render_all.sh` re-renders the five
composed cues in about 40 seconds.

## Licences (as reported by the agent)
- FluidR3_GM soundfont (the only samples used): MIT.
- VSCO-2 Community Edition and VCSL: CC0. Salamander piano: CC BY 3.0. Sonatina: CC Sampling Plus 1.0.
  Virtual Playing Orchestra: allows commercial music.
- ACE-Step 1.5: MIT, model card says outputs may be used commercially.
- MusicGen weights: CC-BY-NC — excluded. Stable Audio Open: free commercially under $1M revenue, gated download.
- Not verified: Musopen (403), Free Music Archive, ccMixter, DiffRhythm VAE licence.

## Measured
- ACE-Step on this CPU: 30 s of music in about 3 min 15 s after a bf16 loading patch (first run was killed for memory).
- One Incompetech library track checked ("Heroic Age") already clips at +1.1 dBTP.

## Agent's recommendation
Make the composed route the score: it is the only route that gives recurring character themes
we own outright. Improve the sound for free by re-rendering the same MIDI with VSCO-2 CE / VCSL
samples (not yet tested). Use YouTube Audio Library "attribution not required" tracks as
filler. Keep ACE-Step as a sketchpad, or run it on a rented GPU.
