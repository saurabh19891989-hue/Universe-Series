"""MeloTTS (MIT). venv python3.11: pip install "git+https://github.com/myshell-ai/MeloTTS.git" soundfile "setuptools<81"
Sandbox fixes: unidic dict missing -> symlink site-packages/unidic/dicdir to unidic_lite/dicdir; nltk averaged_perceptron_tagger_eng + cmudict download."""
import sys, soundfile as sf
sys.path.insert(0, __import__("os").path.dirname(__file__))
from melo.api import TTS
from common import *
m=TTS(language="EN",device="cpu"); S=m.hps.data.spk2id
CAST={"JAX":dict(spk="EN-US",speed=1.1),"MIRA":dict(spk="EN_INDIA",speed=0.95),
      "PIP":dict(spk="EN-BR",speed=1.05),"BARON":dict(spk="EN-AU",speed=0.9)}
MOOD={"quick":1.1,"quiet":0.85}
def synth(i,ch,txt,mood,out):
    c=CAST[ch]; m.tts_to_file(txt,S[c["spk"]],out,speed=c["speed"]*MOOD.get(mood,1.0),quiet=True)
if __name__=="__main__": print(timed_render("melotts",CAST,synth))
