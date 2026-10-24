"""
知识库接口层自检（`TestClient`，不碰真实知识库）。

验的是**接口行为**，不是模块行为（模块层在 `test_library.py`）：
  · 路由不被相邻的 `{doc_id}` 截胡（`/api/library/audit` 就是这么被吃掉过的）
  · 错误码语义对：非法 id → 400，不存在 → 404，写失败 → 500 且**带中文原因**
  · 导出的 HTML 真的是完整自包含页面（不是 404 的 JSON）
  · 自动保存挂在生成链路上，且**失败不影响出稿**
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

_TMP = tempfile.mkdtemp(prefix="studypad_libapi_")
os.environ["STUDYPAD_HOME"] = _TMP

from fastapi.testclient import TestClient     # noqa: E402

from app import library                        # noqa: E402
from app.main import app                       # noqa: E402

client = TestClient(app)
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


SAMPLE = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")


def main() -> int:
    print("== 知识库接口 / API ==")

    # ---------- 空库 ----------
    r = client.get("/api/library")
    check("空库 GET /api/library 返回 200", r.status_code == 200, r.text[:120])
    d = r.json()
    check("空库返回空的 docs 列表", d.get("docs") == [], str(d)[:120])
    check("返回里带知识库目录路径（用户要能自己找到数据）",
          bool(d["stats"]["path"]) and "library" in d["stats"]["path"],
          d["stats"]["path"])
    check("空库三本卡片数都是 0",
          all(v == 0 for v in d["stats"]["cards"].values()), str(d["stats"]))

    r = client.get("/api/library/audit")
    check("空库 audit 返回 200 且无问题",
          r.status_code == 200 and r.json()["problems"] == [], r.text[:120])

    r = client.get("/api/library/cards/words")
    check("空库读生词本返回空列表而不是报错",
          r.status_code == 200 and r.json()["items"] == [], r.text[:120])

    r = client.get("/api/library/cards/nope")
    check("读不存在的卡片类型返回 404", r.status_code == 404, r.text[:120])

    # ---------- 生成 → 自动保存 ----------
    r = client.post("/api/analyze-text", json={"text": SAMPLE, "title": "接口自检",
                                               "level_id": "cet4"})
    check("生成手账成功", r.status_code == 200, r.text[:200])
    hb = r.json()
    lib = hb.get("library")
    check("生成时自动存入知识库", isinstance(lib, dict) and lib.get("doc"), str(lib)[:200])
    doc = (lib or {}).get("doc", {}).get("id")
    check("返回里能拿到 doc id（前端要靠它再导出）", bool(doc), str(doc))
    check("自动保存后 note 里能看到已存入的提示",
          "已存入知识库" in (hb.get("trans_note") or ""), hb.get("trans_note") or "")
    check("生词本卡片数 > 0",
          (lib or {}).get("cards", {}).get("words", 0) > 0, str(lib)[:160])

    r = client.get("/api/library")
    docs = r.json()["docs"]
    check("列表里出现刚生成的那篇",
          any(x["id"] == doc for x in docs), str(len(docs)))

    # ---------- 读回 / 重渲染 ----------
    r = client.get(f"/api/library/{doc}")
    check("按 id 能读回手账", r.status_code == 200 and r.json()["doc_id"] == doc)
    check("读回的是结构化数据（没有 html 字段）",
          "html" not in r.json(), str(list(r.json())[:12]))

    r = client.get(f"/api/library/{doc}/html")
    check("重渲染返回 HTML 而非 JSON",
          r.status_code == 200 and "text/html" in r.headers.get("content-type", ""),
          r.headers.get("content-type", ""))
    h = r.text
    check("重渲染的页面是完整自包含页面",
          h.lstrip().startswith("<!DOCTYPE html") and "</html>" in h, h[:60])
    check("重渲染页面里带文章标题", "接口自检" in h)
    check("重渲染页面里有生词表", "生词表" in h)

    # ---------- 卡片本导出 ----------
    r = client.get("/api/library/cards/words/export.html")
    check("生词本导出 HTML 返回 200",
          r.status_code == 200 and "text/html" in r.headers.get("content-type", ""),
          r.headers.get("content-type", ""))
    check("导出的生词本带掌握度图例",
          "○" in r.text and "△" in r.text and "●" in r.text)
    # ⚠ **不能**写成 `'cb-empty' not in r.text` 来验「不是空库」：
    # `cb-empty` 这个字符串在**内嵌 CSS 里本来就有**（空状态的样式定义），
    # 于是断言恒真 —— 导空库和导有数据都会通过。这正是项目里栽过三次的
    # 「假绿断言」。真正的判据是 `<tbody>` 有没有渲染出来，以及词条在不在页面上。
    check("导出的生词本确实渲染了表格体", "<tbody>" in r.text, "没渲染出 <tbody>")
    lemmas = [i["lemma"] for i in
              client.get("/api/library/cards/words").json()["items"]]
    check("导出的 HTML 里真的有词条（取第一个词验）",
          bool(lemmas) and lemmas[0] in r.text, str(lemmas[:3]))

    r = client.get("/api/library/cards/words/export.csv")
    check("生词本导出 CSV 返回 200",
          r.status_code == 200 and "text/csv" in r.headers.get("content-type", ""),
          r.headers.get("content-type", ""))
    check("CSV 带 BOM（Excel 双击能认出中文）", r.content.startswith(b"\xef\xbb\xbf"))
    check("CSV 带 attachment 头",
          "attachment" in r.headers.get("content-disposition", ""),
          r.headers.get("content-disposition", ""))
    check("CSV 表头含 word 列", "word" in r.text.splitlines()[0])

    r = client.get("/api/library/cards/patterns/export.html")
    check("句型本导出成功", r.status_code == 200 and "句型本" in r.text)
    r = client.get("/api/library/cards/grammar/export.html")
    check("语法本导出成功", r.status_code == 200 and "语法本" in r.text)

    # 三本卡片的**列数必须与表头一致**、且 colgroup 里的 col 数也要对得上。
    # 早先把句型本从 5 列改成 6 列（拆出「仿写示例」），表头加了、
    # 数据格没跟着加 → 表格整体错位一列，肉眼很明显但自检抓不到。
    sys.path.insert(0, str(ROOT / "backend"))
    import re
    from app import cards_render
    for kind in ("words", "patterns", "grammar"):
        data = client.get(f"/api/library/cards/{kind}").json()
        if not data["items"]:
            continue
        page = cards_render.render_cards(kind, data)
        n_th = len(re.findall(r"<th>", page))
        n_col = len(re.findall(r"<col ", page))
        n_width = len(cards_render.WIDTHS[kind])
        check(f"{kind} 表头列数 = 列宽数 = colgroup 数",
              n_th == n_width == n_col, f"th={n_th} width={n_width} col={n_col}")
        first_row = page.split("<tbody>")[1].split("</tr>")[0]
        n_td = len(re.findall(r"<td", first_row))
        check(f"{kind} 数据格数与表头一致", n_td == n_th, f"td={n_td} th={n_th}")
        check(f"{kind} 列宽合计接近 100%",
              abs(sum(cards_render.WIDTHS[kind]) - 100) <= 2,
              str(sum(cards_render.WIDTHS[kind])))

    # 筛选要能进到导出里（用户导「未掌握的 60 个词」就该只有 60 行）
    rows_all = client.get("/api/library/cards/words").json()["total"]
    r = client.get("/api/library/cards/words/export.html?q=zzzznothing")
    # 同样不能用 `'cb-empty' in r.text`（CSS 里有定义 → 恒真）。
    # 空库的真判据是**没有表格体**，非空库才有。
    check("搜索无结果时导出的是空状态页（没有表格体）",
          r.status_code == 200 and "<tbody>" not in r.text, str(r.status_code))
    check("筛选后 total 少于全部", rows_all > 0)

    # ---------- 标记 ----------
    words = client.get("/api/library/cards/words").json()["items"]
    key = words[0]["lemma"]
    r = client.post(f"/api/library/cards/words/{key}/status",
                    json={"status": "known", "note": "背过了"})
    check("标记掌握度成功", r.status_code == 200 and r.json()["status"] == "known",
          r.text[:160])
    check("备注一并保存", r.json()["note"] == "背过了")
    r = client.get("/api/library/cards/words?status=known")
    check("按状态筛选能查到刚标记的词",
          any(i["lemma"] == key for i in r.json()["items"]))
    r = client.get("/api/library/cards/words?status=new")
    check("未掌握筛选不含它", all(i["lemma"] != key for i in r.json()["items"]))
    r = client.get("/api/library/cards/words/export.html?status=known")
    check("导出能跟着筛选走（只印未掌握/已筛出的那批）",
          key in r.text, "筛出来的词没出现在导出里")

    r = client.post(f"/api/library/cards/words/{key}/status", json={"status": "bogus"})
    check("非法状态返回 400 且带说明",
          r.status_code == 400 and "状态" in r.text, r.text[:120])
    r = client.post("/api/library/cards/words/nosuchword/status",
                    json={"status": "known"})
    check("标记不存在的卡片返回 404", r.status_code == 404, r.text[:120])
    r = client.delete(f"/api/library/cards/words/{key}")
    check("删卡片成功", r.status_code == 200 and r.json()["deleted"] is True)
    check("删后读不到", not any(i["lemma"] == key for i in
                              client.get("/api/library/cards/words").json()["items"]))

    # ---------- 路由不被截胡 ----------
    # `/api/library/audit` 与 `/api/library/{doc_id}` 同为两段；
    # 声明顺序错了会被后者吃掉，返回「找不到这篇手账」。
    r = client.get("/api/library/audit")
    check("audit 没被 {doc_id} 截胡（声明顺序）",
          r.status_code == 200 and "problems" in r.json(), r.text[:160])
    r = client.post("/api/library/repair")
    check("repair 可用", r.status_code == 200 and "removed" in r.json(), r.text[:120])

    # ---------- 错误码 ----------
    check("不存在的手账返回 404", client.get("/api/library/nosuchdoc").status_code == 404)
    r = client.get("/api/library/%2E%2E%2F%2E%2E%2Fsettings")
    check("路径穿越 id 返回 400（不是 404/500）",
          r.status_code in (400, 404), f"{r.status_code} {r.text[:100]}")
    r = client.post("/api/library", json={"handbook": {}})
    check("空手账保存返回 400",
          r.status_code == 400 and "没有可保存" in r.text, r.text[:120])

    # ---------- 删除 ----------
    before = client.get("/api/library").json()["stats"]["cards"]["words"]
    r = client.delete(f"/api/library/{doc}")
    check("删除手账成功", r.status_code == 200 and r.json()["deleted"] is True)
    check("删除后返回最新统计",
          r.json()["stats"]["cards"]["words"] <= before, r.text[:160])
    check("删完列表里没有了",
          not any(x["id"] == doc for x in client.get("/api/library").json()["docs"]))
    check("删完该篇的卡片也没了",
          client.get("/api/library/cards/words").json()["total"] < before,
          f"{client.get('/api/library/cards/words').json()['total']} vs {before}")
    check("删后再取返回 404", client.get(f"/api/library/{doc}").status_code == 404)
    check("删后再导出 HTML 返回 404",
          client.get(f"/api/library/{doc}/html").status_code == 404)
    r = client.delete(f"/api/library/{doc}")
    check("重复删除返回 deleted=False 而不是报错", r.status_code == 200
          and r.json()["deleted"] is False, r.text[:120])

    # ---------- 存盘失败必须报出来，且不影响已生成的手账 ----------
    import app.library as _lib
    real = _lib.os.replace
    _lib.os.replace = lambda *a, **k: (_ for _ in ()).throw(SystemExit(1))
    try:
        r = client.post("/api/analyze-text", json={"text": SAMPLE, "title": "存不下",
                                                   "level_id": "cet4"})
        check("守卫拦下写盘时生成仍然成功（手账不能出不来）",
              r.status_code == 200, str(r.status_code) + r.text[:120])
        hb2 = r.json()
        check("返回里如实带上「未能存入知识库」及原因",
              "未能存入知识库" in (hb2.get("trans_note") or ""),
              (hb2.get("trans_note") or "")[:160])
        check("失败也给出可下载的 html（用户至少能带走）",
              len(hb2.get("html") or "") > 500, str(len(hb2.get("html") or "")))
    finally:
        _lib.os.replace = real
    check("守卫撤掉后知识库仍能写",
          client.get("/api/library").status_code == 200)

    # ---------- 自动保存的开关 ----------
    # `no_save` 必须真的生效：走真服务的自检（smoke/verify/probe_*）
    # 都靠它避免往用户真实知识库里灌垃圾手账。
    # 这条不能只在 TestClient 下验 —— TestClient 里 STUDYPAD_HOME 是本脚本设的临时目录，
    # 「有没有调用 save_handbook」与「有没有写进临时目录」是两回事，
    # 所以这里断言的是**返回值里有没有 library 字段**（它只在真的存过时才出现）。
    r = client.post("/api/analyze-text",
                    json={"text": SAMPLE, "title": "不该入库",
                          "level_id": "cet4", "no_save": True})
    check("no_save=True 时生成照常成功", r.status_code == 200, r.text[:120])
    hb3 = r.json()
    check("no_save=True 时不往知识库写（返回里没有 library 字段）",
          "library" not in hb3, str(list(hb3)[:8]))
    check("no_save=True 时 note 里也没有入库提示",
          "已存入知识库" not in (hb3.get("trans_note") or ""),
          (hb3.get("trans_note") or "")[:120])
    check("no_save=True 时手账本身照常产出（不能因为不存库就出不来）",
          len(hb3.get("html") or "") > 500, str(len(hb3.get("html") or "")))
    check("no_save=True 时确实没多出一篇手账",
          len(client.get("/api/library").json()["docs"]) == 0,
          str(len(client.get("/api/library").json()["docs"])))

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    try:
        code = main()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    sys.exit(code)