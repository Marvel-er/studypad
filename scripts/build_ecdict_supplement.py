"""生成 ECDICT 补充词典：过滤掉现有数据源已有的词和明显不是词汇的 token。

设计（三层过滤，都是可复现的规则，不是手工挑）：
  1. 现有数据源（六档索引 / general.json / extra.json）已有的 → 不要，避免重复；
  2. 太生僻的（BNC 无排名或 > 30000）→ 不要，收了也没人查；
  3. 明显不是词汇的 → 不要：
       · 长度 < 3（an / er / de / p / ah / us …）
       · 纯化学元素符号与常见缩略语（一张小的阻止表，逐条列出理由）
       · analyzer.STOPWORDS 里的功能词
       · 缺音标或缺释义的
  4. 输出与 general.json 同构，便于同一套加载代码复用。

⚠ 许可证与来历（写进 _meta，随文件一起交付）：
ECDICT 仓库本身是 **MIT**（已读仓库根目录的 LICENSE 原文，Copyright (c) 2025 Linwei）。
但 MIT 覆盖的是**仓库**，不等于底层数据全部可自由再分发 —— 作者在 README 里说明
数据来自多处：网友提供的 EDictAZ.txt、用爬虫从「各种资料」爬取的音标、Linux 的
cdict 开源词典数据、以及 WordNet。这些上游的许可并未逐一明确。
→ 因此本文件是** fallback 层**（优先级最低），并在 _meta 里如实记录这一点，
  由使用者自行判断是否接受。
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

CSV = ROOT / "vendor" / "ecdict" / "ECDICT-master" / "ecdict.csv"
OUT = ROOT / "data" / "dict" / "ecdict.json"
BNC_MAX = 30000

# 明显不是「英语词汇」的 token：化学元素符号 / 常见缩略语 / 单位。
# 逐条列出理由，避免以后有人看不懂为什么偏偏屏蔽这几个。
BLOCKLIST = {
    # 化学元素符号（BNC 里居然有排名，但没人需要背）
    "er", "re", "de", "hm", "ho", "hf", "dy", "es", "tb", "tm", "yb",
    "lu", "eu", "gd", "nd", "pr", "sm", "ce", "la", "nb", "mo", "zr",
    # 缩略语 / 符号
    "mr", "mrs", "ms", "dr", "st", "vs", "etc", "eg", "ie", "aka",
    "cos", "cosec", "cot", "tan", "sin", "log", "exp",
    # 感叹词与口头禅
    "erm", "er", "um", "uh", "ah", "oh", "eh", "hmm", "huh", "yeah",
    "yep", "nope", "wow", "oops", "alas",
}


def main() -> int:
    from app import wordlist
    from app.analyzer import STOPWORDS

    known_idx = set(wordlist._index().keys())
    known_gen = set(wordlist._general().keys())
    known_extra = set(wordlist._extra().keys())

    out: dict[str, dict] = {}
    seen: set[str] = set()
    n_known = n_rare = n_junk = n_nodata = 0

    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = (row.get("word") or "").strip().lower()
            if not w or w in seen:
                continue
            seen.add(w)
            if w in known_idx or w in known_gen or w in known_extra:
                n_known += 1
                continue
            try:
                bnc = int((row.get("bnc") or "0").strip() or 0)
            except ValueError:
                bnc = 0
            if not bnc or bnc > BNC_MAX:
                n_rare += 1
                continue
            if len(w) < 3 or w in BLOCKLIST or w in STOPWORDS:
                n_junk += 1
                continue
            ph = (row.get("phonetic") or "").strip().strip("'")
            tr = (row.get("translation") or "").strip()
            if not ph or not tr:
                n_nodata += 1
                continue
            # 释义里把词性写成了前缀（"n. 印花棉布"）→ 拆出来单独存 pos，
            # 并把前缀从释义里去掉，否则表格里「词性 n」和「释义 n. 印花棉布」重复
            pos = ""
            head = tr.split("\\n", 1)[0].strip()
            gloss = head
            for tag in ("n.", "v.", "vt.", "vi.", "a.", "ad.", "adv.", "pron.",
                        "conj.", "prep.", "int.", "num.", "art.", "abbr.",
                        "aux.", "det."):
                if head.startswith(tag):
                    pos = tag.rstrip(".")
                    gloss = head[len(tag):].strip()
                    break
            out[w] = {
                "p": ph,
                "pos": pos,
                # 只取首个义项：多义项堆在一起在表格里很难看
                "t": gloss.split(",", 1)[0].strip() or gloss,
                "e": (row.get("definition") or "").split("\\n", 1)[0].strip(),
                "s": "",
                "bnc": bnc,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            "what": "ECDICT 补充词典（fallback 层，优先级最低）",
            "source": "skywind3000/ECDICT (MIT, 8438 stars) — ecdict.csv，770,611 条",
            "license": "仓库为 MIT（LICENSE 原文：Copyright (c) 2025 Linwei）。"
                       "但 MIT 覆盖仓库本身；底层数据由作者自多处汇编（网友的 EDictAZ.txt、"
                       "爬虫抓取的音标、Linux cdict、WordNet），上游许可未逐一明确。",
            "provenance_caveat": "因此这里只作**最后兜底**：六档词表 / general.json / "
                                 "extra.json 都查不到时才用它。是否接受该 caveat 由使用者决定；"
                                 "不接受就删掉本文件即可，wordlist._ecdict() 会静默降级。",
            "filters": [
                "现有数据源（六档索引 / general.json / extra.json）已有的词一律不收",
                f"BNC 无排名或 > {BNC_MAX} 的不收（太生僻）",
                "长度 < 3、化学元素符号、常见缩略语、感叹词、功能词一律不收",
                "缺音标或缺释义的不收",
                "只取首个义项；词性从译文中缀（'n. xxx'）拆出来",
            ],
            "stats": {
                "ecdict_total": len(seen),
                "skipped_known": n_known,
                "skipped_too_rare": n_rare,
                "skipped_junk": n_junk,
                "skipped_no_data": n_nodata,
                "kept": len(out),
            },
            "rebuild": "python scripts/build_ecdict_supplement.py",
        }
    }
    payload.update(out)
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    print(f"ECDICT 去重 {len(seen)} 词")
    print(f"  跳过：已有数据源 {n_known}")
    print(f"  跳过：BNC 无排名或 > {BNC_MAX}  {n_rare}")
    print(f"  跳过：长度<3 / 元素符号 / 缩略语 / 感叹词 / 功能词  {n_junk}")
    print(f"  跳过：缺音标或缺释义  {n_nodata}")
    print(f"  → 保留 {len(out)} 条")
    print(f"  → {OUT}  ({OUT.stat().st_size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
