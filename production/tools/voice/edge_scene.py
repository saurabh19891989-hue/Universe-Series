"""edge-tts (UNOFFICIAL Microsoft Edge read-aloud endpoint). venv: pip install edge-tts
Prosody (rate/pitch/volume) is the only control the library exposes (SSML is stripped by the service)."""
import asyncio, os, ssl, edge_tts, edge_tts.communicate as _ec
# Sandbox only: trust the agent proxy's CA bundle (verification stays ON). Harmless elsewhere.
if os.path.exists('/root/.ccr/ca-bundle.crt'): _ec._SSL_CTX=ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
PROXY=os.environ.get('HTTPS_PROXY')
from common import *
CAST={
 "JAX":  dict(voice="en-US-GuyNeural",   rate="+10%", pitch="+0Hz"),
 "MIRA": dict(voice="en-IN-NeerjaNeural",rate="-3%",  pitch="-2Hz"),
 "PIP":  dict(voice="en-GB-RyanNeural",  rate="+8%",  pitch="+0Hz"),
 "BARON":dict(voice="en-GB-ThomasNeural",rate="-12%", pitch="-6Hz"),
}
MOOD={"quick":("+8%",None),"quiet":("-18%","-4Hz"),"bombastic":("-5%","+3Hz")}
def synth(i,ch,txt,mood,out):
    c=CAST[ch]; r=c["rate"]; p=c["pitch"]
    def add(a,b): return f"{int(a.rstrip('%'))+int(b.rstrip('%')):+d}%"
    if mood in MOOD:
        if MOOD[mood][0]: r=add(r,MOOD[mood][0])
        if MOOD[mood][1]: p=f"{int(p[:-2])+int(MOOD[mood][1][:-2]):+d}Hz"
    async def go():
        await edge_tts.Communicate(txt,c["voice"],rate=r,pitch=p,proxy=PROXY).save(out+".mp3")
    asyncio.run(go())
    import subprocess; subprocess.run(["ffmpeg","-y","-loglevel","error","-i",out+".mp3","-ar","24000","-ac","1",out],check=True)
if __name__=="__main__": print(timed_render("edge-tts",CAST,synth))
