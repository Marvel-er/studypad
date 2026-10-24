"""
知识库**打真服务**的端到端探针。

模块层（test_library.py）与接口层（test_library_api.py）都跑完了，但它们走的是
TestClient / 进程内 ASGI —— **验不出「服务还挂着旧模块」**（项目里踩过：
改完代码没重启，输出全是旧值，误判成代码写错）。

这里走 `scripts/_api` 优先打真服务；连不上才回退进程内，并把实际传输方式打出来。
注意：回退的那条路**同样验不出旧模块**，所以真服务确认仍靠 restart_server.py
重启后重跑本脚本。

用法：
    python scripts/run_selftest.py scripts/probe_library_e2e.py out/_lib_e2e.txt
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _api                                    # noqa: E402

BASE = "http://127.0.0.1:8300"
C = _api.client()
SAMPLE = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")

FAILED: list[str] = []
N = 0


def check(label: str, cond, extra: str = "") -> None:
    global N
    N += 1
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {extra}")
        FAILED.append(label)


def jget(path: str):
    r = C.get(BASE + path)
    if r.status_code != 200:
        return {"__status": r.status_code, "__body": r.text[:200]}
    return r.json()


def jpost(path: str, payload: dict | None = None):
    r = C.post(BASE + path, json=payload or {})
    if r.status_code != 200:
        return {"__status": r.status_code, "__body": r.text[:200]}
    return r.json()


def status(path: str) -> int:
    return C.get(BASE + path).status_code


def text_of(path: str) -> tuple[int, str]:
    r = C.get(BASE + path)
    return r.status_code, r.text


def main() -> int:
    print("== 知识库端到端（真服务） ==")
    print(f"传输方式：{_api.MODE}")

    # ⚠ 这个探针**故意**要真的入库（它验的就是这条链路），所以它必须
    # ① 先清掉自己之前跑剩下的、标题为「知识库E2E」的残留；
    # ② 结尾把自己的数据删干净。绝不能碰用户真实导入的手账 ——
    #    那正是用户回头要找的东西。
    _prefix = "知识库E2E"
    for d in jget("/api/library").get("docs", []):
        if _prefix in (d.get("title") or ""):
            C.delete(BASE + "/api/library/" + quote(d["id"]))
    before_docs = len(jget("/api/library").get("docs", []))

    # ---------- 生成 → 自动入库 ----------
    r = jpost("/api/analyze-text",
              {"text": SAMPLE, "title": "知识库E2E", "level_id": "cet4"})
    check("生成成功", isinstance(r, dict) and "html" in r, str(r)[:200])
    lib = (r or {}).get("library") or {}
    doc = (lib.get("doc") or {}).get("id")
    check("自动写入知识库并返回 doc id", bool(doc), str(lib)[:200])
    check("note 里明说已入库",
          "已存入知识库" in ((r or {}).get("trans_note") or ""),
          (r or {}).get("trans_note") or "")
    cards = lib.get("cards") or {}
    check("三本卡片都收进了东西",
          cards.get("words", 0) > 0 and cards.get("patterns", 0) > 0
          and cards.get("grammar", 0) > 0, str(cards))

    # ---------- 读回 + 重渲染 ----------
    r2 = jget(f"/api/library/{doc}")
    check("按 id 读回手账", isinstance(r2, dict) and r2.get("doc_id") == doc,
          str(r2)[:160])
    check("读回的是结构化数据（无 html）", isinstance(r2, dict) and "html" not in r2)

    st, html = text_of(f"/api/library/{doc}/html")
    check("重渲染返回完整 HTML 页面",
          st == 200 and html.lstrip().startswith("<!DOCTYPE html")
          and "</html>" in html, f"{st} {html[:60]}")
    check("重渲染页面带标题", "知识库E2E" in html)
    check("重渲染页面有生词表", "生词表" in html)

    # ---------- 卡片本 ----------
    for kind, label in (("words", "生词本"), ("patterns", "句型本"),
                        ("grammar", "语法本")):
        d = jget(f"/api/library/cards/{kind}")
        check(f"{label}可读且非空",
              isinstance(d, dict) and d.get("total", 0) > 0, str(d)[:120])
        t = (d.get("items") or []) if isinstance(d, dict) else []
        check(f"{label}卡片带出处", bool(t) and all(i.get("sources") for i in t),
              str(t[:1])[:140])
        check(f"{label}卡片带例句（来自原文）",
              bool(t) and any(len(i.get("example") or "") > 10 for i in t))

    # ---------- 标记 ----------
    items = jget("/api/library/cards/words").get("items") or []
    key = items[0]["lemma"] if items else ""
    jpost(f"/api/library/cards/words/{key}/status",
          {"status": "known", "note": "e2e 标记"})
    again = jget("/api/library/cards/words?status=known")
    check("标记后按状态能查到",
          any(i["lemma"] == key and i["note"] == "e2e 标记"
              for i in (again.get("items") or [])),
          str((again.get("items") or [])[:1])[:160])
    st, exp = text_of("/api/library/cards/words/export.html?status=known")
    check("导出跟着筛选走（只印已掌握的）", st == 200 and key in exp, str(st))

    st, csv = text_of("/api/library/cards/words/export.csv")
    check("CSV 可下载且有表头",
          st == 200 and csv.lstrip("﻿").startswith("word,"), csv[:60])

    # ---------- 删除回滚 ----------
    before = jget("/api/library/cards/words")["total"]
    rr = C.delete(BASE + f"/api/library/{doc}")
    d3 = rr.json() if rr.status_code == 200 else {}
    check("删除成功", rr.status_code == 200 and d3.get("deleted") is True,
          f"{rr.status_code} {rr.text[:120]}")
    after = jget("/api/library/cards/words")["total"]
    check("删除后卡片回滚（生词本变少）", after < before, f"{after} vs {before}")
    check("删除后该篇不在列表里",
          not any(x["id"] == doc for x in jget("/api/library")["docs"]))
    check("删除后取回是 404", status(f"/api/library/{doc}") == 404,
          str(status(f"/api/library/{doc}")))

    # ---------- audit / 路由不被截胡 ----------
    check("audit 可用且干净",
          jget("/api/library/audit").get("problems") == [],
          str(jget("/api/library/audit"))[:160])

    # ---------- 收尾：确认自己没留下垃圾 ----------
    left = [d for d in jget("/api/library").get("docs", [])
            if _prefix in (d.get("title") or "")]
    check("探针跑完没留下自己的手账", left == [], str(left)[:160])
    check("探针没动用户的手账",
          len(jget("/api/library").get("docs", [])) == before_docs,
          f"{len(jget('/api/library').get('docs', []))} vs {before_docs}")

    print(f"\n{N - len(FAILED)}/{N} 通过")
    print(f"（传输方式：{_api.MODE}）")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())