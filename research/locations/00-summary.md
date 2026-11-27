# SECRET UNIVERSE - Season 1 asset research summary

Generated from real API/page responses in one research session (NASA Image and Video Library API, NASA SVS API, ESA/Hubble, ESA/Webb and ESO archives, Wikimedia Commons API). Catalogue: `/home/user/Universe-Series/assets/candidates.json`. Nothing was downloaded beyond headers/first byte.

**Totals: 376 assets catalogued, 288 verified (HTTP 200/206 on HEAD or 1-byte range), 88 unverified.**

## Locations

| # | Location | Assets | Verified | Videos | Verified minutes (stated durations) | Verdict |
|---|---|---|---|---|---|---|
| 1 | [Moon - Shackleton crater / south pole](01-moon-south-pole.md) | 30 | 14 | 25 | 12.7 (+2 videos w/o duration) | ADEQUATE |
| 2 | [Moon - far side and Earthrise](02-moon-farside-earthrise.md) | 30 | 25 | 22 | 58.0 (+3 videos w/o duration) | RICH |
| 3 | [Earth from orbit and Earth-Moon space](03-earth-orbit.md) | 30 | 25 | 24 | 193.0 (+1 videos w/o duration) | RICH |
| 4 | [Mars - Valles Marineris and Olympus Mons from orbit](04-mars-orbit.md) | 30 | 13 | 23 | 4.9 (+1 videos w/o duration) | ADEQUATE |
| 5 | [Mars - surface](05-mars-surface.md) | 30 | 25 | 21 | 16.2 (+9 videos w/o duration) | RICH |
| 6 | [Phobos and Deimos](06-phobos-deimos.md) | 14 | 4 | 12 | 0.3 (+0 videos w/o duration) | THIN |
| 7 | [Venus](07-venus.md) | 28 | 12 | 19 | 7.7 (+0 videos w/o duration) | THIN |
| 8 | [Mercury and the Sun](08-mercury-sun.md) | 30 | 30 | 28 | 68.0 (+0 videos w/o duration) | RICH |
| 9 | [Asteroid belt and small bodies](09-small-bodies.md) | 30 | 30 | 30 | 103.9 (+0 videos w/o duration) | RICH |
| 10 | [Jupiter](10-jupiter.md) | 30 | 30 | 27 | 20.3 (+2 videos w/o duration) | ADEQUATE |
| 11 | [Io](11-io.md) | 5 | 3 | 2 | 0.0 (+0 videos w/o duration) | THIN |
| 12 | [Europa and Ganymede](12-europa-ganymede.md) | 29 | 17 | 20 | 3.3 (+4 videos w/o duration) | THIN |
| 13 | [Saturn, rings, Titan, Enceladus](13-saturn-system.md) | 30 | 30 | 29 | 48.2 (+1 videos w/o duration) | ADEQUATE |
| 14 | [Generic deep-space plates](14-deep-space.md) | 30 | 30 | 30 | 95.4 (+0 videos w/o duration) | RICH |

Minutes count verified, non-concept video with a stated duration and include narrated explainers and long compilations; they are an upper bound on 'clean' footage. Asset counts are capped at 30 per location by the selection step (many more candidate rows exist in the scratch data for ESA/ESO/NASA sources).

## Licence rules per source

| Source | Licence / terms | Key sentence (with URL) | Traps |
|---|---|---|---|
| NASA Image and Video Library, JPL Photojournal (PIA), SVS | Generally not copyrighted (US); commercial use allowed without implying endorsement | "NASA content - images, audio, video, and media files ... generally are not subject to copyright in the United States." and "If the NASA material is to be used for commercial purposes, including advertisements, it must not explicitly or implicitly convey NASA's endorsement of commercial goods or services." https://www.nasa.gov/nasa-brand-center/images-and-media/ | NASA logo/insignia; identifiable persons ("using the media for commercial purposes may infringe that person's right of privacy or publicity"; current NASA astronauts' likeness banned on commercial products); third-party material "marked identified as copyright protected"; video soundtracks/music |
| NASA SVS | Public domain unless noted | "All of our content is in the public domain (unless otherwise noted)... some of our visualizations feature licensed music, which is not in the public domain." https://svs.gsfc.nasa.gov/help/ | Music/narration tracks (Universal Production Music, Killer Tracks): strip audio. Media files returned 403 from this sandbox, so unverified |
| ESA/Hubble | CC BY 4.0 | "ESA/Hubble images, videos and web texts are released under the Creative Commons Attribution 4.0 International license and may on a non-exclusive basis be reproduced without fee provided they are clearly and visibly credited." https://esahubble.org/copyright/ | Full credit line mandatory; music and scientific papers are NOT CC BY ("can not be used for non-ESA/Hubble products"); items credited to others (e.g. ESO, Digitized Sky Survey, Robert Gendler) may have their own terms |
| ESA/Webb | CC BY 4.0 | Same sentence with 'ESA/Webb'. https://esawebb.org/copyright/ | Same: music excluded; credit visible |
| ESO | CC BY 4.0 | "...licensed under a Creative Commons Attribution 4.0 International License, and may on a non-exclusive basis be reproduced without fee provided the credit is clear and visible." https://www.eso.org/public/outreach/copyright/ | Music (other than the Music Archive) not covered; 2004 transit-of-Venus pages carry owners' copyright; ESOcasts are narrated |
| esa.int (general ESA website) | NON-commercial by default | "The contents of the ESA website are intended for the personal and non-commercial use of its users... ESA does not grant the right to resell or redistribute any information, documents, images or material from its website or to compile or create derivative works." https://www.esa.int/terms-and-conditions | Per-item CC BY-SA 3.0 IGO tags exist on some multimedia but could not be confirmed on esa.int in this session; do NOT use esa.int Mars Express/Rosetta/Gaia video without per-item check. Commons-hosted ESA items show their own tag |
| Wikimedia Commons mirrors | Per-file tag (public domain, CC BY, CC BY-SA, GODL-India) | Licence tag read from the Commons API (LicenseShortName) | CC BY-SA = share-alike; Commons tag is a secondary source, re-check agency page; throttled 429 here |
| JunoCam / citizen-processed (missionjuno.swri.edu) | No licence stated | Page says only: "We invite you to download raw JunoCam images posted here and do your own image processing on them" and asks users to avoid official NASA/Juno logos. https://www.missionjuno.swri.edu/junocam/processing | Citizen products are credited "NASA/JPL-Caltech/SwRI/MSSS/<name>" but no reuse terms are given for the processor's work: treat as unclear, use raw/official NASA PIA releases instead |
| JAXA | Copyright JAXA; commercial use needs permission | "Your use of the Materials for business or commercial purposes without the prior permission of the copyright holder (JAXA) is strictly prohibited." https://global.jaxa.jp/policy.html | Monetised YouTube probably counts as commercial: do not use Akatsuki/Hayabusa2/Kaguya material without written permission |
| ISRO | Not confirmed | ISRO policy page could not be retrieved (isro.gov.in Policies path returned nothing usable). One Chandrayaan-2 clip on Commons is tagged GODL-India (Government Open Data License, attribution, commercial use allowed) | Treat as unchecked until the licence page is read |
| USGS Astrogeology | Not checked | astrogeology.usgs.gov returned HTTP 403 to this sandbox | Unchecked; USGS is generally public domain but verify |
| JPL image-use policy page | Not retrievable | jpl.nasa.gov/image-policy returned 403/404; PIA images were treated under the NASA guidelines above | Check PIA caption for 'courtesy of' third parties (e.g. University of Arizona HiRISE credits) |

## 20 most spectacular assets overall

| # | Asset | Location | Source | Kind | Res | Link |
|---|---|---|---|---|---|---|
| 1 | How did the Earth form? | 3 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/cs0012a/) |
| 2 | Strangest stars | 14 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/cs0007a/) |
| 3 | Come to the Dark Side, we have stars | 14 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/cs0008a/) |
| 4 | Does the Milky Way central black hole rotate? This star could tell us | 14 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/eso2612a/) |
| 5 | OSIRIS-REx Mission Arrives at Asteroid Bennu | 9 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20181203_Arrival_m12166_Bennu) |
| 6 | A Web Around Asteroid Bennu | 9 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20210510_M13856_Web) |
| 7 | Asteroid Bennu: Selecting Site Nightingale | 9 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20200227_M13565_Nightingale) |
| 8 | Perseverance Explores the Jezero Crater Delta | 5 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/JPL-20220906-Perseverance_Explores_Jezero_Crater_Delta_UHD) |
| 9 | Welcome to the Ionosphere | 3 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20171107_Ionosphere_m12532_ICON) |
| 10 | Curiosity Explores Gediz Vallis Channel 360 | 5 | NASA Image and Video Libra | OBSERVED | 7680x4320 | [page](https://images.nasa.gov/details/JPL-20240717-MSLf-0001-Curiosity_Explores_Gediz_Vallis_360_View_8k) |
| 11 | Space Sparks Episode 11: Webb celebrates first year of science with cl | 8 | ESA/Webb video archive | OBSERVED | 3840x2160 (u | [page](https://esawebb.org/videos/weic2316a/) |
| 12 | The Earth in 4k | 3 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/earth_2015_4k/) |
| 13 | NASA’s Curiosity Rover Reaches Gediz Vallis Channel (360 View) | 5 | NASA Image and Video Libra | OBSERVED | 7680x4320 | [page](https://images.nasa.gov/details/JPL-20240329-MSLf-0001-Curiosity_Reaches_Gediz_Vallis_Channel_360_8k) |
| 14 | Artemis II Moon Watch - Emily Kollin | 2 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/jsc2026m000094_Artemis-II_Moon_Watch-Emily_Kollin) |
| 15 | 2016 Mercury Transit in 4K | 8 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20160601_Mercury_m12268_Transit_4K) |
| 16 | NASA’s SDO Captures Stunning 4K View of April 17 Solar Flare | 8 | NASA Image and Video Libra | OBSERVED | 3840x2160 | [page](https://images.nasa.gov/details/GSFC_20160426_SDO_m12224_SolarFlare_4K) |
| 17 | Jupiter’s clouds are not made of ammonia ice | 10 | ESO video archive | OBSERVED | 3840x2160 (u | [page](https://www.eso.org/public/videos/potw2502a/) |
| 18 | Moving features on Jupiter | 10 | ESA/Hubble video archive | OBSERVED | 3840x2160 (u | [page](https://esahubble.org/videos/heic1522b/) |
| 19 | Pullout of aurora observations on Jupiter | 10 | ESA/Webb video archive | OBSERVED | 3840x2160 (u | [page](https://esawebb.org/videos/weic2510a/) |
| 20 | Saturn (2024 Hubble and Webb images, clean) | 13 | ESA/Webb video archive | OBSERVED | 3840x2160 (u | [page](https://esawebb.org/videos/weic2606a/) |

Wow factor is my metadata-based estimate (resolution, real vs. visualisation, narration penalty); no thumbnails were reviewed visually.

## What could not be checked

- NASA SVS media files: HTTP 403 for every /vis/ URL tested (HEAD and 1-byte Range, several user agents). SVS entries are therefore unverified, including the key lunar-pole and Mars flyovers.
- Wikimedia Commons file downloads: 429 (retry-after 600 s) throughout the later part of the session; only a handful of files verified.
- ISRO, USGS Astrogeology, JPL image policy page, JAXA digital archive item pages, esa.int per-item licences (esa.int multimedia pages could not be searched).
- No video was played or thumbnail inspected: `kind`, `has_audio_or_music` and `wow_factor` are heuristics from metadata; confirm by viewing.
- Resolution for NASA library items comes from the metadata.json where present; ESA/ESO resolutions are inferred from the format folder name (ultra_hd = 3840x2160, hd_1080p = 1920x1080).
