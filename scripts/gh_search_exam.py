"""
GitHub 检索：六档英语考试（高中/CET4/CET6/考研/雅思/托福）考点相关资源。

- 中英文多组关键词交叉检索，比单次搜得全；中文关键词常能挖到英文搜漏的优质仓库
- 未认证搜索 API 限额 10 次/分钟 → 每次间隔 8 秒，403/429 等 35 秒重试
- 搜索接口已返回 default_branch / size / stars / archived / pushed_at，不再二次调 core API
  （core API 未认证只有 60 次/小时，要留给后面核实许可证）
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RAW = OUT / "_gh_exam.json"
LOG = OUT / "_gh_exam.txt"

QUERIES = [
    # —— 高中
    "高考英语 词汇",
    "高中英语 语法",
    "高中英语 3500词",
    # —— 四级
    "CET4 vocabulary list",
    "大学英语四级 词汇",
    "cet-4 word list",
    # —— 六级
    "CET6 vocabulary",
    "大学英语六级 词汇",
    # —— 考研
    "考研英语 词汇",
    "kaoyan english vocabulary",
    "考研英语 真题",
    # —— 雅思
    "IELTS vocabulary list",
    "雅思 词汇",
    # —— 托福
    "TOEFL vocabulary",
    "托福 词汇",
    # —— 通用：语法体系 / 语料
    "english grammar rules list",
    "英语 语法 体系 总结",
]


def main() -> None:
    log: list[str] = []
    merged: dict[str, dict] = {}

    with httpx.Client(timeout=45, headers={"Accept": "application/vnd.github+json"}) as c:
        for i, q in enumerate(QUERIES, 1):
            items = None
            for attempt in range(3):
                try:
                    r = c.get("https://api.github.com/search/repositories",
                              params={"q": q, "sort": "stars", "order": "desc",
                                      "per_page": 20})
                    if r.status_code in (403, 429):
                        log.append(f"[{i:>2}] {q:<32} → {r.status_code} 限流，等 35s 重试")
                        time.sleep(35)
                        continue
                    r.raise_for_status()
                    items = r.json().get("items", [])
                    break
                except Exception as e:  # noqa: BLE001
                    log.append(f"[{i:>2}] {q:<32} → 异常 {type(e).__name__}: {e}")
                    time.sleep(5)
            if items is None:
                log.append(f"[{i:>2}] {q:<32} → 放弃")
                continue

            log.append(f"[{i:>2}] {q:<32} → {len(items)} 条")
            for it in items:
                full = it["full_name"]
                rec = merged.setdefault(full, {
                    "full_name": full,
                    "stars": it.get("stargazers_count", 0),
                    "size_kb": it.get("size", 0),
                    "branch": it.get("default_branch", "main"),
                    "desc": (it.get("description") or "").strip()[:200],
                    "pushed": (it.get("pushed_at") or "")[:10],
                    "archived": bool(it.get("archived")),
                    "fork": bool(it.get("fork")),
                    "topics": it.get("topics", []) or [],
                    "queries": [],
                })
                rec["queries"].append(q)
            time.sleep(8)

    # 排序：先剔 fork 与归档，再按 star
    cands = [v for v in merged.values() if not v["fork"] and not v["archived"]]
    cands.sort(key=lambda x: (-x["stars"], -x["size_kb"]))

    RAW.write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"去重后候选 {len(merged)} 个，剔除 fork/归档后 {len(cands)} 个", ""]
    lines.append(f"{'stars':>7} {'sizeKB':>8} {'pushed':>10}  full_name / desc")
    lines.append("-" * 118)
    for v in cands:
        lines.append(f"{v['stars']:>7} {v['size_kb']:>8} {v['pushed']:>10}  {v['full_name']}")
        if v["desc"]:
            lines.append(f"{'':>28}  {v['desc']}")
    LOG.write_text("\n".join(log + [""] + lines), encoding="utf-8")
    print(f"candidates={len(cands)}")


if __name__ == "__main__":
    main()
