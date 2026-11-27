"""Kyutai Pocket TTS (pip install pocket-tts soundfile). Uses the public 'without voice cloning' weights + predefined voices.
Only voices with commercial-OK source datasets are cast (vctk CC-BY, voice-donations CC0, voice-zero LibriVox PD).
Excluded: cosette (Expresso CC-BY-NC), jean (EARS CC-BY-NC)."""
import sys, time, numpy as np, soundfile as sf, torch
from pocket_tts import TTSModel
from common import *
m=TTSModel.load_model()
CAST={ "JAX":dict(voice=sys.argv[1] if len(sys.argv)>1 else "marius"),
       "MIRA":dict(voice=sys.argv[2] if len(sys.argv)>2 else "vera"),
       "PIP":dict(voice=sys.argv[3] if len(sys.argv)>3 else "peter_yearsley"),
       "BARON":dict(voice=sys.argv[4] if len(sys.argv)>4 else "stuart_bell")}
ST={}
def synth(i,ch,txt,mood,out):
    v=CAST[ch]["voice"]
    if v not in ST: ST[v]=m.get_state_for_audio_prompt(v)
    a=m.generate_audio(ST[v],txt)
    a=a.detach().cpu().numpy() if hasattr(a,"detach") else np.asarray(a)
    sf.write(out,a.squeeze(),m.sample_rate)
if __name__=="__main__": print(timed_render("pocket-tts",CAST,synth))
