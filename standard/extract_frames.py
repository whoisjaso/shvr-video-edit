#!/usr/bin/env python3
"""Split a walkthrough GIF (or a folder of PNGs) into tutorials/<topic>/source/stepN.png.
usage: python3 standard/extract_frames.py walkthrough.gif tutorials/<topic>"""
import os, sys
from PIL import Image
src, tut = sys.argv[1], sys.argv[2].rstrip("/"); os.makedirs(os.path.join(tut, "source"), exist_ok=True)
im = Image.open(src); i = 0
try:
    while True: im.convert("RGB").save(os.path.join(tut, "source", f"step{i + 1}.png")); i += 1; im.seek(i)
except EOFError: pass
print(i, "steps written")
