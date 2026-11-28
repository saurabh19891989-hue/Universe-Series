#!/bin/bash
# TEST 3 (flat cartoon rig): the design pictures. Codex CLI, one job per picture, <=4 at once.
# usage: [TOOL=agy|codex] [MAXJ=2] make_pictures.sh [name ...]   (default: all)
set -u
R=/home/user/Universe-Series
CX="python3 $R/production/tools/look/codex_image.py"
AGY="python3 $R/production/tools/toon/agy_pic.py"
TOOL=${TOOL:-codex}
OUT=/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/toon/pics
STYLE="Flat 2D cartoon style of our own original design: bold clean dark-brown outlines of even weight, flat saturated colour with exactly one darker shadow tone per colour, no gradients, no texture, no rendering, simple readable shapes, strong silhouette, bright and colourful, attractive, tasteful. Do not imitate any existing cartoon show's character designs, eye style, mouth style or colour scheme. No text, no logos."
NOMOUTH="IMPORTANT: draw the face with NO eyes, NO eyebrows and NO mouth at all - leave plain flat skin where they would be (they are added later as separate animated parts); keep the nose, ears, hair, beard/stubble and face shape."
declare -A P REF
P[jax_heads]="Character head model sheet on a plain flat pure white background. Exactly two separate drawings of the SAME head with neck, side by side, large, not touching, same size: LEFT facing the viewer straight front; RIGHT the same head in three-quarter view turned toward the viewer's right. Heads and necks only, no body, no shoulders. Character (keep him recognisable from Image 1): Jax Vale, Mediterranean Greek man, late 30s, handsome, olive skin, dark curly hair greying slightly at the temples, short stubble, strong jaw. $NOMOUTH $STYLE"
REF[jax_heads]=$R/assets/characters/jax/master.jpg
P[mira_heads]="Character head model sheet on a plain flat pure white background. Exactly two separate drawings of the SAME head with neck, side by side, large, not touching, same size: LEFT facing the viewer straight front; RIGHT the same head in three-quarter view turned toward the viewer's left. Heads and necks only, no body, no shoulders. The braid is NOT drawn (it is a separate part): hair pulled back tidily from the face. Character (keep her recognisable from Image 1): Dr. Mira Sen, Bengali Indian woman aged 32, strikingly beautiful film-star face, warm brown skin, dark hair, small gold stud earrings. $NOMOUTH $STYLE"
REF[mira_heads]=$R/assets/characters/mira/master.jpg
P[jax_body]="Full-body character design, standing straight, facing the viewer, arms relaxed slightly away from the body, feet apart, on a plain flat pure white background, whole figure visible head to toe, centred. Character (keep him recognisable from Image 1): Jax Vale, Mediterranean Greek man, late 30s, handsome, olive skin, dark curly hair greying slightly at the temples, stubble, crooked half-smile; scuffed burnt-orange flight jacket with too many pockets over a grey-green t-shirt, dark brown work trousers, heavy boots. $STYLE"
REF[jax_body]=$R/assets/characters/jax/master.jpg
P[mira_body]="Full-body character design, standing straight, facing the viewer, arms relaxed slightly away from the body, feet apart, on a plain flat pure white background, whole figure visible head to toe, centred. Character (keep her recognisable from Image 1): Dr. Mira Sen, Bengali Indian woman aged 32, strikingly beautiful film-star face, long dark braid over one shoulder, sharp intelligent eyes, ink-stained fingers; fitted indigo flight suit with tan shoulder patches and a belt, a brass loupe on a chain round her neck, dark boots. $STYLE"
REF[mira_body]=$R/assets/characters/mira/master.jpg
P[ship_side]="Side view of the spaceship from Image 1 redrawn as a flat 2D cartoon prop: exact side profile, nose pointing to the RIGHT, whole ship visible with margin, on a plain flat pure white background. Keep its design: boxy patched courier hull in cream, mustard-yellow, grey and rust-red panels, cargo crates in green netting along the side, two round gas tanks, a roof railing, antenna and small dish, a cab with windows at the front, four round engine pods on struts. $STYLE"
REF[ship_side]=$R/assets/ship/master.jpg
P[hall_bg]="Wide background painting for a 2D cartoon, no people: the Rim Port customs hall on the Moon, as in Image 1 but redrawn in flat cartoon style. Camera straight on at standing eye height. The whole back wall is one enormous window divided by a few slim frame bars; the glass of the window is PURE SOLID BLACK (#000000) with nothing in it (real footage is put in later). In front: a clean pale floor with warm cream and teal tiles, two rows of empty orange-red benches on the left, a tall flip-number board on the far left wall, and on the right a single customs desk with a glass screen, a lamp and a rubber stamp, lit warm. Bright, cheerful, colourful, lots of floor space in the lower third for characters to walk. $STYLE"
REF[hall_bg]=$R/assets/sets/customs/master-bright.jpg
names=("$@"); [ ${#names[@]} -eq 0 ] && names=(jax_heads mira_heads jax_body mira_body ship_side hall_bg)
for n in "${names[@]}"; do
  if [ "$TOOL" = agy ]; then $AGY "$OUT" "$n" "${P[$n]}" "${REF[$n]}" &
  else $CX toon "$n" "${P[$n]}" -i "${REF[$n]}" --no-style --purpose "toon test 3 design" & fi
  while [ "$(jobs -rp | wc -l)" -ge ${MAXJ:-2} ]; do sleep 5; done
done
wait
