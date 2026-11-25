#!/usr/bin/env python3
"""Narration for a tutorial: tutorials/<topic>/vo/line0.mp3 (intro) and line1..lineN.mp3 (one per step), from tutorial.json
("intro_say" and each step's "say") with the house voice in standard/style.json.
usage: python3 standard/make_voice.py tutorials/<topic> [--only 3]
Key: ELEVENLABS_API_KEY in the environment. In a Claude Code cloud session the proxy adds the key, so any value works.
Writing rules for "say": plain words, second person, contractions, one action per sentence, name the button exactly as it is labelled,
say numbers the way a person would ("twenty-two eleven"), no em dashes."""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); TUT = sys.argv[1].rstrip("/")
cfg = json.load(open(os.path.join(TUT, "tutorial.json"))); v = json.load(open(os.path.join(HERE, "style.json")))["voice"]
lines = [cfg["intro_say"]] + [s["say"] for s in cfg["steps"]]
only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
os.makedirs(os.path.join(TUT, "vo"), exist_ok=True)
for k, text in enumerate(lines):
    if only is not None and k != only: continue
    assert "\u2014" not in text, f"em dash in line {k}"
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": v["model_id"], "voice_settings": v["settings"]}).encode(),
        headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "set-by-proxy"), "Content-Type": "application/json"})
    open(os.path.join(TUT, "vo", f"line{k}.mp3"), "wb").write(urllib.request.urlopen(req, timeout=120).read()); print("line", k, "ok")
