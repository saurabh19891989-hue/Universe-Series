#!/usr/bin/env bash
# Route C: how ACE-Step 1.5 (MIT) was made to run on this 4-core, no-GPU box (tested 2026-11-27).
# Everything lands in $SCR (scratchpad), never in the repo. ~6 GB weights, ~3 GB venv.
set -euo pipefail
SCR=${SCR:-/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/music/acestep}
mkdir -p "$SCR/src/ace" "$SCR/ckpt" "$SCR/out"
cd "$SCR"
# 1. source code: github.com was blocked from this sandbox, so files came via the jsDelivr mirror
#    of github.com/ace-step/ACE-Step-1.5 (main branch), listed by data.jsdelivr.com.
#    Any normal machine: download the repo zip from GitHub instead.
# 2. weights (DiT-only, no 5Hz LM): turbo DiT + VAE + Qwen3-Embedding-0.6B text encoder
pip install -q huggingface_hub
python3 -c "from huggingface_hub import snapshot_download as d; d('ACE-Step/Ace-Step1.5', local_dir='$SCR/ckpt', allow_patterns=['acestep-v15-turbo/*','vae/*','Qwen3-Embedding-0.6B/*','config.json','README.md'])"
ln -sfn "$SCR/ckpt" "$SCR/src/ace/checkpoints"
# 3. Python 3.12 venv (project needs <3.13) with CPU torch
pip install -q uv
export UV_CACHE_DIR=$SCR/uvcache UV_PYTHON_INSTALL_DIR=$SCR/uvpy
uv venv -q -p 3.12 venv
. venv/bin/activate
uv pip install -q torch==2.10.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cpu
uv pip install -q "transformers>=4.51.0,<4.58.0" diffusers safetensors scipy soundfile loguru einops \
  accelerate numba vector-quantize-pytorch toml "torchao>=0.16.0,<0.17.0" matplotlib modelscope
# 4. local patch: upstream loads in float32 on CPU (~12 GB RAM -> OOM-killed here). Use bf16:
F=src/ace/acestep/core/generation/handler/init_service_orchestrator.py
sed -i 's/torch.bfloat16 if resolved_device == "xpu" else torch.float32/torch.bfloat16 if resolved_device in ("xpu", "cpu") else torch.float32/' "$F"
# 5. generate (30 s took ~3 min 15 s wall: ~45 s diffusion + ~2 min 20 s VAE decode, 3 threads)
#    HF_HUB_OFFLINE=1 venv/bin/python /home/user/Universe-Series/production/tools/music/c_acestep_generate.py \
#        "$SCR/src/ace" "$SCR/out/C1-acestep.wav" 30
