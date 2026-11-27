"""Re-render cues with the v2 sound (VPO 3 SFZ orchestra + GeneralUser GS colours).

python3 v2_render.py            # everything
python3 v2_render.py A1 A4      # selected cues
Each cue script is run first so its MIDI is current, then mixed per the table below.
"""
import os
import sys
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sulib
import v2mix

MID = sulib.MIDI_DIR

# mix tables: track -> preset, lvl = active-RMS target dBFS (auto-balance), pan (-1..1), reverb send
A1_MIX = {
    "cello": dict(inst="vc", lvl=-24, pan=0.25, send=0.22),
    "bass": dict(inst="cb", lvl=-25, pan=0.35, send=0.2),
    "viola": dict(inst="vla", lvl=-29, pan=0.1, send=0.25),
    "pad": dict(inst="vln2", lvl=-27, pan=-0.15, send=0.45),
    "vln": dict(inst="vln1", lvl=-21, pan=-0.45, send=0.4),
    "horn": dict(inst="hn", lvl=-21, pan=-0.2, send=0.45),
    "tpt": dict(inst="tpt", lvl=-23, pan=0.15, send=0.4),
    "lowbr": dict(inst="tbn", lvl=-25, pan=0.3, send=0.35),
    "tuba": dict(inst="tuba", lvl=-27, pan=0.35, send=0.3),
    "choir": dict(gm=True, lvl=-30, pan=0, send=0.6),            # no free CC0 choir found
    "sitar": dict(gm=True, sf2="fluidr3", lvl=-21, pan=0.45, send=0.35),  # FluidR3 sitar measured cleaner than GU GS
    "taiko": dict(gm=True, lvl=-23, pan=0, send=0.3),            # GeneralUser GS taiko
    "timp": dict(inst="timp", lvl=-25, pan=0, send=0.35),
    "drums": dict(lvl=-29, pan=0, send=0.4),
}
A4_MIX = {
    "flute": dict(inst="fl", lvl=-20, pan=0.15, send=0.45),
    "vln": dict(inst="vln1", lvl=-24, pan=-0.4, send=0.5),
    "vsolo": dict(inst="vln_solo", lvl=-21, pan=-0.1, send=0.45),
    "pad": dict(inst="vln2", lvl=-30, pan=0.0, send=0.55),
    "cello": dict(inst="vc", lvl=-25, pan=0.35, send=0.35),
    "gtr": dict(gm=True, sf2="fluidr3", lvl=-27, pan=-0.35, send=0.3),  # FluidR3 nylon: lower noise floor
    "harp": dict(inst="harp", lvl=-27, pan=0.4, send=0.45),
    "drums": dict(lvl=-31, pan=0.1, send=0.3),
}
A5_MIX = {
    "shaku": dict(gm=True, lvl=-20, pan=-0.1, send=0.5),          # GeneralUser GS shakuhachi
    "koto": dict(gm=True, lvl=-22, pan=0.3, send=0.35),          # GeneralUser GS koto
    "pad": dict(inst="vln2", lvl=-29, pan=0, send=0.55),
    "bass": dict(inst="cb", lvl=-28, pan=0.1, send=0.3),
    "taiko": dict(gm=True, lvl=-22, pan=0, send=0.3),
    "shime": dict(gm=True, lvl=-30, pan=0.3, send=0.25),
    "drums": dict(lvl=-30, pan=-0.2, send=0.3),
}

A1_FULL_MIX = dict(A1_MIX)
A1_FULL_MIX.update({
    "pizz": dict(inst="pizz", lvl=-27, pan=0.3, send=0.35),
    "harp": dict(inst="harp", lvl=-28, pan=-0.5, send=0.5),
    "flute": dict(inst="fl", lvl=-25, pan=-0.2, send=0.45),
})
JAX_MIX = {
    "clar": dict(inst="cl", lvl=-20, pan=-0.1, send=0.3),
    "gtr": dict(gm=True, sf2="fluidr3", lvl=-25, pan=0.35, send=0.25),
    "pizzB": dict(inst="pizz", lvl=-24, pan=0.15, send=0.2),
    "pad": dict(inst="vln2", lvl=-33, pan=-0.2, send=0.5),
    "drums": dict(lvl=-31, pan=0.1, send=0.2),
}
MIRA_MIX = {
    "flute": dict(inst="fl", lvl=-20, pan=0.1, send=0.45),
    "cello": dict(inst="vc_solo", lvl=-24, pan=0.35, send=0.4),
    "drone": dict(inst="vc", lvl=-29, pan=-0.1, send=0.5),
    "pad": dict(inst="vln2", lvl=-31, pan=-0.3, send=0.55),
    "celesta": dict(inst="celesta", lvl=-29, pan=-0.45, send=0.35),
    "harp": dict(inst="harp", lvl=-27, pan=0.5, send=0.45),
}
PIP_MIX = {
    "picc": dict(inst="picc", lvl=-22, pan=0.1, send=0.25),
    "glock": dict(inst="glock", lvl=-28, pan=0.3, send=0.25),
    "bsn": dict(inst="bsn", lvl=-23, pan=-0.2, send=0.2),
    "pizz": dict(inst="pizz", lvl=-26, pan=-0.35, send=0.2),
    "drums": dict(lvl=-27, pan=0.0, send=0.25),
}
VOSS_MIX = {
    "vln": dict(inst="vln1", lvl=-20, pan=-0.4, send=0.5),
    "celesta": dict(inst="celesta", lvl=-27, pan=-0.2, send=0.5),
    "cello": dict(inst="vc", lvl=-25, pan=0.3, send=0.35),
    "bass": dict(inst="cb", lvl=-28, pan=0.35, send=0.3),
    "chords": dict(inst="vln2", lvl=-27, pan=0.1, send=0.4),
    "horn": dict(inst="hn", lvl=-31, pan=0.2, send=0.55),
    "harp": dict(inst="harp", lvl=-28, pan=0.5, send=0.5),
}

CUES = {
    "A1": ("a1_main_title", "A1-main-title", "A1-main-title-v2", A1_MIX, dict(dialogue=True)),
    "A4": ("a4_emotional", "A4-emotional", "A4-emotional-v2", A4_MIX, {}),
    "A5": ("a5_global_japan", "A5-global-japan-urashima", "A5-global-japan-urashima-v2", A5_MIX, {}),
    "A1FULL": ("a1_full_90", "A1-main-title-full-90", "A1-main-title-full-90-v2", A1_FULL_MIX, dict(dialogue=True)),
    "JAX": ("m_jax", "M1-jax-motif", "M1-jax-motif-v2", JAX_MIX, dict(rt60=1.8)),
    "MIRA": ("m_mira", "M2-mira-motif", "M2-mira-motif-v2", MIRA_MIX, dict(rt60=2.4)),
    "PIP": ("m_pip", "M3-pip-motif", "M3-pip-motif-v2", PIP_MIX, dict(rt60=1.4)),
    "VOSS": ("m_voss", "M4-voss-motif", "M4-voss-motif-v2", VOSS_MIX, dict(rt60=2.8)),
}

# stings cut from the full-90 mix (bar = 2.0 s at 120 BPM; ritardando only after 84 s)
STINGS = {
    # 10 s title sting: the tag (bar 41 = 80 s: E-B-E-F#-G ... final E minor chord) to the ring-out
    "A1-title-sting-10s": [(80.0, 90.0)],
    # 5 s end card: last two beats of bar 42 (the D#-E leading note) + the final chord
    "A1-endcard-sting-5s": [(83.0, 88.0)],
}


def make_stings(raw):
    import numpy as np
    import sfzr
    x, sr = sfzr.sf.read(raw, dtype="float32", always_2d=True)
    res = {}
    for name, segs in STINGS.items():
        parts = [x[int(a * sr):int(b * sr)] for a, b in segs]
        y = np.concatenate(parts)
        f_in = int(0.012 * sr)
        y[:f_in] *= np.linspace(0, 1, f_in)[:, None]
        tmp = os.path.join(sulib.SCRATCH, name + "-cut.wav")
        sfzr.write_wav(tmp, y)
        dur = len(y) / sr
        # same bus as the cues, with a longer musical fade on the last 1.5 s
        res[name] = v2mix.finish(tmp, os.path.join(v2mix.V2_DIR, name + ".mp3"), dur)
    return res


def run(keys):
    report = {}
    for k in keys:
        mod, mid, out, mix, opts = CUES[k]
        # regenerate the MIDI without the v1 FluidR3 render (import builds the Cue)
        m = __import__(mod)
        m.c.write_midi()
        outs, raw = v2mix.render_cue(os.path.join(MID, mid + ".mid"), mix, out, **opts)
        for kind, (path, st) in outs.items():
            report[os.path.basename(path)] = st
        if k == "A1FULL":
            for name, (path, st) in make_stings(raw).items():
                report[os.path.basename(path)] = st
    return report


if __name__ == "__main__":
    keys = sys.argv[1:] or list(CUES)
    print(json.dumps(run(keys), indent=1))
