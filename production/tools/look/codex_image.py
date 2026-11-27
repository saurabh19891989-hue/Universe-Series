#!/usr/bin/env python3
"""Run ONE image job through the OpenAI Codex CLI (ChatGPT-subscription login, no API key)
and log it to samples/look-codex/usage-log.json.

Usage:
  codex_image.py JOB NAME "image prompt" [-i ref1.png -i ref2.png] [--ref-note "Image 1 is ..."]
                 [--no-style] [--purpose "..."]

- Works in SCRATCH/cx/JOB/ (never in the repo). Reference images are copied there first.
- The style line is appended to every prompt unless --no-style.
- After the run the full-size original is taken from ~/.codex/generated_images/<session>/ (newest png)
  and saved as JOB_DIR/NAME.png.
- Reads the rate-limit snapshot Codex writes to its rollout log (~/.codex/sessions/...) - read-only,
  no auth data is touched or printed.
- Exit 3 = a usage/rate/quota limit message was seen: the caller must stop.
Never sets OPENAI_API_KEY; strips it from the environment if present.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

SCRATCH = Path(os.environ.get("CX_SCRATCH",
    "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/cx"))
LOG = Path(__file__).resolve().parents[3] / "samples/look-codex/usage-log.json"
CODEX_HOME = Path.home() / ".codex"

STYLE = ("Photorealistic cinematic film still, 35mm, shallow depth of field, practical lighting, "
         "natural skin texture, muted teal-and-amber grade, worn practical costumes, no logos, "
         "no readable text, looks like a frame from a live-action science fiction film, "
         "not an illustration, not CGI.")

LIMIT_RE = re.compile(r"usage limit|rate limit|rate_limit|quota|too many requests|429|"
                      r"limit reached|exceeded", re.I)


def rate_limits(session_id):
    files = glob.glob(str(CODEX_HOME / "sessions/**" / f"rollout-*{session_id}.jsonl"), recursive=True)
    snap = None
    for f in files:
        for line in open(f, errors="replace"):
            if '"rate_limits"' in line:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                rl = d.get("payload", {}).get("rate_limits") or d.get("rate_limits")
                if rl:
                    snap = rl
    return snap


def append_log(entry):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(LOG.read_text()) if LOG.exists() else []
    data.append(entry)
    LOG.write_text(json.dumps(data, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job"); ap.add_argument("name"); ap.add_argument("prompt")
    ap.add_argument("-i", dest="refs", action="append", default=[])
    ap.add_argument("--ref-note", default="")
    ap.add_argument("--no-style", action="store_true")
    ap.add_argument("--purpose", default="")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()

    d = SCRATCH / a.job
    d.mkdir(parents=True, exist_ok=True)
    refs = []
    for k, r in enumerate(a.refs, 1):
        dst = d / f"ref{k}{Path(r).suffix}"
        shutil.copy(r, dst)
        refs.append(dst.name)

    prompt = a.prompt if a.no_style else f"{STYLE} {a.prompt}"
    instr = ("Use your built-in image generation tool to generate exactly ONE image, landscape 16:9, "
             f"and save it in the current directory as {a.name}.png. Do not write any code, do not use "
             "Python or any drawing library, do not use the fallback CLI/API mode, do not read or write "
             "anything outside the current directory except your own generated_images folder, and do not "
             "generate more than one image. ")
    if refs:
        instr += (f"{len(refs)} reference image(s) are attached ({', '.join(refs)}). "
                  f"{a.ref_note} ")
    instr += f"Image prompt: {prompt} After saving, reply with the file path and nothing else."

    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write"]
    for r in refs:
        cmd += ["-i", r]
    # -i takes several values and would swallow a positional prompt, so the
    # instruction is passed on stdin instead.
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=d, env=env, input=instr.encode(),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=a.timeout)
        out, rc = p.stdout.decode(errors="replace"), p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or b"").decode(errors="replace") + "\n[TIMEOUT]", -9
    secs = round(time.time() - t0, 1)
    (d / f"{a.name}.run.log").write_text(out)

    m = re.search(r"session id:\s*(\S+)", out)
    sid = m.group(1) if m else None
    tk = re.findall(r"tokens used\s*\n\s*([\d,]+)", out)
    tokens = int(tk[-1].replace(",", "")) if tk else None

    # newest original from generated_images for this session
    final = d / f"{a.name}.png"
    src = None
    if sid:
        pngs = sorted(glob.glob(str(CODEX_HOME / "generated_images" / sid / "*.png")), key=os.path.getmtime)
        if pngs:
            src = pngs[-1]
    n_gen = len(glob.glob(str(CODEX_HOME / "generated_images" / sid / "*.png"))) if sid else 0
    if src:
        shutil.copy(src, final)
    ok = final.exists()

    # limit detection: only look at error-ish lines, not the skill text Codex echoes
    err_lines = [l for l in out.splitlines() if re.search(r"^(ERROR|error|stream error)|\bError\b", l)]
    limit_hit = any(LIMIT_RE.search(l) for l in err_lines)
    rl = rate_limits(sid) if sid else None
    entry = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "job": a.job, "name": a.name,
             "purpose": a.purpose, "refs": [Path(r).name for r in a.refs], "seconds": secs,
             "tokens_used": tokens, "success": ok and not limit_hit, "images_generated": n_gen,
             "returncode": rc, "session": sid,
             "rate_limits": rl, "errors": err_lines[-5:] if err_lines else []}
    append_log(entry)
    print(json.dumps({k: entry[k] for k in ("name", "seconds", "tokens_used", "success", "images_generated", "errors")}))
    if rl:
        print("rate_limits:", json.dumps({k: rl.get(k) for k in ("primary", "secondary")}))
    if limit_hit:
        print("LIMIT MESSAGE:", "\n".join(err_lines[-5:]))
        sys.exit(3)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
