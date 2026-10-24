# 语法、题型与词汇标签

## 目录

1. 统一证据边界
2. 语法标签
3. 问题类型
4. 词汇标签与 lemma
5. 难度分级
6. 报告解释

## 统一证据边界

所有自动语法标签和问题类型都由确定性规则启发式生成，只服务于检索、抽样和统计，不是答案或人工裁决。

- corpus：`grammar_tags` 配套 `tag_review_status: "heuristic_unreviewed"`、`tag_confidence: null`；
- questions：`question_type` 配套 `type_review_status: "heuristic_unreviewed"`、`type_confidence: null`。

即使规则内部存在强弱信号，也不得把它转换为对外置信度。`that`、`as`、`doing`、`done`、引号和设问关键词都可能具有多种功能；教学时必须回到完整原句或完整题干重新判断。

`corpus-insights-reviewed.md` 中的 reviewed 只表示当前统计使用双源精确文本，不表示 `grammar_tags`、主干、从句边界或修饰关系已经人工复核。

## 语法标签

- `relative_clause`：关系代词或关系副词引导的定语从句候选。
- `noun_clause`：主语、宾语、表语或同位语从句候选。
- `adverbial_clause`：时间、原因、条件、让步、比较、目的或结果从句候选。
- `non_finite`：不定式、现在分词、过去分词或动名词候选。
- `passive_voice`：be/get 与过去分词构成的被动候选。
- `parenthetical`：破折号、括号或插入成分候选。
- `apposition`：同位语或解释性名词短语候选。
- `comparison`：比较级、`as...as`、`the more...the more` 等候选。
- `inversion`：否定/限制成分前置、nor/neither、only 等倒装候选。
- `coordination`：多重并列或并列层次候选。
- `prepositional_postmodifier`：介词短语后置修饰候选。
- `abstract_subject`：抽象名词或名词化结构作句首主语候选。
- `complex_reference`：跨分句代词或指代链候选。
- `negation_transfer`：think/believe/suppose 等结构中的否定转移候选。

讲解长难句时重新提取最小主干、全部谓语/非谓语、从句边界和修饰指向；发现标签错误时直接纠正，不顺着标签讲错。

## 问题类型

- `detail_or_reference`：细节、指代或定位信息候选。
- `word_or_phrase_meaning`：词义、短语义或语境释义候选。
- `main_idea_or_title`：主旨、中心思想或标题候选。
- `attitude_or_tone`：作者/人物态度或语气候选。
- `inference`：推断、暗示或可推出结论候选。
- `example_or_rhetorical_function`：例子、引用或修辞功能候选。
- `text_structure_or_purpose`：篇章结构、段落目的或写作意图候选。
- `reason_or_cause`：原因、理由或因果解释候选。

这些类型由题干措辞匹配，不代表答案推理链已经人工核验。`exam-points.md` 中的分布和考点也是 `heuristic_unreviewed`；答案索引只确认答案字母存在，不能自动证明题型或命题意图。

## 词汇标签与 lemma

句子层的词汇标签包括：

- `academic_verb`：研究、论证、表明、构成、处理等学术动词候选。
- `familiar_word_unfamiliar_meaning`：address、issue、subject、account 等熟词僻义候选。
- `abstract_noun`：名词化或抽象概念密集候选。
- `logical_connector`：转折、因果、让步、递进、例证等逻辑标记候选。
- `fixed_collocation`：规则表中可稳定识别的固定搭配候选。

词汇资产统计大小写归一化后的表层词形和每次出现位置。当前没有经过验证的词形还原器，因此每条词汇记录保持 `lemma: null`、`lemma_status: "not_computed"`。不能用简单删后缀制造 lemma，也不能把表层词频说成词元、词族、词义或官方大纲覆盖。

## 难度分级

- 1级：单一主干和简单修饰。
- 2级：一个明显从句或非谓语结构。
- 3级：两个以上修饰层次或较强逻辑连接。
- 4级：主干被插入、嵌套、长后置修饰或抽象表达遮蔽。
- 5级：多层嵌套，同时含复杂指代、逻辑或名词化。

难度综合词数、标签数量、嵌套信号、标点和逻辑结构，同样属于启发式初筛，不是学习者成绩或人工句法等级。

## 报告解释

- `material-openability.md` 说明文件能否视觉浏览和机器提取，不证明文本正确；
- `vocabulary-coverage.md` 说明表层词形与年份覆盖，不证明 lemma 或官方词表覆盖；
- `exam-points.md` 汇总问题类型和考点信号，不代表人工命题分析；
- `corpus-insights-reviewed.md` 只提高原文文本可信度，不提高自动语法标签可信度。
