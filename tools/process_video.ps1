# process_video.ps1 — 將原始 MOV 影片轉成網頁最佳化的 MP4(H.264) + poster 影格。
#
#   - 長邊上限 1080px、CRF 23、preset slow、faststart（可邊下載邊播）
#   - -map_metadata -1 完全剝除 GPS/中繼資料（隱私要求）
#   - 自動套用 iPhone 旋轉、輸出偶數尺寸
#   - 擷取 0.5 秒處影格做 poster（poster 也不含中繼資料）
#   只讀原始 MOV、只寫 assets/video/ 下的輸出。
#
# 用法：  pwsh tools/process_video.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# --- 找 ffmpeg ---
$ffmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
if (-not $ffmpeg) {
    $cand = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cand) { $ffmpeg = $cand.FullName }
}
if (-not $ffmpeg) { throw "找不到 ffmpeg，請先 winget install Gyan.FFmpeg" }
Write-Host "使用 ffmpeg：$ffmpeg"

# essay slug -> 原始資料夾
$sources = [ordered]@{
    "fish"   = Join-Path $root "國文課\魚_第二次書寫"
    "bamboo" = Join-Path $root "國文課\竹子_第三次書寫"
}

# 長邊封頂 1080：landscape 限寬、portrait 限高，另一邊 -2（自動偶數）
$scale = "scale='if(gte(iw,ih),min(1080,iw),-2)':'if(gte(iw,ih),-2,min(1080,ih))'"

foreach ($slug in $sources.Keys) {
    $srcDir = $sources[$slug]
    if (-not (Test-Path $srcDir)) { Write-Host "!! 找不到 $srcDir"; continue }
    $movs = Get-ChildItem -Path $srcDir -Filter "*.MOV" | Sort-Object Name
    if ($movs.Count -eq 0) { continue }
    $outDir = Join-Path $root "assets\video\$slug"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-Host "`n=== $slug：$($movs.Count) 段 ==="
    $i = 0
    foreach ($mov in $movs) {
        $i++
        $name = "{0}-clip-{1:d2}" -f $slug, $i
        $mp4 = Join-Path $outDir "$name.mp4"
        $poster = Join-Path $outDir "$name-poster.jpg"

        & $ffmpeg -y -loglevel error -i $mov.FullName `
            -vf $scale -c:v libx264 -profile:v high -crf 23 -preset slow `
            -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k `
            -map_metadata -1 $mp4

        & $ffmpeg -y -loglevel error -ss 00:00:00.5 -i $mp4 -vframes 1 -q:v 3 `
            -map_metadata -1 $poster

        $mb = [math]::Round((Get-Item $mp4).Length / 1MB, 1)
        Write-Host ("  [{0:d2}/{1:d2}] {2} -> {3}  ({4} MB)" -f $i, $movs.Count, $mov.Name, $name, $mb)
    }
}
Write-Host "`n影片轉檔完成。"
