"""抓取入围仓库的 LICENSE 原文 —— 走 GitHub API 的 contents 接口。

⚠ 传输方式（2026-10-15 实测）：
  · `raw.githubusercontent.com` → 代理返回 **502 Bad Gateway**（白名单外）；
  · `api.github.com` → **通**（同会话的搜索脚本就是这么拿到 93 个候选的）；
  · `curl.exe` → 在本机不可用（要连回环代理，Bash 沙箱连不上 → HTTP 000）。
  → 只能用 `urllib` + `api.github.com`，并且**用 PowerShell 工具跑**。

为什么要读真实文件而不是信元数据：本项目的红线是「许可证要读仓库里的
LICENSE / DATA_LICENSE 文件，不能只信元数据字段」——OpenEtymology 那次元数据写
NOASSERTION，实际 DATA_LICENSE.md 是 CC BY-SA 4.0（share-alike，会传染数据层）。

API 用法：`/repos/{o}/{r}/contents/{path}` 返回 base64 内容；
先列根目录（1 次调用）看有哪些许可文件，再逐个取，省额度（未认证 60 次/时）。
"""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "_gh_collins"
OUT.mkdir(parents=True, exist_ok=True)

REPOS = [
    ("skywind3000", "ECDICT", "master"),
    ("skywind3000", "ECDICT-ultimate", "master"),
    ("Konyaco", "CollinsDictionary", "master"),
    ("OrcheInk", "english-dictionary", "master"),
    ("jn7163", "YoudaoCollins", "master"),
    ("mahavivo", "open-ecdict", "main"),
    ("windwerfer", "volubilis_dict", "main"),
    ("ikey4u", "wikit", "master"),
]

# 根目录里可能叫这些名字的许可文件（大小写不敏感匹配）
LICENSE_NAMES = ("license", "license.md", "license.txt", "copying",
                 "copying.md", "data_license", "data_license.md",
                 "copyright", "unlicense")

UA = {"Accept": "application/vnd.github+json",
      "User-Agent": "studypad-dict-license-check"}


def api(url: str, timeout: int = 25) -> tuple[int, object]:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                print(f"    [{e.code}] 等 35s 重试…", flush=True)
                time.sleep(35)
                continue
            return e.code, None
        except Exception as e:  # noqa: BLE001
            return -1, str(e)
    return -1, "retry-exhausted"


def main() -> int:
    report: list[str] = []
    found: list[tuple[str, str, str]] = []
    calls = 0

    for owner, repo, branch in REPOS:
        full = f"{owner}/{repo}"
        report.append("=" * 78)
        report.append(f"## {full}  (branch={branch})")
        report.append("=" * 78)
        print(f"[ ] {full}", flush=True)

        # 1) 列根目录，找出许可文件（1 次调用）
        code, data = api(f"https://api.github.com/repos/{full}/contents/?ref={branch}")
        calls += 1
        lic_files: list[str] = []
        if code == 200 and isinstance(data, list):
            for it in data:
                name = (it.get("name") or "").lower()
                if name in LICENSE_NAMES and it.get("type") == "file":
                    lic_files.append(it["name"])
            report.append(f"  根目录 {len(data)} 项；许可文件候选：{lic_files or '无'}")
        else:
            report.append(f"  列目录失败：HTTP {code} {str(data)[:100]}")

        # 2) 逐个取许可文件内容
        for f in lic_files:
            code, data = api(
                f"https://api.github.com/repos/{full}/contents/{f}?ref={branch}")
            calls += 1
            if code == 200 and isinstance(data, dict):
                try:
                    body = base64.b64decode(data.get("content") or "").decode(
                        "utf-8", errors="replace")
                except Exception as e:  # noqa: BLE001
                    body = f"<解码失败 {e}>"
                report.append(f"--- {f}  ({len(body)} 字符) ---")
                report.append(body[:3000])
                report.append("")
                found.append((full, f, body))
                print(f"    ✓ {f}  {len(body)} 字符", flush=True)
            else:
                report.append(f"--- {f} → HTTP {code} ---")
        report.append("")

    (OUT / "license_report.txt").write_text("\n".join(report), encoding="utf-8")

    print()
    print("=" * 78)
    print(f"许可文件摘要（共用 {calls} 次 core API 调用）")
    print("=" * 78)
    if not found:
        print("⚠ 一个许可文件都没读到 —— 需人工核对")
    for full, f, body in found:
        print(f"\n### {full} :: {f}")
        print(body.replace("\r", "")[:700])
    print()
    print(f"完整报告：{OUT / 'license_report.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
