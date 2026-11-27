#!/usr/bin/env bash
# Re-render every Route A cue: MIDI -> FluidSynth (FluidR3_GM, MIT) -> sox -> -16 LUFS MP3 192k.
# Needs: apt install fluidsynth fluid-soundfont-gm sox ; pip install pretty_midi mido numpy
# Output: samples/music/A*.mp3, samples/music/midi/*.mid, samples/music/spectrograms/*.jpg
# Swap the sound set with SU_SF2=/path/to/other.sf2 (e.g. MuseScore_General.sf3, MIT).
set -euo pipefail
cd "$(dirname "$0")"
for s in a1_main_title a2_caper a3_tension a4_emotional a5_global_japan; do
  python3 "$s.py"
done
