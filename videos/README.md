# Videos

Drop footage here. One folder per episode, numbered to match the tracker.

```
videos/
  _shared/          things every episode reuses: intro sting, outro, music, snap sound
  _template/        copy this to start a new episode
  00-intro/         the channel intro
  01-jakefirework/  app #1, and so on
```

## Inside each episode folder

```
raw/        phone clips exactly as recorded. Never edit these, never rename beyond adding a short note.
assets/     screen recordings, app screenshots, tracker screenshots, b-roll, thumbnail files
export/     the finished video and thumbnail that got uploaded
SCRIPT.md   narration and shot list. Fill in what you can, I fill in the rest.
```

## Naming raw clips

Keep the phone's filename and add a short tag so we both know what it is:

```
PXL_20260920_101500.mp4            ->  PXL_20260920_101500_hivis-intro.mp4
PXL_20260920_101830.mp4            ->  PXL_20260920_101830_snap-hoodie.mp4
```

Good tags: `hivis`, `hoodie`, `snap`, `talking`, `broll`, `screen`, `outtake`.

## Filming checklist

- Phone on a tripod, landscape, 1080p or 4K at 30 fps.
- Same spot, tape marks on the floor, for both halves of a snap.
- Record 5 seconds of silence before you talk so we can clean up audio.
- Say the line, pause, say it again. Second take is usually the keeper.
- Screen recordings of the app go in `assets/`, not `raw/`.

## What happens next

1. You drop clips in `raw/` and add anything you know to `SCRIPT.md`.
2. Tell me the episode is ready.
3. I write the narration to match the clips, build the shot list, and cut the video.
4. Finished file lands in `export/`, you upload, paste the link into the tracker.

Raw and export video files stay out of git (too big). Scripts and notes are committed.
