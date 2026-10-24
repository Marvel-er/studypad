"""验「真服务上跑的确实是新代码」——进程内 ASGI 那条路恰恰验不出这件事。

背景：`run_all.py` 的接口测试在本机沙箱下走的是**进程内 ASGI**，它直接调
`app.main:app`，永远是「新代码」。所以「服务还挂着旧模块」这种最常见的假成功，
只有这一条探针能查：向真服务发一次标注，看返回的 HTML 里有没有本轮的特征串。

用法：python scripts/run_selftest.py scripts/probe_live_service.py out/_live_service.txt
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")

sys.path.insert(0, str(ROOT / "scripts"))
import _api  # noqa: E402

C = _api.client()
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


print("=" * 88)
print("真服务代码新鲜度探针")
print(f"传输方式：{_api.MODE}")
print("=" * 88)

r = C.post("http://127.0.0.1:8300/api/analyze-text", timeout=120,
           json={"text": TEXT, "level_id": "cet4", "title": "live-check", "no_save": True,
                 "use_llm": False, "translate": False, "trans_mode": "sentence"})
html = r.json().get("html") or ""
print(f"  返回 html {len(html)} 字节")

# 本轮的标志性改动：CSS 变量全部加 --sp- 前缀 + 荧光笔不再依赖变量
check("--sp-hl:#FFE066" in html, "真服务返回的产物带 --sp- 前缀变量（本轮改动）")
# 注意断言要按**整条规则**写，不能写一半：产物里 `.w-target` 还有一条
# `print-color-adjust` 的规则，所以按 `\.w-target\{[^}]*\}` 匹配会截断。
# 这里直接查那条渐变本身 —— 它才是「荧光笔会不会变黑」的决定性证据。
check("linear-gradient(180deg,rgba(255,224,102,0) 52%,#FFE066 52%,"
      "#FFE066 92%,rgba(255,224,102,0) 92%)" in html,
      "荧光笔是字面量 + 同色族零透明（不是 var() 也不是 transparent）")

# 反向确认：旧写法一个都不许有
bad = []
if re.search(r"var\(--(?!sp-)", html):
    bad.append("存在未加前缀的 var() 引用")
if re.search(r"gradient\([^;{}\"']*\btransparent\b", html):
    bad.append("渐变里用了 transparent")
check(not bad, "产物里没有旧写法的痕迹", "；".join(bad) if bad else "干净")

print()
print("=" * 88)
print(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("=" * 88)
sys.exit(1 if fails else 0)
