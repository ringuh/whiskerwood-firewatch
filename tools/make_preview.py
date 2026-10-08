from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import sys
src, out = sys.argv[1], sys.argv[2]
W = 1174
im = Image.open(src).convert('RGB')
im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
im = ImageOps.grayscale(im).convert('RGB')
im = ImageEnhance.Brightness(im).enhance(0.38)
BAR = 190
H = im.height + BAR
canvas = Image.new('RGB', (W, H), (18, 17, 16))
canvas.paste(im, (0, 0))
RED = (229, 50, 50)
# stamp
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = ImageFont.truetype(F, 150)
txt = 'DEPRECATED'
bb = font.getbbox(txt)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
pad = 40
st = Image.new('RGBA', (tw + 2 * pad + 20, th + 2 * pad + 20), (0, 0, 0, 0))
d = ImageDraw.Draw(st)
d.rounded_rectangle((10, 10, st.width - 10, st.height - 10), radius=26, outline=RED + (255,), width=16)
d.text((10 + pad - bb[0], 10 + pad - bb[1]), txt, font=font, fill=RED + (255,))
st = st.rotate(22, resample=Image.BICUBIC, expand=True)
if st.width > W - 40:
    s = (W - 40) / st.width
    st = st.resize((round(st.width * s), round(st.height * s)), Image.LANCZOS)
canvas.paste(st, ((W - st.width) // 2, (im.height - st.height) // 2), st)
d = ImageDraw.Draw(canvas)
f1 = ImageFont.truetype(F, 46); f2 = ImageFont.truetype(F, 38)
def center(y, t, f, c):
    b = d.textbbox((0, 0), t, font=f); d.text(((W - (b[2] - b[0])) // 2 - b[0], y), t, font=f, fill=c)
center(im.height + 40, 'This mod is no longer maintained', f1, (240, 240, 240))
center(im.height + 112, 'Use Remote Campfire by Niklas', f2, (255, 200, 50))
canvas.save(out, optimize=True)
print(canvas.size)
