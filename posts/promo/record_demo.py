"""Record real interactions with the tracker: visible cursor, click a square, scroll the form, drag squares."""
import os, sys, time, json, shutil, subprocess
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

SC = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
OUT = os.path.join(SC, 'clips'); os.makedirs(OUT, exist_ok=True)

CURSOR_JS = """
(() => {
  const c = document.createElement('div'); c.id = 'fakeCursor';
  c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:38px;z-index:99999;pointer-events:none;transform:translate(-4px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.6))';
  c.innerHTML = '<svg width="26" height="38" viewBox="0 0 26 38"><path d="M2 2 L2 30 L9 23 L14 35 L19 33 L14 21 L24 21 Z" fill="#fff" stroke="#000" stroke-width="2" stroke-linejoin="round"/></svg>';
  document.body.appendChild(c);
  const r = document.createElement('div'); r.id = 'clickRing';
  r.style.cssText = 'position:fixed;width:44px;height:44px;border:3px solid #ffb84d;border-radius:50%;z-index:99998;pointer-events:none;opacity:0;transform:translate(-50%,-50%) scale(.4)';
  document.body.appendChild(r);
  window.__cur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; };
  window.__ring = (x, y) => {
    r.style.transition = 'none'; r.style.left = x + 'px'; r.style.top = y + 'px'; r.style.opacity = '1'; r.style.transform = 'translate(-50%,-50%) scale(.4)';
    requestAnimationFrame(() => { r.style.transition = 'opacity .45s ease-out, transform .45s ease-out'; r.style.opacity = '0'; r.style.transform = 'translate(-50%,-50%) scale(1.6)'; });
  };
})();
"""

def run():
    state = json.load(open(os.path.join(SC, 'state-demo.json')))
    html_path = os.path.join(SC, 'shot.html')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1,
                                  record_video_dir=OUT, record_video_size={'width': W, 'height': H})
        page = ctx.new_page()
        page.goto('file:///' + html_path.replace('\\', '/'))
        page.wait_for_selector('.cell')
        page.evaluate(CURSOR_JS)
        page.evaluate("window.scrollTo(0, 0)")
        # hide the page scrollbar for a cleaner recording
        page.add_style_tag(content='html{scrollbar-width:none} ::-webkit-scrollbar{display:none}')

        def move(x, y, steps=40, dwell=0.0):
            # animated cursor: many small mouse moves
            cx, cy = page.evaluate("[window.__mx||0, window.__my||0]")
            for i in range(1, steps + 1):
                t = i / steps; e = 0.5 - 0.5 * __import__('math').cos(3.14159 * t)
                nx, ny = cx + (x - cx) * e, cy + (y - cy) * e
                page.mouse.move(nx, ny); page.evaluate(f"window.__cur({nx},{ny}); window.__mx={nx}; window.__my={ny};")
                time.sleep(0.012)
            time.sleep(dwell)
        def click(x, y):
            move(x, y, dwell=0.25); page.evaluate(f"window.__ring({x},{y})"); page.mouse.click(x, y); time.sleep(0.5)
        def center(sel):
            b = page.locator(sel).bounding_box(); return b['x'] + b['width'] / 2, b['y'] + b['height'] / 2

        # ---- scene 1: open the 100 Apps square, scroll the form, close ----
        time.sleep(0.8)
        x, y = center('.cell[data-n="6"]'); click(x, y); time.sleep(0.9)
        page.evaluate("document.getElementById('f_name').blur()")
        # scroll the modal slowly with the wheel
        modal = page.locator('.modal'); mb = modal.bounding_box()
        move(mb['x'] + mb['width'] / 2, mb['y'] + mb['height'] / 2, dwell=0.3)
        for _ in range(28): page.mouse.wheel(0, 60); time.sleep(0.07)
        time.sleep(1.0)
        # add a dated note so they see it land
        nx, ny = center('#noteText'); click(nx, ny)
        page.keyboard.type('Recorded the demo video. Drag and drop works.', delay=28); time.sleep(0.3)
        ax, ay = center('#addNote'); click(ax, ay); time.sleep(1.0)
        sx, sy = center('#saveBtn'); click(sx, sy); time.sleep(0.9)

        # ---- scene 2: drag square 7 onto square 9, then square 4 onto 10 ----
        page.evaluate("window.scrollTo(0, 0)"); time.sleep(0.4)
        def drag(from_sel, to_sel):
            fx, fy = center(from_sel); tx, ty = center(to_sel)
            move(fx, fy, dwell=0.3); page.mouse.down(); time.sleep(0.15)
            # HTML5 drag needs a few moves to start
            for i in range(1, 41):
                t = i / 40; e = 0.5 - 0.5 * __import__('math').cos(3.14159 * t)
                nx, ny = fx + (tx - fx) * e, fy + (ty - fy) * e
                page.mouse.move(nx, ny, steps=2); page.evaluate(f"window.__cur({nx},{ny}); window.__mx={nx}; window.__my={ny};"); time.sleep(0.02)
            time.sleep(0.3); page.evaluate(f"window.__ring({tx},{ty})"); page.mouse.up(); time.sleep(0.9)
        drag('.cell[data-n="7"]', '.cell[data-n="9"]')
        drag('.cell[data-n="4"]', '.cell[data-n="10"]')
        time.sleep(0.6)
        drag('.cell[data-n="10"]', '.cell[data-n="4"]')  # and put it back
        time.sleep(1.2)
        after = page.evaluate("JSON.parse(localStorage.getItem('hundredApps.v1')).apps.slice(0,10).map(a=>a.n+':'+(a.name||'-'))")
        print('slots after drags:', after)
        page.close(); ctx.close(); browser.close()
    webm = sorted([os.path.join(OUT, f) for f in os.listdir(OUT) if f.endswith('.webm')], key=os.path.getmtime)[-1]
    mp4 = os.path.join(OUT, 'demo.mp4')
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-y', '-i', webm, '-an', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-r', '30', mp4], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = subprocess.run([ff, '-i', mp4], capture_output=True, text=True).stderr
    dur = [l for l in out.splitlines() if 'Duration' in l]
    print('clip', mp4, dur[0].strip() if dur else '')

if __name__ == '__main__':
    run()
