#!/usr/bin/env python3
"""Gemini (Nano Banana) image generation for the SECRET UNIVERSE look test.

Uses the Gemini Interactions API (POST /v1beta/interactions, Api-Revision 2026-05-20)
as documented at https://aistudio.google.com/docs/image-generation (Nov 2026).

No secrets here: the request carries a dummy `x-goog-api-key: placeholder` header and
the session's network proxy substitutes the real key. Never put a real key in this file.

Every successful call is appended to samples/look-gemini/spend-log.json, and the
script refuses to run past the agreed caps (45 images total, 8 on the pro model).

Usage:
  gemini_image.py --out path.jpg --purpose "..." --prompt "..." \
      [--model gemini-3.1-flash-image] [--ref img1.jpg --ref img2.jpg] \
      [--aspect 16:9] [--size 2K] [--prev INTERACTION_ID]
"""
import argparse, base64, io, json, os, sys, time
import requests
from PIL import Image

API = "https://generativelanguage.googleapis.com/v1beta/interactions"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTDIR = os.path.join(REPO, "samples", "look-gemini")
LOG = os.path.join(OUTDIR, "spend-log.json")
CAP_TOTAL, CAP_PRO = 45, 8

# USD per output image, from https://ai.google.dev/gemini-api/docs/pricing (read 2026-11-27)
PRICE = {
    "gemini-3.1-flash-image": {"512": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151},
    "gemini-3-pro-image": {"1K": 0.134, "2K": 0.134, "4K": 0.24},
    "gemini-nano-banana-2.1": {"1K": 0.0336, "2K": 0.0504, "4K": 0.113},
    "gemini-3.1-flash-lite-image": {"1K": 0.0336},
}
# input images: flash $0.50/M tokens, pro $2.00/M; ~560 tokens per input image (pro doc)
IN_PER_IMG = {"gemini-3-pro-image": 0.0011}


def load_log():
    if os.path.exists(LOG):
        return json.load(open(LOG))
    return {"caps": {"total_images": CAP_TOTAL, "pro_images": CAP_PRO},
            "pricing_source": "https://ai.google.dev/gemini-api/docs/pricing", "entries": []}


def totals(log):
    t = sum(e["count"] for e in log["entries"])
    p = sum(e["count"] for e in log["entries"] if "pro" in e["model"])
    c = sum(e["est_cost_usd"] for e in log["entries"])
    return t, p, c


def img_part(path, max_side=1536):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA"); bg.paste(im, mask=im.split()[3]); im = bg
    im = im.convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    return {"type": "image", "mime_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemini-3.1-flash-image")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--size", default="2K")
    ap.add_argument("--out", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--prev", default=None, help="previous_interaction_id for multi-turn edit")
    ap.add_argument("--png", action="store_true", help="keep PNG output")
    a = ap.parse_args()

    log = load_log()
    t, p, c = totals(log)
    if t + 1 > CAP_TOTAL or ("pro" in a.model and p + 1 > CAP_PRO):
        sys.exit(f"CAP REACHED: total={t} pro={p}; refusing to call")

    inp = [{"type": "text", "text": a.prompt}] + [img_part(r) for r in a.ref]
    body = {"model": a.model, "input": inp,
            "response_format": {"type": "image", "aspect_ratio": a.aspect, "image_size": a.size}}
    if a.prev:
        body["previous_interaction_id"] = a.prev
    hdr = {"x-goog-api-key": "placeholder", "Content-Type": "application/json",
           "Api-Revision": "2026-05-20"}
    t0 = time.time()
    r = requests.post(API, headers=hdr, json=body, timeout=300)
    dt = time.time() - t0
    if r.status_code != 200:
        print("HTTP", r.status_code, r.text[:2000]); sys.exit(1)
    d = r.json()

    imgs, texts = [], []
    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "image" and isinstance(o.get("data"), str) and len(o["data"]) > 1000:
                imgs.append(o["data"])
            elif o.get("type") == "text" and isinstance(o.get("text"), str):
                texts.append(o["text"])
            for k, v in o.items():
                if k != "data":
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for step in d.get("steps", []):
        if step.get("type") == "model_output":
            walk(step)
    if not imgs:
        walk(d.get("outputs", d))
    usage = d.get("usage", d.get("usage_metadata"))
    meta = {k: v for k, v in d.items() if k not in ("steps", "outputs", "input")}

    n = 1 if imgs else 0  # bill one image (the final output) per call
    price = PRICE.get(a.model, {}).get(a.size, 0.15) * n + IN_PER_IMG.get(a.model, 0.0003) * len(a.ref)
    log["entries"].append({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "model": a.model,
                           "purpose": a.purpose, "count": n, "size": a.size, "aspect": a.aspect,
                           "ref_images": len(a.ref), "out": os.path.relpath(a.out, REPO),
                           "interaction_id": d.get("id"), "seconds": round(dt, 1),
                           "est_cost_usd": round(price, 4), "usage": usage})
    t2, p2, c2 = totals(log)
    log["totals"] = {"images": t2, "pro_images": p2, "est_cost_usd": round(c2, 3)}
    json.dump(log, open(LOG, "w"), indent=1)

    if not imgs:
        print("NO IMAGE returned. meta:", json.dumps(meta)[:1500], "text:", texts); sys.exit(2)
    raw = base64.b64decode(imgs[-1])
    im = Image.open(io.BytesIO(raw))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if a.png:
        im.save(a.out)
    else:
        im.convert("RGB").save(a.out, "JPEG", quality=90)
    print(json.dumps({"out": a.out, "size": im.size, "images_in_response": len(imgs),
                      "id": d.get("id"), "sec": round(dt, 1), "text": " ".join(texts)[:300],
                      "usage": usage, "running_total": log["totals"]}))


if __name__ == "__main__":
    main()
