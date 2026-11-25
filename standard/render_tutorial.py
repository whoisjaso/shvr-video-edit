#!/usr/bin/env python3
"""Render a narrated SHVR tutorial from step screenshots.

usage:  python3 standard/render_tutorial.py tutorials/<topic> [--format 16x9|9x16|both]

Reads tutorials/<topic>/tutorial.json (see standard/STANDARD.md for the fields), the step screenshots it lists and the voice lines
in tutorials/<topic>/vo/ (made by standard/make_voice.py). Writes:
  tutorials/<topic>/frames/   the screenshots after the privacy blur (review these before sharing anything)
  tutorials/<topic>/output/   <slug>_16x9.mp4 and/or <slug>_9x16.mp4, 60 fps
Look: light theme, one typeface (Inter), one accent, the screenshot on a rounded card, a cursor that glides to each highlight and
clicks, progress dots, a title card and a done card. Motion uses the expo-out curve of the house web standard (cubic-bezier .19,1,.22,1).
"""
import json, math, os, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TUT = sys.argv[1].rstrip("/"); FMT = (sys.argv[sys.argv.index("--format") + 1] if "--format" in sys.argv else "both")
CFG = json.load(open(os.path.join(TUT, "tutorial.json")))
FPS = 60
INTER = os.path.join(HERE, "fonts", "Inter.ttf")
SFX = {k: os.path.join(HERE, "sfx", f) for k, f in (("click", "click.ogg"), ("whoosh", "whoosh.wav"), ("done", "done.wav"))}
STY = json.load(open(os.path.join(HERE, "style.json")))
INK, MUTED, ACCENT, LINE, PAPER = (tuple(STY["colors"][k]) for k in ("ink", "muted", "accent", "line", "paper"))
BG_TOP, BG_BOT = np.array(STY["colors"]["bg_top"]), np.array(STY["colors"]["bg_bottom"])

def font(size, weight):
    f = ImageFont.truetype(INTER, size); f.set_variation_by_name(weight); return f
def expo(x):                                                 # ease-out, close to cubic-bezier(.19,1,.22,1)
    x = min(1, max(0, x)); return 1 - pow(2, -10 * x) if x < 1 else 1.0
def inout(x):
    x = min(1, max(0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)
def heading(t):                                             # owner rule 2026-11-25: every word of a heading starts with a capital
    return " ".join(w[:1].upper() + w[1:] for w in t.split(" "))
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

# ---------- privacy: blur every listed box before anything else touches the frames ----------
STEPS = CFG["steps"]; os.makedirs(os.path.join(TUT, "frames"), exist_ok=True)
frames = []
for k, s in enumerate(STEPS):
    im = Image.open(os.path.join(TUT, s["frame"])).convert("RGB")
    for p in CFG.get("privacy", []):
        if p["step"] == k + 1:
            x0, y0, x1, y1 = p["box"]; reg = im.crop((x0, y0, x1, y1))
            reg = reg.resize((max(1, (x1 - x0) // 10), max(1, (y1 - y0) // 10)), Image.BILINEAR).resize((x1 - x0, y1 - y0), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
            im.paste(reg, (x0, y0))
    im.save(os.path.join(TUT, "frames", f"step{k + 1}.png")); frames.append(im)

# ---------- timeline (shared by both formats) ----------
vo = [dur(os.path.join(TUT, "vo", f"line{k}.mp3")) for k in range(len(STEPS) + 1)]
INTRO = vo[0] + 0.9; spans = []; t = INTRO
for k, s in enumerate(STEPS):
    last_at = max([g["at"] for g in s["targets"]] or [0]); d = max(vo[k + 1] + 1.1, last_at + 1.6); spans.append((t, d)); t += d
LAST = t; OUTRO = 2.6; END = LAST + OUTRO; N = int(END * FPS)

def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if d.textlength(nxt, font=f) <= width: cur = nxt
        else: lines.append(cur); cur = w
    return lines + [cur] if cur else lines

def render(fmt):
    V = fmt == "9x16"; W, H = (1080, 1920) if V else (1920, 1080)
    g = np.linspace(0, 1, H)[:, None]; BG = Image.fromarray((BG_TOP * (1 - g) + BG_BOT * g)[:, None, :].repeat(W, 1).astype(np.uint8))
    M = 60 if V else 160                                      # side margin
    fTitle, fSub = font(60 if V else 50, "SemiBold"), font(34 if V else 28, "Regular")
    fSmall, fBadge, fBrand = font(26 if V else 24, "Medium"), font(30, "Bold"), font(28 if V else 26, "Bold")
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw_max = W - M - (M + 84)
    title_l = [wrap(tmp, heading(s["title"]), fTitle, tw_max) for s in STEPS]; sub_l = [wrap(tmp, s["text"], fSub, tw_max) for s in STEPS]
    if V:                                                     # card under the tallest text block so it never moves between steps
        text_h = max(len(a) * 72 + 16 + len(b) * 44 for a, b in zip(title_l, sub_l))
        CARD = (M, 190 + text_h + 60, W - M, H - 190)
    else:
        CARD = (160, 300, 1760, 1020)
    CW, CH = CARD[2] - CARD[0], CARD[3] - CARD[1]; R = 22
    mask = Image.new("L", (CW, CH), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW - 1, CH - 1], R, fill=255)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle([CARD[0], CARD[1] + 18, CARD[2], CARD[3] + 18], R, fill=INK + (60,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    n = len(STEPS)
    def chrome(k):
        img = Image.alpha_composite(BG.convert("RGBA"), shadow); d = ImageDraw.Draw(img); top = 90 if V else 64
        d.text((M, top), CFG["brand"], font=fBrand, fill=INK)
        if not V: d.text((M + d.textlength(CFG["brand"] + "  ", font=fBrand), top + 2), "·  " + heading(CFG["title"]), font=fSmall, fill=MUTED)
        lab = f"Step {k + 1} of {n}"; lw = d.textlength(lab, font=fSmall); dw = n * 22
        d.text((W - M - lw - dw - 24, top + 2), lab, font=fSmall, fill=MUTED)
        for i in range(n):
            x = W - M - dw + i * 22 + 6; col = ACCENT if i == k else ((203, 213, 225) if i > k else (148, 163, 184)); d.ellipse([x, top + 12, x + 10, top + 22], fill=col)
        y = 190 if V else 150
        d.ellipse([M, y + 10, M + 60, y + 70], fill=ACCENT); s = str(k + 1); d.text((M + 30 - d.textlength(s, font=fBadge) / 2, y + 22), s, font=fBadge, fill=(255, 255, 255))
        for ln in title_l[k]: d.text((M + 84, y), ln, font=fTitle, fill=INK); y += 72 if V else 62
        y += 10
        for ln in sub_l[k]: d.text((M + 86, y), ln, font=fSub, fill=MUTED); y += 44 if V else 38
        return img
    CHROME = [chrome(k) for k in range(n)]

    def body_box(k): return STEPS[k]["body"]
    def zoom_for(k, box):
        bx0, by0, bx1, by1 = body_box(k); fit = min(CW / (bx1 - bx0), CH / (by1 - by0)); w = (box[2] - box[0]) * fit; h = (box[3] - box[1]) * fit
        lo, hi = (1.6, 2.8) if V else (1.4, 2.2)
        return min(hi, max(lo, min(0.4 * CW / w, 0.42 * CH / h)))
    def view(k, ts):
        bx0, by0, bx1, by1 = body_box(k); c0 = ((bx0 + bx1) / 2, (by0 + by1) / 2); T = STEPS[k]["targets"]
        keys = [(0.0, 1.0) + c0] + [(g["at"], zoom_for(k, g["box"]), (g["box"][0] + g["box"][2]) / 2, (g["box"][1] + g["box"][3]) / 2) for g in T]
        z, cx, cy = keys[0][1:]
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(keys, keys[1:]):
            if ts >= t1 - 0.8: z, cx, cy = z1, x1, y1; continue
            if ts >= t0: p = inout((ts - (t1 - 0.8)) / 0.8) if ts > t1 - 0.8 else 0; z, cx, cy = z0 + (z1 - z0) * p, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
        d = spans[k][1]
        if ts > d - 0.7: p = inout((ts - (d - 0.7)) / 0.7); z, cx, cy = z + (1 - z) * p, cx + (c0[0] - cx) * p, cy + (c0[1] - cy) * p
        return z, cx, cy
    def window(k, z, cx, cy):
        bx0, by0, bx1, by1 = body_box(k); bw, bh = bx1 - bx0, by1 - by0; ca = CW / CH
        vw, vh = (bw, bw / ca) if bw / bh > ca else (bh * ca, bh); vw /= z; vh /= z
        x0 = min(max(cx - vw / 2, bx0), bx1 - vw) if vw <= bw else (bx0 + bx1) / 2 - vw / 2
        y0 = min(max(cy - vh / 2, by0), by1 - vh) if vh <= bh else (by0 + by1) / 2 - vh / 2
        return x0, y0, vw, vh
    def body(k, x0, y0, vw, vh):
        src = frames[k]; c = Image.new("RGB", (int(round(vw)) + 2, int(round(vh)) + 2), PAPER); bx0, by0, bx1, by1 = body_box(k)
        sx0, sy0, sx1, sy1 = max(bx0, x0), max(by0, y0), min(bx1, x0 + vw), min(by1, y0 + vh)
        c.paste(src.crop((int(sx0), int(sy0), int(sx1), int(sy1))), (int(sx0 - x0), int(sy0 - y0)))
        return c.crop((0, 0, int(round(vw)), int(round(vh)))).resize((CW, CH), Image.BICUBIC)
    def arrow(scale):
        s = 2; pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
        im = Image.new("RGBA", (60 * s, 60 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.polygon([(x * s + 3, y * s + 4) for x, y in pts], fill=(0, 0, 0, 70))
        im = im.filter(ImageFilter.GaussianBlur(2)); d = ImageDraw.Draw(im)
        d.polygon([(x * s, y * s) for x, y in pts], fill=(17, 24, 39)); d.line([(x * s, y * s) for x, y in pts] + [(0, 0)], fill=(255, 255, 255), width=3)
        w = int(60 * scale * (1.25 if V else 1)); return im.resize((w, w), Image.LANCZOS)
    A1, A2 = arrow(1.0), arrow(0.86)
    def cursor(k, ts):
        bx0, by0, bx1, by1 = body_box(k); T = STEPS[k]["targets"]
        pts = [(0.0, ((bx0 + bx1) / 2 + 60, (by0 + by1) / 2 + 80))] + [(g["at"], ((g["box"][0] + g["box"][2]) / 2, (g["box"][1] + g["box"][3]) / 2)) for g in T]
        pos = pts[0][1]
        for (t0, p0), (t1, p1) in zip(pts, pts[1:]):
            if ts >= t1: pos = p1; continue
            if ts >= t1 - 0.9: q = inout((ts - (t1 - 0.9)) / 0.9); pos = (p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q - 30 * math.sin(math.pi * q))
            else: pos = p0
            break
        return pos
    def step_frame(k, ts):
        z, cx, cy = view(k, ts); x0, y0, vw, vh = window(k, z, cx, cy)
        img = CHROME[k].copy(); img.paste(body(k, x0, y0, vw, vh), (CARD[0], CARD[1]), mask); ImageDraw.Draw(img).rounded_rectangle(CARD, R, outline=LINE, width=2)
        px, py = cursor(k, ts); ox = CARD[0] + (px - x0) / vw * CW; oy = CARD[1] + (py - y0) / vh * CH; T = STEPS[k]["targets"]
        for g in T:
            a = ts - g["at"]
            if 0 <= a < 0.6:
                r = 10 + 44 * expo(a / 0.6); al = int(200 * (1 - a / 0.6)); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ov).ellipse([ox - r, oy - r, ox + r, oy + r], outline=ACCENT + (al,), width=5); img = Image.alpha_composite(img, ov)
        if CARD[0] - 20 < ox < CARD[2] and CARD[1] - 20 < oy < CARD[3]:
            img.alpha_composite(A2 if any(0 <= ts - g["at"] < 0.16 for g in T) else A1, (int(ox), int(oy)))
        return img
    fBig, fMid = font(84 if V else 96, "Bold"), font(34 if V else 36, "Regular")
    def card(lines, ts, check=False):
        img = BG.copy().convert("RGBA"); d = ImageDraw.Draw(img); p = expo(ts / 0.9)
        blocks = []
        for text, f, col, gap in lines: blocks += [(ln, f, col, gap) for ln in wrap(d, text, f, W - 2 * M)]
        y = H / 2 - sum(b[3] for b in blocks) / 2 + (60 if check else 0)
        if check:
            cy = y - 110; r = 56 * expo(ts / 0.6); d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], fill=ACCENT)
            if ts > 0.25: q = inout((ts - 0.25) / 0.4); pts = [(W / 2 - 24, cy + 2), (W / 2 - 6, cy + 20), (W / 2 + 26, cy - 18)]; d.line(pts[:2] if q < 0.4 else pts, fill=(255, 255, 255), width=10, joint="curve")
        for text, f, col, gap in blocks:
            tw = d.textlength(text, font=f); c = tuple(int(cc * p + bb * (1 - p)) for cc, bb in zip(col, BG_TOP))
            d.text(((W - tw) / 2, y + (1 - p) * 24), text, font=f, fill=c); y += gap
        return img
    INTRO_L = [(CFG["brand"], font(30, "Bold"), MUTED, 70), (heading(CFG["title"]), fBig, INK, 110 if V else 130), (CFG["subtitle"] + f"  ·  {n} steps", fMid, MUTED, 50)]
    OUT_L = [(heading(CFG["outro"]["title"]), font(72 if V else 80, "Bold"), INK, 100), (CFG["outro"]["line"], fMid, MUTED, 50)]

    slug = os.path.basename(TUT); out = os.path.join(TUT, "output", f"{slug}_{fmt}.mp4"); silent = out + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-tune", "animation", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for i in range(N):
        ts = i / FPS
        if ts < INTRO: img = card(INTRO_L, ts)
        elif ts < LAST:
            k = max(j for j in range(n) if spans[j][0] <= ts); tt = ts - spans[k][0]; img = step_frame(k, tt)
            if tt < 0.35: pv = card(INTRO_L, INTRO) if k == 0 else step_frame(k - 1, spans[k - 1][1]); img = Image.blend(pv, img, inout(tt / 0.35))
        else:
            tt = ts - LAST; img = card(OUT_L, tt, check=True)
            if tt < 0.35: img = Image.blend(step_frame(n - 1, spans[-1][1]), img, inout(tt / 0.35))
        if ts > END - 0.6: img = Image.blend(img, BG.convert("RGBA"), inout((ts - (END - 0.6)) / 0.6))
        enc.stdin.write(img.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", AUDIO, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(silent); print("wrote", out)

# ---------- audio (shared): voice on each step, click on each target, whoosh between steps, done chime, quiet music ----------
SR = 48000
def load(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "quiet", "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).reshape(-1, 2)
mix = np.zeros((int(END * SR) + SR, 2), np.float32)
def put(a, t, g): i = int(t * SR); a = a[: len(mix) - i] * 10 ** (g / 20); mix[i:i + len(a)] += a
for k in range(len(STEPS) + 1):
    a = load(os.path.join(TUT, "vo", f"line{k}.mp3")); a = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 0.1; put(a, 0.35 if k == 0 else spans[k - 1][0] + 0.25, 0)
L = STY["sfx_db"]
cues = [(spans[k][0] - 0.1, "whoosh") for k in range(len(STEPS))] + [(spans[k][0] + g["at"], "click") for k, s in enumerate(STEPS) for g in s["targets"]] + [(LAST + 0.05, "done")]
for t0, name in cues: a = load(SFX[name]); a = a / (np.abs(a).max() + 1e-9) * 0.25; put(a, t0, L[name])
mus = CFG.get("music") and os.path.join(HERE, "music", CFG["music"])
if mus and os.path.exists(mus):
    bed = load(mus)[: len(mix)]; bed = bed / (np.sqrt(np.mean(bed ** 2)) + 1e-9) * 0.1; idx = np.arange(len(bed))
    env = np.clip(idx / (1.5 * SR), 0, 1) * np.clip((END * SR - idx) / (1.5 * SR), 0, 1); mix[: len(bed)] += bed * 10 ** (STY["music_db"] / 20) * env[:, None]
elif mus: print("music file missing (run standard/fetch_assets.sh): rendering without music")
os.makedirs(os.path.join(TUT, "output"), exist_ok=True); AUDIO = os.path.join(TUT, "output", "mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"loudnorm=I={STY['lufs']}:TP=-1.5", "-ar", str(SR), AUDIO], input=mix[: int(END * SR)].tobytes(), check=True)
for f in (["16x9", "9x16"] if FMT == "both" else [FMT]): render(f)
os.remove(AUDIO)
json.dump(dict(intro=INTRO, steps=spans, end=END), open(os.path.join(TUT, "output", "timeline.json"), "w"), indent=1)
