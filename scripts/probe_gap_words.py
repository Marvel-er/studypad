"""探针：列出文档里所有「六档之外且查不到词条」的词 —— 用来决定补哪些数据。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

PDF = Path(r"E:\英语PDF素材\短篇小说\classic_A_Piece_of_Red_Calico_Stockton.pdf")

from app import annotator, parsers, wordlist  # noqa: E402
from app.lemmatize import is_content_word, lemma_candidates, tokenize  # noqa: E402

out: list[str] = []

blocks, info = parsers.parse(PDF.name, PDF.read_bytes())
parsed = annotator.analyze_document([b.as_dict() for b in blocks], "cet6")

# 直接扫全文 token，凡是「不在六档、且取不到词条」的都列出来
gaps: dict[str, int] = {}
allbeyond: dict[str, int] = {}
for b in blocks:
    if b.meta.get("skip"):
        continue
    for surface, _s, _e in tokenize(b.text):
        if not is_content_word(surface):
            continue
        _lemma, mask = wordlist.lookup(surface)
        if mask:
            continue
        low = surface.lower()
        allbeyond[low] = allbeyond.get(low, 0) + 1
        if not wordlist.lookup_entry(surface, "cet6"):
            gaps[low] = gaps.get(low, 0) + 1

out.append(f"文档：{len(blocks)} 块，{info}")
out.append(f"六档之外的词形 {len(allbeyond)} 种，其中**查不到任何词条**的 {len(gaps)} 种：")
out.append("")
out.append(f"  {'词':<16}{'次数':<6}{'候选词形'}")
for w, n in sorted(gaps.items(), key=lambda kv: (-kv[1], kv[0])):
    out.append(f"  {w:<16}{n:<6}{lemma_candidates(w)}")

out.append("")
out.append("--- 有词条的六档之外词（对照组）---")
ok = [w for w in allbeyond if w not in gaps]
out.append("  " + "、".join(sorted(ok)))

print("\n".join(out))
