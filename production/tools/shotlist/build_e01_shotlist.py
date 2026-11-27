#!/usr/bin/env python3
"""Builds episodes/E01/shotlist.json (+ stats JSON for the summary) from compact shot definitions.
Line ids: E01-L### = 1-based data-row number in samples/tableread/E01/lines.csv."""
import csv, json, os, sys
from collections import OrderedDict, Counter, defaultdict

ROOT = "/home/user/Universe-Series"
LINES = list(csv.DictReader(open(f"{ROOT}/samples/tableread/E01/lines.csv", encoding="utf-8")))
CANDS = {x["id"]: x for x in json.load(open(f"{ROOT}/assets/candidates.json"))}

SPK = {"JAX": "jax", "MIRA": "mira", "LUCÍA": "lucia", "BARON": "baron", "PIP": "pip",
       "CHICHIKOV": "chichikov", "NOAKES": "noakes", "TEMI": "temi", "MAMANI": "mamani"}
GAP = 0.5      # planned pause between lines inside a shot (TTS read ran ~0.2-0.4 s)
PAD = 0.6      # lead-in + tail breath per shot that carries dialogue

STYLE = ("Photorealistic cinematic film still, 35mm, shallow depth of field, practical lighting, natural skin "
         "texture, muted teal-and-amber grade, worn practical costumes, no logos, no readable text, looks like a "
         "frame from a live-action science fiction film, not an illustration, not CGI.")
HOUSE = ("Every window or viewport is pure black (real footage is inserted later). All screens, tags, labels, "
         "signs, cards and papers are blank or illegible (text is added later).")

LOCK = {
 "jax": "Jax Vale: Mediterranean Greek man, late 30s, olive skin, dark curly hair greying slightly at the temples, stubble, weathered face, crooked half-smile; scuffed burnt-orange flight jacket with too many pockets.",
 "mira": "Dr Mira Sen: Bengali Indian woman, mid-30s (she must look 34, not older), dark braid, sharp tired eyes, ink-stained fingers; indigo customs flight suit, brass loupe on a chain.",
 "lucia": "Lucía Ortega: Mexican woman, early 30s (she must look 31, not older), strong athletic build, broad shoulders, short practical hair; grease-stained coveralls, a red ribbon tied round her wrist.",
 "baron": "Baron Munchausen: German man in his 70s, enormous white moustache that completely covers his mouth, black tricorn hat; moth-eaten red 18th-century cavalry coat over a patched pressure suit. Design after Doré's 1862 engravings, never any film.",
 "chichikov": "Pavel Chichikov: Russian man, 45, round pleasant forgettable face, neither handsome nor plain; good grey overcoat, grey gloves, a small inlaid wooden travelling box.",
 "noakes": "Superintendent Noakes: English man, 55, tired; customs uniform without real insignia.",
 "temi": "Temi Adeyemi: Nigerian woman in a headset, bright, mid-smile, bank call-centre desk.",
 "mamani": "Officer Inti Mamani: Andean man, kind, tired, port control desk.",
 "pip": "PIP: small brass-and-cream machine like a desk lamp crossed with a postal scale, one glowing amber lens, a rubber-stamp arm; photographed as a real practical object.",
}

# ---------------------------------------------------------------- reference library
# status: EXISTS (in git now) / PLANNED (library agent is building it) / GAP (not on the library agent's list)
REF = OrderedDict()
def ref(key, path, label, status):
    REF[key] = dict(path=path, label=label, status=status)
C = "assets/characters/"
ref("jax", C+"jax/master.jpg", "Jax Vale", "EXISTS")
ref("jaxC", C+"jax/ref-closeup.jpg", "Jax Vale close-up", "EXISTS")
ref("jaxP", C+"jax/ref-profile.jpg", "Jax Vale profile", "EXISTS")
ref("jaxH", C+"jax/ref-helmet.jpg", "Jax Vale in pressure suit and helmet", "EXISTS")
ref("jaxL", C+"jax/ref-laugh.jpg", "Jax Vale laughing", "EXISTS")
ref("mira", C+"mira/master.jpg", "Dr Mira Sen", "PLANNED")
ref("miraS", C+"mira/ref-suit-helmet.jpg", "Dr Mira Sen in customs pressure suit and helmet", "GAP")
ref("lucia", C+"lucia/master.jpg", "Lucía Ortega", "PLANNED")
ref("luciaS", C+"lucia/ref-suit-helmet.jpg", "Lucía Ortega in pressure suit and helmet", "GAP")
ref("baron", C+"baron/master.jpg", "the Baron", "EXISTS")
ref("baronS", C+"baron/ref-fullbody-suit.jpg", "the Baron full body in pressure suit", "EXISTS")
ref("baronL", C+"baron/ref-laugh.jpg", "the Baron laughing", "EXISTS")
ref("baronHT", C+"baron/ref-helmet-tricorn.jpg", "the Baron in helmet with his tricorn strapped on top", "GAP")
ref("chich", C+"chichikov/master.jpg", "Chichikov", "EXISTS")
ref("noakes", C+"noakes/master.jpg", "Superintendent Noakes", "PLANNED")
ref("temi", C+"temi/master.jpg", "Temi Adeyemi", "PLANNED")
ref("mamani", C+"mamani/master.jpg", "Officer Mamani", "PLANNED")
S = "assets/sets/"
ref("bridge", S+"bridge/master.jpg", "the bridge set", "EXISTS")
ref("hold", S+"hold/master.jpg", "the cargo hold set", "PLANNED")
ref("hall", S+"customs/master.jpg", "the customs hall", "EXISTS")
ref("desk", S+"customs/desk.jpg", "Mira's desk behind its glass screen", "PLANNED")
ref("cage", S+"customs/holding-cage.jpg", "the holding-bay cage", "PLANNED")
ref("office", S+"customs/noakes-office.jpg", "Noakes's office", "PLANNED")
ref("corr", S+"customs/corridor.jpg", "the customs corridor with its long window", "PLANNED")
ref("console", S+"customs/clamp-console.jpg", "the clamp console under the board", "PLANNED")
ref("board", S+"customs/board.jpg", "the flip-number board", "PLANNED")
ref("chaise", S+"postchaise/master.jpg", "the post-chaise rover (horse's head on the bonnet, trunk on the roof)", "PLANNED")
ref("cab", S+"postchaise/cab.jpg", "the post-chaise cab interior", "PLANNED")
ref("innx", S+"hatchet/exterior.jpg", "the Silver Hatchet exterior", "PLANNED")
ref("parl", S+"hatchet/parlour.jpg", "the Silver Hatchet parlour", "PLANNED")
ref("cold", S+"hatchet/coldstore.jpg", "the cold store", "PLANNED")
ref("apron", S+"apron/master.jpg", "the bay nine apron", "PLANNED")
ref("ship", "assets/ship/master.jpg", "The Unscheduled, exterior", "EXISTS")
P = "assets/props/"
for k, n, l in [("parcel","parcel","the parcel"),("hatchet","hatchet","the silver hatchet"),("horn","posthorn","the brass post horn"),
                ("trunk","trunk","the LOT 14 trunk"),("box","inlaid-box","Chichikov's inlaid box"),("stamp","stamp","the customs stamp"),
                ("lock","padlock","the Riga padlock")]:
    ref(k, P+n+"/master.jpg", l, "PLANNED")
ref("pip", P+"pip/master.jpg", "PIP", "EXISTS")
ref("pipW", P+"pip/ref-wrist.jpg", "PIP's wrist unit (same amber lens, strapped to a wrist)", "GAP")
ref("crawler", "assets/vehicles/crawler/master.jpg", "the customs crawler", "GAP")
ref("notebook", P+"notebook/master.jpg", "Mira's battered paper notebook", "GAP")

CHAR_OF = {"jax": "jax", "jaxC": "jax", "jaxP": "jax", "jaxH": "jax", "jaxL": "jax", "mira": "mira", "miraS": "mira",
           "lucia": "lucia", "luciaS": "lucia", "baron": "baron", "baronS": "baron", "baronL": "baron", "baronHT": "baron",
           "chich": "chichikov", "noakes": "noakes", "temi": "temi", "mamani": "mamani", "pip": "pip", "pipW": "pip"}

SCENE_SOUND = {
 "0": "Bridge room tone (engine hum, relays); PIP motif accents.", "1": "Hold room tone; reactor tick.",
 "2": "Bridge tone; A1 under dialogue.", "3": "Hall: huge reverb, ventilation; no music under dialogue.",
 "4": "Desk close-mic; hall hush.", "5": "Hall hush; Voss motif hint on Chichikov.", "6": "Cage tone; light caper colour (C1 sparse).",
 "7": "Office tone.", "8": "Cab: rover hum, rattles, trunk thumps on the roof; C1 caper.", "9": "Vacuum: no effects; score only, then silence.",
 "10": "Parlour tone; stove.", "11": "Parlour tone; near silence.", "12": "Office tone; Voss motif (M4).", "13": "C2 broken harpsichord.",
 "14": "Parlour tone; A4 enters at the turn.", "15": "Cold store: frost crackle, cold hum; C3 frozen march.", "16": "Parlour; M4 under Chichikov.",
 "17": "Cab under strain; no score.", "18–19": "Office, then corridor footsteps; M2 colour.", "20": "Hold tone; no score until PIP.",
 "21": "Suit radio only; A4 low; vacuum: no effects.", "22": "Hall hush; clock tick; C4 tension rises.", "23": "Klaxon; C1 chase.",
 "24": "Vacuum outside: score only (C1 chase); cab interior dry.", "25": "Hall hush; clock tick; C4 tension.", "26": "Cab; silence on black.",
 "27": "Cab heater, frost; radio hiss; C5 cue (map) very low.", "28": "Hall; silence at 1.3 s.", "29": "Suit radios; vacuum; C1 chase; silence on the throw.",
 "30": "Bridge tone; A4; A1 under V.O.", "31": "Night tones; M4; knocks.", "WWR": "A1 under PIP.", "END": "End sting.", "T": "Title sting."}

LIB_GAP_JOBS = [
 ("pipW", "PIP's wrist unit: the same brass-and-cream lens housing and amber lens as PIP, miniaturised onto a worn leather wrist strap on a man's forearm in a burnt-orange sleeve, macro product shot, dark background.", ["pip", "jax"]),
 ("crawler", "A customs crawler: a squat six-wheeled pressurised lunar patrol rover of original design, white and dull yellow, one round cab window, a grapple launcher on the roof, scuffed by regolith dust, side view, on grey lunar ground under a low hard sun, black sky.", []),
 ("notebook", "A battered pocket notebook with a cracked brown cover and swollen ink-stained pages, on a steel desk, macro.", []),
 ("miraS", "Full body, Dr Mira Sen in a slim indigo customs pressure suit with a clear-visor helmet, loupe on a chain clipped outside the suit, standing on grey lunar regolith under a low hard sun, black sky.", ["mira", "jaxH"]),
 ("luciaS", "Full body, Lucía Ortega in a heavy scuffed engineer's pressure suit, helmet with clear visor, red ribbon tied round the outside of her glove cuff, on grey lunar regolith under a low hard sun, black sky.", ["lucia", "jaxH"]),
 ("baronHT", "Head and shoulders, the Baron in a patched pressure-suit helmet with a clear visor; his black tricorn hat is strapped absurdly on top of the helmet with a leather belt; the white moustache fills the lower visor; low hard sun, black sky.", ["baron", "baronS"]),
]

# ---------------------------------------------------------------- footage
def foot(cid, in_s=None, out_s=None, note="", fallback=None):
    x = CANDS[cid]
    d = dict(id=cid, source=x["source"], title=x["title"], credit=x["credit_line"], licence_note=x["licence"],
             verified=x["verified"], verified_means="download URL answered HTTP 200 in the research sweep; content not yet viewed",
             kind=x["kind"], resolution=x.get("resolution"), media_duration_s=x.get("duration_s"),
             has_audio_or_music=x.get("has_audio_or_music"),
             in_s=in_s, out_s=out_s, note=note)
    if fallback:
        f = CANDS[fallback]
        d["fallback"] = dict(id=fallback, title=f["title"], credit=f["credit_line"], verified=f["verified"], kind=f["kind"])
    return d

SVS4944 = "Preferred plate is NASA SVS 4944 (Earth and Sun from the south pole) but it is NOT in candidates.json: it must be logged in assets/ with URL, credit and licence and its download verified before use."
FT = {
 "moonvid": lambda a, b, n="": foot("Moon Below Orion art001m1013251756", a, b, "Real Orion footage of the Moon for the bridge window. In/out to pick on viewing (no stated duration). " + n, "art001e000270"),
 "moonstill": lambda n="": foot("art001e000270", None, None, "Still; slow drift inside the window. " + n),
 "pole": lambda n="": foot("PIA12077", None, None, "Real south-polar composite still (4000x3796); slow push toward Shackleton. " + n),
 "clem": lambda n="": foot("PIA00001", None, None, "Real Clementine south-pole mosaic (7943x7943); slow push. " + n),
 "fly": lambda a, b, n="": foot("SVS-3686/SPflyover_v07_lg.mp4", a, b, "LOLA south-pole flyover (data visualisation from real altimetry). Unverified: SVS host gave 403 to the sweep. " + n, "ARC-20210920-AAV3366-VIPER-LandingSiteAnnouncement-YouTubeHD"),
 "lroc": lambda a, b, n="": foot("SVS-3634/LROC_1st_light.mp4", a, b, "Shackleton's rim through LROC. Unverified. " + n, "PIA12077"),
 "psr": lambda a, b, n="": foot("SVS-4043/shot1_on_1080p30.mp4", a, b, "LRO view into permanent shadow. Unverified. " + n, "GSFC_20130306_Moons_m11218_Shadowed"),
 "poleEarth": lambda a, b, n="": foot("File:Lunar South Pole Illumination with Earth and Sun (SVS5228).webm", a, b, SVS4944 + " Planned stand-in from the list: SVS5228 (Commons mirror, unverified). " + n, "art002e016299"),
 "earth": lambda n="": foot("art002e016299", None, None, "Real Orion photo of Earth; used ONLY as the Earth disc composited low over a generated horizon (WWR says so). " + n),
 "earthset": lambda a, b, n="": foot("ART-DL-1_2022_325_1209_SHARED_art001m1013251209", a, b, "Real Artemis I Earthset behind the lunar limb (1008 s; audio stripped). " + n, "art002e021278"),
 "farside": lambda a, b, n="": foot("a2_flyby_1min_2160p30", a, b, "Simulated Artemis II flyby built from real LRO data (4K). Strip audio; check for burnt-in text. " + n, "art002e012216"),
 "earthrise": lambda a, b, n="": foot("ART-SAW4_2022_325_1305_SHARED_art001m1203251305", a, b, "Real Orion Earthrise video (142 s); audio stripped. " + n, "art002e016299"),
 "peek": lambda n="": foot("art002e021283", None, None, "Real Artemis II still, Earth from the far side (5568x3712). " + n),
}

# ---------------------------------------------------------------- shots
JOBS = OrderedDict()   # id -> job dict
SHOTS = []
SCENE_ORDER = ["0", "T", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
               "17", "18–19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "WWR", "END"]
ACT = {"0": "Cold open", "T": "Cold open", **{k: "Act 1" for k in "1 2 3 4 5 6 7".split()},
       **{k: "Act 2" for k in "8 9 10 11 12 13 14 15 16".split()},
       **{k: "Act 3" for k in ["17", "18–19", "20", "21", "22"]},
       **{k: "Act 4" for k in "23 24 25 26 27 28 29 30".split()}, "31": "Tag", "WWR": "What was real", "END": "What was real"}
BARON_SAT = {"Cold open": 100, "Act 1": 100, "Act 2": 87, "Act 3": 73, "Act 4": 60, "Tag": 60}

def J(group, name, refs, desc):
    jid = f"E01-J{len(JOBS)+1:03d}"
    JOBS[jid] = dict(job_id=jid, group=group, target_file=f"$SU_WORK/E01/stills/{jid.lower()}_{name}.png",
                     references=[REF[r]["path"] for r in refs], ref_keys=refs, shot_description=desc, used_by=[])
    return jid

def prompt_for(job):
    who, parts = [], []
    for i, k in enumerate(job["ref_keys"]):
        base = CHAR_OF.get(k)
        if base:
            parts.append(f"Image {i+1} is the reference for {REF[k]['label']}: keep the same face, hair, age and costume exactly.")
            if LOCK[base] not in who:
                who.append(LOCK[base])
        else:
            parts.append(f"Image {i+1} is the reference for {REF[k]['label']}: keep the same design, materials and lighting.")
    refline = " ".join(parts) if parts else "No reference image: this is a new plate."
    name = os.path.basename(job["target_file"])
    return ("Use your built-in image generation tool to generate exactly ONE image, landscape 16:9, and save it in the "
            f"current directory as {name}. Do not write any code, do not use Python or any drawing library, do not use the "
            f"fallback CLI/API mode, and do not generate more than one image. {refline} Image prompt: {STYLE} "
            f"{job['shot_description']} {' '.join(who)} {HOUSE} After saving, reply with the file path and nothing else.")

cur = dict(scene=None, n=0)
def s(sc, typ, lines, beat, desc, cam, mot, chars="", img=None, assets=(), ft=None, comp=None, snd=None, risk=None):
    if cur["scene"] != sc:
        cur.update(scene=sc, n=0)
    cur["n"] += 1
    SHOTS.append(dict(sc=sc, typ=typ, lines=lines, beat=beat, desc=desc, cam=cam, mot=mot, chars=chars, img=img,
                      assets=list(assets), ft=ft, comp=comp, snd=snd, risk=risk, n=cur["n"]))

# ================================================================= COLD OPEN (0)
pip_lens = J("PIP", "pip_lens_dark", ["pip"], "Extreme close-up of PIP's single amber lens glowing in near-total darkness on a cramped ship's bridge, brass rim catching the glow, everything else black.")
br_wide = J("SET bridge", "bridge_wide_jax_back", ["bridge", "jax"], "Wide from behind the two bridge seats: Jax Vale seen from behind and slightly left, flying with one hand, a half-eaten sandwich in the other, silhouetted against the large pure-black window, screens glowing.")
coffee = J("SET bridge", "coffee_machine", ["bridge"], "Macro insert of a battered little drip coffee machine wedged into the bridge console among cable ties and tape, one small green indicator light lit.")
jax_sandw = J("Jax", "jax_sandwich_mcu", ["jax", "jaxC"], "Three-quarter medium close-up of Jax Vale in the pilot seat, lit by dying amber screens, a sandwich raised to his mouth mid-bite so the sandwich hides his mouth, eyes wide with outrage.")
jax_alarm = J("Jax", "jax_listen_screen", ["jax", "bridge"], "Medium close-up of Jax Vale half-turned toward a glowing screen off-frame left, sandwich lowered, mouth firmly closed, appalled disbelief, screen light on his face, black window behind.")
jax_ots = J("Jax", "jax_ots_screen", ["jax", "bridge"], "Over-the-shoulder from behind Jax Vale's head and burnt-orange collar toward a large blank console screen at the side of the bridge; his face is not visible.")
pip_jax = J("PIP", "pip_fg_jax_bg", ["pip", "jax", "bridge"], "PIP sharp in the foreground on the bridge console, amber lens glowing; behind it, soft and out of focus, Jax Vale as a dark silhouette against the pure-black window.")
pip_turn = J("PIP", "pip_lens_swivel", ["pip"], "PIP on the bridge console, its lamp-like head swivelled sharply toward camera-left as if hearing a sound, amber lens bright, stamp arm raised.")
jax_eyes = J("Jax", "jax_ecu_eyes_screen", ["jax", "jaxC"], "Extreme close-up of Jax Vale's eyes and brows only (frame cuts below the nose), lit by a cold screen glow, narrowed, calculating.")
pip_stamp = J("PIP", "pip_stamp_arm", ["pip"], "Macro of PIP's brass rubber-stamp arm slamming down onto a small blank paper slip on the console, motion frozen at impact, amber glow above.")
jax_prof = jax_alarm  # merged: reuse, no new image
jax_lucky = J("Jax", "jax_mcu_halfsmile", ["jax", "jaxC"], "Medium close-up of Jax Vale, three-quarter front, crooked half-smile with lips closed, warm console light, black window behind.")

s("0", "BLACK", [], 2.0, "Black. Silence.", "hold", "none", snd="Total silence (0.5 s room tone fade-in from digital zero).")
s("0", "INSERT", [2], 0.8, "PIP's amber lens blinks on out of the black: the first line is a light, not a mouth.", "slow push-in 3% over the shot", "lens glow driven by PIP's voice envelope; lens flare bloom", "pip", pip_lens, risk=("low", "prop only"))
s("0", "SET_STILL", [3, 4], 1.0, "The bridge from behind: Jax flying one-handed with a sandwich; the real Moon fills the window.", "push-in 4% over 5 s; 3-layer parallax (window plate drifts at 40% of set speed)", "screen flicker; slow dust motes", "jax", br_wide, ft=FT["moonvid"](10, 20),
  comp="Real Orion Moon video into the black window via a per-set window mask (generalise composite_window.py: polygon per set, not hard-coded); crush blacks, match grain.", risk=("medium", "window mask must be drawn per set; generator may not leave the window pure black"))
s("0", "DATA_VISUAL", [5], 0.3, "A row of engine readouts on a bridge screen drops to zero, one by one.", "hold, 2% drift", "readouts animate down; screen flicker", img="CODE", comp="Code-built readout UI composited onto a crop of the bridge master's centre screen.")
s("0", "INSERT", [], 1.6, "The coffee machine's little green light goes out.", "hold", "green light switched off at frame 12 (mask)", img=coffee, snd="Tiny electrical click; fridge-like hum stops.")
s("0", "CHARACTER_STILL", [6], 0.2, "Jax mid-bite, outraged; the sandwich hides his mouth.", "slow push-in 3%", "breath (0.5% scale), one blink at 0.6 s", "jax", jax_sandw, risk=("low", "mouth hidden by sandwich"))
s("0", "INSERT", [7], 0.2, "PIP's lens, a little wider, the stamp arm visible.", "hold", "lens glow with speech", "pip", pip_lens)
s("0", "DATA_VISUAL", [(8, 0, 4.6)], 0.6, "A cheerful chime; a smiling bank logo, then a call window opens: Temi in her headset, bright.", "hold on screen; slight push", "call window animates open; Temi's video runs at 8 fps with compression blocks; mouth patch in 2 frames", "temi:m", "CODE",
  assets=[REF["temi"]["path"]], comp="Library Temi master inside a code-built call-window UI on the bridge's side screen. Low-fps call video hides the patch.", risk=("medium", "the only Temi mouth patch; low-fps call look makes it forgiving"))
s("0", "CHARACTER_STILL", [(8, 4.6, None)], 0.0, "Jax listening, appalled, sandwich lowered.", "push-in 3%", "breath; blink; screen light flicker on face", "jax:m", jax_alarm, risk=("low", "listener, mouth closed and silent"))
s("0", "TWO_SHOT", [9, 10, 11, 12], 0.2, "Over Jax's shoulder to the call window: he argues with the screen; Temi keeps talking over him, then the window resets with a chirp: 'Hello!'.", "handheld drift 1%, push-in 4% on the reset", "call window stutters (1.3 s lag): freeze-frames between lines; window flashes and re-opens on L012", "jax,temi", jax_ots, assets=[REF["temi"]["path"]], comp="Temi call window composited into the blank screen (Temi small, low-fps; no patch on this shot).")
s("0", "TWO_SHOT", [13, 14, 15], 0.3, "PIP sharp in the foreground; Jax a soft silhouette behind it against the Moon.", "rack focus: Jax (soft) to PIP (sharp) on PIP's line", "lens glow", "pip,jax", pip_jax, ft=FT["moonstill"](), comp="Real Moon still in the window behind; heavy defocus.", risk=("low", "silhouette, no mouth"))
s("0", "INSERT", [(16, 0, 3.0)], 0.0, "A soft, old-fashioned shop-door chime; PIP's lens swivels toward it.", "whip-pan 6% left into the hold", "two-position swivel: cut between pip_lens and this image on the chime", "pip", pip_turn, snd="SFX: shop-door bell (single, warm). First appearance of the bell motif.")
s("0", "DATA_VISUAL", [(16, 3.0, None)], 1.0, "The job card on screen: ONE PARCEL · SEALED · PREPAID · SHACKLETON CRATER · BY 18:00 · FEE —. The fee field stays blank as PIP stops.", "push-in 5%", "text types on; cursor blinks on the empty fee field", img="CODE")
s("0", "CHARACTER_STILL", [17, 18], 0.0, "Jax's eyes only, on the screen.", "hold, 1% drift", "one slow blink", "jax", jax_eyes, risk=("low", "eyes-only crop, mouth out of frame"))
s("0", "TWO_SHOT", [19, 20, 21], 0.0, "Over Jax's shoulder, pushing in on the job card as he says 'take it' five times.", "fast push-in 10% over the shot", "screen flicker", "jax,pip", jax_ots)
s("0", "INSERT", [(22, 0, 1.0)], 0.2, "PIP's stamp arm comes down. THUNK.", "hold; 2-frame shake on impact", "arm up/down: cut-out warp of the arm layer", "pip", pip_stamp, snd="SFX: stamp thunk (hero version).")
s("0", "DATA_VISUAL", [(22, 1.0, None)], 0.8, "PIP's screen: REPORT #1,204 — RE: CAPTAIN. \"TAKE IT\" (x5).", "hold", "text stamps on line by line", img="CODE")
s("0", "SET_STILL", [], 3.2, "One point three seconds of nothing. Then the left engine coughs back to life: lights come back, the heating ticks, the coffee machine does not.", "push-in 3%", "lights relight in sequence via masks; window plate drifts", "jax", br_wide, ft=FT["moonvid"](20, 24), snd="1.3 s silence, then engine cough, relay clunks, heating ticks.")
s("0", "INSERT", [], 1.2, "The coffee machine stays dark.", "hold", "none", img=coffee, snd="Silence on the insert (the joke).")
s("0", "DATA_VISUAL", [24], 0.6, "The cargo-camera screen: a brown-paper parcel, soft at the corners, thick with stamps and labels.", "push-in 6% (CCTV zoom feel)", "scan lines; timecode", img="CODE", assets=[REF["parcel"]["path"]], comp="Library parcel master graded as a monochrome cargo-camera feed.")
s("0", "CHARACTER_STILL", [25], 1.6, "Jax, half-turned to the screen, looks at the parcel a moment longer than he'd like.", "very slow push-in 2%", "breath; screen-light flicker; no blink (the stare)", "jax", jax_prof, comp="Re-use of jax_listen_screen, regraded warmer and cropped tighter; the profile still was cut to avoid profile drift.")
s("0", "CHARACTER_STILL", [26], 0.4, "Jax: 'Lucky.' A crooked half-smile.", "hold", "mouth patch (2 visemes); blink", "jax:m", jax_lucky, risk=("medium", "mouth patch on a 0.6 s word"))
s("0", "INSERT", [27], 0.4, "PIP's lens: 'Filed under arithmetic.'", "hold", "lens glow", "pip", pip_lens, snd="Smash cut to title.")
s("T", "TITLE", [], 10.0, "MAIN TITLE: SECRET UNIVERSE over real Earthrise from Orion.", "slow push-in 4%", "title animates in", img="CODE", ft=FT["earthrise"](30, 40), snd="A1-title-sting-10s (v2).",
  comp="Title in house font; real footage behind, graded.")

# ================================================================= 1 CARGO HOLD
hold_boots = J("SET hold", "hold_wide_boots", ["hold", "lucia"], "Wide of the empty cargo hold: one brown-paper parcel strapped down in the middle like a patient; beyond it, a pair of work boots sticks out of the open reactor housing at the back; one work lamp.")
hand_spanner = J("Lucía", "hand_ribbon_palm", ["lucia", "jax"], "Insert: a grease-stained woman's hand with a red ribbon tied round the wrist emerges palm-up from a dark machine opening; a man's hand in a burnt-orange sleeve places a spanner in it.")
hand_back = hand_spanner  # merged: reuse, no new image
jax_hold_back = J("Jax", "jax_hold_from_behind", ["jax", "hold"], "Jax Vale seen from behind and slightly to the side, crouched by an open reactor housing in a cargo hold, holding a tool tray, his face not visible.")
pip_hold = J("PIP", "pip_hold_wall", ["pip", "hold"], "A small brass-and-cream intercom speaker on the cargo-hold wall with PIP's amber lens in its centre, glowing, cables taped beside it.")
lucia_creeper = J("Lucía", "lucia_creeper", ["lucia", "hold"], "Lucía Ortega sliding out from under a reactor housing on a mechanic's creeper, broad shoulders, grease to the elbows, looking up, mouth closed, seen from slightly above.")
lucia_palm = J("Lucía", "palm_on_parcel", ["lucia", "parcel"], "Macro insert: a strong grease-stained woman's palm with a red ribbon at the wrist laid flat on brown wrapping paper covered in layered stamps and labels.")
s("1", "SET_STILL", [32], 2.0, "The hold: the parcel strapped in the middle like a patient; boots sticking out of the reactor housing.", "slow push-in 4% over 4 s", "work-lamp flicker; dust motes", "", hold_boots, snd="Hold room tone; Lucía's voice muffled inside metal.")
s("1", "INSERT", [], 1.2, "The hand with the red ribbon, palm up. Jax puts a spanner in it.", "hold", "hand withdraws: cut", "", hand_spanner)
s("1", "INSERT", [33], 0.2, "The hand comes back out with the spanner.", "hold, 2-frame jolt", "none", "", hand_back)
s("1", "CHARACTER_STILL", [34, 35], 0.0, "Jax from behind, handing in tools.", "slow lateral parallax 3%", "breath", "jax", jax_hold_back)
s("1", "SET_STILL", [36, 37, 38], 0.0, "Tighter: the boots in the housing, the parcel soft in the foreground.", "push-in 6%", "boot shifts (2-frame)", "", hold_boots)
s("1", "INSERT", [39, 40], 0.3, "PIP's lamp on the hold wall brightens.", "hold", "lens glow with speech", "pip", pip_hold)
s("1", "CHARACTER_STILL", [], 1.4, "Lucía slides out on the creeper: shoulders, grease, a look.", "tilt-up 4%", "breath", "lucia:m", lucia_creeper, risk=("low", "first sight of Lucía; silent"))
s("1", "INSERT", [41, 42], 0.3, "Her palm on the brown paper. It's warm.", "very slow push-in 3%", "faint heat shimmer above the paper (displacement)", "", lucia_palm)
s("1", "INSERT", [43], 0.6, "The parcel's stamps and labels, layered twenty years deep.", "macro pan 5% across labels", "none", "", "LIB:parcel", snd="Low warm drone under the last line (parcel motif seed).")

# ================================================================= 2 BRIDGE APPROACH
s("2", "REAL_FOOTAGE", [45], 3.5, "The real south pole turns up toward us: a crater rim burning white, a pit of total black.", "footage's own move; no added camera", "real footage", "", "REAL", ft=FT["fly"](0, 10, "Pick the section where Shackleton enters frame. If the fallback VIPER tour has burnt-in graphics, use PIA12077 with a 6% push instead."),
  comp="Full frame. Strip audio. Grade toward the episode look but keep it honest (no added Earth here).", snd="Score: A1 theme low (under-dialogue v2), no effects.", risk=("medium", "plate unverified; fallback ready"))
s("2", "SET_STILL", [46], 0.8, "Jax a silhouette against all that white and black in the window.", "slow push-in 3%", "window plate drifts", "jax", br_wide, ft=FT["pole"]("Crop on Shackleton, graded as seen through glass."))
for i, (ln, beat, txt) in enumerate([([48], 1.2, "THE SILVER HATCHET — SHACKLETON FLOOR, glowing on the black crater floor."),
                                     ([49], 0.6, "THE SILVER HATCH"), ([50], 0.4, "THE SILVER HAT"), ([], 1.0, "THE SILVER"),
                                     ([51], 0.3, "THE"), ([52], 0.6, "The label is gone.")]):
    s("2", "DATA_VISUAL", ln, beat, f"The Atlas display: {txt}", "hold (one held frame per stage); 1% creep across the sequence", "letters dim from the end, one at a time", img="CODE",
      ft=FT["pole"]("Used as the Atlas base map, desaturated and contoured."), comp="Atlas UI over the real polar still (DATA_VISUAL 1).")
s("2", "CHARACTER_STILL", [53], 0.0, "Jax's eyes in the Atlas glow.", "hold", "blue screen light pulses", "jax", jax_eyes, comp="Regrade the eyes still cold blue for the Atlas light.")
s("2", "INSERT", [54], 0.2, "PIP's lens.", "push-in 2%", "lens glow", "pip", pip_lens)
s("2", "DATA_VISUAL", [], 3.0, "The little street names go out like lamps: HATCHET LANE, BEAN ROW, STRAW STAIRS. The floor is only dark.", "slow pull-out 5%", "labels extinguish one by one with a faint after-glow", img="CODE", ft=FT["pole"]())
s("2", "TWO_SHOT", [55, 56], 0.3, "PIP sharp, Jax soft behind it.", "hold", "lens glow", "pip,jax", pip_jax, ft=FT["pole"]())
s("2", "DATA_VISUAL", [(57, 0, 6.0)], 0.0, "A radio click. On the bridge screen, an inset: Officer Mamani at his control desk, handset at his mouth.", "push-in 4% on the inset", "inset video at 10 fps; radio-noise lines", "mamani", "CODE", assets=[REF["mamani"]["path"]],
  comp="Library Mamani master (handset covers mouth) in a port-control inset UI on the bridge screen.", risk=("low", "handset hides mouth"))
s("2", "CHARACTER_STILL", [(57, 6.0, None)], 0.3, "Jax listens: 'Your client is nowhere, Captain.'", "slow push-in 3%", "breath; blink", "jax:m", jax_alarm, comp="Regrade colder than the cold open.")
s("2", "INSERT", [58], 0.0, "PIP's lens swivels toward the screen.", "hold", "lens glow", "pip", pip_turn)
s("2", "DATA_VISUAL", [59], 0.4, "PIP's screen: REPORT #1,205 — RE: THE ATLAS.", "hold", "text stamps on", img="CODE")
s("2", "SET_STILL", [60], 1.6, "The bridge from behind; the real pole fills the window as they descend.", "slow push-in 3%", "window plate slow scale-up (descent)", "jax", br_wide, ft=FT["pole"](), snd="Score resolves; cut to the hall's hush.")

# ================================================================= 3 CUSTOMS DESK
hall_jax = J("SET customs", "hall_xwide_jax", ["hall", "jax"], "Extreme wide of a customs hall built for two thousand people and staffed for three: rows of empty benches, one lit desk behind a glass screen, a blank flip-number board high on the far wall, Jax Vale a tiny figure alone on the floor.")
jax_benches = hall_jax  # merged: reuse, no new image
mira_hands = J("Mira", "mira_hands_desk", ["mira", "desk", "stamp"], "Insert: a woman's ink-stained fingers at a steel customs desk behind a scratched glass screen, squaring a blank form, a heavy brass-handled stamp and ink pad beside it.")
mira_ots = J("Mira", "ots_mira_to_jax", ["mira", "jax", "desk"], "Over the shoulder from behind Dr Mira Sen's head (dark braid, indigo collar) through a scratched glass customs screen to Jax Vale leaning on the counter; a round perforated speaking-disc set in the glass sits exactly over Jax's mouth and hides it.")
mira_refl = J("Mira", "mira_reflection_glass", ["mira", "desk"], "Dr Mira Sen's faint reflection in a customs glass screen, seen over a blurred hall, her eyes holding a look one beat too long; reflection soft and ghostly.")
stamp_hit = J("Props", "stamp_seized_hit", ["stamp", "mira"], "Macro insert: a heavy brass-handled customs stamp slamming onto a blank paper form at a steel desk, an ink-stained hand on the handle, motion frozen at impact.")
hall_baron = J("SET customs", "hall_xwide_baron_scale", ["hall", "baron"], "Extreme wide down a vast customs hall: far away at the end, a tiny old figure in a tricorn hat and red coat stands on a freight scale while a small hovering inspection drone hangs beside him; empty benches lead to him.")
s("3", "REAL_FOOTAGE", [], 3.5, "Landing at Rim Port: the real rim sliding past below, the crater's black pit beyond.", "footage move only", "real", "", "REAL", ft=FT["fly"](30, 34, "Short descent section; no port is added (we never fake a structure into a real plate here)."), comp="Full frame; honest grade.", snd="Score out; landing-gear thump as the cut lands on the hall.")
s("3", "SET_STILL", [62], 2.6, "The hall built for two thousand and staffed for three. One lit desk. On the far wall, the board.", "slow push-in 5% over 5 s", "fluorescent flicker on one tube; dust", "jax", hall_jax, ft=FT["earth"]("Earth disc low in the far window if the window shows sky; otherwise black."),
  comp="Board numbers (1,094) composited in code on every shot that shows it. Library hall master has a model-drawn planet in its window: library agent to regenerate with a pure-black window or paint it out.", snd="Huge empty-hall reverb tail on 'Next.'; distant ventilation.", risk=("medium", "library hall master window not black"))
s("3", "CHARACTER_STILL", [63, 64], 0.0, "Jax turns to the empty benches.", "slow pan 3% following his look", "breath", "jax", jax_benches)
s("3", "INSERT", [65], 0.2, "Mira's ink-stained hands square the form beside her stamp.", "hold", "fingers tap (2-frame)", "mira", mira_hands)
s("3", "TWO_SHOT", [66, 67, 68, 69], 0.0, "Over Mira's shoulder through the glass: Jax leaning in, charming; the speaking-disc in the glass sits over his mouth.", "handheld drift 1%", "glass reflections drift", "mira,jax", mira_ots, risk=("medium", "the speaking-disc must land on Jax's mouth; fix in post with a disc overlay if not"))
s("3", "TWO_SHOT", [70, 71], 0.0, "Tighter on Jax through the glass.", "push-in 6%", "breath", "jax", mira_ots)
s("3", "INSERT", [72, 73], 0.0, "Her hand flattens the form: NEXT OF KIN: NONE.", "hold", "none", "mira", mira_hands, comp="Form text in code.")
s("3", "TWO_SHOT", [74, 75, 76], 0.0, "Jax through the glass, very pleased with section twelve.", "slow push-in 3%", "breath", "jax", mira_ots)
s("3", "INSERT", [77, 78], 0.0, "Her hand lifts the stamp and hovers.", "hold", "stamp rises (cut-out, 3 px)", "mira", mira_hands)
s("3", "DATA_VISUAL", [80], 2.2, "Her screen: VALE, JAX. MASTER, COURIER CLASS. The record begins seven years ago; above that line the fields are empty. Not redacted. Empty.", "slow tilt-up 6% to the empty fields", "cursor blinks in an empty field", img="CODE")
s("3", "TWO_SHOT", [81, 82], 0.0, "Over her shoulder again.", "hold", "glass reflection drift", "mira,jax", mira_ots)
s("3", "CHARACTER_STILL", [], 2.4, "In the glass, silently, her reflection looks at him one beat too long.", "very slow push-in 2%", "reflection opacity breathes", "mira:m", mira_refl, risk=("low", "silent beat, as staged"))
s("3", "TWO_SHOT", [83, 84], 0.0, "Jax through the glass.", "hold", "breath", "jax", mira_ots)
s("3", "INSERT", [], 1.0, "Her stamp. THUNK. SEIZED.", "2-frame shake", "ink impression appears", "mira", stamp_hit, snd="SFX: stamp thunk (customs version, heavier, hall reverb).", comp="SEIZED impression in code.")
s("3", "TWO_SHOT", [86, 87], 0.0, "Jax through the glass, deflated.", "hold", "none", "jax", mira_ots)
s("3", "SET_STILL", [88], 1.6, "Far down the hall, a tiny figure in a tricorn on a cargo scale; a customs drone reads his weight.", "slow push-in 4%", "drone hovers (1 px bob); scale needle twitch", "baron", hall_baron, snd="Baron's line pre-delayed with long hall reverb, distant.")

# ================================================================= 4 MIRA'S DESK
pages = J("Mira", "notebook_pages", ["notebook", "mira"], "Macro: the battered notebook open on the desk, pages of small neat handwritten entries in blue-black ink (illegible), a pencil in an ink-stained hand.")
drawer = pages  # merged: reuse, no new image
noakes_refl = J("Noakes", "noakes_reflection_monitor", ["noakes", "mira", "desk"], "A dark switched-off monitor on a customs desk reflecting, faint and soft, a tired man in a customs uniform standing behind a seated woman with a dark braid; his face is dim and blurred, cut by the monitor bezel at the chin.")
board_ins = J("SET customs", "board_insert", ["board", "hall"], "Insert: a mechanical flip-number board on a concrete customs-hall wall, four blank number flaps under a blank header panel, a little dust, one flickering tube light above.")
s("4", "DATA_VISUAL", [90], 1.0, "The deletion record: THE SILVER HATCHET. STATUS: WITHDRAWN AT THE REQUEST OF THE OWNER. OWNER: —", "slow push-in 5% to the empty OWNER field", "cursor blink", "", "CODE")
s("4", "INSERT", [], 1.5, "She takes the battered notebook from her drawer.", "hold", "drawer slides (cut-out 6 px)", "mira", drawer, snd="Drawer scrape, small and close.")
s("4", "INSERT", [91], 0.6, "Page after page in her small exact hand. Every entry ends OWNER: —.", "slow pan down the page 8%", "page edge flutter", "", pages, comp="Handwriting overlay in code (pencil font + jitter).")
s("4", "INSERT", [92], 0.4, "She writes: 41. THE SILVER HATCHET. OWNER: —", "hold", "write-on animation of the entry", "mira", pages)
s("4", "CHARACTER_STILL", [93], 0.0, "In her dark monitor: Noakes behind her, soft and dim.", "rack focus: monitor glass to reflection (never sharp)", "reflection drift", "noakes", noakes_refl, risk=("medium", "reflection must stay soft enough that his mouth is unreadable"))
s("4", "INSERT", [94, 95], 0.0, "Her hand flat on the notebook.", "hold", "none", "mira", pages)
s("4", "INSERT", [96], 0.3, "Behind him, on the wall: DAYS WITHOUT INCIDENT: 1,094.", "push-in 4%", "tube flicker", "", board_ins, comp="Header and 1,094 in code; same code on every board shot.")
s("4", "INSERT", [97], 2.0, "His reflection leaves. She looks at the page. She doesn't close it.", "hold", "page lifts 1 px then settles", "", pages, snd="Mira motif (M2) phrase, solo, under the hold.")

# ================================================================= 5 BENCH
bench_wide = J("SET customs", "bench_wide_jax", ["jax", "hall"], "Wide: Jax Vale alone in the middle of a very long empty customs-hall bench, shoulders down, wrist raised toward his face, the empty hall stretching behind; his face small in frame.")
wrist = J("PIP", "wrist_comm_jax", ["pipW", "jax"], "Insert: PIP's small wrist unit with its amber lens strapped to Jax Vale's wrist in a burnt-orange sleeve, glowing, a customs-hall bench blurred behind.")
bench_clean = J("SET customs", "bench_two_clean", ["hall", "jax"], "Bench two-shot plate: Jax Vale sharp at the near end of a long bench, turned toward the far end, face in three-quarter back; the far end of the bench is empty and out of focus.")
bench_chich = J("Chichikov", "bench_two_chichikov", ["chich", "box", "hall"], "Edit of the bench plate: at the soft far end of the bench sits a plump polite man in grey with a small inlaid box on his knees and a teacup in his hand, deeply out of focus; keep everything else identical.")
jax_wary = J("Jax", "jax_bench_listen", ["jax", "jaxC", "hall"], "Medium close-up of Jax Vale on a bench, wary, listening to someone off-frame right, lips pressed shut, hall lights bokeh behind.")
box_knees = J("Chichikov", "box_on_knees", ["chich", "box"], "Insert: a small inlaid wooden travelling box on a man's grey-overcoat knees, grey-gloved hands resting on it, a teacup on a saucer balanced beside.")
card = J("Chichikov", "card_on_bench", ["chich"], "Insert: a cream calling card being laid on a worn wooden bench by a grey-gloved hand, illegible looping script on it.")
card_jax = card  # merged: reuse, no new image
s("5", "SET_STILL", [99], 1.2, "Jax alone on a long bench. His wrist comm buzzes.", "slow push-in 3%", "breath", "jax", bench_wide, snd="Wrist buzz SFX; Lucía dry and loud from the comm (small speaker EQ).")
s("5", "INSERT", [100, 101], 0.5, "The wrist comm: Lucía's call light, then the click.", "hold", "light pulses then dies on the click", "pip", wrist, snd="Hang-up click.")
s("5", "SET_STILL", [102], 0.0, "Jax on the bench; PIP's light on his wrist.", "push-in 4%", "wrist light glows", "jax", bench_wide)
s("5", "TWO_SHOT", [104, 105], 1.2, "Jax turns. At the soft end of the bench, a plump polite man in grey, box on his knees, teacup in hand. He seems to have been there a while.", "rack focus held soft on Chichikov (he is never sharp)", "teacup steam", "jax,chichikov", bench_chich, risk=("low", "Chichikov soft; Jax turned away"))
s("5", "CHARACTER_STILL", [(106, 0, 6.0)], 0.0, "Jax listens, wary.", "slow push-in 3%", "blink; breath", "jax:m", jax_wary)
s("5", "INSERT", [(106, 6.0, None), 107], 0.0, "The inlaid box on Chichikov's knees, gloved hands still.", "hold", "steam", "", box_knees)
s("5", "TWO_SHOT", [108], 0.0, "Back to the two-shot, Chichikov soft as a smudge.", "hold", "steam", "jax,chichikov", bench_chich)
s("5", "INSERT", [109], 0.2, "A card laid on the bench. A name in neat, looping script.", "hold", "card slides 10 px (cut-out)", "", card)
s("5", "INSERT", [110], 0.3, "Jax reads the card: 'Chich… Chicha…'", "push-in 8% onto the name", "none", "", card_jax, comp="Same card still, tighter; Jax's thumb added as a cut-out from the hand_spanner sleeve. Script name in code, slightly too ornate to read.")
s("5", "SET_STILL", [], 2.0, "He looks up. The bench is empty. The teacup is gone.", "hold", "none", "jax", bench_clean, snd="Score drops out; one dry pizzicato.")
s("5", "SET_STILL", [112, 113, 114, 115], 0.5, "Wide: Jax alone on the long bench, talking to his wrist.", "slow pull-out 4%", "breath", "jax", bench_wide)

# ================================================================= 6 HOLDING BAY
cage_wide = J("SET customs", "cage_wide_baron", ["cage", "baron", "trunk"], "Wide of a wire-mesh holding cage at the end of a customs hall, crowded with tagged lots: a stopped grandfather clock, a stuffed bear in a hussar's jacket, half a saddle with a green shoot growing from the leather; on a battered steamer trunk sits the Baron with a brown-paper parcel on his knee, both hands resting on it like a cat.")
cage_enter = J("SET customs", "cage_gate_mira_jax", ["mira", "jax", "cage"], "From inside the cage looking out: Dr Mira Sen and Jax Vale come through the mesh gate, both seen from behind as she locks it with a key; their faces not visible.")
baron_rise = J("Baron", "baron_rising", ["baron", "cage"], "Medium shot: the Baron rising from a battered trunk with great deliberate dignity, one hand on his knee, tricorn tilted, eyes bright, parcel held in the crook of his arm.")
ots_jax_baron = J("Jax", "ots_jax_to_baron", ["jax", "baron", "cage"], "Over-the-shoulder from behind Jax Vale's curly head toward the Baron standing among tagged junk in a wire cage; Jax's face not visible.")
baron_bow = J("Baron", "baron_bow", ["baron", "cage"], "Medium-wide: the Baron in a magnificent sweeping bow, tricorn swept off in one hand, red coat flaring, among tagged lots in a customs cage.")
jax_swamp = J("Jax", "jax_squint_recognition", ["jax", "jaxC"], "Medium close-up of Jax Vale with a slow squint of half-recognition, head tilted, lips closed, cage mesh soft behind.")
baron_eyes = J("Baron", "baron_ecu_eyes", ["baron"], "Extreme close-up of the Baron: bright wounded old eyes and bushy brows above the enormous white moustache, tricorn brim at the top of frame.")
tag_button = J("Baron", "tag_on_button", ["baron", "mira"], "Insert: a brown luggage tag on string tied to the top brass button of a moth-eaten red cavalry coat, a woman's ink-stained fingers turning it to read.")
parcel_tilt = J("Props", "parcel_tilted_labels", ["parcel", "baron"], "Insert: old hands in lace cuffs tilt a brown-paper parcel toward the light; labels pasted over labels, twenty years of different handwriting (illegible).")
loupe_eye = J("Mira", "mira_loupe_eye", ["mira"], "Extreme close-up: a brass jeweller's loupe held to a woman's eye, the dark eye hugely magnified inside the brass, the rest of the face cut off below the nose.")
mira_key = J("Mira", "mira_key_lanyard", ["mira", "cage"], "Insert: an ink-stained hand lifting a heavy brass customs key on a lanyard, cage mesh behind.")
baron_gate = J("Baron", "baron_back_at_gate", ["baron", "cage", "lock"], "The Baron seen from behind, facing the mesh gate, arm raised grandly toward a big old iron padlock; red coat, tricorn.")
fingers_lock = J("Props", "fingers_on_padlock", ["lock", "baron"], "Macro insert: two old fingers in a lace cuff laid gently on a big old iron padlock on a wire-mesh gate, waiting.")
clock_still = J("Props", "clock_stopped", ["cage"], "Insert: the face and still pendulum of an old grandfather clock that has stopped, brass dull, dust on the glass.")
jax_mira_nolook = J("Jax+Mira", "jax_mira_not_looking", ["jax", "mira"], "Two-shot seen through the wire mesh of a customs cage (mesh sharp in the foreground across both faces): Jax Vale and Dr Mira Sen standing side by side, both very carefully not looking at each other, lips pressed shut, deadpan.")
mira_wrist = mira_key  # merged: reuse, no new image
s("6", "SET_STILL", [], 3.2, "The cage: a stopped clock, a bear in a hussar's jacket, half a saddle sprouting; on trunk LOT 14, the Baron with Jax's parcel on his knee like a cat.", "slow push-in 5% over 6 s; 3-layer parallax (mesh / lots / Baron)", "dust motes; Baron breathes (0.5%)", "baron", cage_wide,
  comp="LOT 14 and THE BARON tags lettered in code. Mesh foreground layer cut out for parallax.", snd="Cage room tone; no clock tick (the clock is stopped: a planted absence).")
s("6", "TWO_SHOT", [118, 119, 120], 0.0, "Mira and Jax come in; she locks the gate behind them.", "hold", "key turns (cut)", "mira,jax", cage_enter, snd="Gate clang; key in lock.")
s("6", "CHARACTER_STILL", [121], 0.8, "The Baron rises. It takes a while. He makes it look deliberate.", "tilt-up 5% as he rises", "rise: 2 stills cross-cut (seated wide crop, then this)", "baron", baron_rise)
s("6", "TWO_SHOT", [122, 123], 0.0, "Over Jax's shoulder to the Baron.", "hold", "breath", "jax,baron", ots_jax_baron)
s("6", "CHARACTER_STILL", [124], 0.3, "A bow, magnificent.", "slow push-in 4%", "coat flare held; dust", "baron", baron_bow)
s("6", "CHARACTER_STILL", [125], 0.2, "Jax: '…The swamp guy?'", "hold", "mouth patch (3 visemes)", "jax:m", jax_swamp, risk=("medium", "mouth patch on a comic beat"))
s("6", "CHARACTER_STILL", [126], 1.0, "The Baron takes it in the chest, like a soldier.", "very slow push-in 2%", "one long blink; brow lift", "baron", baron_eyes)
s("6", "TWO_SHOT", [127], 0.0, "Over Jax's shoulder.", "hold", "none", "jax,baron", ots_jax_baron)
s("6", "CHARACTER_STILL", [128], 0.0, "The Baron: by my pigtail, and my horse with me.", "push-in 6% from medium to MCU", "brow lift on 'horse'", "baron", baron_rise)
s("6", "INSERT", [129], 0.0, "Mira reads his tag: RESIDUE. DELISTED.", "hold", "tag swings 2 px", "", tag_button, comp="Tag text in code.")
s("6", "CHARACTER_STILL", [130], 0.0, "The Baron's eyes: liar, scoundrel, delicious, never residue.", "slow push-in 3%", "brow work: 3 brow positions by warp", "baron", baron_eyes)
s("6", "CHARACTER_STILL", [131, 132], 0.0, "The Baron, holding his dignity.", "hold", "breath", "baron", baron_rise)
s("6", "INSERT", [133, 134], 0.4, "He tilts the parcel to the light: labels on labels; on top, in looping brown ink, c/o the Baron von Munchausen, The Silver Hatchet.", "macro pan 6% up the labels", "light sweep across paper", "", parcel_tilt, comp="Top label lettered in code (looping brown ink).")
s("6", "CHARACTER_STILL", [135], 1.0, "Something private crosses his eyes, and goes.", "hold", "one blink; eye-line shift (warp)", "baron", baron_eyes)
s("6", "INSERT", [136], 0.0, "Mira's eye, huge behind the brass loupe, counting edges.", "hold", "eye darts (warp 3 positions)", "mira", loupe_eye)
s("6", "CHARACTER_STILL", [137], 0.0, "The Baron: thirty-two; one fell off in the spring.", "hold", "breath", "baron", baron_bow, comp="Crop to MCU of the bow still (upscaled).")
s("6", "CHARACTER_STILL", [138], 0.0, "The Baron listens to Jax's plan.", "hold", "blink", "baron", baron_eyes)
s("6", "INSERT", [139], 0.0, "Mira's hand lifts her customs key on its lanyard.", "hold", "key swings", "", mira_key)
s("6", "CHARACTER_STILL", [140, 141], 0.0, "He turns to the gate, grand: the lock from Riga.", "slow push-in 5% over the speech", "coat sways", "baron", baron_gate)
s("6", "INSERT", [], 2.6, "Two old fingers laid on the padlock. Waiting. Nothing.", "hold (deliberate stillness)", "none", "", fingers_lock, snd="Total silence under the score's held note.")
s("6", "INSERT", [], 1.4, "He taps it. Nothing.", "2-frame tap jolt", "none", "", fingers_lock, snd="Single dull tap.")
s("6", "INSERT", [], 2.0, "Behind him, the clock does not tick.", "hold", "none", "", clock_still, snd="Silence where a tick should be.")
s("6", "TWO_SHOT", [], 2.4, "Jax and Mira are careful not to look at each other.", "hold", "both blink, out of sync", "jax:m,mira:m", jax_mira_nolook, risk=("low", "silent two-shot"))
s("6", "CHARACTER_STILL", [143], 0.6, "Quiet, to the lock: 'You used to.'", "push-in 3%", "none", "baron", baron_gate)
s("6", "INSERT", [144], 0.0, "Mira's key.", "hold", "none", "", mira_key)
s("6", "CHARACTER_STILL", [145], 0.0, "The Baron: then it is loyal.", "hold", "brow lift", "baron", baron_eyes)
s("6", "INSERT", [(146, 0, 2.8)], 0.0, "Mira's wrist chimes: LOT 14 — PUBLIC SALE.", "hold", "display text animates", "", mira_wrist, comp="Wrist UI text in code.", snd="Wrist chime (customs, two-tone).")
s("6", "CHARACTER_STILL", [(146, 2.8, None), 147], 0.0, "The Baron hears himself listed for sale.", "slow push-in 3%", "breath", "baron", baron_rise)
s("6", "TWO_SHOT", [148], 0.0, "Over Jax's shoulder.", "hold", "none", "jax,baron", ots_jax_baron)
s("6", "SET_STILL", [149], 1.6, "He sits back down on his trunk and settles the parcel on his knee.", "slow push-in from wide to medium-wide 8%", "breath", "baron", cage_wide)

# ================================================================= 7 NOAKES'S OFFICE
office_wide = J("SET customs", "office_noakes_silhouette", ["office", "noakes", "jax"], "Noakes's office: a tired man in customs uniform stands in silhouette against a large pure-black window, back mostly to us; Jax Vale at the desk lays his wrist unit down; desk lamp, files.")
wrist_desk = J("PIP", "wrist_on_desk", ["pipW", "office"], "Insert: PIP's wrist unit unstrapped and lying lens-up on a cluttered office desk, amber lens glowing, desk lamp light.")
jax_office = J("Jax", "jax_office_amused", ["jax", "office"], "Medium shot of Jax Vale standing by an office desk, looking down at it, amused, face partly in shadow, mouth closed.")
door_mira = J("Mira", "mira_doorway_small", ["mira", "office"], "From inside a dim office: a small distant figure of Dr Mira Sen framed in a lit doorway, far away, standing very straight.")
noakes_turn = J("Noakes", "noakes_turning", ["noakes", "office"], "Noakes three-quarters from behind, turning his head toward a doorway, face in shadow, black window behind, tired shoulders.")
s("7", "SET_STILL", [151], 0.6, "A window onto the black crater; Noakes in silhouette against it. Jax lays his wrist comm on the desk, lens up.", "slow push-in 4%", "lamp flicker", "noakes,jax", office_wide, ft=FT["pole"]("Shackleton crop: lit rim, black pit, graded dark."), comp="Real polar plate in the office window.", snd="Office: clock-less, ventilation hum, distant PA.")
s("7", "INSERT", [152], 0.0, "PIP's light on the desk.", "push-in 3%", "lens glow with speech", "pip", wrist_desk)
s("7", "DATA_VISUAL", [(153, 0, 6.0)], 0.0, "Regulation 41(c), 1840, scrolls on Noakes's screen in copperplate.", "slow tilt down with the scroll", "text scrolls", "", "CODE")
s("7", "SET_STILL", [(153, 6.0, None), 154], 0.0, "Noakes in silhouette.", "push-in 4%", "none", "noakes", office_wide)
s("7", "INSERT", [155], 0.0, "PIP's light.", "hold", "lens glow", "pip", wrist_desk)
s("7", "CHARACTER_STILL", [156], 0.0, "Noakes half turns.", "hold", "none", "noakes", noakes_turn)
s("7", "INSERT", [157], 0.0, "PIP's light: the parcel of eels in Bristol.", "slow push-in 4%", "lens glow", "pip", wrist_desk)
s("7", "CHARACTER_STILL", [158, 159], 0.3, "Jax, amused.", "hold", "breath", "jax", jax_office)
s("7", "INSERT", [160, 161], 0.0, "PIP's light, offended.", "hold", "lens flares bright on 'concise'", "pip", wrist_desk)
s("7", "SET_STILL", [162], 0.0, "Noakes in silhouette: he can't spare a witness.", "hold", "none", "noakes", office_wide)
s("7", "SET_STILL", [163], 0.5, "Mira, small, in the doorway.", "slow push-in 3%", "corridor light flicker", "mira", door_mira, risk=("low", "tiny figure, mouth unreadable"))
s("7", "CHARACTER_STILL", [164], 0.0, "Noakes turns to her.", "hold", "none", "noakes", noakes_turn)
s("7", "SET_STILL", [165], 0.0, "Mira in the doorway.", "push-in 3%", "none", "mira", door_mira)
s("7", "CHARACTER_STILL", [], 0.9, "Noakes looks at her.", "hold", "none", "noakes", noakes_turn)
s("7", "INSERT", [], 0.8, "At the little amber light.", "hold", "glow", "pip", wrist_desk)
s("7", "SET_STILL", [166], 0.0, "Noakes: back by six, stamped at one minute past, nothing happens in between.", "slow push-in 4%", "none", "noakes,jax", office_wide)
s("7", "SET_STILL", [167], 0.0, "Mira in the doorway.", "hold", "none", "mira", door_mira)
s("7", "SET_STILL", [168, 169], 2.0, "The office, wide: 'Road trip.' 'Inventory.'", "slow pull-out 4%", "none", "noakes,jax", office_wide, snd="Caper button; END OF ACT ONE (2 s black optional).")

# ================================================================= 8 POST-CHAISE
rim_plate = J("EXT plates", "rim_road_plate", [], "Generated lunar terrain plate (not a photograph): a pale graded service road running along the bright white rim of a huge polar crater, the Sun sitting right on the horizon throwing very long hard shadows, on one side a slope dropping into total black shadow, black sky, no vehicles, no people.")
cab_back = J("SET post-chaise", "cab_from_back_seat", ["cab", "baron", "lucia", "jax"], "Inside an old rover cab, shot from the back seat looking forward through the windscreen: four heads in silhouette (a driver with short hair, a curly-haired man beside her, an old man in a tricorn hat behind, a woman with a dark braid), a red ribbon on the driver's wrist on the wheel; the windscreen is pure black.")
baron_point = J("Baron", "baron_arm_window", ["baron", "cab"], "Insert inside a rover cab: an old arm in a red coat sleeve with a lace cuff pointing grandly out of a pure-black side window.")
wheel_ribbon = J("Lucía", "hands_on_wheel", ["lucia", "cab"], "Insert: strong grease-stained hands on a worn rover steering wheel, a red ribbon tied round one wrist, bright glare from the windscreen.")
mira_cab_note = pages  # merged: reuse, no new image
lucia_driving = J("Lucía", "lucia_driving_from_behind", ["lucia", "cab"], "Lucía Ortega seen from behind and slightly right, driving the rover, hands on the wheel, her face turned away toward a pure-black windscreen.")
s("8", "REAL_FOOTAGE", [(172, 0, 4.0)], 1.0, "The real south pole from above: Shackleton's bright rim and black pit.", "slow push-in 6% toward the rim", "real still", "", "REAL", ft=FT["clem"]("Push toward Shackleton at the pole."), comp="Full frame, honest grade.", snd="Score: A2-style caper (new cue C1 'Post-chaise') starts.")
s("8", "SET_STILL", [(172, 4.0, None)], 2.0, "A white road on a white rim, the Sun on the horizon, a slope into ink; the Baron's rover crawls along, carved horse's head on the bonnet, LOT 14 trunk plainly on the roof rack.", "lateral parallax 6% (3 layers: foreground rocks, road, horizon); rover translates across", "rover translates; dust kicked up falls ballistically (no billowing)", "", rim_plate, assets=[REF["chaise"]["path"]],
  comp="GENERATED TERRAIN — NOT REAL FOOTAGE. Library post-chaise cut-out composited with contact shadow; trunk with LOT 14 tag readable in every wide.", snd="Exterior: no effects at all (vacuum). Score only.", risk=("medium", "a generated plate must not be passed off as real; ground-level pole view does not exist as a photograph"))
s("8", "SET_STILL", [173, 174, 175], 0.0, "The cab from the back seat: four heads, the tricorn, Lucía's ribbon on the wheel, the bright rim through the windscreen.", "handheld drift 1.5% + cabin bounce (2 Hz, 3 px)", "windscreen plate slides; bounce", "lucia,jax,mira,baron", cab_back, comp="Rim plate (generated) in the windscreen, moving.", snd="Cab: dry rover hum, rattles, the trunk thumping on the roof.", risk=("medium", "4 characters in one image, though all from behind"))
s("8", "INSERT", [176, 177], 0.0, "The Baron's lace cuff points out of the side window.", "hold", "plate slides past the window", "baron", baron_point, comp="Rim plate in the side window.")
s("8", "INSERT", [178], 0.0, "Lucía's ribbon on the wheel.", "hold; bounce", "wheel jiggle (warp)", "", wheel_ribbon)
s("8", "SET_STILL", [179, 180], 1.6, "The cab: 'There is no king.' 'Not any more.' That lands.", "slow push-in 3%", "bounce", "lucia,jax,mira,baron", cab_back)
s("8", "INSERT", [], 1.4, "Mira's pencil writes something down.", "hold", "write-on", "", mira_cab_note)
s("8", "SET_STILL", [181, 182, 183, 184], 0.0, "The cab, front seats.", "crop to front two; drift", "bounce", "lucia,jax", cab_back)
s("8", "CHARACTER_STILL", [185, 186], 0.0, "Lucía from behind, driving.", "hold; bounce", "wheel jiggle", "lucia", lucia_driving)
s("8", "SET_STILL", [187], 0.0, "The cab: Jax in the passenger seat.", "crop on Jax; drift", "bounce", "jax", cab_back)
s("8", "REAL_FOOTAGE", [188], 2.0, "The Sun at the pole, going round, not rising.", "footage move only", "real visualisation", "", "REAL", ft=FT["poleEarth"](0, 8, "Section where the Sun circles near the horizon."), comp="Full frame; Baron V.O. over it.", risk=("medium", "unverified plate"))

# ================================================================= 9 RIM / INN DOOR
inn_door = J("SET hatchet", "four_suits_iron_door", ["innx", "jaxH", "baronHT", "miraS", "luciaS"], "Four figures in pressure suits at a round iron door cut into crater rock, half in hard sunlight half in black shadow; one holds up a notebook and pencil; one wears a tricorn strapped on his helmet; faces small behind reflective visors.")
fist = J("Jax", "gloved_fist_knock", ["jaxH"], "Insert: a gloved pressure-suit fist mid-knock against a round riveted iron door, hard sunlight, black shadow.")
s("9", "REAL_FOOTAGE", [190], 2.0, "Over the bright rim, down to where the light ends.", "footage move only", "real", "", "REAL", ft=FT["fly"](20, 30, "Section descending toward the shadow line."), comp="Full frame.", snd="Silence: score only.", risk=("medium", "unverified plate"))
s("9", "SET_STILL", [], 3.0, "Cut into the crater wall, half in sun and half in dark: one lit window and a painted sign, THE SILVER HATCHET, its letters flaking one by one.", "slow push-in 5%", "window glow flickers; sign letters flake (code)", "", "LIB:innx", comp="Library exterior; sign lettering in code; tiny rover cut-out parked.", snd="Silence: score only.")
s("9", "SET_STILL", [], 1.4, "Four suited figures at a round iron door. Mira holds up her notebook.", "hold", "none", "jax,baron,mira,lucia", inn_door, risk=("high", "4 suited characters, 4 references: generate as two two-shots and layer if consistency fails"))
s("9", "INSERT", [], 2.4, "Jax's gloved fist knocks three times. The score stops. Not a sound.", "3 x 2-frame knock jolts", "none", "", fist, snd="SCORE DROPS OUT. Absolute silence for the knocks (the joke).")
s("9", "SET_STILL", [192, 193], 0.8, "The four at the door.", "push-in 4%", "none", "jax,baron,mira,lucia", inn_door, snd="Suit radio (narrow); silence under.")

# ================================================================= 10 PARLOUR
parl_wide = J("SET hatchet", "parlour_wide_group", ["parl", "baron", "jax", "lucia"], "Wide of a low inn parlour cut into rock, crowded with impossible objects (a stuffed bear, a sabre bent into a knot, a jar of very large teeth), a slow wedge of sunlight across the floor; the Baron leads two visitors in, all small in frame, faces turned away.")
bear2 = J("Props", "bear_two", ["parl"], "Insert: a second stuffed bear standing in the corner of a rock-walled parlour, wearing a faded hussar's jacket, glass eyes, a little lonely.")
pat_bear = bear2  # merged: reuse, no new image
baron_bear = J("Baron", "baron_with_bear", ["baron", "parl"], "Medium shot of the Baron standing beside a stuffed bear in a hussar's jacket, one hand on the bear's shoulder like an old friend, eyes amused.")
jax_parl = J("Jax", "jax_parlour_sceptic", ["jax", "parl"], "Medium shot of Jax Vale in a crowded rock parlour, sceptical, arms loosely folded, lips closed, eyes on someone off-frame.")
sun_wedge = J("SET hatchet", "sun_wedge_sofa", ["parl"], "A wedge of hard white sunlight lying across a rock floor toward an old velvet sofa in a dim crowded parlour, dust in the beam.")
stove_back = J("Baron+Lucía", "baron_stove_lucia", ["baron", "lucia", "parl"], "The Baron seen from behind addressing a squat iron stove with a raised hand; crouched at the stove's little door, unnoticed, Lucía Ortega with a spanner, face turned to the stove.")
flame = J("Props", "stove_blue_flame", ["parl", "lucia"], "Macro insert: a small blue flame catching inside a squat iron stove's open door, a spanner withdrawing from the frame.")
baron_warm = J("Baron", "baron_ecu_stove_light", ["baron"], "Extreme close-up of the Baron's eyes and brows above the white moustache, lit warm from below by a stove, a beat of wounded dignity.")
mira_watch = J("Mira", "mira_watching_parlour", ["mira", "parl"], "Medium shot of Dr Mira Sen in a crowded rock parlour seen through the old bevelled glass of a curio cabinet in the foreground (slight distortion and reflections over her face), watching someone off-frame with quiet attention, lips closed.")
s("10", "SET_STILL", [195], 1.6, "The parlour: every surface holds something impossible; a wedge of sunlight on the floor.", "slow push-in 5%; parallax on foreground junk", "dust in the sunbeam", "baron,jax,lucia", parl_wide, snd="Parlour: warm small-room tone, stove ticking cold.")
s("10", "INSERT", [196, 197, 198], 0.2, "There's another bear. Lucía's hand comes in and pats its head: 'Hello, lonely.'", "push-in 4%", "hand enters (cut-out from the ribbon-hand still)", "", bear2)
s("10", "CHARACTER_STILL", [199, 200], 0.0, "The Baron beside his bear.", "push-in 3%", "breath", "baron", baron_bear)
s("10", "CHARACTER_STILL", [201], 0.0, "Jax, sceptical.", "hold", "blink", "jax:m", jax_parl)
s("10", "SET_STILL", [202], 0.0, "The wedge of sunlight that reaches the sofa on the fourteenth.", "slow push-in 6% toward the sofa", "the wedge creeps 2% across the floor (animated mask)", "", sun_wedge)
s("10", "SET_STILL", [203], 0.0, "He turns to the stove. Behind him, unnoticed, Lucía crouches at its door with her spanner.", "hold", "breath", "baron,lucia", stove_back)
s("10", "INSERT", [], 1.0, "A blue flame catches. Lucía's spanner withdraws.", "hold", "flame flicker (code element)", "", flame, snd="Gas whump, small.")
s("10", "CHARACTER_STILL", [205, 206, 207], 0.6, "A beat. 'It prefers her.' 'Pilot was blocked.' 'Of course it was.'", "very slow push-in 3%", "brow lift on 'Of course'", "baron", baron_warm)
s("10", "CHARACTER_STILL", [], 1.4, "Mira watches him.", "push-in 3%", "blink", "mira:m", mira_watch)
s("10", "CHARACTER_STILL", [], 1.4, "Jax watches Mira watching him.", "push-in 3%", "eye-line shift (warp)", "jax:m", jax_parl)

# ================================================================= 11 SIGNATURE
slip = J("Props", "delivery_slip_finger", ["jax", "parl"], "Insert: a blank delivery slip on an old wooden table, a man's finger in a burnt-orange cuff on the signature line, a pen beside it.")
cuff = J("Baron", "lace_cuff_pen", ["baron"], "Insert: an old hand in a lace cuff writing with a pen on a blank slip, long flourishes, lamp light.")
baron_down = baron_eyes  # merged: reuse, no new image
s("11", "INSERT", [209, 210], 0.0, "A delivery slip; Jax's finger on the line.", "hold", "none", "", slip)
s("11", "INSERT", [211, 212], 0.4, "A lace cuff. The pen moves for a long time.", "slow pan 6% with the pen", "pen moves (cut-out)", "", cuff)
s("11", "INSERT", [], 3.0, "The signature, wet and magnificent. One second. Then it fades, stroke by stroke, to blank paper.", "hold", "signature fade (code)", "", slip, snd="Silence; a tiny glassy shimmer as it fades.")
s("11", "INSERT", [214], 2.0, "He does it again. It fades faster.", "hold", "faster fade", "", slip)
s("11", "CHARACTER_STILL", [215, 216], 0.0, "The Baron: never signed smaller in my life.", "hold", "brow lift", "baron", baron_warm)
s("11", "INSERT", [(217, 0, 4.5)], 0.0, "PIP's light on the table.", "hold", "lens glow", "pip", wrist_desk, comp="Regrade warm for the parlour table.")
s("11", "SET_STILL", [(217, 4.5, None)], 0.0, "The parlour table: three of them around the clean paper.", "slow push-in 4%", "none", "baron,jax,lucia", parl_wide, comp="Crop of the parlour wide.")
s("11", "CHARACTER_STILL", [218], 1.0, "The Baron looks at the clean paper: the treaty still signed in Constantinople.", "very slow push-in 2%", "blink", "baron", baron_down)

# ================================================================= 12 NOAKES + CHICHIKOV
box_open = J("Chichikov", "inlaid_box_open_contracts", ["box", "chich"], "Macro insert: a small inlaid wooden travelling box opening in grey-gloved hands; inside, in neat compartments, dozens of small contracts each tied with ribbon.")
noakes_desk = J("Noakes+Chichikov", "noakes_back_chich_soft", ["noakes", "chich", "office"], "Noakes seated at his office desk seen from behind; across the desk, deeply out of focus, a plump grey man in an overcoat; black window behind.")
chich_refl = noakes_desk  # merged: reuse, no new image
pen_hover = J("Noakes", "pen_hovering", ["noakes", "office"], "Insert: a tired man's hand holding a pen hovering over the signature line of a contract on an office desk, not yet touching.")
s("12", "INSERT", [220], 1.4, "A small inlaid travelling box opens: contracts, dozens, each tied with ribbon.", "push-in 5%", "lid opens (cut-out rotate)", "", box_open, snd="Voss motif (M4) enters, pizzicato.")
s("12", "SET_STILL", [221, 222, 223], 0.0, "Noakes's back; Chichikov soft across the desk.", "slow push-in 4% over the shot", "steam", "noakes,chichikov", noakes_desk)
s("12", "CHARACTER_STILL", [224, 225], 0.0, "Chichikov, soft, across the desk: 'And who listens?'", "rack toward him, never sharp", "steam", "chichikov", chich_refl)
s("12", "INSERT", [226], 3.0, "Noakes's pen hovers over the line, long enough to be an answer.", "hold (the hover is the joke)", "pen trembles 1 px", "", pen_hover, snd="Score holds one note.")
s("12", "SET_STILL", [227, 228], 0.0, "Noakes's back, Chichikov soft.", "hold", "none", "noakes,chichikov", noakes_desk)
s("12", "CHARACTER_STILL", [229], 0.0, "Chichikov, soft: 'I like to be early.'", "slow drift", "none", "chichikov", chich_refl)
s("12", "INSERT", [230, 231], 0.6, "Noakes signs.", "hold", "pen moves (cut-out)", "", pen_hover)

# ================================================================= 13 MONTAGE
tags = J("Mira", "mira_ties_tags", ["mira", "parl"], "Insert: ink-stained hands tying a brown luggage tag onto an old object with string, writing on the tag with a pencil, lamp light, crowded shelf.")
saddle = J("Props", "half_saddle_laurel", ["parl"], "Insert: half of an old leather saddle cut clean through, a living laurel branch growing out of the leather, on a rock shelf.")
rope = J("Props", "straw_rope", ["parl"], "Insert: a coil of old twisted straw rope about three metres long on a rock shelf, its end cut and re-knotted many times.")
hatchet_wall = "LIB:hatchet"  # merged: reuse, no new image
hatchet_hand = J("Jax", "jax_hand_hatchet", ["jax", "hatchet"], "Insert: a man's hand in a burnt-orange cuff lifting a small dented silver hatchet off a wall, weighing it in his palm as if it belongs there.")
s("13", "INSERT", [], 2.0, "Mira's hands tie tag after tag.", "push-in 4%", "hands move between 2 crops", "", tags, snd="New cue C2: the harpsichord that has gone slightly wrong.")
s("13", "INSERT", [233], 0.0, "Half a saddle, a laurel growing out of the leather.", "slow push-in 5%", "leaf flutter (slight warp)", "", saddle)
s("13", "INSERT", [234, 235, 236], 0.0, "Her tag: SADDLE. HALF. PLANT GROWING FROM IT.", "hold", "write-on", "", tags)
s("13", "INSERT", [237], 0.0, "A coil of old straw rope.", "slow pan 5%", "none", "", rope)
s("13", "INSERT", [238], 0.0, "Her tag: ROPE. 3 M.", "hold", "write-on", "", tags)
s("13", "INSERT", [239, 240, 241], 0.0, "The rope's end, cut and re-tied many times.", "macro pan 6%", "none", "", rope)
s("13", "INSERT", [], 1.0, "On the wall, a small silver hatchet, dented.", "hold", "glint", "", hatchet_wall)
s("13", "INSERT", [(243, 0, 4.0)], 0.0, "Jax's hand lifts it down and weighs it without thinking.", "slow push-in 4%", "hand dips (warp)", "", hatchet_hand)
s("13", "INSERT", [(243, 4.0, None)], 0.0, "It sits in his palm as if it has been waiting for him.", "macro push-in 6%", "glint", "", hatchet_hand)
s("13", "INSERT", [244, 245], 0.0, "Her tag: HATCHET. SILVER. DENTED.", "hold", "write-on", "", tags)
s("13", "CHARACTER_STILL", [], 2.0, "The Baron's eyes above the moustache, watching Jax's hand.", "very slow push-in 2%", "eye-line shift", "baron", baron_eyes)
s("13", "INSERT", [], 2.4, "Her tag on the saddle: she crosses out PLANT and writes LAUREL.", "hold", "strike-through and write-on", "", tags, snd="Harpsichord resolves (wrongly, sweetly).")

# ================================================================= 14 PROVE ONE
arms = J("Lucía", "lucia_arms_folded", ["lucia"], "Insert: a strong woman's arms folded across grease-stained coveralls, a red ribbon on one wrist, chest height, face out of frame.")
pigtail = J("Baron", "baron_back_pigtail", ["baron", "parl"], "The Baron seen from behind, both old fists gripping his own grey pigtail above his head, straining upward, tricorn askew, red coat taut.")
hair_wide = J("Baron", "baron_alone_wide_hair", ["baron", "parl"], "Wide: an old man in a red coat alone in the middle of a crowded rock parlour, holding his own pigtail up in both fists, boots flat on the floor, going nowhere; sunlight wedge on the floor.")
baron_sofa = J("Baron", "baron_seated_sofa", ["baron", "parl"], "The Baron seated on an old velvet sofa, deflated, tricorn in his lap, eyes down, moustache hiding his mouth.")
arms_drop = J("Lucía", "lucia_arms_unfold", ["lucia"], "Insert: a strong woman's arms unfolding and dropping to her sides, red ribbon on one wrist, coveralls, face out of frame.")
s("14", "INSERT", [247, 248], 0.0, "Lucía's arms, folded.", "hold", "breath", "", arms)
s("14", "CHARACTER_STILL", [249], 0.0, "The Baron's eyes as she sets the terms.", "slow push-in 3%", "blink", "baron", baron_warm)
s("14", "CHARACTER_STILL", [250], 0.0, "The Baron: horribly fair.", "hold", "breath", "baron", baron_bear)
s("14", "CHARACTER_STILL", [251], 0.0, "From behind: he takes hold of his pigtail in both fists.", "slow push-in 4%", "breath", "baron", pigtail)
s("14", "CHARACTER_STILL", [], 1.8, "He heaves. His boots stay on the floor. He heaves again.", "2 strain pulses (1.5% scale)", "tremor", "baron", pigtail, snd="Effort breaths (Baron VO, wordless).")
s("14", "SET_STILL", [], 9.0, "WIDE (HELD): an old man in the middle of a room on the Moon, holding his own hair, going nowhere.", "hold, 1.5% creep only", "dust in the sun wedge; nothing else", "baron", hair_wide, snd="NO SCORE. Room tone only.", risk=("low", "deliberate hold"))
s("14", "CHARACTER_STILL", [253], 0.0, "He lets go. 'One-sixth gravity.'", "hold", "none", "baron", baron_down)
s("14", "CHARACTER_STILL", [254], 0.0, "He sits. The post stopped coming; then the stories.", "slow push-in 3%", "breath", "baron", baron_sofa)
s("14", "INSERT", [255], 0.0, "Lucía's arms.", "hold", "none", "", arms)
s("14", "CHARACTER_STILL", [256], 0.0, "'A story no one believed in time.'", "very slow push-in 2%", "blink", "baron", baron_warm)
s("14", "INSERT", [257], 0.0, "Her arms unfold.", "hold", "none", "", arms_drop, snd="A4 emotional cue enters (2 bars).")
s("14", "CHARACTER_STILL", [258], 1.4, "'It has been years since anyone asked.'", "hold", "none", "baron", baron_sofa)

# ================================================================= 15 COLD STORE
cold_door = J("SET hatchet", "coldstore_group_back", ["cold", "baron", "jax", "lucia", "mira"], "A heavy door open on a rock room white with frost, a thick window in the far wall that is pure black; four figures seen from behind in the doorway, breath clouding.")
cold_win = J("SET hatchet", "frost_window_frame", ["cold"], "Close: a thick frost-rimmed window in a rock wall, the glass pure black, ice crystals on the frame.")
mira_fog = J("Mira", "mira_breath_fog", ["mira", "cold"], "Medium close-up of Dr Mira Sen in a frost-white room, the brass loupe raised to one eye, a cloud of her own breath hiding her mouth and chin.")
baron_frost = J("Baron", "baron_frost", ["baron", "cold"], "Close-up of the Baron in a frost-white room, frost on his moustache and brows, breath steaming, eyes shining.")
horn_frost = J("Props", "post_horn_frost", ["horn", "baron"], "Insert: old hands in lace cuffs lifting a brass post horn completely white with frost off a frosted shelf.")
jax_fog = J("Jax", "jax_breath_fog", ["jax", "cold"], "Medium close-up of Jax Vale in a frost-white room, his breath clouding in front of his mouth, sceptical eyes.")
lucia_fog = J("Lucía", "lucia_breath_fog", ["lucia", "cold"], "Medium close-up of Lucía Ortega in a frost-white room, arms wrapped round herself, breath clouding over her mouth.")
horn_drip = J("Props", "horn_sweating_drip", ["horn"], "Macro insert: frost melting on a brass post horn's bell beside a blue flame, a single drop of water running down the brass.")
group_march = J("Group", "four_round_stove_still", ["baron", "jax", "lucia", "mira", "parl"], "Wide: four people frozen still around a squat iron stove in a crowded rock parlour, an old man in a tricorn holding a brass post horn, the others staring at it in astonishment.")
horn_stove = group_march  # merged: reuse, no new image
lucia_laugh = J("Lucía", "lucia_laugh_shocked", ["lucia", "parl"], "Close-up of Lucía Ortega laughing once in shock, one hand flying to cover her mouth, eyes wide.")
loupe_bell = loupe_eye  # merged: reuse, no new image
pip_wrist_glow = J("PIP", "wrist_glow_soft", ["pipW", "jax"], "Insert: PIP's wrist unit on a burnt-orange sleeve in a dim warm parlour, the amber lens glowing soft and steady.")
mira_bare = J("Mira", "mira_bare_eyes_loupe_falls", ["mira", "parl"], "Close-up of Dr Mira Sen's bare eyes (frame cuts at the nose) as a brass loupe drops away on its chain, her gaze soft and astonished for the first time.")
s("15", "SET_STILL", [260], 2.4, "A heavy door opens on a room cut into rock, white with frost. Their breath clouds.", "slow push-in 4%", "breath fog particles drift (code)", "baron,jax,lucia,mira", cold_door, snd="Frost crackle; a deep cold hum; door seal unsticks.", risk=("medium", "4 figures, all from behind"))
s("15", "SET_STILL", [261], 0.0, "The thick window looks down on ground that has never seen the Sun.", "slow push-in 4%", "frost creeps 1% at the edge", "", cold_win, ft=FT["psr"](0, 8, "LRO's scattered-light view into permanent shadow."), comp="Real PSR plate inside the frost frame.", risk=("medium", "unverified plate"))
s("15", "CHARACTER_STILL", [262], 0.0, "Mira: 'Probably. Not certainly.' Her breath hides her mouth.", "hold", "breath fog animated over the mouth", "mira", mira_fog)
s("15", "CHARACTER_STILL", [263], 0.0, "The Baron, frost on his moustache: 'as if it were a ruling'.", "hold", "breath steam", "baron", baron_frost)
s("15", "INSERT", [264], 0.0, "From a shelf he lifts a brass post horn, white with frost.", "slow push-in 5%", "frost sparkle", "", horn_frost)
s("15", "CHARACTER_STILL", [265], 0.0, "Jax: 'Tunes don't freeze.'", "hold", "breath fog over mouth", "jax", jax_fog)
s("15", "CHARACTER_STILL", [266], 0.0, "'Not where you are from.'", "hold", "steam", "baron", baron_frost)
s("15", "CHARACTER_STILL", [267], 0.0, "Lucía: where's the postilion now?", "hold", "breath fog", "lucia", lucia_fog)
s("15", "CHARACTER_STILL", [268], 0.0, "'Married a baker in Riga.'", "slow push-in 3%", "steam", "baron", baron_frost)
s("15", "SET_STILL", [], 2.0, "He carries it back through to the stove and holds it near the blue flame.", "hold", "flame flicker", "baron", horn_stove)
s("15", "INSERT", [], 3.0, "The frost on the brass sweats. A drop runs down the bell.", "macro push-in 4%", "drop runs (code); frost recedes (animated mask)", "", horn_drip, snd="Tiny drip.")
s("15", "INSERT", [], 1.0, "A small crack of ice.", "1-frame jolt", "none", "", horn_drip, snd="SFX: ice crack (sharp, small).")
s("15", "SET_STILL", [], 7.0, "Then — tereng! tereng! — a bright, slightly out-of-tune march fills the room out of a horn no one is blowing. No one moves.", "hold, 1% push only", "breath fog; flame", "baron,jax:m,lucia:m,mira:m", group_march, snd="New cue C3: the frozen post-horn march (diegetic).", risk=("high", "four faces in one still; build as layers from approved singles if needed"))
s("15", "CHARACTER_STILL", [], 1.8, "Lucía laughs once, shocked.", "hold", "shoulder jolt", "lucia", lucia_laugh, snd="Lucía laugh (needs a recorded or built laugh).")
s("15", "INSERT", [270], 0.0, "Mira's eye, huge in the loupe, looks into the bell.", "hold", "eye darts", "mira", loupe_bell)
s("15", "CHARACTER_STILL", [271], 0.0, "'There was a postilion in it.'", "slow push-in 3%", "none", "baron", baron_warm)
s("15", "INSERT", [272, 273, 274], 0.0, "On Jax's wrist, PIP's light glows soft and steady.", "very slow push-in 3%", "lens glow pulses with 'the post'", "pip", pip_wrist_glow, snd="PIP motif (M3) as two soft notes under the march.")
s("15", "SET_STILL", [275], 1.8, "The march stumbles to its last note.", "hold", "none", "baron,jax:m,lucia:m,mira:m", group_march)
s("15", "CHARACTER_STILL", [276], 0.0, "She lets the loupe fall and looks with her own eye.", "hold", "loupe drop: 2-frame fall + chain swing", "mira", mira_bare)
s("15", "CHARACTER_STILL", [277], 1.4, "'No. That is what it's for.'", "hold", "none", "baron", baron_warm)

# ================================================================= 16 OFFER
chich_corner = J("Chichikov", "chich_corner_behind_bear", ["chich", "parl"], "Deep in a crowded rock parlour, in a corner chair behind a stuffed bear, a plump man in grey with a teacup, soft as a smudge, completely out of focus; foreground clutter sharp.")
jax_turn = jax_parl  # merged: reuse, no new image
card_num = J("Chichikov", "card_slid_number", ["chich", "parl"], "Insert: a cream card slid across an old wooden table by a grey-gloved hand, a number on it (illegible).")
mira_seated = mira_watch  # merged: reuse, no new image
baron_hope = baron_warm  # merged: reuse, no new image
lucia_seated = J("Lucía", "lucia_seated_listening", ["lucia", "parl"], "Medium shot of Lucía Ortega seated forward with forearms on her knees, listening hard, lips closed, red ribbon at her wrist.")
ribbon_close = J("Lucía", "hand_closes_ribbon", ["lucia"], "Insert: a strong hand closing tight round a red ribbon tied at the other wrist.")
contract_arrows = slip  # merged: reuse, no new image
s("16", "SET_STILL", [279, 280], 0.6, "They turn. In the corner chair behind the second bear, soft as a smudge: Chichikov, with a teacup.", "rack focus that never finds him", "steam", "chichikov", chich_corner, snd="Voss motif (M4), soft.")
s("16", "CHARACTER_STILL", [281], 0.0, "Jax, startled, listening.", "hold", "blink", "jax:m", jax_turn)
s("16", "INSERT", [282], 0.0, "PIP on the wrist.", "hold", "lens glow", "pip", pip_wrist_glow)
s("16", "DATA_VISUAL", [], 1.4, "PIP's screen: REPORT #1,206 — RE: MAN, AVERAGE.", "hold", "text stamps on", img="CODE")
s("16", "SET_STILL", [283], 0.0, "Chichikov, soft: the carriage of your parcel, under contract to Voss.", "hold", "steam", "chichikov", chich_corner)
s("16", "INSERT", [284], 0.0, "A card slid across the table. A number.", "push-in 5%", "card slides (cut-out)", "", card_num, comp="Number in code.")
s("16", "CHARACTER_STILL", [285, 286], 0.0, "Jax reads it.", "hold", "none", "jax:m", jax_turn)
s("16", "CHARACTER_STILL", [(287, 0, 5.0)], 0.0, "Mira listens: 'The box, Dr Sen. Not the door.'", "slow push-in 3%", "blink", "mira:m", mira_seated)
s("16", "CHARACTER_STILL", [(287, 5.0, None)], 0.0, "Jax listening.", "hold", "none", "jax:m", jax_turn)
s("16", "SET_STILL", [288], 0.4, "The soft grey shape makes a small bow.", "1% drift", "none", "chichikov", chich_corner)
s("16", "CHARACTER_STILL", [289], 0.0, "The Baron's eyes: four audiences a day.", "slow push-in 4%", "eyes widen (warp)", "baron", baron_warm)
s("16", "CHARACTER_STILL", [290, 291, 292], 0.0, "'To the end?'", "hold", "glisten (highlight pulse)", "baron", baron_hope)
s("16", "CHARACTER_STILL", [293], 0.0, "Lucía listens: 'For a story, it is a feast.'", "hold", "breath", "lucia:m", lucia_seated)
s("16", "SET_STILL", [294], 0.0, "Chichikov: both signatures, or neither.", "hold", "steam", "chichikov", chich_corner)
s("16", "CHARACTER_STILL", [(295, 0, 5.0)], 0.0, "Lucía hears her mother's account read aloud.", "slow push-in 4%", "jaw tightens (warp)", "lucia:m", lucia_seated)
s("16", "INSERT", [(295, 5.0, None)], 0.0, "Lucía's hand closes on the ribbon at her wrist.", "hold", "grip tightens", "", ribbon_close)
s("16", "SET_STILL", [296, 297], 0.0, "The soft shape: 'We supply her water.'", "hold", "none", "chichikov", chich_corner)
s("16", "SET_STILL", [], 1.0, "He rises, a soft grey shape.", "the soft shape lifts 30 px (cut-out)", "none", "chichikov", chich_corner)
s("16", "INSERT", [298], 2.0, "Where he sat: the contract, with little arrows drawn in the margin.", "slow push-in 5%", "none", "", contract_arrows, snd="Voss motif button; END OF ACT TWO.")

# ================================================================= 17 CLIMBING BACK
ink_stays = J("Props", "contract_signature_page", ["hall"], "Insert: a contract page on a steel desk with a blank signature line, a pen resting on it, hall lights.")
date_loupe = ink_stays  # merged
mira_contract = J("Mira", "mira_cab_contract_ots", ["mira", "cab"], "Over the shoulder from behind Dr Mira Sen in a rover's back seat: a contract on her knee, the brass loupe raised in her hand, hard white glare through the window.")
baron_cab = J("Baron", "baron_cab_glare", ["baron", "cab"], "Close-up of the Baron in a rover's back seat, white glare across the side window, eyes tired, moustache hiding his mouth.")

s("17", "REAL_FOOTAGE", [301], 1.6, "Out of the shadow into glare: the real sunlit rim, white.", "slow push-in 4%", "real still", "", "REAL", ft=FT["clem"]("Crop on the sunlit rim, overexposed toward white."), comp="Full frame.", snd="Lucía's 'Take it.' dry from the cab over the exterior (O.S.).")
s("17", "SET_STILL", [(302, 0, 4.5)], 0.0, "From the back seat, through the windscreen, the cab climbs into a blinding white plate. Inside, noise.", "handheld drift 1.5%; bounce", "plate overexposes (code)", "lucia,jax,mira,baron", cab_back, comp="Rim plate pushed to white glare.", snd="Rover cabin hum under strain; Lucía dry.")
s("17", "SET_STILL", [(302, 4.5, None)], 0.0, "Jax's head, very still.", "crop on Jax; slow push 3%", "none (he does not move)", "jax", cab_back)
s("17", "CHARACTER_STILL", [303], 0.0, "Mira, contract on her knee.", "hold", "bounce", "mira", mira_contract)
s("17", "CHARACTER_STILL", [304], 0.0, "Lucía from behind, driving.", "hold", "wheel jiggle", "lucia", lucia_driving)
s("17", "CHARACTER_STILL", [305, 306], 0.0, "The Baron: 'She is right.' Lucía: 'Say something.'", "hold", "none", "baron", baron_cab)
s("17", "SET_STILL", [], 1.8, "Jax says nothing. That's worse.", "push-in 4% on Jax", "none", "jax", cab_back)
s("17", "CHARACTER_STILL", [307], 0.0, "Lucía: 'I'd just rather not do it for free.'", "hold", "none", "lucia", lucia_driving)
s("17", "INSERT", [], 2.0, "Through the loupe, a date at the foot of the contract swims into focus: 24th.", "rack focus from blur to sharp (code)", "loupe vignette", "", date_loupe, comp="Date '24th' in code.")
s("17", "CHARACTER_STILL", [309, 310], 0.0, "Mira, loupe lowered.", "hold", "none", "mira", mira_contract)
s("17", "SET_STILL", [311], 0.0, "The cab: they bought the wreck before they sank the ship.", "slow push-in 3%", "bounce", "lucia,jax,mira,baron", cab_back)
s("17", "SET_STILL", [], 2.0, "Silence. The engine.", "hold", "bounce", "lucia,jax,mira,baron", cab_back, snd="Engine only, no score.")
s("17", "CHARACTER_STILL", [312, 313], 1.0, "Lucía, quieter. The Baron: 'On the twenty-fourth I was making jam.'", "slow push-in 3%", "none", "baron", baron_cab)

# ================================================================= 18-19
noakes_hands = J("Noakes", "noakes_hands_contract", ["noakes", "office"], "Insert: a tired man's hands holding a contract on an office desk, the paper trembling very slightly, desk lamp.")
office_mira = J("Noakes+Mira", "noakes_back_mira_beyond", ["noakes", "mira", "office"], "Noakes seated at his desk seen from behind; beyond the desk, in soft focus, Dr Mira Sen standing straight with her hands clasped; black window to one side.")
stamp_out = noakes_hands  # merged: reuse, no new image
stamp_take = J("Props", "stamp_abandoned_face", ["stamp", "mira"], "Insert: an ink-stained woman's hand holding a heavy brass customs stamp face-up, the rubber face shows reversed block letters (illegible), lamp light.")
corr_backs = J("SET customs", "corridor_two_backs", ["corr", "mira", "jax"], "A long customs corridor with a long window onto a pure-black exterior; Dr Mira Sen and Jax Vale walking away from camera side by side, two backs.")
corr_refl = J("SET customs", "corridor_two_reflections", ["corr", "mira", "jax"], "Two faint reflections side by side in a long black corridor window, a woman with a dark braid and a curly-haired man, ghostly over the black.")
corr_refl_jax = J("SET customs", "corridor_reflection_jax_alone", ["corr", "jax"], "One faint reflection of a curly-haired man alone in a long black corridor window, ghostly over the black, the space beside him empty.")
s("18–19", "INSERT", [315], 1.6, "Noakes's hands on the contract. A long read. The paper trembles, very slightly.", "slow push-in 3%", "tremor (1 px)", "", noakes_hands, snd="Office tone; Mira motif hint.")
s("18–19", "SET_STILL", [316, 317, 318], 0.0, "Noakes's back; Mira beyond, soft.", "hold", "none", "noakes,mira", office_mira, risk=("low", "Mira soft and mid-ground"))
s("18–19", "INSERT", [319], 0.0, "His hands on the paper: three floors below the Voss Company.", "slow push-in 4%", "tremor", "", noakes_hands)
s("18–19", "SET_STILL", [320], 0.0, "Noakes's back, Mira beyond.", "hold", "none", "noakes,mira", office_mira)
s("18–19", "SET_STILL", [321], 0.0, "Noakes in silhouette against the crater window: keep being right in private.", "slow push-in 3%", "none", "noakes", office_wide, ft=FT["pole"]())
s("18–19", "INSERT", [322], 0.0, "He holds out the stamp.", "hold", "stamp slides across (cut-out)", "", stamp_out, assets=[REF["stamp"]["path"]], comp="Library stamp prop cut-out composited into Noakes's hands still.")
s("18–19", "SET_STILL", [323, 324, 325], 0.0, "Noakes's back, Mira beyond: 'the polite word for one'.", "push-in 4%", "none", "noakes,mira", office_mira)
s("18–19", "INSERT", [], 2.0, "She takes the stamp: ABANDONED, back to front on its rubber face, in her ink-stained hand.", "hold", "none", "", stamp_take, comp="Reversed ABANDONED in code.")
s("18–19", "SET_STILL", [327, 328, 329], 0.0, "The long corridor, a window onto the dark crater. Two backs walking.", "slow tracking push 5% (walking pace)", "walk bob 2 px", "mira,jax", corr_backs, ft=FT["pole"](), comp="Real polar plate in the long window.", snd="Footsteps, hall reverb.")
s("18–19", "SET_STILL", [330], 0.0, "Tighter on the two backs.", "push-in 4%", "walk bob", "mira,jax", corr_backs)
s("18–19", "SET_STILL", [331], 0.0, "Jax's back.", "crop on Jax", "walk bob", "jax", corr_backs)
s("18–19", "SET_STILL", [332, 333], 0.0, "The two backs and the long black window.", "slow pull-out 4%", "walk bob", "mira,jax", corr_backs)
s("18–19", "SET_STILL", [334, 335], 0.0, "She stops.", "hold", "none (stopped)", "mira,jax", corr_backs)
s("18–19", "CHARACTER_STILL", [], 2.4, "In the glass, two reflections side by side over the black. His has no answer ready, for once.", "very slow push-in 2%", "reflections breathe", "mira:m,jax:m", corr_refl, risk=("low", "silent beat, as staged"))
s("18–19", "SET_STILL", [336, 337], 0.0, "Jax's back.", "crop on Jax, push 3%", "none", "jax", corr_backs)
s("18–19", "SET_STILL", [338], 0.0, "The two backs.", "hold", "none", "mira,jax", corr_backs)
s("18–19", "CHARACTER_STILL", [], 3.0, "Her reflection walks out of the glass. His stays.", "hold", "her reflection dissolves out (cross-fade between the two reflection stills)", "jax:m", corr_refl_jax, snd="Mira motif (M2) phrase, then air.")

# ================================================================= 20 HOLD
kitbag = J("Lucía", "kitbag_rammed", ["lucia", "hold"], "Insert: clothes rammed hard into an old kit bag by strong hands with a red ribbon on one wrist.")
hold_pack = J("SET hold", "hold_lucia_packing_jax_hatch", ["hold", "lucia", "jax", "parcel"], "Cargo hold: Lucía Ortega seen from behind packing a kit bag in the foreground; the brown-paper parcel strapped down in the middle of the frame; Jax Vale a dark silhouette in the bright hatchway beyond.")
jax_hatch = J("Jax", "jax_silhouette_hatch", ["jax", "hold"], "Jax Vale as a dark silhouette in a bright cargo-hold hatchway, shoulders slumped, face unreadable.")
lucia_turn = J("Lucía", "lucia_turned_arms_folded", ["lucia", "hold"], "Medium shot of Lucía Ortega turned to face camera in a cargo hold, arms folded, jaw set, lips pressed shut, red ribbon visible.")
s("20", "INSERT", [], 1.0, "Clothes rammed into a kit bag.", "hold", "2 cuts of the hand", "", kitbag, snd="Hard fabric stuffing; zip.")
s("20", "SET_STILL", [340], 0.0, "Lucía, back to us, packing; Jax a silhouette in the hatch; the parcel in the middle of it all.", "slow push-in 3%", "lamp flicker", "lucia,jax", hold_pack)
s("20", "CHARACTER_STILL", [341], 0.0, "Jax in the hatch.", "hold", "none", "jax", jax_hatch)
s("20", "SET_STILL", [342], 0.0, "Lucía packing.", "hold", "arm move (2 crops)", "lucia,jax", hold_pack)
s("20", "CHARACTER_STILL", [343], 0.0, "Jax in the hatch, promising.", "slow push-in 4%", "none", "jax", jax_hatch)
s("20", "CHARACTER_STILL", [], 1.4, "She stops. Turns. Folds her arms. Lets him run out.", "hold", "none", "lucia:m", lucia_turn)
s("20", "CHARACTER_STILL", [344], 0.0, "Jax in the hatch takes it.", "hold", "none", "jax", jax_hatch)
s("20", "INSERT", [(345, 0, 6.0)], 0.0, "PIP's lamp brightens on the wall.", "hold", "lens glow", "pip", pip_hold)
s("20", "INSERT", [(345, 6.0, None)], 0.0, "The parcel. Posted thirty-two times.", "slow push-in 4%", "faint warmth shimmer", "", "LIB:parcel")
s("20", "INSERT", [346, 347], 0.0, "PIP's lamp dims.", "hold", "glow dims", "pip", pip_hold)
s("20", "CHARACTER_STILL", [348], 0.0, "Jax looks at the parcel. At her bag.", "hold", "eye-line (none visible)", "jax", jax_hatch)
s("20", "SET_STILL", [349], 2.0, "'Good.' She doesn't look as if it is. She doesn't unpack, either.", "slow pull-out 3%", "none", "lucia,jax", hold_pack)

# ================================================================= 21 OUTER RIM
boulder = J("EXT plates", "boulder_two_backs", ["jaxH", "baronHT"], "Generated lunar exterior (not a photograph): two figures in pressure suits sitting on a boulder at the edge of a vast black crater, backs to us, one with a tricorn hat strapped absurdly on top of his helmet; ahead, empty black sky low over a bright grey horizon.")
baron_visor = J("Baron", "baron_visor_close", ["baronHT", "baron"], "Close-up of the Baron's helmet visor: behind the glass his white moustache is a white shape and his eyes are bright; the visor reflects a small blue Earth low on a grey horizon; tricorn strapped on top.")
jax_visor = J("Jax", "jax_visor_close", ["jaxH", "jax"], "Close-up of Jax Vale's helmet visor three-quarter front, strong reflections across the lower visor hiding his mouth, his eyes visible, hard low sunlight.")
tricorn_helmet = "LIB:baronHT"  # merged: reuse, no new image
jax_laugh = boulder  # merged: reuse, no new image
boulder_xw = J("EXT plates", "boulder_extreme_wide", ["jaxH", "baronHT"], "Generated lunar exterior (not a photograph), extreme wide: two tiny suited figures on a boulder at the lip of a vast crater full of black shadow, empty black sky over a long bright horizon.")
hatchet_pass = J("Props", "gloved_hands_hatchet", ["hatchet", "baronHT", "jaxH"], "Insert: two pairs of pressure-suit gloves, one patched and old, passing a small dented silver hatchet from one to the other, hard sunlight.")
s("21", "REAL_FOOTAGE", [], 4.0, "Earth, low and half-lit on the horizon of the south pole.", "footage move only", "real", "", "REAL", ft=FT["poleEarth"](10, 20), comp="Full frame.", snd="A click. Private channel. Score: A4 emotional (v2) very low.", risk=("medium", "unverified; preferred SVS 4944 not logged"))
s("21", "SET_STILL", [351], 0.0, "Two suited figures on a boulder at the edge of the world, backs to us; the tricorn strapped on the Baron's helmet; Earth low ahead.", "slow push-in 3%", "Earth shimmer none (vacuum); dust still", "jax,baron", boulder, ft=FT["earth"](), comp="GENERATED TERRAIN — NOT REAL FOOTAGE; real Earth disc composited low on the horizon (size: about 2 degrees, i.e. large).", snd="Suit radio, private channel (narrow, intimate). No exterior sound.", risk=("medium", "honesty label; Earth scale must be right (~4x the full Moon from Earth)"))
s("21", "SET_STILL", [352, 353], 0.0, "Tighter on the two backs.", "push-in 5%", "none", "jax,baron", boulder)
s("21", "CHARACTER_STILL", [354], 0.0, "The Baron's visor, Earth reflected, moustache a white shape behind the glass.", "slow push-in 4%", "reflection slides 1%", "baron", baron_visor)
s("21", "CHARACTER_STILL", [355], 0.0, "Jax's visor.", "hold", "reflection drift", "jax", jax_visor, risk=("low", "visor reflection hides mouth"))
s("21", "CHARACTER_STILL", [356], 0.0, "The Baron: 'You want one?'", "hold", "brow lift", "baron", baron_visor)
s("21", "CHARACTER_STILL", [357], 0.0, "Jax: eleven minutes.", "hold", "none", "jax", jax_visor)
s("21", "INSERT", [358], 0.0, "The tricorn strapped on the helmet, absurd.", "hold", "none", "", tricorn_helmet)
s("21", "REAL_FOOTAGE", [(359, 0, 6.0)], 0.0, "Earth alone, low on the horizon.", "footage move only", "real", "", "REAL", ft=FT["poleEarth"](20, 28), comp="Full frame.")
s("21", "SET_STILL", [(359, 6.0, None), 360], 0.0, "The two backs: 'I jumped on the ball.' 'On it.'", "slow push-in 3%", "none", "jax,baron", boulder)
s("21", "CHARACTER_STILL", [361], 0.0, "'Astride. Like a horse, but rounder.'", "hold", "brow lift", "baron", baron_visor)
s("21", "REAL_FOOTAGE", [(362, 0, 5.5)], 0.0, "Earth, low.", "footage move only", "real", "", "REAL", ft=FT["poleEarth"](28, 34), comp="Full frame.")
s("21", "CHARACTER_STILL", [(362, 5.5, None)], 0.0, "Jax's visor, listening.", "slow push-in 3%", "none", "jax", jax_visor)
s("21", "SET_STILL", [363], 0.0, "The two backs.", "hold", "none", "jax,baron", boulder)
s("21", "CHARACTER_STILL", [364], 0.0, "The Baron: 'Back, I took a different cannonball.'", "slow push-in 3%", "none", "baron", baron_visor)
s("21", "CHARACTER_STILL", [], 3.0, "Jax laughs, in spite of himself, a real one. His shoulders shake.", "hold", "shoulder shake (warp, 3 Hz decaying)", "jax", jax_laugh, snd="Jax laugh on suit radio (needs a laugh recording/build).")
s("21", "CHARACTER_STILL", [365], 0.0, "'You listened to the end.'", "hold", "none", "baron", baron_visor)
s("21", "CHARACTER_STILL", [366], 0.0, "Jax: 'Did it happen?'", "hold", "none", "jax", jax_visor)
s("21", "CHARACTER_STILL", [367], 0.0, "'It's happening now. You are the audience.'", "very slow push-in 2%", "none", "baron", baron_visor)
s("21", "SET_STILL", [], 3.6, "A silence, long enough to hurt: two tiny figures on a boulder at the lip of the dark.", "hold (deliberate three-second hold plus cut breath)", "none", "jax,baron", boulder_xw, ft=FT["earth"](), comp="GENERATED TERRAIN — NOT REAL FOOTAGE; real Earth disc composited.", snd="Score out. Radio hiss only.")
s("21", "CHARACTER_STILL", [368], 0.0, "'I will come. By cannonball.'", "hold", "none", "baron", baron_visor)
s("21", "CHARACTER_STILL", [369], 0.0, "Jax: not a real promise.", "hold", "none", "jax", jax_visor)
s("21", "CHARACTER_STILL", [370], 0.0, "'It is the only kind I make.'", "hold", "none", "baron", baron_visor)
s("21", "INSERT", [372], 0.0, "Gloved hands: the Baron puts the silver hatchet into Jax's.", "slow push-in 4%", "glint", "", hatchet_pass)
s("21", "CHARACTER_STILL", [373, 374], 0.0, "The Baron's visor turns; Earth sits in its reflection.", "slow rotate 1 degree + push 2%", "reflection slides", "baron", baron_visor)
s("21", "CHARACTER_STILL", [375], 0.0, "'You lie like a man who once had to lie for his life.'", "very slow push-in 2%", "none", "baron", baron_visor)
s("21", "REAL_FOOTAGE", [], 2.6, "Nothing on the channel. Earth, low, shifts a hair on the horizon, as if it heard.", "footage move only", "real", "", "REAL", ft=FT["poleEarth"](34, 40), comp="Full frame.", snd="Radio hiss only.")
s("21", "CHARACTER_STILL", [376], 0.0, "Jax: 'It's twenty to.'", "hold", "none", "jax", jax_visor)
s("21", "SET_STILL", [377], 2.6, "'I'll watch it a little longer. It might do something.'", "slow pull-out 4%", "none", "jax,baron", boulder_xw, snd="A4 phrase resolves.")

# ================================================================= 22 SIGNING
hall_clock = J("SET customs", "hall_clock", ["hall"], "Insert: a large plain analogue wall clock in a concrete customs hall, the hands removed (we add them), flicker of a tube light.")
hall_desk_plate = J("SET customs", "hall_signing_plate", ["hall", "board"], "Wide plate of a vast empty customs hall with one desk in the middle of the floor and a flip-number board on the wall behind it, no people (characters are added as layers).")
chich_hall = J("Chichikov", "chich_soft_hall", ["chich", "box", "hall"], "At the far end of a vast customs hall, soft grey and out of focus: a plump man in an overcoat at a desk with a small inlaid box open in front of him.")
three_shot = J("Group", "baron_jax_lucia_desk", ["baron", "jax", "lucia", "hall"], "Three-shot at a customs desk in a vast hall: the Baron holding a pen, looking sideways at Jax Vale; Lucía Ortega beside them with a packed kit bag at her feet; all lips closed.")
coat_colour = J("Baron", "coat_chest_detail", ["baron"], "Insert: the chest and brass buttons of a moth-eaten red 18th-century cavalry coat over a patched pressure suit, close.")
lucia_hall = J("Lucía", "lucia_hall_mcu", ["lucia", "hall"], "Medium close-up of Lucía Ortega in a vast customs hall, watching someone beside her, breath held, lips closed.")
baron_hands = J("Baron", "baron_looks_at_hands", ["baron", "hall"], "Medium close-up of the Baron looking down at his own open hands in wonder, moustache hiding his mouth, hall lights.")
page_turn = J("Jax", "page_turned_pen", ["jax", "hall"], "Insert: the second page of a contract turned toward a man's hand in a burnt-orange cuff as he picks up a pen, steel desk.")
baron_hall = J("Baron", "baron_ecu_hall", ["baron", "hall"], "Extreme close-up of the Baron's eyes above the moustache under cold hall light, delighted then frightened.")
jax_desk = J("Jax", "jax_desk_mcu", ["jax", "jaxC", "hall"], "Medium close-up of Jax Vale at a customs desk, pen in hand, watching someone beside him, lips closed, cold hall light.")
mira_side = J("Mira", "mira_stamp_side", ["mira", "stamp", "hall"], "Medium shot of Dr Mira Sen standing at the side of a customs desk holding a heavy brass stamp, seen through the scratched glass of the desk screen with its reflections, watching, lips closed.")
baron_laugh_hall = J("Baron", "baron_laugh_hall", ["baron", "baronL", "hall"], "Close-up of the Baron sagging and then laughing hugely behind his moustache, eyes creased shut, under cold hall light.")
bag_grab = kitbag  # merged: reuse, no new image
noakes_alone = J("Noakes", "noakes_alone_wide_board", ["noakes", "hall", "board"], "Wide: a tired man in customs uniform alone at one desk in the middle of a vast empty customs hall, small in frame, a flip-number board on the wall above him.")
s("22", "INSERT", [379], 0.6, "The hall clock: 17:45.", "push-in 4%", "second hand ticks (code)", "", hall_clock, snd="Clock tick (first heard).")
s("22", "SET_STILL", [380], 0.4, "One desk in the middle of the enormous hall; Chichikov soft at the far end; the Baron, Jax, Lucía with her bag, Mira with the stamp, Noakes; on the wall, the board: 1,094.", "slow push-in 4%", "layers parallax 2%", "noakes,baron,jax,lucia,mira,chichikov", hall_desk_plate,
  comp="LAYERED: hall plate + cut-outs from approved singles (three_shot, mira_side, noakes, chich_hall). All small in frame.", risk=("high", "six characters in one wide; layered build, check every face"))
s("22", "SET_STILL", [381], 0.0, "Chichikov, soft grey, his box open: initial where the little arrows are.", "hold", "none", "chichikov", chich_hall)
s("22", "TWO_SHOT", [], 1.8, "The Baron takes the pen. Looks at Jax. Signs.", "hold", "eye-line shift (warp)", "baron,jax:m,lucia:m", three_shot, risk=("high", "three faces in one generated image"))
s("22", "INSERT", [], 2.4, "The ink. It stays. It stays.", "hold", "signature writes on and holds (code)", "", ink_stays)
s("22", "INSERT", [382], 2.0, "The Baron's coat: the faded red seeps back to red.", "hold", "saturation ramp 60% to 100% (code, coat matte)", "", coat_colour)
s("22", "CHARACTER_STILL", [], 0.8, "Lucía, breath held.", "hold", "breath", "lucia:m", lucia_hall)
s("22", "CHARACTER_STILL", [383, 384], 0.0, "The Baron looks at his own hands: 'I am… somewhere. I believe I am taller.'", "slow push-in 3%", "none", "baron", baron_hands)
s("22", "SET_STILL", [385], 0.0, "Chichikov: 'Welcome back, Baron.'", "hold", "none", "chichikov", chich_hall)
s("22", "INSERT", [386], 0.0, "The second page turned toward Jax. He picks up the pen.", "hold", "pen lifts (cut-out)", "", page_turn)
s("22", "CHARACTER_STILL", [387], 0.0, "The Baron, delighted: 'prisoner of the Sultan, keeping his bees, and—'", "hold", "brows up", "baron", baron_hall)
s("22", "CHARACTER_STILL", [388], 1.4, "He stops. 'I… took a scheduled shuttle.' Silence.", "hold", "eyes freeze", "baron", baron_hall)
s("22", "CHARACTER_STILL", [389], 0.0, "Jax watches.", "hold", "none", "jax:m", jax_desk)
s("22", "CHARACTER_STILL", [390], 0.0, "'Economy. It was perfectly pleasant.'", "push-in 3%", "eyes appalled (warp)", "baron", baron_hall)
s("22", "CHARACTER_STILL", [391], 0.0, "Mira watches, stamp in hand.", "hold", "none", "mira:m", mira_side)
s("22", "SET_STILL", [392], 0.0, "Chichikov: Clause nine. Approved material.", "slow push-in 3%", "none", "chichikov", chich_hall)
s("22", "CHARACTER_STILL", [393, 394], 0.0, "The Baron fights it: 'The bean — the horns of the —' 'The shuttle had a lovely lounge.'", "hold with 1 px tremor", "tremor", "baron", baron_hall)
s("22", "CHARACTER_STILL", [], 2.0, "His eyes find Jax's. Smiling. Terrified. Tidy.", "very slow push-in 2%", "none", "baron", baron_hall)
s("22", "INSERT", [], 1.8, "Jax's pen touching the signature line. A bead of ink.", "macro push-in 4%", "ink bead swells (code)", "", page_turn)
s("22", "CHARACTER_STILL", [395], 0.2, "Jax: 'Both or neither.'", "hold", "mouth patch (4 visemes)", "jax:m", jax_desk, risk=("medium", "mouth patch"))
s("22", "CHARACTER_STILL", [396, 397], 0.0, "'I'm sorry?' The Baron's eyes as Jax explains.", "hold", "eyes widen", "baron", baron_hall)
s("22", "INSERT", [], 1.0, "He lays the pen down.", "hold", "pen settles", "", page_turn)
s("22", "CHARACTER_STILL", [398], 0.3, "Jax: 'Neither.'", "hold", "mouth patch (2 visemes)", "jax:m", jax_desk, risk=("medium", "mouth patch"))
s("22", "INSERT", [], 2.4, "On the Voss contract, the Baron's signature fades, stroke by stroke, to nothing.", "hold", "signature fade (code)", "", ink_stays)
s("22", "INSERT", [], 1.8, "The red drains out of the coat again.", "hold", "saturation ramp 100% to 60%", "", coat_colour)
s("22", "CHARACTER_STILL", [400], 0.3, "The Baron sags — and then, behind the moustache, a huge laugh: 'I came on a beanstalk!'", "push-in 3%", "laugh shake", "baron", baron_laugh_hall)
s("22", "INSERT", [], 3.5, "Lucía's hand closes on the ribbon at her wrist. Holds. Holds.", "hold (three silent seconds, as written)", "grip tightens then still", "", ribbon_close, snd="Silence under: no score for 3 s.")
s("22", "INSERT", [401], 0.2, "She lets go, and picks up her bag: 'Good.'", "hold", "none", "", bag_grab)
s("22", "SET_STILL", [402], 0.0, "Chichikov, pleasant, unruffled.", "hold", "none", "chichikov", chich_hall)
s("22", "INSERT", [403], 0.2, "Jax looks at the clock: quarter to.", "hold", "second hand", "", hall_clock)
s("22", "SET_STILL", [], 1.4, "He grabs the parcel; Lucía grabs the Baron; they are gone.", "whip-pan 8%", "motion-blur streak layers", "", hall_desk_plate, snd="Caper hit (C1 sting); running feet.")
s("22", "SET_STILL", [404, 405], 2.0, "Noakes, alone at the desk in the enormous hall. Above him: DAYS WITHOUT INCIDENT: 1,094. 'That was an incident. Seal the port.'", "slow push-in 5%", "tube flicker", "noakes", noakes_alone, snd="A3-style tension cue (new C4) enters; END OF ACT THREE.")

# ================================================================= 23 CORRIDOR LEAP
klaxon = J("SET customs", "klaxon_red", ["corr"], "Insert: a red rotating warning lamp on a concrete corridor wall, mid-turn, throwing red light.")
leap = J("Group", "lucia_leap_baron_overhead", ["lucia", "baron", "corr"], "Hero silhouette against bright corridor lights: a strong woman mid-leap three metres off the floor in low gravity holding an old man in a tricorn and long coat straight over her head like a trophy belt; both shapes mostly in silhouette, red warning light.")
jax_run = J("Jax", "jax_running_parcel", ["jax", "parcel", "corr"], "Jax Vale running in a long bounding low-gravity stride down a red-lit corridor, the brown-paper parcel under one arm, motion, mostly silhouette.")
boots_leave = jax_run  # merged: reuse, no new image
s("23", "INSERT", [], 1.0, "A klaxon light turns red.", "hold", "light rotates (code)", "", klaxon, snd="SFX: klaxon (two-tone, ours).")
s("23", "SET_STILL", [408, 409], 0.0, "Lucía mid-leap, the Baron held overhead like a trophy belt, three metres off the floor in one-sixth gravity.", "slow push-in 3%; 1% float drift", "red light sweeps", "lucia,baron", leap, risk=("high", "two-body pose; play as silhouette"))
s("23", "INSERT", [410], 0.0, "Boots leaving the floor.", "hold", "none", "", boots_leave)
s("23", "SET_STILL", [411], 0.0, "Jax behind with the parcel.", "lateral move 5%", "red light", "jax", jax_run)
s("23", "SET_STILL", [412], 0.4, "The Baron overhead: 'Mind my trunk. It is on the roof. It always is.'", "crop on the Baron; push 4%", "red light", "baron,lucia", leap, snd="C1 caper cue, chase variant, starts.")

# ================================================================= 24 CHASE
crawler_side = J("Vehicles", "crawler_alongside", ["crawler", "cab"], "From inside an old rover cab through its side window: a customs crawler driving alongside close enough to touch on a bright lunar road, black sky.")
card_window = J("Vehicles", "crawler_window_card", ["crawler"], "Insert: through a crawler's round cab window, a blank mirrored helmet visor and a laminated blank card pressed to the glass by a gloved hand.")
gully = J("EXT plates", "gully_plate", [], "Generated lunar terrain plate (not a photograph): a pale road along a bright crater rim kinking over a narrow gully of pure black shadow, low Sun on the horizon, black sky, no vehicles.")
cab_air = J("SET post-chaise", "cab_airborne", ["cab", "jax", "baron", "lucia"], "Inside an old rover cab in mid-air in low gravity: the driver, a curly-haired man and an old man in a tricorn all floating an inch above their seats; a brown-paper parcel lifting off the man's knees, held down by his hand; the old man's tricorn lifting, held down by his hand; bright glare windows.")
baron_fist = J("Baron", "baron_side_window_fist", ["baron", "cab"], "The Baron at a rover's side window, fist raised, magnificent, glare outside, moustache hiding his mouth.")
wheels = J("Vehicles", "wheels_meet_dust", ["chaise"], "Insert: an old rover's wheel meeting grey lunar dust, a spray of dust frozen in a clean ballistic arc, no billowing.")
rear_window = J("Vehicles", "rear_window_crawler_nose_down", ["crawler", "cab"], "Through a rover's rear window: far behind, a customs crawler nose-down in a black gully, wheels in the air, perfectly still; a tiny card in its window.")
s("24", "REAL_FOOTAGE", [], 2.0, "The real rim from above, racing.", "footage move only, speed-ramped 1.3x", "real", "", "REAL", ft=FT["fly"](40, 50), comp="Full frame.", snd="No exterior sound. Score only (C1 chase).", risk=("medium", "unverified"))
s("24", "SET_STILL", [414, 415, 416, 417, 418], 0.0, "The post-chaise tears along the white rim, trunk on its roof; two customs crawlers behind. Not a sound outside.", "lateral parallax 8%, vehicles translate", "vehicles translate; ballistic dust", "", rim_plate, assets=[REF["chaise"]["path"], REF["crawler"]["path"]],
  comp="GENERATED TERRAIN — NOT REAL FOOTAGE. Rover and two crawler cut-outs.", risk=("medium", "vehicle cut-outs must sit in the light"))
s("24", "SET_STILL", [], 1.6, "A crawler slides up alongside, close enough to touch. Silent as a cloud.", "slow push 3%", "crawler drifts closer 20 px", "", crawler_side, comp="Rim plate behind.")
s("24", "INSERT", [420, 421], 0.0, "Through its window: a blank visor, a card pressed to the glass: CUSTOMS. PULL OVER.", "hold", "none", "", card_window, comp="Card text in code.")
s("24", "INSERT", [423], 0.8, "The card flips over: PLEASE.", "flip (two cut-out states)", "card flip", "", card_window)
s("24", "SET_STILL", [], 1.4, "Ahead, the road kinks over a black gully. Lucía doesn't brake.", "push-in 6% (speed)", "plate slides", "", gully, comp="GENERATED TERRAIN — NOT REAL FOOTAGE.")
s("24", "SET_STILL", [], 8.0, "WIDE (HELD): the post-chaise leaves the rim and hangs in the air over the gully. Black below. Sun above. It hangs. It goes on hanging.", "hold; rover cut-out moves on a true 1/6 g arc (code), almost static", "rover ballistic arc; wheels still spinning", "", gully, assets=[REF["chaise"]["path"]],
  comp="GENERATED TERRAIN — NOT REAL FOOTAGE. Rover arc computed (1.62 m/s2).", snd="Score holds one single note.", risk=("medium", "the hang must read as funny, not frozen: wheels spin and the arc moves"))
s("24", "SET_STILL", [425, 426], 0.0, "Inside: everyone an inch above their seats; parcel and tricorn floating, held down.", "1% float drift", "float bob (code)", "jax,baron,lucia", cab_air, snd="Cab: engine whine with no road noise.", risk=("medium", "three characters plus floating props"))
s("24", "CHARACTER_STILL", [(427, 0, 6.5)], 0.0, "The Baron at the side window, fist raised, magnificent: 'Cowards of customs!'", "slow push-in 4%", "fist shake (warp)", "baron", baron_fist)
s("24", "CHARACTER_STILL", [(427, 6.5, None)], 0.0, "Closer: 'I was swallowed by a fish and left by the front door!'", "push-in 6% to eyes", "none", "baron", baron_fist)
s("24", "CHARACTER_STILL", [428, 429], 0.0, "'Your radio's off.' 'They are not worthy of the words.'", "slow push-in 3%", "fist lowers (warp)", "baron", baron_fist)
s("24", "INSERT", [], 2.0, "The wheels meet the dust. Not a sound. Inside, everyone drops an inch.", "1-frame drop jolt", "dust arc", "", wheels, snd="Interior thump only (felt, not heard outside).")
s("24", "INSERT", [430], 0.0, "The rear window: crawler one nose-down in the gully, wheels in the air, still asking nicely.", "hold", "none", "", rear_window)
s("24", "SET_STILL", [], 2.2, "Ahead, in silence, a third crawler slews across the road.", "hold", "crawler slides into frame (cut-out)", "", rim_plate, assets=[REF["crawler"]["path"]], comp="GENERATED TERRAIN — NOT REAL FOOTAGE.")

# ================================================================= 25 CLAMP CONSOLE
console_wide = J("SET customs", "console_noakes_mira", ["console", "noakes", "mira", "hall"], "A two-slot clamp console under a flip-number board in a vast customs hall: Noakes from behind on a headset, Dr Mira Sen beside him with a key on a lanyard, her face turned to the console; far at the back of the hall a soft grey figure with a teacup.")
mira_console = J("Mira", "mira_console_back34", ["mira", "console"], "Dr Mira Sen three-quarters from behind at a console, key lanyard in hand, face turned away toward the console screen.")
noakes_headset = J("Noakes", "noakes_headset_back", ["noakes", "console"], "Close shot of Noakes from behind and slightly to one side, a headset on, one hand at the earpiece, console glow on his ear and cheek, face not visible.")
brass_tap = J("Chichikov", "glove_taps_brass_device", ["chich"], "Insert: a soft grey-gloved hand tapping once on a small brass device the size of a matchbox, out of focus edges, teacup nearby.")
noakes_turn2 = noakes_headset  # merged: reuse, no new image
console_keys = "CODE"  # merged: reuse, no new image
key_slot = J("Mira", "mira_key_in_slot", ["mira", "console"], "Insert: a woman's ink-stained hand sliding a brass key into the second slot of a steel console, thumb resting on it.")
s("25", "SET_STILL", [432], 0.0, "Noakes, back to us, on a headset; Mira at the console; above them, the board: 1,094; at the back, a soft grey shape with a teacup.", "slow push-in 3%", "none", "noakes,mira,chichikov", console_wide, snd="Hall hush; console hum; the line read fast, no pauses.", risk=("medium", "three characters; Mira faces away"))
s("25", "INSERT", [], 1.3, "The second hand on the clock. Nothing.", "hold", "second hand ticks", "", hall_clock, snd="Ticks, very loud in the silence.")
s("25", "SET_STILL", [433, 434], 2.6, "'Yes.' Nothing. 'No, that's its name.' Nothing.", "very slow push-in 3%", "console screen spinner (code)", "noakes,mira", console_wide)
s("25", "CHARACTER_STILL", [435], 0.0, "Mira: 'They haven't asked you anything yet.'", "hold", "none", "mira", mira_console)
s("25", "CHARACTER_STILL", [436], 0.0, "Noakes on the headset: four questions, two point six seconds late.", "slow push-in 3%", "none", "noakes", noakes_headset)
s("25", "CHARACTER_STILL", [437, 438], 0.0, "Noakes on the headset: 'What are you saving them for?' 'My retirement.'", "hold", "none", "noakes", noakes_headset)
s("25", "INSERT", [], 1.4, "At the back of the hall, a soft grey hand taps once on a small brass device.", "hold", "tap (2-frame)", "", brass_tap, snd="SFX: tiny brass click.")
s("25", "INSERT", [], 1.3, "The second hand. Nothing.", "hold", "ticks", "", hall_clock)
s("25", "CHARACTER_STILL", [439, 440], 0.0, "Noakes stiffens: 'A reason?'", "1 px jolt", "none", "noakes", noakes_headset)
s("25", "SET_STILL", [(441, 0, 6.0)], 0.0, "The soft grey shape at the back: Regulation nineteen.", "hold", "steam", "chichikov", chich_hall)
s("25", "CHARACTER_STILL", [(441, 6.0, None)], 0.0, "Noakes turns.", "hold", "none", "noakes", noakes_turn2)
s("25", "SET_STILL", [442], 0.6, "The soft grey shape sips its tea.", "hold", "cup lifts (cut-out)", "chichikov", chich_hall)
s("25", "INSERT", [443], 0.0, "The console: BAY 9 CLAMP — CLOSED. KEY 1 — SUPERINTENDENT. KEY 2 — DUTY OFFICER.", "push-in 4%", "screen text", "", console_keys, comp="Console labels in code (DATA_VISUAL 5).")
s("25", "CHARACTER_STILL", [444, 445], 0.0, "Noakes: 'Until Earth says yes, Dr Sen, nothing has happened.'", "slow push-in 3%", "none", "noakes", noakes_headset)
s("25", "INSERT", [], 2.0, "Mira's key slides into slot two. Her thumb rests on it.", "slow push-in 4%", "key slides (cut-out)", "", key_slot, snd="Key click; tension cue C4 holds.")

# ================================================================= 26 INNER EDGE
lip_plate = J("EXT plates", "inner_lip_plate", [], "Generated lunar terrain plate (not a photograph): a road at the very inner lip of a huge crater, a customs crawler parked across the road ahead, the rim falling away on the left into absolute black, low hard Sun.")
headlamps = J("EXT plates", "headlamps_slope", [], "Pure darkness except two rover headlamp beams lighting three metres of steep grey lunar slope, then nothing at all.")
s("26", "SET_STILL", [447, 448, 449, 450], 0.0, "Blocked ahead. A crawler behind. On the left, the inner lip of the crater and the black.", "push-in 6%", "plate slides", "", lip_plate, comp="GENERATED TERRAIN — NOT REAL FOOTAGE.", snd="Cab voices dry; no exterior sound.")
s("26", "SET_STILL", [451, 452, 453], 0.0, "From the back seat: the lip on the left of the windscreen.", "handheld 2%", "bounce", "lucia,jax,baron", cab_back, comp="Lip plate in the windscreen.")
s("26", "SET_STILL", [], 1.0, "The rover goes over the lip.", "tilt 5 degrees + drop", "plate tips", "", lip_plate)
s("26", "BLACK", [454], 2.4, "CUT TO BLACK. Silence. 'Lights.'", "none", "none", img="CODE", snd="Total silence 1.5 s, then Lucía dry.")
s("26", "SET_STILL", [], 2.4, "Headlamps: three metres of grey slope. Then nothing at all.", "hold", "headlamp flicker", "", headlamps, comp="GENERATED, labelled.")

# ================================================================= 27 INNER WALL
faces_below = J("Group", "three_faces_lit_below", ["lucia", "jax", "baron", "cab"], "Inside a dark rover cab from the dashboard looking back: three faces (a woman driver with short hair, a curly-haired man, an old man with a huge white moustache and tricorn) lit only from below by dashboard glow, black beyond, lips closed, very still.")
frost3 = J("SET post-chaise", "frost_windscreen_3", ["cab"], "Insert: the same rover windscreen almost covered in thick frost ferns, a small clear patch, dashboard glow.")
frost1 = frost3  # merged: reuse, no new image
frost2 = frost3  # merged: reuse, no new image
radio_grille = J("SET post-chaise", "cab_radio_grille", ["cab"], "Insert: an old rover dashboard radio speaker grille with one small green signal lamp lit, in near darkness.")
mira_console_mic = J("Mira", "mira_console_headset_boom", ["mira", "noakes", "console"], "Dr Mira Sen at a console in a dim hall wearing a headset whose microphone boom sits right in front of her mouth, eyes intent on a screen; Noakes in shadow beside her.")
s("27", "CHARACTER_STILL", [], 2.0, "Three faces lit from below by the dashboard. Black beyond.", "hold (held still)", "dashboard flicker", "lucia:m,jax:m,baron", faces_below, snd="Cab heater wheezing; battery whine.", risk=("high", "three faces in one still, low light; fallback: three singles"))
s("27", "INSERT", [456], 0.0, "Frost on the windscreen.", "hold", "frost stage 1: heavy-frost still revealed 20% through an animated mask", "", frost1, snd="Frost crackle.")
s("27", "CHARACTER_STILL", [457], 0.0, "The Baron lit from below: 'That's why it is empty.'", "crop on Baron (upscaled)", "flicker", "baron", faces_below)
s("27", "INSERT", [458, 459], 0.0, "PIP on the wrist, crackling.", "hold", "lens glow stutters", "pip", pip_wrist_glow, comp="Regrade cold and dark.")
s("27", "INSERT", [], 1.6, "Frost, thicker.", "hold", "frost stage 2: mask reveals 55%", "", frost2)
s("27", "INSERT", [460, 461], 0.0, "The cab radio: Mira on the open channel.", "hold", "signal lamp lights", "", radio_grille, snd="Mira filtered (open channel, wider with hiss).")
s("27", "CHARACTER_STILL", [462], 0.0, "The three faces, very still: 'Hello, everyone.'", "hold", "flicker", "lucia:m,jax:m,baron", faces_below, risk=("low", "silent faces under radio V.O."))
s("27", "DATA_VISUAL", [463], 0.0, "A pale laser map blooms in the black, contour by contour: the inner wall, measured from orbit. A small dot: them.", "slow orbit 6 degrees", "contours bloom outward", img="CODE", comp="DATA_VISUAL 6 from LOLA altimetry (real data, rendered by us).")
s("27", "CHARACTER_STILL", [464], 0.0, "Jax's eyes, lit from below.", "crop eyes only (upscaled)", "none", "jax", faces_below)
s("27", "DATA_VISUAL", [465], 0.0, "The map: LEFT 11°. The dot turns.", "hold", "dot moves", img="CODE")
s("27", "INSERT", [], 1.0, "Lucía steers.", "hold", "wheel turn (warp)", "", wheel_ribbon, comp="Regrade dark, dashboard light.")
s("27", "DATA_VISUAL", [466], 0.8, "STOP. They stop.", "hold", "dot halts", img="CODE")
s("27", "DATA_VISUAL", [467], 0.0, "Four metres to the right, the wall goes down four kilometres: the map shows it.", "slow push 5% toward the drop", "drop highlighted in a cold line", img="CODE")
s("27", "CHARACTER_STILL", [468], 0.0, "Jax's eyes.", "hold", "none", "jax", faces_below)
s("27", "CHARACTER_STILL", [469], 0.0, "The three faces: 'You're the first one who's had to listen.'", "very slow push-in 2%", "flicker", "lucia:m,jax:m,baron", faces_below)
s("27", "CHARACTER_STILL", [470], 0.0, "At the console, Mira; Noakes beside her in shadow: 'Dr Sen. Get off this channel.'", "hold", "screen glow", "mira,noakes", mira_console_mic, risk=("low", "mic boom hides her mouth; Noakes in shadow"))
s("27", "DATA_VISUAL", [471, 472], 0.0, "The map: forward 40 m, a boulder the size of a house, round it on the left.", "slow orbit", "dot moves round the boulder", img="CODE")
s("27", "INSERT", [(473, 0, 4.0)], 0.0, "Frost, nearly covering the glass.", "hold", "frost stage 3: 90% revealed", "", frost3)
s("27", "DATA_VISUAL", [(473, 4.0, None)], 0.0, "The map: the service ramp to bay nine, climbing into the Sun.", "push-in 6%", "ramp lights up", img="CODE")
s("27", "CHARACTER_STILL", [474, 475, 476], 0.6, "The Baron, softly: 'Madam, you are a wonder.'", "slow push-in 3%", "none", "baron", faces_below)
s("27", "CHARACTER_STILL", [], 1.4, "At the console, Mira, alone in her work.", "hold", "none", "mira", mira_console_mic)

# ================================================================= 28 THE KEY
mira_profile = J("Mira", "mira_profile_console_bare", ["mira", "console"], "Profile of Dr Mira Sen at a console in a vast dim hall, headset off and in her hand, nothing between her face and the camera, still, lips closed.")
noakes_hand = J("Noakes", "noakes_hand_midair", ["noakes", "console"], "Insert: a tired man's hand stopped in mid-air above a console, fingers half open.")
badge = J("Mira", "badge_and_stamp_laid", ["mira", "stamp", "console"], "Insert: an ink-stained hand laying a customs badge on a steel desk beside a heavy brass stamp.")
chich_notebook = J("Chichikov", "glove_writes_notebook", ["chich"], "Insert: a soft grey-gloved hand writing in a small black notebook under a long list of handwritten names (illegible).")
mira_walk = J("Mira", "mira_back_walks_hall", ["mira", "hall"], "Dr Mira Sen seen from behind, small, walking away down the length of an enormous empty customs hall, notebook under her arm.")
s("28", "CHARACTER_STILL", [478], 1.0, "Mira takes off the headset: in profile, nothing between her and the camera, for the first time.", "very slow push-in 2%", "open-channel light dies on the console", "mira:m", mira_profile, risk=("medium", "profile; check hardest against master"))
s("28", "CHARACTER_STILL", [479], 0.0, "Noakes, holding.", "hold", "none", "noakes", noakes_headset)
s("28", "INSERT", [], 1.4, "Mira's hand on her key. She turns it. Not to LOCK. To OPEN.", "hold", "key turns (rotate cut-out)", "", key_slot)
s("28", "DATA_VISUAL", [], 1.0, "The console: BAY 9 CLAMP — OPEN.", "hold", "status flips", img="CODE", snd="Console chime.")
s("28", "INSERT", [481], 0.0, "She draws the key out of the slot.", "hold", "key withdraws", "", key_slot)
s("28", "CHARACTER_STILL", [482], 0.0, "Noakes: 'What are you doing?' Mira (O.S.): 'Nothing, sir. Earth hasn't said yes.'", "hold", "none", "noakes", noakes_headset)
s("28", "DATA_VISUAL", [], 2.4, "Silence, one point three seconds of it. Then a box pops up on the console: AUTHORITY TO LOCK — RECEIVED.", "hold", "box pops after exactly 1.3 s", img="CODE", snd="NO SCORE. Silence, then a polite chime.")
s("28", "INSERT", [484], 0.0, "Noakes's hand stops in mid-air.", "hold", "none", "", noakes_hand)
s("28", "CHARACTER_STILL", [485], 0.0, "Mira, in profile: 'Courageous. Yes. I've heard.'", "hold", "mouth patch (profile, 5 visemes)", "mira:m", mira_profile, risk=("high", "profile mouth patch on the payoff line; test early, fallback: play on Noakes's hand"))
s("28", "INSERT", [], 2.0, "Her badge laid on the desk. Then the stamp beside it. The key goes into her pocket.", "hold", "2 cuts", "", badge)
s("28", "INSERT", [], 2.4, "Her notebook, entry 41: OWNER: —. She writes in the empty field: VOSS.", "hold", "write-on", "", pages)
s("28", "INSERT", [487], 0.4, "At the back of the hall, a soft grey hand writes under a long list of names: SEN, M. 'Cartographer.'", "hold", "write-on", "", chich_notebook)
s("28", "INSERT", [488, 489, 490], 0.0, "'Where will you go?' She closes the notebook and puts it under her arm.", "hold", "cover closes", "", pages)
s("28", "SET_STILL", [491], 3.0, "'Then the map is wrong, sir. I did mention it.' She goes, a small figure down the length of the enormous hall.", "slow push-in 3%", "none", "mira", mira_walk, snd="Mira motif (M2) full statement, then into C1.")

# ================================================================= 29 APRON
apron_wide = J("EXT plates", "apron_establishing", ["apron", "ship"], "Generated lunar exterior (not a photograph): a landing apron at the top of a ramp road climbing out of black shadow 80 m below; at the top of the apron a boxy patched courier ship with its cargo ramp lowered; blinding low Sun; black sky.")
jax_bound = J("Jax", "jax_suit_bounding_parcel", ["jaxH", "parcel", "apron"], "Jax Vale in a pressure suit mid-stride in a huge low-gravity bound across a bright lunar apron, the brown-paper parcel under one arm, both feet off the ground.")
jax_ramp = J("Jax", "jax_ramp_hatchet", ["jaxH", "hatchet", "ship"], "Jax Vale in a pressure suit on a ship's lowered cargo ramp, setting down a parcel, a small silver hatchet in his other hand, hard low sun behind.")
throw_wide = J("EXT plates", "throw_wide_silhouette", ["jaxH", "ship", "apron"], "Generated lunar exterior (not a photograph), wide from the side: a suited figure in silhouette on a ship's ramp against a blinding low Sun, arm just released from a throw; far below and to the side, an old rover on a ramp road tethered by a thin line to a crawler; black sky.")
glove_open = J("Jax", "glove_open_close", ["jaxH"], "Insert: a pressure-suit glove opening slowly, fingers spread, as if it belonged to someone else, hard sunlight.")
jax_visor_ramp = jax_visor  # merged: reuse, no new image
mira_bound1 = J("Mira", "mira_bound_1", ["miraS", "apron"], "Dr Mira Sen in a slim indigo customs pressure suit mid-bound across a bright lunar apron, both feet off the ground, visor reflecting the sun.")
mira_bound2 = J("Mira", "mira_bound_2", ["miraS", "apron", "ship"], "Dr Mira Sen in a customs pressure suit landing a huge low-gravity stride at the foot of a ship's ramp, one arm out, visor reflecting.")
lucia_cab = J("Lucía", "lucia_helmet_cab", ["luciaS", "cab"], "Lucía Ortega in helmet inside a rover cab looking up through the windscreen at a ship's ramp, visor reflections hiding her mouth.")
baron_apron = J("Baron", "baron_apron_by_rover", ["baronHT", "baronS", "chaise", "apron"], "The Baron in pressure suit and helmet with tricorn strapped on, standing on a bright lunar apron beside an old rover with a carved horse's head on its bonnet, refusing to move, one hand raised.")
baron_salute = J("Baron", "baron_visor_salute", ["baronHT", "baron", "ship"], "Close-up: the Baron lifting the tricorn off the top of his helmet in salute; his visor reflects a small boxy ship with its ramp down.")
lucia_trunk = J("Lucía", "lucia_heaves_trunk", ["luciaS", "trunk", "ship"], "Lucía Ortega in a pressure suit heaving a battered steamer trunk with a brown luggage tag up a ship's cargo ramp, strong, black sky.")
liftoff = J("EXT plates", "liftoff_speck_figure", ["chaise"], "Generated lunar exterior (not a photograph), extreme wide: over a bright white crater rim a tiny ship speck lifting into black sky; far below on an apron beside an old rover, one small motionless figure in a long coat and tricorn hat.")
s("29", "SET_STILL", [493], 2.6, "The rover bursts up the ramp road into blinding Sun. At the top of the apron, 80 m ahead: The Unscheduled, clamp open, ramp up.", "slow push-in 4%; rover translates up the road", "rover translates; ballistic dust", "", apron_wide, assets=[REF["chaise"]["path"], REF["crawler"]["path"]],
  comp="GENERATED TERRAIN — NOT REAL FOOTAGE. Geography in one wide: ship, ramp, ramp road 80 m below, rover, crawler.", snd="Suit radios (narrow). No exterior sound. C1 chase cue.")
s("29", "SET_STILL", [], 1.4, "Jax out of the hatch with the parcel, bounding ahead in huge low strides.", "lateral move 5%", "bound (2 stills crossed)", "jax", jax_bound)
s("29", "SET_STILL", [494], 0.6, "Behind the rover, a crawler fires a grapple line. Silent. It hooks the post-chaise by the tail; the rover slews.", "hold", "grapple line draws (code)", "", apron_wide)
s("29", "SET_STILL", [495, 496], 0.0, "Jax on the ramp sets down the parcel. In his other hand, the silver hatchet.", "slow push-in 4%", "none", "jax", jax_ramp)
s("29", "SET_STILL", [], 9.0, "WIDE (HELD): the hatchet rises in a long slow arc, turns over once at the top, comes down on the line. The line parts. The rover lurches free and races in. The glint keeps going, over the rim. Gone.", "hold (deliberate)", "glint on a true 1/6 g parabola (code); line parts; rover moves", "jax", throw_wide, comp="GENERATED TERRAIN — NOT REAL FOOTAGE. Arc computed: about 11-13 m/s lob over 80 m.", snd="TOTAL SILENCE: no score, no effects.", risk=("medium", "must read at phone size: glint needs a highlight trail"))
s("29", "SET_STILL", [498, 499], 0.0, "The rover races in.", "push-in 4%", "rover translates", "", apron_wide)
s("29", "INSERT", [500, 501], 0.4, "'Darts.' His gloved hand, opening and closing, as if it belonged to someone else. 'Lot of… bars.'", "hold", "hand opens/closes (2 states)", "", glove_open)
s("29", "SET_STILL", [502], 0.0, "PIP: clamp open, bay nine.", "hold", "none", "jax", jax_ramp)
s("29", "CHARACTER_STILL", [503], 0.0, "Jax's visor: 'Mira.'", "hold", "flare", "jax", jax_visor_ramp)
s("29", "SET_STILL", [504], 0.0, "Across the apron, a figure in a customs suit comes bounding in.", "lateral move 4%", "bound", "mira", mira_bound1, risk=("medium", "suit and helmet reference is a library gap"))
s("29", "SET_STILL", [505, 506], 0.0, "She lands a stride at the foot of the ramp.", "hold", "none", "jax,mira", mira_bound2)
s("29", "CHARACTER_STILL", [507, 508], 0.0, "Jax's visor: 'There are nine sections.' 'Which is why twelve is so exclusive.'", "slow push-in 3%", "none", "jax", jax_visor_ramp)
s("29", "CHARACTER_STILL", [509], 0.0, "Lucía in the cab: 'Welcome aboard. No one gets paid.'", "hold", "none", "lucia", lucia_cab)
s("29", "SET_STILL", [510], 0.0, "The rover stops at the foot of the ramp. The Baron climbs out onto the apron, and stays there.", "slow push-in 3%", "none", "baron", baron_apron)
s("29", "SET_STILL", [511, 512], 0.0, "'Baron, come on—' The Baron: 'Go to the far side.'", "push-in 4%", "none", "baron", baron_apron)
s("29", "INSERT", [513, 514], 0.0, "PIP on the wrist: six o'clock in four minutes.", "hold", "lens glow", "pip", pip_wrist_glow, comp="Regrade hard sunlight on the suit sleeve.")
s("29", "CHARACTER_STILL", [515], 0.0, "Jax's visor: '…Far side.'", "hold", "none", "jax", jax_visor_ramp)
s("29", "SET_STILL", [516, 517, 518], 0.0, "The Baron: 'tell the lady I said nothing about her.' 'Go!'", "slow push-in 3%", "none", "baron", baron_apron)
s("29", "INSERT", [], 2.4, "His visor, the ship reflected in it. He lifts the tricorn off his helmet in salute.", "hold", "tricorn lifts (2 states)", "baron", baron_salute, snd="A4 emotional phrase.")
s("29", "SET_STILL", [], 1.0, "Jax turns up the ramp.", "hold", "none", "jax", jax_ramp)
s("29", "SET_STILL", [519], 0.0, "Lucía heaves the LOT 14 trunk up the ramp. Heavier than luggage. She doesn't notice.", "slow push-in 3%", "strain", "lucia", lucia_trunk)
s("29", "SET_STILL", [], 1.4, "The ramp rises.", "hold", "ramp rotates up (cut-out)", "", apron_wide)
s("29", "SET_STILL", [], 5.0, "The ship lifts, a speck over the white rim. Far below on the apron, beside the post-chaise, one small figure with a hat. It does not move.", "slow pull-out 6%", "ship speck rises", "", liftoff, comp="GENERATED TERRAIN — NOT REAL FOOTAGE. The 'figure' is the coat and tricorn on the horse's head; never closer than this.", snd="Silence, then A4 single sustained note.")

# ================================================================= 30 BRIDGE AFTERWARDS
three_backs = J("SET bridge", "bridge_three_backs", ["bridge", "jax", "mira", "lucia"], "The bridge from behind: three people seen from behind against the large pure-black window, a curly-haired man in burnt orange, a woman with a dark braid, a broad-shouldered woman with short hair; a call window glowing on a side screen.")
lucia_ribbon_seat = J("Lucía", "lucia_back_ribbon_armrest", ["lucia", "bridge"], "Lucía Ortega seen from behind in a bridge seat, not looking up, her wrist with a red ribbon resting on the armrest.")
lucia_coffee = J("Lucía", "lucia_raps_coffee", ["lucia", "bridge"], "Lucía Ortega seen from behind at a battered little coffee machine on a ship's console, rapping it with a spanner.")
s("30", "DATA_VISUAL", [], 2.0, "The clock: 17:59:58.", "hold", "seconds tick", img="CODE")
s("30", "SET_STILL", [522], 0.0, "Three backs to us. In the window, low over the grey limb of the Moon, Earth, sinking. On a screen, Temi's call window.", "very slow push-in 2%", "Temi window low-fps; real plate moves", "jax,mira,lucia,temi", three_backs, ft=FT["earthset"](None, None, "Pick the Earthset passage; in/out on viewing."),
  comp="Real Earthset video in the window; Temi still in the call window.", snd="Bridge tone; Temi bright and kind.", risk=("medium", "three characters, from behind"))
s("30", "REAL_FOOTAGE", [], 3.0, "Earth slips below the horizon.", "footage move only, cropped to the window frame", "real", "", "REAL", ft=FT["earthset"](None, None, "The moment of set."), comp="Window-frame crop of the real footage.", snd="Temi's voice cuts mid-word at Earth's set.")
s("30", "DATA_VISUAL", [], 1.4, "Temi's still freezes. The call window goes black.", "hold", "freeze then cut to black", "temi", "CODE", assets=[REF["temi"]["path"]])
s("30", "REAL_FOOTAGE", [], 2.4, "Silence. The far side's grey below the window.", "footage move only", "real", "", "REAL", ft=FT["farside"](0, 6), comp="Full frame.", snd="Silence.")
s("30", "INSERT", [524], 0.0, "PIP's lens on the bridge.", "hold", "lens glow", "pip", pip_lens, comp="Regrade warmer: the cold open's light, quieter.")
s("30", "SET_STILL", [], 2.4, "A long silence. Three backs.", "hold", "none", "jax,mira,lucia", three_backs, ft=FT["farside"](6, 12))
s("30", "INSERT", [(525, 0, 5.0)], 0.0, "PIP: status.", "hold", "lens glow", "pip", pip_turn)
s("30", "SET_STILL", [(525, 5.0, None), 526], 0.0, "Three backs: 'I know the number.'", "push-in 3%", "none", "jax,mira,lucia", three_backs, ft=FT["farside"](12, 20))
s("30", "INSERT", [527], 0.0, "PIP: eight months, three weeks and six days.", "hold", "lens glow", "pip", pip_lens)
s("30", "CHARACTER_STILL", [528], 0.0, "Lucía from behind, the ribbon on the armrest: 'Nine. I'm rounding up.'", "hold", "none", "lucia", lucia_ribbon_seat)
s("30", "TWO_SHOT", [529, 530], 0.0, "Over Jax's shoulder.", "hold", "none", "jax", jax_ots)
s("30", "SET_STILL", [531, 532], 0.0, "Three backs: 'I gave up my job for a coordinate.'", "slow push-in 2%", "none", "jax,mira,lucia", three_backs, ft=FT["farside"](20, 28))
s("30", "CHARACTER_STILL", [], 1.4, "Lucía crosses to the dead coffee machine and raps it once with her spanner.", "hold", "2-frame rap jolt", "lucia", lucia_coffee, snd="Spanner rap on tin.")
s("30", "INSERT", [], 1.0, "The little green light comes on.", "hold", "light on", "", coffee, snd="Small happy click; the machine gurgles.")
s("30", "INSERT", [534], 0.0, "PIP: property of the bank.", "hold", "lens glow", "pip", pip_lens)
s("30", "CHARACTER_STILL", [535], 0.0, "Lucía at the machine: 'Then they can come and get it.'", "hold", "steam rises", "lucia", lucia_coffee)
s("30", "SET_STILL", [536], 0.6, "Mira, quietly: 'It prefers her.'", "hold", "none", "jax,mira,lucia", three_backs, ft=FT["farside"](28, 34))
s("30", "REAL_FOOTAGE", [], 3.0, "A small silence, for an old man on the Moon: the window, the grey far side.", "footage move only", "real", "", "REAL", ft=FT["farside"](34, 40), comp="Full frame.", snd="Silence; A4 one chord under.")
s("30", "INSERT", [(537, 0, 6.0)], 0.0, "PIP files a report on himself.", "slow push-in 3%", "lens glow", "pip", pip_lens)
s("30", "SET_STILL", [(537, 6.0, None)], 0.0, "Three backs: 'one count of enjoying it'.", "hold", "none", "jax,mira,lucia", three_backs, ft=FT["farside"](40, 46))
s("30", "TWO_SHOT", [538, 539], 0.0, "Over Jax's shoulder: 'Denied.' 'You are not the recipient.'", "hold", "none", "jax,pip", jax_ots)
s("30", "DATA_VISUAL", [], 3.4, "For the audience only: PIP's screen, REPORT #1,207 — SENT. Hold 2.6 s. Then a small grey line: READ — 00:00:01.3", "hold", "line appears after 2.6 s", img="CODE", snd="Silence; one PIP motif note when READ appears.")
s("30", "REAL_FOOTAGE", [541], 0.0, "The far side, grey and unlit by Earth, below the window.", "footage move only", "real", "", "REAL", ft=FT["moonvid"](30, 42, "Real Orion footage of the lunar surface below."), comp="Full frame.", snd="A1 theme (v2 under dialogue) begins under the V.O.")
s("30", "REAL_FOOTAGE", [542], 0.0, "The far side drifting below.", "footage move only", "real", "", "REAL", ft=FT["farside"](46, 54), comp="Full frame.")
s("30", "REAL_FOOTAGE", [543], 2.0, "'We definitely left him.'", "slow push 3%", "real still", "", "REAL", ft=FT["peek"](), comp="Full frame.")

# ================================================================= 31 TAG
chich_night = J("Chichikov", "chich_sharp_back_window", ["chich", "hall", "board"], "Night in an empty customs hall, lights low: a plump man in a grey overcoat in sharp focus, seen from behind against a large pure-black window, speaking into a small brass recorder; above him on the wall a flip-number board.")
recorder = J("Chichikov", "thumb_recorder_off", ["chich"], "Insert: a grey-gloved thumb clicking off a small brass pocket recorder, sharp focus, night light.")
box_close = box_open  # merged: reuse, no new image
lock_alone = J("Props", "padlock_alone_cage_night", ["lock", "cage"], "Insert: a big old iron padlock alone on the gate of an empty wire-mesh cage at night, shackle just sprung open.")
stove_dark = flame  # merged: reuse, no new image
trunk_hold = J("Props", "trunk_beside_parcel_hold", ["trunk", "parcel", "hold"], "Insert: a battered steamer trunk with a blank brown luggage tag strapped down beside a brown-paper parcel in a dim cargo hold at night.")
trunk_lid = J("Baron", "trunk_lid_moustache", ["trunk", "baron"], "Insert: the lid of a battered steamer trunk lifted one inch; in the dark gap, a great white moustache and bright eyes, no hat.")
warrant_ots = J("Jax", "jax_ots_warrant_night", ["jax", "bridge"], "Night on a ship's bridge: over Jax Vale's shoulder toward a glowing screen showing a list (illegible), his face not visible.")
s("31", "SET_STILL", [546], 1.0, "The empty hall, lights low. For the first time, Chichikov alone and in focus, seen from behind against the window and the black crater. On the board: DAYS WITHOUT INCIDENT: 0.", "very slow push-in 2%", "none", "chichikov", chich_night, ft=FT["pole"](), comp="Board reads 0 (code). Real polar plate in the window, night grade.", snd="Voss motif (M4), slow, on celesta.")
s("31", "INSERT", [], 1.0, "His thumb clicks the recorder off.", "hold", "click", "", recorder, snd="Recorder click.")
s("31", "INSERT", [], 1.0, "The inlaid box closes.", "hold", "lid closes", "", box_close)
s("31", "INSERT", [], 2.2, "The empty holding cage. The Riga padlock, alone, clicks open.", "hold", "shackle springs (2 states)", "", lock_alone, snd="Padlock click, no score change.")
s("31", "INSERT", [], 2.4, "In the empty inn, the cold dark stove. A blue flame catches.", "hold", "flame", "", stove_dark, snd="Gas whump, far away.")
s("31", "INSERT", [], 1.6, "The parcel, strapped down, warm.", "hold", "faint warmth shimmer", "", "LIB:parcel")
s("31", "INSERT", [], 3.0, "Beside it, the trunk: LOT 14. From inside, three small, polite knocks.", "hold; 3 x 1-frame jolts", "none", "", trunk_hold, comp="LOT 14 tag in code.", snd="Three knocks from inside a trunk (wood, muffled, polite): the first knock on a door we hear.")
s("31", "INSERT", [], 2.6, "The lid lifts an inch. Under it, in the dark, a great white moustache, and no hat. The lid closes.", "hold", "lid up/down (2 states)", "baron", trunk_lid)
s("31", "INSERT", [549], 0.0, "PIP's lens, night.", "hold", "lens glow", "pip", pip_lens)
s("31", "TWO_SHOT", [550, 551], 0.0, "Over Jax's shoulder toward the warrant screen.", "slow push-in 3%", "screen text scrolls (code)", "jax", warrant_ots)
s("31", "TWO_SHOT", [552, 553, 554], 0.0, "Over his shoulder: 'Captain—' PIP stops.", "push-in 3%", "none", "jax", warrant_ots)
s("31", "DATA_VISUAL", [], 1.4, "The warrant screen: CAPTAIN: nobody", "hold", "none", img="CODE")
s("31", "TWO_SHOT", [555], 0.0, "Over his shoulder: a beat; then he laughs.", "hold", "shoulders shake", "jax", warrant_ots)
s("31", "INSERT", [556, 557], 0.0, "PIP: 'Shall I file a correction?'", "hold", "lens glow", "pip", pip_lens)
s("31", "TWO_SHOT", [558], 0.4, "He goes, out of frame. 'Correction filed.'", "hold", "Jax layer slides out (cut-out over clean plate)", "", warrant_ots, comp="Clean plate: generate warrant_ots then paint Jax out, or crop the bridge master.")
s("31", "DATA_VISUAL", [], 4.2, "The field flickers: CAPTAIN: VALE, JAX. It refreshes. It settles. CAPTAIN: nobody", "hold", "flicker, refresh, settle", img="CODE", snd="Silence; a single refresh tick.")
s("31", "BLACK", [], 1.2, "CUT TO BLACK.", "none", "none", img="CODE", snd="Silence.")

# ================================================================= WWR
s("WWR", "REAL_FOOTAGE", [(561, 0, 12.0)], 0.6, "What was real: the real south-pole flyover; credits small at the bottom.", "footage move only", "credits roll", "", "REAL", ft=FT["fly"](0, 12), comp="Full frame; credit crawl.", snd="A1 theme (v2) under PIP.")
s("WWR", "REAL_FOOTAGE", [(561, 12.0, 24.0)], 0.0, "The permanently shadowed regions visualisation.", "footage move only", "credits roll", "", "REAL", ft=FT["psr"](0, 12), comp="Full frame.")
s("WWR", "REAL_FOOTAGE", [(561, 24.0, None)], 0.6, "Earth from the far side, real, from Orion.", "slow push-in 4%", "credits roll", "", "REAL", ft=FT["peek"](), comp="Full frame.")
s("END", "TITLE", [], 5.0, "End card.", "hold", "none", img="CODE", snd="A1-endcard-sting-5s.")

# ---------------------------------------------------------------- build
def line_info(spec):
    if isinstance(spec, int):
        idx, a, b = spec, 0.0, None
    else:
        idx, a, b = spec
    row = LINES[idx - 1]
    d = float(row["duration_s"])
    b2 = d if b is None else min(b, d)
    part = None if (a == 0 and b is None) else f"{a:.1f}-{b2:.1f}s of {d:.2f}s"
    return dict(line_id=f"E01-L{idx:03d}", speaker=row["speaker"], tags=row["tags"], text=row["spoken_text"],
                part=part, seconds=round(b2 - a, 2)), row

out, seen_img = [], set()
mouth_patches = []
for i, sh in enumerate(SHOTS):
    linfo, speakers, sp_tags = [], set(), {}
    for spec in sh["lines"]:
        li, row = line_info(spec)
        linfo.append(li)
        who = SPK.get(row["speaker"])
        if who:
            speakers.add(who)
            sp_tags.setdefault(who, []).append(row["tags"])
    talk = sum(l["seconds"] for l in linfo)
    dur = (talk + GAP * max(0, len(linfo) - 1) + (PAD if linfo else 0) + sh["beat"])
    dur = round(max(dur, 1.0), 1)
    chars = []
    for c in [c for c in sh["chars"].split(",") if c]:
        cid, mv = (c.split(":")[0], c.endswith(":m"))
        speaking = cid in speakers
        onscreen_voice = speaking and any(("V.O." not in t) for t in sp_tags.get(cid, []))
        patch = bool(mv and (onscreen_voice or (cid == "temi" and speaking)) and cid not in ("pip", "baron"))
        chars.append(dict(id=cid, mouth_visible=mv, speaking_in_shot=speaking, needs_mouth_patch=patch))
    patch_any = any(c["needs_mouth_patch"] for c in chars)
    img = sh["img"]
    lib, job, src = list(sh["assets"]), None, None
    if img and img.startswith("E01-J"):
        jb = JOBS[img]
        jb["used_by"].append(None)  # filled below
        if img not in seen_img:
            seen_img.add(img)
            job = dict(job_id=img, group=jb["group"], target_file=jb["target_file"], references=jb["references"],
                       prompt=prompt_for(jb))
            src = f"NEW image job {img}"
        else:
            src = f"REUSE of {img} (new crop/move/grade)"
            lib.append(f"{jb['target_file']} (from {img})")
        lib = [REF[k]["path"] for k in jb["ref_keys"] if REF[k]["path"] not in lib] + lib if job is None else lib
    elif img and img.startswith("LIB:"):
        key = img[4:]
        lib.append(REF[key]["path"]); src = "LIBRARY master (crop/move/grade)"
    elif img == "CODE":
        src = "BUILT IN CODE"
    elif img == "REAL":
        src = "REAL FOOTAGE"
    elif sh["typ"] == "BLACK":
        src = "BLACK"
    act = ACT[sh["sc"]]
    if sh["risk"] is None:
        nchar = len([c for c in chars])
        if sh["typ"] == "REAL_FOOTAGE":
            v = sh["ft"]["verified"] if sh["ft"] else True
            sh["risk"] = ("low", "verified plate") if v else ("medium", "plate unverified; fallback named")
        elif img == "CODE" or sh["typ"] in ("BLACK", "TITLE"):
            sh["risk"] = ("low", "built in code")
        elif job is not None:
            nref = len([k for k in JOBS[img]["ref_keys"] if k in CHAR_OF and CHAR_OF[k] not in ("pip",)])
            sh["risk"] = ("medium", f"new image with {nref} character references; check every face against its master") if nref >= 2 else \
                         ("low", "new single-subject image from its master")
        else:
            sh["risk"] = ("low", "reuse of an approved still (new crop, move or grade)")
    comp = sh["comp"] or ("Grade: house look (cinema.py grade: halation, split tone, filmic curve, vignette, grain 0.022). "
                          "Any text, numbers or tags added in code.")
    if any(c["id"] == "baron" for c in chars) or "baron" in (sh["desc"].lower()) and sh["typ"] in ("CHARACTER_STILL", "SET_STILL", "TWO_SHOT", "INSERT"):
        if any(c["id"] == "baron" for c in chars):
            sat = BARON_SAT.get(act, 100)
            if sh["sc"] == "22":
                comp += " Baron coat/moustache saturation 73% except the colour-return beat (100% between the ink-stays insert and the fade)."
            else:
                comp += f" Baron coat and moustache saturation {sat}% (hue-selective matte; never younger)."
    snd = sh["snd"] or SCENE_SOUND.get(sh["sc"], "")
    if img and img.startswith("E01-J") and sh["sc"] in ("8", "9", "21", "24", "26", "29") and "GENERATED" not in comp:
        dsc = JOBS[img]["shot_description"].lower()
        if any(k in dsc for k in ("lunar", "pressure suit", "generated", "crater", "apron")) and "cab" not in dsc:
            comp += " Exterior background is GENERATED, not real footage; log it as such."
    sid = f"E01-S{sh['sc'].replace('–', '-').zfill(2) if sh['sc'][0].isdigit() else sh['sc']}-{sh['n']:03d}"
    rec = OrderedDict(
        id=sid, scene=sh["sc"], act=act, order=i + 1, lines=linfo, duration_s=dur, type=sh["typ"],
        description=sh["desc"], camera=sh["cam"], motion=sh["mot"], characters=chars, needs_mouth_patch=patch_any,
        image_source=src, library_assets=lib,
        real_footage=sh["ft"] if sh["ft"] else "none",
        new_image_job=job, compositing=comp, sound=snd, risk=dict(level=sh["risk"][0], reason=sh["risk"][1]))
    if patch_any:
        mouth_patches.append((sid, [c["id"] for c in chars if c["needs_mouth_patch"]], [l["text"] for l in linfo]))
    out.append(rec)

# backfill used_by
for r in out:
    src = r["image_source"] or ""
    for jid in JOBS:
        if jid in src:
            JOBS[jid]["used_by"].append(r["id"])
for j in JOBS.values():
    j["used_by"] = [u for u in j["used_by"] if u]

JOBS = OrderedDict((k, v) for k, v in JOBS.items() if v["used_by"])
json.dump(out, open(f"{ROOT}/episodes/E01/shotlist.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
stats = dict(shots=out, jobs=JOBS, refs=REF, lib_gap_jobs=LIB_GAP_JOBS, mouth=mouth_patches)
json.dump(stats, open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("shots", len(out), "jobs", len(JOBS), "total s", round(sum(r["duration_s"] for r in out), 1))
print("mouth patches", mouth_patches)
