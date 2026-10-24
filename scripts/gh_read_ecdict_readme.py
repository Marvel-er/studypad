"""读 ECDICT 的 README 全文 —— 确认它的数据来源，尤其是 Collins 部分的来历。

为什么必须读：MIT 许可覆盖的是**仓库本身**（代码与汇编），不等于底层词典内容
也可以自由再分发。ECDICT 的条目里有一个 `collins` 字段，源自 HarperCollins 的
Collins COBUILD 词典 —— 那是商业版权内容。本项目红线：不能引入来路不明或有
share-alike / 商业版权风险的数据。所以要先看作者自己怎么声明数据来源。
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "_gh_collins"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("skywind3000", "ECDICT", "master", "README.md"),
    ("skywind3000", "ECDICT", "master", "README_EN.md"),
    ("skywind3000", "ECDICT-ultimate", "master", "README.md"),
]

UA = {"Accept": "application/vnd.github+json",
      "User-Agent": "studypad-dict-readme"}


def api(url: str, timeout: int = 25):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return -1, str(e)


out: list[str] = []
for owner, repo, branch, path in TARGETS:
    code, data = api(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}")
    if code != 200 or not isinstance(data, dict):
        out.append(f"### {owner}/{repo}::{path} → HTTP {code}")
        continue
    try:
        body = base64.b64decode(data.get("content") or "").decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        body = f"<解码失败 {e}>"
    out.append("=" * 78)
    out.append(f"### {owner}/{repo} :: {path}  ({len(body)} 字符)")
    out.append("=" * 78)
    out.append(body)
    out.append("")

(OUT / "ecdict_readme.txt").write_text("\n".join(out), encoding="utf-8")

# 只把与「数据来源 / collins / 版权」相关的行打到 stdout，便于快速判断
text = "\n".join(out)
KEYS = ("collins", "cobuild", "oxford", "wordnet", "wiktionary", "来源", "版权",
        "license", "许可", "数据", "copyright", "哈珀", " HarperCollins", "extract",
        "词典数据", "词库", "百度", "必应", "有道")
print("=" * 78)
print("README 里与「数据来源 / 版权」相关的行")
print("=" * 78)
hits = 0
for ln in text.splitlines():
    low = ln.lower()
    if any(k.lower() in low for k in KEYS):
        print(ln[:200])
        hits += 1
if not hits:
    print("（没命中关键词）")
print()
print(f"README 全文：{OUT / 'ecdict_readme.txt'}")
