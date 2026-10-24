"""
构建通用英语词频索引。

数据来源：first20hours/google-10000-english（20k.txt，Google Trillion Word Corpus 词频序）
输出：data/wordlists/_freq.json  {"word": rank}，rank 越小越常用（1 起）
未收录的词在查询时视为「极低频」（rank = 20001）。
"""
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
SRC = ROOT / "vendor" / "google-10000-english-master" / "20k.txt"
DST = ROOT / "data" / "wordlists" / "_freq.json"

UNKNOWN_RANK = 20001


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"缺少词频文件：{SRC}")

    freq: dict[str, int] = {}
    with open(SRC, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            w = line.strip().lower()
            if w and w not in freq:
                freq[w] = i

    import json
    DST.write_text(json.dumps(freq, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")

    report = [f"[OK] _freq.json  words={len(freq)}  size={DST.stat().st_size/1048576:.2f}MB"]
    for probe in ["different", "probably", "millions", "frequently", "productivity",
                  "endurance", "negotiation", "transparent", "remediation", "pandemic",
                  "the", "algorithm", "counterproductive"]:
        report.append(f"   {probe:18s} rank={freq.get(probe, UNKNOWN_RANK)}")
    (ROOT / "data" / "wordlists" / "_freq_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
