"""
接口层自检：/api/exam-points 系列。

重点验证三件事：
1. 「有据可查」在**接口层**站得住 —— 返回体里必须带得出来源（tier + 链接）。
2. 非法阶段码要有明确 404，而不是静默兜底成别的阶段（静默兜底会让用户
   以为自己看的是雅思、其实是高中）。
3. `brief` 端点在没有大模型时必须走规则兜底且仍然带来源 ——
   「有据可查」不能依赖模型是否可用。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = ROOT / "out" / "_cfgtest_exam"
os.environ["STUDYPAD_HOME"] = str(TMP)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app import exam_points as ep  # noqa: E402

LOG: list[str] = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


c = TestClient(app)
LOG.append("")

# ---------------------------------------------------------------- 1. 索引
r = c.get("/api/exam-points")
check("GET /api/exam-points → 200", r.status_code == 200, str(r.status_code))
d = r.json()
check("索引含 6 档", len(d["levels"]) == 6, str(len(d.get("levels", []))))
check("索引含 stats", d["stats"]["levels"] == 6)
check("索引含来源总表", len(d["sources"]) >= 10, str(len(d.get("sources", {}))))
check("索引含开源交叉校验源", len(d["oss"]) >= 10, str(len(d["oss"])))
check("索引条目带 vocab_target",
      all(x.get("vocab_target") for x in d["levels"]))
check("索引不带正文（volume 控制）",
      all("grammar" not in x and "question_types" not in x for x in d["levels"]))
ids = [x["id"] for x in d["levels"]]
check("索引顺序与 ORDER 一致", ids == ep.ORDER, str(ids))

# 每一档的 json 必须可序列化（含中文）
import json as _json  # noqa: E402
try:
    _json.dumps(d, ensure_ascii=False)
    check("索引 JSON 可序列化", True)
except Exception as e:  # noqa: BLE001
    check("索引 JSON 可序列化", False, str(e))

# ---------------------------------------------------------------- 2. 详情
for lid in ep.ORDER:
    r = c.get(f"/api/exam-points/{lid}")
    check(f"GET /{lid} → 200", r.status_code == 200, str(r.status_code))
    body = r.json()
    p = body["point"]
    check(f"{lid}: 带 point/sources/sections",
          all(k in body for k in ("point", "sources", "sections")))
    check(f"{lid}: 六个维度齐全",
          all(k in p for k in ("profile", "vocabulary", "grammar",
                               "question_types", "high_frequency", "focus")))
    srcs = body["sources"]
    check(f"{lid}: 来源已展开（带 tier）",
          bool(srcs) and all("tier" in s for s in srcs), str(len(srcs)))
    check(f"{lid}: 来源带链接",
          all(s.get("url") for s in srcs))
    check(f"{lid}: 至少 1 条 official 来源",
          any(s["tier"] == "official" for s in srcs))

# ---------------------------------------------------------------- 3. 维度查询
r = c.get("/api/exam-points/cet4/vocabulary")
check("GET /cet4/vocabulary → 200", r.status_code == 200)
check("四级词汇 target=4500", r.json()["data"]["target"] == 4500)
check("维度查询也带回来源", bool(r.json()["sources"]))

r = c.get("/api/exam-points/toefl/question_types")
check("GET /toefl/question_types → 200", r.status_code == 200)
items = r.json()["data"]["items"]
check("托福题型含新旧两制",
      any(i.get("effective_until") for i in items) and
      any(not i.get("effective_until") for i in items))

r = c.get("/api/exam-points/kaoyan/focus")
check("GET /kaoyan/focus → 200", r.status_code == 200)
check("考研 focus 非空", len(r.json()["data"]) >= 2)

# ---------------------------------------------------------------- 4. 错误处理
r = c.get("/api/exam-points/nope")
check("未知阶段 → 404（不静默兜底）", r.status_code == 404, str(r.status_code))
r = c.get("/api/exam-points/cet4/nope")
check("未知维度 → 404", r.status_code == 404, str(r.status_code))
r = c.post("/api/exam-points/nope/brief", json={"use_llm": False})
check("未知阶段 brief → 404", r.status_code == 404, str(r.status_code))

# ---------------------------------------------------------------- 5. brief 兜底
r = c.post("/api/exam-points/ielts/brief", json={"use_llm": False})
check("brief（不用模型）→ 200", r.status_code == 200, str(r.status_code))
b = r.json()
check("brief 走规则模式", b["mode"] == "rule", b.get("mode", ""))
check("brief 带来源", len(b["sources"]) >= 3, str(len(b.get("sources", []))))
check("brief 正文含依据行", "依据" in b["brief"])
check("brief 正文含阶段名", "雅思" in b["brief"])
check("brief 正文含词汇目标", "8000" in b["brief"])

# 即使声称用模型但没有 Key，也必须降级成功且仍然有据
r = c.post("/api/exam-points/kaoyan/brief", json={"use_llm": True})
check("brief（声称用模型但无 Key）→ 降级成功", r.status_code == 200)
b = r.json()
check("降级后仍为 rule 模式", b["mode"] == "rule")
check("降级后仍带来源", len(b["sources"]) >= 2)

# 六档 brief 全都要能出
for lid in ep.ORDER:
    r = c.post(f"/api/exam-points/{lid}/brief", json={"use_llm": False})
    ok = r.status_code == 200 and len(r.json()["brief"]) > 120
    check(f"brief /{lid} 内容充实", ok, str(len(r.json().get("brief", ""))))

# ---------------------------------------------------------------- 6. 与 /api/levels 联动
r = c.get("/api/levels")
check("GET /api/levels 仍正常", r.status_code == 200)
d = r.json()
check("/api/levels 带 exam_points 统计", "exam_points" in d)
check("/api/levels 阶段数仍为 6", len(d["levels"]) == 6)
check("level id 与考点库 id 完全对齐",
      {x["id"] for x in d["levels"]} == set(ep.ORDER),
      str({x["id"] for x in d["levels"]} ^ set(ep.ORDER)))

# ---------------------------------------------------------------- 7. 提示注入
ctx = ep.prompt_context("kaoyan")
check("考研提示上下文含阶段名", "考研" in ctx)
check("考研提示上下文含高频考点", "【高频考点" in ctx)
check("考研提示上下文含重点语法", "【重点语法】" in ctx)
check("考研提示上下文不含旧制标记", "【旧制参考】" not in ctx)

LOG.append("")
LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
(ROOT / "out" / "_examapi_test.txt").write_text("\n".join(LOG), encoding="utf-8")
print(f"PASS={PASS} FAIL={FAIL}")

if TMP.exists():
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()
