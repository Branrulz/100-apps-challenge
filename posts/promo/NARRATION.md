# Promo video narration (34 s)

File: `100-apps-promo.mp4` (1920x1080, silent). Record your voice over it, or read this live and
lay the video on top. On-screen captions match each line, so read at a normal pace and you'll land on time.

| Time | On screen | Say |
|------|-----------|-----|
| 0:00 - 0:04 | Title card: 100 Apps Challenge / Blue Collar to Code | I was let go from factory automation. So I started building apps. A few apps in, the idea hit me: build a hundred. |
| 0:04 - 0:10 | Stat tiles: shipped, videos, in progress, hours, revenue, spent | A project that size needs managing. So before the next app, I built the scoreboard. |
| 0:10 - 0:17 | Pan down the 100-square grid | One square per app. Red means building, yellow shipped, green has a video up. The slash means I killed it on purpose. |
| 0:17 - 0:23 | Full board with costs and weekly hours panels | Every dollar it took to get to production. Every hour, by week, by app. |
| 0:23 - 0:29 | Lists: currently building, shipped, abandoned | What I'm building, what shipped, what I dropped. Nothing gets hidden. |
| 0:29 - 0:34 | End card with the repo link | The whole dataset is one file in a public repo. Follow along. I'm finding out in public. |

## Recording tips
- Phone voice memo or the laptop mic is fine. Sit close, quiet room, no fan.
- Read it twice. Use the second take.
- Leave a half second of silence at the start so the fade-in has room.
- If a line runs long, cut words, not speed.

## Regenerate
The video is built from a render of tracker.html with your current data:
`python make_promo.py <scratch dir> posts/promo`. Ask Claude to re-render when the numbers change.
