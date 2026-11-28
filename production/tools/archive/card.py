# Chichikov's calling card on the bench, rendered in code (2400x1350 so a slow push stays sharp).
import numpy as np, cv2, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Universe-Series/production/tools/edit")
import overlays as OV
F = "/tmp/claude-0/-home-user-Universe-Series/3757f133-43aa-510b-bfaf-b45b089ed136/scratchpad/fonts/"
W, H = 2400, 1350
rng = np.random.default_rng(3)
# bench: dark varnished wood planks with grain
y = np.arange(H, dtype=np.float32)[:, None]; x = np.arange(W, dtype=np.float32)[None]
grain = np.sin(x / 9.0 + 6 * np.sin(y / 140.0) + cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 30) * 40) * 0.5 + 0.5
wood = np.float32([0.30, 0.17, 0.08])[None, None] * (0.75 + 0.35 * grain[..., None])
for k in range(1, 4):
    yy = int(H * k / 4); wood[yy - 3:yy + 3] *= 0.35
wood *= (0.55 + 0.6 * np.exp(-(((x - W * 0.55) / (W * 0.45)) ** 2 + ((y - H * 0.45) / (H * 0.6)) ** 2)))[..., None]
img = Image.fromarray((np.clip(wood, 0, 1) * 255).astype(np.uint8))
# card with soft shadow
cw, ch = 1300, 720
card = OV.enamel(ch, cw, 9, chips=0) * np.float32([1.04, 1.02, 0.96])
cimg = Image.fromarray((np.clip(card, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(cimg)
d.rectangle([28, 28, cw - 29, ch - 29], outline=(140, 100, 50), width=3)
d.text((cw // 2, ch * 0.42), "Pavel Ivanovich Chichikov", font=ImageFont.truetype(F + "PinyonScript-Regular.ttf", 112), fill=(34, 24, 18), anchor="mm")
d.text((cw // 2, ch * 0.66), "COLLEGIATE COUNCILLOR  ·  BUYER", font=ImageFont.truetype(F + "IMFellEnglish-Regular.ttf", 44), fill=(90, 66, 44), anchor="mm")
d.text((cw // 2, ch * 0.78), "Souls, registers & sundries", font=ImageFont.truetype(F + "IMFellEnglish-Italic.ttf", 38), fill=(110, 84, 58), anchor="mm")
cimg = cimg.rotate(-4, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
mask = Image.new("L", (cw, ch), 255).rotate(-4, expand=True, resample=Image.BICUBIC)
sh = Image.new("L", img.size, 0); sh.paste(mask, (560, 360)); sh = sh.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(28))
base = np.asarray(img, np.float32) * (1 - 0.6 * np.asarray(sh, np.float32)[..., None] / 255)
img = Image.fromarray(base.astype(np.uint8)); img.paste(cimg, (520, 300), mask)
img.save(sys.argv[1])
