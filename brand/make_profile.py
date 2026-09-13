from PIL import Image, ImageDraw, ImageFont
S = 800; SS = 4; W = S * SS  # supersample for smooth edges
img = Image.new('RGB', (W, W), '#15181f')
d = ImageDraw.Draw(img)

BLUE = '#1f56b3'; DARK = '#15181f'; HIVIS = '#ffb020'; GREEN = '#3ddc84'; WHITE = '#f4f6fa'

# Diagonal split: left/top = blue collar, right/bottom = code
d.polygon([(0, 0), (W, 0), (0, W)], fill=BLUE)
d.polygon([(W, 0), (W, W), (0, W)], fill=DARK)
# thin divider line along the diagonal
lw = 10 * SS
d.line([(W, 0), (0, W)], fill=WHITE, width=lw)

# --- Hard hat (upper-left) ---
cx, cy = int(W * 0.31), int(W * 0.34)
r = int(W * 0.15)
# dome
d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=WHITE)
# crown band
d.rectangle([cx - r, cy - int(r * 0.05), cx + r, cy + int(r * 0.12)], fill=WHITE)
# brim
bw = int(r * 1.45); bh = int(r * 0.22)
d.rounded_rectangle([cx - bw, cy + int(r * 0.08), cx + bw, cy + int(r * 0.08) + bh], radius=bh // 2, fill=WHITE)
# hi-vis stripe across dome
d.rectangle([cx - int(r * 0.18), cy - r, cx + int(r * 0.18), cy - int(r * 0.05)], fill=HIVIS)
# ridges on dome (blue lines)
for k in (-0.55, 0.55):
    x = cx + int(r * k)
    d.line([(x, cy - int(r * 0.83)), (x, cy)], fill=BLUE, width=6 * SS)

# --- Code brackets (lower-right) ---
font = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', int(W * 0.30))
txt = '</>'
bbox = d.textbbox((0, 0), txt, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx, ty = int(W * 0.69) - tw // 2 - bbox[0], int(W * 0.66) - th // 2 - bbox[1]
d.text((tx, ty), txt, font=font, fill=GREEN)

out = img.resize((S, S), Image.LANCZOS)
out.save('profile-800.png')

# circular preview so you can see what YouTube will show
mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
circ = Image.new('RGB', (S, S), '#0f0f0f'); circ.paste(out, (0, 0), mask)
prev = Image.new('RGB', (S + 400, S), '#0f0f0f'); prev.paste(circ, (0, 0))
prev.paste(circ.resize((160, 160), Image.LANCZOS), (S + 60, 40))
prev.paste(circ.resize((48, 48), Image.LANCZOS), (S + 60, 240))
prev.save('profile-preview.png')
print('ok')
