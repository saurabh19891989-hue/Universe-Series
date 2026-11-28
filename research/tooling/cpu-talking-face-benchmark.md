# CPU talking-face benchmark (28 Nov)

Question: on this box (4 cores, 15 GB, no GPU), limited to 2 threads, can a free model make a photoreal Jax still talk in sync with our own voice stem, and how slow?

Input: `assets/characters/jax/master.jpg` (1664x936, three-quarter smirk) + `E01_S30_L021_JAX.wav` (4.267 s, "What we got for it was a parcel we couldn't deliver...").
Setup: python 3.11 venv, torch 2.2.2 CPU, `OMP_NUM_THREADS=2`, `torch.set_num_threads(2)`, fp32, batch 4. Another agent was rendering video at the same time, so timings are pessimistic by an unknown amount.

## Result table

| Candidate | Licence (code / weights) | Ran? | Compute s per s of video (2 threads) | Peak RAM | Face resolution | What the frames look like |
|---|---|---|---|---|---|---|
| 1. MuseTalk v1.5 | Code MIT (https://github.com/TMElyralab/MuseTalk/blob/main/LICENSE). Weights stated MIT "for any purpose, even commercially" (https://huggingface.co/TMElyralab/MuseTalk), BUT their NOTICE says "trained on the HDTF and private dataset. Please communicate with the HDTF owner about commercialization issues". Sub-models: sd-vae-ft-mse MIT; whisper-tiny Apache-2.0 (HF page; MIT in the NOTICE); DWPose dw-ll_ucoco_384 Apache-2.0 (https://huggingface.co/yzd-v/DWPose); BiSeNet face-parse 79999_iter.pth from github.com/zllrunning/face-parsing.PyTorch (code MIT; weights trained on CelebAMask-HQ, which I recall as research/non-commercial - NOT verified); S3FD detector s3fd.pth from adrianbulat.com (face-alignment, BSD-3 code; trained on WIDER FACE - weight terms NOT verified). | YES, runs on CPU | **144 s per s** end to end (616 s wall for 4.27 s). Split: inference loop 545 s = 128 s/s (5.1 s per frame); blending/paste-back 38 s; one-time face preprocessing 6 s per still; model load ~25 s | 7.6 GB | Network works on a 256x256 face crop; output video 1664x936, the repainted mouth/jaw patch is about 300 px wide on screen | Mouth region repainted, soft and plasticky; moustache and stubble around mouth/chin erased into smooth skin; lips small movements only; see below |
| 2. LatentSync 1.5/1.6 (ByteDance) | Code Apache-2.0; weights on https://huggingface.co/ByteDance/LatentSync are OpenRAIL++ (commercial use allowed with use-restrictions; read before use) | NOT RUN - ran out of time box; it is an SD1.5-class diffusion UNet over 16-frame chunks, so expect clearly slower than MuseTalk on CPU (single-step MuseTalk is the cheap case). Not measured. | not measured | not measured | 256x256 face crop | not seen |
| 3. SadTalker | Code Apache-2.0 | NOT RUN, not checked weight by weight. It also makes a whole-head moving face from one still (3DMM), so it would not keep our framing. | - | - | - | - |

Hosts: all reachable (github.com via git clone, raw.githubusercontent.com, huggingface.co, download.pytorch.org, pypi.org, adrianbulat.com, drive.google.com via gdown). Nothing blocked.

Licence verdict for MuseTalk: **not cleanly usable commercially until the HDTF training-data question and the CelebAMask-HQ / WIDER FACE questions on the two helper weights are settled.** The authors say the model is free for commercial use, so it is a showrunner decision, not a hard stop. I did not read the HDTF terms live.

## How it was made to run (honest list of hacks)
- mmpose 1.1.0 needs mmdet for the CSPNeXt backbone, and mmdet imports compiled mmcv ops. I installed `mmcv-lite` and put a stub `mmcv/_ext.py` in the venv so the import passes. The ops are never called by DWPose pose inference. Works; but it is a hack in the venv only, not in the repo.
- The still image was given as a 1-frame video, so DWPose + S3FD ran once, not on 107 identical frames (first attempt on 107 frames was ~7-8 s per frame of preprocessing alone and was stopped).
- Paths and CPU: patched nothing in MuseTalk source; ran `scripts/inference.py` via a wrapper that sets 2 threads and records peak RSS (resource.getrusage).

## What the 6 frames show (looked at: `samples/motion/cpu-talk-test-sheet.jpg`, plus 340x230 mouth crops)
- Mouth moves: lips part and close, small amplitude, slight lopsided shapes. It is a mild mumble-level opening, not the broad vowel shapes of real speech.
- Identity: the eyes, hair, jacket and brow are the untouched source pixels, so it is still clearly Jax in the upper face. The lower face is not: the dark moustache and the stubble band round the mouth are smoothed out and the lip colour is pinkish-flat; a dark smudge appears at the right moustache end. Reads as a different, cleaner mouth pasted on a weathered face.
- Blur: lower half of the face is visibly softer than the rest; the paste-back boundary along the cheek/jaw is faintly visible. Teeth appear in one frame (t=3.00 s) as a white smear.
- Rest of the picture: everything else is frozen, as it is a still (no blinks, no head motion). It would need motion layered separately.
- Sync (checked only by numbers, cannot hear): mouth-region change per frame vs the 40 ms loudness envelope of the stem has correlation 0.29 (weak, lags -3..+3 frames give 0.13-0.31). Mouth shapes at quiet gaps (0.92 s, 2.45 s) look closed-ish and at loud syllables more open, but the effect is subtle. I would not call it lip-sync-accurate without a human watching it with sound.
- Audio track in the mp4 is our stem, muxed in by MuseTalk (aac).

## Arithmetic: 20 minutes of talking shots per episode (1200 s of video)
- MuseTalk at 2 threads, as measured: 144 s per s x 1200 = 172,800 s = **48 hours** per episode (inference alone 128 s/s = 42.7 h).
- If 4 threads gave a perfect 2x (not measured, and the other agent needs the cores): ~24 hours per episode.
- 10 episodes: ~20 days of the whole machine at 4 threads, ~40 days at 2.
- It also only fixes mouths on a still; talking shots in the episodes are mostly short lines (a few seconds) so real use would be maybe 3-5 minutes per episode: 3-5 min = 180-300 s video -> 7-12 h at 2 threads. Still too slow for "as many episodes as fast as possible", and quality (lost moustache, blur) is below the stills.

## Not checked
- LatentSync and SadTalker were not run or timed. No GPU run. 4-thread speed. float16/bfloat16 or quantised CPU speed-ups. Other faces/angles (this master is a hard three-quarter smirk; a frontal reference may look better). Audio sync by ear. Licence terms of HDTF, CelebAMask-HQ, WIDER FACE read live.
- Working files (venv, weights ~4.5 GB) are in `/tmp/claude-0/.../scratchpad/bench-talk/` outside the repo.
