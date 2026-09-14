"""Render a plain-spreadsheet version of the tracker data and compose it beside the board."""
import re, json, os, glob, sys, subprocess, html
from PIL import Image, ImageDraw, ImageFont

SC = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, SC)
from chrome_ls import latest_state

d = latest_state()
apps = [a for a in d['apps'] if a.get('name')]
STATUS = {'idea': 'Idea', 'building': 'Building', 'shipped': 'Shipped', 'video': 'Video published'}
def cost(a): return sum(float(c.get('amount') or 0) for c in a.get('costs') or [])
def hrs(a): return sum(float(w.get('hours') or 0) for w in a.get('weeks') or []) or float(a.get('hours') or 0)
def note(a):
    log = a.get('log') or []
    return (log[-1]['text'] if log else (a.get('notes') or ''))
def money(x): return ('-$' if x < 0 else '$') + f'{abs(x):,.2f}' if x else ''

rows = []
for a in apps:
    rows.append([a['n'], a['name'], 'Abandoned' if a.get('dead') else STATUS.get(a.get('status'), ''), a.get('started', ''), a.get('shipped', ''),
                 f"{hrs(a):g}" if hrs(a) else '', money(cost(a)), money(float(a.get('revenue') or 0)) if a.get('revenue') else '',
                 'Yes' if a.get('play') else '', 'Yes' if a.get('ios') else '', note(a)[:60]])
headers = ['#', 'App', 'Status', 'Started', 'Shipped', 'Hours', 'Cost', 'Revenue', 'Play', 'iOS', 'Latest note']
cols = 'ABCDEFGHIJK'
# pad to 22 rows so it looks like a sheet
while len(rows) < 22: rows.append([''] * len(headers))

def week_totals():
    t = {}
    for w in d.get('weeks') or []: t[w['week']] = max(t.get(w['week'], 0), float(w.get('hours') or 0))
    app = {}
    for a in apps:
        for w in a.get('weeks') or []: app[w['week']] = app.get(w['week'], 0) + float(w.get('hours') or 0)
    for wk, h in app.items(): t[wk] = max(t.get(wk, 0), h)
    return t
gen = [['', ''], ['General costs', ''], *[[c['item'], money(float(c['amount'] or 0))] for c in d.get('costs') or []],
       ['Total', money(sum(float(c['amount'] or 0) for c in d.get('costs') or []) + sum(cost(a) for a in apps))],
       ['', ''], ['Weekly hours', ''], *[[wk, f"{h:g}"] for wk, h in sorted(week_totals().items())]]

def td(v, cls=''): return f'<td class="{cls}">{html.escape(str(v))}</td>'
body = ''
for r, row in enumerate(rows, start=2):
    body += f'<tr><th class="rn">{r}</th>' + ''.join(td(v, 'num' if i in (0, 5, 6, 7) else '') for i, v in enumerate(row)) + '</tr>'
side = ''.join(f'<tr><th class="rn">{i+2}</th>{td(a, "b" if a in ("General costs","Weekly hours","Total") else "")}{td(b, "num")}</tr>' for i, (a, b) in enumerate(gen))

page = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#fff;font-family:Calibri,Arial,sans-serif;font-size:15px;color:#000}}
.bar{{height:34px;background:#f8f9fa;border-bottom:1px solid #dadce0;display:flex;align-items:center;padding:0 12px;gap:18px;font-size:13px;color:#444}}
.bar b{{color:#188038;font-size:15px}}
.fx{{height:30px;border-bottom:1px solid #dadce0;display:flex;align-items:center;padding:0 8px;gap:10px;font-size:13px;color:#555}}
.fx span{{border:1px solid #dadce0;padding:3px 10px;min-width:60px;background:#fff}}
table{{border-collapse:collapse;table-layout:fixed}}
th,td{{border:1px solid #e0e0e0;padding:0 6px;height:24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}}
th{{background:#f8f9fa;font-weight:normal;color:#555;text-align:center;font-size:12px}}
th.rn{{width:34px}} thead th.h{{background:#f8f9fa}}
tr.hdr td{{font-weight:bold;background:#fff;border-bottom:2px solid #999}}
td.num{{text-align:right}} td.b{{font-weight:bold}}
.wrap{{display:flex;gap:0}}
.tabs{{height:30px;border-top:1px solid #dadce0;background:#f8f9fa;display:flex;align-items:flex-end;padding-left:60px;font-size:13px}}
.tabs span{{padding:6px 18px;border:1px solid #dadce0;border-bottom:0;background:#fff;color:#188038;font-weight:bold}}
.tabs i{{padding:6px 18px;color:#666;font-style:normal}}
</style>
<div class="bar"><b>▦</b> 100 Apps Tracker.xlsx <span>File</span><span>Edit</span><span>View</span><span>Insert</span><span>Format</span><span>Data</span></div>
<div class="fx"><span>A1</span> fx <span style="min-width:600px">#</span></div>
<div class="wrap">
<table style="width:1180px">
<colgroup><col style="width:34px"><col style="width:36px"><col style="width:170px"><col style="width:120px"><col style="width:92px"><col style="width:92px"><col style="width:58px"><col style="width:78px"><col style="width:78px"><col style="width:46px"><col style="width:46px"><col style="width:330px"></colgroup>
<thead><tr><th></th>{''.join(f'<th class="h">{c}</th>' for c in cols)}</tr></thead>
<tbody><tr class="hdr"><th class="rn">1</th>{''.join(td(h) for h in headers)}</tr>{body}</tbody></table>
<table style="width:300px">
<colgroup><col style="width:34px"><col style="width:170px"><col style="width:96px"></colgroup>
<thead><tr><th></th><th class="h">M</th><th class="h">N</th></tr></thead>
<tbody><tr class="hdr"><th class="rn">1</th>{td('')}{td('')}</tr>{side}</tbody></table>
</div>
<div class="tabs"><span>Apps</span><i>Costs</i><i>Hours</i><i>+</i></div>
"""
sheet_html = os.path.join(SC, 'sheet.html'); open(sheet_html, 'w', encoding='utf-8').write(page)
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2', '--window-size=1500,720',
                f'--screenshot={os.path.join(SC, "shots", "sheet.png")}', 'file:///' + sheet_html.replace('\\', '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---- compose: sheet left, board right, labels on top ----
sheet = Image.open(os.path.join(SC, 'shots', 'sheet.png')).convert('RGB')
board = Image.open(os.path.join(SC, 'shots', 'page.png')).convert('RGB').crop((40, 30, 3160, 2380))
H = 1500; pad = 40; label_h = 120
def fit(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
b = fit(board, H); s_ = fit(sheet, int(H * 0.74))
W = pad * 3 + s_.width + b.width
canvas = Image.new('RGB', (W, H + label_h + pad * 2), (15, 17, 21))
dr = ImageDraw.Draw(canvas)
def font(sz, bold=True):
    for n in (['segoeuib.ttf', 'arialbd.ttf'] if bold else ['segoeui.ttf', 'arial.ttf']):
        p = 'C:/Windows/Fonts/' + n
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
F, f = font(54), font(30, False)
sx = pad; sy = label_h + pad + (H - s_.height) // 2
bx = pad * 2 + s_.width; by = label_h + pad
dr.text((sx, pad), 'Before: a spreadsheet', font=F, fill=(232, 234, 240))
dr.text((sx, pad + 66), 'Same data. Rows, columns, and hoping you remember to update it.', font=f, fill=(139, 147, 167))
dr.text((bx, pad), 'After: the 100 Apps tracker', font=F, fill=(255, 77, 77))
dr.text((bx, pad + 66), 'Same data. One click per square, totals that keep themselves honest.', font=f, fill=(139, 147, 167))
# thin frames
canvas.paste(s_, (sx, sy)); dr.rectangle([sx - 2, sy - 2, sx + s_.width + 1, sy + s_.height + 1], outline=(90, 95, 110), width=2)
canvas.paste(b, (bx, by)); dr.rectangle([bx - 2, by - 2, bx + b.width + 1, by + b.height + 1], outline=(90, 95, 110), width=2)
# arrow between
ax = bx - pad; ay = label_h + pad + H // 2
dr.polygon([(ax - 26, ay - 22), (ax + 4, ay), (ax - 26, ay + 22)], fill=(255, 184, 77))
os.makedirs(OUT, exist_ok=True)
canvas.save(os.path.join(OUT, '06-spreadsheet-vs-tracker.png'))
sheet.save(os.path.join(OUT, '07-spreadsheet-only.png'))
print('saved', canvas.size, 'apps', len(apps))
