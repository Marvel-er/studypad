"""探针：Markdown 里表格 / 代码块的位置是否被保留。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import parsers  # noqa: E402

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


MD = """# Title

First paragraph about productivity and corridors.

| Word | Meaning |
|---|---|
| endurance | the ability to last |
| afterthought | something considered later |

Second paragraph about documentation and prevention.

```python
print("code block")
```

Third paragraph about negotiation.
"""

blocks = parsers.parse_markdown(MD)
out.append("实际块顺序：")
for i, b in enumerate(blocks):
    out.append(f"  {i}. [{b.type:9}] order={b.order}  {b.text[:44]!r}")

types = [b.type for b in blocks]
out.append("")
out.append(f"  type 序列 = {types}")

# 期望顺序：title, paragraph, table, paragraph, code, paragraph
check(types[0] == "title", "标题在最前")
check("table" in types and "code" in types, "表格和代码块都在")
if "table" in types and "code" in types:
    ti, ci = types.index("table"), types.index("code")
    check(ti == 2, "表格排在第 3 块（紧跟第一段）", f"实际第 {ti} 块")
    check(ci == 4, "代码块排在第 5 块（跟在第二段后）", f"实际第 {ci} 块")

# 段落之间的相对顺序不能乱
WANT = ["First paragraph", "Second paragraph", "Third paragraph"]
paras = [b.text for b in blocks if b.type == "paragraph"]
out.append(f"  段落顺序 = {[p[:18] for p in paras]}")
check(len(paras) == 3, "三段正文都在", f"实际 {len(paras)} 段")
if len(paras) == 3:
    idx = []
    for p in paras:
        hit = [k for k, w in enumerate(WANT) if p.startswith(w)]
        idx.append(hit[0] if hit else -1)
    check(idx == sorted(idx) and -1 not in idx,
          "三段正文保持 First → Second → Third", f"相对位置 {idx}")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
