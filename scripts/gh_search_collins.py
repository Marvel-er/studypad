"""搜 GitHub 上的柯林斯词典数据集，并把候选仓库连许可证一起记下来。

按 skills/github-search-and-batch-download 的规程：
  · 多组中英文关键词交叉检索，去重后按 star 合并；
  · 未认证搜索 API 限额 10 次/分 → 每次间隔 8 秒，403/429 等 35 秒重试；
  · 搜索接口已返回 default_branch/size/star/archived/pushed_at，
    **只有 license 需要单独调 core API**（未认证 60 次/小时，不能浪费）。
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "_gh_collins"
OUT.mkdir(parents=True, exist_ok=True)

QUERIES = [
    "collins dictionary",
    "collins cobuild",
    "柯林斯词典",
    "collins english dictionary data",
    "ecdict",
    "mdx dictionary",
    "english dictionary dataset json",
    "柯林斯 英汉",
    "collins phonetic",
    "dictionary stardict mdx",
]

UA = {"Accept": "application/vnd.github+json",
      "User-Agent": "studypad-dict-search"}


def get(url: str, tries: int = 3) -> dict | None:
    """带 403/429 退避的 GET。返回 None 表示彻底失败。"""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < tries - 1:
                wait = 35
                print(f"    [{e.code}] 等 {wait}s 重试…", flush=True)
                time.sleep(wait)
                continue
            print(f"    [HTTP {e.code}] {url[:90]}", flush=True)
            return None
        except Exception as e:  # noqa: BLE001
            print(f"    [{type(e).__name__}] {url[:90]}", flush=True)
            return None
    return None


def main() -> int:
    cands: dict[str, dict] = {}
    for i, q in enumerate(QUERIES, 1):
        url = ("https://api.github.com/search/repositories?q="
               + urllib.parse.quote(q)
               + "&sort=stars&order=desc&per_page=20")
        print(f"[{i}/{len(QUERIES)}] {q}", flush=True)
        data = get(url)
        if not data:
            continue
        items = data.get("items") or []
        print(f"    命中 {len(items)} 个", flush=True)
        for it in items:
            full = it["full_name"]
            prev = cands.get(full)
            hit = {
                "full_name": full,
                "stars": it.get("stargazers_count", 0),
                "size_kb": it.get("size", 0),
                "branch": it.get("default_branch", "main"),
                "archived": bool(it.get("archived")),
                "pushed_at": (it.get("pushed_at") or "")[:10],
                "desc": (it.get("description") or "")[:160],
                "topics": (it.get("topics") or [])[:6],
                "queries": [q],
                "license_spdx": ((it.get("license") or {}) or {}).get("spdx_id"),
            }
            if prev:
                prev["queries"].append(q)
                prev["stars"] = max(prev["stars"], hit["stars"])
            else:
                cands[full] = hit
        # 限速：未认证 10 次/分
        if i < len(QUERIES):
            time.sleep(8)

    rows = sorted(cands.values(), key=lambda r: -r["stars"])
    (OUT / "candidates.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"去重后候选 {len(rows)} 个（按 star 降序）：")
    print(f"  {'full_name':<44}{'star':>6}{'MB':>7}  {'branch':<10}{'pushed':<11}license")
    for r in rows[:45]:
        print(f"  {r['full_name']:<44}{r['stars']:>6}{r['size_kb'] // 1024:>7}  "
              f"{r['branch']:<10}{r['pushed_at']:<11}{r['license_spdx']}")
    print()
    print("→ 接下来只对入围者逐个调 core API 核实许可证（core API 只有 60 次/时）")
    print(f"→ 明细：{OUT / 'candidates.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
