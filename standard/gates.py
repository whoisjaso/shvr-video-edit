#!/usr/bin/env python3
"""Checks a tutorial before anyone sees it. usage: python3 standard/gates.py tutorials/<topic>
PASS/FAIL: both outputs exist at exactly 60/1 fps and the right size, loudness -16 LUFS (+/-1), true peak <= -1 dBTP, every step has
a privacy decision recorded, no em dash or dollar figure in the on-screen text or narration, narration files match the steps.
Then it prints the review state: nothing goes to a franchise owner until "review.jason_watched" is true."""
import json, os, re, subprocess, sys
TUT = sys.argv[1].rstrip("/"); cfg = json.load(open(os.path.join(TUT, "tutorial.json"))); slug = os.path.basename(TUT); fails = []
def gate(name, ok, info=""): print(("PASS " if ok else "FAIL ") + name + (f"  ({info})" if info else "")); ok or fails.append(name)
for fmt, (w, h) in (("16x9", (1920, 1080)), ("9x16", (1080, 1920))):
    f = os.path.join(TUT, "output", f"{slug}_{fmt}.mp4")
    if not os.path.exists(f): gate(f"{fmt} output exists", False, f); continue
    p = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate", "-of", "csv=p=0", f]).decode().strip()
    gate(f"{fmt} is {w}x{h} at 60/1", p == f"{w},{h},60/1", p)
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
    gate(f"{fmt} loudness", abs(I + 16) <= 1 and TP <= -1.0, f"I {I} LUFS, TP {TP} dBTP")
texts = [cfg["title"], cfg["subtitle"], cfg["intro_say"], cfg["outro"]["title"], cfg["outro"]["line"]] + [s[k] for s in cfg["steps"] for k in ("title", "text", "say")]
gate("no em dashes", not any("\u2014" in t for t in texts))
gate("no dollar figures in text or narration", not any(re.search(r"\$\s?\d", t) for t in texts))
gate("narration files", all(os.path.exists(os.path.join(TUT, "vo", f"line{k}.mp3")) for k in range(len(cfg["steps"]) + 1)))
gate("privacy notes recorded", bool(cfg.get("privacy_notes")), "write what was blurred and what was checked")
print(f"\n{len(fails)} failed" if fails else "\nall gates pass")
r = cfg.get("review", {})
print("REVIEW: Jason has watched it" if r.get("jason_watched") else "REVIEW: NOT cleared. Jason must watch it before it goes to any franchise owner.")
sys.exit(1 if fails else 0)
