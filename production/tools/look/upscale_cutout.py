#!/usr/bin/env python3
"""Route 2 finishing: CPU upscaling (Real-ESRGAN weights, BSD-3, loaded with spandrel, MIT)
and background removal (rembg, MIT; default u2net model, Apache-2.0).

Usage: upscale_cutout.py IN.png OUT_PREFIX [--model path.pth] [--tile 256] [--no-cut]
Writes OUT_PREFIX_x4.png (upscaled RGB) and OUT_PREFIX_cut.png (RGBA cut-out).
"""
import argparse, time
import numpy as np, torch
from PIL import Image


def upscale(img, model_path, tile=256, pad=12):
    from spandrel import ModelLoader
    torch.set_num_threads(4)
    m = ModelLoader().load_from_file(model_path).eval()
    sc = m.scale
    x = torch.from_numpy(np.asarray(img.convert("RGB"), np.float32) / 255).permute(2, 0, 1)[None]
    _, _, H, W = x.shape
    out = torch.zeros(1, 3, H * sc, W * sc)
    with torch.inference_mode():
        for y0 in range(0, H, tile):
            for x0 in range(0, W, tile):
                ya, xa = max(0, y0 - pad), max(0, x0 - pad)
                yb, xb = min(H, y0 + tile + pad), min(W, x0 + tile + pad)
                o = m.model(x[:, :, ya:yb, xa:xb])
                oy, ox = (y0 - ya) * sc, (x0 - xa) * sc
                th, tw = min(tile, H - y0) * sc, min(tile, W - x0) * sc
                out[:, :, y0 * sc:y0 * sc + th, x0 * sc:x0 * sc + tw] = o[:, :, oy:oy + th, ox:ox + tw]
    a = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(a)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("prefix")
    ap.add_argument("--model", required=True); ap.add_argument("--tile", type=int, default=256)
    ap.add_argument("--no-cut", action="store_true")
    a = ap.parse_args()
    t = time.time(); up = upscale(Image.open(a.inp), a.model, a.tile); t1 = time.time() - t
    up.save(a.prefix + "_x4.png")
    print(f"upscale {up.size} {t1:.1f}s", flush=True)
    if not a.no_cut:
        from rembg import remove, new_session
        t = time.time()
        cut = remove(up, session=new_session("isnet-general-use"))
        cut.save(a.prefix + "_cut.png"); print(f"rembg {time.time()-t:.1f}s")


def key_out_disc(rgba_path, out_path, hue=(9, 19), min_sat=170, min_val=200, min_frac=0.0003):
    """Remove large flat-colour regions (e.g. the halo disc FLUX likes to paint behind heads)
    that rembg keeps as 'subject'. Only connected regions bigger than min_frac of the image go."""
    import cv2
    im = np.asarray(Image.open(rgba_path).convert("RGBA")).copy()
    hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV)  # OpenCV hue 0..180
    m = ((hsv[..., 0] >= hue[0]) & (hsv[..., 0] <= hue[1]) & (hsv[..., 1] >= min_sat) &
         (hsv[..., 2] >= min_val) & (im[..., 3] > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    kill = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > min_frac * m.size:
            kill[lab == i] = 1
    kill = cv2.dilate(kill, np.ones((13, 13), np.uint8))
    a = im[..., 3].astype(np.float32) * (1 - kill)
    a = cv2.GaussianBlur(a, (0, 0), 1.2)
    im[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(im).save(out_path)
