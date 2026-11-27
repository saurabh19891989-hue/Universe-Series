"""Piper (piper-tts 1.x). venv: pip install piper-tts soundfile ; voices from huggingface.co/rhasspy/piper-voices.
NOTE: only voices whose dataset licence allows commercial use are cast (ryan = CC-BY-NC, hfc_male = BY-NC-SA are excluded)."""
import wave, sys
from piper import PiperVoice, SynthesisConfig
from common import *
P=f"{SCRATCH}/models/piper"
V={n:PiperVoice.load(f"{P}/{n}.onnx") for n in ["en_US-joe-medium","en_GB-vctk-medium","en_GB-northern_english_male-medium"]}
CAST={
 "JAX":  dict(model="en_US-joe-medium", length=0.92, noise=0.667, noisew=0.8),               # CC0
 "MIRA": dict(model="en_GB-vctk-medium", spk=87, length=1.05, noise=0.5, noisew=0.6, vctk="p248 (Indian-accented female)"),  # CC-BY 4.0
 "PIP":  dict(model="en_GB-vctk-medium", spk=95, length=0.92, noise=0.3, noisew=0.4, vctk="p226 (British male)"),
 "BARON":dict(model="en_GB-northern_english_male-medium", length=1.15, noise=0.8, noisew=0.9), # CC-BY-SA 4.0 (OpenSLR 83)
}
MOOD_LEN={"quick":0.92,"quiet":1.2,"bombastic":1.0}
def synth(i,ch,txt,mood,out):
    c=CAST[ch]; v=V[c["model"]]
    cfg=SynthesisConfig(speaker_id=c.get("spk"),length_scale=c["length"]*MOOD_LEN.get(mood,1),noise_scale=c["noise"],noise_w_scale=c["noisew"])
    with wave.open(out,"wb") as w: v.synthesize_wav(txt,w,syn_config=cfg)
if __name__=="__main__": print(timed_render("piper",CAST,synth))
