"""WER of gemini scene files vs script (faster-whisper small int8), same normalisation as wer.py."""
import sys, re, glob, os, subprocess, numpy as np, jiwer
from faster_whisper import WhisperModel
from common import LINES, SAMPLES, SCRATCH
def norm(t):
    t=t.lower().replace("11","eleven").replace("9 ","nine ").replace("-"," ").replace("’","'")
    t=re.sub(r"[^a-z0-9' ]"," ",t); return re.sub(r"\s+"," ",t).strip()
ref=norm(" ".join(l[1] for l in LINES))
m=WhisperModel("small",device="cpu",compute_type="int8",download_root=f"{SCRATCH}/whisper")
for f in sys.argv[1:]:
    raw=subprocess.run(["ffmpeg","-loglevel","error","-i",f,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True,check=True).stdout
    segs,_=m.transcribe(np.frombuffer(raw,dtype=np.float32),language="en",beam_size=5)
    hyp=norm(" ".join(s.text for s in segs)); o=jiwer.process_words(ref,hyp)
    errs=[f"{c.type}: '{' '.join(ref.split()[c.ref_start_idx:c.ref_end_idx])}' -> '{' '.join(hyp.split()[c.hyp_start_idx:c.hyp_end_idx])}'" for c in o.alignments[0] if c.type!="equal"]
    print(os.path.basename(f), round(o.wer,3)); [print("  ",e) for e in errs]
