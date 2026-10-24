"""
构建通用补充词典 `data/dict/general.json`。

## 为什么需要它

六档词表（KyleBing/english-vocabulary 的 1–6 档）之外，还有大量**真实文章里会出现**
的词：专四/专八/GRE/GMAT/雅思学术词、以及更普通的词典词。它们会被标成
「超纲」或「六档之外」，但生词表那一行的**音标 / 词性 / 释义 / 例句全是空的** ——
用户看到的就是一行没有内容的空白（截图反馈里的 origin 问题）。

## 数据源与许可

同一仓库的 `vendor/english-vocabulary-master/full_line_jsonl/full/正序/*.jsonl`：
有道的完整词条格式，含美式音标 `usphone`、`trans`（词性 + 中英释义）、
`sentence`（例句）。与项目现有 `data/wordlists/*.json` **同源**
（KyleBing/english-vocabulary，MIT），因此不引入新的许可证风险。

## 只收录六档之外的词

六档词表本身已经有 2 万多条完整词条，重复收录只会让文件变大。
所以先读 `data/wordlists/_index.json`，跳过所有已收录的词。
这一步把产物从十几万条压到几万条量级。

用法：
    <venv>/Scripts/python.exe scripts/build_general_dict.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "vendor" / "english-vocabulary-master" / "full_line_jsonl" / "full" / "正序"
INDEX = ROOT / "data" / "wordlists" / "_index.json"
OUT_DIR = ROOT / "data" / "dict"
OUT = OUT_DIR / "general.json"

# 与 analyzer 的「六档之外」判定保持一致：短词不值得进词典，也标不出来
MIN_LEN = 5

# 词性归一：有道给的 pos 有时是 "n" / "vt" / "adj."，统一带点
_POS_FIX = re.compile(r"^([a-zA-Z]+)\.?$")


def _norm_pos(p: str) -> str:
    p = (p or "").strip()
    m = _POS_FIX.match(p)
    return f"{m.group(1)}." if m else p


def _pick_phone(c: dict) -> str:
    """音标：优先美式。统一用 /.../ 包裹（生词表那一列本来就是音标列）。"""
    for k in ("usphone", "phone", "ukphone"):
        v = (c.get(k) or "").strip()
        if v:
            return f"/{v.strip('/[]')}/"
    return ""


def _pick_trans(c: dict) -> tuple[str, str, str]:
    """返回 (词性, 中文释义, 英文释义)。"""
    trans = c.get("trans")
    if not isinstance(trans, list):
        trans = [trans] if isinstance(trans, dict) else []

    poss: list[str] = []
    cns: list[str] = []
    ens: list[str] = []
    for item in trans:
        if not isinstance(item, dict):
            continue
        pos = _norm_pos(item.get("pos") or "")
        cn = (item.get("tranCn") or "").strip()
        en = (item.get("tranOther") or "").strip()
        if pos and pos not in poss:
            poss.append(pos)
        # 同一个 pos 的多个义项用顿号连着更像词典；这里统一用 "；" 分隔
        if cn:
            for piece in re.split(r"[，,;；]\s*", cn):
                piece = piece.strip()
                if piece and piece not in cns:
                    cns.append(piece)
        if en and en not in ens:
            ens.append(en)

    pos_s = "/".join(poss[:3])                  # 最多三个词性，够用了
    cn_s = "；".join(cns[:6])                   # 最多六个义项
    en_s = "；".join(ens[:2])
    return pos_s, cn_s, en_s


def _pick_sentence(c: dict) -> str:
    s = c.get("sentence")
    if not isinstance(s, dict):
        return ""
    arr = s.get("sentences")
    if not isinstance(arr, list):
        return ""
    for item in arr:
        if isinstance(item, dict):
            txt = (item.get("sContent") or "").strip()
            if txt:
                return txt
    return ""


def _score(entry: dict) -> int:
    """信息完整度打分，用于在同一个词的多个副本里取最全的那条。"""
    return (2 if entry["p"] else 0) + (2 if entry["t"] else 0) + \
           (1 if entry["pos"] else 0) + (1 if entry["s"] else 0)


def main() -> int:
    if not SRC.exists():
        print(f"语料目录不存在：{SRC}")
        return 2

    known: set[str] = set(json.loads(INDEX.read_text(encoding="utf-8")).keys())
    print(f"六档词表已有 {len(known)} 词，这些将被跳过")

    files = sorted(SRC.glob("*.jsonl"))
    print(f"待扫描 {len(files)} 个词库文件")

    out: dict[str, dict] = {}
    scanned = 0
    for f in files:
        n_file = 0
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                scanned += 1
                # 快速预筛：绝大多数行都不含我们关心的键名组合
                if '"headWord"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except (ValueError, KeyError):
                    continue
                head = (d.get("headWord") or "").strip()
                if not head or len(head) < MIN_LEN:
                    continue
                key = head.lower()
                if key in known or not key.isalpha():
                    continue

                node = (d.get("content") or {}).get("word") or {}
                c = node.get("content") or {}
                if not isinstance(c, dict):
                    continue

                pos, cn, en = _pick_trans(c)
                cand = {
                    "p": _pick_phone(c),
                    "pos": pos,
                    "t": cn,
                    "e": en,
                    "s": _pick_sentence(c),
                }
                if not (cand["p"] or cand["t"]):
                    continue                     # 什么都没有的词条没有意义
                cur = out.get(key)
                if cur is None or _score(cand) > _score(cur):
                    out[key] = cand
                n_file += 1
        print(f"  {f.stem:<14} 收录累计 {len(out)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")

    size_mb = OUT.stat().st_size / 1024 / 1024
    full = sum(1 for v in out.values() if v["p"] and v["t"] and v["s"])
    print()
    print(f"扫描 {scanned} 行 → 收录 {len(out)} 词")
    print(f"  音标+释义+例句齐全: {full}（{full / max(1, len(out)) * 100:.1f}%）")
    print(f"  有音标: {sum(1 for v in out.values() if v['p'])}")
    print(f"  有词性: {sum(1 for v in out.values() if v['pos'])}")
    print(f"  有释义: {sum(1 for v in out.values() if v['t'])}")
    print(f"产物 {OUT}  {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
