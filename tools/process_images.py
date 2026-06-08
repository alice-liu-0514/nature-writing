#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process_images.py — 將原始 HEIC 照片轉成網頁最佳化的 WebP + JPEG。

功能：
  - HEIC -> 多尺寸 responsive WebP(主) + JPEG(fallback)
  - 烘焙旋轉 (exif_transpose)、P3 -> sRGB 色彩轉換
  - 完全剝除 EXIF/GPS/中繼資料（隱私要求）
  - 產生 400px 縮圖供相簿使用
  - 重新命名為語意 slug（peanut-01…），輸出 manifest.json

只讀原始檔、只寫 assets/img/ 下的輸出，不修改任何來源檔。
用法：  python tools/process_images.py            （轉全部）
        python tools/process_images.py peanut     （只轉某一篇）
"""
import io
import json
import sys
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps, ImageCms

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "assets" / "img"

# essay slug -> 原始資料夾
SOURCES = {
    "peanut": ROOT / "國文課" / "花生_第一次書寫",
    "fish":   ROOT / "國文課" / "魚_第二次書寫",
    "bamboo": ROOT / "國文課" / "竹子_第三次書寫",
}

WIDTHS = [640, 1024, 1600, 2048]   # responsive 長邊寬度（不放大）
THUMB = 400                         # 相簿縮圖長邊
WEBP_Q = 80
JPEG_Q = 82

_SRGB = ImageCms.createProfile("sRGB")


def to_srgb(im: Image.Image) -> Image.Image:
    """把帶有 ICC profile（多半是 Display P3）的影像轉成 sRGB；失敗則退回單純 RGB。"""
    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            return ImageCms.profileToProfile(im, src, _SRGB, outputMode="RGB")
        except Exception as e:  # profile 壞掉就退回
            print(f"    ! ICC 轉換失敗，退回 RGB：{e}")
    return im.convert("RGB")


def resized(im: Image.Image, long_edge: int) -> Image.Image:
    """等比縮放，使長邊 = long_edge（永不放大）。"""
    w, h = im.size
    if max(w, h) <= long_edge:
        return im.copy()
    r = im.copy()
    r.thumbnail((long_edge, long_edge), Image.LANCZOS)  # 同時限制兩邊 -> 長邊=long_edge
    return r


def save_pair(im: Image.Image, base: Path):
    """存成 .webp + .jpg，完全不帶任何中繼資料。"""
    base.parent.mkdir(parents=True, exist_ok=True)
    im.save(base.with_suffix(".webp"), "WEBP", quality=WEBP_Q, method=6)
    im.save(base.with_suffix(".jpg"), "JPEG", quality=JPEG_Q, optimize=True, progressive=True)


def assert_clean(path: Path):
    """確認輸出檔不含 EXIF（隱私把關）。"""
    with Image.open(path) as im:
        exif = im.getexif()
        assert len(exif) == 0, f"輸出 {path.name} 仍含 EXIF！"


def process_essay(slug: str, src_dir: Path) -> list[dict]:
    # Windows 檔案系統不分大小寫，用 suffix 比對並去重，避免同檔被處理兩次
    files = sorted(p for p in src_dir.iterdir()
                   if p.is_file() and p.suffix.lower() == ".heic")
    out_dir = OUT_ROOT / slug
    thumb_dir = out_dir / "thumbs"
    items = []
    print(f"\n=== {slug}：{len(files)} 張 ===")
    for i, f in enumerate(files, 1):
        name = f"{slug}-{i:02d}"
        with Image.open(f) as raw:
            im = ImageOps.exif_transpose(raw)   # 烘焙旋轉
            im = to_srgb(im)                     # P3 -> sRGB
        # 各 responsive 寬度
        gen_widths = []
        ref_w = ref_h = 0
        for w in WIDTHS:
            if w > max(im.size) and gen_widths:
                continue  # 不放大（且至少留一個）
            r = resized(im, w)
            save_pair(r, out_dir / f"{name}-{w}")
            gen_widths.append(w)
            ref_w, ref_h = r.size  # 記錄最大已產生變體尺寸
        # 縮圖
        t = resized(im, THUMB)
        save_pair(t, thumb_dir / f"{name}-{THUMB}")
        tw, th = t.size
        # 抽查 EXIF 乾淨
        assert_clean(out_dir / f"{name}-{gen_widths[-1]}.jpg")
        items.append({
            "slug": name,
            "w": ref_w, "h": ref_h,            # 最大變體尺寸（給 width/height 防 CLS）
            "ratio": round(ref_w / ref_h, 4) if ref_h else 1,
            "widths": gen_widths,
            "thumb": {"w": tw, "h": th},
            "alt": "",                          # 之後人工填寫（策展階段）
            "caption": "",
        })
        print(f"  [{i:02d}/{len(files)}] {f.name} -> {name}  ({ref_w}x{ref_h}, {len(gen_widths)} 尺寸)")
    return items


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    manifest_path = OUT_ROOT / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = {only: SOURCES[only]} if only else SOURCES
    for slug, src in targets.items():
        if not src.exists():
            print(f"!! 找不到來源資料夾：{src}")
            continue
        manifest[slug] = process_essay(slug, src)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(len(v) for v in manifest.values())
    print(f"\n完成。manifest.json 共 {total} 張，寫到 {manifest_path}")


if __name__ == "__main__":
    main()
