import sys
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, parsers, analyzer  # noqa: E402

blocks, _ = parsers.parse("sample_article.md", (ROOT / "samples" / "sample_article.md").read_bytes())
parsed = annotator.analyze_document([b.as_dict() for b in blocks], "cet4")

for t in ("word_highlight", "word_circle", "word_rare"):
    items = [c for c in parsed["candidates"] if c["type"] == t]
    items.sort(key=lambda c: -c["confidence"])
    lines = [f"=== {t}  候选 {len(items)} 个，按分数前 25 ==="]
    for c in items[:25]:
        lines.append(f'  {c["confidence"]:.3f}  {c["surface"]:16s} mask={c["payload"]["levels"]:2d} '
                     f'pop={analyzer.popcount(c["payload"]["levels"])} kind={c["payload"]["kind"]}')
    print("\n".join(lines))

# 看看 different / heavily 的 mask
for w in ["different", "heavily", "frequently", "millions", "employees", "becomes", "probably"]:
    t = analyzer.classify_word(w, "cet4", w, 0)
    print(f"MASK {w:12s} mask={t.mask:2d} kind={t.kind} score={analyzer.word_score(t.kind, t.mask, w):.3f}")
