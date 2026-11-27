#!/usr/bin/env python3
"""Route 1: free hosted image generation clients (no paid keys).

Backends:
  pollinations  - https://image.pollinations.ai/prompt/... (legacy anonymous endpoint)
  horde         - AI Horde (https://aihorde.net), anonymous key 0000000000, crowdsourced GPUs

Usage:
  hosted_gen.py pollinations OUT.jpg "prompt" [--seed N] [--w 768 --h 768]
  hosted_gen.py horde OUT.webp "prompt" [--model "Flux.1-Schnell fp8 (Compact)"] [--seed N] [--source-image ref.png --strength 0.5]
"""
import argparse, base64, json, sys, time, urllib.parse
import requests

UA = {"User-Agent": "look-test/0.1"}


def pollinations(prompt, out, seed=42, w=768, h=768, model=None):
    q = {"width": w, "height": h, "seed": seed, "nologo": "true"}
    if model:
        q["model"] = model
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?" + urllib.parse.urlencode(q)
    t = time.time()
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    open(out, "wb").write(r.content)
    return time.time() - t


def horde(prompt, out, model="Flux.1-Schnell fp8 (Compact)", seed=None, w=768, h=768, steps=4,
          cfg=1.0, sampler="k_euler", source_image=None, strength=0.55, timeout=900):
    hdr = {"apikey": "0000000000", "Client-Agent": "look-test:0.1:anon", **UA}
    params = {"width": w, "height": h, "steps": steps, "cfg_scale": cfg, "sampler_name": sampler, "n": 1}
    if seed is not None:
        params["seed"] = str(seed)
    body = {"prompt": prompt, "params": params, "models": [model], "r2": True, "nsfw": False,
            "censor_nsfw": True}
    if source_image:
        body["source_image"] = base64.b64encode(open(source_image, "rb").read()).decode()
        body["source_processing"] = "img2img"
        params["denoising_strength"] = strength
    t = time.time()
    r = requests.post("https://aihorde.net/api/v2/generate/async", json=body, headers=hdr, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(r.text)
    jid = r.json()["id"]
    while time.time() - t < timeout:
        time.sleep(6)
        s = requests.get(f"https://aihorde.net/api/v2/generate/check/{jid}", headers=UA, timeout=30).json()
        if s.get("done"):
            break
        if s.get("faulted"):
            raise RuntimeError("faulted")
    st = requests.get(f"https://aihorde.net/api/v2/generate/status/{jid}", headers=UA, timeout=60).json()
    g = st["generations"][0]
    img = g["img"]
    data = requests.get(img, timeout=120).content if img.startswith("http") else base64.b64decode(img)
    open(out, "wb").write(data)
    return time.time() - t, g.get("seed"), g.get("worker_name"), g.get("model")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("backend"); ap.add_argument("out"); ap.add_argument("prompt")
    ap.add_argument("--seed", type=int, default=42); ap.add_argument("--w", type=int, default=768)
    ap.add_argument("--h", type=int, default=768); ap.add_argument("--model")
    ap.add_argument("--steps", type=int, default=4); ap.add_argument("--cfg", type=float, default=1.0)
    ap.add_argument("--sampler", default="k_euler")
    ap.add_argument("--source-image"); ap.add_argument("--strength", type=float, default=0.55)
    a = ap.parse_args()
    if a.backend == "pollinations":
        print(json.dumps({"secs": round(pollinations(a.prompt, a.out, a.seed, a.w, a.h, a.model), 1)}))
    else:
        res = horde(a.prompt, a.out, a.model or "Flux.1-Schnell fp8 (Compact)", a.seed, a.w, a.h, a.steps,
                    a.cfg, a.sampler, a.source_image, a.strength)
        print(json.dumps({"secs": round(res[0], 1), "seed": res[1], "worker": res[2], "model": res[3]}))
