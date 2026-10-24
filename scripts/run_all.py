"""
全量回归：一条命令跑完所有自检并汇总。

为什么要它：这些自检以前是一条条手工敲的（`out/_all_summary.txt` 就是那么来的），
于是「加了一个新自检但忘了跑」和「漏跑某一项却以为跑全了」都会发生。
一条命令 + 一张汇总表，才能真的说清「改动之后还剩什么没验」。

用法（**必须用装了依赖的那个解释器**，OCR 自检要 rapidocr 才能跑）：
    <venv>/Scripts/python.exe scripts/run_all.py

每一项都通过 `run_selftest.py` 起子进程跑，输出落在 out/_t_*.txt：
子进程隔离 + 自带 UTF-8 落盘，既不会被本机 PowerShell 的解码路径弄乱中文，
也不会让某一项的模块级副作用（比如临时 STUDYPAD_HOME）污染下一项。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "out"

sys.path.insert(0, str(SCRIPTS))
import _api  # noqa: E402

# 这两项是「打接口」的，但**不再因为探不到端口就跳过**。
# 本机工具进程的沙箱会把出网强制走代理（`http_proxy=127.0.0.1:<随机端口>`），
# 于是直连回环 TimeoutError、走代理 502 —— 以前这里就会判成
# SKIP（服务未启动），而服务其实好好地在 LISTENING，正是「以为跑全了」的假跳过。
# 现在由 scripts/_api.py 决定传输：能连真服务就打真服务，连不上退回进程内 ASGI。
REQUIRES_SERVICE: set[str] = set()

# 需要 Chrome 无头渲染的项（找不到 Chrome 就跳过，不算失败）。
# 这两项验的是「断言验不到的东西」：产物结构对了，不等于用户肉眼看到的对。
NEEDS_CHROME = {"probe_pixels.py", "probe_pagination.py"}
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# 有序链：后一项依赖前一项的产物，必须按顺序跑。
# 留白这个问题在**分页**里才现形，所以链路是
#   造长文夹具 → 生成「修复前/后」两份产物 → 量像素 → 导出 PDF 量分页留白。
CHAINS: list[tuple[str, list[tuple[str, list[str]]]]] = [
    ("留白视觉链（像素 + 真分页）", [
        ("make_long_article.py", []),
        ("make_trans_fail_demo.py", ["sample_article.md"]),
        ("make_trans_fail_demo.py", ["long_article.md"]),
        ("probe_pixels.py", []),
        ("probe_pagination.py", []),
    ]),
]

TESTS = [
    "test_parsers.py",
    "test_settings.py",
    "test_llm_config_api.py",
    "test_exam_points.py",
    "test_exam_points_api.py",
    "test_llm_chat.py",
    "test_translate.py",
    "test_translate_api.py",
    "test_translate_e2e.py",
    "test_progress.py",
    "check_render.py",
    "check_inline_js.py",
    "test_pages.py",
    "probe_css_check.py",
    "probe_kb_cols.py",
    "probe_theme.py",
    "probe_theme_render.py",
    "probe_compound.py",
    "probe_md_order.py",
    "probe_vocab_order.py",
    "probe_ws_offset.py",
    "probe_level_config.py",
    "probe_cache_guard.py",
    "probe_api_error.py",
    "probe_ecdict_integrated.py",
    "probe_irregular.py",
    "test_library.py",
    "test_library_api.py",
    "probe_library_e2e.py",
    "smoke_api.py",
    "verify_render_api.py",
    "probe_live_service.py",
]

def run_one(name: str, extra: list[str], tag: str = "") -> tuple[int, str]:
    """跑一项，返回 (退出码, 日志文件名)。"""
    script = SCRIPTS / name
    if not script.exists():
        return -1, ""
    log = OUT / f"_t_{tag or Path(name).stem}.txt"
    p = subprocess.run([sys.executable, str(SCRIPTS / "run_selftest.py"),
                        str(script), str(log)] + extra,
                       capture_output=True, text=True,
                       cwd=str(ROOT), timeout=1800)
    return p.returncode, log.name


def transport_label() -> str:
    """接口测试实际会走哪条传输 —— 打出来，避免「以为打了真服务」。"""
    target = (os.environ.get("STUDYPAD_API") or _api.DEFAULT_LIVE).rstrip("/")
    if os.environ.get("STUDYPAD_API"):
        return f"真服务 {target}（STUDYPAD_API 指定）"
    if _api.loopback_ok(target):
        return f"真服务 {target}"
    return "进程内 ASGI（沙箱挡掉回环）—— 验不出「服务挂着旧模块」"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    chrome = CHROME.exists()
    # 只在真的有项要求「必须起服务」时才去探端口。
    # （`live` 原来是在分支里直接引用的，一旦 REQUIRES_SERVICE 非空就会 NameError ——
    #   而那个集合现在是空的，所以这条错一直藏着没炸。）
    live = True
    if REQUIRES_SERVICE:
        live = _api.loopback_ok(
            (os.environ.get("STUDYPAD_API") or _api.DEFAULT_LIVE).rstrip("/"))
    rows: list[tuple[str, str]] = []
    failed: list[str] = []

    rows.append(("接口传输", transport_label()))
    rows.append(("", ""))

    for name in TESTS:
        script = SCRIPTS / name
        if not script.exists():
            rows.append((name, "MISSING"))
            failed.append(name)
            continue
        if name in REQUIRES_SERVICE and not live:
            rows.append((name, "SKIP（服务未启动，先跑 uvicorn 再来）"))
            continue
        if name in NEEDS_CHROME and not chrome:
            rows.append((name, "SKIP（找不到 Chrome，无法做视觉核验）"))
            continue

        code, logname = run_one(name, [])
        rows.append((name, f"exit={code}"))
        if code != 0:
            failed.append(name)
            log = OUT / logname
            tail = (log.read_text(encoding="utf-8", errors="replace")
                    if log.exists() else "")
            rows.append(("", "   失败详情（末 400 字）："
                         + tail.strip()[-400:].replace("\n", "\n    ")))

    # ---- 有序链 ----
    for chain, steps in CHAINS:
        if any(s in NEEDS_CHROME and not chrome for s, _a in steps):
            rows.append((chain, "SKIP（找不到 Chrome）"))
            continue
        bad = []
        for idx, (name, extra) in enumerate(steps, 1):
            if not (SCRIPTS / name).exists():
                bad.append(f"{name}(MISSING)")
                continue
            code, logname = run_one(name, extra, tag=f"chain{idx}_{Path(name).stem}")
            rows.append(("", f"    ↳ [{idx}/{len(steps)}] {name} "
                             f"{' '.join(extra)}  → exit={code}"))
            if code != 0:
                bad.append(name)
                log = OUT / logname
                tail = (log.read_text(encoding="utf-8", errors="replace")
                        if log.exists() else "")
                rows.append(("", "      失败详情（末 400 字）："
                             + tail.strip()[-400:].replace("\n", "\n      ")))
        rows.append((chain, "OK" if not bad else "FAIL：" + "、".join(bad)))
        if bad:
            failed.append(chain)

    total = len(TESTS) + len(CHAINS)
    lines = [f"{'测试':<26}结果", "-" * 72]
    for name, res in rows:
        if name:
            lines.append(f"{name:<26}{res}")
        else:
            lines.append(res)          # 失败详情是多行文本，不再补列宽
    lines.append("-" * 72)
    skipped = sum(1 for _n, r in rows if r.startswith("SKIP"))
    lines.append(f"合计 {total} 项：通过 {total - len(failed) - skipped}，"
                 f"失败 {len(failed)}，跳过 {skipped}")
    if failed:
        lines.append("失败：" + "、".join(failed))
    lines.append("明细日志：out/_t_*.txt；留白视觉链产物：out/visual/")
    lines.append("接口传输：能连上真服务就打真服务；沙箱挡回环时退回进程内 ASGI"
                 "（此时验不出「服务挂着旧模块」，改完代码记得 restart_server.py）")

    text = "\n".join(lines)
    (OUT / "_all_summary.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
