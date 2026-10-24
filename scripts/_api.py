"""统一的 API 客户端：优先真服务，连不上就退回**进程内 ASGI**。

为什么要写这个（本机的沙箱限制，会反复咬人）：

本机工具进程的出网被**强制走代理** —— 环境里被塞了
`http_proxy=http://127.0.0.1:<随机端口>`。于是打本机 8300 时两条路都不通：

    connect 127.0.0.1:8300  →  TimeoutError（沙箱拦掉直连回环）
    urllib / httpx 默认      →  502 Bad Gateway（trust_env=True 走了代理，代理到不了回环）

`run_all.py` 探不到端口就把 `smoke_api.py` / `verify_render_api.py` 判成
**SKIP（服务未启动）** —— 可服务明明好好地在 8300 上 LISTENING。
「端口通不了所以跳过」这种假跳过，正是本项目最想避免的「以为跑全了」。

正解不是关掉沙箱，而是**根本不开 socket**：用 httpx 的 ASGI 传输
（`fastapi.testclient.TestClient`，`test_llm_config_api.py` 早就这么用了）
在本进程内直接调 `app.main:app`。

用法：

    import _api
    C = _api.client()
    r = C.get(f"{BASE}/api/levels")

**代价要写清楚**：进程内这条路验不出「服务还挂着旧模块」——
所以 `client()` 顺便把实际走的路记进 `_api.MODE`，调用方应当打印出来。
想看真服务就设 `STUDYPAD_API=http://127.0.0.1:8300`（或别的地址）强制执行。
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_LIVE = "http://127.0.0.1:8300"

MODE = ""          # 实际用的传输方式，调用方读它并打印


def _split_base(base: str) -> tuple[str, int]:
    rest = base.split("://", 1)[-1]
    hostport = rest.split("/", 1)[0]
    host, _, port = hostport.partition(":")
    return host or "127.0.0.1", int(port or "80")


def loopback_ok(base: str, timeout: float = 1.0) -> bool:
    """真的能 TCP 连上才算「服务在跑」。沙箱下这里通常是静默超时。"""
    host, port = _split_base(base)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _wrap(raw):
    """统一 `get` / `post` 的调用姿势，把两条传输的差异藏起来。

    · 真服务（httpx.Client）：收 `timeout`；
    · 进程内（TestClient）：不收 `timeout`，传了会刷 StarletteDeprecationWarning。
    所以这里对 ASGI 客户端把 `timeout` 扔掉，调用方两种情况下写法完全一致。
    """
    is_asgi = "ASGI" in MODE

    def _drop(kwargs: dict) -> dict:
        if is_asgi:
            kwargs.pop("timeout", None)
        return kwargs

    class _Client:
        def get(self, url, **kwargs):
            return raw.get(url, **_drop(kwargs))

        def post(self, url, **kwargs):
            return raw.post(url, **_drop(kwargs))

        def __getattr__(self, name):
            return getattr(raw, name)

    return _Client()


def client(timeout: float = 900.0):
    """返回一个已经配好传输方式的客户端（带 get / post，`timeout` 可不传）。"""
    global MODE
    live = (os.environ.get("STUDYPAD_API") or DEFAULT_LIVE).rstrip("/")
    forced = bool(os.environ.get("STUDYPAD_API"))

    if forced or loopback_ok(live):
        MODE = f"真服务 {live}" + ("（STUDYPAD_API 指定）" if forced else "")
        return _wrap(httpx.Client(base_url=live, timeout=timeout, trust_env=False))

    MODE = ("进程内 ASGI（沙箱挡掉回环：直连 TimeoutError、走代理 502）"
            "—— 这条路验不出「服务还挂着旧模块」")
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))
    import warnings  # noqa: PLC0415

    # 本机装的是 httpx 1.x + starlette 的 TestClient，组合起来会刷
    # StarletteDeprecationWarning；这不是代码问题，别让它污染日志。
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient   # noqa: PLC0415
        from app.main import app                    # noqa: PLC0415
        return _wrap(TestClient(app))
