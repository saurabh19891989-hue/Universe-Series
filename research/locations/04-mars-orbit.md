# 04 - Mars - Valles Marineris and Olympus Mons from orbit

**Verdict: ADEQUATE**

Verified items are thin: Curiosity/Mars explainers, Hubble Mars clips, and MRO stills. The real orbital flyovers (ESA Mars Express Valles Marineris / Olympus Mons; NASA MOLA flyovers SVS 3896, 1335) exist per the SVS and Commons APIs, but could not be confirmed from here (403 / 429). ESA Mars Express clips on Commons are 720x720 or 1080x1080 social-format squares.

## What real footage exists

- 30 assets catalogued (13 verified with HTTP 200 on HEAD/range; 17 unverified), of which 23 are videos and 7 are stills.
- Kinds: OBSERVED 13, DATA_VIS 11, ARTIST_CONCEPT 6 (kind is a metadata heuristic; confirm by viewing).
- Verified moving footage with a stated duration (excluding artist concept): **4.9 minutes** across 6 videos (1 verified videos have no stated duration, so the true total is higher). This includes narrated explainers; usable silent minutes are lower, and long compilations (e.g. ISS 4K) dominate where present.

## Best 10 assets

| # | Title | Source | Kind | Res | Dur | Size MB | Verified | Link |
|---|---|---|---|---|---|---|---|---|
| 1 | NASA’s Curiosity Rover Finds New Clues to Mars’ Watery Past | NASA Image and Video Library | OBSERVED | 3840x2160 | 190s | 1849.8 | yes | [page](https://images.nasa.gov/details/JPL-20230208-MSLf-0001-Curiosity_Finds_New_Clues_to_Mars_Watery_Past) |
| 2 | InSight Captures Sound of a Meteoroid Striking Mars | NASA Image and Video Library | OBSERVED | unknown | - | 293.2 | yes | [page](https://images.nasa.gov/details/JPL-20220919-INSIGHf-0001-InSight%20Captures%20Sound%20of%20a%20Meteoroid%20Striking%20Mars_1080) |
| 3 | The surface and the moons of Mars | ESA/Hubble video archive | DATA_VIS | 1920x1080 (p | 30s | 16.1 | yes | [page](https://esahubble.org/videos/heic1814d/) |
| 4 | Animation of difference in Mars orientation, 2016 and 2018 | ESA/Hubble video archive | DATA_VIS | 1920x1080 (p | 30s | 30.3 | yes | [page](https://esahubble.org/videos/heic1814e/) |
| 5 | Flight over craters and canyons on Mars | ESA/Hubble video archive | DATA_VIS | 1920x1080 (p | 30s | 25.7 | yes | [page](https://esahubble.org/videos/astro_o/) |
| 6 | Mars 360 degree rotation | ESA/Hubble video archive | DATA_VIS | 1920x1080 (p | 16s | 0.5 | yes | [page](https://esahubble.org/videos/astro_n/) |
| 7 | Layers within the Valles Marineris: Clues to the Ancient Crust of Mars | NASA Image and Video Library | OBSERVED | 3500x2000 | - | 1.0 | yes | [page](https://images.nasa.gov/details/PIA01167) |
| 8 | Regions of Mars with Clays and Hydrated Minerals Identified from Orbit | NASA Image and Video Library | OBSERVED | 2999x1515 | - | 0.6 | yes | [page](https://images.nasa.gov/details/PIA13703) |
| 9 | Artist's concept of the surface of Mars | ESA/Hubble video archive | ARTIST_CONCEPT | 1920x1080 (p | 30s | 25.7 | yes | [page](https://esahubble.org/videos/hubblecast27d/) |
| 10 | Base on Mars  (artist's impression) | ESA/Hubble video archive | ARTIST_CONCEPT | 1920x1080 (p | 19s | 16.1 | yes | [page](https://esahubble.org/videos/astro_az/) |

Full list with download URLs, credit lines and licence text: `/home/user/Universe-Series/assets/candidates.json` (filter `location` = 4).

## Gaps (must be illustrated, not shown for real)

- Verified, silent, high-resolution Valles Marineris / Olympus Mons flyover video: found only as unverified SVS or low-res Commons squares.
- True-colour oblique views: most flyovers are DEM-draped visualisations, not camera video.

## Three physical facts that could drive a story problem

- Olympus Mons is 23 km high versus Mauna Loa's 10 km measured from the ocean floor, despite Mars being half Earth's size. Source: https://svs.gsfc.nasa.gov/2864/
- Mars has a radius of 3,390 km (about half Earth's), a dusty cold desert with a very thin atmosphere. Source: https://science.nasa.gov/mars/facts/
- MGS/MOLA topography shows Olympus Mons, Valles Marineris, Hellas Basin and both poles as the major features. Source: https://svs.gsfc.nasa.gov/3896/

## Licence cautions for this location

- Sources used: ESA/Hubble video archive; NASA Image and Video Library; NASA SVS; Wikimedia Commons mirror of agency media. See `00-summary.md` for the licence table and quotes.
- NASA SVS entries are UNVERIFIED: the media host returned HTTP 403 to HEAD/Range from this sandbox. Sizes are API-stated. Visualisations are public domain, but accompanying music (Universal Production Music, Killer Tracks) is not.
- Commons-mirrored entries were NOT verifiable (upload.wikimedia.org returned 429 with retry-after 600 s repeatedly) except where marked verified. Licence tags (public domain / CC BY / CC BY-SA / GODL-India) come from the Commons API; CC BY-SA requires share-alike and attribution.
