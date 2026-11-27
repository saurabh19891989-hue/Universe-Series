#!/usr/bin/env bash
# Fetch the free sample libraries used by the v2 renders into the scratchpad (never the repo).
#  - Virtual Playing Orchestra 3 (Paul Battersby): "I enforce no restrictions on using this library
#    to make music, even for commercial purposes" - http://virtualplaying.com/virtual-playing-orchestra/
#    Contains Sonatina SO (CC Sampling+ 1.0), VSCO-2 CE (CC0), No Budget Orchestra (CC BY-SA 4.0),
#    Mattias Westlund (CC BY-SA 3.0), Univ. of Iowa MIS (no restrictions), stamperadam (CC0).
#  - GeneralUser GS v2.0.3 (S. Christian Collins): "You may use GeneralUser GS without restriction
#    for your own music creation, private or commercial." - https://github.com/mrbumpy409/GeneralUser-GS
set -euo pipefail
L=${SU_LIBS:-/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/music/libs}
mkdir -p "$L/vpo_dl/x" "$L/gugs"
cd "$L/vpo_dl"
curl -sSL -o wave.zip https://virtualplaying.com/go/virtual-playing-orchestra-v3-2-wave-files-archive/   # ~616 MB
curl -sSL -o std.zip https://virtualplaying.com/go/virtual-playing-orchestra-v3-3-standard-scripts/
python3 -I -c "import zipfile; [zipfile.ZipFile(z).extractall('x') for z in ('wave.zip','std.zip')]"
cd "$L/gugs"
curl -sSL -o GeneralUser-GS.sf2 https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2
curl -sSL -o LICENSE.txt https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/documentation/LICENSE.txt
