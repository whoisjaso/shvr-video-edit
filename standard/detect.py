#!/usr/bin/env python3
"""Suggest "body" (the screenshot area under the instruction header) and "targets" (orange highlight boxes) for each step image.
usage: python3 standard/detect.py tutorials/<topic>/source/step*.png
Works on screenshots annotated with orange boxes (as in the book-job GIF). Paste the printed boxes into tutorial.json, then set each
target's "at" (seconds into the step when the narration says to click it). Always check the result on the stills."""
import sys, json, numpy as np
from PIL import Image
for f in sys.argv[1:]:
    a = np.array(Image.open(f).convert("RGB")).astype(int); H, W, _ = a.shape; bg = a[5, 5]
    d = np.abs(a - bg).sum(2) > 30
    rows = [y for y in range(40, H) if d[y, W // 6: W * 5 // 6].mean() > 0.9]; top = rows[0] if rows else 0
    bot = max([y for y in range(top, H) if d[y, W // 6: W * 5 // 6].mean() > 0.9] or [H - 1])
    cols = [x for x in range(W) if d[top:bot, x].mean() > 0.9]
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; m = (R > 220) & (G > 90) & (G < 170) & (B < 90); m[:top] = False
    cell = 20; grid = np.zeros((H // cell + 1, W // cell + 1), bool); ys, xs = np.nonzero(m); grid[ys // cell, xs // cell] = True
    seen = np.zeros_like(grid); boxes = []
    for gy, gx in zip(*np.nonzero(grid)):
        if seen[gy, gx]: continue
        st = [(gy, gx)]; seen[gy, gx] = True; pts = []
        while st:
            y, x = st.pop(); pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < grid.shape[0] and 0 <= xx < grid.shape[1] and grid[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        py, px = [p[0] for p in pts], [p[1] for p in pts]; b = [min(px) * cell, min(py) * cell, (max(px) + 1) * cell, (max(py) + 1) * cell]
        if (b[2] - b[0]) * (b[3] - b[1]) > 2500: boxes.append([int(v) for v in b])
    print(json.dumps({"frame": f, "body": [int(cols[0]) if cols else 0, int(top), int(cols[-1]) + 1 if cols else W, int(bot) + 1], "targets": [{"box": b, "at": 1.2} for b in boxes]}))
