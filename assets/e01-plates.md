# Episode 1 plates: real footage and stills (acquired 27 Nov 2026)

Machine-readable manifest: `assets/e01-plates.json` (every field: sha256, URLs, credit, licence quote, crop notes, usable ranges). Files live outside the repo in the session scratchpad: `/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/e01/plates/` (proxies in `plates/proxies/`, rejects in `plates/rejected/`). Move the keepers to Google Drive `01-samples-for-review` or the build machine; nothing was uploaded.

**What was checked:** every kept file was downloaded, audio-stripped (`ffmpeg -an -c copy`), hashed, probed, proxied, and three frames per video (or the still itself) were looked at on contact sheets. **What was not checked:** nobody has played the motion plates end to end; video 'usable ranges' come from sampling every few seconds (or every 50 s on the long Artemis I clips), so boundaries are approximate. Agents cannot judge audio; all original audio is gone anyway.

**Totals:** 59 files downloaded = 25 videos (93.3 min) + 34 stills, 6.4 GB. After review: 34 usable (7 videos, 27 stills), 9 marginal, 16 rejected. Largest single file 1.06 GB. 8 SVS items are listed in the JSON as `NOT_DOWNLOADED_403`.

## 1. NASA SVS downloads: what works and what does not

- **Works:** the SVS page API `https://svs.gsfc.nasa.gov/api/{id}/` (HTTP 200) lists every media file, size, frame set and credit; the SVS HTML page also loads (200). Used for 4944, 4893, 4043, 3686, 3634, 3633, 5633, 15103, 4720, 4605.
- **Does not work from this machine:** every file under `https://svs.gsfc.nasa.gov/vis/...` returns **403 Forbidden** from the SVS Apache server (`server: Apache`, body "You don't have permission to access this resource"), not from our egress proxy. Tested with real GETs (not just HEAD): 1080p/720p/360p mp4, webm, jpg thumbnails, PNG, directory index and `frames/` folder of SVS 4944; plus one file each from 4893, 5633, 3686, 4043. Variants tried: browser-like User-Agent without personal data, `curl` UA, `Accept`/`Accept-Language` headers, `Referer` set to the SVS page, http and https, range request and full GET, sequential with 2 s gaps. All 403. The SVS page itself and `images-api.nasa.gov` return 200 from the same session, so this is a block on the `/vis/` path for this network, not a missing file. I stopped there: one attempt to fetch an SVS file through a web-archive cache was refused by this session's permission system, and I did not retry or look for other ways round the block.
- **What to do:** the owner (or any normal browser/home network) can fetch the SVS files directly; the exact filenames and URL stems are in the JSON (`direct_url`, 8 SVS entries) and below. Priority downloads: SVS 4944 `shackleton_earth_1080p30.mp4` (1920x1080, 177 MB), SVS 4893 `ShadowsMoonSouthPole_MASTER.mov`, SVS 3634 `LROC_1st_light.mp4`, SVS 5633 `mission_2160p30.mp4` (the only true 4K). If the owner sends them, the same strip/hash/proxy pipeline (`ffmpeg -an`) applies.
- **Partial workaround that does work:** some SVS products are mirrored on the NASA Image and Video Library (`images-assets.nasa.gov`, HTTP 200). Downloaded that way: Artemis II flyby visualisations (`lunarflyby_1min_2160p30`, `a2_flyby_1min_2160p30`; the files are named 2160p but are actually **1920x1080**), the Lee Lincoln LROC flyover, the PSR compilation, the VIPER south-pole tour. SVS 4944 itself is **not** on the library. The library copy of `mission_1min_2160p30` has the same byte sizes as `lunarflyby_1min_2160p30` so it was treated as a duplicate and not fetched.
- **Per-page credit and licence:** SVS 4944 page says "Please give credit for this item to: NASA's Scientific Visualization Studio"; SVS help page says content is public domain unless noted, and that licensed music (4944 and 4893 use Universal Production Music) is not public domain while the visualisation itself is. Third-party material: none stated on the 4944 page other than the music. Re-read each page at download time.

## 2. Plates table (downloaded files, best first)

Status: USE = clean as is; USE_WITH_CROP / USE_RANGES_ONLY / USE_LOW_LIGHT / USE_LABELLED = clean only with the stated crop, time ranges, lifting, or an honest on-screen label; MARGINAL = weak; REJECT = do not use. Kind: OBSERVED = camera data, DATA_VIS = rendered from measured data, ARTIST_CONCEPT. Scene numbers follow script-v3 (0 cold open window, 2 approach, 8/17/24/26 rim road, 9 rim wide, 21 Earth on the horizon, 27 inner wall in the dark, 29 bay nine, 30 limb and far side, WWR = What Was Real note).

| ID | Status | Kind | Resolution | Duration | Scenes | MB |
|---|---|---|---|---|---|---|
| GSFC_20190513_m4714_Lee_Lincoln_Sc | USE | DATA_VIS | 1920x1080 | 30 s | 8, 17, 24, 26 (rim-road wides as terrain stand-in), 29 | 43.0 |
| a2_flyby_1min_2160p30 | USE | DATA_VIS | 1920x1080 | 72 s | 0, 2 (Moon filling window on approach, 28-41 s), 30 (far sid | 44.9 |
| lunarflyby_1min_2160p30 | USE | DATA_VIS | 1920x1080 | 57 s | 0 (Moon in window, crop), 2 (approach), 30 (far side, limb), | 36.7 |
| GSFC_20171208_Archive_e001939 | USE | DATA_VIS | 1600x1600 | still | 30 (far side as a map-view insert), What Was Real | 2.0 |
| art002e009057 | USE | OBSERVED | 8256x5504 | still | 0, 2 | 1.0 |
| art002e009212 | USE | OBSERVED | 8256x5504 | still | 0, 2 (Moon in window), 30 | 2.0 |
| art002e009281 | USE | OBSERVED | 5568x3712 | still | 30 (far side below, terminator), 2 | 1.9 |
| art002e009282 | USE | OBSERVED | 5568x3712 | still | 27/29 (long-shadow relief), 30 | 2.1 |
| art002e009283 | USE | OBSERVED | 5568x3712 | still | 30 (far side below), 2 | 1.6 |
| art002e009284 | USE | OBSERVED | 5568x3712 | still | 30, 0 | 0.5 |
| art002e009285 | USE | OBSERVED | 5568x3712 | still | 30 | 1.0 |
| art002e009287 | USE | OBSERVED | 5568x3712 | still | 30, 21 | 1.2 |
| art002e009288 | USE | OBSERVED | 5568x3712 | still | 30, 21 | 0.9 |
| art002e009289 | USE | OBSERVED | 5568x3712 | still | 30 (limb with Earth sinking behind it; surface fills frame), | 2.3 |
| art002e012216 | USE | OBSERVED | 5568x3712 | still | 30 (far-side below), 2 | 1.7 |
| art002e012702 | USE | OBSERVED | 5568x3712 | still | 30 (far-side highlands) | 1.2 |
| art002e015231 | USE | OBSERVED | 8256x5504 | still | 30, 2 | 1.7 |
| art002e020922 | USE | OBSERVED | 5568x3712 | still | 30, 0 | 1.5 |
| art002e021007 | USE | OBSERVED | 5568x3712 | still | 21 (Earth low, wide), 30 | 0.9 |
| art002e021219 | USE | OBSERVED | 5568x3712 | still | 30 (Earthset), 21 | 1.8 |
| art002e021278 | USE | OBSERVED | 5568x3712 | still | 21 (Earth low on the lunar limb, wide), 30 (Earth sinking be | 1.0 |
| art002e021283 | USE | OBSERVED | 5568x3712 | still | 30 (Earth peeking over/under the limb), 21 | 1.2 |
| art002e021296 | USE | OBSERVED | 5568x3712 | still | 30 (dark limb with Earth glint) | 1.2 |
| as08-13-2329 | USE | OBSERVED | 5262x5122 | still | 21 (black-and-white variant) | 1.5 |
| as08-14-2383 | USE | OBSERVED | 3000x3000 | still | 21 (Earth low over lunar horizon, iconic), 30 (reverse) | 0.5 |
| as08-14-2384 | USE | OBSERVED | 4136x4136 | still | 21 | 0.7 |
| as17-152-23272 | USE | OBSERVED | 3000x3000 | still | 30 (crescent Earth behind a lunar slope), 21 | 1.5 |
| ART-DL-1_2022_325_1209_SHARED_art0 | USE_WITH_CROP | OBSERVED | 1280x720 | 1008 s | 30 (Earth with Moon limb; heavy crop and upscale needed) | 633.8 |
| art002e009280b | USE_WITH_CROP | OBSERVED | 5568x3712 | still | 30 (Earth as a thin crescent) | 0.5 |
| art002e015228 | USE_WITH_CROP | OBSERVED | 8256x5504 | still | 30 | 2.0 |
| ARC-20210920-AAV3366-VIPER-Landing | USE_RANGES_ONLY | DATA_VIS | 1920x1080 | 165 s | 2 (south-pole flyover feel), What Was Real | 322.7 |
| GSFC_20130306_Moons_m11218_Shadowe | USE_RANGES_ONLY | DATA_VIS | 1280x720 | 118 s | What Was Real (PSR visualisation), 27 (dark crater wall refe | 73.2 |
| art002m1200970119 | USE_LOW_LIGHT | OBSERVED | 1920x1080 | 130 s | 30 (dark far-side crossing), 27 (total-dark mood) | 731.1 |
| GSFC_20171208_Archive_e000496 | USE_LABELLED | COMPOSITE | 952x952 | still | 21 (Earth low over a lunar horizon, wide) | 0.6 |
| ART-CMA1_2022_325_1250_SHARED_art0 | MARGINAL | OBSERVED | 1280x1024 | 457 s | 30 cutaway (Earth as a dot) | 402.0 |
| ART-SAW4_2022_325_1305_SHARED_art0 | MARGINAL | OBSERVED | 1920x1080 | 142 s | none recommended | 186.2 |
| GSFC_20110617_LRO_m10794_Eclipse_L | MARGINAL | DATA_VIS | 1280x720 | 12 s | 0 (generic Moon in window) | 16.2 |
| GSFC_20110617_LRO_m10794_Eclipse_M | MARGINAL | DATA_VIS | 1280x720 | 60 s | 21 only if an eclipse beat is wanted | 84.2 |
| jsc2026m000089_Artemis II Moments  | MARGINAL | OBSERVED | 1920x1080 | 114 s | 30 (far side below), 2 | 290.3 |
| GSFC_20171208_Archive_e001129 | MARGINAL | OBSERVED | 700x700 | still | 21 (tiny Earth over the horizon, real LROC frame of 1 Feb 20 | 2.0 |
| PIA00001 | MARGINAL | DATA_VIS | 7943x7943 | still | What Was Real (south-pole map) | 6.6 |
| PIA13523 | MARGINAL | DATA_VIS | 1521x1521 | still | What Was Real (south-pole map) | 0.4 |
| as08-12-2188 | MARGINAL | OBSERVED | 3785x3785 | still | none (Earth is tiny) | 0.5 |
| ARC-20191025-AAV3232-VIPER-Animati | REJECT | ARTIST_CONCEPT | 1920x1080 | 88 s | none | 156.3 |
| BR__NOV_18_ORION_DOWNLINK_2022_322 | REJECT | OBSERVED | 1280x720 | 75 s | none | 149.8 |
| FD 19 Moon | REJECT | OBSERVED | 1920x1080 | 71 s | none | 42.3 |
| FD 20 3 | REJECT | OBSERVED | 1920x1080 | 237 s | none | 171.5 |
| Flight Day 14 | REJECT | OBSERVED | 1920x1080 | 340 s | none | 205.0 |
| GSFC_20080611_LRO_m10257_Return | REJECT | ARTIST_CONCEPT/INTERVI | 1280x720 | 202 s | none | 392.6 |
| GSFC_20171006_LRO_m12739_100LunarD | REJECT | DATA_VIS/EXPLAINER | 1920x1080 | 125 s | none | 222.3 |
| GSFC_20171006_LRO_m12739_100LunarD | REJECT | DATA_VIS/EXPLAINER | 1920x1080 | 189 s | none | 367.8 |
| GSFC_20190618_LRO_m13229_10Years | REJECT | OBSERVED | 1280x720 | 112 s | none | 210.0 |
| Moon Below Orion art001m1013251756 | REJECT | OBSERVED | 1920x1080 | 301 s | none | 37.6 |
| Moon_Base_Trailer-4K | REJECT | ARTIST_CONCEPT/PROMO | 1920x1080 | 79 s | none | 49.3 |
| art001m1013241924ART-DL-1_2022_324 | REJECT | OBSERVED | 1280x720 | 227 s | none | 453.3 |
| art002m1010962338_A | REJECT | OBSERVED | 1280x720 | 1187 s | none | 1038.7 |
| PIA12905 | REJECT | OBSERVED | 350x350 | still | none | 0.0 |
| art002e016299 | REJECT | OBSERVED | 4000x3000 | still | none | 0.5 |
| as8-14-2392 | REJECT | OBSERVED | 4077x4096 | still | none | 2.2 |

Detail for the video plates:

- **GSFC_20190513_m4714_Lee_Lincoln_Scarp_Moon_Flyover** (USE, DATA_VIS): ranges: 0-30 s all clean; 12-30 s is a low oblique run across a lunar plain toward a ridge (best ground-feel) Crop/text/logos: none; text: no; logos: no. Taurus-Littrow valley (Apollo 17 site), NOT the south pole. Label honestly as a lunar terrain visualisation; no black south-pole shadows.
- **a2_flyby_1min_2160p30** (USE, DATA_VIS): ranges: 0-72 s; Moon grows 2-38 s and fills the frame 34-41 s (far side fully lit); recedes 41-72 s Crop/text/logos: none; text: no; logos: no. Library file named 2160p30 but is 1920x1080. Simulated, not observed.
- **lunarflyby_1min_2160p30** (USE, DATA_VIS): ranges: 0-57 s whole clip; Moon growing/rotating 0-30 s; far-side crescent 30-45 s; Earth dot appears ~46-50 s Crop/text/logos: none (Moon only; Earth is a 3-px dot at ~48 s); text: no; logos: no. Rendered from LRO data (Artemis II flyby simulation). Library file is named 2160p30 but is 1920x1080. Label as visualisation on screen.
- **ART-DL-1_2022_325_1209_SHARED_art001m1013251209** (USE_WITH_CROP, OBSERVED): ranges: Whole 1008 s is near-static; best 560-1008 s (Earth dot nearest the limb, Moon larger). Use 10-30 s sub-clips. Crop/text/logos: Crop to the right 60% of frame (x >= 0.38 W) to remove spacecraft hardware; Earth is a tiny dot (~8 px) low in frame, crosses toward the Moon limb late in the clip; text: no; logos: no logo visible; Orion service-module hardware fills the left ~35% of frame. Only 1280x720. Earth too small for a hero shot; better as texture of real camera motion. For Earthset hero shots use the Artemis II stills.
- **ARC-20210920-AAV3366-VIPER-LandingSiteAnnouncement-YouTubeHD** (USE_RANGES_ONLY, DATA_VIS (with ARTIST_CONCEPT rover renders 54-91 s)): ranges: 4-13 s (Moon turning to the south pole, clean), 20-28 s (south-pole terrain, very faint polar graticule), 136-152 s (low oblique shadowed terrain, clean, ends on Moon). Avoid 14-19 s ('South Pole' label), 29-40, 54-135, 154-165. Crop/text/logos: Use only clean ranges; text: yes: 'South Pole' label 14-19 s, 'NOBILE CRATER' ~37 s, 'Nobile Region' ~95 s, pink outline overlays 104-130 s; logos: VIPER logo 29-33 s; Artemis logo 160-165 s. Audio carries licensed music (Universal Production Music, stripped). Insets 79-91 s show a render of Earth low over the lunar horizon but with the VIPER rover and overlays; not usable as a plate.
- **GSFC_20130306_Moons_m11218_Shadowed** (USE_RANGES_ONLY, DATA_VIS): ranges: 9-14 s (Moon), 42-48 s (crater interior in shadow), 91-97 s (crater shadow), 105-108 s (Moon). Avoid 0-6, 51-90, 111-118. Crop/text/logos: Use only clean ranges; text: yes: title card 0-6 s, 'LOLA Topography' ~51-66 s, 'LAMP Starlight' ~69 s, labels 75-87 s; logos: NASA Goddard end card 111-118 s; LRO spacecraft renders. Original audio narration stripped. Contains LRO spacecraft render (NASA hardware, no logo seen).
- **art002m1200970119** (USE_LOW_LIGHT, OBSERVED): ranges: 0-130 s (Moon's dark disc with a faint limb glow, spacecraft behind the Moon during eclipse) Crop/text/logos: none; very dark and noisy, lift exposure and denoise; text: no; logos: no. 1920x1080 29.97 fps, 731 MB master. Real observation; limb glow is real (eclipse corona/earthshine).
- **ART-CMA1_2022_325_1250_SHARED_art001m1203251250** (MARGINAL, OBSERVED): ranges: 58-457 s: black sky with Earth as a ~4-px blue dot Crop/text/logos: Frame is 1280x1024 with grey side bars; crop to the central 960-px band; text: no; logos: no. Titled 'Earthrise' but the Earth is a dot and the Moon is not in frame. Low value.
- **ART-SAW4_2022_325_1305_SHARED_art001m1203251305** (MARGINAL, OBSERVED): ranges: 0-142 s Crop/text/logos: No clean crop: array crosses the frame above the Earth; text: no; logos: no logo visible; Orion hardware and solar array cross the frame. Real Earth disc but with spacecraft hardware; cannot be used as a plain Earth plate.
- **GSFC_20110617_LRO_m10794_Eclipse_Librating_Moon** (MARGINAL, DATA_VIS): ranges: 0-12 s (phases/libration, Moon disc, 720p) Crop/text/logos: none; text: no; logos: no. Low resolution 1280x720.
- **GSFC_20110617_LRO_m10794_Eclipse_Moonview** (MARGINAL, DATA_VIS): ranges: 44-60 s (lunar horizon with Sun beside a DARK Earth disc) Crop/text/logos: none; text: tiny 'LRO' label ~26-30 s; logos: no. Shows Earth eclipsing the Sun (dark Earth), not a normal lit Earth. Not a plate for the quiet Earth-low scene.
- **jsc2026m000089_Artemis II Moments Around the Moon_1080p_AVAIL** (MARGINAL, OBSERVED (crew-cam and Orion footage in a recap edit)): ranges: approx 56.5-58.5 s (half-lit Moon disc, clean) and 60-62.5 s (grazing-light oblique terrain, clean); verify boundaries by eye. Everything else has people, text or logos. Crop/text/logos: Use only the two short Moon-only passages; text: yes: burned-in MET banners (e.g. 0-55 s); logos: NASA 'worm' logo on capsule 74-76 s; mission-elapsed-time graphic. 1920x1080 59.94 fps. Do not use whole clip: identifiable astronauts (likeness rules) and logos.

Rejects (kept in `plates/rejected/` for audit): ARC-20191025-AAV3232-VIPER-Animation-NAS - ARTIST_CONCEPT animation of the VIPER rover (a real NASA design; look-alike risk).; BR__NOV_18_ORION_DOWNLINK_2022_322_1229_ - Orion capsule with NASA logo and solar array dominate frame.; FD 19 Moon - Orion capsule with NASA 'worm' logo in frame; Moon a small disc.; FD 20 3 - Heavy lens flare, spacecraft edge in frame; crescent Earth is a pink smear.; Flight Day 14 - Orion capsule with NASA 'worm' logo in frame.; GSFC_20080611_LRO_m10257_Return - Interview and CGI astronaut with a face; text slides.; GSFC_20171006_LRO_m12739_100LunarDays_Pt - Explainer with text, graphics, narration.; GSFC_20171006_LRO_m12739_100LunarDays_Pt - Explainer with text, LRO spacecraft render, white infographics.; GSFC_20190618_LRO_m13229_10Years - Explainer: people, control room, launch pad, burned-in text.; Moon Below Orion art001m1013251756 - Orion hardware dominates the frame; Moon a tiny crescent; dim.; Moon_Base_Trailer-4K - Promotional trailer: burned-in text, astronauts/people, NASA logos, composited/artist content. 1920x1080 'large' copy fetched only to classify.; art001m1013241924ART-DL-1_2022_324_1924_ - Orion capsule with NASA 'worm' logo; blown-out exposure.; art002m1010962338_A - Solar-array camera pointing at the Sun: heavy glare, Orion hardware at left edge, blue no-signal frames at 266-442 s. 1187 s, 1280x720. Not usable.; PIA12905 - 350x350 only; the library caption describes Timocharis crater, not the south pole: mislabelled; rejected.; art002e016299 - Hardware with insignia in frame; Earth tiny.; as8-14-2392 - High oblique Earthrise with a spacecraft window/hardware edge and red band at the bottom-left.

## 3. Best five and what they serve

1. **Artemis II Earthset stills** (`art002e021278`, `art002e009289`, `art002e021283`, `art002e021219`, `art002e021007`): real Earth on the curved lunar limb from the far side, up to 5568x3712. Scenes 21 (Earth low on the horizon; orbital vantage) and 30 (Earth sinking behind the limb). These are the only real, photoreal 'Earth meets lunar horizon' plates available.
2. **Artemis II terminator and far-side stills** (`art002e009282` Vavilov, `art002e009283`, `art002e012216`, `art002e009281`): hard long shadows and cratered far side for the 'grey far side below' and as light/shadow reference for the rim.
3. **AAV3366 VIPER tour, clean ranges 4-13 s, 20-28 s, 136-152 s** (DATA_VIS): the only moving south-pole flyover we hold (real LOLA/LROC data); scene 2 and the end note. Needs ranges cut around labels. Hybrid with artist-concept rover renders elsewhere in the clip.
4. **a2_flyby / lunarflyby** (DATA_VIS, 1080p): the Moon growing to fill the frame then receding, far-side lit, plus a far-side crescent and Earth point: scenes 0, 2 (Moon filling the window), 30.
5. **Lee Lincoln scarp flyover** (DATA_VIS): the closest thing to a low surface-level rim-road plate (scenes 8, 17, 24, 26), honestly labelled as lunar terrain (Taurus-Littrow), not Shackleton.

Also: Apollo 8 AS08-14-2383/2384 and Apollo 17 AS17-152-23272 for a classic Earth-over-horizon beat; ESO Milky Way panorama for star fields.

## 4. Gaps: wanted by the script, not available as real footage

| Script wants | Reality | Best honest substitute |
|---|---|---|
| Ground-level view along the Shackleton rim (scenes 8, 9, 17, 24, 26, 29) | No camera has ever been on the south-pole surface | Lee Lincoln scarp flyover (DATA_VIS, wrong site, label as terrain visualisation); VIPER tour 136-152 s low oblique terrain (DATA_VIS); composite our own characters/vehicles over these; or render a LOLA-based scene in Blender from SVS 4720 CGI Moon Kit (needs owner download) |
| Inside of Shackleton in visible light (scenes 26-27, WWR) | Floor is permanently shadowed; no visible-light images exist | Black frame plus headlamp composite for the scene (the script already plays it as black); for WWR, the PSR visualisation 42-48 s and 91-97 s of the Shadowed Regions clip (DATA_VIS, labelled) |
| South-pole flyover with Earth low on the horizon (SVS 4944) | Not downloadable here (403); not in the NASA library | Owner fetches SVS 4944; until then AAV3366 ranges plus an Artemis II Earthset still composited on the horizon |
| Earth low on the lunar horizon from the surface (scene 21) | Only seen from orbit (Apollo 8/17, Artemis I/II); no surface-level photos from a near-pole site | Artemis II Earthset stills and Apollo 8 Earthrise, with an on-screen note that the vantage is orbital; DATA_VIS inset in AAV3366 (79-91 s) has Earth over a horizon but with a rover |
| Earth sinking behind the limb as a moving shot (scene 30) | Artemis II stills are single frames; Artemis I video has Earth as a few pixels with hardware in frame | Animate a slow push/drift on `art002e009289` and `art002e021278` (Ken Burns, with a sequence of Earthset stills 009287 > 021283 > 021219 > 009289 as a time-lapse), or use ART-DL-1 cropped (Earth a dot) |
| Moon filling a cockpit window on approach (scene 0, 2) | Real Orion-window video is not in the library in clean form (recap reels carry people/logos) | a2_flyby 28-41 s and lunarflyby (DATA_VIS), or `art002e009212`/`009057` full-Moon stills composited behind a window; label as visualisation where it is |
| Grey far side below (scene 30) | Real photos exist | Artemis II far-side stills (OBSERVED) are fine; no moving real far-side footage in clean form |
| Shadowed-region visualisation for the end note | Exists | Shadowed Regions clip (clean ranges), PIA13523 polar mosaic; SVS 4893/4043 would be better (pending download) |
| Stars at 4K | Photographic star fields exist | ESO Milky Way panorama (6000x3000); more ESO/Webb stills available on request |
| LROC oblique of Shackleton and rim | Exists (LROC NAC mosaic 0.8 m/px in SVS 3634) but SVS blocked; LROC site not searched successfully (lroc.im-ldi.com search 404) | Owner fetch of SVS 3634; PIA13523 meanwhile |

## 5. Rights notes (unclear or needing a human decision)

- NASA media is generally not copyrighted (quote and URL in the JSON). Commercial use must not imply NASA endorsement; **no NASA worm/meatball logo on fictional things.** Orion hardware carrying the worm logo is why many Artemis I videos were rejected.
- Artemis I/II Orion-camera and crew-photo credits in the library carry no named photographer: they are credited "NASA" (the stills say "Credit: NASA"). I did not find a stated 'third-party material' warning on those library pages, but I read only metadata, not every page.
- The NASA Library's still JPEGs are small in bytes (1-2 MB for 5568x3712 / 8256x5504): resolution is full but compression is heavy. Higher-quality originals may exist on the NASA JSC Gateway to Astronaut Photography; not checked.
- `GSFC_20171208_Archive_e000496` (LRO Earthrise) is a composite (Earth inserted); it must not be described as a single photograph. Credit includes Arizona State University (LROC): public NASA release, still worth a glance at the LROC terms.
- `PIA12905` caption does not match its title (describes Timocharis): rejected as mislabelled.
- Artemis II crew faces appear only in the recap reel and are excluded.
- Visualisation audio (SVS music by Universal Production Music) is stripped; nothing of it is kept.
- Libraries named files "2160p30" that are actually 1080p: do not promise 4K.
- Hubble/ESO: only the ESO Milky Way panorama is used; CC BY 4.0 needs a visible credit.
- YouTube's altered/synthetic disclosure applies to the episode (the script already notes this).

## 6. Draft credits block (episode description, and a shorter version for the end note)

**Description block (draft, pending owner sign-off):**

Real space imagery in this episode:
- Moon and Earth photographs from the Artemis II mission (6 April 2026): NASA.
- Apollo 8 and Apollo 17 lunar-orbit photographs: NASA.
- Lunar visualisations built from Lunar Reconnaissance Orbiter data (LRO, LOLA, LROC): NASA's Scientific Visualization Studio; Ernie Wright; David Ladd; Tom Waters; Dan Gallagher; Chris Smith; NASA Goddard Space Flight Center.
- South-polar terrain tour: NASA's Scientific Visualization Studio.
- Moon and Earth images from the Lunar Reconnaissance Orbiter Camera: NASA/Goddard/Arizona State University.
- Milky Way panorama: ESO/S. Brunier (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/).
- Artemis I Orion camera footage: NASA.
All NASA material is used under NASA's media guidelines; NASA does not endorse this production. The characters, story and score are fiction. Lunar surface views of the south pole are visualisations from measured data, not photographs.

**End-note (WWR) small-print version:** "Imagery: NASA (Artemis I, II; Apollo 8, 17; LRO/LROC/LOLA; Scientific Visualization Studio) and ESO/S. Brunier (CC BY 4.0). Surface views are data visualisations. Not endorsed by NASA or ESO."

Add per-plate credits only for the plates actually used in the cut: the `credit_line` field in the JSON is the exact wording.
