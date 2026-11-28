# Render the four sample-5 score cues with the v3 sound. usage: python3 render_sample5.py OUT_DIR [A B1 CUT B2]
import sys, time, json, numpy as np, soundfile as sf
sys.path.insert(0, "/home/user/Universe-Series/production/tools/music")
import sample5_score as P, v3mix
out = sys.argv[1]
for k in (sys.argv[2:] or list(P.ALL)):
    t0 = time.time(); c, mix, m = P.ALL[k]()
    y, _ = v3mix.render(c, mix, m["dur"], hall=m["hall"], target=m["target"], fade_s=m["fade_s"])
    sf.write(f"{out}/cue_{k}.wav", y, 48000, subtype="FLOAT")
    print(json.dumps(dict(cue=k, start=m["start"], dur=m["dur"], render_s=round(time.time()-t0,1))), flush=True)
