# SHVR tutorial video standard

Every SHVR how-to video follows this file. It is built from two house standards: the website VSL standard (calm, one job, receipts
not claims, eased motion, measured gates, owner OK before shipping) and the talking-head edit standard (narration, sound design,
pacing, privacy). The first video made to this standard is `tutorials/book-job-from-estimate/`.

## 1. One video, one job
- A tutorial teaches one task from start to finish ("book a job from an approved estimate"). If the problem needs two tasks, make two videos.
- Start from the problem in the staff member's words (`problem` in tutorial.json) and the screenshots of each click.
- 3 to 9 steps. One step = one screen and one or two clicks.
- Target length: under 75 seconds. People watch these while the app is open next to them.

## 2. Privacy (non-negotiable)
Before any render leaves this machine:
- Blur every customer name, address, phone number and email, and every staff or crew name (salesperson chips, filters named after a
  person, roster lists). Blur dollar amounts that the task does not need (pipeline value, totals). `privacy` boxes in tutorial.json
  are blurred automatically by the renderer; check `frames/` after every render.
- Write what was blurred and what was checked in `privacy_notes`. The gate fails without it.
- Use screenshots only. Never use a live store's saved data, exports or logins to build a tutorial.
- Nothing goes to a franchise owner until Jason has watched it. Set `review.jason_watched` to true only after he has.

## 3. Look (from the website standard: calm, one face, one accent)
- Light background (soft vertical gradient), ink text, one accent (orange, the same as the highlight boxes). Values: `style.json`.
- **Headings in title case** (Jason, 2026-11-25): every word of every heading starts with a capital: the task title on the title card and top bar, each step title, the done card ("How To Book A Job", "Click A Free Time On The Calendar"). The renderer does it, so write titles normally in tutorial.json. Detail lines and narration stay in sentence case.
- One typeface: Inter. Step title SemiBold, detail line Regular, brand and cards Bold. Text is set by the renderer, never left baked
  into the screenshot.
- Top bar on every step: brand, task name (16:9) and "Step N of M" with progress dots.
- The screen sits on one rounded card (22 px radius, soft shadow, 2 px hairline). The card never moves between steps.
- Title card at the start (brand, task, "N steps"); done card at the end (check mark + what is now true).
- No stats, logos or claims that are not on the screen. No prices in the text.

## 4. Motion
- Each step: the full screen first (about 1 s, long enough to read the title), then the camera eases in on the highlight, holds while
  the narration names it, and eases back out before the next step.
- A cursor glides to each spot (a slight arc), presses, and an accent ripple marks the click. Zoom 1.4x to 2.2x on 16:9, 1.6x to
  2.8x on 9:16 (the card is narrower).
- Steps change with a 0.35 s crossfade. Entrances use the expo-out curve of the web standard (cubic-bezier .19,1,.22,1); camera moves
  use a sine in-out. Nothing bounces.
- 60 fps exactly. 16:9 is 1920x1080, 9:16 is 1080x1920.

## 5. Narration
- Voice: ElevenLabs "Sarah" (mature, reassuring, American), settings in `style.json`. One voice across every SHVR tutorial.
- One line per step plus a one-line intro ("Here's how to... It takes N quick steps.") and a short close on the last step ("And that's it. You're done.").
- Plain words, second person, contractions, one action per sentence. Name every button exactly as it is labelled. Say numbers the
  way a person would. No em dashes.
- The narration says the same thing as the on-screen text, a little warmer. It never adds steps the screen does not show.
- Each target's `at` (seconds into the step) is set to land about when the voice names that button.

## 6. Sound
- Click (Kenney mouse click, CC0) on every cursor press. Soft whoosh (house original) at each step change. A short confirmation chime
  (Kenney, CC0) on the final click. Files in `sfx/`; levels in `style.json` (`sfx_db`).
- Music: one calm track very low under the voice (`music_db` -18 under the voice before loudness normalisation). Default: Mixkit
  "Discover" (free licence, may not be redistributed as a file, so `fetch_assets.sh` downloads it). Optional: a tutorial can set
  `"music": null`.
- Master -16 LUFS (spoken content on phones and laptops), true peak below -1.5 dBTP.

## 7. Gates (run `python3 standard/gates.py tutorials/<topic>`)
Both formats exist at 60/1 and the right size; loudness in range; no em dashes or dollar figures in the text; narration files match
the steps; privacy notes recorded. Then a person watches both outputs with sound before Jason sees them.

## 8. Hand-off
1. Render, gate, watch.
2. Jason watches. Set `review.jason_watched: true` in tutorial.json and commit.
3. Only then does it go to the franchise owner or staff member. Record that in `review.sent_to_franchise_owner`.
