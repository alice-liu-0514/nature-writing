# 過溪 ｜ 自然書寫作品集

劉芸辰的三篇國文書寫，圍繞同一片田地「過溪」（大肚溪出海口旁的家族菜田）：
**花生**（種花生與泥沼）、**魚**（蓄水池的吳郭魚）、**竹子**（颱風後的竹林與阿公的記憶）。

純靜態網站（vanilla HTML / CSS / JS，零建置），可直接部署到 GitHub Pages。

## 線上瀏覽

部署後即為 `https://<使用者名稱>.github.io/<repo>/`（或 user site 根網域）。

## 本機預覽

需用 HTTP 伺服器（ES modules 與 `fetch` 不能在 `file://` 下運作）：

```bash
python tools/serve.py 8137
# 開啟 http://127.0.0.1:8137/
```

## 結構

```
index.html                 封面 + 三篇導覽
essays/{peanut,fish,bamboo}.html
assets/css/{tokens,base,components,essay}.css   設計系統（tokens.css 為唯一色彩/字級來源）
assets/js/{main,reveal,lightbox,video}.js       漸進增強：scroll-reveal、相簿燈箱、影片
assets/img/<篇>/…  + manifest.json              最佳化後的照片（WebP+JPEG，多尺寸）
assets/video/<篇>/…                             最佳化後的影片（MP4 + poster）
assets/fonts/                                    子集化的 Noto Serif/Sans TC（自架）
content/*.md                                     文稿（建置素材）
design/style-brief.md                            設計風格 brief
tools/                                           一次性的素材處理腳本
```

## 重新產生素材（需要原始檔，原始檔不在 repo 內）

原始 HEIC/MOV 放在 `國文課/`（已 gitignore）。處理腳本：

```bash
pip install pillow-heif fonttools brotli       # 一次
winget install Gyan.FFmpeg                       # 一次（影片用）

python tools/process_images.py     # HEIC → 多尺寸 WebP/JPEG + 縮圖 + 剝 EXIF + manifest
pwsh   tools/process_video.ps1     # MOV  → MP4 + poster
python tools/fetch_fonts.py        # 依站內實際用字，子集化中文字型（需網路下載來源一次）
```

> `tools/fetch_fonts.py` 會掃描所有 HTML/MD/manifest 的用字後再子集化字型；
> 若日後新增文字，重跑一次即可補齊字。

## 部署到 GitHub Pages

```bash
git add .
git status        # 確認沒有 HEIC / MOV / docx 被加入
git commit -m "..."
# 在 GitHub 建立 repo 後：
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

到 GitHub repo → **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/ (root)`**，
等待綠燈後即可瀏覽。已含 `.nojekyll`，無需 Jekyll 建置。

## 隱私

- 原始照片/影片含 GPS，轉檔時已**完全剝除 EXIF/中繼資料**。
- 原始 HEIC/MOV 與含學號的 `.docx` 一律 `.gitignore`，**不會進 repo、不會公開**。

---

文字與攝影：劉芸辰
