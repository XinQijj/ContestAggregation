# -*- coding: utf-8 -*-
"""本地/服务器运行：python serve.py [端口]  -> http://127.0.0.1:8770
后台每 12 小时自动运行 scripts/sync.py，网页刷新即可看到最新数据。"""
import sys as _s; _s.stdout.reconfigure(encoding="utf-8", errors="replace")
import functools, http.server, os, subprocess, sys, threading, time

ROOT = os.path.dirname(os.path.abspath(__file__))
_nums = [a for a in sys.argv[1:] if a.isdigit()]
PORT = int(_nums[0]) if _nums else int(os.environ.get("PORT", 8770))
INTERVAL = int(os.environ.get("SYNC_HOURS", 12)) * 3600


def sync_loop():
    while True:
        print("[sync] 开始同步…", flush=True)
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "sync.py")])
        time.sleep(INTERVAL)


if __name__ == "__main__":
    if "--no-sync" not in sys.argv:
        threading.Thread(target=sync_loop, daemon=True).start()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=os.path.join(ROOT, "web"))
    print(f"打开 http://127.0.0.1:{PORT}", flush=True)
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler).serve_forever()
