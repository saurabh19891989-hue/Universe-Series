"""Shared scene script + assembly + WER tools for the free-TTS bake-off.
Usage from engine scripts: from common import LINES, assemble, out_dir"""
import os, json, subprocess, time, numpy as np, soundfile as sf
REPO = "/home/user/Universe-Series"
SAMPLES = f"{REPO}/samples/voices"
SCRATCH = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/voice"

# (character, spoken text, gap-after seconds, mood note)
LINES = [
 ("JAX", "Here's the thing nobody tells you about the Moon. It is a terrible place to be broke. I'd been broke on nine worlds, and the Moon was the only one that charged me for the view.", 0.5, "confiding"),
 ("PIP", "Captain. The destination no longer exists.", 0.3, "flat"),
 ("JAX", "It's a crater, Pip. Craters don't leave.", 0.25, "quick"),
 ("PIP", "The crater is present. The address has been withdrawn. I am now legally required to deliver this parcel to nowhere, and we are eleven minutes late.", 0.4, "flat"),
 ("MIRA", "That's not a glitch. Somebody deleted it. Somebody deleted a place.", 0.45, "dry"),
 ("BARON", "Deleted? Madam, I have been shot from a cannon, swallowed by a fish, and married on the Moon, twice, and I have never once been deleted. I find it extremely rude.", 0.3, "bombastic"),
 ("JAX", "Who is this?", 0.25, "quick"),
 ("PIP", "According to the registry: nobody. According to him: Baron Munchausen.", 0.5, "flat"),
 ("MIRA", "Jax. If they can erase a place... they can erase the people in it.", 0.6, "quiet"),
 ("JAX", "And that was the moment. Right there. I could have handed over the parcel, taken the money, and been a happy, shallow man for the rest of my life. Instead I did the stupidest thing I have ever done. I asked a follow-up question.", 0.0, "confiding"),
]
CHARS = ["JAX", "MIRA", "PIP", "BARON"]

def out_dir(engine):
    d = f"{SAMPLES}/{engine}"; os.makedirs(d, exist_ok=True); return d

def work_dir(engine):
    d = f"{SCRATCH}/work/{engine}"; os.makedirs(d, exist_ok=True); return d

def _concat(parts, sr):
    return np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)

def _mp3(wav_path, mp3_path, norm=True):
    af = "loudnorm=I=-16:TP=-1.5:LRA=11" if norm else "anull"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav_path,"-af",af,"-ar","44100","-ac","1","-b:a","192k",mp3_path],check=True)

def assemble(engine, clips, sr_of=None):
    """clips: list of (idx, wav_path) in LINES order. Writes scene.mp3 + per-character mp3s."""
    d = out_dir(engine); w = work_dir(engine)
    scene=[]; per={c:[] for c in CHARS}
    for (i,p),(ch,_,gap,_) in zip(clips, LINES):
        x, sr = sf.read(p, dtype="float32")
        if x.ndim>1: x=x.mean(1)
        if sr!=24000:
            import subprocess as sp
            tmp=p+".24k.wav"; sp.run(["ffmpeg","-y","-loglevel","error","-i",p,"-ar","24000","-ac","1",tmp],check=True)
            x,_=sf.read(tmp,dtype="float32")
        sil=np.zeros(int(24000*gap),dtype="float32")
        scene += [x, sil]; per[ch] += [x, np.zeros(int(24000*0.4),dtype="float32")]
    sf.write(f"{w}/scene.wav", _concat(scene,24000), 24000); _mp3(f"{w}/scene.wav", f"{d}/scene.mp3")
    for c in CHARS:
        sf.write(f"{w}/{c}.wav", _concat(per[c],24000), 24000); _mp3(f"{w}/{c}.wav", f"{d}/{c.lower()}.mp3")
    return f"{d}/scene.mp3"

def write_meta(engine, **kw):
    p=f"{out_dir(engine)}/metrics.json"
    cur=json.load(open(p)) if os.path.exists(p) else {}
    cur.update(kw); json.dump(cur,open(p,"w"),indent=2)

def timed_render(engine, casting, synth):
    """synth(idx, char, text, mood, out_wav) renders one line. Returns scene path; records timing."""
    w=work_dir(engine); clips=[]; t0=time.time(); dur=0
    for i,(ch,txt,gap,mood) in enumerate(LINES):
        p=f"{w}/line{i:02d}_{ch}.wav"; synth(i,ch,txt,mood,p); clips.append((i,p))
    secs=time.time()-t0
    scene=assemble(engine, clips)
    json.dump(casting, open(f"{out_dir(engine)}/casting.json","w"), indent=2)
    speech=sum(sf.info(p).duration for _,p in clips)
    words=sum(len(l[1].split()) for l in LINES)
    rtf=secs/speech
    # compute hours for 5500 words: speech seconds per word * words * rtf
    ep_speech=speech/words*5500
    write_meta(engine, synth_seconds=round(secs,1), speech_seconds=round(speech,1), rtf=round(rtf,3),
               episode_compute_hours_est=round(ep_speech*rtf/3600,2), words=words)
    return scene
