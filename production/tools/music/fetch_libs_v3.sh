#!/usr/bin/env bash
# Fetch the v3 sound libraries into the scratchpad (never the repo). Licences: assets/audio-sources.json.
#  - VCSL (CC0), sparse checkout of the 'sfz' branch: only the instruments v3mix.PRESETS3 uses (~1.8 GB)
#  - FreePats Spanish classical guitar SFZ (CC0), needs 7z (apt install p7zip-full)
#  - Voxengo IM Reverbs impulses (royalty-free incl. commercial use; do not redistribute)
# Note: a partial clone fetches blobs lazily - never run `git ls-tree -l` in it (that downloads everything).
set -euo pipefail
A2=${SU_AUDIO2:-/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/audio2/libs}
mkdir -p "$A2"; cd "$A2"
if [ ! -d vcsl ]; then
  git clone -q --filter=blob:none --no-checkout --depth 1 -b sfz https://github.com/sgossner/VCSL vcsl
fi
cd vcsl; git config gc.auto 0; git sparse-checkout init --no-cone
cat > .git/info/sparse-checkout <<'LIST'
*.sfz
/README.md
/Idiophones/Struck Idiophones/Balafon/
/Idiophones/Struck Idiophones/Marimba/
/Idiophones/Struck Idiophones/Xylophone/
/Idiophones/Struck Idiophones/Vibraphone/
/Idiophones/Struck Idiophones/Woodblock/
/Idiophones/Struck Idiophones/Slapstick/
/Idiophones/Struck Idiophones/Flexatone/
/Idiophones/Struck Idiophones/Vibraslap/
/Idiophones/Struck Idiophones/Ratchet/
/Idiophones/Struck Idiophones/Guiro/
/Idiophones/Struck Idiophones/Finger Cymbals/
/Idiophones/Struck Idiophones/Hand Bells, Nepalese/
/Idiophones/Struck Idiophones/Mark Trees/
/Idiophones/Struck Idiophones/Suspended Cymbal 1/
/Idiophones/Struck Idiophones/Shaker, Small/
/Idiophones/Struck Idiophones/Claves/
/Idiophones/Struck Idiophones/Triangles/
/Idiophones/Struck Idiophones/Glockenspiel/
/Idiophones/Struck Idiophones/Hi-Hat Cymbal/
/Idiophones/Struck Idiophones/Cajon/
/Idiophones/Plucked Idiophones/Kalimba, Kenya/
/Membranophones/Struck Membranophones/Darbuka/
/Membranophones/Struck Membranophones/Frame Drum/
/Membranophones/Struck Membranophones/Conga/
/Membranophones/Struck Membranophones/Bongos/
/Membranophones/Struck Membranophones/Snare Drum, Modern 1/
/Membranophones/Struck Membranophones/Bass Drum 1/
/Membranophones/Struck Membranophones/Tom 1/
/Chordophones/Zithers/Grand Piano, Kawai/
/Chordophones/Zithers/Dan Tranh/
/Chordophones/Composite Chordophones/Folk Harp/
/Chordophones/Composite Chordophones/Concert Harp/
/Aerophones/Edge-blown Aerophones/Train Whistle, Toy/
LIST
git checkout -q HEAD
cd "$A2"
mkdir -p freepats_dl voxengo_dl
[ -f freepats_dl/g.7z ] || curl -sSL -o freepats_dl/g.7z https://freepats.zenvoid.org/Guitar/SpanishClassicalGuitar/SpanishClassicalGuitar-SFZ-20190618.7z
[ -d freepats/SpanishClassicalGuitar-SFZ-20190618 ] || 7z x -y -ofreepats freepats_dl/g.7z > /dev/null
[ -f voxengo_dl/IMreverbs.zip ] || curl -sSL -o voxengo_dl/IMreverbs.zip https://www.voxengo.com/files/impulses/IMreverbs.zip
python3 -I -c "import zipfile; zipfile.ZipFile('voxengo_dl/IMreverbs.zip').extractall('voxengo')"
echo "v3 libraries ready in $A2"
