"""探针：复现「生词表有的行音标/词性/释义全空」并定位每一行的原因。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

PDF = Path(r"E:\英语PDF素材\短篇小说\classic_A_Piece_of_Red_Calico_Stockton.pdf")

from app import annotator, markup, parsers, wordlist  # noqa: E402
from app.lemmatize import lemma_candidates  # noqa: E402

out: list[str] = []
fails: list[str] = []

data = PDF.read_bytes()
blocks, info = parsers.parse(PDF.name, data)
out.append(f"解析：{len(blocks)} 块，info={info}")
for b in blocks[:5]:
    out.append(f"  [{b.type:9}] {b.text[:70]!r}")

parsed = annotator.analyze_document([b.as_dict() for b in blocks], "cet6")
hb = markup.build(parsed, "cet6")
vocab = hb["vocab"]
out.append("")
out.append(f"生词表 {len(vocab)} 词，逐行看四个字段：")
out.append(f"  {'surface':<14}{'p':<12}{'pos':<8}{'gloss':<22}kind")
empty_rows = []
for v in vocab:
    miss = [k for k in ("phonetic", "pos", "gloss") if not v.get(k)]
    if miss:
        empty_rows.append(v["surface"])
    out.append(f"  {v['surface']:<14}{(v.get('phonetic') or ''):<12}"
               f"{(v.get('pos') or ''):<8}{(v.get('gloss') or '')[:20]:<22}"
               f"{v.get('kind','')}  缺={miss or '无'}")

out.append("")
out.append(f"四列不全的行：{empty_rows}")

# ---- 逐个追：这些词在数据层到底能不能查到 ----
out.append("")
out.append("--- 取词追因 ---")
idx = wordlist._index()
gen = wordlist._general()
for w in empty_rows:
    cands = lemma_candidates(w)
    out.append(f"  {w!r}: 候选词形 = {cands}")
    out.append(f"      在六档索引里？{[c for c in cands if c in idx] or '无'}")
    out.append(f"      在补充词典里？{[c for c in cands if c in gen] or '无'}"
               f"（补充词典共 {len(gen)} 条）")
    hit = wordlist.lookup_entry(w, "cet6")
    out.append(f"      lookup_entry → {hit[0] if hit else None}"
               f" / {sorted((hit[1] or {}).keys()) if hit else None}")
    # 复合词兜底有没有机会
    out.append(f"      长度 {len(w.lower())}（复合词要求 8..20）")

out.append("")
out.append("--- 其它有数据的词做对照 ---")
for v in vocab:
    if v["surface"] in empty_rows:
        continue
    hit = wordlist.lookup_entry(v["surface"], "cet6")
    src = "六档" if hit and not (hit[1] or {}).get("c") else (
        "复合词" if hit and (hit[1] or {}).get("c") else "补充词典")
    out.append(f"  {v['surface']:<14} 来自 {src}（命中词形 {hit[0] if hit else None}）")
    break

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败'}")
print("\n".join(out))
sys.exit(1 if fails else 0)
