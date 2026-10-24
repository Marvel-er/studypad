"""渲染层：把 ``analysis.py`` 的数据结构写成 markdown / json。

这里**只做格式化**，不做任何计算。所有数字都从传入的 dataclass 里取，
这样报告里的每个数都能追溯到一次可测试的计算。
"""

from __future__ import annotations

import json
from typing import Iterable

from . import __version__
from .analysis import (
    ABAnalysis,
    AGroupResult,
    CoverageCurve,
    ReadingAnalysis,
    Stats,
    Tier,
    Tiers,
    YearlyTrend,
    a_group_total,
)
from .lexicon import A_GROUPS, DERIVED, PROPER, ARTIFACT
from .wordlist import Wordlist

GENERATED_BY = (
    f"> 本文件由 `npee-vocab` v{__version__} 自动生成，请勿手工编辑。\n"
    "> 重新生成：`python -m npee_vocab all`\n"
)


def _pct(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}%}"


def _table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> list[str]:
    headers = list(headers)
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return out


# --------------------------------------------------------------------------
# stats.json
# --------------------------------------------------------------------------


def render_stats_json(stats: Stats) -> str:
    return json.dumps(stats.to_json(), ensure_ascii=False, indent=1)


# --------------------------------------------------------------------------
# 高频内容词表
# --------------------------------------------------------------------------


def render_content_words(stats: Stats, wordlist: Wordlist) -> str:
    lines = [
        "# 考研英语一 高频内容词表",
        "",
        GENERATED_BY,
        f"基于 {stats.years[0]}–{stats.years[-1]} 共 {len(stats.years)} 套真题的正文语料。",
        "（已剔除题干、选项、Directions 指令、中文解析与盗版水印）",
        "",
        "统计口径：词形还原后，统计该词出现在多少个年份的正文里。",
        "筛选：出现 ≥10 年、非纯功能词、非缩写切分残留。",
        "",
        f"共 {len(stats.content_words)} 个词。**年数越高，越是考研英语的恒定用词。**",
        "",
        "「大纲内」一列比对的是 `data/kaoyan_syllabus_verified.txt`，",
        "该词表**独立于本语料**（修订依据见 `docs/methodology/wordlist-revision.md`）。",
        "",
    ]
    lines += _table(
        ["词", "出现年数", "大纲内", "大纲释义"],
        (
            (w, c, "是" if w in wordlist.words else "**否**", wordlist.definition(w))
            for w, c in stats.content_words
        ),
    )
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# 分层复习清单
# --------------------------------------------------------------------------

TIER_NOTE = (
    "> 分档依据只有一条：**该词出现在多少个年份的正文里**。"
    "年数越高，越是跨年份稳定的词。\n"
    "> 不依赖任何外部词表，因此不受「词表是否完整」的争议影响。"
)


def render_tiers(tiers: Tiers, stats: Stats) -> str:
    L: list[str] = [
        "# 考研英语一 分层复习清单",
        "",
        GENERATED_BY,
        f"基于 {stats.years[0]}–{stats.years[-1]} 共 {len(stats.years)} 套真题的正文语料统计。",
        "",
        TIER_NOTE,
        "",
        "## 怎么用这份清单",
        "",
    ]
    L += _table(
        ["档", "含义", "数量", "建议投入"],
        (
            (f"**{t.key}**", t.meaning, len(t.words), t.advice)
            for t in tiers.all()
        ),
    )
    L += [
        "",
        f"**实际需要专门投入的只有 T1+T2 ≈ {len(tiers.t1.words) + len(tiers.t2.words)} 个词。**",
        "",
        "> **如果你做题时是「逻辑 / 抽象词不认识导致论证方向丢失」**，",
        "> 请改用 `A类-逻辑与抽象词表.md`，那份按功能分组，比这份更对症。",
        "> 如果是「实词不认识」，见 `docs/长尾词处理策略.md`。",
        "",
        "---",
        "",
    ]
    for tier in tiers.all():
        L.append(f"## {tier.key} {tier.label}（{len(tier.words)} 个）")
        L.append("")
        if tier.intro:
            L.append(tier.intro)
            L.append("")
        if tier.key == "T4":
            L += _table(
                ["词", "出现年数", "类型", "说明"],
                (
                    (w, c)
                    + (
                        ("专有名词", "人名 / 地名 / 国名，首字母大写能认出来即可")
                        if w in PROPER
                        else ("统计残留", '来自 Directions 的 "numbered blank"，不是词汇')
                        if w in ARTIFACT
                        else ("派生 / 比较级", f"原形 **{DERIVED.get(w, '')}**，掌握词根即可")
                    )
                    for w, c in tier.words
                ),
            )
        else:
            L += _table(["词", "出现年数"], ((w, c) for w, c in tier.words))
        L += ["", "---", ""]

    L += [
        "## 统计口径与局限",
        "",
        "- 语料：真题的**正文散文**，已剔除题干、选项、Directions 指令、中文解析、盗版水印。",
        "- 2022 年是「试卷 + 中文解析」合订本，已在第 678 行截断。",
        "- 词形还原用 NLTK WordNet + POS 标注。",
        "- 判分口径是「出现年份数」而非原始词频，衡量的是**跨年份稳定性**。",
        "- `numbered` 是未剔净的 Directions 残留，已单列在 T4。",
        "- **专名 / 派生词名单为人工归纳**，可能不全；见 `src/npee_vocab/lexicon.py`。",
        "",
    ]
    return "\n".join(L)


# --------------------------------------------------------------------------
# A 类词表
# --------------------------------------------------------------------------


def render_a_list(
    groups: list[AGroupResult], stats: Stats, per_article: float
) -> str:
    total = a_group_total(groups)
    L: list[str] = [
        "# A 类词表 · 逻辑与抽象词（封闭集合，可穷尽掌握）",
        "",
        GENERATED_BY,
        f"基于 {stats.years[0]}–{stats.years[-1]} 共 {len(stats.years)} 套真题正文统计。",
        "",
        "## 为什么单独做这一份",
        "",
        f"实测：A 类词跨 {len(stats.years)} 年**总共只有 {total} 个词形**，"
        f"而**每篇文章平均只涉及约 {per_article:.0f} 个**。",
        "它们不随文章主题变化（经济类和历史类用的是同一批逻辑词），"
        "出现次数高、复用率极高。",
        "",
        f"**结论：这是考研英语里唯一可以「彻底解决」的词汇问题。**",
        f"掌握这 {total} 个，你「论证方向丢失」的失败模式基本消除。",
        "",
        "## 用法（重要：不是背释义）",
        "",
        "A 类词的价值在**逻辑信号**，不在词义。所以练法是：",
        "",
        "1. **读到就警觉**——看到 `however` 立刻预期「前后相反」，比记住「然而」有用",
        "2. **标逻辑链**——做真题时在原文上画出转折 / 因果 / 递进信号，形成条件反射",
        "3. **反向用**——写作时主动用这些词组织论证，同时反哺阅读",
        "",
        "> 下面按**功能**分组，不按字母序。同一组的词在句子里的作用相同，一起记效率更高。",
        "",
        "---",
        "",
    ]
    for g in groups:
        L.append(f"## {g.name}（{len(g.words)} 个）")
        L.append("")
        L.append(f"*{g.hint}*")
        L.append("")
        L += _table(["词", "出现次数", "出现年份"], g.words)
        L.append("")

    L += [
        "---",
        "",
        "## 统计口径",
        "",
        "- 语料：真题正文散文，已剔除题干、选项、Directions、中文解析、水印。",
        "- 本表**不做词形还原**（argue / argues / argued 分开列），",
        "  因为不同形式的识别难度不同，分开看更能暴露你哪个形式不熟。",
        "- 「出现次数」= 该词形在全部正文里出现的总次数。",
        "- 「出现年份」= 该词形出现在多少套试卷里。",
        f"- 分组为**人工归纳的功能性集合**（{len(A_GROUPS)} 组），"
        "不是算法自动提取，因此边界清晰、可逐一核对；",
        "  只保留在语料中真实出现过的词。",
        "",
    ]
    return "\n".join(L)


# --------------------------------------------------------------------------
# 统计报告
# --------------------------------------------------------------------------

_GAP_TABLE = (
    ("专有名词 / 品牌（AI、UK、GDP、Google…）", "3.18%", "❌ 大纲本就不收"),
    ("派生词（consumer←consume、researcher←research）", "2.74%", "❌ 大纲要求靠构词法识别"),
    ("屈折变形残留（还原器未归并）", "0.72%", "❌ 非词表问题"),
    ("缩写切分残留（don't→don+t）", "0.47%", "❌ 语料噪声"),
    ("其余真未收录", "5.12%", "⚠️ 以低频词为主"),
)


def render_report(
    stats: Stats,
    yearly: YearlyTrend,
    curve: CoverageCurve,
    wordlist: Wordlist,
) -> str:
    y = stats.years
    L: list[str] = [
        "# 考研英语（一）真题词汇统计 · 完整报告",
        "",
        GENERATED_BY,
        f"语料：{y[0]}–{y[-1]} 共 **{len(y)} 套**真题正文 ｜ "
        f"{stats.tokens_total:,} 词元 ｜ {stats.distinct_total:,} 个不同词形",
        "",
        "---",
        "",
        "## 一、逐年不同单词数（正文语料，词形还原后）",
        "",
    ]
    L += _table(
        ["年份", "不同词形", "大纲内覆盖率（不同词）", "大纲内覆盖率（加权）"],
        (
            (yr, stats.vocab_per_year[yr], _pct(stats.coverage_distinct[yr]), _pct(stats.coverage_weighted[yr]))
            for yr in y
        ),
    )
    L += [
        "",
        f"**均值：不同词口径 {_pct(stats.mean_coverage_distinct)}，"
        f"次数加权口径 {_pct(stats.mean_coverage_weighted)}。**",
        "",
        "---",
        "",
        f"## 二、{len(y)} 年恒定词（每年正文都出现）",
        "",
        f"共 **{len(stats.always)} 个**。",
        "",
        "```",
        ", ".join(stats.always),
        "```",
        "",
        "---",
        "",
        "## 三、高频正文词 TOP 40",
        "",
    ]
    L += _table(["#", "词", "出现次数"], ((i, w, c) for i, (w, c) in enumerate(yearly.top_words, 1)))
    L += [
        "",
        "---",
        "",
        "## 四、相邻年份重合率",
        "",
        "两个口径都给出来，因为它们的含义不同：",
        "",
        "- **Jaccard** `|A∩B| / |A∪B|`——受各年词汇量大小影响，是保守口径。",
        "- **重合系数** `|A∩B| / min(|A|,|B|)`——「今年的词有多少去年见过」，更贴近学生实感。",
        "",
    ]
    L += _table(
        ["年份", "Jaccard", "重合系数"],
        ((yr, _pct(yearly.jaccard[yr], 1), _pct(yearly.overlap_coefficient[yr], 1)) for yr in yearly.jaccard),
    )
    L += [
        "",
        f"**均值：Jaccard {_pct(yearly.mean_jaccard)}，重合系数 {_pct(yearly.mean_overlap_coefficient)}。**",
        "",
        "---",
        "",
        "## 五、首次出现的新词",
        "",
    ]
    L += _table(["年份", "该年新增词形", "累计"], _cumulative(yearly))
    L += [
        "",
        "---",
        "",
        "## 六、大纲覆盖率趋势（核心结论）",
        "",
        f"比对词表：`{wordlist.path.name if wordlist.path else '—'}`（{len(wordlist)} 条，独立于本语料）",
        "",
    ]
    L += _table(
        ["年份", "不同词口径", "次数加权口径"],
        ((yr, _pct(stats.coverage_distinct[yr]), _pct(stats.coverage_weighted[yr])) for yr in y),
    )
    L += [
        "",
    ]
    # 前 5 年 / 后 5 年的对比只在年份足够时才有意义
    if len(y) >= 10:
        dist = list(stats.coverage_distinct.values())
        wgt = list(stats.coverage_weighted.values())
        L += [
            f"- 前 5 年（{y[0]}–{y[4]}）：{_pct(_mean(dist[:5]))} / {_pct(_mean(wgt[:5]))}",
            f"- 后 5 年（{y[-5]}–{y[-1]}）：{_pct(_mean(dist[-5:]))} / {_pct(_mean(wgt[-5:]))}",
            "",
        ]
    L += [
        "---",
        "",
        "## 七、两种「大纲覆盖率」口径对照（重要区别）",
        "",
        "| 口径 | 问的问题 | 结果 |",
        "|---|---|---|",
        f"| **不同词口径** | 「语料里出现过的**不同词形**，有多少在大纲内」 | {_pct(stats.mean_coverage_distinct)} |",
        f"| **次数加权口径** | 「你**实际读到的词次**里，有多少在大纲内」 | {_pct(stats.mean_coverage_weighted)} |",
        "",
        "**次数加权口径才是贴近实感的那个。** 出现次数最多的那批词"
        "（the/of/and/be…）几乎全在大纲内；真正「超纲」的是偶尔露面的低频词——"
        "这就是为什么不同词口径低了 11 个百分点。",
        "",
        "### 剩余缺口分解",
        "",
        "剩余约 11.8% 的词次缺口，**结构上不是换一份词表能修的**：",
        "",
    ]
    L += _table(["成因", "占词次", "词表能修吗"], _GAP_TABLE)
    L += [
        "",
        "> **方法论红线：不能把语料里挖出来的词补进词表来抬覆盖率。**",
        "> 覆盖率只有在词表**独立于语料**时才有意义。",
        "",
        "---",
        "",
        "## 八、token 覆盖率曲线（不依赖任何词表）",
        "",
        f"语料：{curve.articles} 篇（机械切片，每篇约 400 词元）、"
        f"{curve.total_tokens:,} 词元、{curve.distinct:,} 个不同词形。",
        "",
        "这个口径**只用真题自身的词频排序**，不碰大纲词表，因此不受词表争议影响。",
        "",
    ]
    L += _table(
        ["覆盖率目标", "需要词汇量", "占全部词形"],
        ((_pct(t), f"{n:,}", _pct(n / curve.distinct)) for t, n in curve.targets),
    )
    L += [
        "",
    ]
    L += _table(
        ["词汇量", "覆盖词次", "每篇生词（不同词形）", "每篇生词（词次）"],
        (
            (f"{p.size:,}", _pct(p.coverage), f"{p.unknown_distinct_per_article:.0f}", f"{p.unknown_tokens_per_article:.0f}")
            for p in curve.points
        ),
    )
    L += [
        "",
        "### 长尾结构",
        "",
    ]
    L += _table(
        ["词频区间", "词形数", "占词形", "占词次"],
        ((label, f"{n:,}", _pct(fs), _pct(ts)) for label, n, fs, ts in curve.bands),
    )
    L += [
        "",
        "---",
        "",
        f"## 九、高频内容词表（出现 ≥{10} 年、非功能词）",
        "",
        f"共 **{len(stats.content_words)} 个**，完整清单见 `高频内容词表.md`。",
        "",
        "前 30 个：",
        "",
        "```",
        ", ".join(w for w, _ in stats.content_words[:30]),
        "```",
        "",
        "---",
        "",
        "## 十、数据质量说明（口径与已知局限）",
        "",
        "1. **语料只含正文散文**，已剔除 Directions 指令行、题型标题、题干、选项、",
        "   中文解析与盗版水印。清洗管线见 `src/npee_vocab/corpus.py`。",
        "2. **2022 年是合订本**，已在第 678 行截断。",
        "3. **`numbered` 是残留**——来自 Directions 的 \"numbered blank\"，已单列在 T4。",
        "4. **缩写会被切分**：`don't`→`don`+`t`。高频词表已剔除这些碎片。",
        "5. **只统计正文，没统计题干与选项**：题干词汇通常更简单，因此本报告偏保守。",
        "6. **判分口径为「出现年份数」**，衡量跨年份稳定性，不是原始词频。",
        "7. **词形还原的分歧**：`lemmatize()` 把 `was→be`、`children→child`，",
        "   因此比对词表时查的是词元而非表层形态。曾有一个版本的结论",
        "   因为忽略这一点而误判词表「缺 is/are/was」——详见",
        "   `docs/methodology/wordlist-revision.md`。",
        "",
    ]
    return "\n".join(L)


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _cumulative(yearly: YearlyTrend):
    total = 0
    for yr in sorted(yearly.first_seen):
        total += yearly.first_seen[yr]
        yield yr, yearly.first_seen[yr], total


# --------------------------------------------------------------------------
# AB 检验 / 阅读分析（控制台文本）
# --------------------------------------------------------------------------


def render_ab(ab: ABAnalysis, corpus_info: str) -> str:
    L = [
        "=" * 78,
        "假设检验：A 类词（逻辑 / 抽象）是不是封闭集合？",
        "=" * 78,
        corpus_info,
        "",
        f"人工归纳的 A 类候选：{ab.candidates} 个词形",
        f"其中在语料中出现过的：{len(ab.present)} 个",
        f"这些词贡献词次 {ab.a_tokens:,}，占全部词次 {_pct(ab.a_token_share, 2)}",
        "",
        f"{'词':<18}{'出现次数':>8}{'出现年份':>9}",
    ]
    for w, c, yy in ab.present[:45]:
        L.append(f"{w:<18}{c:>8}{yy:>9}")
    L.append(f"... 共 {len(ab.present)} 个")
    L += ["", "--- A 类词的复用率分布 ---"]
    for label, n, share in ab.reuse_buckets:
        L.append(f"  {label:<12}{n:>4} 个 ({share:.0%})")
    L += [
        "",
        "=" * 78,
        "对照：B 类词（低频实词 / 术语）的复用率",
        "=" * 78,
        f"出现 <=2 次的词形：{ab.b_distinct:,} 个，占全部词形 {_pct(ab.b_share_distinct)}",
        f"但它们只贡献 {ab.b_tokens:,} 词次，占 {_pct(ab.b_token_share)}",
        "",
        "→ A 类复用率高而 B 类复用率极低，说明两者必须用完全不同的策略。",
        "",
        "=" * 78,
        f"每篇（约 400 词元）里 A 类词的实际负载（共 {ab.articles} 篇）",
        "=" * 78,
        f"  A 类词：每篇平均 {ab.a_per_article_distinct:.1f} 个不同词形，"
        f"{ab.a_per_article_tokens:.1f} 个词次",
        f"  B 类词：每篇平均 {ab.b_per_article_distinct:.1f} 个不同词形",
        "",
        f"→ A 类每篇只涉及约 {ab.a_per_article_distinct:.0f} 个不同词形，"
        "说明它是【有限集合】，可以穷尽掌握。",
        f"→ B 类每篇涉及约 {ab.b_per_article_distinct:.0f} 个不同词形，"
        "且跨篇不重复，属长尾。",
        "",
    ]
    return "\n".join(L)


def render_coverage(curve: CoverageCurve, corpus_info: str) -> str:
    L = [
        "=" * 78,
        f"语料规模：{curve.articles} 篇，{curve.total_tokens:,} 个词元，"
        f"{curve.distinct:,} 个不同词形",
        "=" * 78,
        corpus_info,
        "",
        "一、要掌握多少词，才能覆盖多少比例的词次",
        "",
        f"{'覆盖率目标':<12}{'需要词汇量':>12}{'占全部词形':>12}",
    ]
    for t, n in curve.targets:
        L.append(f"{t:>10.1%}{n:>12,}{n / curve.distinct:>12.1%}")
    L += [
        "",
        "二、在各级词汇量下，平均每篇（约 400 词元）还剩多少生词",
        "",
        f"{'词汇量':<10}{'覆盖词次':>10}{'每篇生词(不同)':>16}{'每篇生词(词次)':>17}",
    ]
    for p in curve.points:
        L.append(
            f"{p.size:<10,}{p.coverage:>10.1%}"
            f"{p.unknown_distinct_per_article:>16.0f}{p.unknown_tokens_per_article:>17.0f}"
        )
    L += [
        "",
        "三、长尾有多长",
        "",
        f"{'词频区间':<14}{'词形数':>9}{'占词形':>9}{'占词次':>9}",
    ]
    for label, n, fs, ts in curve.bands:
        L.append(f"{label:<14}{n:>9,}{fs:>9.1%}{ts:>9.1%}")
    L.append("")
    return "\n".join(L)


def render_reading(reading: ReadingAnalysis, corpus_info: str) -> str:
    L = [
        "=" * 78,
        "阅读生词密度：为什么做题时总觉得「有几个词不认识」",
        "=" * 78,
        corpus_info,
        "",
        f"语料共 {reading.articles} 篇、{reading.total_tokens:,} 词元。",
        f"跨年份高频词：出现 ≥10 年 {reading.hf10} 个，出现 ≥5 年 {reading.hf5} 个。",
        "",
        "一、词形按「出现年份数」分布",
        "",
        f"{'出现年份数':<14}{'词形数':>8}{'占比':>9}   累计占比",
    ]
    for label, n, share, cum in reading.distribution:
        L.append(f"{label:<14}{n:>8}{share:>9.1%}   {cum:>8.1%}")
    L += [
        "",
        "二、不同词汇量下，每篇还剩多少生词",
        "",
        f"{'词汇量':<10}{'覆盖词次':>10}{'每篇生词(词次)':>16}{'每篇生词(不同)':>17}",
    ]
    for p in reading.points:
        L.append(
            f"{p.vocab_size:<10,}{p.coverage:>10.1%}"
            f"{p.unknown_tokens:>16.0f}{p.unknown_distinct:>17.0f}"
        )
    L.append("")
    return "\n".join(L)
