"""
把开源的六档词表（KyleBing/english-vocabulary, MIT）归一化为本项目使用的紧凑索引。

输入：vendor/english-vocabulary-master/full_line_jsonl/sentence/正序/{高中,四级,六级,考研,雅思,托福}.jsonl
输出：
  data/wordlists/{level}.json   每档词条详情 {word: {p 音标, t 释义, pos 词性, s 例句, r 词频序}}
  data/wordlists/_index.json    {word: bitmask}  用于 O(1) 判定某词属于哪些档

bitmask 位序（低 → 高）：高中=1, 四级=2, 六级=4, 考研=8, 雅思=16, 托福=32
"""
import json
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
SRC = ROOT / "vendor" / "english-vocabulary-master" / "full_line_jsonl" / "sentence" / "正序"
DST = ROOT / "data" / "wordlists"

# (level_id, 中文文件名, 显示名, bit)
LEVELS = [
    ("high_school", "高中", "高中", 1),
    ("cet4",        "四级", "大学英语四级", 2),
    ("cet6",        "六级", "大学英语六级", 4),
    ("kaoyan",      "考研", "考研英语", 8),
    ("ielts",       "雅思", "雅思", 16),
    ("toefl",       "托福", "托福", 32),
]


def main():
    DST.mkdir(parents=True, exist_ok=True)
    index: dict[str, int] = {}
    report = []

    for level_id, cn_name, _, bit in LEVELS:
        src = SRC / f"{cn_name}.jsonl"
        if not src.exists():
            report.append(f"[MISS] {src}")
            continue

        entries = {}
        with open(src, encoding="utf-8") as f:
            for rank, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                word = (obj.get("word") or "").strip().lower()
                if not word or not word.isascii():
                    continue

                trans = obj.get("translations") or []
                meaning = trans[0].get("translation", "") if trans else ""
                pos = trans[0].get("type", "") if trans else ""
                sents = obj.get("sentences") or []
                example = sents[0].get("sentence", "") if sents else ""

                entries[word] = {
                    "p": obj.get("us") or obj.get("uk") or "",
                    "t": meaning,
                    "pos": pos,
                    "s": example,
                    "r": rank,
                }
                index[word] = index.get(word, 0) | bit

        out = DST / f"{level_id}.json"
        out.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
                       encoding="utf-8")
        report.append(f"[OK] {level_id:12s} {cn_name:4s} words={len(entries):6d} "
                      f"size={out.stat().st_size/1048576:.2f}MB")

    idx_out = DST / "_index.json"
    idx_out.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")),
                       encoding="utf-8")
    report.append(f"[OK] _index.json  unique_words={len(index)} "
                  f"size={idx_out.stat().st_size/1048576:.2f}MB")

    # 统计各档累计覆盖
    report.append("--- cumulative coverage (known-set) ---")
    cum = 0
    for i, (level_id, cn_name, _, bit) in enumerate(LEVELS):
        mask = (1 << (i + 1)) - 1
        cum = sum(1 for v in index.values() if v & mask)
        report.append(f"  {level_id:12s} known={cum:6d}")

    (ROOT / "data" / "wordlists" / "_build_report.txt").write_text(
        "\n".join(report), encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
