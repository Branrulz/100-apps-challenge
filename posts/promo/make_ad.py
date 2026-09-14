"""Ad-style transition frame: gray spreadsheet wipes into the bright tracker along a glowing diagonal."""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

SC, OUT = sys.argv[1], sys.argv[2]
LINKEDIN = '--linkedin' in sys.argv
W, H = 3840, 2160
BG = (12, 14, 18); RED = (255, 77, 77); ORANGE = (255, 184, 77); WHITE = (236, 238, 243); MUTED = (150, 158, 176)

def font(sz, bold=True):
    for n in (['segoeuib.ttf', 'arialbd.ttf'] if bold else ['segoeui.ttf', 'arial.ttf']):
        p = 'C:/Windows/Fonts/' + n
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def _coeffs(dst, src):
    """Perspective coefficients so that source rect corners land on dst quad (UL, UR, LR, LL)."""
    import numpy as np
    A = []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    B = np.array([c for p in src for c in p], dtype=float)
    return np.linalg.solve(np.array(A, dtype=float), B).tolist()

def perspective(im, dx_top, dx_bot, shrink):
    """Skew a card so one side recedes. shrink<0 = left edge shorter, >0 = right edge shorter."""
    w, h = im.size
    pad = int(h * 0.12)
    canvas = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); canvas.paste(im, (pad, pad))
    cw, ch = canvas.size
    s = abs(shrink) * ch
    if shrink < 0:  # left edge recedes
        dst = [(0, s), (cw, 0), (cw, ch), (0, ch - s)]
    else:           # right edge recedes
        dst = [(0, 0), (cw, s), (cw, ch - s), (0, ch)]
    src = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    return canvas.transform((cw, ch), Image.PERSPECTIVE, _coeffs(dst, src), Image.BICUBIC)

def shadow(card, blur=60, offset=(0, 40), alpha=170):
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: int(v * alpha / 255))
    sh.putalpha(a); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', (card.width + 200, card.height + 200), (0, 0, 0, 0))
    out.paste(sh, (100 + offset[0], 100 + offset[1]), sh); out.paste(card, (100, 100), card)
    return out

# ---- source images ----
sheet = Image.open(os.path.join(SC, 'shots', 'sheet.png')).convert('RGB')
board = Image.open(os.path.join(SC, 'shots', 'page.png')).convert('RGB').crop((140, 60, 3060, 2380))

# spreadsheet: gray, dim, slightly blurred = the past
sheet = ImageOps.grayscale(sheet).convert('RGB')
sheet = ImageEnhance.Brightness(sheet).enhance(0.55)
sheet = ImageEnhance.Contrast(sheet).enhance(0.9)

# ---- background: dark gradient + faint grid ----
bg = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(bg)
for y in range(H):
    t = y / H; c = (int(12 + 10 * t), int(14 + 10 * t), int(18 + 14 * t)); d.line([(0, y), (W, y)], fill=c)
for x in range(0, W, 120): d.line([(x, 0), (x, H)], fill=(20, 23, 30))
for y in range(0, H, 120): d.line([(0, y), (W, y)], fill=(20, 23, 30))
# red glow behind the right half
glow = Image.new('RGB', (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([W * 0.55, -H * 0.3, W * 1.25, H * 1.3], fill=(70, 14, 14))
glow = glow.filter(ImageFilter.GaussianBlur(260))
import numpy as np
bg = Image.fromarray(np.clip(np.asarray(bg, dtype=int) + np.asarray(glow, dtype=int), 0, 255).astype('uint8'))
frame = bg.convert('RGBA')

# ---- cards ----
card_h = int(H * 0.60)
def fit_h(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
s_card = fit_h(sheet, int(card_h * 0.92)).convert('RGBA')
b_card = fit_h(board, card_h).convert('RGBA')
# rounded corners + thin border
def rounded(im, r=28, border=(70, 76, 92)):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    im = im.copy(); im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, outline=border, width=3)
    return im
s_card = rounded(s_card); b_card = rounded(b_card, border=(255, 77, 77))
s_card = shadow(perspective(s_card, 0, 0, +0.09), blur=50, alpha=140)
b_card = shadow(perspective(b_card, 0, 0, -0.07), blur=80, alpha=220)

# positions: overlap slightly at the seam, tracker on top
cy = int(H * 0.60)
sx = int(W * 0.03); sy = cy - s_card.height // 2 + 20
bx = int(W * 0.40); by = cy - b_card.height // 2
frame.alpha_composite(s_card, (sx, sy))

# ---- diagonal wipe: darken everything left of the seam a little more, then glowing seam ----
seam_top = int(W * 0.47); seam_bot = int(W * 0.37)
mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0), (seam_top, 0), (seam_bot, H), (0, H)], fill=90)
dark = Image.new('RGBA', (W, H), (0, 0, 0, 255)); dark.putalpha(mask); frame.alpha_composite(dark)
frame.alpha_composite(b_card, (bx, by))
seam = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(seam)
sd.line([(seam_top, 0), (seam_bot, H)], fill=(255, 120, 60, 255), width=14)
seam = seam.filter(ImageFilter.GaussianBlur(22))
frame.alpha_composite(seam)
sd2 = ImageDraw.Draw(frame); sd2.line([(seam_top, 0), (seam_bot, H)], fill=(255, 200, 120, 255), width=4)

# ---- headline ----
F1, F2, F3 = font(150), font(56, False), font(46, False)
dr = ImageDraw.Draw(frame)
hx, hy = int(W * 0.045), int(H * 0.05)
dr.text((hx, hy), 'From spreadsheet', font=F1, fill=MUTED)
w1 = dr.textlength('From spreadsheet ', font=F1)
dr.text((hx + w1, hy), 'to scoreboard.', font=F1, fill=RED)
dr.text((hx, hy + 175), 'Same data. One click per app. Totals that keep themselves honest.', font=F2, fill=WHITE)
# footer
foot = '100 Apps Challenge' + ('' if LINKEDIN else '  ·  Blue Collar to Code') + '  ·  github.com/Branrulz/100-apps-challenge'
fw = dr.textlength(foot, font=F3)
dr.text(((W - fw) / 2, H - 110), foot, font=F3, fill=MUTED)
# small labels on the cards
sb = s_card.getbbox(); bb = b_card.getbbox()
dr.text((sx + sb[0] + 10, sy + sb[1] - 70), 'BEFORE', font=font(40), fill=(120, 126, 140))
aw = dr.textlength('AFTER', font=font(40))
dr.text((bx + bb[2] - aw - 10, by + bb[1] - 70), 'AFTER', font=font(40), fill=RED)

os.makedirs(OUT, exist_ok=True)
name = '08-transition-ad' + ('-linkedin' if LINKEDIN else '') + '.png'
frame.convert('RGB').save(os.path.join(OUT, name), quality=95)
print('saved', name, frame.size)
