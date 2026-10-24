"""量一下：把 ECDICT 并进来，实际需要新增多少条、文件多大。

设计意图（避免无脑吞 77 万条）：
  1. 只收**现有数据源没有的词**（六档索引 + general.json + extra.json 之外的），
     否则就是重复造数据；
  2. 只收**词频够常见的**（BNC 有排名且不太靠后），生僻词收了也没人查；
  3. 输出格式与 general.json 一致，方便同一套加载代码复用。
先量规模，再决定要不要真的生成。
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

CSV = ROOT / "vendor" / "ecdict" / "ECDICT-master" / "ecdict.csv"

from app import wordlist  # noqa: E402

out: list[str] = []

known_idx = set(wordlist._index().keys())
known_gen = set(wordlist._general().keys())
known_extra = set(wordlist._extra().keys())
out.append(f"现有数据源：六档索引 {len(known_idx)} + general.json {len(known_gen)}"
           f" + extra.json {len(known_extra)}（手写）")

BNC_MAX = 30000          # BNC 排名门槛：比这更生僻的不收
rows: list[dict] = []
seen: set[str] = set()
skipped_known = skipped_rare = skipped_nophon = 0

with CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        w = (row.get("word") or "").strip().lower()
        if not w or w in seen:
            continue
        seen.add(w)
        if w in known_idx or w in known_gen or w in known_extra:
            skipped_known += 1
            continue
        try:
            bnc = int((row.get("bnc") or "0").strip() or 0)
        except ValueError:
            bnc = 0
        if not bnc or bnc > BNC_MAX:
            skipped_rare += 1
            continue
        ph = (row.get("phonetic") or "").strip()
        tr = (row.get("translation") or "").strip()
        if not ph or not tr:
            skipped_nophon += 1
            continue
        rows.append({
            "word": w,
            "phonetic": ph,
            "translation": tr,
            "definition": (row.get("definition") or "").strip(),
            "bnc": bnc,
            "frq": (row.get("frq") or "").strip(),
            "collins": (row.get("collins") or "").strip(),
            "oxford": (row.get("oxford") or "").strip(),
            "exchange": (row.get("exchange") or "").strip(),
        })

out.append("")
out.append(f"ECDICT 去重后 {len(seen)} 词")
out.append(f"  跳过：已有数据源收录 {skipped_known}")
out.append(f"  跳过：BNC 无排名或 > {BNC_MAX}（太生僻）{skipped_rare}")
out.append(f"  跳过：缺音标或缺释义 {skipped_nophon}")
out.append(f"  → **实际新增 {len(rows)} 条**")

rows.sort(key=lambda r: r["bnc"])
out.append("")
out.append("按 BNC 升序前 25 条预览：")
out.append(f"  {'word':<16}{'bnc':>7}{'frq':>8}  {'phonetic':<18}{'translation[:30]'}")
for r in rows[:25]:
    out.append(f"  {r['word']:<16}{r['bnc']:>7}{r['frq']:>8}  {r['phonetic']:<18}"
               f"{r['translation'][:30]!r}")

# 估个体积
blob = json.dumps(rows, ensure_ascii=False)
out.append("")
out.append(f"预估 JSON 体积：{len(blob.encode('utf-8')) / 1024 / 1024:.1f} MB")

print("\n".join(out))
