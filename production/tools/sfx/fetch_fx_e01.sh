#!/usr/bin/env bash
# Fetch the CC0 recorded effects used by the 28 Nov customs-desk remix (licence re-checked per file).
# Records go to <dir>/manifest.json; the curated copy with usage is assets/audio-sources.json.
set -euo pipefail
D=${1:-/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/audio2/fx_real}
cd "$(dirname "$0")"
python3 fetch_freesound_cc0.py get "$D" "$D/manifest.json" \
  458871:roomtone_large_interior_ac 570015:roomtone_empty_office_hallway 451918:fluorescent_hum_store \
  637555:footsteps_shoes_hard_floor 534635:footsteps_docmartens 461888:rubber_stamp_plastic 448474:stamp_es \
  182889:paper_shuffle_stack 653953:paper_rustling 256310:clothing_movement 788342:clothes_walking_foley \
  464252:office_chair_creaky 822460:bang_table_desk 142348:cartoony_whooshes 568834:swish_whoosh
