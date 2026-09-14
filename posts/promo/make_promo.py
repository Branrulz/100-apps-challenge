import os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

SC = sys.argv[1]; OUT = sys.argv[2]
PAGE = Image.open(os.path.join(SC, 'shots', 'page.png')).convert('RGB')
MODAL = Image.open(os.path.join(SC, 'shots', 'modal.png')).convert('RGB')  # the 100 Apps square opened
W, H = 1920, 1080; FPS = 30
BG = (15, 17, 21); RED = (255, 77, 77); MUTED = (139, 147, 167); WHITE = (232, 234, 240)

def font(size, bold=True):
    for name in (['segoeuib.ttf', 'arialbd.ttf'] if bold else ['segoeui.ttf', 'arial.ttf']):
        p = 'C:/Windows/Fonts/' + name
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = font(120); F_SUB = font(52, False); F_CAP = font(54); F_SMALL = font(36, False)

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * t)

def kb_frame(r0, r1, t, src=None):
    """Ken Burns: crop rect interpolated from r0 to r1 (both 16:9), resized to 1920x1080."""
    src = src or PAGE
    e = ease(t)
    r = [r0[i] + (r1[i] - r0[i]) * e for i in range(4)]
    # keep the crop inside the page: shift, never distort
    PW, PH = src.size
    if r[0] < 0: r[2] -= r[0]; r[0] = 0
    if r[1] < 0: r[3] -= r[1]; r[1] = 0
    if r[2] > PW: r[0] -= r[2] - PW; r[2] = PW
    if r[3] > PH: r[1] -= r[3] - PH; r[3] = PH
    return src.crop(tuple(int(v) for v in r)).resize((W, H), Image.LANCZOS)

def caption(img, text):
    if not text: return img
    d = ImageDraw.Draw(img, 'RGBA')
    tw = d.textlength(text, font=F_CAP)
    pad = 30; bw = tw + pad * 2; bh = 56 + pad * 2
    x = (W - bw) / 2; y = H - bh - 48
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=14, fill=(15, 17, 21, 215))
    d.text((x + pad, y + pad - 4), text, font=F_CAP, fill=WHITE)
    return img

F_BIG = font(108); F_MED = font(78); F_KICK = font(40)
def title(img, beats, t):
    """beats: list of (start, end, text, pos). pos = 'left' | 'right' | 'bottomleft'. Slide+fade in, fade out."""
    for (b0, b1, text, pos) in beats:
        if not (b0 <= t < b1): continue
        a_in = min(1, (t - b0) / 0.45); a_out = min(1, (b1 - t) / 0.4); a = ease(min(a_in, a_out))
        if a <= 0: continue
        lines = text.split('|')
        d = ImageDraw.Draw(img, 'RGBA')
        small = pos in ('leftsm', 'rightsm'); F = F_MED if small else F_BIG; LH = 82 if small else 112
        lw = max(d.textlength(l, font=F) for l in lines); lh = LH * len(lines)
        pad = 30 if small else 34; bw = lw + pad * 2 + 22; bh = lh + pad * 2
        if pos == 'left': x, y = 70, H // 2 - bh // 2
        elif pos == 'leftsm': x, y = 40, H // 2 - bh // 2
        elif pos == 'rightsm': x, y = W - bw - 40, H // 2 - bh // 2
        elif pos == 'right': x, y = W - bw - 70, H // 2 - bh // 2
        elif pos == 'top': x, y = 70, 150
        elif pos == 'topright': x, y = W - bw - 70, 150
        else: x, y = 70, H - bh - 90
        slide = int((1 - a) * 60) * (1 if pos.startswith('right') or pos == 'topright' else -1)
        x += slide
        al = int(235 * a)
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=12, fill=(10, 12, 16, int(215 * a)))
        d.rectangle([x, y, x + 12, y + bh], fill=(255, 77, 77, al))
        for i, l in enumerate(lines):
            d.text((x + pad + 22, y + pad - 8 + i * LH), l, font=F, fill=(240, 242, 246, al))
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

CLIP = os.path.join(SC, 'clips', 'demo.mp4')
class Vid:
    """Streams frames of a clip range through ffmpeg; frame(0) is cached for crossfades."""
    def __init__(self, path, start, dur):
        self.path, self.start, self.dur = path, start, dur; self.proc = None; self.i = -1; self.first = None; self.last = None
    def _open(self):
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        self.proc = subprocess.Popen([ff, '-ss', str(self.start), '-t', str(self.dur + 0.2), '-i', self.path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-'],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.i = -1
    def frame(self, i):
        if i == 0 and self.first is not None: return self.first
        if self.proc is None: self._open()
        while self.i < i:
            raw = self.proc.stdout.read(W * H * 3)
            if len(raw) < W * H * 3: return self.last or self.first
            self.last = Image.frombytes('RGB', (W, H), raw); self.i += 1
            if self.i == 0: self.first = self.last.copy()
        return self.last

def fade(a, b, t):
    return Image.blend(a, b, ease(t))

# ---- storyboard: (seconds, kind, args, caption) ----
# crop rects are in page.png pixel coords (3200 wide). All 16:9.
def rect(cx, cy, w): h = w * 9 / 16; return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
LINKEDIN = '--linkedin' in sys.argv  # no channel branding, just the challenge
AD = Image.open(os.path.join(OUT, '..', 'screenshots', '08-transition-ad' + ('-linkedin' if LINKEDIN else '') + '.png')).convert('RGB').resize((W, H), Image.LANCZOS)
SEG = [
    (3.0, 'img', (AD,), []),
    (4.0, 'card', ('100 Apps Challenge', 'Building 100 apps. Tracking every one.' if LINKEDIN else 'Blue Collar to Code', None), []),
    (6.0, 'kb', (rect(1600, 560, 2400), rect(1600, 420, 1800)), []),
    (3.5, 'kb', (rect(1600, 1000, 2200), rect(1600, 1050, 2000)), [(0.2, 3.3, 'ONE SQUARE|PER APP', 'right')]),
    (13.5, 'vid', (Vid(CLIP, 0.6, 13.5),), [(0.2, 3.2, 'CLICK|A SQUARE', 'leftsm'), (3.6, 7.0, 'HOURS|BY WEEK', 'leftsm'), (7.4, 13.2, 'DATED|NOTES', 'leftsm')]),
    (10.5, 'vid', (Vid(CLIP, 14.2, 10.5),), [(0.2, 4.4, 'DRAG TO|REARRANGE', 'leftsm'), (4.8, 10.2, 'EVERYTHING|MOVES|WITH IT', 'leftsm')]),
    (4.5, 'kb', (rect(1600, 900, 3200), rect(1600, 800, 2900)), [(0.2, 4.3, 'COSTS AND HOURS|ADD THEMSELVES UP', 'bottomleft')]),
    (5.0, 'kb', (rect(2000, 2950, 2400), rect(2000, 3050, 2300)), [(0.2, 4.8, 'NOTHING|HIDDEN', 'rightsm')]),
    (5.0, 'card', ('100 Apps Challenge', 'Honest numbers, real lessons learned', 'github.com/Branrulz/100-apps-challenge') if LINKEDIN
               else ('Blue Collar to Code', '100 apps, honest numbers, real lessons learned', 'github.com/Branrulz/100-apps-challenge'), []),
]
XF = 0.5  # crossfade seconds

frames = []
def seg_frame(seg, t):
    dur, kind, args, beats = seg
    if kind == 'card': img = card(*args)
    elif kind == 'img':
        # slow push-in on a still
        z = 1 + 0.04 * ease(t / dur); cw, ch = int(W / z), int(H / z)
        img = args[0].crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.LANCZOS)
    elif kind == 'vid': img = args[0].frame(int(round(t * FPS))).copy()
    elif kind == 'kbm': img = kb_frame(args[0], args[1], t / dur, MODAL)
    else: img = kb_frame(args[0], args[1], t / dur)
    return title(img, beats, t)

total = sum(s[0] for s in SEG)
print('duration', total, 's')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(OUT, exist_ok=True)
outfile = os.path.join(OUT, '100-apps-promo-linkedin.mp4' if LINKEDIN else '100-apps-promo.mp4')
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
