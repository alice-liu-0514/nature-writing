#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生一致的 <picture> 標記（WebP + JPEG，含 srcset/sizes/尺寸）。
一次印出文章頁要用的精選圖標記，貼進 HTML 即可。"""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "assets" / "img" / "manifest.json").read_text(encoding="utf-8"))
BY = {it["slug"]: (essay, it) for essay, items in M.items() for it in items}

def pic(slug, sizes, cls="", prefix="../", loading="lazy", fp=None, figclass=None, cap=None):
    essay, it = BY[slug]
    base = f"{prefix}assets/img/{essay}/{slug}"
    widths = it["widths"]
    webp = ", ".join(f"{base}-{w}.webp {w}w" for w in widths)
    jpg = ", ".join(f"{base}-{w}.jpg {w}w" for w in widths)
    default = f"{base}-1024.jpg" if 1024 in widths else f"{base}-{widths[-1]}.jpg"
    fpa = f' fetchpriority="{fp}"' if fp else ""
    cla = f' class="{cls}"' if cls else ""
    img = (f'<img{cla} src="{default}" srcset="{jpg}" sizes="{sizes}" '
           f'width="{it["w"]}" height="{it["h"]}" loading="{loading}" decoding="async" '
           f'alt="{it["alt"]}">')
    pict = f'<picture>\n    <source type="image/webp" srcset="{webp}" sizes="{sizes}">\n    {img}\n  </picture>'
    if figclass is not None:
        caphtml = f"\n  <figcaption>{cap}</figcaption>" if cap else ""
        fc = f' class="{figclass}"' if figclass else ""
        return f'<figure{fc} data-lightbox="{slug}">\n  {pict}{caphtml}\n</figure>'
    return pict

if __name__ == "__main__":
    # 印出每篇精選圖的標記（prefix='../' 給 essays/ 底下的頁面）
    specs = {
      "── PEANUT hero (full-bleed, eager) ──":
        [("peanut-01", "100vw", "", "eager", "high", "hero-figure bleed", None)],
      "── PEANUT inline ──": [
        ("peanut-06", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-right", "過溪的菜田一隅"),
        ("peanut-09", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-left", None),
        ("peanut-16", "100vw", "", "lazy", None, "bleed", None),
        ("peanut-25", "(max-width:700px) 92vw, 42rem", "", "lazy", None, "", "一週後，種下的花生發了芽"),
      ],
      "── FISH hero ──":
        [("fish-10", "100vw", "", "eager", "high", "hero-figure bleed", None)],
      "── FISH inline ──": [
        ("fish-01", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-right", "蓄水池上的木板，只留一扇窺看水下的小窗"),
        ("fish-02", "100vw", "", "lazy", None, "bleed", None),
        ("fish-06", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-left", "丟進池裡的地瓜葉，是魚的食物"),
      ],
      "── BAMBOO hero ──":
        [("bamboo-25", "100vw", "", "eager", "high", "hero-figure bleed", None)],
      "── BAMBOO inline ──": [
        ("bamboo-17", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-right", "從竹林下仰望交錯的竹葉"),
        ("bamboo-10", "100vw", "", "lazy", None, "bleed", "颱風過後，滿地枯黃的竹葉"),
        ("bamboo-06", "(max-width:1000px) 92vw, 58rem", "", "lazy", None, "offset-left", "田的另一頭，爸爸種的年輕竹子"),
        ("bamboo-22", "(max-width:700px) 92vw, 42rem", "", "lazy", None, "", "竹子根部冒出的新筍，雨後春筍具象化了"),
      ],
    }
    for label, items in specs.items():
        print("\n" + label)
        for a in items:
            print(pic(*[a[0], a[1]], cls=a[2], loading=a[3], fp=a[4], figclass=a[5], cap=a[6]))
