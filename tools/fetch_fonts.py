#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自架「子集化」中文字型：
  1. 從 Fontsource 下載 Noto Serif/Sans TC 的繁中單檔 woff2（來源，暫存、不 commit）
  2. 用 fontTools pyftsubset 子集到站內實際用到的字 -> 極小 woff2
  3. 寫出 assets/fonts/fonts.css

所有 HTML/CSS 都建好後再跑一次即可補齊新字。需要網路（下載來源一次）。"""
import json, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
SRC = ROOT / "tools" / "_work" / "fontsrc"
FONTS.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121 Safari/537.36"

EXTRA = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    " ．。，、；：？！「」『』（）〈〉《》—–…‧·/※－"
    "過溪自然書寫三篇第一二三四五六七八九十次回望關於作者劉芸辰"
    "花生魚竹子記憶失去韌性靜觀神秘深度詼諧感官泥土水面風裡"
    "進入向下捲動跳至主要內容上張關閉放大播放影片相簿全部"
    "回到首頁文字與攝影前言概述種與沼澤泥巴路魚塘一池地新朋友"
    "層的世界餵颱之後採筍光線顏色鏡頭看不見補田阿嬤公爸哥"
)
# family key -> (fontsource id, [weights])
FAMILIES = {
    "noto-serif-tc": ("noto-serif-tc", [400, 700]),
    "noto-sans-tc":  ("noto-sans-tc", [300, 400, 500]),
}
LABEL = {"noto-serif-tc": "Noto Serif TC", "noto-sans-tc": "Noto Sans TC"}


def collect_chars():
    chars = set(EXTRA)
    for p in ROOT.glob("content/*.md"):
        chars |= set(p.read_text(encoding="utf-8"))
    for p in list(ROOT.glob("*.html")) + list(ROOT.glob("essays/*.html")):
        chars |= set(p.read_text(encoding="utf-8"))
    mp = ROOT / "assets" / "img" / "manifest.json"
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))
        for items in m.values():
            for it in items:
                chars |= set(it.get("alt", "")) | set(it.get("caption", ""))
    return {c for c in chars if ord(c) >= 0x20 and c != "　"}


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 10000:
        return
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())


def main():
    chars = collect_chars()
    charfile = SRC / "_chars.txt"
    charfile.write_text("".join(sorted(chars)), encoding="utf-8")
    print(f"獨特字元數：{len(chars)}")

    css = ["/* 自架字型（pyftsubset 子集化）— tools/fetch_fonts.py 產生，勿手改 */"]
    for key, (fid, weights) in FAMILIES.items():
        for w in weights:
            url = f"https://cdn.jsdelivr.net/fontsource/fonts/{fid}@latest/chinese-traditional-{w}-normal.woff2"
            src = SRC / f"{key}-{w}-src.woff2"
            download(url, src)
            out = FONTS / f"{key}-{w}.woff2"
            subprocess.run([
                sys.executable, "-m", "fontTools.subset", str(src),
                f"--text-file={charfile}",
                "--flavor=woff2",
                "--layout-features=*",
                "--no-hinting",
                "--desubroutinize",
                f"--output-file={out}",
            ], check=True)
            print(f"   {out.name}  {out.stat().st_size/1024:.1f} KB")
            css.append(
                f"@font-face{{font-family:'{LABEL[key]}';font-style:normal;"
                f"font-weight:{w};font-display:swap;"
                f"src:url('{out.name}') format('woff2');}}"
            )
    (FONTS / "fonts.css").write_text("\n".join(css) + "\n", encoding="utf-8")
    total = sum(f.stat().st_size for f in FONTS.glob("*.woff2"))
    print(f"\n完成。{len(list(FONTS.glob('*.woff2')))} 個 woff2，共 {total/1024:.0f} KB")


if __name__ == "__main__":
    main()
