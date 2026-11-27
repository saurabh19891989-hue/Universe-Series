# Episode 4 — Casting and art-department notes

For the art department. Descriptions follow `canon/CHARACTER-LOCKS.md` style and are meant to be
pasted into prompts with the style line from `production/IMAGE-PIPELINE.md` §2. Every new face
needs one master image and the owner's casting approval before any scene image is made; after
that, always generate from the master. Status of everything new here: **PROPOSED**.

**Rules for this episode's pictures**
- Photoreal, bright, well lit, rich colour. No film look, no murk. Mars light is warm salmon-orange
  and comes from above in every Phobos interior.
- **No readable text in any generated image.** Every slip, card, form, sign, board and screen is
  generated blank and lettered by us in post.
- Windows and skylights are generated pure black; the real Mars plate is composited by us
  (`production/tools/look/composite_window.py`).
- Say the age firmly (the model ages women 5–10 years).
- Prompts never name an actor or real person.

---

## 1. Characters

| Id | Character | Locked description (proposed, for prompts) | Notes |
|---|---|---|---|
| oyuna | Oyuna Tseren | **Match the existing master** `assets/characters/oyuna/master.jpg`: Mongolian woman in her early 50s, calm weathered face with rosy cheeks and fine lines, a small warm closed-mouth smile; long, wavy, grey-streaked dark hair loose over her shoulders; quilted earth-brown wool jacket over a patterned brown-and-ochre wrap collar, a maroon felt strap across her chest, a worn tan leather satchel at her hip | Always pass the master with `-i`. For 15 add a small two-stringed lute (topshuur) with a carved horse-head-free plain neck. For E05 continuity she later wears a formal deel; not in this episode |
| nasreddin | Nasreddin (guest) | Old man of about 70 of no single nationality, warm sun-browned face, bright amused eyes with deep laughter lines, a very full, long grey beard that completely covers his mouth; an enormous soft felt traveller's hat with a wide floppy brim; a long quilted coat patched with squares of many different countries' cloth (ikat, plaid, block-print, felt, velvet) in faded bright colours; soft leather slippers | No turban, no religious dress or objects. Not modelled on any statue, film or national illustration. Most shots are from behind or in profile, sitting backwards; generate a back-view reference and a three-quarter-from-behind reference with the master |
| donkey | His donkey | A small grey donkey with a pale muzzle and dark eye-rings, a worn red woollen blanket, a paper ticket clipped to its bridle (blank) | Prop-animal master; keep it identical across shots |
| pell | Auditor Pell | English man, about 60, tall and thin, mild long pale face, neat short grey hair, rimless reading glasses on a cord; a long dove-grey Directorate coat of plain cut with no insignia, grey gloves; carries a furled black umbrella and a folded newspaper | Must read as kind and precise, never sinister-looking. Key references: eyes over a newspaper; holding a teacup at his chin; from behind with the umbrella; in a pressure suit with the umbrella clipped to it |
| arakawa | Commander Tomoe Arakawa | Japanese woman, 45, severe and composed, hair in a low practical knot, a few strands of grey; fitted navy-black uniform with a high collar and no real-world insignia; holds a small black notebook and a steel pen | Updates the PROPOSED lock. No samurai or katana imagery, no calligraphy brush. References: profile; notebook held up (page blank); bowing |
| wen | Wen Jialing, chief dispatcher, Relay Guild | Chinese woman, 38, sharp, warm, quick eyes, chin-length black hair tucked behind one ear with a pencil behind it; a signal-yellow Relay Guild work jacket with teal piping and many pockets; a slim headset; a steel stopwatch on a lanyard | The season's Chinese recurring role, introduced here. Practical, not glamorous-costumed; no cheongsam or "oriental" styling. Silent this episode |
| registrar | The Registrar (a machine) | A tall office machine of polished brass and dark green enamel, with rotating brass card drums, rows of small card-index drawers, a printer slot that issues paper slips, a round brass desk bell, and one small warm amber-green indicator lamp; seen through a frosted glass counter window; photographed as a real practical prop | Treat like PIP: a prop master. Never a face. Two states: lit and working; dark (26) |
| officer | Cutter boarding officer | A helmeted figure in a plain grey Directorate pressure suit, opaque visor, holding up a blank card | Generic; no face |
| waiters | The long-term waiters | A middle-aged Mongolian lawyer in a good suit with a briefcase; a choir of eight in matching teal scarves (mixed ages and origins); two young Mongolian cousins, a man and a woman in their 20s in practical travel clothes; a lean older man holding a wooden ladder | Background; each needs one consistent still. Global, bright, slightly eccentric, never comic grotesques |
| dispatchers | Relay Guild dispatchers | Four or five people of different origins in signal-yellow Guild jackets with headsets, at boards | Background |

Existing masters used unchanged: Jax, Mira (redo pending), Lucía (redo pending), Seo, PIP, Chichikov
(soft focus only), Idris (PROPOSED; E03 should lock him), the dog (E03's big grey-muzzled rough-coated
working dog; lock from E03).

---

## 2. Sets and places

| Id | Place | Locked description (proposed) | Colour world |
|---|---|---|---|
| phobos-surface | Phobos, near Stickney | Charcoal-grey dusty ground scored with long, straight, parallel grooves, scattered boulders, a gentle crater rim on the horizon; harsh white sunlight; black sky (generated black for the Mars plate) | Charcoal, white, salmon from Mars |
| office-door | Exception Office door | A round steel door set into the crater wall, a painted sign board above it (blank), a small mail dock with a short landing pad beside it | as above, plus a cobalt door |
| waiting-room | The Waiting Room | A vast hall like a grand old railway station cut into rock, under a huge round skylight (black, for Mars); rows of teal wooden benches with brass rails; wild green plants grown over everything; a brass tea urn; a big clay pot of pebbles; a flip-number board and a small brass music box on the wall; warm salmon-orange light from above | Salmon-orange light, teal, brass, green |
| counters | The Counters | A long hall of cobalt-blue and cream glazed tiles; forty frosted glass counter windows in a row, all shuttered with cream blinds except one lit window; brass pneumatic tubes running along the ceiling; a brass ledge under each window | Cobalt, cream, brass, one green-lit window |
| reading-room | The Reading Room and ger | A round domed hall lined with empty wooden shelves, a round oculus in the dome (black, for Mars), and in the centre a traditional Mongolian ger of white felt over a wooden lattice, with an orange-painted wooden door decorated with blue knotwork, a thin stovepipe | White felt, saffron-orange, blue, Mars-salmon |
| ger-interior | Inside the ger | Felt rugs in red and blue, a small iron stove in the centre, a two-stringed lute hanging on the lattice wall, painted wooden chests, bowls of milk tea, a brass pneumatic-tube outlet by the stove | Warm red, blue, gold firelight |
| skylight-dome | The great skylight, from outside | A wide shallow dome of glass panes in a brass frame set flush into charcoal ground; through it, far below, a warm orange-lit hall | Charcoal, glass, orange glow |
| vault | The Records Vault | A long straight trench roofed with glass panels (black, for Mars), both walls lined floor to thirty metres with amber-wood card-index drawers with small brass label plates, brass rolling ladders, warm light, a vanishing point | Amber, honey wood, brass, salmon glow |
| deimos-hall | Relay Guild dispatch hall, Deimos | A long low hall painted signal-yellow and teal, one whole wall a giant split-flap board (blank tiles), a central dispatch desk with printers and a stopwatch, a long window (black, for the dish and Mars) | Signal-yellow, teal, white flaps |
| deimos-dock | Relay Guild dock, Deimos | A small landing dock on smooth pale-grey dust under black sky, a large white relay dish on a mast, a ramp | Pale grey, white, red ferry |
| bridge, hold | The Unscheduled | Existing (`assets/sets/bridge`, `assets/sets/hold`) | as locked |

## 3. Vehicles
| Id | What | Description |
|---|---|---|
| ferry | Relay Guild mail ferry | A small, stubby, bright pillar-box-red mail ferry, rounded and old-fashioned, with a side mail hatch, brass trim, a yellow stripe; original design |
| shuttle | Directorate shuttle | A plain grey, flat, unadorned small shuttle |
| cutter | Arakawa's cutter *Steadfast* | A grey Directorate enforcement cutter, long and narrow, a lit window band and a searchlight; original design, must not resemble any film or TV ship |
| ship | The Unscheduled | Existing master |

## 4. Props
Tickets (blank, two sizes); the NOW SERVING flip board (blank flaps); the brass music box; the clay
pot of pebbles; a box full of torn paper slips; brass pneumatic-tube capsules; FORM 1 (long, ruled,
blank); DIRECTORATE FORM 0 (grey, one stamp box); Arakawa's black notebook and steel pen; the
*Directorate Gazette* (blank newsprint); Pell's furled umbrella and teacup; PIP's canvas postal
satchel; the Registrar's small brass letter scale; a green FRAGILE label (blank); a canvas mail
sack; the 1877 index card (aged, blank, lettered in post); the topshuur; salt-tea bowls; Wen's
stopwatch and dispatch slips; the ferry delivery slip; playing cards (one ace of clubs); a ground
anchor and tether line; Seo's wrist screen; Chichikov's inlaid box, teacup and notebook (existing);
the LOT 14 trunk (existing); the parcel with 31 labels and the new knightly label (existing + E03).

## 5. Real footage needed (from `assets/candidates.json`, NASA and ESA/Hubble only)
- Mars full, gibbous, half and crescent for windows and skylights: ESA/Hubble astro_n "Mars 360
  degree rotation" and heic1814d, graded per phase; crescent and dark-disc versions built from them.
- PIA10366 / PIA10367 (HiRISE Phobos) for "What was real" and any orbital view of Phobos.
- ESA/Hubble opo1729b (Phobos in orbit time-lapse) for "What was real".
- Strip all original audio (ESA/Hubble music is not covered by the licence).
- Do not use the ESA Mars Express Commons re-uploads until their licences are verified.
