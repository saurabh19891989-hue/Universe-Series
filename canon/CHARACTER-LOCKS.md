# Character locks — the look of every recurring character

Rule: once the owner approves a master image, the face is fixed. Every later image of that
character is generated from the master as a reference plus the locked description below
(see `production/IMAGE-PIPELINE.md`). Change a description only with the owner's approval.

Status key: PROPOSED (description written, no master yet) · TEST (master exists from a test,
owner has not approved the face) · LOCKED (owner approved; master in `assets/characters/`).

| Id | Character | Locked description (use verbatim in prompts) | Master | Status |
|---|---|---|---|---|
| jax | Jax Vale, captain | Mediterranean Greek man, late 30s, olive skin, dark curly hair greying slightly at the temples, stubble, weathered face, crooked half-smile; scuffed burnt-orange flight jacket with too many pockets | `assets/characters/jax/master.jpg` | LOCKED (owner, 27 Nov) |
| mira | Dr. Mira Sen, cartographer | Bengali Indian woman, 32, strikingly beautiful film-star face, dark braid, sharp intelligent eyes, ink-stained fingers; fitted indigo flight suit, brass loupe on a chain | `samples/look-codex/cast-mira.jpg` | REDO 2 — more glamorous (owner, 27 Nov) |
| lucia | Lucía "Lucha" Ortega, engineer | Mexican woman, 29, slim, lean and athletic, strikingly attractive film-star face, short practical dark hair; fitted grease-marked coveralls, a red ribbon tied round her wrist | `samples/look-codex/cast-lucia.jpg` | REDO 2 — slimmer, more glamorous (owner, 27 Nov) |
| idris | Idris al-Rahhal, navigator | Iraqi Arab man, 40, elegant, trimmed beard, gambler's smile; threadbare but beautiful embroidered coat | — | PROPOSED |
| seo | Han Seo-yeon, pilot | Korean woman, 30, composed, cropped hair, unreadable expression; plain grey pilot's jacket | `assets/characters/seo/master.jpg` | LOCKED (owner, 27 Nov) |
| oyuna | Oyuna Tseren, archivist | Mongolian woman in her 50s, calm lined face, long grey-streaked hair; layered wool, worn leather satchel | `assets/characters/oyuna/master.jpg` | LOCKED (owner, 27 Nov) |
| pip | PIP, ship's computer (a prop, not a face) | Small brass-and-cream machine like a desk lamp crossed with a postal scale, one glowing amber lens, a rubber-stamp arm; photographed as a real practical object | `assets/props/pip/master.jpg` | LOCKED (owner, 27 Nov) |
| baron | Baron Munchausen | German man in his 70s, enormous white moustache that completely covers his mouth, black tricorn hat; moth-eaten red 18th-century cavalry coat over a patched pressure suit. Design after Doré's 1862 engravings, never any film | `assets/characters/baron/master.jpg` | LOCKED (owner, 27 Nov) |
| chichikov | Pavel Chichikov, buyer for Voss | Russian man, 45, round pleasant forgettable face, neither handsome nor plain; good grey overcoat, grey gloves, a small inlaid wooden travelling box | `assets/characters/chichikov/master.jpg` | LOCKED (owner, 27 Nov) |
| voss | Soren Voss, patriarch | Scandinavian man, late 60s, silver hair, kind eyes that do not blink enough; immaculate dark suit of an unfamiliar cut | — | PROPOSED |
| ilse | Ilse Voss, heir | To be written | — | — |
| mattias | Mattias Voss, younger son | To be written | — | — |
| pell | Auditor Pell | To be written | — | — |
| arakawa | Commander Tomoe Arakawa | Japanese woman, 40s, severe dark uniform with no real-world insignia | — | PROPOSED |
| cass | Cass Rook, rival captain | Nigerian-British man, 40s, charming; expensive but travel-worn pilot's coat | — | PROPOSED |
| noakes | Superintendent Noakes (ep 1) | English man, 55, tired; customs uniform without real insignia | `assets/characters/noakes/master.jpg` | LOCKED (owner, 27 Nov) |
| temi | Temi Adeyemi, "Recoveries" (ep 1) | Nigerian woman in a headset, bright, mid-smile, bank call-centre desk | `assets/characters/temi/master.jpg` | LOCKED (owner, 27 Nov) |
| mamani | Officer Inti Mamani (ep 1) | Andean man, kind, tired, port control desk | `assets/characters/mamani/master.jpg` | LOCKED (owner, 27 Nov) |

## Sets, ship and props
| Id | What | Locked description | Master | Status |
|---|---|---|---|---|
| bridge | Bridge of *The Unscheduled* | Cramped working cockpit, tape and cable ties, mismatched screens, one large window (kept pure black for real footage) | `assets/sets/bridge/master.jpg` | TEST |
| hold | Cargo hold | Empty hold, one brown-paper parcel strapped down in the middle, reactor housing at the back | — | PROPOSED |
| ship | *The Unscheduled*, exterior | Boxy, patched, lived-in working courier ship of original design; must not resemble any film or TV ship | `assets/ship/master.jpg` | TEST |
| customs | Rim Port customs hall | Hall built for two thousand, staffed for three; rows of empty benches; flip-number board on the far wall | `assets/sets/customs/master.jpg` | TEST |
| inn | The Silver Hatchet | Low inn cut into crater rock, half in harsh sunlight, half in permanent dark; crowded with impossible objects | — | PROPOSED |
