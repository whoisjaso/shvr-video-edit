# shvr-video-edit

Customer tutorial videos for SHVR: short narrated walkthroughs that show a staff member exactly where to click to finish one task.
Private. Every tutorial follows [standard/STANDARD.md](standard/STANDARD.md).

```
standard/                 the rules every tutorial follows, and the tools
  STANDARD.md             editing rules: privacy, look, motion, narration, sound, gates, hand-off
  style.json              colours, voice settings, sound levels, loudness, formats
  render_tutorial.py      tutorial.json + screenshots + narration -> 16:9 and 9:16 MP4 (60 fps)
  make_voice.py           narration lines -> vo/lineN.mp3 (ElevenLabs, voice "Sarah")
  detect.py               finds the screenshot area and the orange highlight boxes on each step image
  extract_frames.py       splits a walkthrough GIF into step images
  gates.py                checks a finished tutorial and prints its review state
  fetch_assets.sh         downloads the font (Inter) and the music bed (not stored in git)
  sfx/                    click, whoosh and done sounds (CC0 / house originals)
tutorials/<topic>/        one folder per tutorial
  source/                 the step screenshots (stepN.png) and the original walkthrough
  tutorial.json           problem, steps, on-screen text, narration, click targets, privacy boxes, review state
  vo/                     narration (line0 = intro, lineN = step N)
  frames/                 the screenshots after the privacy blur (made by the renderer; check these)
  output/                 <topic>_16x9.mp4 and <topic>_9x16.mp4
```

## Make a new tutorial (from a problem description and screenshots)
1. **Problem.** Write the task in the staff member's words: who it's for, what they're stuck on, what "done" looks like. One task per video.
2. **Screenshots.** One screenshot per click, in order, with the spot to click boxed in orange (the format of the book-job walkthrough).
   If you have a GIF: `python3 standard/extract_frames.py walkthrough.gif tutorials/<topic>`. Otherwise save them as `tutorials/<topic>/source/step1.png`, `step2.png`...
3. **Privacy first.** Open every step image. List a box in `privacy` for each customer name, address, phone, email, staff or crew name,
   and any dollar amount the task doesn't need. Write `privacy_notes`. Screenshots only, never a live store's saved data.
4. **tutorial.json.** Copy `tutorials/book-job-from-estimate/tutorial.json` as a start. Run `python3 standard/detect.py tutorials/<topic>/source/step*.png`
   and paste each step's `body` and `targets`. Write each step's `title` (short, imperative), `text` (one line of detail) and `say` (what the narrator says).
5. **Narration.** `python3 standard/make_voice.py tutorials/<topic>`. Then set each target's `at` to when the voice names that button
   (`ffprobe` the line length if unsure).
6. **Render.** `bash standard/fetch_assets.sh` once, then `python3 standard/render_tutorial.py tutorials/<topic> --format both`.
7. **Check.** Look at `frames/` (privacy), then `python3 standard/gates.py tutorials/<topic>`, then watch both MP4s with sound.
8. **Review.** Jason watches it. Set `review.jason_watched: true` and commit. Only then does it go to the franchise owner.

Needs Python 3 with Pillow and numpy, ffmpeg, and an ElevenLabs key for new narration (`ELEVENLABS_API_KEY`; in a Claude Code cloud
session the proxy supplies it).

## Tutorials
| Tutorial | For | Steps | Length | Review |
|---|---|---|---|---|
| [book-job-from-estimate](tutorials/book-job-from-estimate/) | Office staff (Stephanie) | 7 | 0:56 | Waiting for Jason |
