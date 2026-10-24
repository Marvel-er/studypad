"""
下载六档考点相关仓库（codeload zip）+ 核实许可证。

设计要点（都是踩过坑之后定的）：
- 目录名一律用 `<owner>__<repo>`：zip 内顶层目录只看 repo+branch、与 owner 无关，
  不同 owner 的同名仓库会静默互相覆盖，Windows 上大小写不同也会撞。
- 解压用系统 tar.exe（比 Expand-Archive 快一个数量级），先解到唯一临时目录再 rename。
- 幂等：目录已存在就 SKIP、zip 已存在且 >1KB 就复用，中断后原样重跑即可。
- 许可证只对最终定稿的这批仓库核实（core API 未认证仅 60 次/小时）。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RAW = OUT / "_gh_exam.json"
DEST = ROOT / "vendor" / "gh_exam"
ZIPS = DEST / "_zips"
TMPROOT = DEST / "_tmp"
LOG = OUT / "_gh_dl.log"
STATS = OUT / "_gh_dl_stats.json"

# 挑选逻辑：优先「考点含量高 + 体积可控」。体积巨大的（my-ielts 752MB 等）跳过。
TARGETS = [
    # —— 语法体系 / 考点纲要
    "yulaoshizuikeai/English-Note",                 # 高考英语语法知识体系（外研版/人教版）
    "aa339519589-cpu/3600-english",                 # 高中语法 + 3600 词汇 + 每日阅读
    "ZhaoyuanLiu23/CET-Prompt-Hub",                 # CET-4/6 写作翻译策略·句型·范文
    "Elomami1976/typogrammar",                      # IELTS / TOEFL 语法与写作
    "singgou/kaoyan-english-one-sentence-trainer",  # 考研长难句训练方法
    "Jobo16/ielts-buddy",                           # 雅思 Agent Skills（学习方法论）
    # —— 真题词频 / 高频考点
    "wangjiuyi543-ui/cet6-vocabulary",              # CET-6 2020-2025 真题词频统计
    "yikun-justcai/npee-vocab-statistics",          # 考研英语一 25 套真题词汇统计·大纲覆盖率
    "JTKING27/kaoyan-vocab-context",                # 考研真题里真正考过的释义
    "chunsi-w/ielts-vocab-cloudflare",              # 剑桥雅思 4-19 真题语料高频词
    "lhzzzzzzzj/english-wordlists-for-ocr",         # CET-6/考研词表（含 source 字段）
    "YSMull/words-statistics",                      # 考研真题词汇统计分析
    # —— 写作 / 语料 / 加分表达
    "IKTNF/kaoyan-english-writing-corpus",          # 考研英语一作文语料库 17 主题
    "purpyviolet/IELTS-Learning-Notes",             # 雅思分话题词汇 + 作文句式 + 口语表达
    # —— 分档高频词表
    "zhuying66/Gaokao688",                          # 高考 688 高频词 JSON
    "YR7429/english-vocab-cn",                      # 高考考纲 3185 词（2025 修订，含熟词生义）
    "Ye767/cet4-high-frequency-words-ye767",        # CET-4 高频 800 词
    "openetymology/OpenEtymology",                  # 词源，覆盖 CET4/CET6/TOEFL/GRE
    # —— 雅思听力场景词（题型相关的考点）
    "Gracegejiaqi/listening-vocab-reader",          # 雅思听力 12 类高频场景 914 词
    "prantomollick/IELTS-Listening-Spelling-Bank",  # 雅思听力高频拼写陷阱
    # —— 托福
    "surajk95/wordsta",                             # GRE/TOEFL/IELTS 词汇数据
    "luminorhan-stack/part_of_speech",              # 托福阅读学术词汇变形
]

MAX_MB = 120.0


def log_write(lines: list[str]) -> None:
    LOG.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    log: list[str] = []
    cands = {r["full_name"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))}
    DEST.mkdir(parents=True, exist_ok=True)
    ZIPS.mkdir(parents=True, exist_ok=True)
    TMPROOT.mkdir(parents=True, exist_ok=True)

    stats: list[dict] = []
    proxy = os.environ.get("https_proxy") or os.environ.get("http_proxy") or ""
    log.append(f"代理 = {proxy}")
    log.append(f"目标 {len(TARGETS)} 个仓库 → {DEST}")
    log.append("")

    with httpx.Client(timeout=60, proxy=proxy or None,
                      headers={"Accept": "application/vnd.github+json"}) as c:
        for i, full in enumerate(TARGETS, 1):
            owner, repo = full.split("/")
            safe = f"{owner}__{repo}"
            final = DEST / safe
            rec = {"full_name": full, "dir": safe, "license": "?", "status": ""}

            if final.exists() and any(final.iterdir()):
                log.append(f"[{i:>2}/{len(TARGETS)}] SKIP(exists) {full}")
                rec["status"] = "skip"
                stats.append(rec)
                continue

            meta = cands.get(full)
            if not meta:
                log.append(f"[{i:>2}/{len(TARGETS)}] SKIP(不在候选里) {full}")
                rec["status"] = "not-found"
                stats.append(rec)
                continue

            size_mb = meta["size_kb"] / 1024
            if size_mb > MAX_MB:
                log.append(f"[{i:>2}/{len(TARGETS)}] SKIP(过大 {size_mb:.0f}MB) {full}")
                rec["status"] = "too-big"
                stats.append(rec)
                continue

            branch = meta["branch"]
            rec["branch"] = branch
            rec["size_mb"] = round(size_mb, 1)

            # —— 许可证（单独调 core API；失败不阻塞下载）
            try:
                r = c.get(f"https://api.github.com/repos/{full}", timeout=30)
                if r.status_code == 200:
                    lic = (r.json().get("license") or {})
                    rec["license"] = lic.get("spdx_id") or "NONE"
                elif r.status_code in (403, 429):
                    rec["license"] = "rate-limited"
                else:
                    rec["license"] = f"http-{r.status_code}"
            except Exception as e:  # noqa: BLE001
                rec["license"] = f"err-{type(e).__name__}"
            time.sleep(0.6)

            # —— 下载
            zip_path = ZIPS / f"{safe}.zip"
            url = f"https://codeload.github.com/{full}/zip/refs/heads/{branch}"
            if not (zip_path.exists() and zip_path.stat().st_size > 1024):
                cmd = ["curl.exe", "-sL", "--ssl-no-revoke", "--max-time", "900",
                       "-o", str(zip_path), url]
                if proxy:
                    cmd[1:1] = ["-x", proxy]
                try:
                    subprocess.run(cmd, check=True, timeout=900)
                except Exception as e:  # noqa: BLE001
                    log.append(f"[{i:>2}/{len(TARGETS)}] FAIL(download) {full}: {e}")
                    rec["status"] = "download-failed"
                    stats.append(rec)
                    continue

            if not zip_path.exists() or zip_path.stat().st_size < 1024:
                log.append(f"[{i:>2}/{len(TARGETS)}] FAIL(空包) {full}")
                rec["status"] = "empty-zip"
                stats.append(rec)
                continue

            # —— 解压：先到唯一临时目录，再 rename 出内层目录
            tmp = TMPROOT / safe
            if tmp.exists():
                shutil.rmtree(tmp, ignore_errors=True)
            tmp.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(["tar.exe", "-xf", str(zip_path), "-C", str(tmp)],
                               check=True, timeout=900)
            except Exception as e:  # noqa: BLE001
                log.append(f"[{i:>2}/{len(TARGETS)}] FAIL(解压) {full}: {e}")
                rec["status"] = "extract-failed"
                stats.append(rec)
                continue

            inner = [p for p in tmp.iterdir() if p.is_dir()]
            if not inner:
                log.append(f"[{i:>2}/{len(TARGETS)}] FAIL(无内层目录) {full}")
                rec["status"] = "no-inner"
                stats.append(rec)
                continue

            if final.exists():
                shutil.rmtree(final, ignore_errors=True)
            os.rename(inner[0], final)
            shutil.rmtree(tmp, ignore_errors=True)

            nfiles = sum(1 for _ in final.rglob("*") if _.is_file())
            rec["files"] = nfiles
            rec["status"] = "ok"
            log.append(f"[{i:>2}/{len(TARGETS)}] OK {full}  lic={rec['license']}  "
                       f"{size_mb:.1f}MB  files={nfiles}")
            stats.append(rec)
            STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
            log_write(log)

    # —— 汇总
    ok = [s for s in stats if s["status"] == "ok"]
    log.append("")
    log.append(f"完成：{len(ok)}/{len(TARGETS)} 下载成功")
    lic_count: dict[str, int] = {}
    for s in stats:
        lic_count[s["license"]] = lic_count.get(s["license"], 0) + 1
    log.append("许可证分布：" + json.dumps(lic_count, ensure_ascii=False))
    risky = [s["full_name"] for s in stats
             if s["license"] in ("GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0")]
    log.append("传染性许可（只可理解思路，不可引代码）：" + (", ".join(risky) or "无"))
    log.append("许可未知/无（NONE）的仓库只能用于理解思路与事实性数据核对：")
    for s in stats:
        if s["license"] in ("NONE", "?", "rate-limited") or str(s["license"]).startswith("err"):
            log.append(f"   · {s['full_name']}  lic={s['license']}")

    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    log_write(log)
    print(f"ok={len(ok)}/{len(TARGETS)}")


if __name__ == "__main__":
    main()
