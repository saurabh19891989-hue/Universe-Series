"""WER of each engine's scene.mp3 vs script using faster-whisper small (CPU, int8)."""
import sys, re, json, glob, os
from faster_whisper import WhisperModel
import jiwer
from common import LINES, SAMPLES, SCRATCH
def norm(t):
    t=t.lower().replace("-"," ").replace("’","'")
    t=re.sub(r"[^a-z0-9' ]"," ",t); return re.sub(r"\s+"," ",t).strip()
ref=norm(" ".join(l[1] for l in LINES))
m=WhisperModel("small",device="cpu",compute_type="int8",download_root=f"{SCRATCH}/whisper")
engines=sys.argv[1:] or sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(f"{SAMPLES}/*/scene.mp3"))
for e in engines:
    segs,_=m.transcribe(f"{SAMPLES}/{e}/scene.mp3",language="en",beam_size=5)
    hyp=norm(" ".join(s.text for s in segs))
    o=jiwer.process_words(ref,hyp)
    wer=o.wer
    # list errors
    errs=[]
    for chunk in o.alignments[0]:
        if chunk.type!="equal":
            errs.append(f"{chunk.type}: '{' '.join(ref.split()[chunk.ref_start_idx:chunk.ref_end_idx])}' -> '{' '.join(hyp.split()[chunk.hyp_start_idx:chunk.hyp_end_idx])}'")
    p=f"{SAMPLES}/{e}/metrics.json"; cur=json.load(open(p)) if os.path.exists(p) else {}
    cur.update(wer=round(wer,3),wer_errors=errs,wer_model="faster-whisper small int8"); json.dump(cur,open(p,"w"),indent=2)
    print(e,round(wer,3),errs)
