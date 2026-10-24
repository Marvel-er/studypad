"""
并发自检：证明「慢请求不会冻住整个服务」。

## 为什么必须有这一项

FastAPI 的一个经典陷阱：端点写成 `async def`，但函数体里做的是**同步阻塞**调用
（httpx 最长 90 秒、OCR 推理数秒、词法分析 CPU 密集）。
FastAPI 对 `async def` 的处理是**直接在事件循环上跑**，不是丢进线程池 ——
于是这一个请求会把整个服务卡住：其它所有请求（包括首页）全部排队等待。

本项目就踩过：有人在页面上点了一次「测试连接」，服务从此再不响应任何请求，
而进程还好好地在 8300 上 LISTENING，日志里也看不出任何异常
（最后两条恰好是 `POST /api/llm/test` → `POST /api/llm/config`）。
**"端口通、接口不通"最容易误诊成网络问题，所以这里用两层断言把它钉死。**

## 两层断言

1. **静态**：遍历路由表，断言没有任何端点是协程函数 —— 一眼可查、零成本；
2. **动态**：起一个「只收不回」的假上游，真发一个会长时间悬挂的请求，
   同时打普通接口，断言它们仍然在毫秒级返回。
   只做第 1 层不够 —— 万一以后有人把阻塞调用搬进了依赖项或中间件呢。

需要先启动服务（默认读 8300，可用 `STUDYPAD_SMOKE_BASE` 覆盖）。
"""
from __future__ import annotations

import inspect
import os
import socket
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

BASE = os.environ.get("STUDYPAD_SMOKE_BASE", "http://127.0.0.1:8300")

LOG: list[str] = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


# =====================================================================
# 假上游：接受连接、收下请求，然后一直不回应
# =====================================================================

class Staller:
    def __init__(self) -> None:
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.port = self.sock.getsockname()[1]
        self.stop = False
        self.conns: list[socket.socket] = []
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        self.sock.settimeout(0.5)
        while not self.stop:
            try:
                c, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self.conns.append(c)
            threading.Thread(target=self._hold, args=(c,), daemon=True).start()

    def _hold(self, c: socket.socket) -> None:
        """收下请求，然后装死 —— 让客户端一直等它的读超时。"""
        c.settimeout(0.5)
        try:
            c.recv(65536)
            while not self.stop:
                time.sleep(0.2)
        except OSError:
            pass

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    def close(self) -> None:
        self.stop = True
        for c in self.conns:
            try:
                c.close()
            except OSError:
                pass
        try:
            self.sock.close()
        except OSError:
            pass


def main() -> None:
    import httpx
    from app.main import app

    # ---------------- 1. 静态：路由表里不许有协程端点 ----------------
    # 要排除 FastAPI 自带的 /docs、/redoc、/openapi.json —— 那些本来就是协程，
    # 而且不归我们管。按「端点定义在哪个模块」判断，比按路径黑名单更稳。
    def is_framework(r) -> bool:
        mod = (getattr(r.endpoint, "__module__", "") or "")
        return mod.startswith(("fastapi", "starlette"))

    routes = [r for r in app.routes
              if hasattr(r, "endpoint") and hasattr(r, "path")]
    ours = [r for r in routes if not is_framework(r)]
    skipped = len(routes) - len(ours)
    async_eps = sorted(
        f"{getattr(r, 'path', '?')} ({getattr(r.endpoint, '__name__', '?')})"
        for r in ours if inspect.iscoroutinefunction(r.endpoint)
    )
    check("★ 自有端点里没有任何 async def（阻塞调用会冻住事件循环）",
          not async_eps,
          "、".join(async_eps) if async_eps
          else f"自有 {len(ours)} 条（另跳过框架自带 {skipped} 条）")
    for r in ours:
        name = getattr(r.endpoint, "__name__", "")
        LOG.append(f"      {getattr(r, 'path', '?'):<38} {name}")

    # ---------------- 2. 服务可达 ----------------
    try:
        r = httpx.get(f"{BASE}/api/levels", timeout=8.0, trust_env=False)
        up = r.status_code == 200
    except Exception as e:  # noqa: BLE001
        up = False
        LOG.append(f"      {type(e).__name__}: {e}")
    check("服务可达（GET /api/levels 200）", up)
    if not up:
        return

    # ---------------- 3. 动态：慢请求在飞时，普通接口必须不被拖慢 ----------------
    st = Staller()
    try:
        # 基线：没有任何慢请求时的单次延迟
        t0 = time.time()
        httpx.get(f"{BASE}/api/levels", timeout=8.0, trust_env=False)
        baseline = time.time() - t0

        slow_done = threading.Event()
        slow_result: list[str] = []

        def fire_slow() -> None:
            try:
                # 这个请求会在假上游那里一直挂到读超时（90 秒）
                httpx.post(f"{BASE}/api/llm/test", timeout=30.0, trust_env=False,
                           json={"provider": "custom", "base_url": st.base_url,
                                 "model": "staller", "api_key": "sk-x"})
                slow_result.append("正常返回")
            except Exception as e:  # noqa: BLE001
                slow_result.append(type(e).__name__)
            finally:
                slow_done.set()

        t = threading.Thread(target=fire_slow, daemon=True)
        t.start()
        time.sleep(2.0)                       # 确保它已经在飞（并且在等模型响应）

        still_flying = not slow_done.is_set()
        check("慢请求确实正在飞行中（没被提前结束）", still_flying,
              "已完成" if not still_flying else "在飞")

        lat: list[float] = []
        codes: list[int] = []
        for path in ("/api/levels", "/api/translate/status", "/api/exam-points",
                     "/", "/api/levels", "/api/levels"):
            t0 = time.time()
            try:
                rr = httpx.get(f"{BASE}{path}", timeout=6.0, trust_env=False)
                codes.append(rr.status_code)
            except Exception as e:  # noqa: BLE001
                codes.append(0)
                LOG.append(f"      {path} 失败：{type(e).__name__}")
            lat.append(time.time() - t0)

        worst = max(lat)
        LOG.append(f"      基线（无慢请求）={baseline * 1000:.0f} ms；"
                   f"慢请求在飞时 6 次探测={[f'{x * 1000:.0f}ms' for x in lat]}")
        check("★ 慢请求在飞时所有接口仍然全部 200", all(c == 200 for c in codes), str(codes))
        check("★ 慢请求在飞时延迟没有被拖到秒级（事件循环未被阻塞）",
              worst < 1.0, f"最慢 {worst * 1000:.0f} ms（基线 {baseline * 1000:.0f} ms）")
        # 如果事件循环被阻塞，这里会退化成接近慢请求的等待时长（数十秒），
        # 所以「最慢 < 1 秒」是真正的判据，单纯 200 不能说明问题。

        # ---------------- 4. 慢请求最终要能自己收场（不能永久占着线程） ----------------
        st.close()
        t.join(timeout=15)
        check("慢上游断开后，那个请求能收尾（不无限挂住）", slow_done.is_set(),
              str(slow_result or "仍在等待"))
        if slow_done.is_set():
            LOG.append(f"      慢请求结局：{slow_result}")
    finally:
        st.close()


def _report(tb: str = "") -> None:
    if tb:
        LOG.append("*** 自检中途异常终止 ***")
        LOG.append(tb)
    LOG.append("")
    LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
    (ROOT / "out" / "_concurrency_test.txt").write_text("\n".join(LOG), encoding="utf-8")
    print(f"PASS={PASS} FAIL={FAIL}")


if __name__ == "__main__":
    tb = ""
    try:
        main()
    except BaseException:  # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
    _report(tb)
    sys.exit(1 if (FAIL or tb) else 0)
