"""探针：生词表顺序到底是不是「文章出现顺序」。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup, parsers  # noqa: E402

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# 夹具：直接用样例文章的真实段落，按段拆成多个 block。
# 每个 block 的 start 偏移都从 0 起算，所以「只按 start 排序」必然分不清先后。
MD = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
PARAS = [p.strip() for p in MD.split("\n\n") if p.strip() and not p.strip().startswith("#")]
BLOCKS = [{"id": f"b{i}", "type": "paragraph", "order": i, "text": t,
           "page": None, "level": None, "bbox": None, "meta": {}, "annotations": []}
          for i, t in enumerate(PARAS)]

parsed = annotator.analyze_document([dict(b) for b in BLOCKS], "cet4")
hb = markup.build(parsed, "cet4")
vocab = hb["vocab"]

out.append(f"夹具：{len(BLOCKS)} 个 block，生词表 {len(vocab)} 词")
out.append("生词表实际顺序：")
for i, v in enumerate(vocab):
    out.append(f"  {i}. {v['surface']:<16} kind={v['kind']}")

# 文章顺序：b1 的词（unprecedented / bewildered / negotiation）都该早于 b2 的词
order_in_text = []
for b in BLOCKS:
    for v in vocab:
        if v["surface"].lower() in b["text"].lower():
            order_in_text.append((b["id"], v["surface"]))

b1_pos = [i for i, v in enumerate(vocab) if v["surface"].lower() in BLOCKS[0]["text"].lower()]
b2_pos = [i for i, v in enumerate(vocab) if v["surface"].lower() in BLOCKS[1]["text"].lower()]
b3_pos = [i for i, v in enumerate(vocab) if v["surface"].lower() in BLOCKS[2]["text"].lower()]
out.append("")
out.append(f"  block1 的词在生词表中的下标：{b1_pos}")
out.append(f"  block2 的词在生词表中的下标：{b2_pos}")
out.append(f"  block3 的词在生词表中的下标：{b3_pos}")

if b1_pos and b2_pos:
    check(max(b1_pos) < min(b2_pos),
          "block1 的词全部排在 block2 之前（文章顺序）",
          f"b1={b1_pos} b2={b2_pos}")
if b2_pos and b3_pos:
    check(max(b2_pos) < min(b3_pos),
          "block2 的词全部排在 block3 之前（文章顺序）",
          f"b2={b2_pos} b3={b3_pos}")

# 每个 block 内部也该按出现顺序
for b in BLOCKS:
    pos = [i for i, v in enumerate(vocab) if v["surface"].lower() in b["text"].lower()]
    if len(pos) >= 2:
        first_word = next(v["surface"] for v in vocab if v["surface"].lower() in b["text"].lower())
        out.append(f"  {b['id']} 内首个词 = {first_word}，下标 {pos}")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
