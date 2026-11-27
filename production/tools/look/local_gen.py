#!/usr/bin/env python3
"""Route 2: local CPU generation. DreamShaper 8 (SD1.5 fine-tune, CreativeML OpenRAIL-M)
+ LCM-LoRA (openrail++) for 4-6 step sampling, optional IP-Adapter Plus (Apache-2.0) for
character consistency from a reference image.

Env: HF_HOME must point at the scratchpad cache (models are never stored in the repo).

Usage:
  local_gen.py --out x.png --prompt "..." [--seed 1] [--steps 5] [--w 512 --h 768]
               [--ref ref.png --ref-scale 0.6 --face]
  local_gen.py --batch jobs.json      # list of {out,prompt,seed,ref,...}; loads the model once
"""
import argparse, json, os, time
import torch
from diffusers import StableDiffusionPipeline, LCMScheduler
from PIL import Image

NEG = os.environ.get("LOOK_NEG") or "blurry, deformed, extra fingers, bad hands, text, watermark, logo, signature, photo, 3d render"
STYLE = ("graphic novel realism illustration, bold clean ink linework, cel shading, dramatic cinematic "
         "orange rim light, teal fill light, limited palette of deep space navy, burnt orange, teal and cream")

_pipe = {"p": None, "ip": None}


def load(ip=None):
    if _pipe["p"] is None:
        torch.set_num_threads(4)
        p = StableDiffusionPipeline.from_pretrained(os.environ.get("LOOK_MODEL", "Lykon/dreamshaper-8"), variant="fp16",
                                                    torch_dtype=torch.float32, safety_checker=None)
        p.scheduler = LCMScheduler.from_config(p.scheduler.config)
        p.load_lora_weights("latent-consistency/lcm-lora-sdv1-5", adapter_name="lcm")
        p.fuse_lora()
        p.set_progress_bar_config(disable=True)
        _pipe["p"] = p
    p = _pipe["p"]
    if ip and _pipe["ip"] != ip:
        p.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name=ip,
                          image_encoder_folder="models/image_encoder")
        _pipe["ip"] = ip
    return p


def gen(out, prompt, seed=1, steps=5, w=512, h=768, cfg=1.5, ref=None, ref_scale=0.6, face=False,
        style=True):
    ip = None
    if ref:
        ip = "ip-adapter-plus-face_sd15.safetensors" if face else "ip-adapter-plus_sd15.safetensors"
    p = load(ip)
    kw = {}
    if ref:
        p.set_ip_adapter_scale(ref_scale)
        kw["ip_adapter_image"] = Image.open(ref).convert("RGB")
    elif _pipe["ip"]:
        p.set_ip_adapter_scale(0.0)
        kw["ip_adapter_image"] = Image.new("RGB", (224, 224))
    style = style and not os.environ.get("LOOK_NOSTYLE")
    full = f"{prompt}, {STYLE}" if style else prompt
    t = time.time()
    img = p(full, negative_prompt=NEG, num_inference_steps=steps, guidance_scale=cfg, width=w, height=h,
            generator=torch.Generator().manual_seed(seed), **kw).images[0]
    dt = time.time() - t
    img.save(out)
    print(json.dumps({"out": out, "secs": round(dt, 1), "w": w, "h": h, "steps": steps}), flush=True)
    return dt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out"); ap.add_argument("--prompt"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=5); ap.add_argument("--w", type=int, default=512)
    ap.add_argument("--h", type=int, default=768); ap.add_argument("--cfg", type=float, default=1.5)
    ap.add_argument("--ref"); ap.add_argument("--ref-scale", type=float, default=0.6)
    ap.add_argument("--face", action="store_true"); ap.add_argument("--batch")
    a = ap.parse_args()
    if a.batch:
        for j in json.load(open(a.batch)):
            gen(**j)
    else:
        gen(a.out, a.prompt, a.seed, a.steps, a.w, a.h, a.cfg, a.ref, a.ref_scale, a.face)
