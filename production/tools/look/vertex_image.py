#!/usr/bin/env python3
"""Vertex AI image generation helper for the SECRET UNIVERSE look tests.

No secrets here: the network proxy injects the credential for
aiplatform.googleapis.com. Never add an Authorization header.

Usage (as a module):
    from vertex_image import gen
    gen("jax_master", "prompt...", refs=[path], aspect="16:9", purpose="A1 Jax master")
"""
import base64, io, json, os, sys, threading, time, datetime
import requests
from PIL import Image

PROJECT = "project-6153920b-b099-4ae9-b90"
MODEL = "gemini-nano-banana-2.1"
URL = (f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/"
       f"publishers/google/models/{MODEL}:generateContent")
HEADERS = {"Content-Type": "application/json", "x-goog-user-project": PROJECT}

RAW = os.environ.get("VX_RAW", "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/vx/raw")
OUT = os.environ.get("VX_OUT", "/home/user/Universe-Series/samples/look-vertex")
LOG = os.path.join(OUT, "spend-log.json")
MAX_IMAGES = 70
COST = 0.05

STYLE = ("Photorealistic cinematic film still, 35mm, shallow depth of field, practical lighting, "
         "natural skin texture, muted teal-and-amber grade, worn practical costumes and sets, no logos, "
         "no readable text, looks like a frame from a live-action science fiction film, not an "
         "illustration, not CGI. ")

_lock = threading.Lock()
DEAD = threading.Event()  # set on 401/403


class TokenDead(Exception):
    pass


def _load_log():
    if os.path.exists(LOG):
        with open(LOG) as f:
            return json.load(f)
    return {"model": MODEL, "cost_per_image_usd": COST, "calls": []}


def _append(entry):
    with _lock:
        d = _load_log()
        d["calls"].append(entry)
        d["images_billed"] = sum(1 for c in d["calls"] if c.get("status") == 200)
        d["est_cost_usd"] = round(d["images_billed"] * COST, 2)
        with open(LOG, "w") as f:
            json.dump(d, f, indent=1)


def billed():
    with _lock:
        return sum(1 for c in _load_log()["calls"] if c.get("status") == 200)


def ref_part(path, width=1024):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=88)
    return {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}}


def save_jpg(png_path, jpg_path):
    im = Image.open(png_path).convert("RGB")
    q = 88
    while True:
        im.save(jpg_path, "JPEG", quality=q, optimize=True)
        if os.path.getsize(jpg_path) < 1.5e6 or q < 60:
            break
        q -= 6


def gen(name, prompt, refs=(), aspect="16:9", purpose="", style=True):
    if DEAD.is_set():
        raise TokenDead("token dead")
    if billed() >= MAX_IMAGES:
        raise RuntimeError("image cap reached")
    os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    parts = [ref_part(r) for r in refs] + [{"text": (STYLE if style else "") + prompt}]
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": aspect}}}
    for attempt in range(4):
        t0 = time.time()
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        try:
            r = requests.post(URL, headers=HEADERS, json=body, timeout=180)
            status = r.status_code
        except Exception as e:
            _append({"name": name, "purpose": purpose, "time": ts, "status": "error", "error": str(e)[:200]})
            time.sleep(5); continue
        entry = {"name": name, "purpose": purpose, "time": ts, "status": status,
                 "secs": round(time.time() - t0, 1), "aspect": aspect, "refs": [os.path.basename(x) for x in refs]}
        if status in (401, 403):
            entry["error"] = r.text[:300]; _append(entry); DEAD.set()
            raise TokenDead(f"{status}")
        if status == 429:
            entry["error"] = "rate limited"; _append(entry); time.sleep(20); continue
        if status != 200:
            entry["error"] = r.text[:300]; _append(entry); time.sleep(5); continue
        data = r.json()
        img = None; txt = []
        for c in data.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p and img is None:
                    img = base64.b64decode(p["inlineData"]["data"])
                elif "text" in p:
                    txt.append(p["text"])
        if img is None:
            entry["error"] = "no image: " + " ".join(txt)[:200]
            entry["finish"] = str([c.get("finishReason") for c in data.get("candidates", [])])
            _append(entry); return None
        png = os.path.join(RAW, name + ".png")
        with open(png, "wb") as f:
            f.write(img)
        save_jpg(png, os.path.join(OUT, name + ".jpg"))
        entry["size"] = list(Image.open(png).size)
        _append(entry)
        print(f"OK {name} {entry['secs']}s", flush=True)
        return png
    return None


def run_batch(jobs, workers=3):
    """jobs: list of dicts with gen() kwargs. Returns {name: png or None}."""
    from concurrent.futures import ThreadPoolExecutor
    res = {}
    def one(j):
        try:
            return j["name"], gen(**j)
        except TokenDead:
            return j["name"], "DEAD"
        except Exception as e:
            print("ERR", j["name"], e, flush=True); return j["name"], None
    with ThreadPoolExecutor(workers) as ex:
        for n, p in ex.map(one, jobs):
            res[n] = p
            print(n, "->", p, flush=True)
    return res


if __name__ == "__main__":
    print(gen(sys.argv[1], sys.argv[2], purpose="cli"))
