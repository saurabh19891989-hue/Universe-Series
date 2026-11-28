"""usage: python3 -I e01_customs_plan.py  (writes SCRATCH/audio2/customs_plan.json), then
   python3 ../mix3.py episodes/E01/toon-test-shotlist.json SCRATCH/audio2/customs_plan.json OUT.wav --report OUT.json
Builds the mix3 plan for the E01 customs-desk toon test (levels set from measurements)."""
import json, sys, numpy as np
sys.path.insert(0, "/home/user/Universe-Series/production/tools/music")
sys.path.insert(0, "/home/user/Universe-Series/production/tools/sfx")
import dsp, mix3
S="/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad"
A2=S+"/audio2"
def lufs(p, a=0, d=None):
    x=mix3.load(p)[int(a*48000):]; x=x[:int(d*48000)] if d else x
    return dsp.loudness(x)
def peak(p, a=0, d=None):
    x=mix3.load(p)[int(a*48000):]; x=x[:int(d*48000)] if d else x
    return float(20*np.log10(np.abs(x).max()+1e-9))
DLG=-23.0   # line loudness before master
def bed(src, at, dur, target, **k):
    g = target - lufs(src, k.get("from",0), min(dur, 20))
    return dict(src=src, at=at, dur=dur, gain_db=round(g,1), **k)
def hit(src, at, peak_rel, **k):          # peak relative to dialogue peaks (~ -9 dBFS at -23 LUFS lines)
    g = (-9 + peak_rel) - peak(src, k.get("from",0), k.get("dur"))
    return dict(src=src, at=at, gain_db=round(g,1), **k)
R=A2+"/fx_real"; E=S+"/e01/sfx"
walk=[10.95 + k*0.486 for k in range(7)]
plan = {
 "vars": {"A2": A2},
 "room": {"ir": A2+"/libs/voxengo/Masonic Lodge.wav", "wet_db": -15, "predelay_s": 0.018, "hp_hz": 220, "from_s": 6.6},
 "speakers": {
   "jax": {"hp": 95, "eq": [["peak", 220, 1.0, -2.5], ["peak", 3200, 0.9, 3.0], ["hs", 9000, 0.7, 2.0]], "comp": {"thr_rel": 6, "ratio": 3.0}},
   "mira": {"hp": 110, "eq": [["peak", 350, 1.0, -1.5], ["peak", 3500, 0.9, 2.5], ["hs", 10000, 0.7, 1.5]], "comp": {"thr_rel": 6, "ratio": 3.0}}},
 "dialogue": {"line_lufs": DLG, "deess": {"f": 5500, "thr_rel": 2}, "pan_scale": 0.3},
 "music": [dict(src=A2+"/out/E01-customs-scene-v3.wav", at=0.0, dur=6.95, gain_db=-5, fade_out=0.05),
           dict(src=A2+"/out/E01-customs-scene-v3.wav", at=6.95, dur=45.95, gain_db=-12, fade_in=0.05, fade_out=0.03, **{"from": 6.95}),
           dict(src=A2+"/out/E01-customs-scene-v3.wav", at=52.9, dur=3.1, gain_db=-6, fade_in=0.03, **{"from": 52.9})],
 "beds": [
   bed(E+"/ship_engine_idle_loop.wav", 0.0, 6.4, -27, fade_in=0.8, fade_out=0.3, hp_hz=45),
   bed(E+"/ship_engine_spindown.wav", 6.2, 2.6, -30, fade_out=1.2, hp_hz=45, loop=False),
   bed(R+"/roomtone_large_interior_ac.wav", 6.8, 49.2, -48, fade_in=0.5, fade_out=0.6, hp_hz=70, **{"from": 3.0}),
   bed(R+"/roomtone_empty_office_hallway.wav", 6.8, 49.2, -47, fade_in=0.5, fade_out=0.6, hp_hz=80, **{"from": 5.0}),
   bed(E+"/customs_hall_roomtone_loop.wav", 6.8, 49.2, -49, fade_in=0.5, fade_out=0.6, hp_hz=60),
   bed(R+"/fluorescent_hum_store.wav", 6.8, 49.2, -55, fade_in=0.5, fade_out=0.6, hp_hz=110, **{"from": 10.0}),
 ],
 "fx": [
   # footsteps: single steps cut from a real take, placed on the walk cycle, following Jax across the frame
   dict(src=R+"/footsteps_shoes_hard_floor.wav", gain_db=round(-9-12-peak(R+"/footsteps_shoes_hard_floor.wav"),1),
        follow="jax", send_db=-10, eq=[["hp", 90, 0.7]],
        slice={"thr_db": -22, "min_gap_s": 0.3, "len_s": 0.32, "times": walk, "pick": [0,1,2,3,4,5,6], "vary_db": [0,-1.5,-0.5,-2,0,-1,-0.5]}),
   # cloth on the big gestures (Jax arm moves; Mira's form hand and stamp wind-up)
   dict(src=R+"/clothing_movement.wav", gain_db=round(-9-20-peak(R+"/clothing_movement.wav"),1), follow="jax", send_db=-16,
        eq=[["hp", 200, 0.7]], slice={"thr_db": -18, "min_gap_s": 0.4, "len_s": 0.4,
        "times": [8.05, 14.25, 17.95, 21.0, 24.7, 26.7, 33.45, 35.75, 46.8, 50.85], "vary_db": [0,-2,-1,-3,0,-2,-1,0,-2,0]}),
   dict(src=R+"/clothing_movement.wav", gain_db=round(-9-22-peak(R+"/clothing_movement.wav"),1), follow="mira", send_db=-16,
        eq=[["hp", 250, 0.7]], slice={"thr_db": -18, "min_gap_s": 0.4, "len_s": 0.35, "times": [13.1, 30.25, 44.3], "pick": [3,5,7]}),
   # paper: the parcel docket (12.95) and the form (22.08): real paper + our synth slide
   hit(R+"/paper_rustling.wav", 12.9, -14, follow="mira", send_db=-14, dur=0.9, fade_out=0.3, **{"from": 1.0}),
   hit(E+"/paper_slip_rustle.wav", 22.077, -13, follow="mira", send_db=-14),
   hit(R+"/paper_shuffle_stack.wav", 22.2, -18, follow="mira", send_db=-16, dur=0.8, fade_out=0.3, **{"from": 2.0}),
   # the stamp: wind-up swish, then real rubber stamp + our heavy synth thunk + a real desk bang for weight
   hit(R+"/swish_whoosh.wav", 52.5, -16, pan=0.35, send_db=-12, dur=0.5, fade_out=0.15),
   hit(R+"/rubber_stamp_plastic.wav", 52.98, -6, pan=0.3, send_db=-8, dur=0.6, fade_out=0.2),
   hit(E+"/customs_desk_stamp_heavy_a.wav", 52.98, -4, pan=0.3, send_db=-8),
   hit(R+"/bang_table_desk.wav", 52.985, -9, pan=0.3, send_db=-8, dur=0.5, fade_out=0.2),
   # Jax flinches at the slam
   dict(src=R+"/clothing_movement.wav", gain_db=round(-9-16-peak(R+"/clothing_movement.wav"),1), follow="jax", send_db=-14,
        eq=[["hp", 200, 0.7]], slice={"thr_db": -12, "min_gap_s": 0.4, "len_s": 0.5, "times": [53.06], "pick": [2]}),
 ],
 "duck": {"speech_db": -9, "broad_db": -4, "fx_db": -2},
 "master": {"lufs": -16, "tp": -1.5}}
json.dump(plan, open(A2+"/customs_plan.json","w"), indent=1)
print("ok")
