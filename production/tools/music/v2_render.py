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

CUES = {
    "A1": ("a1_main_title", "A1-main-title", "A1-main-title-v2", A1_MIX, dict(dialogue=True)),
    "A4": ("a4_emotional", "A4-emotional", "A4-emotional-v2", A4_MIX, {}),
    "A5": ("a5_global_japan", "A5-global-japan-urashima", "A5-global-japan-urashima-v2", A5_MIX, {}),
}


def run(keys):
    report = {}
    for k in keys:
        mod, mid, out, mix, opts = CUES[k]
        # regenerate the MIDI without the v1 FluidR3 render (import builds the Cue)
        m = __import__(mod)
        m.c.write_midi()
        outs, _ = v2mix.render_cue(os.path.join(MID, mid + ".mid"), mix, out, **opts)
        for kind, (path, st) in outs.items():
            report[os.path.basename(path)] = st
    return report


if __name__ == "__main__":
    keys = sys.argv[1:] or list(CUES)
    print(json.dumps(run(keys), indent=1))
