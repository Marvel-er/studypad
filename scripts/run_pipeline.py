"""
命令行跑通整条链路，无需启动 Web 服务。

用法：
    python scripts/run_pipeline.py [level_id] [输入文件]
默认：cet4 + samples/sample_article.md
产物：out/handbook-<level>.html
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup, parsers, render  # noqa: E402

level_id = sys.argv[1] if len(sys.argv) > 1 else "cet4"
src = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "samples" / "sample_article.md"

raw = src.read_bytes()
blocks, info = parsers.parse(src.name, raw)

lines = []
lines.append(f"源文件   : {src.name}  ({len(raw)} bytes)")
lines.append(f"解析引擎 : {info.get('engine')}  区块数={len(blocks)}")

parsed = annotator.analyze_document([b.as_dict() for b in blocks], level_id)
lines.append(f"词元统计 : {parsed['counters']}  总词数={parsed['word_count']}")
lines.append(f"候选标注 : {len(parsed['candidates'])}")

hb = markup.build(parsed, level_id)
lines.append(f"最终标注 : {hb['counters']}")
lines.append(f"预算     : {hb['budget']}")
lines.append(f"生词数   : {len(hb['vocab'])}   句型数={len(hb['patterns'])}")
lines.append("--- 生词前 20 ---")
for v in hb["vocab"][:20]:
    lines.append(f"  {v['surface']:18s} {v['kind']:9s} {v['phonetic']:16s} {v['gloss'][:24]}")
lines.append("--- 句型 ---")
for p in hb["patterns"]:
    lines.append(f"  {p['name']}  | {'、'.join(p['usage'])}")

out_dir = ROOT / "out"
out_dir.mkdir(exist_ok=True)
html = render.render_handbook(hb, "The Cost of Convenience")
out_file = out_dir / f"handbook-{level_id}.html"
out_file.write_text(html, encoding="utf-8")
lines.append(f"\n渲染输出 : {out_file}  ({len(html)} 字符)")

(ROOT / "out" / "_pipeline.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
