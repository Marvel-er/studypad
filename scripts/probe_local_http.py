"""探针：从当前进程能否连上本机 8300。"""
from __future__ import annotations

import socket
import sys
import urllib.request

out: list[str] = []
out.append(f"python = {sys.executable}")
for host, port in [("127.0.0.1", 8300), ("localhost", 8300), ("0.0.0.0", 8300)]:
    try:
        with socket.create_connection((host, port), timeout=2.0):
            out.append(f"connect {host}:{port} → OK")
    except OSError as exc:
        out.append(f"connect {host}:{port} → FAIL {type(exc).__name__}: {exc}")

for url in ["http://127.0.0.1:8300/api/levels", "http://localhost:8300/api/levels"]:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            out.append(f"GET {url} → {r.status}, {len(r.read())} bytes")
    except Exception as exc:  # noqa: BLE001
        out.append(f"GET {url} → FAIL {type(exc).__name__}: {exc}")

# 顺便看有没有代理环境变量在捣乱（urllib 会读 http_proxy）
import os  # noqa: E402
for k in ("http_proxy", "https_proxy", "no_proxy", "NO_PROXY", "HTTP_PROXY", "HTTPS_PROXY"):
    v = os.environ.get(k)
    if v:
        out.append(f"env {k}={v}")

print("\n".join(out))
