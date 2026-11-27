#!/usr/bin/env bash
# One command to re-render every cue.
#   ./render_all.sh          v1 (FluidR3) A1-A5  +  v2 (VPO SFZ + GeneralUser GS) everything
#   ./render_all.sh v2       v2 only
#   ./render_all.sh e01      Episode 1 score only (e01_score.py -> e01_render.py)
# Needs: apt install fluidsynth fluid-soundfont-gm sox ffmpeg ; pip install pretty_midi mido numpy scipy soundfile
# Sample libraries (fetched once into the scratchpad by ./fetch_libs.sh):
#   Virtual Playing Orchestra 3 wave files + standard scripts, GeneralUser GS v2.0.3.
# Outputs: samples/music/*.mp3 (v1), samples/music/v2/*.mp3, samples/music/midi/*.mid, spectrograms/*.jpg,
#          samples/e01/music/ (E01 review MP3s + cues.json) and scratchpad/e01/music/ (48 kHz WAV masters, stems)
set -euo pipefail
cd "$(dirname "$0")"
[ -d "${SU_VPO:-/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/music/libs/vpo_dl/x/Virtual-Playing-Orchestra3}" ] || ./fetch_libs.sh
if [ "${1:-all}" = "e01" ]; then python3 e01_render.py; exit 0; fi
if [ "${1:-all}" != "v2" ]; then
  for s in a1_main_title a2_caper a3_tension a4_emotional a5_global_japan; do python3 "$s.py"; done
fi
python3 v2_render.py
[ "${1:-all}" = "v2" ] || python3 e01_render.py
