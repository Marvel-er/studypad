"""
语法结构 & 加分句型的规则库。

设计原则：规则先行、LLM 增强。
没有配置任何大模型时，本文件足以产出完整的手账标注；
配置了 LLM 后，LLM 只负责「把讲解写得更像老师」和补充规则漏掉的点。

explain 按 1→4 四档深度，对应 six 档能力画像的 explain_depth。
"""
from __future__ import annotations

import re

# ============================================================ 语法结构

GRAMMAR_RULES: list[dict] = [
    {
        "id": "inversion",
        "name": "部分倒装",
        "color": "#0891B2",
        "regex": r"^\s*(?:Not until|Never|Hardly|Scarcely|Seldom|Rarely|Little|Nowhere|"
                 r"No sooner|Only (?:then|when|after|by|in this way)|Not only|At no time)\b",
        "explain": {
            1: "否定词/Only 置于句首要部分倒装。",
            2: "否定词或 Only 短语置于句首时，主句要部分倒装：把助动词/be 动词提到主语之前。",
            3: "否定副词或 Only + 状语置于句首 → 主句部分倒装（助动词前置），用于强调。"
               "注意：若 Only 修饰的是主语，则不倒装。",
            4: "倒装结构：把助动词（do/did/have/had/will）或 be 动词提到主语前，实义动词保持原形。"
               "还原方法：把助动词放回主语后面，否定词放回原位。"
               "常见触发词：Not until、Never、Hardly...when、No sooner...than、Seldom、"
               "Only when/after/by、At no time、Under no circumstances。"
               "典型例句：Not until the committee had reviewed all the submissions did they realize "
               "the flaw. → 还原为 They did not realize the flaw until the committee had reviewed...",
        },
    },
    {
        "id": "emphatic",
        "name": "强调句",
        "color": "#CA8A04",
        "regex": r"\bIt (?:is|was)\b[^.;]{0,90}?\b(?:that|who|which|whom)\b",
        "explain": {
            1: "It is/was ... that/who ... 强调句型。",
            2: "强调句 It is/was + 被强调成分 + that/who + 其余部分，可强调主语、宾语或状语。",
            3: "去掉 It is/was 和 that/who 后句子仍完整 —— 这是判断强调句的可靠方法。"
               "强调人用 who，其余用 that。",
            4: "判断口诀：删掉「It is/was」和「that/who」，剩下的部分若仍是完整句子，"
               "就是强调句而不是主语从句或定语从句。"
               "被强调成分可以是主语、宾语、时间状语、地点状语或原因状语（强调状语用 that，不用 when/where）。",
        },
    },
    {
        "id": "subjunctive",
        "name": "虚拟语气",
        "color": "#DB2777",
        "regex": r"\b(?:if\s+\w+(?:\s+\w+)?\s+had\s+\w+(?:ed|en)\b|were\s+to\s+\w+|"
                 r"\bwish\s+(?:I|you|he|she|it|we|they|had|were)\b|should\s+have\s+\w+(?:ed|en)\b|"
                 r"had\s+better\b|would\s+rather\b|as\s+if\s+\w+\s+were\b|"
                 r"it\s+is\s+(?:essential|important|necessary|vital)\s+that\b)",
        "explain": {
            1: "虚拟语气：说与事实相反或不太可能的事。",
            2: "虚拟语气表达与事实相反的假设。与现在相反用过去式，与过去相反用过去完成时，"
               "将来不太可能用 were to / should + 动词原形。",
            3: "核心是「时态后退」：与现在事实相反 → 从句用一般过去时、主句用 would/could + 动词原形；"
               "与过去事实相反 → 从句用 had + 过去分词、主句用 would/could have + 过去分词。",
            4: "三种基本形式：① 与现在相反：If + 主语 + 动词过去式（be 用 were）, 主句 would/could/might + 动词原形；"
               "② 与过去相反：If + 主语 + had + 过去分词, 主句 would/could/might have + 过去分词；"
               "③ 与将来相反：If + 主语 + were to do / should do, 主句 would + 动词原形。"
               "另外：wish 后接过去式表示现在的遗憾、接过去完成时表示过去的遗憾；"
               "suggest/demand/insist/require 等动词后的 that 从句用 (should) + 动词原形。",
        },
    },
    {
        "id": "relative_clause",
        "name": "定语从句",
        "color": "#2563EB",
        "regex": r"(?:,\s*)?\b(?:which|who|whom|whose|where|when)\b\s+\w+|"
                 r"\b(?:that|which|who)\b\s+(?:is|are|was|were|has|have|had|can|could|will|would|"
                 r"makes?|made|takes?|took|gives?|gave|provides?|leads?|led|comes?|came)\b",
        "explain": {
            1: "定语从句修饰前面的名词。",
            2: "定语从句跟在名词后修饰它，关系代词 which/that 指物、who/whom 指人、whose 表所属。",
            3: "拆句方法：先找到先行词（被修饰的名词），把从句单独拎出来翻译，再放到先行词前面。"
               "逗号隔开的是非限制性定语从句，只是补充说明，删掉不影响句子完整。",
            4: "三步拆解：① 找先行词 —— 从句紧挨着的那个名词；② 看关系词在从句中的成分 —— "
               "作主语用 which/that/who 不可省，作宾语可省，作定语用 whose；"
               "③ 非限制性定语从句（有逗号）不能用 that，且关系词不可省略。"
               "翻译时把从句前置到先行词之前，或独立成句用「这/它」承接。",
        },
    },
    {
        "id": "adverbial_clause",
        "name": "状语从句",
        "color": "#059669",
        "regex": r"\b(?:although|though|even though|whereas|while|whilst|because|since|as long as|"
                 r"unless|until|till|provided that|given that|so that|in order that|as if|"
                 r"as though|in case|the moment|by the time)\b",
        "explain": {
            1: "状语从句：表示时间、原因、让步、条件等。",
            2: "状语从句用连词引导，说明主句发生的时间、原因、条件、让步或结果。",
            3: "常见类型：让步（although/though/even though/while）、原因（because/since/as）、"
               "条件（if/unless/as long as/provided that）、时间（when/while/until/by the time）、"
               "结果（so that/such that）。",
            4: "判断要点：状语从句是「附属」的，去掉后主句仍然成立。"
               "让步状语从句（although/though）不能与 but 连用，中文可译为「尽管……但是……」。"
               "since 既可表原因也可表时间，看后面的从句是否指过去某个时间点。"
               "so that 引导目的状语从句时通常带情态动词（can/could/may/might/will/would）。",
        },
    },
    {
        "id": "nominal_clause",
        "name": "名词性从句",
        "color": "#7C3AED",
        "regex": r"^\s*(?:What|Whether|That|Whoever|Whatever|Whichever|Why|How|Where)\b\s+\w+\s+\w+|"
                 r"\b(?:that|whether)\s+\w+\s+(?:is|are|was|were|will|would|can|could|should|"
                 r"has|have|had|do|does|did)\b",
        "explain": {
            1: "名词性从句可以作主语、宾语或表语。",
            2: "名词性从句在句子里充当名词的角色：主语、宾语或表语。引导词有 that/whether/what/how 等。",
            3: "三类：主语从句（What matters is...）、宾语从句（I believe that...）、"
               "表语从句（The problem is that...）。that 只起连接作用、不充当成分，"
               "what 则在从句中充当主语或宾语。",
            4: "区分口诀：把从句当成一个「名词」看它在主句里做什么成分。"
               "主语从句常用 It 作形式主语后置（It is clear that...）；"
               "that 在宾语从句中常可省略，在主语从句和表语从句中不可省；"
               "what = the thing that，本身在从句里要当主语或宾语，所以 what 从句少了它不完整。",
        },
    },
    {
        "id": "non_finite",
        "name": "非谓语动词",
        "color": "#EA580C",
        "regex": r"^\s*\w+ing\b|,\s*\w+ing\b|,\s*\w+(?:ed|en)\b|"
                 r"\b(?:to\s+)?\w+ing\s+(?:by|of|in|to)\b|\bto\s+be\s+\w+(?:ed|en)\b",
        "explain": {
            1: "非谓语动词：动词变成分词或不定式，不再作谓语。",
            2: "非谓语动词包括不定式（to do）、动名词（doing）和分词（doing / done），"
               "它们不能单独作谓语。",
            3: "选择规则：主动、进行 → doing；被动、完成 → done；表目的、将来 → to do。"
               "放在句首或句中用逗号隔开的分词短语，多作状语（时间、原因、条件、伴随）。",
            4: "核心判断：一个句子只能有一个谓语动词，凡是多出来的动词就必须变成非谓语。"
               "doing 表示主动进行，done 表示被动完成，to do 表示目的或未发生。"
               "分词短语作状语时，其逻辑主语必须与主句主语一致 —— 不一致就是悬垂修饰，是常见错误。",
        },
    },
    {
        "id": "comparison",
        "name": "比较结构",
        "color": "#4D7C0F",
        "regex": r"\bas\s+\w+\s+as\b|\bmore\s+\w+\s+than\b|\bless\s+\w+\s+than\b|"
                 r"the\s+(?:more|better|worse|less)\b.*\bthe\s+(?:more|better|worse|less)\b|"
                 r"\bnot\s+so\s+much\b|\brather\s+than\b",
        "explain": {
            1: "比较结构：比较两个事物。",
            2: "比较结构表示两者之间的程度差异，如 as...as（一样）、more...than（更）、"
               "less...than（不如）。",
            3: "the more...the more... 表示「越……越……」；"
               "as...as 中间用形容词或副词原级；not so much A as B 表示「与其说 A 不如说 B」。",
            4: "考点集中在三点：① as...as 之间只能放原级，不能在 as 后用比较级；"
               "② the + 比较级, the + 比较级 是「越……越……」的固定句式，前后都要倒装式的词组；"
               "③ not so much A as B 与 rather than 都表示取舍对比，写作中用来替换 but。",
        },
    },
    {
        "id": "parenthesis",
        "name": "插入语",
        "color": "#6B7280",
        "regex": r",\s*(?:however|therefore|moreover|furthermore|nevertheless|for example|for instance|"
                 r"in fact|in other words|that is|to be sure|by contrast|on the contrary|"
                 r"as a result|in short|indeed|of course|after all)\s*,",
        "explain": {
            1: "插入语：补充说明，去掉不影响句子结构。",
            2: "用逗号隔开的插入成分，起补充或转折作用，读的时候可以先跳过它抓住主干。",
            3: "常见插入语：however（然而）、in fact（事实上）、for example（例如）、"
               "in other words（换言之）。它们把句子切开，阅读时要跳跃着找主干。",
            4: "阅读技巧：看到成对的逗号或破折号，先把中间的内容整段划掉，找出主谓宾，"
               "再把插入语放回去理解。这类成分在长难句里极多，是拉开阅读速度的关键。",
        },
    },
]


def detect_grammar(sentence: str) -> list[dict]:
    """返回句子中命中的语法结构（可能多个）。"""
    hits: list[dict] = []
    for rule in GRAMMAR_RULES:
        for m in re.finditer(rule["regex"], sentence, flags=re.I | re.M):
            start, end = m.span()
            if end - start < 3:
                continue
            # 圈定到整句时截取合理范围，避免只标两个词
            hits.append({
                "grammar_id": rule["id"],
                "label": rule["name"],
                "color": rule["color"],
                "start": start,
                "end": end,
                "surface": sentence[start:end],
                "explain_map": rule["explain"],
            })
            break  # 同一结构在同一句只标一次
    return hits


# ============================================================ 加分句型

# level: 该句型从哪个等级开始值得标
PATTERNS: list[dict] = [
    {
        "id": "not_until_inversion", "name": "Not until ... did/be ...",
        "regex": r"Not until\b[^.]{0,120}?\b(?:did|do|does|was|were|is|are|had|has)\b",
        "level": ["basic", "cet", "advanced", "academic"],
        "usage": ["议论文强调", "表示「直到……才」"],
        "imitation": "Not until we understand the underlying data can we draw a sound conclusion.",
    },
    {
        "id": "the_more_the_more", "name": "The more ..., the more ...",
        "regex": r"[Tt]he\s+(?:more|better|worse|less|longer|faster)[^.]{0,90}?,\s*the\s+(?:more|better|worse|less|longer|faster)\b",
        "level": ["basic", "cet", "advanced", "academic"],
        "usage": ["论证递进", "图表作文趋势描述"],
        "imitation": "The more exposure children have to reading, the better their language skills become.",
    },
    {
        "id": "it_is_that", "name": "It is ... that ...（强调句）",
        "regex": r"It (?:is|was)\b[^.;]{0,80}?\bthat\b",
        "level": ["cet", "advanced", "academic"],
        "usage": ["突出论点", "议论文收束"],
        "imitation": "It is not technology itself but the way we use it that shapes the outcome.",
    },
    {
        "id": "not_only_but_also", "name": "Not only ... but also ...",
        "regex": r"Not only\b[^.]{0,110}?\bbut\s+(?:also\s+)?",
        "level": ["basic", "cet", "advanced", "academic"],
        "usage": ["并列递进", "引入双重理由"],
        "imitation": "Not only does the policy reduce emissions, but it also boosts long-term efficiency.",
    },
    {
        "id": "so_that_result", "name": "so ... that ...（结果状语）",
        "regex": r"\bso\s+\w+\s+that\b|\bsuch\s+\w+\s+that\b",
        "level": ["basic", "cet", "advanced"],
        "usage": ["因果论证", "描述程度与后果"],
        "imitation": "The evidence was so compelling that even the sceptics revised their position.",
    },
    {
        "id": "there_is_no_denying", "name": "There is no denying that ...",
        "regex": r"There is no (?:denying|doubt|question|evidence)\b",
        "level": ["cet", "advanced", "academic"],
        "usage": ["议论文开头亮明共识", "让步后转折"],
        "imitation": "There is no denying that remote work has reshaped how firms measure productivity.",
    },
    {
        "id": "what_matters", "name": "What matters most is ...（主语从句）",
        "regex": r"What\s+(?:matters|counts|is|seems)\b[^.]{0,60}?\bis\b|What matters most",
        "level": ["cet", "advanced", "academic"],
        "usage": ["结论句", "观点收束"],
        "imitation": "What matters most is not the speed of change but its direction.",
    },
    {
        "id": "given_that", "name": "Given that ...（鉴于）",
        "regex": r"\b(?:Given|Considering|Provided)\s+that\b|\bGiven\s+the\b",
        "level": ["advanced", "academic"],
        "usage": ["让步前提", "学术写作假设"],
        "imitation": "Given that resources are finite, prioritising is not optional but essential.",
    },
    {
        "id": "rather_than", "name": "rather than（而非）",
        "regex": r"\brather than\b",
        "level": ["cet", "advanced", "academic"],
        "usage": ["对比取舍", "替换 but 的高级写法"],
        "imitation": "Policymakers should invest in prevention rather than remediation.",
    },
    {
        "id": "with_participle", "name": "with + 名词 + 分词（独立主格）",
        "regex": r"\bwith\s+\w+\s+\w+ing\b|\bwith\s+\w+\s+\w+(?:ed|en)\b",
        "level": ["cet", "advanced", "academic"],
        "usage": ["伴随状语", "图表描述背景"],
        "imitation": "With urban populations expanding, demand for clean water has surged.",
    },
    {
        "id": "hardly_when", "name": "Hardly had ... when ...",
        "regex": r"Hardly had\b[^.]{0,90}?\bwhen\b|No sooner had\b[^.]{0,90}?\bthan\b",
        "level": ["advanced", "academic"],
        "usage": ["时间紧迫感", "叙事性开头"],
        "imitation": "Hardly had the results been published when criticism began to mount.",
    },
    {
        "id": "far_from", "name": "Far from ...（远非）",
        "regex": r"\bFar from\b(?:\s+\w+ing)?",
        "level": ["advanced", "academic"],
        "usage": ["反驳预设", "转折强调"],
        "imitation": "Far from resolving the dispute, the ruling deepened the divide.",
    },
]


def detect_patterns(sentence: str, level_patterns: list[str]) -> list[dict]:
    """返回句中命中的加分句型，按 level_profile.pattern_level 过滤。"""
    hits: list[dict] = []
    for p in PATTERNS:
        if not (set(p["level"]) & set(level_patterns)):
            continue
        m = re.search(p["regex"], sentence)
        if not m:
            continue
        start, end = m.span()
        hits.append({
            "pattern_id": p["id"],
            "name": p["name"],
            "start": start,
            "end": end,
            "surface": sentence[start:end],
            "usage": p["usage"],
            "imitation": p["imitation"],
        })
    return hits


def explain_at(hit: dict, depth: int) -> str:
    """按深度取讲解文本。"""
    em = hit.get("explain_map") or {}
    if not em:
        return ""
    d = max(1, min(4, int(depth)))
    return em.get(d) or em.get(max(em.keys())) or ""
