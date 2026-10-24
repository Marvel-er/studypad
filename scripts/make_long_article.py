"""
生成一份**长文布局夹具** samples/long_article.md。

为什么需要它：381 词的样例文章一页就装完了，**复现不出「整页留白 / 留白分页」**。
用户反馈的是打印/分页后的观感，那就必须有一篇真的会跨好几页的文章才能验。

内容为什么是重复的：这测的是**版式与分页行为**，不是内容质量。
把样例文章的段落重复若干遍、配上不同的小标题，块高度分布与真实长文一致，
而长度可以按需放大到刚好跨 3~5 页 —— 比去 vendor 里找真语料更可控。
（vendor 里的考研语料是带 `___` 的填空题，不是散文，反而会污染版式测试。）

用法：python scripts/run_selftest.py scripts/make_long_article.py out/_long.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "samples" / "sample_article.md"
DST = ROOT / "samples" / "long_article.md"

REPEAT = 5

raw = SRC.read_text(encoding="utf-8").strip()
# 拆成「标题 + 正文块」，好给每一遍换小标题
lines = raw.splitlines()
body = []
for ln in lines:
    s = ln.strip()
    if not s:
        continue
    if s.startswith("#"):
        continue                     # 丢掉原大标题，自己排
    body.append(s)

parts = ["# The Cost of Convenience（长文布局夹具）",
         "",
         "> 本文由 `samples/sample_article.md` 的段落重复 %d 遍拼成，"
         "用于验证跨页版式与「翻译失败」时的留白行为。" % REPEAT,
         "> 内容重复是**有意的**：这里测的是分页，不是内容。",
         ""]

for i in range(REPEAT):
    parts.append(f"## Part {i + 1}")
    parts.append("")
    parts.extend(body)
    parts.append("")

DST.write_text("\n".join(parts) + "\n", encoding="utf-8")

words = len(DST.read_text(encoding="utf-8").split())
lines_n = len(DST.read_text(encoding="utf-8").splitlines())
print("=" * 96)
print("长文布局夹具")
print("=" * 96)
print(f"  源：{SRC}（{len(raw.split())} 词）")
print(f"  目标：{DST}")
print(f"  重复 {REPEAT} 遍 → {lines_n} 行 / 约 {words} 词 / {DST.stat().st_size} 字节")
print()
print("断言：")
ok = True
for cond, label in [
    (DST.exists(), "夹具已生成"),
    (words > 1500, f"够长（约 {words} 词，可跨 3 页以上）"),
    (DST.read_text(encoding='utf-8').count("## Part") == REPEAT,
     f"含 {REPEAT} 个 Part 小标题（保证有分节，不是一整块）"),
]:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    ok = ok and cond

sys.exit(0 if ok else 1)
