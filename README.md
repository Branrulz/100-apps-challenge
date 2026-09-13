# 100 Apps Challenge

**Blue collar to app builder.** I spent my career in factory automation (PLCs, controls, plant-floor systems).
I lost that job. Now I'm building 100 apps, on camera, to find out whether I can make a living building software.

## The rules

1. An app counts when it is **usable by someone other than me** (installed, deployed, or downloadable).
2. Every app gets a **YouTube video**: what it is, how I built it, what went wrong.
3. Small is fine. Shipping beats polishing. A weekend app counts the same as a month-long one.
4. Log every app in `tracker.html`: hours, stack, what I learned, revenue if any.
5. Be honest on camera about the numbers, good or bad.

## Tracking

Open `tracker.html` in a browser. It saves automatically and can export a JSON backup.
Keep the latest export in this folder.

## Apps so far

| # | App | What it is | Stack |
|---|-----|-----------|-------|
| 1 | JakeFirework | WiFi-controlled firework spinner rig with a phone deadman interlock | Arduino UNO Q (STM32 + Python) / Flutter |
| 2 | PLC Troubleshooter | Vendor-neutral PLC fault-finding trainer, 40 scenarios | JavaScript / Node |
| 3 | Flock Camera Tracker | Map of ALPR / Flock cameras with state laws | Web + OpenStreetMap pipeline |
| 4 | ChartinSpace | Unicorn toot-platformer game | Flutter (ported from Unity) |
| 5 | Haynes Exchange | Automated Kalshi prediction-market trader | Python / Kalshi API |
| 6 | 100 Apps | Channel companion app: factory-style "days since" counters (in progress) | TBD |

## Idea backlog

Things from the plant floor that nobody has built well yet:

- Shift-differential and overtime pay calculator
- Lockout/tagout checklist with photo proof
- Ladder-logic flashcards / quiz
- Machine downtime logger for small shops
- Tool crib inventory with barcode scan
- Preventive-maintenance scheduler for a single machine
- Sensor/wire color-code reference
- Motor sizing calculator
- Unit converter for controls people (PSI, bar, mA, scaled values)
