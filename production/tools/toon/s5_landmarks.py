#!/usr/bin/env python3
"""Automatic face landmarks for drawn character pictures (MediaPipe Face Landmarker, Apache-2.0,
CPU). usage: s5_landmarks.py MODEL.task OUT.json IMG [IMG ...]
Writes per picture: mouth (corners, top, bottom, centre, width), chin, eye centres and boxes,
brow boxes, face oval polygon — all in picture pixels. Prints which pictures had no face.
"""
import sys, json, numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
model, out, imgs = sys.argv[1], sys.argv[2], sys.argv[3:]
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), num_faces=1, min_face_detection_confidence=0.2))
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
        136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
EYE_L = [33, 160, 158, 133, 153, 144]; EYE_R = [362, 385, 387, 263, 373, 380]
BROW_L = [70, 63, 105, 66, 107, 46, 53, 52, 65, 55]; BROW_R = [336, 296, 334, 293, 300, 285, 295, 282, 283, 276]
res = {}
for p in imgs:
    im = cv2.imread(p); h, w = im.shape[:2]
    # detect on a padded copy with neutral background so the green does not confuse it
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
    if r.face_landmarks:
        L = np.array([[q.x * w, q.y * h] for q in r.face_landmarks[0]])
    else:
        # small faces (knee-up, full body): crop the top of the figure, enlarge, detect, map back
        f = im.astype(np.float32); a = (f[..., 1] - np.maximum(f[..., 0], f[..., 2])) < 50
        ys, xs = np.nonzero(a); L = None
        if len(ys):
            y0, y1 = ys.min(), ys.max(); hh = y1 - y0
            for frac in (0.32, 0.22, 0.45, 0.15):
                cy1 = int(y0 + hh * frac); cols = np.nonzero(a[y0:cy1].any(0))[0]
                if not len(cols): continue
                x0, x1 = max(0, cols.min() - 20), min(w, cols.max() + 20); yy0 = max(0, y0 - 20)
                crop = im[yy0:cy1, x0:x1]; k = min(4.0, 700 / max(1, crop.shape[0]))
                big = np.ascontiguousarray(cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC))
                rr = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(big, cv2.COLOR_BGR2RGB)))
                if rr.face_landmarks:
                    bh, bw = big.shape[:2]
                    L = np.array([[q.x * bw / k + x0, q.y * bh / k + yy0] for q in rr.face_landmarks[0]]); break
        if L is None:
            print("no face:", p); continue
    pt = lambda i: [round(float(L[i][0]), 1), round(float(L[i][1]), 1)]
    box = lambda ids: [round(float(v), 1) for v in (L[ids, 0].min(), L[ids, 1].min(), L[ids, 0].max(), L[ids, 1].max())]
    res[p.split("/")[-1].rsplit(".", 1)[0]] = {
        "mouth_l": pt(61), "mouth_r": pt(291), "lip_top": pt(0), "lip_bot": pt(17), "chin": pt(152), "nose": pt(1),
        "mouth_c": [round(float((L[61][0] + L[291][0]) / 2), 1), round(float((L[0][1] + L[17][1]) / 2), 1)],
        "mouth_w": round(float(np.linalg.norm(L[61] - L[291])), 1), "lips_box": box(LIPS),
        "eye_l": box(EYE_L), "eye_r": box(EYE_R), "brow_l": box(BROW_L), "brow_r": box(BROW_R),
        "oval": [pt(i) for i in OVAL]}
json.dump(res, open(out, "w"), indent=1)
print(len(res), "faces of", len(imgs))
