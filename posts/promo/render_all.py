"""Rebuild every demo asset from the live tracker data, with demo-only renames applied."""
import os, sys, json, subprocess, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chrome_ls import latest_state
from PIL import Image

SC = os.path.dirname(os.path.abspath(__file__))
REPO = r'C:\Users\Brand\OneDrive\Desktop\100 Apps Challege'
SHOTS = os.path.join(REPO, 'posts', 'screenshots'); PROMO = os.path.join(REPO, 'posts', 'promo')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# Names shown in public demos only. The tracker itself is untouched.
DEMO_RENAMES = {'ChartinSpace': ('Unicorn Game', 'Unicorn platformer game')}

def demo_state():
    d = copy.deepcopy(latest_state())
    for a in d['apps']:
        if a.get('name') in DEMO_RENAMES:
            a['name'], a['pitch'] = DEMO_RENAMES[a['name']]
    return d

def chrome(out, url, size, extra=()):
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
                    f'--window-size={size}', *extra, f'--screenshot={out}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

d = demo_state()
json.dump(d, open(os.path.join(SC, 'state-demo.json'), 'w'), indent=1)
src = open(os.path.join(REPO, 'tracker.html'), encoding='utf-8').read()
seed = '<script>localStorage.setItem("hundredApps.v1", ' + json.dumps(json.dumps(d)) + ');</script>\n<script>'
html = src.replace('<script>\n(function () {', seed + '\n(function () {', 1); assert html != src
open(os.path.join(SC, 'shot.html'), 'w', encoding='utf-8').write(html)
open(os.path.join(SC, 'shot-modal.html'), 'w', encoding='utf-8').write(
    html.replace('</body>', '<script>setTimeout(function(){document.querySelector(\'[data-n="6"]\').click();},300);</script>\n</body>'))
url = 'file:///' + os.path.join(SC, 'shot.html').replace('\\', '/')
murl = 'file:///' + os.path.join(SC, 'shot-modal.html').replace('\\', '/')
os.makedirs(os.path.join(SC, 'shots'), exist_ok=True)
chrome(os.path.join(SC, 'shots', 'page.png'), url, '1600,2400')
chrome(os.path.join(SC, 'shots', 'modal.png'), murl, '1600,1500', ['--virtual-time-budget=3000'])
print('rendered page + modal')

# screenshots 01/02
im = Image.open(os.path.join(SC, 'shots', 'page.png')); W, H = im.size
bg = im.getpixel((5, 5))[:3]; last = H - 1
while last > 0 and all(im.getpixel((x, last))[:3] == bg for x in range(0, W, 40)): last -= 1
im.crop((40, 30, W - 40, 2380)).save(os.path.join(SHOTS, '01-full-board.png'))
im.crop((40, 2330, W - 40, min(last + 60, H))).save(os.path.join(SHOTS, '02-lists-below-the-board.png'))
x0, x1 = 730, 2470; w = x1 - x0
im.crop((x0, 40, x1, 40 + int(w / 1.91))).save(os.path.join(SHOTS, '02-stats-and-grid-landscape.png'))
im.crop((x0, 40, x1, 40 + w)).save(os.path.join(SHOTS, '03-stats-and-grid-square.png'))
im.crop((x0, 190, x1, 480)).save(os.path.join(SHOTS, '04-stat-tiles.png'))
print('screenshots done')

env = dict(os.environ, DEMO_STATE=os.path.join(SC, 'state-demo.json'))
run = lambda *a: subprocess.run([sys.executable, *a], check=True, env=env)
run(os.path.join(SC, 'make_sheet.py'), SC, SHOTS)
run(os.path.join(SC, 'make_ad.py'), SC, SHOTS, '--linkedin')
run(os.path.join(SC, 'make_ad.py'), SC, SHOTS)
run(os.path.join(SC, 'make_promo.py'), SC, PROMO, '--linkedin')
run(os.path.join(SC, 'make_promo.py'), SC, PROMO)
print('all done')
