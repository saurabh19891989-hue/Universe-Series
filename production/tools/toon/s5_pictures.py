#!/usr/bin/env python3
"""SAMPLE 5 pictures (animated redesign). Codex CLI via production/tools/look/codex_image.py,
4 at once. Outputs: SCRATCH/cx/s5/<name>.png. usage: s5_pictures.py NAME [NAME ...] | designs
Exit code 3 from the wrapper = usage limit: printed as LIMIT.
Edits (mouth/blink/brow sets) pass the base picture as reference 1 and ask for an identical
picture with one change; production/tools/toon/s5_faces.py then pastes only the changed region.
"""
import subprocess, sys, concurrent.futures as cf, os
R = "/home/user/Universe-Series"
S = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
CX = f"{R}/production/tools/look/codex_image.py"
OUT = f"{S}/cx/s5"
M = {"jax": f"{R}/assets/characters/jax/master.jpg", "mira": f"{R}/assets/characters/mira/master.jpg",
     "baron": f"{R}/assets/characters/baron/master.jpg"}
STY = {
 "A": ("STYLE: a polished modern 2D animated feature film character design of our own: stylised but grounded proportions, "
       "slightly larger expressive eyes, clean simplified shapes, confident clean ink lines, crisp cel shading with soft painted "
       "highlights and a cool teal rim light, bright saturated colour. Not photoreal, not 3D. No text, no logos."),
 "B": ("STYLE: a bold modern 2D animated series character design of our own: clearly animated proportions (head about one sixth "
       "of the height), big expressive eyes, simplified graphic shapes, strong appealing silhouette, elegant slightly exaggerated "
       "proportions, clean even ink lines, crisp cel shading with one shadow tone plus painted highlights and a teal rim light, "
       "very bright saturated colour. Not photoreal, not 3D. No text, no logos."),
}
HOT = ("Strikingly attractive and charismatic, glamorous film-star appeal carried by the face, hair, posture and styling; "
       "tasteful, fully clothed in the costume, nothing revealing.")
CHAR = {
 "jax": ("Jax Vale, the same man as reference image 1, kept recognisable: Mediterranean Greek man, late 30s, olive skin, dark "
         "curly hair greying slightly at the temples, short stubble, strong jaw, crooked confident half-smile; scuffed "
         "burnt-orange flight jacket with many pockets over a grey t-shirt, dark harness straps, dark brown work trousers, "
         "heavy brown boots. " + HOT),
 "mira": ("Dr Mira Sen, the same woman as reference image 1, kept recognisable: Bengali Indian woman aged 32 (young), "
          "strikingly beautiful, warm brown skin, large dark intelligent eyes, long dark braid over her right shoulder; fitted "
          "indigo flight suit with tan shoulder patches and a brown belt, a brass loupe on a chain round her neck, dark boots. " + HOT),
 "baron": ("Baron Munchausen, the same old gentleman as reference image 1, kept recognisable: German man in his 70s, tall and "
           "thin, enormous white moustache that completely covers his mouth, bushy white eyebrows, twinkling eyes, white hair "
           "in a pigtail, black tricorn hat; moth-eaten red 18th-century cavalry coat with brass buttons and gold frogging over a "
           "patched grey pressure suit. Grand theatrical posture, funny and lovable, a magnificent old show-off (NOT a "
           "glamorous young man)."),
}
SHEET = ("CHARACTER DESIGN SHEET on a plain flat light grey background: on the LEFT a full-body drawing standing in a relaxed "
         "confident pose, body turned three-quarters toward the right, whole figure from hair to boots inside the frame; on the "
         "RIGHT a large head-and-shoulders close-up of the same character, three-quarters toward the right, closed-mouth smile. "
         "Same costume and colours in both drawings. No text, no labels.")
JOBS = {}
for c in CHAR:
    for v in STY:
        JOBS[f"{c}_{v}"] = (f"{STY[v]}\nCHARACTER: {CHAR[c]}\n{SHEET}", [M[c]])

def run(n):
    b, refs = JOBS[n]
    cmd = ["python3", CX, "s5", n, b, "--no-style", "--purpose", "sample 5 animated redesign"]
    for r in refs: cmd += ["-i", r]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return n, p.returncode, (p.stdout or p.stderr)[-300:]

def main(sel):
    with cf.ThreadPoolExecutor(4) as ex:
        for n, rc, out in ex.map(run, sel):
            print(n, rc, out.replace("\n", " ")[:260], flush=True)
            if rc == 3: print("LIMIT", n, flush=True)

if __name__ == "__main__":
    import s5_jobs  # second-stage jobs (poses, edits) live in s5_jobs.py
    JOBS.update(s5_jobs.jobs(JOBS, STY, CHAR, M, OUT))
    sel = sys.argv[1:]
    if sel == ["designs"]: sel = [k for k in JOBS if k.endswith(("_A", "_B"))]
    main(sel)
