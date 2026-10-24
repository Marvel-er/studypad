"""
自检脚本运行器：把子脚本的 stdout/stderr 原样落盘，并把它抛出的异常也写进去。

**为什么需要它**：本机 PowerShell 工具会吞掉子进程的 stdout（`Write-Host`、表达式输出
都不回显），而用 `*>` / `| Out-String` 重定向又会把 UTF-8 字节按 GBK 解码，
日志里的中文变成 `缁冧範闆` 这种乱码，还会把 traceback 洗掉。
结果是「脚本失败了但什么都看不到」—— 上一轮就因此把一次自检崩溃误判成别的故障。

做法很直白：由 Python 自己接管 stdout/stderr 并以 UTF-8 写文件，绕开 PowerShell 的解码路径。

用法：
    python scripts/run_selftest.py scripts/test_translate.py out/_translate_test_run.txt
    python scripts/run_selftest.py scripts/run_pipeline.py out/_pipeline.txt cet4

（第 3 个参数起会原样转发给子脚本 —— 不转发的话，子脚本读到的 `sys.argv[1]`
  会是「本运行器的脚本路径」而不是它自己的参数，比如 `run_pipeline.py cet4`
  会把等级读成 `F:\\...\\run_pipeline.py`，再拼出一个非法文件名才报错，很难一眼看出原因。）
"""
from __future__ import annotations

import io
import runpy
import sys
import traceback
from pathlib import Path

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)

SCRIPT, RES = sys.argv[1], Path(sys.argv[2])
EXTRA = sys.argv[3:]

buf = io.StringIO()
_backup = sys.stdout, sys.stderr
sys.stdout = sys.stderr = buf          # 子脚本自己写的结果文件不受影响
code = 0
try:
    sys.argv = [SCRIPT] + EXTRA        # 子脚本要看到的是它自己的参数
    runpy.run_path(SCRIPT, run_name="__main__")
except SystemExit as e:
    code = e.code or 0
    buf.write(f"\n[子脚本退出码 {code!r}]\n")
except BaseException:  # noqa: BLE001 — 崩了才更要留下痕迹
    code = 1
    buf.write("\n[子脚本未捕获异常]\n" + traceback.format_exc())
finally:
    sys.stdout, sys.stderr = _backup

RES.parent.mkdir(parents=True, exist_ok=True)
RES.write_text(buf.getvalue(), encoding="utf-8")
sys.exit(0 if code in (0, None) else 1)
