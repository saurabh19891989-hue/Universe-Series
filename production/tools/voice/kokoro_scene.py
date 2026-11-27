"""Kokoro-82M via kokoro-onnx. venv: pip install kokoro-onnx soundfile ; models from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 (kokoro-v1.0.onnx, voices-v1.0.bin)
Run: python kokoro_scene.py [variant]  (variant names in CAST below)"""
import sys, soundfile as sf
from kokoro_onnx import Kokoro
from common import *
M=f"{SCRATCH}/models/kokoro"
k=Kokoro(f"{M}/kokoro-v1.0.onnx", f"{M}/voices-v1.0.bin")
CASTS={
 "kokoro": {  # main pick
  "JAX":  dict(voice="am_puck", speed=1.08, lang="en-us"),
  "MIRA": dict(voice="hf_alpha", speed=0.95, lang="en-us"),   # Hindi-trained voice reading English => Indian-ish accent (hack)
  "PIP":  dict(voice="bm_george", speed=1.05, lang="en-gb"),
  "BARON":dict(voice="bm_fable", speed=0.88, lang="en-gb"),
 },
 "kokoro_alt": {  # no accent hack
  "JAX":  dict(voice="am_michael", speed=1.08, lang="en-us"),
  "MIRA": dict(voice="bf_emma", speed=0.93, lang="en-gb"),
  "PIP":  dict(voice="bm_daniel", speed=1.1, lang="en-gb"),
  "BARON":dict(voice="am_onyx", speed=0.85, lang="en-us"),
 }}
MOOD_SPEED={"quick":1.1,"quiet":0.85,"flat":1.0,"bombastic":1.0,"dry":1.0,"confiding":1.0}
def run(name):
    cast=CASTS[name]
    def synth(i,ch,txt,mood,out):
        c=cast[ch]; sp=c["speed"]*MOOD_SPEED.get(mood,1)/ (1 if mood!="flat" else 1)
        t=txt
        if ch=="MIRA" and mood=="quiet": t=t.replace("...",",  ...")
        s,sr=k.create(t,voice=c["voice"],speed=sp,lang=c["lang"]); sf.write(out,s,sr)
    print(timed_render(name,cast,synth))
if __name__=="__main__":
    for n in (sys.argv[1:] or CASTS): run(n)
