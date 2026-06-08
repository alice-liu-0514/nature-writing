#!/usr/bin/env python3
"""本機預覽用的多執行緒靜態伺服器（單執行緒 http.server 在瀏覽器並發連線下會卡住）。
用法： python tools/serve.py [port]"""
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8137


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print(f"serving on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
