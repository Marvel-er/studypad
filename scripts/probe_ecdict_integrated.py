"""端到端验证：ECDICT 兜底层接入后，真实 PDF 的生词表还剩几个空行。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

PDF = Path(r"E:\英语PDF素材\短篇小说\classic_A_Piece_of_Red_Calico_Stockton.pdf")

from app import annotator, markup, parsers, wordlist  # noqa: E402

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


out.append("--- 词典分层现状 ---")
out.append(f"  六档索引      {len(wordlist._index())}")
out.append(f"  general.json  {len(wordlist._general())}")
out.append(f"  extra.json    {len(wordlist._extra())}（手写）")
out.append(f"  ecdict.json   {len(wordlist._ecdict())}（MIT，兜底层）")

blocks, info = parsers.parse(PDF.name, PDF.read_bytes())
parsed = annotator.analyze_document([b.as_dict() for b in blocks], "cet6")
hb = markup.build(parsed, "cet6")
vocab = hb["vocab"]

out.append("")
out.append(f"生词表 {len(vocab)} 词：")
out.append(f"  {'surface':<14}{'音标':<16}{'词性':<7}{'释义':<24}kind")
bad = []
for v in vocab:
    miss = [k for k in ("phonetic", "pos", "gloss") if not v.get(k)]
    if miss:
        bad.append(v["surface"])
    out.append(f"  {v['surface']:<14}{(v.get('phonetic') or ''):<16}"
               f"{(v.get('pos') or ''):<7}{(v.get('gloss') or '')[:22]:<24}"
               f"{v.get('kind','')}{'  缺=' + str(miss) if miss else ''}")

check(not bad, "生词表没有任何一行缺音标/词性/释义", f"缺的行：{bad}")

out.append("")
out.append("--- ECDICT 兜底层的实际收益：抽几个它独有的词 ---")
# 找一个只在 ecdict 里有的词
only_ec = [w for w in wordlist._ecdict()
           if w not in wordlist._index() and w not in wordlist._general()
           and w not in wordlist._extra()]
out.append(f"  ECDICT 独有词 {len(only_ec)} 个，抽 8 个看质量：")
for w in only_ec[:8]:
    e = wordlist._ecdict()[w]
    out.append(f"    {w:<14}{e.get('p',''):<18}{e.get('pos',''):<6}{e.get('t','')[:30]!r}")

out.append("")
out.append("--- 反向：确认优先级没被破坏 ---")
# calico 在 extra.json 里，应该走手写而不是更低层。
# ⚠ 判据**不能再用音标**：2026-10-15 起音标一律来自发音词典（`lexicon.sqlite` 的 `pron` 表），
# 与「词条来自哪一层」无关 —— 拿音标当层的代理指标会假红（`calico` 的实际音标是 CMUdict 的
# `/'kælәkoʊ/`，不再是 extra.json 里那个 `/ˈkælɪkəʊ/`）。改判**释义**：手写那条的释义
# 是「印花棉布；白布」，与 ECDICT 系的说法不同。
hit = wordlist.lookup_entry("calico", "cet6")
check(hit is not None and "印花棉布" in (hit[1] or {}).get("t", ""),
      "calico 仍走手写 extra.json（判释义，不判音标）",
      f"实际释义 {(hit[1] or {}).get('t') if hit else None}")
check(bool(hit) and (hit[1] or {}).get("p") == wordlist.pronunciation("calico"),
      "音标来自发音词典（与词条来自哪一层无关）",
      f'音标 {(hit[1] or {}).get("p") if hit else None} / 发音表 {wordlist.pronunciation("calico")}')
# 一个只在 ECDICT 里有的词
if only_ec:
    w = only_ec[0]
    hit2 = wordlist.lookup_entry(w, "cet6")
    check(hit2 is not None, f"ECDICT 独有词 {w!r} 现在查得到了")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
