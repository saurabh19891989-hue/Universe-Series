"""Route C test: ACE-Step 1.5 (MIT licence) text-to-music on CPU, DiT-only (no LM).

Env: SU_CAPTION, SU_BPM, SU_KEY, SU_THREADS override the prompt.
Usage: <venv>/bin/python c_acestep_generate.py <ace-step-src-dir> <out.wav> [seconds]
The source dir must contain checkpoints/ (acestep-v15-turbo, vae, Qwen3-Embedding-0.6B).
"""
import os
import sys
import time

src, out = sys.argv[1], sys.argv[2]
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 30
sys.path.insert(0, src)
import torch
torch.set_num_threads(int(os.environ.get("SU_THREADS", "3")))

from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

t0 = time.time()
dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=src, config_path="acestep-v15-turbo",
                                 device="cpu", offload_to_cpu=False)
print("init", ok, msg, f"{time.time() - t0:.0f}s", flush=True)
if not ok:
    sys.exit(1)

params = GenerationParams(
    task_type="text2music", thinking=False, instrumental=True, lyrics="[Instrumental]",
    caption=os.environ.get("SU_CAPTION") or ("cinematic orchestral main title, driving string ostinato, big brass melody, "
             "taiko drums, sitar colour, heroic and mysterious space adventure, instrumental"),
    bpm=int(os.environ.get("SU_BPM", "120")), keyscale=os.environ.get("SU_KEY", "D minor"), timesignature="4", duration=secs,
    inference_steps=8, guidance_scale=1.0, seed=7,
    use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
config = GenerationConfig(batch_size=1, audio_format="wav")
t1 = time.time()
res = generate_music(dit, None, params=params, config=config, save_dir=os.path.dirname(out))
print("generate", res.success, getattr(res, "status_message", ""), f"{time.time() - t1:.0f}s", flush=True)
for a in res.audios:
    print("audio", a.get("path"))
    if a.get("path"):
        os.replace(a["path"], out)
