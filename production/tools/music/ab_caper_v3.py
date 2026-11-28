"""A/B: re-render the first 40 s of E01 C1 caper (same notes) with the v3 sound. usage: python3 ab_caper_v3.py OUT.wav"""
import sys, time, numpy as np, soundfile as sf
sys.path.insert(0,"/home/user/Universe-Series/production/tools/music")
import e01_score as E, v3mix, dsp
t0=time.time()
c,mix,meta=E.caper()
m3={k:dict(v) for k,v in mix.items()}
m3["cornet"].update(depth="mid", width=0.7, pan=-0.15, send=0.3)
m3["bsn"].update(depth="mid", width=0.7, pan=0.25, send=0.28)
m3["glock"].update(inst="glock3", depth="back", width=0.5, pan=0.4, send=0.35)
m3["gtr"]=dict(inst="guitar", lvl=-23, pan=0.35, width=0.9, depth="front", send=0.18, group="rhythm")
m3["pizzU"].update(depth="mid", width=1.0, pan=-0.35, send=0.3)
m3["bass"].update(depth="mid", width=0.5, pan=0.0, send=0.15)
m3["drums"]=dict(lvl=-28, pan=0.05, width=1.0, depth="back", send=0.25, group="rhythm", kit={38:"snare_side",44:"hat_pedal"})
y,_=v3mix.render(c, m3, 40.0, hall="Scala Milan Opera Hall", target=-17.0)
sf.write(sys.argv[1], y, 48000, subtype="PCM_24")
print("render s", round(time.time()-t0,1))
