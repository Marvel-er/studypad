"""
拆页后的**跨页导航链路**自检（2026-10-15）。

知识库从 `index.html` 拆到 `library.html` 之后，最容易悄悄断掉的是
「两个页面之间怎么走过去」。这类问题的共同特点是：
**任何单页自检都不会红** —— 每页单独看都好好的，只有点下去才发现走不通。

本探针守住三条链路：
  1. 两页互指的入口都在（顶栏 nav + 返回按钮）；
  2. `/library` 路由真的存在且返回的是知识库页（不是主页内容）；
  3. 「打开历史手账」跨页传参能闭环：知识库给出 `/?doc=<id>`，
     主页真的会按这个 id 去取数据并渲染（两端都要能对上同一个 id）。

跑法：
    python scripts/run_selftest.py scripts/test_pages.py out/_pages.txt
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

_TMP = tempfile.mkdtemp(prefix="studypad_pages_")
os.environ["STUDYPAD_HOME"] = _TMP

STATIC = ROOT / "backend" / "static"
INDEX = (STATIC / "index.html").read_text(encoding="utf-8")
LIBRARY = (STATIC / "library.html").read_text(encoding="utf-8")

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


def main() -> int:
    print("== 页面拆分 / 跨页导航 ==")

    # ---------- 1. 页面职责已分离 ----------
    check("主页不再含知识库面板", 'id="kbCard"' not in INDEX)
    check("主页不再含知识库脚本", "function kbRender" not in INDEX
          and "var KB = {" not in INDEX)
    check("主页不再引用 kbCard 的 id", "kbCard" not in INDEX)
    check("知识库页确实是独立文件", 'id="kbCard"' in LIBRARY
          or 'id="kbBody"' in LIBRARY)
    check("知识库页含四本卡片", all(k in LIBRARY for k in
          ("data-k=\"docs\"", "data-k=\"words\"", "data-k=\"patterns\"",
           "data-k=\"grammar\"")))

    # ---------- 2. 两页互指的入口 ----------
    for name, html, other in (("主页", INDEX, "/library"),
                              ("知识库页", LIBRARY, "/")):
        check(f"{name}顶栏有指向 {other} 的入口", f'href="{other}"' in html)
        check(f"{name}声明了自己的 data-page",
              re.search(r'<body[^>]+data-page="(\w+)"', html) is not None)
    check("知识库页有明显的返回入口",
          "返回制作" in LIBRARY, "找不到返回按钮")
    check("顶栏导航有 current 页高亮机制",
          "data-p=" in INDEX and "data-p=" in LIBRARY and
          "data-p" in (STATIC / "common.js").read_text(encoding="utf-8"))

    # ---------- 3. 公共层接线 ----------
    for name, html in (("主页", INDEX), ("知识库页", LIBRARY)):
        check(f"{name}引了 common.css", 'href="/static/common.css"' in html)
        check(f"{name}引了 common.js", 'src="/static/common.js"' in html)
        # 顺序：common.js 必须在内联 script 之前，否则 $ / api 未定义。
        # ⚠ **必须从 <body> 之后开始找** —— <head> 里本来就有一块
        # 「防闪烁」的内联 script（主题用，故意放在 common.js 之前），
        # 从文件开头找 `<script>` 会把它当成页面脚本，位置判定必错。
        body = html[html.find("<body"):]
        ci = body.find('src="/static/common.js"')
        m = re.search(r"<script>(?![\s\S]{0,40}?src=)", body)
        si = m.start() if m else -1
        check(f"{name}的 common.js 在页面脚本之前",
              ci > 0 and si > 0 and ci < si, f"common={ci} inline={si}")
    common = (STATIC / "common.js").read_text(encoding="utf-8")
    for fn in ("function esc", "function api", "function fmtDateTime"):
        check(f"common.js 提供 {fn.split(' ')[1]}", fn in common)

    # ---------- 4. 路由 ----------
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.get("/")
    check("GET / 返回主页", r.status_code == 200 and 'data-page="home"' in r.text,
          str(r.status_code))
    for path in ("/library", "/library/"):
        r = client.get(path)
        check(f"GET {path} 返回知识库页",
              r.status_code == 200 and 'data-page="library"' in r.text,
              str(r.status_code))
        check(f"{path} 不是主页内容", 'id="kbBody"' in r.text)
    r = client.get("/static/common.css")
    check("GET /static/common.css 可访问",
          r.status_code == 200 and "--accent" in r.text, str(r.status_code))
    r = client.get("/static/common.js")
    check("GET /static/common.js 可访问",
          r.status_code == 200 and "function esc" in r.text, str(r.status_code))
    r = client.get("/library/nope")
    check("不存在的路径仍是 404（没有把 /library/* 全吃掉）",
          r.status_code in (404, 307, 308), str(r.status_code))

    # ---------- 5. 「打开历史手账」跨页闭环 ----------
    check("知识库页的「打开」跳向主页并带 doc id",
          "location.href = '/?doc='" in LIBRARY
          or "location.href = '/?doc=' + encodeURIComponent(d.id)" in LIBRARY,
          "找不到跳转语句")
    check("主页会按 ?doc= 取数据",
          "/api/library/' + encodeURIComponent(id)" in INDEX)
    check("主页对历史手账清了 S.file/S.text",
          "S.file = null" in INDEX and "S.text = null" in INDEX,
          "不清的话点「重新生成」会拿历史数据当新材料")
    check("主页的「重新开始」会丢掉 doc 参数",
          "location.search" in INDEX,
          "否则从知识库进来后「重新开始」清不掉")

    # 真跑一次闭环：生成 → 入库 → 按 id 取回 → 主页据其渲染
    sample = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
    r = client.post("/api/analyze-text",
                    json={"text": sample, "title": "跨页闭环", "level_id": "cet4"})
    check("生成成功", r.status_code == 200, r.text[:160])
    doc = ((r.json().get("library") or {}).get("doc") or {}).get("id")
    check("入库拿到 doc id", bool(doc), str(r.json().get("library"))[:160])
    r = client.get("/api/library/" + quote(doc, safe=""))
    check("按 id 能取回（主页跳转后要靠它）", r.status_code == 200, str(r.status_code))
    got = r.json()
    check("取回的是结构化手账（有 blocks 与标题）",
          bool(got.get("blocks")) and got.get("title") == "跨页闭环")
    check("取回的内容可直接重渲染（导出路径同一份数据）",
          client.get("/api/library/" + quote(doc, safe="") + "/html").status_code
          == 200)
    # 清理
    client.delete("/api/library/" + quote(doc, safe=""))

    # ---------- 6. 首屏密度 ----------
    # 考点面板默认展开会把「上传材料」挤出首屏 —— 层级上它是「了解」不是「操作」
    check("考点面板默认折叠",
          re.search(r"<details[^>]*id=\"epDetails\"", INDEX) is not None
          and '<details open id="epDetails"' not in INDEX,
          "考点面板仍是默认展开的")
    # 这条原本写成「主页 < 40000 字符」—— 用体积当「知识库已拆走」的代理指标。
    # 2026-10-15 踩了：主页加了「翻译模型设置」面板 + 修 ?doc= 载入历史手账，
    # 体积自然涨到 43k，**功能是对的，却把这条判红了**。
    # 体积是代理，意图是「知识库那套东西别又长回主页」—— 所以直接验意图：
    # 主页里不许出现只有知识库页才有的东西（列表容器、卡片本导出、KB 状态对象）。
    # 体积只留一个宽松的上界当兜底：真把知识库页整体并回主页会到 70k 量级。
    lib_markers = ['id="kbBody"', "kbExportCsv", "KB.docs", "id=\"kbTab"]
    leaked = [m for m in lib_markers if m in INDEX]
    check("主页没有知识库页的东西（拆页没回流）", not leaked,
          f"混进了 {leaked}" if leaked else "4 个知识库专属标记都不在主页")
    check("主页体积仍在合理范围（兜底：没把整页并回来）", len(INDEX) < 60000,
          f"{len(INDEX)} 字符")

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    try:
        code = main()
    finally:
        import shutil
        shutil.rmtree(_TMP, ignore_errors=True)
    sys.exit(code)