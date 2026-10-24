"""拉取 NPEE 词表（交叉验证用的第二份考纲词表）。

来源：[mahavivo/english-wordlists](https://github.com/mahavivo/english-wordlists)
（NPEE = National Postgraduate Entrance Examination）。

**为什么不直接把它放进仓库**：它带音标与释义，属第三方整理的词表内容；
仓库只带最终合并结果（`data/kaoyan_syllabus_verified.txt`）和这个拉取脚本，
需要交叉验证时现拉即可。

国内直连 GitHub raw 常不通，所以默认走 jsDelivr CDN。

用法::

    python scripts/fetch_npee_wordlist.py                 # 下载到 ./NPEE_Wordlist.txt
    python scripts/fetch_npee_wordlist.py -o /tmp/npee.txt
    python scripts/fetch_npee_wordlist.py --no-verify     # 跳过校验（不推荐）
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import urllib.request

URLS = [
    "https://cdn.jsdelivr.net/gh/mahavivo/english-wordlists@master/NPEE_Wordlist.txt",
    "https://raw.githubusercontent.com/mahavivo/english-wordlists/master/NPEE_Wordlist.txt",
]

# 本项目记录在案的版本（2026-10-01 下载，300,430 B）
EXPECTED_SHA256 = "3E9383908E04AAFA2626FDA429B3D486E0F1667A3A66032097261B55F4BA72AD"
EXPECTED_SIZE = 300_430


def fetch(url: str, timeout: int = 60) -> bytes:
    print(f"  尝试 {url}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
        return resp.read()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="拉取 NPEE 考纲词表")
    ap.add_argument("-o", "--output", default="NPEE_Wordlist.txt", help="输出路径")
    ap.add_argument("--no-verify", action="store_true", help="跳过 SHA256 校验")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args(argv)

    data = None
    for url in URLS:
        try:
            data = fetch(url, args.timeout)
            break
        except Exception as exc:  # noqa: BLE001
            print(f"  失败：{exc}")
    if data is None:
        print("错误：所有镜像都拉取失败。", file=sys.stderr)
        return 1

    digest = hashlib.sha256(data).hexdigest().upper()
    print(f"  大小   {len(data):,} B")
    print(f"  SHA256 {digest}")

    if not args.no_verify:
        if len(data) != EXPECTED_SIZE or digest != EXPECTED_SHA256:
            print(
                "错误：与本项目记录在案的版本不一致。\n"
                f"  期望 {EXPECTED_SIZE:,} B / {EXPECTED_SHA256}\n"
                "上游可能已更新。请人工确认后再用 --no-verify。",
                file=sys.stderr,
            )
            return 1
        print("  校验通过 ✓")
    else:
        print("  已跳过校验（--no-verify）")

    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"已写入 {out}")
    print()
    print("用它复现词表对比（应得 75.4% / 87.0%）：")
    print(f"  python -m npee_vocab stats --wordlist {out} --output-dir /tmp/npee")
    return 0


if __name__ == "__main__":
    sys.exit(main())
