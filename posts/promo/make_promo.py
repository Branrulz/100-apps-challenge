import os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

SC = sys.argv[1]; OUT = sys.argv[2]
PAGE = Image.open(os.path.join(SC, 'shots', 'page.png')).convert('RGB')
W, H = 1920, 1080; FPS = 30
BG = (15, 17, 21); RED = (255, 77, 77); MUTED = (139, 147, 167); WHITE = (232, 234, 240)

def font(size, bold=True):
    for name in (['segoeuib.ttf', 'arialbd.ttf'] if bold else ['segoeui.ttf', 'arial.ttf']):
        p = 'C:/Windows/Fonts/' + name
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = font(120); F_SUB = font(52, False); F_CAP = font(44); F_SMALL = font(36, False)

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * t)

def kb_frame(r0, r1, t):
    """Ken Burns: crop rect interpolated from r0 to r1 (both 16:9), resized to 1920x1080."""
    e = ease(t)
    r = [r0[i] + (r1[i] - r0[i]) * e for i in range(4)]
    # keep the crop inside the page: shift, never distort
    PW, PH = PAGE.size
    if r[0] < 0: r[2] -= r[0]; r[0] = 0
    if r[1] < 0: r[3] -= r[1]; r[1] = 0
    if r[2] > PW: r[0] -= r[2] - PW; r[2] = PW
    if r[3] > PH: r[1] -= r[3] - PH; r[3] = PH
    return PAGE.crop(tuple(int(v) for v in r)).resize((W, H), Image.LANCZOS)

def caption(img, text):
    if not text: return img
    d = ImageDraw.Draw(img, 'RGBA')
    tw = d.textlength(text, font=F_CAP)
    pad = 28; bw = tw + pad * 2; bh = 44 + pad * 2
    x = (W - bw) / 2; y = H - bh - 48
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=14, fill=(15, 17, 21, 215))
    d.text((x + pad, y + pad - 4), text, font=F_CAP, fill=WHITE)
    return img

def card(lines, sub=None, small=None):
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    y = H / 2 - 120 if sub else H / 2 - 60
    # title with red accent on the last word
    words = lines.split(' '); head = ' '.join(words[:-1]) + ' '; tail = words[-1]
    tw = d.textlength(head, font=F_TITLE) + d.textlength(tail, font=F_TITLE)
    x = (W - tw) / 2
    d.text((x, y), head, font=F_TITLE, fill=WHITE); d.text((x + d.textlength(head, font=F_TITLE), y), tail, font=F_TITLE, fill=RED)
    if sub:
        sw = d.textlength(sub, font=F_SUB); d.text(((W - sw) / 2, y + 150), sub, font=F_SUB, fill=MUTED)
    if small:
        sw = d.textlength(small, font=F_SMALL); d.text(((W - sw) / 2, H - 140), small, font=F_SMALL, fill=MUTED)
    return img

def fade(a, b, t):
    return Image.blend(a, b, ease(t))

# ---- storyboard: (seconds, kind, args, caption) ----
# crop rects are in page.png pixel coords (3200 wide). All 16:9.
def rect(cx, cy, w): h = w * 9 / 16; return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
SEG = [
    (4.0, 'card', ('100 Apps Challenge', 'Blue Collar to Code', None), None),
    (6.0, 'kb', (rect(1600, 560, 2400), rect(1600, 420, 1800)), 'One project. 100 apps. A scoreboard.'),
    (7.0, 'kb', (rect(1600, 1000, 2200), rect(1600, 1450, 2200)), 'One square per app. Red building, yellow shipped, green has a video.'),
    (6.0, 'kb', (rect(1600, 900, 3200), rect(1600, 800, 2900)), 'Every dollar to production. Every hour, by week, by app.'),
    (6.0, 'kb', (rect(1600, 2950, 2400), rect(1600, 3050, 2300)), 'Building, shipped, abandoned. Nothing hidden.'),
    (5.0, 'card', ('Blue Collar to Code', '100 apps, honest numbers, real lessons learned', 'github.com/Branrulz/100-apps-challenge'), None),
]
XF = 0.5  # crossfade seconds

frames = []
def seg_frame(seg, t):
    dur, kind, args, cap = seg
    if kind == 'card': img = card(*args)
    else: img = kb_frame(args[0], args[1], t / dur)
    return caption(img, cap)

total = sum(s[0] for s in SEG)
print('duration', total, 's')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(OUT, exist_ok=True)
outfile = os.path.join(OUT, '100-apps-promo.mp4')
cmd = [ffmpeg, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-s', f'{W}x{H}', '-pix_fmt', 'rgb24', '-r', str(FPS), '-i', '-',
       '-an', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', outfile]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
n = 0; samples = {}
for i, seg in enumerate(SEG):
    dur = seg[0]; nf = int(dur * FPS)
    for f in range(nf):
        t = f / FPS
        img = seg_frame(seg, t)
        # crossfade into the next segment during the last XF seconds
        if i + 1 < len(SEG) and t > dur - XF:
            nxt = seg_frame(SEG[i + 1], 0.0)
            img = fade(img, nxt, (t - (dur - XF)) / XF)
        # fade in from black at the very start, out at the very end
        if i == 0 and t < 0.8: img = Image.blend(Image.new('RGB', (W, H), BG), img, t / 0.8)
        if i == len(SEG) - 1 and t > dur - 1.0: img = Image.blend(img, Image.new('RGB', (W, H), BG), (t - (dur - 1.0)) / 1.0)
        proc.stdin.write(np.asarray(img, dtype=np.uint8).tobytes()); n += 1
        if f == nf // 2: samples[i] = img.copy()
proc.stdin.close(); proc.wait()
for i, img in samples.items(): img.save(os.path.join(SC, 'shots', f'promo-seg{i}.jpg'), quality=85)
print('frames', n, 'file', outfile, os.path.getsize(outfile) // 1024, 'KB')
