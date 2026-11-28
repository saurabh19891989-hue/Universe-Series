#!/usr/bin/env python3
"""Make ONE picture with the Antigravity CLI (agy), master pictures as references.
usage: agy_pic.py OUTDIR NAME "BRIEF" REF1 [REF2 ...]
Runs agy headless (--sandbox, accept-edits, no shell), copies only the picture it names to
OUTDIR/NAME.<ext>, logs the stream to OUTDIR/NAME.jsonl. Prints one JSON line.
(Same approach as production/tools/anim/agy_image.py; separate copy for the toon test.)
"""
import json, os, re, shutil, subprocess, sys, time
outdir, name, brief, refs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
os.makedirs(outdir, exist_ok=True)
local = []
for i, r in enumerate(refs):
    dst = os.path.join(outdir, f"{name}_ref{i+1}{os.path.splitext(r)[1]}")
    shutil.copy(r, dst); local.append(dst)
ref_txt = "\n".join(f"- Reference image {i+1}: `{p}`" for i, p in enumerate(local))
prompt = ("Generate EXACTLY ONE image with your image generation tool (call it exactly once, pass the "
          "reference image paths below as ImagePaths), aspect ratio 16:9, then reply with the saved file "
          "path and nothing else. Do not run any shell commands and do not write any code.\n\n"
          f"{ref_txt}\n\nImage brief:\n{brief}\n")
t0 = time.time(); log = os.path.join(outdir, f"{name}.jsonl")
with open(log, "w") as f:
    p = subprocess.run(["agy", "-p", prompt, "--sandbox", "--mode", "accept-edits",
                        "--output-format", "stream-json", "--print-timeout", "280s"],
                       cwd=outdir, stdout=f, stderr=subprocess.STDOUT, timeout=330)
txt = open(log).read()
paths = re.findall(r"(/root/\.gemini/antigravity-cli/brain/[0-9a-f-]+/[A-Za-z0-9_.-]+\.(?:png|jpg|jpeg|webp))", txt)
paths = [q for q in dict.fromkeys(paths) if os.path.isfile(q) and "_ref" not in os.path.basename(q)]
if not paths:
    lim = re.findall(r"(?i)[^\"]{0,80}(?:quota|rate limit|usage limit|resource.exhausted)[^\"]{0,120}", txt)
    print(json.dumps({"name": name, "ok": False, "secs": round(time.time() - t0), "rc": p.returncode, "limit": lim[:2]}))
    sys.exit(1)
src = paths[-1]; dst = os.path.join(outdir, name + os.path.splitext(src)[1])
shutil.copy(src, dst)
print(json.dumps({"name": name, "ok": True, "file": dst, "secs": round(time.time() - t0)}))
