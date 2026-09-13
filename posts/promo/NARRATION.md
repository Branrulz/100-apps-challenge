# Promo video narration (45 s)

Two files, same cut:
- `100-apps-promo-linkedin.mp4`: opens and closes on "100 Apps Challenge", no channel name. Use for LinkedIn.
- `100-apps-promo.mp4`: same, but the cards say Blue Collar to Code. Use for YouTube.

Both are 1920x1080 and silent. Record your voice over it, or read this live and lay the video on top.
On-screen captions match each line, so read at a normal pace and you'll land on the cuts.

| Time | On screen | Say |
|------|-----------|-----|
| 0:00 - 0:04 | Title card | I was let go from factory automation. So I started building apps. A few apps in, the idea hit me: build a hundred. |
| 0:04 - 0:10 | Stat tiles: shipped, videos, in progress, hours, revenue, spent | A project that size needs managing. So before the next app, I built the scoreboard. |
| 0:10 - 0:17 | Pan down the 100-square grid | One square per app. Red means building, yellow shipped, green has a video up. The slash means I killed it on purpose. |
| 0:17 - 0:20 | Zoom toward square 6 | Every square opens. |
| 0:20 - 0:28 | Pan down the open square: dates, hours by week, costs, dated notes | Start and ship dates. Hours by week. What it cost. And a dated note every time I learn something. That's where the real lessons live. |
| 0:28 - 0:34 | Full board with costs and weekly hours panels | Every dollar it took to get to production. Every hour, by week, by app. |
| 0:34 - 0:40 | Lists: currently building, shipped, abandoned | What I'm building, what shipped, what I dropped. Nothing gets hidden. |
| 0:40 - 0:45 | End card with the repo link | LinkedIn: One hundred apps. Honest numbers. Real lessons learned. The whole dataset is in a public repo. / YouTube: same, then "Follow along. I'm finding out in public." |

## Recording tips
- Phone voice memo or the laptop mic is fine. Sit close, quiet room, no fan.
- Read it twice. Use the second take.
- Leave a half second of silence at the start so the fade-in has room.
- If a line runs long, cut words, not speed.

## Regenerate
The video is built from a render of tracker.html with your current data.
`python make_promo.py <scratch dir> posts/promo` for YouTube, add `--linkedin` for the LinkedIn cut.
Ask Claude to re-render when the numbers change.
