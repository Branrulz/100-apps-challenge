# Promo video narration (55 s)

Two files, same cut:
- `100-apps-promo-linkedin.mp4`: opens and closes on "100 Apps Challenge", no channel name. Use for LinkedIn.
- `100-apps-promo.mp4`: same, but the cards say Blue Collar to Code. Use for YouTube.

Both are 1920x1080 and silent. Record your voice over it, or read this live and lay the video on top.
On-screen captions match each line, so read at a normal pace and you'll land on the cuts.

| Time | On screen | Say |
|------|-----------|-----|
| 0:00 - 0:03 | Transition frame: gray spreadsheet, bright tracker | I used to track everything in a spreadsheet. Then I built this. |
| 0:03 - 0:07 | Title card | I was let go from factory automation. So I started building apps. A few apps in, the idea hit me: build a hundred. |
| 0:07 - 0:13 | Stat tiles: shipped, videos, in progress, hours, revenue, spent | A project that size needs managing. So before the next app, I built the scoreboard. |
| 0:13 - 0:16 | Hold on the colored row of the grid | One square per app. Red is building, yellow shipped, green has a video up. The slash means I killed it on purpose. |
| 0:16 - 0:30 | Live: cursor clicks square 6, the form opens, scrolls, a note is typed and saved | Every square opens. Start and ship dates. Hours by week. What it cost. And a dated note every time I learn something. That's where the real lessons live. |
| 0:30 - 0:40 | Live: a square is dragged to a new slot, then another, then dragged back | Change your mind? Drag a square anywhere. Everything moves with it. |
| 0:40 - 0:45 | Full board with costs and weekly hours panels | Every dollar it took to get to production. Every hour, by week, by app. |
| 0:45 - 0:50 | Lists: currently building, shipped, abandoned | What I'm building, what shipped, what I dropped. Nothing gets hidden. |
| 0:50 - 0:55 | End card with the repo link | LinkedIn: One hundred apps. Honest numbers. Real lessons learned. The whole dataset is in a public repo. / YouTube: same, then "Follow along. I'm finding out in public." |

## Recording tips
- Phone voice memo or the laptop mic is fine. Sit close, quiet room, no fan.
- Read it twice. Use the second take.
- Leave a half second of silence at the start so the fade-in has room.
- If a line runs long, cut words, not speed.

## Regenerate
`python render_all.py` rebuilds every screenshot, the spreadsheet split, the ad frames, and both videos
from the live tracker data, with demo-only renames applied. `python record_demo.py` re-records the
live interaction clip (cursor, click, scroll, note, drags) that the videos splice in. Ask Claude to run
them when the numbers change.
