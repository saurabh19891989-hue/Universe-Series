#!/usr/bin/env python3
"""Pick the E01 cast by maximin fingerprint distance. Output: voice-cast.json (+ distance table .md).
Run: <venv>/bin/python cast_select.py RAW_FP.json OUT_DIR"""
import itertools, json, subprocess, sys, numpy as np
from kokoro_onnx import Kokoro
from voice_fingerprint import SENTENCE, fingerprint, distance, scale_from, vec
KD = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice/models/kokoro"

def C(voice, speed, pitch=1.0, formant="preserved", lang=None, **kw):
    lang = lang or ("en-gb" if voice[:2] in ("bm", "bf") else "en-us")
    return dict(voice=voice, speed=speed, pitch=pitch, formant=formant, lang=lang, **kw)

CANDS = {
 "JAX": [C("am_puck", 1.08)],
 "PIP": [C("bm_george", 1.05, band="250-4500 Hz")],
 "BARON": [C("bm_fable", 0.90, 0.93), C("bm_lewis", 0.85, 0.92)],
 "CHICHIKOV": [C("bm_daniel", 0.92), C("am_michael", 0.90), C("am_adam", 0.92), C("bm_lewis", 0.92, 1.12)],
 "NOAKES": [C("bm_daniel", 1.15, 1.10, "shifted"), C("bm_george", 1.12, 1.0), C("bm_george", 1.15, 1.08, "shifted")],
 "MIRA": [C("bf_emma", 0.95, 0.94), C("bf_alice", 0.95, 0.90), C("bf_isabella", 0.95, 0.90), C("bf_lily", 0.95, 0.96)],
 "LUCÍA": [C("af_heart", 1.10), C("af_bella", 1.10), C("af_nova", 1.12), C("af_river", 1.10), C("af_sarah", 1.10)],
 "TEMI": [C("af_sky", 1.08, 1.04), C("af_jessica", 1.08, 1.02), C("af_aoede", 1.08, 1.05), C("af_alloy", 1.08, 1.06)],
 "MAMANI": [C("am_eric", 0.95), C("am_liam", 0.95), C("am_adam", 0.95, 1.06), C("em_alex", 0.95)],
}
def pitch_filter(c):
    return f"rubberband=pitch={c['pitch']}:formant={c['formant']}" if abs(c["pitch"] - 1) > 1e-6 else None

def render(k, c):
    s, sr = k.create(SENTENCE, voice=c["voice"], speed=c["speed"], lang=c["lang"])
    x = np.asarray(s, dtype="float32")
    f = pitch_filter(c)
    if f:
        p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-", "-af", f,
                            "-f", "f32le", "-ar", "24000", "-ac", "1", "-"], input=x.tobytes(), capture_output=True, check=True)
        x = np.frombuffer(p.stdout, dtype="<f4").copy()
    if c.get("band"):  # PIP's small-speaker band limit is part of his identity
        p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-", "-af",
                            "highpass=f=250,lowpass=f=4500", "-f", "f32le", "-ar", "24000", "-ac", "1", "-"], input=x.tobytes(), capture_output=True, check=True)
        x = np.frombuffer(p.stdout, dtype="<f4").copy()
    return fingerprint(x, 24000)

def main(raw_path, out_dir):
    raw = json.load(open(raw_path)); sd = scale_from(list(raw.values()))
    k = Kokoro(f"{KD}/kokoro-v1.0.onnx", f"{KD}/voices-v1.0.bin")
    fps = {r: [render(k, c) for c in cs] for r, cs in CANDS.items()}
    roles = list(CANDS)
    def ok(ch):
        f = {r: fps[r][i] for r, i in zip(roles, ch)}
        return (f["BARON"]["f0_median"] < f["PIP"]["f0_median"] - 10 and f["BARON"]["f0_median"] < f["NOAKES"]["f0_median"] - 10
                and f["BARON"]["rate_wps"] < f["NOAKES"]["rate_wps"] - 0.3 and f["NOAKES"]["rate_wps"] > f["CHICHIKOV"]["rate_wps"] + 0.3
                and f["MIRA"]["f0_median"] < f["LUCÍA"]["f0_median"] - 10 and f["MIRA"]["f0_median"] < f["TEMI"]["f0_median"] - 5
                and f["CHICHIKOV"]["rate_wps"] < f["JAX"]["rate_wps"])
    for b in range(len(CANDS["BARON"])):
        print("BARON cand", b, [round(distance(fps["BARON"][b], fps[r][i], sd),1) for r in ("PIP","NOAKES") for i in range(len(CANDS[r]))], round(fps["BARON"][b]["f0_median"]), round(fps["BARON"][b]["rate_wps"],2))
    print("NOAKES", [(round(f["f0_median"]), round(f["rate_wps"],2)) for f in fps["NOAKES"]])
    best = None
    for ch in itertools.product(*[range(len(CANDS[r])) for r in roles]):
        if not ok(ch): continue
        f = [fps[r][i] for r, i in zip(roles, ch)]
        fd = dict(zip(roles, f))
        if distance(fd["BARON"], fd["NOAKES"], sd) < 2.9 or distance(fd["BARON"], fd["PIP"], sd) < 2.4: continue
        d = [distance(a, b, sd) for a, b in itertools.combinations(f, 2)]
        score = (round(min(d), 3), np.mean(d))
        if best is None or score > best[0]: best = (score, ch)
    ch = best[1]; cast = {r: dict(CANDS[r][i], fingerprint=fps[r][i]) for r, i in zip(roles, ch)}
    names = roles; M = np.array([[distance(cast[a]["fingerprint"], cast[b]["fingerprint"], sd) for b in names] for a in names])
    # compare against previous table-read cast
    old = {"JAX": C("am_puck", 1.08), "PIP": C("bm_george", 1.05, band=1), "BARON": C("bm_fable", 0.91, 0.93), "MIRA": C("bf_emma", 0.95),
           "LUCÍA": C("af_heart", 1.08, 0.98), "CHICHIKOV": C("bm_lewis", 0.92), "NOAKES": C("bm_daniel", 1.12, 1.06, "shifted"),
           "TEMI": C("af_sky", 1.08, 1.04), "MAMANI": C("am_eric", 0.95, 0.97)}
    ofp = {r: render(k, c) for r, c in old.items()}
    Mo = np.array([[distance(ofp[a], ofp[b], sd) for b in names] for a in names])
    iu = np.triu_indices(len(names), 1)
    out = dict(selection="exhaustive maximin over candidate voice+speed+pitch combos, with role-fit ordering constraints",
               feature_weights=dict(f0_median=4, f0_range=1, centroid=2.25, rate=1, mfcc=2.25),
               feature_scale_sd_over_53_voices=[float(v) for v in sd],
               cast=cast, min_pair_distance_new=float(M[iu].min()), mean_pair_distance_new=float(M[iu].mean()),
               min_pair_distance_tableread_cast=float(Mo[iu].min()), mean_pair_distance_tableread_cast=float(Mo[iu].mean()),
               distance_matrix=dict(names=names, new=M.round(2).tolist(), tableread_cast=Mo.round(2).tolist()),
               all_candidates={r: [dict(CANDS[r][i], f0=round(fps[r][i]["f0_median"]), centroid=round(fps[r][i]["centroid"]), rate=round(fps[r][i]["rate_wps"], 2)) for i in range(len(CANDS[r]))] for r in roles})
    json.dump(out, open(f"{out_dir}/cast_select.json", "w"), indent=1, ensure_ascii=False)
    def tab(M):
        s = "| |" + "|".join(names) + "|\n|---|" + "---|" * len(names) + "\n"
        for i, a in enumerate(names): s += f"|**{a}**|" + "|".join("" if i == j else f"{M[i][j]:.1f}" for j in range(len(names))) + "|\n"
        return s
    feat = "| role | voice | speed | pitch | formant | f0 median Hz | f0 range Hz | centroid Hz | rate words/s |\n|---|---|---|---|---|---|---|---|---|\n"
    for r in names:
        c = cast[r]; fp = c["fingerprint"]
        feat += f"|{r}|{c['voice']}|{c['speed']}|{c['pitch']}|{c['formant']}|{fp['f0_median']:.0f}|{fp['f0_range']:.0f}|{fp['centroid']:.0f}|{fp['rate_wps']:.2f}|\n"
    md = (f"# E01 voice-cast fingerprint distances\n\nDistance = weighted, z-scored (over all 53 Kokoro voices) difference of median f0, f0 range, spectral centroid, speaking rate "
          f"and 12 MFCC means on one fixed sentence, measured after the pitch/speed/band treatment. Larger = easier to tell apart by these measures. These are not listening results; nobody has listened.\n\n"
          f"## Chosen cast\n\n{feat}\n## Pairwise distances, new cast (min {M[iu].min():.2f}, mean {M[iu].mean():.2f})\n\n{tab(M)}\n"
          f"## Pairwise distances, table-read cast (min {Mo[iu].min():.2f}, mean {Mo[iu].mean():.2f})\n\n{tab(Mo)}\n")
    open(f"{out_dir}/voice-cast-distances.md", "w").write(md); print(md)

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
