#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生每篇的縮圖聯絡表（contact sheet），方便一次檢視所有照片並策展。
輸出到 tools/_work/contact_<essay>.jpg（已 gitignore）。標上 slug 編號。"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
WORK = ROOT / "tools" / "_work"
WORK.mkdir(parents=True, exist_ok=True)

COLS = 5
CELL = 320          # 每格寬
PAD = 10
LABEL_H = 26

def font(size):
    for name in ("msjh.ttc", "msyh.ttc", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def sheet(essay, items):
    thumbs = IMG / essay / "thumbs"
    n = len(items)
    rows = (n + COLS - 1) // COLS
    cellh = CELL + LABEL_H
    W = COLS * CELL + (COLS + 1) * PAD
    H = rows * cellh + (rows + 1) * PAD
    canvas = Image.new("RGB", (W, H), (28, 28, 26))
    d = ImageDraw.Draw(canvas)
    f = font(15)
    for i, it in enumerate(items):
        r, c = divmod(i, COLS)
        x = PAD + c * (CELL + PAD)
        y = PAD + r * (cellh + PAD)
        tp = thumbs / f"{it['slug']}-400.jpg"
        if tp.exists():
            im = Image.open(tp).convert("RGB")
            im.thumbnail((CELL, CELL))
            ox = x + (CELL - im.width) // 2
            oy = y + (CELL - im.height) // 2
            canvas.paste(im, (ox, oy))
        d.text((x + 2, y + CELL + 4), it["slug"], fill=(230, 220, 200), font=f)
    out = WORK / f"contact_{essay}.jpg"
    canvas.save(out, "JPEG", quality=85)
    print(f"{essay}: {n} 張 -> {out}")

def main():
    m = json.loads((IMG / "manifest.json").read_text(encoding="utf-8"))
    for essay, items in m.items():
        sheet(essay, items)

if __name__ == "__main__":
    main()
