#!/usr/bin/env python3
"""Submit many AI Horde jobs at once (anonymous key), poll them together, download results.

Usage: horde_batch.py jobs.json OUTDIR
jobs.json: [{"name": "jax", "prompt": "...", "w": 768, "h": 1024, "seed": 7,
             "model": "Flux.1-Schnell fp8 (Compact)", "steps": 4, "cfg": 1}, ...]
Writes OUTDIR/<name>.webp and appends one JSON line per finished job to OUTDIR/log.jsonl.
"""
import json, os, sys, time
import requests

API = "https://aihorde.net/api/v2"
HDR = {"apikey": "0000000000", "Client-Agent": "look-test:0.2:anon", "User-Agent": "look-test/0.2"}


def submit(j):
    params = {"width": j.get("w", 768), "height": j.get("h", 1024), "steps": j.get("steps", 4),
              "cfg_scale": j.get("cfg", 1.0), "sampler_name": j.get("sampler", "k_euler"), "n": 1}
    if "seed" in j:
        params["seed"] = str(j["seed"])
    body = {"prompt": j["prompt"], "params": params, "models": [j.get("model", "Flux.1-Schnell fp8 (Compact)")],
            "r2": True, "nsfw": False, "censor_nsfw": True}
    for attempt in range(6):
        r = requests.post(f"{API}/generate/async", json=body, headers=HDR, timeout=60)
        if r.status_code < 300:
            return r.json()["id"]
        print("submit retry", j["name"], r.status_code, r.text[:200], flush=True)
        time.sleep(3 + attempt * 3)
    raise RuntimeError(r.text)


def main():
    jobs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    pending = {}
    t0 = time.time()
    resume = dict(l.split() for l in open(sys.argv[3])) if len(sys.argv) > 3 else {}
    for j in jobs:
        if os.path.exists(f"{out}/{j['name']}.webp"):
            continue
        if j["name"] in resume:           # re-attach to a job already queued on the server
            pending[resume[j["name"]]] = (j, time.time()); continue
        pending[submit(j)] = (j, time.time())
        print("submitted", j["name"], list(pending)[-1], flush=True)
        time.sleep(1.2)
    while pending:
        time.sleep(15)
        for jid, (j, ts) in list(pending.items()):
            try:
                s = requests.get(f"{API}/generate/check/{jid}", headers=HDR, timeout=30).json()
            except Exception as e:
                print("check err", e, flush=True); continue
            if s.get("faulted"):  # is_possible=False is often transient (a worker blinked offline)
                print("FAULT", j["name"], s, flush=True); pending.pop(jid); continue
            if not s.get("done"):
                if int(time.time()) % 300 < 16:
                    print("wait", j["name"], {k: s.get(k) for k in ("waiting", "processing", "restarted", "queue_position", "wait_time")}, flush=True)
                continue
            st = requests.get(f"{API}/generate/status/{jid}", headers=HDR, timeout=60).json()
            g = st["generations"][0]
            data = requests.get(g["img"], timeout=120).content
            open(f"{out}/{j['name']}.webp", "wb").write(data)
            rec = {"name": j["name"], "secs": round(time.time() - ts), "seed": g.get("seed"),
                   "worker": g.get("worker_name"), "model": g.get("model"), "censored": g.get("censored")}
            open(f"{out}/log.jsonl", "a").write(json.dumps(rec) + "\n")
            print("done", rec, flush=True)
            pending.pop(jid)
    print(f"ALL DONE in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
