#!/usr/bin/env python3
"""本機預覽用的多執行緒靜態伺服器（單執行緒 http.server 在瀏覽器並發連線下會卡住）。
支援 HTTP Range 請求（影片 <video> 播放需要；GitHub Pages 線上亦支援）。
用法： python tools/serve.py [port]"""
import os, re, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8137


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        # 無 Range 或目標為目錄 -> 走預設（並補上 Accept-Ranges 提示）
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or os.path.isdir(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)\s*$", rng.strip())
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        try:
            size = os.fstat(f.fileno()).st_size
            if m.group(1) == "":                       # 後綴範圍：最後 N 個 byte
                length = min(int(m.group(2)), size)
                start = size - length
            else:
                start = int(m.group(1))
                end = min(int(m.group(2)) if m.group(2) else size - 1, size - 1)
                if start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    return None
                length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{start + length - 1}/{size}")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            if self.command == "HEAD":
                return None
            f.seek(start)
            remaining = length
            while remaining > 0:
                buf = f.read(min(65536, remaining))
                if not buf:
                    break
                self.wfile.write(buf)
                remaining -= len(buf)
            return None
        finally:
            f.close()


if __name__ == "__main__":
    print(f"serving on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
