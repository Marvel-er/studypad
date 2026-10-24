"""ECDICT 能不能替代手写的 extra.json？逐词比对音标/词性/释义。

extra.json 是手写的（48 条，src=hand），ECDICT 是 MIT 仓库 + 77 万词条。
如果 ECDICT 对这批词有**更完整**的数据，就该换成它；否则保留手写版。
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

CSV = ROOT / "vendor" / "ecdict" / "ECDICT-master" / "ecdict.csv"
EXTRA = ROOT / "data" / "dict" / "extra.json"

out: list[str] = []
fails: list[str] = []

extra = json.loads(EXTRA.read_text(encoding="utf-8"))
words = [k for k in extra if not k.startswith("_")]
words.append("calico")
words.append("deserter")

ec: dict[str, dict] = {}
with CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        w = (row.get("word") or "").lower()
        if w in words and w not in ec:
            ec[w] = row

out.append(f"待验证 {len(words)} 个词（extra.json 的 {len(words) - 3} 个 + calico + deserter）")
out.append(f"ECDICT 收录 {len(ec)} 个，未收录 {len(words) - len(ec)} 个")
out.append("")
out.append(f"  {'word':<14}{'ECDICT音标':<22}{'pos':<10}{'释义(前30字)':<34}{'tag'}")
better = same = worse = 0
for w in sorted(words):
    r = ec.get(w)
    mine = extra.get(w) or {}
    if not r:
        out.append(f"  {w:<14}{'— 未收录 —':<22}")
        worse += 1
        continue
    ph = (r.get("phonetic") or "").strip()
    pos = (r.get("pos") or "").strip()
    tr = (r.get("translation") or "").replace("\\n", " ")[:30]
    tag = r.get("tag") or ""
    out.append(f"  {w:<14}{ph or '(空)':<22}{pos or '(空)':<10}{tr:<34}{tag}")
    # 粗判：ECDICT 三项都有 → 更好；缺音标或缺释义 → 不如手写
    if ph and pos and tr:
        better += 1
    elif not ph and not tr:
        worse += 1
    else:
        same += 1

out.append("")
out.append(f"粗判：ECDICT 更完整 {better} 个 / 相当 {same} 个 / 不如手写 {worse} 个")
out.append("")
out.append("--- 抽 3 个词看完整字段 ---")
for w in ["calico", "truffle", "gibbet"]:
    r = ec.get(w)
    if not r:
        out.append(f"  {w}: ECDICT 未收录")
        continue
    out.append(f"  {w}:")
    for k in ("word", "phonetic", "definition", "translation", "pos",
              "collins", "oxford", "tag", "bnc", "frq", "exchange"):
        v = (r.get(k) or "")[:120]
        out.append(f"      {k:<12} {v!r}")

print("\n".join(out))
