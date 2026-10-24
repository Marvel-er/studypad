"""下载 ECDICT 并验证它能不能补上本项目测出来的 49 个缺口词。

按 skills/github-search-and-batch-download 的规程：
  · 走 **codeload.github.com**（raw.githubusercontent.com 被代理挡成 502，
    api.github.com 可用于读小文件，但整个 zip 要走 codeload）；
  · 解压用 Windows 自带 `tar.exe`；
  · 解压落到**唯一临时目录**再从里面 rename，绝不复用再清空；
  · 幂等：目标目录已存在且非空 → SKIP；zip 已存在且 >1KB → 复用。
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "ecdict"
ZIP = ROOT / "out" / "_gh_collins" / "skywind3000__ECDICT-master.zip"
TMP = ROOT / "out" / "_gh_collins" / "_tmp_ecdict"
CSV = VENDOR / "ECDICT-master" / "ecdict.csv"

UA = {"User-Agent": "studypad-ecdict-download"}


def log(msg: str) -> None:
    print(msg, flush=True)


def download() -> bool:
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    if ZIP.exists() and ZIP.stat().st_size > 1024:
        log(f"  SKIP(exists) {ZIP.name}  {ZIP.stat().st_size // 1024} KB")
        return True
    url = "https://codeload.github.com/skywind3000/ECDICT/zip/refs/heads/master"
    log(f"  下载 {url}")
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=300) as r, ZIP.open("wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:  # noqa: BLE001
        log(f"  下载失败：{type(e).__name__}: {e}")
        if ZIP.exists():
            ZIP.unlink(missing_ok=True)
        return False
    log(f"  完成 {ZIP.stat().st_size // 1024} KB")
    return True


def extract() -> bool:
    if CSV.exists() and CSV.stat().st_size > 1024:
        log(f"  SKIP(exists) {CSV}  {CSV.stat().st_size // 1024 // 1024} MB")
        return True
    VENDOR.mkdir(parents=True, exist_ok=True)
    if TMP.exists():
        log(f"  _tmp 已存在（上次中断？），先复用：{TMP}")
    TMP.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["tar.exe", "-xf", str(ZIP), "-C", str(TMP)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        log(f"  tar 失败：{r.stderr[:300]}")
        return False
    inner = TMP / "ECDICT-master"
    if not inner.is_dir():
        log(f"  解压后没找到 ECDICT-master，实际内容："
            f"{[p.name for p in TMP.iterdir()][:10]}")
        return False
    dest = VENDOR / "ECDICT-master"
    if dest.exists():
        log(f"  目标已存在，跳过 rename：{dest}")
    else:
        os.rename(inner, dest)
    log(f"  OK → {dest}")
    return True


def main() -> int:
    log("[1/3] 下载 ECDICT zip")
    if not download():
        return 1
    log("[2/3] 解压")
    if not extract():
        return 1
    log("[3/3] 用 49 个缺口词验证")
    if not CSV.exists():
        log(f"  没找到 {CSV}")
        return 1

    gaps = json.loads((ROOT / "out" / "_gh_collins" / "gaps.json").read_text("utf-8")) \
        if (ROOT / "out" / "_gh_collins" / "gaps.json").exists() else None
    if gaps is None:
        log("  没有 gaps.json，跳过逐词验证（只报规模）")
        with CSV.open(encoding="utf-8") as f:
            n = sum(1 for _ in f) - 1
        log(f"  ecdict.csv 共 {n} 条")
        return 0

    want = set(gaps)
    hit: dict[str, dict] = {}
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = (row.get("word") or "").lower()
            if w in want and w not in hit:
                hit[w] = row
    log(f"  49 个缺口词中，ECDICT 收录了 {len(hit)} 个：")
    for w in sorted(hit):
        r = hit[w]
        log(f"    {w:<14} 音标={r.get('phonetic') or '(空)':<20}"
            f"词性={r.get('pos') or '(空)':<8}"
            f"释义={(r.get('translation') or '')[:34]!r}"
            f" collins={r.get('collins')} oxford={r.get('oxford')} tag={r.get('tag')}")
    missing = sorted(want - set(hit))
    log(f"  仍未收录 {len(missing)} 个：{missing}")

    with CSV.open(encoding="utf-8") as f:
        n = sum(1 for _ in f) - 1
    log(f"  ecdict.csv 总条目 {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
