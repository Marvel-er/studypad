"""
考点知识库自检。

这份库的价值全在「可溯源」，所以最重要的检查是：
**每一条 `src` 都必须指回 SOURCES 里真实存在的条目**。
一个写错的 key 会让「有据可查」变成「假装有据可查」。

另一个重点是时效性：TOEFL 这类改过制的考试，
新制与旧制必须标清生效区间，否则会答错。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import exam_points as ep  # noqa: E402

FAILS: list[str] = []
CHECKS = 0


def check(cond: bool, msg: str) -> None:
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(msg)


def collect_srcs(obj, path: str = "") -> list[tuple[str, str]]:
    """递归收集所有 (src_id, 出现位置)。"""
    found: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "src" and isinstance(v, list):
                for sid in v:
                    found.append((sid, path or "root"))
            else:
                found += collect_srcs(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += collect_srcs(v, f"{path}[{i}]")
    return found


# ---------------------------------------------------------------- 1. 结构
check(len(ep.ORDER) == 6, f"应有 6 档，实际 {len(ep.ORDER)}")
check(set(ep.ORDER) == set(ep.EXAM_POINTS.keys()),
      "ORDER 与 EXAM_POINTS 的键不一致")

for lid in ep.ORDER:
    d = ep.EXAM_POINTS[lid]
    check(d["id"] == lid, f"{lid}: id 字段不匹配")
    for key in ("label", "en", "profile", "vocabulary", "grammar",
                "question_types", "high_frequency", "focus", "sources"):
        check(key in d, f"{lid}: 缺字段 {key}")
    check(len(d["grammar"]["items"]) >= 4, f"{lid}: 语法条目过少（{len(d['grammar']['items'])}）")
    check(len(d["question_types"]["items"]) >= 4,
          f"{lid}: 题型条目过少（{len(d['question_types']['items'])}）")
    check(len(d["high_frequency"]) >= 3, f"{lid}: 高频考点过少")
    check(len(d["focus"]) >= 2, f"{lid}: 考查重点过少")
    check(d["vocabulary"].get("target"), f"{lid}: 缺词汇目标量")
    check(len(d["sources"]) >= 2, f"{lid}: 来源少于 2 条，溯源强度不足")

# ---------------------------------------------------------------- 2. 溯源
all_pairs = []
for lid in ep.ORDER:
    all_pairs += collect_srcs(ep.EXAM_POINTS[lid], lid)

check(len(all_pairs) >= 80, f"src 引用总数偏少（{len(all_pairs)}），覆盖不足")

bad = [(sid, where) for sid, where in all_pairs if sid not in ep.SOURCES]
check(not bad, f"存在无法溯源到 SOURCES 的 src（{len(bad)} 处）：{bad[:5]}")

# 每条 grammar / question_type / high_frequency / focus 都必须有 src
missing_src = []
for lid in ep.ORDER:
    d = ep.EXAM_POINTS[lid]
    for g in d["grammar"]["items"]:
        if not g.get("src"):
            missing_src.append(f"{lid}.grammar.{g.get('name')}")
    for q in d["question_types"]["items"]:
        if not q.get("src"):
            missing_src.append(f"{lid}.question_types.{q.get('name')}")
    for t in d["high_frequency"]:
        if not t.get("src"):
            missing_src.append(f"{lid}.high_frequency.{t.get('topic')}")
    for f in d["focus"]:
        if not f.get("src"):
            missing_src.append(f"{lid}.focus.{f.get('title')}")
check(not missing_src, f"有 {len(missing_src)} 条数据没标来源：{missing_src[:5]}")

# 每档的 sources 列表必须与其 entry 里的 src 有交集（不能挂着没用到的来源）
for lid in ep.ORDER:
    d = ep.EXAM_POINTS[lid]
    used = {sid for sid, _ in collect_srcs(d, lid)}
    declared = set(d["sources"])
    check(used <= declared,
          f"{lid}: 用到了未在 sources 里声明的来源 {used - declared}")

# ---------------------------------------------------------------- 3. 来源表
for sid, s in ep.SOURCES.items():
    check(s.get("tier") in ("official", "semi_official", "secondary", "oss"),
          f"{sid}: tier 非法（{s.get('tier')}）")
    for key in ("title", "publisher", "url", "accessed"):
        check(s.get(key), f"{sid}: 缺字段 {key}")
    check(bool(s.get("establishes")), f"{sid}: 缺 establishes 说明")

official = [k for k, v in ep.SOURCES.items() if v["tier"] == "official"]
check(len(official) >= 5, f"official 级来源过少（{len(official)}）")

# 每个来源都要有短标签，否则前端徽章会退化成生硬的 id
missing_short = [k for k in ep.SOURCES if k not in ep.SHORT]
check(not missing_short, f"来源缺短标签：{missing_short}")
orphan_short = [k for k in ep.SHORT if k not in ep.SOURCES]
check(not orphan_short, f"短标签指向不存在的来源：{orphan_short}")
check(all("short" in s for s in ep.sources_of("toefl")), "sources_of 未带 short 字段")

# ---------------------------------------------------------------- 4. 时效
# TOEFL 必须同时给出新旧两制，且旧制有明确的失效日期
toefl = ep.EXAM_POINTS["toefl"]
legacy = [q for q in toefl["question_types"]["items"] if q.get("effective_until")]
current = [q for q in toefl["question_types"]["items"] if not q.get("effective_until")]
check(bool(legacy), "TOEFL 缺旧制条目（2026-01-20 前的题型体系）")
check(bool(current), "TOEFL 缺新制条目")
check(toefl["profile"].get("effective_from") == "2026-01-21",
      "TOEFL 新制生效日期应为 2026-01-21")

# 提示层必须只注入现行题型条目（「旧制参考」前缀是已失效条目的标记）
ctx = ep.prompt_context("toefl")
check("【旧制参考】" not in ctx,
      "prompt_context 把已失效的题型条目也注入进去了")
# 反过来，现行题型一条都不能少
for q in current:
    check(q["name"] in ctx, f"prompt_context 漏了现行题型：{q['name']}")
for lid in ep.ORDER:
    c = ep.prompt_context(lid)
    check(len(c) <= ep._MAX_CHARS, f"{lid}: prompt_context 超过字数上限")
    check("【考试阶段】" in c, f"{lid}: prompt_context 缺阶段标识")
    check("【高频考点" in c, f"{lid}: prompt_context 缺高频考点")

# ---------------------------------------------------------------- 5. 关键事实
def qt(lid: str, keyword: str) -> dict | None:
    for q in ep.EXAM_POINTS[lid]["question_types"]["items"]:
        if keyword in q["name"] or keyword in q["section"]:
            return q
    return None


check(ep.EXAM_POINTS["cet4"]["profile"]["paper_count"] == "57 题", "CET4 题量应为 57")
check(ep.EXAM_POINTS["cet6"]["profile"]["paper_count"] == "57 题", "CET6 题量应为 57")
check("52" in ep.EXAM_POINTS["kaoyan"]["profile"]["paper_count"], "考研题量应含 52（英一）")
check(ep.EXAM_POINTS["high_school"]["vocabulary"]["target"] == 3500, "高中词汇应为 3500")
check(ep.EXAM_POINTS["cet4"]["vocabulary"]["target"] == 4500, "四级词汇应为 4500")
check(ep.EXAM_POINTS["cet6"]["vocabulary"]["target"] == 5500, "六级词汇应为 5500")
check(ep.EXAM_POINTS["kaoyan"]["vocabulary"]["target"] == 5500, "考研词汇应为 5500")
# 考研大纲词表已由独立仓库核实到 5,501 条，口径要写到正文里而不是只挂个 5500
check("5,501" in ep.EXAM_POINTS["kaoyan"]["vocabulary"]["basis"],
      "考研词汇依据应写明独立核实后的 5,501 条")
# 四六级词书的独立核对面必须挂上，否则「交叉验证」只存在于注释里
for lid, src_id in (("cet4", "oss_cet_wordbook"),
                    ("cet6", "oss_cet_wordbook"),
                    ("kaoyan", "oss_kaoyan_wordlist"),
                    ("ielts", "oss_ielts_spelling")):
    check(src_id in ep.EXAM_POINTS[lid]["sources"],
          f"{lid} 的来源列表缺独立核对面 {src_id}")
# 被丢弃的仓库（无有效产出）不能以任何形式出现在数据里
discarded = {k for k, v in ep.OSS_SOURCES.items() if v.get("usage") == "discarded"}
check(discarded, "应至少标记一个 discarded 仓库（english-wordlists-for-ocr 只有生成中的占位产出）")
leaked = [f"{lid}.{k}" for lid in ep.ORDER
          for k in discarded
          if k in ep.EXAM_POINTS[lid].get("sources", [])]
check(not leaked, f"discarded 仓库泄漏进了来源列表：{leaked}")
# share-alike 许可必须被显式记录 —— 自动检查漏判过一次
check("share-alike" in ep.OSS_SOURCES["openetymology/OpenEtymology"]["license"],
      "OpenEtymology 的 CC BY-SA 必须显式标注 share-alike")
check(ep.OSS_SOURCES["openetymology/OpenEtymology"]["usage"] == "cross_check_only",
      "share-alike 仓库只能是 cross_check_only")

# 分值合计校验（这部分最容易写错，逐个加）
cet4_listen = [q for q in ep.EXAM_POINTS["cet4"]["question_types"]["items"]
               if q["section"] == "听力"]
check(len(cet4_listen) == 3, f"CET4 听力应有 3 类，实际 {len(cet4_listen)}")
cet6_listen = [q for q in ep.EXAM_POINTS["cet6"]["question_types"]["items"]
               if q["section"] == "听力"]
check(len(cet6_listen) == 3, f"CET6 听力应有 3 类，实际 {len(cet6_listen)}")

# 雅思写作 Task 1 必须写明 >=150 词、Task 2 >=250 词
t1 = qt("ielts", "Task 1")
t2 = qt("ielts", "Task 2")
check(t1 and "150" in t1["detail"], "雅思 Task 1 应注明 >=150 词")
check(t2 and "250" in t2["detail"], "雅思 Task 2 应注明 >=250 词")

# ---------------------------------------------------------------- 6. 查询接口
check(ep.get("cet4") is not None, "get(cet4) 应为有效")
check(ep.get("nope") is None, "未知识别码应返回 None")
check(ep.require("nope")["id"] == "high_school", "require 兜底应回退到 high_school")
check(ep.section("cet6", "vocabulary")["target"] == 5500, "section 查询失败")
check(isinstance(ep.sources_of("ielts"), list), "sources_of 应返回列表")
check(len(ep.sources_of("ielts")) >= 3, "雅思来源应 >= 3")
check(len(ep.summary()) == 6, "summary 应返回 6 档")
check(ep.stats()["levels"] == 6, "stats.levels 应为 6")
check(ep.stats()["sources"] >= 10, "来源总数应 >= 10")
check(len(ep.grammar_names("kaoyan")) >= 4, "grammar_names 查询失败")
check(ep.get("CET4") is not None, "get 应大小写不敏感")

# ---------------------------------------------------------------- 7. 输出
if FAILS:
    print(f"[FAIL] {len(FAILS)} / {CHECKS} 项未通过\n")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)

s = ep.stats()
print(f"[OK] 全部 {CHECKS} 项通过\n")
print("知识库规模：")
print(f"  阶段数          {s['levels']}")
print(f"  来源条目        {s['sources']}（其中 official "
      f"{sum(1 for v in ep.SOURCES.values() if v['tier'] == 'official')}）")
print(f"  开源交叉校验源  {s['oss_sources']}")
print(f"  语法条目        {s['grammar_items']}")
print(f"  题型条目        {s['question_types']}")
print(f"  高频考点主题    {s['high_frequency_topics']}")
print(f"  考查重点        {s['focus_items']}")
print(f"  src 引用总数    {len(all_pairs)}")
print()
for lid in ep.ORDER:
    d = ep.EXAM_POINTS[lid]
    print(f"  {d['label']:<28} 词 {d['vocabulary']['target']:>6}  "
          f"语法 {len(d['grammar']['items']):>2}  题型 {len(d['question_types']['items']):>2}  "
          f"高频 {len(d['high_frequency']):>2}  来源 {len(d['sources'])}")
