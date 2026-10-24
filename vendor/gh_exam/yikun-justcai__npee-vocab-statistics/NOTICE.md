# 第三方内容与使用声明

本仓库的**代码**以 MIT 协议发布（见 `LICENSE`）。但仓库里还包含来自他处的数据，
它们的权利不属于本项目。这里逐项说明。

---

## 1. 考研真题原文 —— **不在本仓库内**

考研（英语一）历年真题的著作权属于**教育部教育考试院**及相关出版机构。

本仓库**只发布统计结果，不发布试卷全文**，也不发布由 PDF 抽取的文本：

- `raw/`（抽取文本）与 `pdfs/`（原始 PDF）已在 `.gitignore` 中排除；
- CI 里有一道 `no-exam-text` 检查，确保 `raw/`、`pdfs/` 与任何 `.pdf` 都不会被提交；
- `examples/sample_corpus/` 里是**为本仓库撰写的合成语料**，
  题材（交通需求、睡眠与记忆、远程办公、海洋塑料）与真题无关，不含任何真题句子。

统计产出（词表、词频、分档清单）是**词汇与数字的集合**，
不含原文句子，可以自由使用。

## 2. 大纲词表 `data/kaoyan_syllabus_verified.txt`

5,501 条 `词<TAB>释义`。构成与修订依据见
`docs/methodology/wordlist-revision.md`，来源有两条：

1. 一份流传较广的考纲词表整理（gb18030，5,491 条），
   与本项目参考的 [YSMull/words-statistics](https://github.com/YSMull/words-statistics)
   所用词表同源；
2. [mahavivo/english-wordlists](https://github.com/mahavivo/english-wordlists)
   的 NPEE 词表，用于交叉验证。

再加 6 条有外部依据的手工补丁（`an` 与 5 个英美拼写变体）。

**这份词表的权利归原始整理者 / 出版方所有。** 本项目把它作为**研究用的比对基准**
收录，仅为复现统计结果之必需。若权利方有异议，请开 issue，
我们会立即移除该文件并改为「用户自备」。

## 3. NLTK 数据

词形还原依赖 NLTK 的 `wordnet` / `omw-1.4` / `averaged_perceptron_tagger_eng`
等数据包，由用户在首次运行时自行下载，不随本仓库分发。
它们各自的许可见 [nltk_data](https://github.com/nltk/nltk_data)。

## 4. 引用到的方法论

本项目的方法与问题设定受
[YSMull/words-statistics](https://github.com/YSMull/words-statistics) 启发
（2014 年建、2017 年停更）。上游仓库因关键依赖 NodeBox `en` 库未随仓库提供而无法运行，
且数据停在 2012 年，因此本项目用一套独立的 Python 管线重做。

**本项目与该仓库没有代码继承关系**，是独立实现。

---

## 如果你要复用本项目的产出

| 你想用 | 需要做什么 |
|---|---|
| 代码（`src/`、`tests/`、`examples/`） | 遵守 MIT，保留版权声明即可 |
| 统计产出（`reports/` 里的数字与词表） | 自由使用，建议注明来源 |
| `data/kaoyan_syllabus_verified.txt` | 请自行判断权利风险，本项目不代为授权 |
| 真题原文 | **本仓库没有**，需自行取得合法来源 |
