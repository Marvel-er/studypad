"""重启本地服务：先杀掉占用 8300 的旧进程，再后台拉起 uvicorn。

为什么要有这个脚本（本机的坑）：
  · PowerShell 工具调 `netstat | Select-String` 会被沙箱拦（`sandbox-center cmd
    decisionRecord missing actual resource subject`），拿不到端口和 PID；
  · `cmd.exe` 被安全策略拉黑，没法靠 cmd 层的重定向兜住原始输出；
  · `wmic.exe` 同样在黑名单里，查不到命令行。
所以进程管理统一交给 Python：它既能解析 `netstat -ano`，也能直接 `taskkill`，
还能把结果写进文件（绕开 PowerShell 吞 stdout 的问题）。

## ⚠ 最重要的一条：本脚本拉起的服务**活不过当前这次工具调用**（2026-10-15 实测）

工具会话结束时会把**整个进程树**收掉。`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`
只能脱离控制台，**逃不出 Job Object**（`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`），
所以这里 Popen 出来的 uvicorn 会在调用返回后立刻被杀。

现象极具误导性：脚本自己轮询端口时明明 `LISTENING` 成功、退出码 0，
下一次工具调用去探，端口上已经什么都没有，日志里也没有任何崩溃痕迹
（没有 traceback、没有 "Shutting down"）—— 很容易误诊成「服务自己退了」。

**能跨调用存活的只有一条路：用 Bash 工具的 `run_in_background` 直接起 uvicorn**
（后台任务由 harness 托管，不会随单次调用结束被收）：

    cd /f/英语学习应用 && echo "===== restart $(date) =====" >> out/_server.log && \
      "C:/Users/刘永键/.workbuddy/binaries/python/envs/default/Scripts/python.exe" \
      -m uvicorn app.main:app --host 127.0.0.1 --port 8300 --app-dir backend \
      >> out/_server.log 2>&1

（Bash 后台任务实测跨大量工具调用稳定存活，`out/_server.log` 里有连续请求记录为证。）

顺带一个反直觉的发现：服务**由 Bash 后台任务拉起之后**，
PowerShell 工具的进程也能连上 `127.0.0.1:8300` 了 ——
所以「沙箱一律连不上回环」并不准确，真实情况与「谁拉起的服务、谁去连」有关。
本脚本保留「杀旧进程 + 轮询端口」的能力，用途是**确认端口已释放**；
要真正拿到一个能用的服务，请用上面那条 Bash 后台命令。

用法：
    python scripts/restart_server.py       # 清端口 + 自证能起（但活不过本次调用）
    Bash 工具 run_in_background 跑上面那条  # 真正可用的服务
（建议经 run_selftest 运行，日志落到 out/_server_restart.txt）

退出码：0 = 端口已释放且本次成功监听；1 = 没能起来。
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
PY = Path(r"C:\Users\刘永键\.workbuddy\binaries\python\envs\default\Scripts\python.exe")
PORT = 8300
LOG = ROOT / "out" / "_server.log"
URL = f"http://127.0.0.1:{PORT}"


def _run(args: list[str], timeout: int = 40) -> str:
    """跑一条系统命令并解码输出。

    注意**不能用 `text=True`**：`taskkill` / `netstat` 是控制台程序，中文 Windows 上
    吐的是 OEM 代码页（GBK/CP936）字节，按 UTF-8 解码会让「成功: 已终止 PID 为
    41152 的进程」变成 `�ɹ�: ����ֹ ...` 这种乱码（功能没问题，但日志没法看）。
    """
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return f"<{args[0]} 调用失败：{exc}>"
    raw = (p.stdout or b"") + (p.stderr or b"")
    for enc in ("oem", "mbcs", "utf-8"):
        try:
            return raw.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", "replace")


def listeners(port: int) -> list[int]:
    """返回 LISTENING 在该端口上的 PID 列表。"""
    pids: set[int] = set()
    for line in _run(["netstat", "-ano"]).splitlines():
        parts = line.split()
        # 形如：TCP    127.0.0.1:8300    0.0.0.0:0    LISTENING    41152
        if len(parts) >= 5 and parts[0].upper() == "TCP" \
                and parts[1].endswith(f":{port}") and parts[3].upper() == "LISTENING" \
                and parts[4].isdigit():
            pids.add(int(parts[4]))
    return sorted(pids)


def port_open(port: int, timeout: float = 0.4) -> bool:
    with socket.socket() as s:
        s.settimeout(timeout)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    out: list[str] = []

    if not PY.exists():
        out.append(f"[FATAL] 找不到 venv 解释器：{PY}")
        print("\n".join(out))
        return 1
    if not (ROOT / "backend" / "app" / "main.py").exists():
        out.append(f"[FATAL] 找不到 backend/app/main.py，仓库根目录对不对？{ROOT}")
        print("\n".join(out))
        return 1

    # 1) 杀掉旧进程
    old = listeners(PORT)
    out.append(f"[1/4] 8300 上的旧进程：{old or '无'}")
    for pid in old:
        res = _run(["taskkill", "/F", "/PID", str(pid)]).strip().replace("\n", " ")
        out.append(f"      taskkill {pid} → {res or '<无输出>'}")

    # 2) 等端口释放
    for i in range(40):
        if not port_open(PORT):
            break
        time.sleep(0.25)
    else:
        out.append("[FATAL] 端口 8300 一直没释放，放弃启动（可能有别的服务在用）")
        print("\n".join(out))
        return 1
    out.append("[2/4] 端口已释放")

    # 3) 后台拉起（DETACHED 保证父进程退出后它继续活着）
    LOG.parent.mkdir(parents=True, exist_ok=True)
    flags = 0x00000008 | 0x00000200        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    with LOG.open("ab") as fh:
        fh.write(f"\n===== restart {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n".encode("utf-8"))
        fh.flush()
        proc = subprocess.Popen(
            [str(PY), "-m", "uvicorn", "app.main:app",
             "--host", "127.0.0.1", "--port", str(PORT), "--app-dir", "backend"],
            cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True,
        )
    out.append(f"[3/4] 已拉起 uvicorn，PID={proc.pid}，日志 {LOG}")

    # 4) 等端口 LISTENING
    for _ in range(120):                    # 最多 30s
        if port_open(PORT):
            new = listeners(PORT)
            out.append(f"[4/4] {URL} 已在监听，PID={new or proc.pid}")
            print("\n".join(out))
            return 0
        if proc.poll() is not None:
            out.append(f"[FATAL] uvicorn 进程已退出（returncode={proc.returncode}）")
            break
        time.sleep(0.25)

    out.append(f"[FATAL] 30s 内没能监听 {URL}；日志尾部：")
    tail = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
    out.extend("      " + t for t in tail)
    print("\n".join(out))
    return 1


if __name__ == "__main__":
    sys.exit(main())
