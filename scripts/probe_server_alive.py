"""探针：确认服务在监听，并记录进程树关系（判断能否跨会话存活）。"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

out: list[str] = []


def listeners(port: int) -> list[int]:
    txt = subprocess.run(["netstat", "-ano"], capture_output=True, timeout=40)
    raw = txt.stdout or b""
    for enc in ("oem", "mbcs", "utf-8"):
        try:
            s = raw.decode(enc)
            break
        except (LookupError, UnicodeDecodeError):
            continue
    pids: set[int] = set()
    for line in s.splitlines():
        p = line.split()
        if len(p) >= 5 and p[0].upper() == "TCP" and p[1].endswith(f":{port}") \
                and p[3].upper() == "LISTENING" and p[4].isdigit():
            pids.add(int(p[4]))
    return sorted(pids)


pids = listeners(8300)
out.append(f"8300 LISTENING 的 PID = {pids or '无'}")

# 端口是否真的可连（本进程探测，走 socket 不走代理）
ok = False
try:
    with socket.create_connection(("127.0.0.1", 8300), timeout=2.0):
        ok = True
except OSError as e:
    out.append(f"connect 失败：{type(e).__name__}: {e}")
out.append(f"本进程能连上 8300 = {ok}")

out.append(f"本进程 PID = {os.getpid()}，父 PID = {os.getppid()}")

# uvicorn 进程的命令行，确认启动参数没走样
for pid in pids:
    ps = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "LIST"],
                        capture_output=True, timeout=40)
    raw = ps.stdout or b""
    for enc in ("oem", "mbcs", "utf-8"):
        try:
            s = raw.decode(enc)
            break
        except (LookupError, UnicodeDecodeError):
            continue
    out.append(f"--- PID {pid} tasklist ---")
    out.extend("    " + ln for ln in s.splitlines() if ln.strip())

print("\n".join(out))
