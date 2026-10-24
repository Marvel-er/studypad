"""
六档考点知识库（Exam-Point Knowledge Base）。

用途：让 agent 按用户选择的阶段，输出**准确、有据可查**的考点内容，
而不是凭模型记忆「编」一套看起来合理的考试结构。

三条硬约束（改动前必读）：
1. **每条数据都带 `src`**，指回 `SOURCES` 里的可核查条目。查不到出处的宁可不写 ——
   这份库的价值全在「可溯源」，掺一条假数据就废一半。
2. **事实性数据（题量/分值/时长/词汇量）与官方口径对齐**；
   媒体或教研机构的二手归纳降级标 `semi_official`，第三方整理标 `secondary`，
   在前端与 API 里都要把 tier 露出来，让用户自己判断可信度。
3. **它只在提示层起作用，不当判据**。词表归属、语法命中等仍走规则引擎；
   本库只用于（a）给 LLM 注入「该考什么」的上下文，（b）前端展示考点，
   （c）给密度编排提供「本级高频语法」的加权依据。见 `prompt_context()`。

数据口径变更记录：
- 2026-10-14 建立。TOEFL 采用 ETS 2026-01-21 起生效的自适应新制（1–6 分制），
  同时保留 2023–2026.1 的旧制，用 `effective_from` / `effective_until` 区分 ——
  网上一半资料还是旧制，不区分会直接答错。
"""
from __future__ import annotations

# =====================================================================
# 一、来源登记表
# =====================================================================
# tier 取值：
#   official       —— 考试主办方 / 教育主管部门的原文或官方页面
#   semi_official  —— 官方媒体、权威教研机构对官方口径的转述（新东方等）
#   secondary      —— 第三方整理（维基、商业站点），仅作旁证
#   oss            —— 开源仓库，仅作结构与事实的交叉校验，不作内容来源

SOURCES: dict[str, dict] = {
    # ---------------- 高中 ----------------
    "moe_curriculum_2017": {
        "tier": "official",
        "title": "《普通高中英语课程标准（2017 年版 2020 年修订）》",
        "publisher": "中华人民共和国教育部",
        "url": "http://www.moe.gov.cn/",
        "establishes": "高中英语必修 + 选择性必修词汇约 3000 词，加选修累计约 3500 词；"
                       "明确语法、语篇、语用三大块的语言知识要求",
        "accessed": "2026-10-14",
    },
    "gaokao_structure": {
        "tier": "official",
        "title": "普通高等学校招生全国统一考试英语科试卷结构（新高考卷）",
        "publisher": "教育部教育考试院命题 · 各省教育考试院公开试卷解析",
        "url": "https://www.neea.edu.cn/",
        "establishes": "150 分卷结构与题型：听力 20 题 30 分、阅读 20 题 50 分、"
                       "语言运用 25 题 30 分、写作 40 分（应用文 15 + 读后续写 25）",
        "note": "北京、上海、天津、浙江等省市自主命题，结构与全国新高考卷不同；"
                "上海卷另有 10 分听说测试",
        "accessed": "2026-10-14",
    },
    "gaokao_grammar_fill": {
        "tier": "semi_official",
        "title": "高考英语语法填空命题规律（10 空考点分布）",
        "publisher": "教研机构真题统计（新东方等）",
        "url": "https://www.xdf.cn/",
        "establishes": "语法填空六大考点：冠词、介词、连词、时态、非谓语、词性转换；"
                       "有提示词约 6–7 空、无提示词约 3–4 空",
        "accessed": "2026-10-14",
    },
    # ---------------- 四六级 ----------------
    "cet_syllabus_2016": {
        "tier": "official",
        "title": "《全国大学英语四、六级考试大纲（2016 年修订版）》",
        "publisher": "全国大学英语四、六级考试委员会 · 中国教育考试网",
        "url": "https://cet.neea.edu.cn/",
        "establishes": "CET-4/6 现行题型、题量、分值比例与考试时长；"
                       "听力语速约 120–140 词/分钟，录音只播放一遍",
        "accessed": "2026-10-14",
    },
    "cet_course_req": {
        "tier": "semi_official",
        "title": "《大学英语课程教学要求》词汇量口径",
        "publisher": "教育部高等教育司（教研机构转述）",
        "url": "https://cet.neea.edu.cn/",
        "establishes": "一般要求 4538 词（对应四级）；较高要求在此基础上 +1081 词（对应六级）；"
                       "更高要求另 +1055 词",
        "note": "通行简写为四级 4500 词 / 700 词组、六级 5500 词 / 1200 词组",
        "accessed": "2026-10-14",
    },
    "cet_freq_corpus": {
        "tier": "semi_official",
        "title": "近 10 年四六级真题词频统计",
        "publisher": "新东方四六级教研",
        "url": "https://cet4-6.xdf.cn/",
        "establishes": "真题高频词再现率约 67%；核心高频词约 300 个覆盖考题词汇 50% 以上；"
                       "四级超纲词占比约 5%，六级约 8–10%",
        "accessed": "2026-10-14",
    },
    # ---------------- 考研 ----------------
    "kaoyan_syllabus": {
        "tier": "official",
        "title": "《全国硕士研究生招生考试英语（一）/（二）考试大纲》",
        "publisher": "教育部教育考试院 · 中国研究生招生信息网",
        "url": "https://yz.chsi.com.cn/",
        "establishes": "英语一 52 题 / 英语二 48 题，满分均 100 分、时长 180 分钟；"
                       "完形 20×0.5、阅读 Part A 20×2、Part B 5×2、"
                       "翻译英一 5 句 10 分 / 英二段落 15 分、写作英一 10+20 / 英二 10+15",
        "accessed": "2026-10-14",
    },
    "kaoyan_types": {
        "tier": "semi_official",
        "title": "考研英语一/二 题型差异与阅读题型分布",
        "publisher": "新东方考研教研",
        "url": "https://kaoyan.xdf.cn/",
        "establishes": "英一新题型三种备选（七选五/排序/标题匹配）、英二两种（多项对应/标题对应）；"
                       "阅读五大题型占比：细节约 40%、推理约 20%、态度约 15%、"
                       "主旨约 15%、词义约 10%",
        "accessed": "2026-10-14",
    },
    # ---------------- 雅思 ----------------
    "ielts_org_official": {
        "tier": "official",
        "title": "IELTS Academic 考试结构与评分标准",
        "publisher": "IELTS 官方（ielts.org / British Council / IDP）",
        "url": "https://www.ielts.org/for-organisations/how-to-use-ielts-results",
        "establishes": "听力 30 分钟 4 部分 40 题、阅读 60 分钟 3 篇 40 题、"
                       "写作 60 分钟 Task 1 ≥150 词 / Task 2 ≥250 词、口语 11–14 分钟三部分；"
                       "总分 1–9 分制，四舍五入到最近半分；Task 2 权重高于 Task 1",
        "accessed": "2026-10-14",
    },
    "ielts_band_descriptors": {
        "tier": "official",
        "title": "IELTS 写作与口语评分四项标准（band descriptors）",
        "publisher": "IELTS 官方 · British Council 雅思官网",
        "url": "https://takeielts.britishcouncil.org/results/how-is-ielts-assessed",
        "establishes": "写作四项：任务完成（Task 1）/任务回答（Task 2）、连贯与衔接、"
                       "词汇丰富度、语法多样性与准确性；口语四项：流利度与连贯性、"
                       "词汇丰富度、语法多样性与准确性、发音，各占 25%",
        "accessed": "2026-10-14",
    },
    "ielts_no_wordlist": {
        "tier": "semi_official",
        "title": "雅思不存在官方词表",
        "publisher": "IELTS 官方考纲 + 主流留学机构共识",
        "url": "https://www.chinaielts.org/",
        "establishes": "雅思不发布官方词汇表，通行备考词量 6000–8000 词"
                       "（6.5 分约 6000–7000，7 分以上约 8000）",
        "accessed": "2026-10-14",
    },
    # ---------------- 托福 ----------------
    "ets_toefl_2026": {
        "tier": "official",
        "title": "TOEFL iBT Test Content and Structure（2026-01-21 起自适应新制）",
        "publisher": "ETS 美国教育考试服务中心",
        "url": "https://www.ets.org/toefl/test-takers/ibt/about/content.html",
        "establishes": "阅读 50 题 30 分钟、听力 47 题 29 分钟、写作 12 题 23 分钟、"
                       "口语 11 题 8 分钟，总计约 2 小时；1–6 分制（每 0.5 一档），"
                       "总分取四项平均；过渡期两年内同时给出 0–120 对照分",
        "accessed": "2026-10-14",
    },
    "ets_toefl_legacy": {
        "tier": "official",
        "title": "TOEFL iBT 旧制（2023 缩短版，至 2026-01-20）",
        "publisher": "ETS 美国教育考试服务中心",
        "url": "https://www.ets.org/toefl/test-takers/ibt/about/content.html",
        "establishes": "阅读 2 篇 ×10 题 35 分钟、听力 3 讲座 + 2 对话 36 分钟、"
                       "口语 4 任务 16 分钟、写作 2 任务 29 分钟；0–120 分制",
        "effective_until": "2026-01-20",
        "accessed": "2026-10-14",
    },
    "ets_toefl_no_wordlist": {
        "tier": "semi_official",
        "title": "托福无官方词表，核心词量口径",
        "publisher": "ETS 考纲 + 主流培训机构统计",
        "url": "https://www.ets.org/",
        "establishes": "托福不发布官方词表；通行备考词量 8000–10000 词"
                       "（含约 1000+ 学科专业词），核心不是「背」而是「用」",
        "accessed": "2026-10-14",
    },
    # ---------------- 开源侧独立核实（tier=oss，第三方面，不是主办方）
    "oss_kaoyan_wordlist": {
        "tier": "oss",
        "title": "考研英语（一）大纲词汇表（独立核实版）+ 25 套真题词汇统计",
        "publisher": "GitHub: yikun-justcai/npee-vocab-statistics（MIT）",
        "url": "https://github.com/yikun-justcai/npee-vocab-statistics",
        "establishes": "大纲词表独立核实为 5,501 条（含 a/an 合并与 5 个英美拼写变体补丁，"
                       "附 SHA256）。基于 2002–2026 共 25 套英语（一）真题正文语料："
                       "大纲按词形覆盖 76.8%、按词次覆盖 88.2%；"
                       "4000 词汇量每篇约剩 19 个生词；98% 阅读流畅门槛约需 5,926 词元；"
                       "出现 ≥50 次的 146 个词形覆盖 51.6% 的词次；"
                       "A 类逻辑/抽象词跨 25 年共 140 个、每篇约 6 个，可穷尽掌握",
        "note": "MIT。真题原文因版权未入库；统计口径与全部修订记录在仓库内公开，"
                "是考研词汇量口径目前可复现性最强的独立核实。"
                "它纠正了一个常见误判：按不同词形算覆盖率会低估实感，应按词次算。",
        "accessed": "2026-10-14",
    },
    "oss_cet_wordbook": {
        "tier": "oss",
        "title": "四六级单词本（OpenEtymology 开源词书）",
        "publisher": "GitHub: openetymology/OpenEtymology",
        "url": "https://github.com/openetymology/OpenEtymology",
        "establishes": "CET4 词书 4,533 词、CET6 词书 2,219 词（六级册按「四级之外新增」组织）。"
                       "CET4 的 4,533 与《大学英语课程教学要求》的 4,538 只差 5，互相印证",
        "note": "⚠ 词书文件是 CC BY-SA 4.0（含 share-alike）。本项目只引用「词量」这一事实，"
                "未复制任何词条 —— share-alike 数据一旦并入会传染整个数据层。"
                "（本项目下载脚本的自动许可检查把它归为 NOASSERTION、漏判了传染性，此处更正。）",
        "accessed": "2026-10-14",
    },
    "oss_cet6_freq": {
        "tier": "oss",
        "title": "CET-6 真题词频统计",
        "publisher": "GitHub: wangjiuyi543-ui/cet6-vocabulary（MIT）",
        "url": "https://github.com/wangjiuyi543-ui/cet6-vocabulary",
        "establishes": "13 份六级真题、84,596 个 token、过滤后 5,279 个词元；"
                       "另产出 Top300 核心词与 Top100 急救词，"
                       "与「六级核心高频词约 300」的口径一致",
        "note": "MIT。作者自述局限：听力原文缺失、非官方词表、属统计推断。",
        "accessed": "2026-10-14",
    },
    "oss_ielts_spelling": {
        "tier": "oss",
        "title": "雅思听力拼写词库",
        "publisher": "GitHub: prantomollick/IELTS-Listening-Spelling-Bank",
        "url": "https://github.com/prantomollick/IELTS-Listening-Spelling-Bank",
        "establishes": "雅思听力拼写风险词去重后 2,032 条，按星期、月份、数字、颜色、"
                       "学科等语义场组织，并保留 UK/US 拼写差异与 week-weak 这类易混对",
        "note": "无许可证。只引用「规模 + 组织方式」这一事实，未复制词条内容。"
                "它量化了「雅思听力丢分主要在拼写而非听不懂」这个判断。",
        "accessed": "2026-10-14",
    },
    "oss_ielts_notes": {
        "tier": "oss",
        "title": "雅思分题型笔记（阅读 / 口语 / 分话题词汇）",
        "publisher": "GitHub: purpyviolet/IELTS-Learning-Notes",
        "url": "https://github.com/purpyviolet/IELTS-Learning-Notes",
        "establishes": "阅读 Matching 题的关键操作顺序：先看题干有无 NB 提示"
                       "（出现 NB 后可重复选同一选项，这是最容易漏的审题点），"
                       "再回原文定位、精读关键句、逐项比对选项",
        "note": "无许可证。只引用解题步骤这一事实性方法，未复制笔记内容。",
        "accessed": "2026-10-14",
    },
}

# 开源仓库：只用于结构与事实的交叉校验，不作内容来源。
# 逐字搬运 `lic=NONE` 仓库的文字会侵权 —— 这条边界必须守住。
# ⚠ 2026-10-14 更正：本项目下载脚本的自动许可检查只看仓库元数据里的 license 字段，
#   openetymology/OpenEtymology 的元数据是 NOASSERTION，但它的 DATA_LICENSE.md 明确写
#   **CC BY-SA 4.0（share-alike）**。脚本因此漏报「无传染性许可」。
#   教训：**许可证要读仓库里的 LICENSE / DATA_LICENSE 文件，不能只信元数据字段**。
OSS_SOURCES: dict[str, dict] = {
    "yulaoshizuikeai/English-Note": {
        "license": "NONE",
        "usage": "cross_check_only",
        "covers": "高中语法体系（11 专题 + 50 条句法公式 + 排雷清单）",
        "note": "无许可证，仅比对知识点是否遗漏，不引用原文",
    },
    "aa339519589-cpu/3600-english": {
        "license": "NONE（词表上游 shui-dun/minitools 为 MIT）",
        "usage": "cross_check_only",
        "covers": "高中 3600 词表（基础/中阶/拔高各 1200）",
        "note": "与本项目 data/wordlists/high_school.json 规模互校",
    },
    "ZhaoyuanLiu23/CET-Prompt-Hub": {
        "license": "MIT",
        "usage": "reference",
        "covers": "四六级写作/翻译策略、话题范文库、六级翻译高频词汇表",
        "note": "MIT 可参考；词数区间（四级 140–180、六级 160–200）与之互校",
    },
    "yikun-justcai/npee-vocab-statistics": {
        "license": "MIT",
        "usage": "cross_check_only",
        "covers": "考研英语（一）大纲词表独立核实 + 25 套真题覆盖率/词频统计",
        "note": "MIT 可引用事实；真题原文未入库。考研词汇口径的最强独立核实。",
    },
    "openetymology/OpenEtymology": {
        "license": "CC BY-SA 4.0（share-alike，元数据字段为 NOASSERTION）",
        "usage": "cross_check_only",
        "covers": "四六级单词本（CET4 4,533 词 / CET6 2,219 词）",
        "note": "⚠ share-alike：只引用词量这一事实，绝不并入其词条数据",
    },
    "wangjiuyi543-ui/cet6-vocabulary": {
        "license": "MIT",
        "usage": "cross_check_only",
        "covers": "六级真题词频 Top300 / 急救 Top100 / 分话题词表",
        "note": "与「六级核心高频词约 300」的教研口径互校",
    },
    "prantomollick/IELTS-Listening-Spelling-Bank": {
        "license": "NONE",
        "usage": "cross_check_only",
        "covers": "雅思听力拼写风险词 2,032 条（按语义场组织）",
        "note": "无许可证，只引用规模与组织方式，不复制词条",
    },
    "purpyviolet/IELTS-Learning-Notes": {
        "license": "NONE",
        "usage": "cross_check_only",
        "covers": "雅思阅读分题型 / 口语 Part 1–3 / 分话题词汇笔记",
        "note": "无许可证，只引用解题步骤等事实性方法，不复制笔记",
    },
    "zhuying66/Gaokao688": {
        "license": "MIT",
        "usage": "cross_check_only",
        "covers": "高考 688 高频词表（词性 + 中文释义）",
        "note": "民间高频词分组，非官方口径，仅作旁证，未并入词表",
    },
    "lhzzzzzzzj/english-wordlists-for-ocr": {
        "license": "MIT",
        "usage": "discarded",
        "covers": "（无有效产出）",
        "note": "仓库内只有「生成中」的状态通知与少量抽样 CSV，未产出完整词表，不作为依据",
    },
}

# =====================================================================
# 二、考点数据
# =====================================================================

EXAM_POINTS: dict[str, dict] = {}

# ---------------------------------------------------------------------
# 2.1 高中（新高考）
# ---------------------------------------------------------------------
EXAM_POINTS["high_school"] = {
    "id": "high_school",
    "label": "高中（新高考）",
    "en": "Senior High / Gaokao",
    "profile": {
        "score_scale": "150 分",
        "duration": "120 分钟（含听力约 20 分钟）",
        "paper_count": "全国新高考 I / II 卷；北京、上海、天津、浙江自主命题",
        "src": ["gaokao_structure"],
    },
    "vocabulary": {
        "target": 3500,
        "basis": "课标必修 + 选择性必修约 3000 词，加选修累计约 3500 词",
        "tiers": [
            {"name": "核心 3500 词", "detail": "高考阅读选材、完形语境、写作表达的共用底座"},
            {"name": "高频超纲词约 500–1000", "detail": "试卷中允许出现且不注汉语，"
                                                     "需靠构词法与语境推断"},
        ],
        "focus": [
            "一词多义与熟词生义（如 last、company、figure 在高考中的非首义项）",
            "词性转换（语法填空高频：名词↔动词↔形容词↔副词）",
            "固定搭配与动词短语（look forward to、make sense of 等）",
            "构词法：前缀 un-/dis-/re-/pre-，后缀 -tion/-ment/-able/-ly",
        ],
        "src": ["moe_curriculum_2017", "gaokao_grammar_fill"],
    },
    "grammar": {
        "note": "高考语法不单独命题，全部通过语法填空、完形填空、阅读长难句与写作间接考查",
        "items": [
            {"name": "词法基础", "detail": "冠词（a/an/the）、介词（固定搭配）、"
                                          "代词（it 作形式主宾语、反身代词）、连词（并列/从属）",
             "src": ["gaokao_grammar_fill"]},
            {"name": "动词时态", "detail": "8 大核心时态 + 过去完成时、现在完成进行时、"
                                          "将来进行时；判定用「时间标志词 → 上下文基准时态 → 动作先后」三步法",
             "src": ["moe_curriculum_2017"]},
            {"name": "语态", "detail": "含进行被动（is being done）、完成被动（has been done）；"
                                       "漏写 being/been 是最常见失分点",
             "src": ["gaokao_grammar_fill"]},
            {"name": "非谓语动词", "detail": "不定式 / 动名词 / 现在分词 / 过去分词；"
                                            "判定顺序：已有谓语且无连词 → 填非谓语；再判逻辑主语 → 主被动 → 时间先后",
             "src": ["moe_curriculum_2017"]},
            {"name": "定语从句", "detail": "关系代词 vs 关系副词（缺主/宾/定用代词，缺状语用副词）；"
                                          "介词 + which/whom；非限制性从句不用 that；as 与 which 之别",
             "src": ["moe_curriculum_2017"]},
            {"name": "名词性从句", "detail": "主语/宾语/表语/同位语从句；that 与 what 的判定"
                                            "（缺成分表事物用 what，成分完整用 that）；从句一律陈述语序",
             "src": ["moe_curriculum_2017"]},
            {"name": "状语从句", "detail": "时间/条件/让步/原因/结果/目的/方式；"
                                          "主语一致且含 be 时可省略主语与 be；no matter wh- vs wh-ever",
             "src": ["moe_curriculum_2017"]},
            {"name": "情态动词与虚拟语气", "detail": "推测体系 must/may/can't (+have done)；"
                                                   "should have done 的「本应而未」义；条件句时态倒退；"
                                                   "一坚持二命令三建议四要求后的 (should) do",
             "src": ["moe_curriculum_2017"]},
            {"name": "特殊句式", "detail": "倒装（否定副词句首、only + 状语）、强调句 "
                                          "（去掉 It is/was 与 that 后仍成句）、省略、it 形式主宾语",
             "src": ["moe_curriculum_2017"]},
            {"name": "主谓一致", "detail": "语法一致、意义一致、就近原则（either...or / there be）、"
                                          "就远原则（as well as / together with / rather than）",
             "src": ["moe_curriculum_2017"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "以新高考全国卷为准，总分 150",
        "items": [
            {"section": "听力", "name": "第一节 短对话 / 第二节 长对话与独白",
             "items": "20 题", "score": "30 分", "per_item": "1.5 分",
             "detail": "第一节 5 段短对话 5 题；第二节 5 段长对话或独白 15 题",
             "src": ["gaokao_structure"]},
            {"section": "阅读理解", "name": "第一节 四选一 / 第二节 七选五",
             "items": "20 题", "score": "50 分", "per_item": "2.5 分",
             "detail": "第一节 4 篇文章 15 题；第二节 七选五补全语篇 5 题",
             "src": ["gaokao_structure"]},
            {"section": "语言运用", "name": "完形填空 + 语法填空",
             "items": "25 题", "score": "30 分",
             "detail": "完形填空 15 题 ×1 分（四选一）；语法填空 10 题 ×1.5 分",
             "src": ["gaokao_structure"]},
            {"section": "写作", "name": "应用文 + 读后续写",
             "items": "2 题", "score": "40 分",
             "detail": "应用文写作（书信/通知/演讲稿）15 分，约 80 词；"
                       "读后续写 25 分，约 150 词（已取消短文改错）",
             "src": ["gaokao_structure"]},
        ],
    },
    "high_frequency": [
        {"topic": "语法填空六大考点",
         "points": ["冠词 a/an/the 与零冠词", "介词固定搭配", "连词（并列与从属）",
                    "谓语动词时态与语态", "非谓语动词", "词性转换（派生词）"],
         "src": ["gaokao_grammar_fill"]},
        {"topic": "完形填空高频逻辑",
         "points": ["上下文复现（原词、同义、反义）", "逻辑关系词（however、therefore、"
                    "moreover、instead）", "情感态度一致性", "动词与搭配的语境适配"],
         "src": ["gaokao_structure"]},
        {"topic": "阅读六大题型",
         "points": ["细节理解", "推理判断", "主旨大意", "词义猜测",
                    "观点态度", "语篇结构（七选五的衔接与指代）"],
         "src": ["gaokao_structure"]},
        {"topic": "读后续写加分点",
         "points": ["情感链（fear → relief → gratitude）", "动作链（连续动词精确化）",
                    "感官描写与心理描写", "与原文情节线逻辑衔接", "高级句式"
                    "（分词状语、独立主格、名词性从句）"],
         "src": ["gaokao_structure", "gaokao_grammar_fill"]},
    ],
    "focus": [
        {"title": "语法填空的「先判成分、再定形式」",
         "detail": "有提示词先数谓语与连词：缺谓语填时态语态，不缺则填非谓语；"
                   "无提示词按「介词/冠词/连词/代词」四选一。",
         "src": ["gaokao_grammar_fill"]},
        {"title": "写作的「词数红线」",
         "detail": "应用文约 80 词、读后续写约 150 词；偏离词数区间会被扣分。",
         "src": ["gaokao_structure"]},
        {"title": "书面表达的句式升级而非词汇堆砌",
         "detail": "评分看句式多样性（简单句 + 并列句 + 复合句混用）与衔接自然，"
                   "而非生僻词密度。",
         "src": ["gaokao_grammar_fill"]},
    ],
    "sources": ["moe_curriculum_2017", "gaokao_structure", "gaokao_grammar_fill"],
}

# ---------------------------------------------------------------------
# 2.2 大学英语四级
# ---------------------------------------------------------------------
EXAM_POINTS["cet4"] = {
    "id": "cet4",
    "label": "大学英语四级（CET-4）",
    "en": "CET-4",
    "profile": {
        "score_scale": "710 分（常模计分，425 分被普遍视为合格线）",
        "duration": "125 分钟",
        "paper_count": "57 题",
        "src": ["cet_syllabus_2016"],
    },
    "vocabulary": {
        "target": 4500,
        "basis": "《大学英语课程教学要求》「一般要求」4538 词（含中学已学词汇）；"
                 "通行口径 4500 词 + 700 词组",
        "tiers": [
            {"name": "核心高频词约 300", "detail": "近 10 年真题出现 10 次以上，"
                                                 "覆盖四大题型，占考题词汇量 50% 以上"},
            {"name": "中频词约 500", "detail": "出现 3–10 次，集中在阅读与听力"},
            {"name": "低频/超纲词", "detail": "四级超纲词占比约 5%，多为专有名词，通常不影响解题"},
            {"name": "独立词书核对", "detail": "开源四六级词书的四级册收录 4,533 词，"
                                              "与大纲口径 4,538 只差 5，互相印证"},
        ],
        "focus": [
            "基础义项 + 常见搭配优先（contribute to、account for）",
            "名词→动词→形容词的派生（decide/decision/decisive）",
            "听力场景词：校园、租房、求职、旅行、科技",
            "翻译主题词：中国文化、传统节日、经济社会发展",
        ],
        "src": ["cet_course_req", "cet_freq_corpus", "oss_cet_wordbook"],
    },
    "grammar": {
        "note": "四级不设独立语法题；语法能力通过写作、翻译、阅读长难句间接考查",
        "items": [
            {"name": "时态与语态一致性", "detail": "段落内基准时态统一；"
                                                  "被动语态在翻译中高频（中文无主句 → 英文被动）",
             "src": ["cet_syllabus_2016"]},
            {"name": "主谓一致", "detail": "尤其就远原则（as well as、together with、rather than）"
                                          "与分数/百分数作主语",
             "src": ["cet_syllabus_2016"]},
            {"name": "非谓语动词", "detail": "分词作定语与状语、不定式作目的状语；"
                                            "避免悬垂分词（逻辑主语与主句主语不一致）",
             "src": ["cet_syllabus_2016"]},
            {"name": "三大从句", "detail": "定语从句（介词 + which）、名词性从句、"
                                          "状语从句，用于写作中的句式扩展",
             "src": ["cet_syllabus_2016"]},
            {"name": "选词填空的词性判断", "detail": "先判空格词性（冠词后接名词、"
                                                    "系动词后接形容词、副词修饰动词），再在同类候选中选搭配",
             "src": ["cet_syllabus_2016"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "总分 710，听力与阅读各占 35%、写作与翻译各占 15%",
        "items": [
            {"section": "写作", "name": "短文写作", "items": "1 题", "score": "15%（106.5 分）",
             "time": "30 分钟", "detail": "议论文为主，常见 120–180 词（备考通行区间 140–180 词）",
             "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "短篇新闻 3 篇", "items": "7 题", "score": "7%",
             "detail": "新闻听力，语速约 120–140 词/分钟，录音只播放一遍",
             "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "长对话 2 篇", "items": "8 题", "score": "8%",
             "detail": "两人对话，考查场景理解与言外之意", "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "听力篇章 3 篇", "items": "10 题", "score": "20%",
             "detail": "短文理解，考查主旨与细节", "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "选词填空（词汇理解）", "items": "10 题", "score": "5%",
             "detail": "一篇约 200 词文章，15 选 10，考查词性判断 + 搭配",
             "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "长篇阅读（信息匹配）", "items": "10 题", "score": "10%",
             "detail": "一篇约 1000 词长文，10 个句子匹配到段落，考查定位与同义替换",
             "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "仔细阅读 2 篇", "items": "10 题", "score": "20%",
             "detail": "每篇 5 题四选一，考查细节、推断、主旨、词义",
             "src": ["cet_syllabus_2016"]},
            {"section": "翻译", "name": "汉译英（段落）", "items": "1 题", "score": "15%（106.5 分）",
             "time": "30 分钟", "detail": "140–160 个汉字，主题多为中国文化、历史、社会、经济",
             "src": ["cet_syllabus_2016"]},
        ],
    },
    "high_frequency": [
        {"topic": "听力",
         "points": ["新闻听力信号词（however、according to、reportedly）",
                    "数字、时间、地点等干扰项辨析", "长对话的场景词与态度词",
                    "同义替换（录音用 A 词，选项用 B 词）"],
         "src": ["cet_syllabus_2016"]},
        {"topic": "阅读",
         "points": ["关键词定位 + 同义替换", "排除「原文未提」与「过度推断」",
                    "长篇阅读的段落主旨快速抓取", "选词填空先判词性再定搭配"],
         "src": ["cet_syllabus_2016", "cet_freq_corpus"]},
        {"topic": "翻译",
         "points": ["无主句补主语（用被动或 there be）", "动词连用拆分（分句或非谓语）",
                    "中国传统文化专有名词（春节 Spring Festival、二十四节气）",
                    "避免逐字硬译"],
         "src": ["cet_syllabus_2016"]},
        {"topic": "写作",
         "points": ["三段式（引出观点 → 论证 2–3 点 → 总结）",
                    "论点 + 例证 + 回扣的段落结构",
                    "衔接词（first and foremost、more importantly、to conclude）",
                    "避免中式英语与拼写错误"],
         "src": ["cet_syllabus_2016"]},
    ],
    "focus": [
        {"title": "分值与时间的不对称",
         "detail": "阅读 35% 只给 40 分钟、翻译 15% 给 30 分钟 —— 长文匹配不可恋战，"
                   "翻译与写作要留足时间。",
         "src": ["cet_syllabus_2016"]},
        {"title": "听力录音只放一遍",
         "detail": "每问题后约 15 秒答题，必须边听边涂卡，不能等回放。",
         "src": ["cet_syllabus_2016"]},
    ],
    "sources": ["cet_syllabus_2016", "cet_course_req", "cet_freq_corpus", "oss_cet_wordbook"],
}

# ---------------------------------------------------------------------
# 2.3 大学英语六级
# ---------------------------------------------------------------------
EXAM_POINTS["cet6"] = {
    "id": "cet6",
    "label": "大学英语六级（CET-6）",
    "en": "CET-6",
    "profile": {
        "score_scale": "710 分",
        "duration": "130 分钟",
        "paper_count": "57 题",
        "src": ["cet_syllabus_2016"],
    },
    "vocabulary": {
        "target": 5500,
        "basis": "在四级「一般要求」4538 词基础上增加 1081 词（「较高要求」）；"
                 "通行口径 5500 词 + 1200 词组",
        "tiers": [
            {"name": "六级新增词约 1500", "detail": "四级词汇之外的核心增量，"
                                                  "是六级的真实门槛"},
            {"name": "深层义项词", "detail": "同一词在六级中考「生僻义项 + 学术搭配」，"
                                           "如 develop 的「研制、培养」义"},
            {"name": "超纲词", "detail": "占比约 8–10%，多为学术或职场词，可从上下文推测"},
            {"name": "真题词元实测", "detail": "13 份六级真题过滤后实际出现 5,279 个词元，"
                                              "与大纲 5,500 量级吻合；其中 Top300 即为核心高频词"},
        ],
        "focus": [
            "熟词生义与一词多义（六级的核心区分度所在）",
            "学术与职场语域词汇（hypothesis、sustainable、implementation）",
            "高级搭配与带修饰成分的表达（make a substantial contribution to）",
            "翻译主题：科技、环境、教育、经济、社会变迁",
        ],
        "src": ["cet_course_req", "cet_freq_corpus", "oss_cet_wordbook", "oss_cet6_freq"],
    },
    "grammar": {
        "note": "同四级不设独立语法题；六级更侧重长难句拆解与学术句式表达",
        "items": [
            {"name": "长难句结构分析", "detail": "多重从句嵌套、插入语、后置定语的断句与主干还原",
             "src": ["cet_syllabus_2016"]},
            {"name": "非谓语的高级用法", "detail": "独立主格、分词完成式（having done）"
                                                  "在学术写作中的使用",
             "src": ["cet_syllabus_2016"]},
            {"name": "虚拟语气与倒装", "detail": "作为写作加分句式（Were it not for...、"
                                               "Not only... but also 倒装）",
             "src": ["cet_syllabus_2016"]},
            {"name": "语篇衔接手段", "detail": "指代、省略、连接词与词汇衔接，"
                                              "影响阅读速度与写作连贯度",
             "src": ["cet_syllabus_2016"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "结构与四级同构但难度上移：听力增「讲座/讲话」、翻译字数增加",
        "items": [
            {"section": "写作", "name": "短文写作", "items": "1 题", "score": "15%（106.5 分）",
             "time": "30 分钟", "detail": "议论文为主，常见 150–200 词（备考通行区间 160–200 词）",
             "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "长对话 2 篇", "items": "8 题", "score": "8%",
             "detail": "对话题材更学术化，语速更快", "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "听力篇章 2 篇", "items": "7 题", "score": "7%",
             "detail": "短文理解", "src": ["cet_syllabus_2016"]},
            {"section": "听力", "name": "讲座 / 讲话 3 篇", "items": "10 题", "score": "20%",
             "detail": "六级听力最大区分点，长篇学术讲座，需要边听边记要点",
             "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "选词填空（词汇理解）", "items": "10 题", "score": "5%",
             "detail": "同四级结构，词汇难度上移", "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "长篇阅读（信息匹配）", "items": "10 题", "score": "10%",
             "detail": "同四级结构，文章更长、逻辑更绕", "src": ["cet_syllabus_2016"]},
            {"section": "阅读", "name": "仔细阅读 2 篇", "items": "10 题", "score": "20%",
             "detail": "同四级结构，考查熟词生义与语篇推理", "src": ["cet_syllabus_2016"]},
            {"section": "翻译", "name": "汉译英（段落）", "items": "1 题", "score": "15%（106.5 分）",
             "time": "30 分钟", "detail": "180–200 个汉字，主题偏文化、科技、社会",
             "src": ["cet_syllabus_2016"]},
        ],
    },
    "high_frequency": [
        {"topic": "听力讲座",
         "points": ["先抓主旨句（开头 30 秒）", "笔记只记名词与逻辑词",
                    "学术词高频（theory、evidence、phenomenon）", "态度与结论常在结尾"],
         "src": ["cet_syllabus_2016"]},
        {"topic": "阅读",
         "points": ["熟词生义的快速识别", "长难句主干还原（先找主谓宾）",
                    "作者态度的隐含表达", "段落间逻辑关系（对比、因果、递进）"],
         "src": ["cet_syllabus_2016", "cet_freq_corpus"]},
        {"topic": "翻译",
         "points": ["文化类专有名词（儒家 Confucianism、丝绸之路 the Silk Road）",
                    "长定语的处理（拆分为从句或介词短语）", "数字与年代表达"],
         "src": ["cet_syllabus_2016"]},
        {"topic": "写作",
         "points": ["论点深度与论据具体性（六级对「空泛议论」扣分更重）",
                    "高级替换词与搭配（而非生僻词堆砌）",
                    "段落间逻辑递进（不仅并列）",
                    "词数不低于 150，建议 160–200"],
         "src": ["cet_syllabus_2016"]},
    ],
    "focus": [
        {"title": "六级与四级的分水岭不在「词多」，在「词深」",
         "detail": "1500 个新词之外，更关键是四级旧词的义项扩展与学术语域用法。",
         "src": ["cet_course_req", "cet_freq_corpus"]},
        {"title": "听力讲座是最大失分块",
         "detail": "3 篇讲座占听力 20%（全卷 20%），且篇幅最长、无回放。",
         "src": ["cet_syllabus_2016"]},
    ],
    "sources": ["cet_syllabus_2016", "cet_course_req", "cet_freq_corpus",
                "oss_cet_wordbook", "oss_cet6_freq"],
}

# ---------------------------------------------------------------------
# 2.4 考研英语
# ---------------------------------------------------------------------
EXAM_POINTS["kaoyan"] = {
    "id": "kaoyan",
    "label": "考研英语（一 / 二）",
    "en": "Postgraduate Entrance Exam",
    "profile": {
        "score_scale": "100 分",
        "duration": "180 分钟",
        "paper_count": "英语一 52 题 / 英语二 48 题",
        "note": "科目代码 201 为英语一、204 为英语二；学术硕士一律考英语一，"
                "专业硕士按招生简章确定，近年不少专硕已由英语二改为英语一",
        "src": ["kaoyan_syllabus", "kaoyan_types"],
    },
    "vocabulary": {
        "target": 5500,
        "basis": "大纲词表经独立核实为 5,501 条（含 a/an 合并与 5 个英美拼写变体补丁）；"
                 "一、二词汇量要求基本一致，但英语一阅读中超纲词比例略高",
        "tiers": [
            {"name": "大纲 5,501 词", "detail": "英一二共用底座"},
            {"name": "熟词僻义", "detail": "考研最大区分点 —— 大纲词在学术语境下的生僻义项"},
            {"name": "学术语域词", "detail": "英一选材偏学术期刊，英二偏新闻报道与社会现象"},
            {"name": "98% 流畅门槛约 5,926 词元", "detail": "按 25 套真题语料实测，"
                                                       "背完大纲（5,501）覆盖 88.2% 词次，"
                                                       "仍未达阅读流畅的 98% 门槛"},
        ],
        "focus": [
            "一词多义与熟词僻义（考研区别于四六级的核心）",
            "固定搭配与动词短语的语境义",
            "派生词的词根词缀拆解（应对超纲词）",
            "英一重点：抽象名词与学术动词；英二重点：经济、社会类高频词",
        ],
        "src": ["kaoyan_syllabus", "kaoyan_types", "oss_kaoyan_wordlist"],
    },
    "grammar": {
        "note": "不设独立语法题；语法能力集中体现在长难句理解与翻译题上",
        "items": [
            {"name": "长难句拆解", "detail": "先剥离插入语与后置定语找主干，再逐层挂回修饰成分；"
                                            "英一阅读平均每篇约 4 个长难句",
             "src": ["kaoyan_types"]},
            {"name": "三大从句嵌套", "detail": "定语从句（含介词 + which）、名词性从句、"
                                              "状语从句的嵌套识别",
             "src": ["kaoyan_syllabus"]},
            {"name": "非谓语作后置定语与状语", "detail": "分词短语作定语时的「还原成从句」判断法",
             "src": ["kaoyan_syllabus"]},
            {"name": "特殊结构", "detail": "it 形式主语、倒装、省略、独立主格、"
                                          "平行结构、比较结构、强调结构",
             "src": ["kaoyan_syllabus"]},
            {"name": "翻译的语法处理", "detail": "定语从句拆分译、被动转主动、"
                                                "名词化结构还原为动词、语序调整",
             "src": ["kaoyan_syllabus"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "以下用「英一 / 英二」并列表述；两者同为 100 分 180 分钟",
        "items": [
            {"section": "完形填空", "name": "英语知识运用",
             "items": "20 题 ×0.5 分", "score": "10 分",
             "detail": "英一约 240–280 词文章、偏学术逻辑；英二约 350 词、语言更通俗",
             "src": ["kaoyan_syllabus", "kaoyan_types"]},
            {"section": "阅读理解 Part A", "name": "传统阅读 4 篇",
             "items": "20 题 ×2 分", "score": "40 分",
             "detail": "英一 4 篇共约 1600–1700 词，偏学术期刊；"
                       "英二 4 篇共约 1500–1600 词，偏新闻与社会现象",
             "src": ["kaoyan_syllabus", "kaoyan_types"]},
            {"section": "阅读理解 Part B", "name": "新题型",
             "items": "5 题 ×2 分", "score": "10 分",
             "detail": "英一三种备选：七选五段落填空、排序题、标题匹配（排序题难度最高）；"
                       "英二两种：多项对应、小标题对应",
             "src": ["kaoyan_syllabus", "kaoyan_types"]},
            {"section": "翻译 Part C", "name": "英译汉",
             "items": "英一 5 句 / 英二 1 段", "score": "英一 10 分 / 英二 15 分",
             "detail": "英一：约 400 词文章中划出 5 个长难句（合计约 150 词）；"
                       "英二：翻译约 150 词的完整段落",
             "src": ["kaoyan_syllabus", "kaoyan_types"]},
            {"section": "写作 Part A", "name": "小作文（应用文）",
             "items": "1 题", "score": "10 分（英一英二相同）",
             "detail": "书信、通知、告示等，约 100 词",
             "src": ["kaoyan_syllabus"]},
            {"section": "写作 Part B", "name": "大作文",
             "items": "1 题", "score": "英一 20 分 / 英二 15 分",
             "detail": "英一图画作文，160–200 词；英二图表作文，约 150 词",
             "src": ["kaoyan_syllabus", "kaoyan_types"]},
        ],
    },
    "high_frequency": [
        {"topic": "阅读理解五大题型占比",
         "points": ["细节题约 40%", "推理题约 20%", "态度题约 15%",
                    "主旨题约 15%", "词义猜测题约 10%"],
         "src": ["kaoyan_types"]},
        {"topic": "完形填空",
         "points": ["逻辑关系词（转折、因果、递进、让步）", "固定搭配与动词短语",
                    "上下文语义复现", "英一平均正确率约 52.7%、英二约 68.4%"],
         "src": ["kaoyan_types"]},
        {"topic": "新题型",
         "points": ["七选五：抓段落首尾与指代词", "排序题：抓时间线与逻辑连接词",
                    "标题匹配：抓段落核心概念", "英二多项对应：信息定位"],
         "src": ["kaoyan_types"]},
        {"topic": "翻译",
         "points": ["长难句拆分与重组", "定语从句转前置或独立分句",
                    "被动语态转主动", "抽象名词具体化", "英一此题型平均得分仅约 4.8/10"],
         "src": ["kaoyan_types"]},
        {"topic": "写作",
         "points": ["图画/图表描述段（客观描述 + 抓住对比或趋势）",
                    "原因分析段（2–3 个层面）", "结论与建议段",
                    "主题词准确（考研作文常考社会现象与价值观念）"],
         "src": ["kaoyan_syllabus"]},
        {"topic": "大纲覆盖率与生词密度（25 套真题语料实测）",
         "points": ["大纲按不同词形覆盖 76.8%，按词次覆盖 88.2% —— "
                    "后者才贴近阅读实感，两个口径差 11 个百分点",
                    "4000 词汇量每篇（约 400 词）仍剩约 19 个生词；"
                    "6000 词才降到约 7 个",
                    "出现 ≥50 次的 146 个词形覆盖 51.6% 的词次；"
                    "47% 的词形只出现 1 次、合计仅占 5.3%"],
         "src": ["oss_kaoyan_wordlist"]},
        {"topic": "A 类逻辑/抽象词：唯一可穷尽的词汇问题",
         "points": ["跨 25 年真题总计只有 140 个（however、therefore、assumption 一类）",
                    "不随文章主题变化，经济类与历史类用的是同一批",
                    "每篇只涉及约 6 个，可彻底掌握",
                    "B 类长尾每篇约 69 个、跨篇几乎不重复，背不完，"
                    "只能靠词根词缀与上下文容忍降低成本"],
         "src": ["oss_kaoyan_wordlist"]},
    ],
    "focus": [
        {"title": "长难句是英语一的主战场",
         "detail": "阅读、翻译、新题型三处都建立在「能不能快速还原句子主干」之上。",
         "src": ["kaoyan_types"]},
        {"title": "英语一与英语二的最大分水岭是翻译",
         "detail": "英一 5 个长难句共 10 分、平均得分约 4.8；"
                   "英二一整段 15 分、平均得分折算约 6.9。",
         "src": ["kaoyan_types"]},
        {"title": "阅读 Part A 占 40 分，是绝对重心",
         "detail": "任何备考策略都应以传统阅读为核心，其余题型为补充。",
         "src": ["kaoyan_syllabus"]},
        {"title": "「背完大纲就够」是错的，但差得不多",
         "detail": "大纲覆盖 88.2% 词次，距 98% 的流畅门槛约缺 400+ 词元。"
                   "正确做法不是去背「超纲词表」（64.8% 的词形只出现 1–2 次且跨篇不重复），"
                   "而是把 A 类 140 个逻辑词彻底拿下，再对长尾词降低单个生词的代价。",
         "src": ["oss_kaoyan_wordlist"]},
    ],
    "sources": ["kaoyan_syllabus", "kaoyan_types", "oss_kaoyan_wordlist"],
}

# ---------------------------------------------------------------------
# 2.5 雅思（学术类）
# ---------------------------------------------------------------------
EXAM_POINTS["ielts"] = {
    "id": "ielts",
    "label": "雅思（学术类 IELTS Academic）",
    "en": "IELTS Academic",
    "profile": {
        "score_scale": "1–9 分制（整分或半分），总分取四项平均后四舍五入到最近半分",
        "duration": "约 2 小时 45 分钟（听力 30 + 阅读 60 + 写作 60 + 口语 11–14）",
        "paper_count": "听力 40 题 + 阅读 40 题 + 写作 2 题 + 口语 3 部分",
        "note": "听力、阅读、写作三科同日连考且中间无休息；"
                "口语可在前后 7 天内单独安排",
        "src": ["ielts_org_official"],
    },
    "vocabulary": {
        "target": 8000,
        "basis": "雅思不发布官方词汇表。通行备考口径为 6000–8000 词："
                 "6.5 分约 6000–7000 词，7 分以上约 8000 词",
        "tiers": [
            {"name": "学术词表 AWL 类", "detail": "跨学科学术词（analyse、significant、"
                                                 "hypothesis），阅读与写作共用"},
            {"name": "话题场景词", "detail": "教育、环境、科技、健康、城市化、"
                                            "文化等 Task 2 高频话题"},
            {"name": "同义替换网络", "detail": "雅思听读的灵魂 —— 题干与原文靠同义改写对应"},
        ],
        "focus": [
            "同义替换（paraphrase）能力，比词量更决定分数",
            "学术写作的正式语域词（避免口语词如 kids、a lot of）",
            "拼写准确性（听力填空与写作都直接扣分）",
            "口语的话题词汇与地道搭配（collocation、idiomatic phrase）",
        ],
        "src": ["ielts_no_wordlist", "ielts_band_descriptors"],
    },
    "grammar": {
        "note": "不设独立语法题；通过写作「语法多样性与准确性」与口语同名评分项直接计分",
        "items": [
            {"name": "句式多样性", "detail": "评分要求简单句、并列句、复合句混用；"
                                            "全篇简单句会限制分数上限",
             "src": ["ielts_band_descriptors"]},
            {"name": "复杂从句与条件句", "detail": "定语从句、名词性从句、"
                                                  "让步与条件状语从句、虚拟语气",
             "src": ["ielts_band_descriptors"]},
            {"name": "时态准确性", "detail": "Task 1 描述图表用一般现在时/过去时；"
                                            "Task 2 议论用现在时与情态动词",
             "src": ["ielts_band_descriptors"]},
            {"name": "被动语态与名词化", "detail": "学术写作的客观化表达"
                                                  "（It is widely acknowledged that...）",
             "src": ["ielts_band_descriptors"]},
            {"name": "衔接手段", "detail": "连贯与衔接（Coherence and Cohesion）"
                                          "要求连接词 + 指代 + 段落主题句的自然使用，"
                                          "反对机械堆砌连接词",
             "src": ["ielts_band_descriptors"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "以下为学术类（Academic）结构，培训类（General Training）阅读与写作 Task 1 不同",
        "items": [
            {"section": "听力", "name": "4 个部分 40 题", "items": "40 题", "score": "每题 1 分",
             "time": "30 分钟 + 10 分钟誊写",
             "detail": "Part 1 日常双人对话；Part 2 日常独白；"
                       "Part 3 教育/培训场景最多四人对话；Part 4 学术独白讲座。"
                       "录音只播放一遍，含多国口音",
             "src": ["ielts_org_official"]},
            {"section": "听力题型", "name": "题型清单", "items": "—", "score": "—",
             "detail": "多选、匹配、地图/平面图标注、表单填空、笔记填空、"
                       "表格填空、流程图填空、摘要填空、句子填空、简答",
             "src": ["ielts_org_official"]},
            {"section": "阅读", "name": "3 篇学术文章 40 题", "items": "40 题", "score": "每题 1 分",
             "time": "60 分钟",
             "detail": "选材自书籍、期刊、杂志、报纸，可含图表；"
                       "无额外誊写时间（答案须直接写在答题卡上）",
             "src": ["ielts_org_official"]},
            {"section": "阅读题型", "name": "题型清单", "items": "—", "score": "—",
             "detail": "多选、判断正误（True/False/Not Given）、"
                       "观点判断（Yes/No/Not Given）、信息匹配、标题匹配、"
                       "特征匹配、句子结尾匹配、各类填空、简答",
             "src": ["ielts_org_official"]},
            {"section": "写作", "name": "Task 1 图表描述", "items": "1 题", "score": "占写作 1/3 权重",
             "time": "建议 20 分钟", "detail": "≥150 词，描述图表/表格/流程/地图；"
                                              "考查客观描述能力，不可加入个人观点",
             "src": ["ielts_org_official"]},
            {"section": "写作", "name": "Task 2 议论文", "items": "1 题", "score": "占写作 2/3 权重",
             "time": "建议 40 分钟", "detail": "≥250 词，就某一社会议题展开论述；"
                                              "Task 2 权重高于 Task 1",
             "src": ["ielts_org_official"]},
            {"section": "口语", "name": "三个部分", "items": "3 部分", "score": "1–9 分",
             "time": "11–14 分钟",
             "detail": "Part 1 日常问答（4–5 分钟）；"
                       "Part 2 就给定话题独自陈述 1–2 分钟后回答追问；"
                       "Part 3 围绕 Part 2 话题的深度讨论（4–5 分钟）",
             "src": ["ielts_org_official"]},
        ],
    },
    "high_frequency": [
        {"topic": "写作四项评分标准（权重相同）",
         "points": ["任务完成情况（Task 1）/ 任务回答情况（Task 2）",
                    "连贯与衔接（Coherence and Cohesion）",
                    "词汇丰富度（Lexical Resource）",
                    "语法多样性与准确性（Grammatical Range and Accuracy）"],
         "src": ["ielts_band_descriptors", "ielts_org_official"]},
        {"topic": "口语四项评分标准（各占 25%）",
         "points": ["流利度与连贯性", "词汇丰富度",
                    "语法多样性与准确性", "发音"],
         "src": ["ielts_band_descriptors"]},
        {"topic": "听力高频失分点",
         "points": ["拼写错误（地名、人名、学科名）—— 已整理的拼写风险词库去重后达 2,032 条，"
                    "按星期、月份、数字、颜色、学科等语义场组织，"
                    "并需区分 UK/US 拼写与 week-weak 这类易混对",
                    "数字与字母混读（如 15/50）",
                    "同义替换未识别",
                    "地图题的方位介词（opposite、adjacent to）"],
         "src": ["ielts_org_official", "oss_ielts_spelling"]},
        {"topic": "阅读高频失分点",
         "points": ["True/False/Not Given 与 Yes/No/Not Given 的区别（事实 vs 观点）",
                    "标题匹配（List of Headings）的段落主旨概括",
                    "60 分钟 3 篇的时间分配（建议 17/20/23 分钟）",
                    "Matching 题先审 NB 提示：出现 NB 即表示同一选项可被重复选用，"
                    "这是最容易漏掉的审题点"],
         "src": ["ielts_org_official", "oss_ielts_notes"]},
        {"topic": "Task 1 高频语言功能",
         "points": ["趋势描述（rise、decline、plateau、fluctuate）",
                    "程度修饰（sharply、slightly、steadily）",
                    "比较与极值（the highest、twice as much as）",
                    "流程图被动语态、地图题方位与变化表述"],
         "src": ["ielts_org_official"]},
        {"topic": "Task 2 高频话题",
         "points": ["教育、环境、科技、健康、城市化、"
                    "政府职能、媒体、文化全球化"],
         "src": ["ielts_org_official"]},
    ],
    "focus": [
        {"title": "写作 Task 2 权重高于 Task 1",
         "detail": "Task 2 是议论文（≥250 词），评分权重约为 Task 1 的两倍 —— "
                   "时间不够时应保全 Task 2。",
         "src": ["ielts_org_official"]},
        {"title": "听力有 10 分钟誊写，阅读没有",
         "detail": "阅读必须边做边把答案写进答题卡，这是最容易被忽视的时间陷阱。",
         "src": ["ielts_org_official"]},
        {"title": "听力与阅读按答对题数换分",
         "detail": "40 题制：听力 23 题约 6 分、30 题约 7 分；"
                   "学术类阅读 23 题约 6 分、30 题约 7 分。",
         "src": ["ielts_org_official"]},
    ],
    "sources": ["ielts_org_official", "ielts_band_descriptors", "ielts_no_wordlist",
                "oss_ielts_spelling", "oss_ielts_notes"],
}

# ---------------------------------------------------------------------
# 2.6 托福 iBT
# ---------------------------------------------------------------------
EXAM_POINTS["toefl"] = {
    "id": "toefl",
    "label": "托福 iBT（TOEFL iBT）",
    "en": "TOEFL iBT",
    "profile": {
        "score_scale": "1–6 分制（每 0.5 一档），总分为四项平均；"
                       "2026-01-21 起两年过渡期内同时给出 0–120 对照分",
        "duration": "约 2 小时（不含各部分前的指引）",
        "paper_count": "阅读 50 题 + 听力 47 题 + 写作 12 题 + 口语 11 题",
        "note": "2026-01-21 起改为自适应考试，题量与时长会随作答情况浮动；"
                "全程无固定休息时间",
        "effective_from": "2026-01-21",
        "src": ["ets_toefl_2026"],
    },
    "vocabulary": {
        "target": 10000,
        "basis": "托福不发布官方词汇表。通行备考口径 8000–10000 词，"
                 "其中含约 1000+ 学科专业词（生物、天文、地质、艺术史等）",
        "tiers": [
            {"name": "高中 + 四级底座约 4000", "detail": "与高考、四级词汇高度重叠"},
            {"name": "托福核心约 2000", "detail": "学术高频词，阅读与听力共用"},
            {"name": "学科专业词约 1000+", "detail": "按学科场景成组记忆，"
                                                    "阅读中常可直接忽略细节"},
        ],
        "focus": [
            "同义词辨析（阅读词汇题直接考同义替换）",
            "一词多义与固定搭配（如 game 作「猎物」）",
            "学术听力中的连读、弱读与重音辨识",
            "核心原则：托福词汇重「用」不重「背」——"
            "阅读需认得、听力需听得出、写作需敲得准、口语需说得出",
        ],
        "src": ["ets_toefl_no_wordlist", "ets_toefl_2026"],
    },
    "grammar": {
        "note": "不设独立语法题；2026 新制写作新增「完成句子（Build a Sentence）」"
                "题型，直接考句子结构构建",
        "items": [
            {"name": "句子结构完整性", "detail": "新制写作的「完成句子」题直接考查"
                                                "主谓宾完整与从句连接",
             "src": ["ets_toefl_2026"]},
            {"name": "学术写作句式", "detail": "「学术讨论写作」要求在课堂讨论语境下"
                                              "陈述并支持观点，需准确使用从句与连接词",
             "src": ["ets_toefl_2026"]},
            {"name": "时态与主谓一致", "detail": "口语与写作的准确性隐性评分点",
             "src": ["ets_toefl_2026"]},
            {"name": "长句理解", "detail": "阅读学术长句的插入语、后置定语与"
                                          "多重从句拆解",
             "src": ["ets_toefl_legacy"]},
        ],
        "cross_check": ["yulaoshizuikeai/English-Note"],
    },
    "question_types": {
        "note": "以下为 2026-01-21 起生效的自适应新制；旧制结构见 legacy 说明",
        "items": [
            {"section": "阅读", "name": "补全单词 / 日常生活 / 学术文章",
             "items": "50 题", "score": "1–6 分", "time": "30 分钟",
             "detail": "三种任务混合：补全单词（Complete the Words）、"
                       "日常生活阅读（Read in Daily Life）、学术文章阅读（Read an Academic Passage）",
             "src": ["ets_toefl_2026"]},
            {"section": "听力", "name": "听并选择回应 / 对话 / 公告 / 学术讲座",
             "items": "47 题", "score": "1–6 分", "time": "29 分钟",
             "detail": "Listen and Choose a Response、Listen to a Conversation、"
                       "Listen to an Announcement、Listen to an Academic Talk",
             "src": ["ets_toefl_2026"]},
            {"section": "写作", "name": "完成句子 / 邮件写作 / 学术讨论写作",
             "items": "12 题", "score": "1–6 分", "time": "23 分钟",
             "detail": "Build a Sentence、Write an Email、"
                       "Write for an Academic Discussion",
             "src": ["ets_toefl_2026"]},
            {"section": "口语", "name": "听力及复述 / 面试题",
             "items": "11 题", "score": "1–6 分", "time": "8 分钟",
             "detail": "Listen and Repeat（听并复述）、Take an Interview（面试问答）",
             "src": ["ets_toefl_2026"]},
            {"section": "【旧制参考】阅读", "name": "2 篇 ×10 题",
             "items": "20 题", "score": "0–30 分", "time": "35 分钟",
             "detail": "每篇约 700 词的多焦点文章（对比/因果类），"
                       "旧制题型：词汇题、事实信息题、否定事实题、推断题、"
                       "修辞目的题、句子简化题、插入文本题、总结题、表格题",
             "effective_until": "2026-01-20",
             "src": ["ets_toefl_legacy"]},
            {"section": "【旧制参考】听力", "name": "3 讲座 + 2 对话",
             "items": "28 题", "score": "0–30 分", "time": "36 分钟",
             "detail": "讲座每段 3–5 分钟各 6 题；对话每段约 3 分钟各 5 题。"
                       "题型：主旨题、细节题、功能题、态度题、组织结构题、"
                       "推断题、连接内容题",
             "effective_until": "2026-01-20",
             "src": ["ets_toefl_legacy"]},
            {"section": "【旧制参考】写作", "name": "综合写作 + 学术讨论写作",
             "items": "2 题", "score": "0–30 分", "time": "29 分钟",
             "detail": "综合写作 20 分钟（读 + 听 + 写，150–225 词）；"
                       "学术讨论写作 10 分钟；口语与写作均由 AI + ETS 认证评分员共同评分",
             "effective_until": "2026-01-20",
             "src": ["ets_toefl_legacy"]},
        ],
    },
    "high_frequency": [
        {"topic": "阅读高频题型（旧制题型体系，新制仍通用）",
         "points": ["词汇题（同义替换）", "事实信息题与否定事实题",
                    "推断题", "修辞目的题", "句子简化题",
                    "插入文本题", "总结题（六选三）"],
         "src": ["ets_toefl_legacy"]},
        {"topic": "听力高频考点",
         "points": ["主旨与目的", "关键细节与举例", "说话人态度与语气",
                    "课堂互动中的功能语言", "讲座组织结构（分类、对比、因果、时间线）"],
         "src": ["ets_toefl_legacy"]},
        {"topic": "口语",
         "points": ["新制：听并复述（准确性 + 流利度）、面试问答",
                    "旧制：独立任务（15 秒准备 / 45 秒作答）、"
                    "综合任务（30 秒准备 / 60 秒作答）",
                    "评分看表达清晰度与信息完整度，而非口音"],
         "src": ["ets_toefl_2026", "ets_toefl_legacy"]},
        {"topic": "写作",
         "points": ["新制「完成句子」考语法与逻辑连接",
                    "邮件写作考语域得体（正式/非正式）",
                    "学术讨论写作考「表明立场 + 论据 + 回应他人观点」"],
         "src": ["ets_toefl_2026"]},
    ],
    "focus": [
        {"title": "2026 新制最关键的三个变化",
         "detail": "（1）改为自适应，题量时长浮动；"
                   "（2）新增「补全单词」「完成句子」「邮件写作」「听并复述」等实用任务；"
                   "（3）计分改为 1–6 分制并与 CEFR 对齐。",
         "src": ["ets_toefl_2026"]},
        {"title": "全学术语料",
         "detail": "ETS 明确考试内容 100% 为学术语料并含综合任务，"
                   "备考必须按学科场景积累。",
         "src": ["ets_toefl_legacy"]},
        {"title": "旧资料仍有参考价值",
         "detail": "2026-01-20 前的所有题型解析仍可用于训练阅读与听力核心能力，"
                   "但报分口径与题量描述已不适用。",
         "src": ["ets_toefl_legacy", "ets_toefl_2026"]},
    ],
    "sources": ["ets_toefl_2026", "ets_toefl_legacy", "ets_toefl_no_wordlist"],
}

ORDER: list[str] = ["high_school", "cet4", "cet6", "kaoyan", "ielts", "toefl"]

# 来源短标签：前端在每条数据后挂一个徽章用它 —— 直接显示 `cet_syllabus_2016`
# 这种 id 对用户毫无意义，而完整标题又太长会把行撑散。
SHORT: dict[str, str] = {
    "moe_curriculum_2017": "高中课标",
    "gaokao_structure": "高考卷结构",
    "gaokao_grammar_fill": "语法填空规律",
    "cet_syllabus_2016": "四六级大纲",
    "cet_course_req": "教学要求",
    "cet_freq_corpus": "真题词频",
    "kaoyan_syllabus": "考研大纲",
    "kaoyan_types": "考研题型统计",
    "ielts_org_official": "IELTS 官方",
    "ielts_band_descriptors": "雅思评分标准",
    "ielts_no_wordlist": "无官方词表",
    "ets_toefl_2026": "ETS 新制",
    "ets_toefl_legacy": "ETS 旧制",
    "ets_toefl_no_wordlist": "托福词量口径",
    "oss_kaoyan_wordlist": "考研词表核实",
    "oss_cet_wordbook": "四六级词书",
    "oss_cet6_freq": "六级词频统计",
    "oss_ielts_spelling": "雅思拼写库",
    "oss_ielts_notes": "雅思题型笔记",
}


# =====================================================================
# 三、查询接口
# =====================================================================

def get(level_id: str) -> dict | None:
    """取某档完整考点。未知 ID 返回 None（让调用方决定兜底策略）。"""
    return EXAM_POINTS.get((level_id or "").strip().lower())


def require(level_id: str) -> dict:
    """取某档考点，未知 ID 退回 high_school —— 与 levels.get() 的兜底保持一致。"""
    return get(level_id) or EXAM_POINTS["high_school"]


def section(level_id: str, name: str) -> dict | list | None:
    """
    取某档的某一维度。
    name 取值：vocabulary / grammar / question_types / high_frequency / focus / profile
    """
    data = get(level_id)
    if not data:
        return None
    return data.get(name)


def sources_of(level_id: str) -> list[dict]:
    """取某档引用的全部来源（已展开为完整条目，带 tier 与链接）。"""
    data = get(level_id)
    if not data:
        return []
    out = []
    for sid in data.get("sources", []):
        s = SOURCES.get(sid)
        if s:
            out.append({"id": sid, "short": SHORT.get(sid, sid), **s})
    return out


def summary() -> list[dict]:
    """给前端 / API 用的精简单（不含正文）。"""
    out = []
    for lid in ORDER:
        d = EXAM_POINTS[lid]
        p = d.get("profile", {})
        out.append({
            "id": d["id"],
            "label": d["label"],
            "en": d["en"],
            "score_scale": p.get("score_scale", ""),
            "duration": p.get("duration", ""),
            "paper_count": p.get("paper_count", ""),
            "vocab_target": d.get("vocabulary", {}).get("target"),
            "grammar_count": len(d.get("grammar", {}).get("items", [])),
            "question_type_count": len(d.get("question_types", {}).get("items", [])),
            "source_count": len(d.get("sources", [])),
            "has_legacy": any(i.get("effective_until") for i in
                              d.get("question_types", {}).get("items", [])),
        })
    return out


def stats() -> dict:
    total_grammar = sum(len(EXAM_POINTS[l]["grammar"]["items"]) for l in ORDER)
    total_qt = sum(len(EXAM_POINTS[l]["question_types"]["items"]) for l in ORDER)
    total_hf = sum(len(EXAM_POINTS[l]["high_frequency"]) for l in ORDER)
    total_focus = sum(len(EXAM_POINTS[l]["focus"]) for l in ORDER)
    return {
        "levels": len(ORDER),
        "sources": len(SOURCES),
        "oss_sources": len(OSS_SOURCES),
        "grammar_items": total_grammar,
        "question_types": total_qt,
        "high_frequency_topics": total_hf,
        "focus_items": total_focus,
    }


# =====================================================================
# 四、提示层：把考点压成 LLM 能吃的上下文
# =====================================================================

# 每档最多注入多少条目 —— 提示词不是越长越好，超了反而稀释注意力。
_MAX_GRAMMAR = 8
_MAX_HF = 4
_MAX_FOCUS = 4
_MAX_CHARS = 2600


def prompt_context(level_id: str, sections: tuple[str, ...] = (
        "question_types", "high_frequency", "grammar", "focus")) -> str:
    """
    生成紧凑的考点上下文，供注入 LLM 系统提示。

    刻意不注入完整数据：一是太长会稀释注意力，二是模型可能把考点当成
    「必须全部标注」的清单，导致标注过密。这里只给方向。
    """
    d = get(level_id)
    if not d:
        return ""

    lines: list[str] = [f"【考试阶段】{d['label']}"]
    p = d.get("profile", {})
    if p:
        lines.append(f"【卷面】{p.get('score_scale', '')}；{p.get('duration', '')}；"
                     f"{p.get('paper_count', '')}")

    if "question_types" in sections:
        qts = d["question_types"]["items"]
        # 只取现行题型（有 effective_until 的是旧制，不进提示）
        cur = [q for q in qts if not q.get("effective_until")]
        txt = "；".join(
            f"{q['section']}：{q['name']}"
            + (f"（{q['items']}，{q['score']}）" if q.get("items") not in (None, "—") else "")
            for q in cur[:8]
        )
        if txt:
            lines.append(f"【题型与分值】{txt}")

    if "high_frequency" in sections:
        for t in d.get("high_frequency", [])[:_MAX_HF]:
            pts = "、".join(t["points"][:5])
            lines.append(f"【高频考点·{t['topic']}】{pts}")

    if "grammar" in sections:
        gs = d["grammar"]["items"][:_MAX_GRAMMAR]
        lines.append("【重点语法】" + "；".join(
            f"{g['name']}（{g['detail'][:40]}）" for g in gs))

    if "focus" in sections:
        for f in d.get("focus", [])[:_MAX_FOCUS]:
            lines.append(f"【考查重点·{f['title']}】{f['detail'][:70]}")

    out = "\n".join(lines)
    return out[:_MAX_CHARS]


def grammar_names(level_id: str) -> list[str]:
    """给密度编排用的「本级重点语法名」列表。"""
    d = get(level_id)
    if not d:
        return []
    return [g["name"] for g in d.get("grammar", {}).get("items", [])]


def all_sources() -> dict[str, dict]:
    """来源总表（API 用，便于前端列「依据」）。"""
    return {"sources": SOURCES, "oss": OSS_SOURCES}
