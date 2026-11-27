# LISTEN FIRST: Episode 1 table read (script-v3)

Nobody has listened to these files. Everything below is measured, not heard. The voices are Kokoro text-to-speech with simple filters.

## The four files (mono, 44.1 kHz, about 72 kbps MP3, each under 5 MB)

| File | Covers | Length |
|---|---|---|
| E01-tableread-1-cold-open-and-act1.mp3 | Cold open, main title sting, Act One (scenes 0-7) | 8:47 |
| E01-tableread-2-act2.mp3 | Act Two (scenes 8-16) | 7:30 |
| E01-tableread-3-act3.mp3 | Act Three (scenes 17-22) | 6:34 |
| E01-tableread-4-act4-and-tag.mp3 | Act Four, Tag, "What was real", end sting (scenes 23-31) | 8:44 |

A quiet narrator reads a slate before each scene ("Scene six. Customs hall, holding bay.") and a few short action beats. Narration is 3:43 of the total (11.8%). Two stings are the only music (10 s title after the cold open, 5 s end card).

## Running time

Total **31:36** with narration, slates, 1.2 s scene gaps and the 15 s of stings. Without narration and stings it is about **27:03**. The script's header claims 35:55 (scene targets sum to 35:45). The read is therefore about 4 minutes shorter than the claim with narration, about 8 minutes shorter without it. Cause: the TTS speaks the 4,455 words at about 184 wpm of pure speech, against the 155 wpm in the script's model, and it leaves shorter silences than the script's estimates allow for.

## Three scenes furthest from their targets (narration removed, so the comparison is dialogue plus pauses only)

1. **Scenes 18-19** (Noakes's office, then corridor): 1:22 vs target 1:50, 36 s under.
2. **Scene 21** (outer rim, Earth on the horizon): 1:52 vs target 2:20, 35 s under.
3. **Scene 30** (bridge, afterwards): 1:38 vs target 1:50, 30 s under.

No scene runs over its target once narration is removed. With narration counted, scene 31 (Tag) is the only one over (46.7 s vs 45 s). Every scene's numbers are in timings.json.

## Other files in this folder

casting.json (voices and filters), timings.json (per scene start, duration, spoken words, target, per file and overall totals, loudness), lines.csv (every rendered line with scene, speaker, text as spoken and duration), wer_check.json (speech-recognition check).

## Measured, not heard

- Loudness: -16.3 LUFS integrated on all four files; true peak -2.1, -1.7, -2.3 and -2.2 dBTP; no clipped samples.
- Whisper small on a 3-minute sample of each file: word error rate 4.5%, 6.5%, 3.5%, 5.2% against the script wording. Most mismatches are spelling variants (metres/meters, parlour/parlor). Names that Whisper heard differently: Oczakow ("ochochof", "ochikov"), Mira ("mirror"), Noakes ("nooks"), Jax's hand-built "Chich... Chicha...". Whether they sound right to a person is unknown.
- Things to check by ear first: the Baron's pitch shift, PIP's band-limit, radio filters on V.O. and radio lines, the Chichikov / Noakes / Baron British male voices (four of the six male voices (Pip, Baron, Chichikov, Noakes) are British and could be hard to tell apart), and the "Meera" respelling.
