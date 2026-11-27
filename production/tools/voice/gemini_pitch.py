"""Simple autocorrelation pitch + RMS stats for WAV files (consistency proxy). Usage: python gemini_pitch.py a.wav b.wav"""
import sys, numpy as np, soundfile as sf
for f in sys.argv[1:]:
    x, sr = sf.read(f, dtype="float32"); x = x if x.ndim == 1 else x.mean(1)
    n = int(.04*sr); h = int(.02*sr); lo, hi = int(sr/300), int(sr/70); f0 = []; rms = []
    for i in range(0, len(x)-n, h):
        fr = x[i:i+n]; r = np.sqrt((fr**2).mean())
        if r < 0.02: continue
        fr = fr - fr.mean(); ac = np.correlate(fr, fr, "full")[n-1:]
        if ac[0] <= 0: continue
        k = lo + np.argmax(ac[lo:hi])
        if ac[k]/ac[0] > .5: f0.append(sr/k); rms.append(r)
    f0 = np.array(f0)
    print(f"{f.split('/')[-1]}: dur={len(x)/sr:.2f}s voiced_frames={len(f0)} f0 median={np.median(f0):.1f}Hz mean={f0.mean():.1f} p10={np.percentile(f0,10):.1f} p90={np.percentile(f0,90):.1f} rms_mean={np.mean(rms):.3f}")
