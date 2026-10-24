# 考研英语（一）真题词汇统计

[![CI](https://github.com/yikun-justcai/npee-vocab-statistics/actions/workflows/ci.yml/badge.svg)](https://github.com/yikun-justcai/npee-vocab-statistics/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

> 用 2002–2026 共 **25 套**英语（一）真题的正文语料，回答一个问题：
> **把大纲词汇背完，够用吗？**

**63,174** 词元 ｜ **7,189** 个不同词形 ｜ 大纲覆盖率 **76.8%**（不同词）/ **88.2%**（次数加权）

---

## 结论速览

| 问题 | 答案 |
|---|---|
| 背完大纲词汇，能读懂真题吗？ | **不能。** 4000 词汇量每篇仍有约 **19 个生词**，阅读流畅的 98% 门槛需要约 **5,926** 个词元 |
| 该背什么？ | **高频词。** 出现 ≥50 次的 **146 个**词形覆盖了 **51.6%** 的词次；而 47% 的词形只出现 1 次，加起来只占 5.3% 词次 |
| 为什么「超纲词表」没用？ | **64.8%** 的词形只出现 1–2 次，且跨篇几乎不重复。下一次考试用的是另一批词 |
| 有没有能彻底解决的词汇问题？ | **有，而且是唯一的：A 类逻辑/抽象词。** 跨 25 年总共只有 **140 个**，每篇只涉及约 **6 个** |
| 那剩下的怎么办？ | B 类长尾每篇约 **69 个**生词，背不完——只能降低「每个生词的代价」（词根词缀 + 上下文容忍） |

**可直接用的产出**：[分层复习清单](reports/分层复习清单.md)（T0–T4，547 词）、
[A 类逻辑与抽象词表](reports/A类-逻辑与抽象词表.md)（140 词，按功能分组）、
[高频内容词表](reports/高频内容词表.md)（499 词）、
[B 类长尾词处理策略](docs/长尾词处理策略.md)。

> **实际需要专门投入的只有 T1+T2 ≈ 200 个词。**

---

## 核心发现

### 1. 覆盖率必须按词次（token）算，不能按「不同词数」算

「大纲覆盖率 76.8%」听上去很糟，但它问的是
「语料里出现过的**不同词形**有多少在大纲内」。
真正贴近实感的是**次数加权**口径：**88.2%** ——
你实际读到的词次里，有 88.2% 在大纲内。

两者差 11 个百分点，是因为出现次数最多的那批词（the/of/and/be…）几乎全在大纲内，
而真正「超纲」的是偶尔露面的低频词。

**不要依赖词表的那个口径**：

| 词汇量 | 覆盖词次 | 每篇（约 400 词）剩余生词 |
|---|---|---|
| 2,000 | 87.5% | 47 |
| 3,000 | 92.1% | 29 |
| 4,000 | 95.0% | 19 |
| 5,000 | 96.5% | 13 |
| 6,000 | 98.1% | 7 |

阅读流畅的公认门槛是 **98%**，对应约 **5,926 个词元**。
所以「背完大纲（5,501 词）就够」是错的——差得不算远，但确实不够。

### 2. 「超纲词」这个概念本身有问题

| 出现次数 | 词形数 | 占全部词形 | 占全部词次 |
|---|---|---|---|
| 1 次 | 3,377 | 47.0% | 5.3% |
| 2 次 | 1,067 | 14.8% | 3.4% |
| 3–5 次 | 1,221 | 17.0% | 7.2% |
| 6–10 次 | 637 | 8.9% | 7.6% |
| 11–50 次 | 741 | 10.3% | 24.9% |
| **50 次以上** | **146** | **2.0%** | **51.6%** |

**该投入的是高频词，不是「超纲词表」。** 一半以上的词次集中在 146 个词形上。

### 3. 词汇问题要分成两类处理（最重要的结论）

| 类型 | 规模 | 每篇负载 | 能解决吗 |
|---|---|---|---|
| **A 类** 逻辑 / 抽象词 | **140 个**（跨 25 年总计） | 约 6 个 | ✅ **可以穷尽掌握** |
| **B 类** 长尾实词 | 5,940 个（≤2 次） | 约 69 个 | ❌ 背不完，只能降代价 |

A 类词不随文章主题变化——经济类和历史类用的是同一批逻辑词
（`however` / `therefore` / `suggest` / `assumption`…），出现次数高、复用率极高。
**这是考研英语里唯一可以「彻底解决」的词汇问题。**

B 类跨篇不重复，任何词表都覆盖不了。目标是让生词**不阻断理解**，而不是零生词。
具体三条路径见 [长尾词处理策略](docs/长尾词处理策略.md)。

### 4. 相邻年份的词汇重合率

| 口径 | 均值 | 含义 |
|---|---|---|
| Jaccard `\|A∩B\| / \|A∪B\|` | **21.4%** | 保守，受各年词汇量影响 |
| 重合系数 `\|A∩B\| / min(\|A\|,\|B\|)` | **36.2%** | 「今年的词有多少去年见过」，更贴近学生实感 |

25 年**每年都出现**的恒定词有 **59 个**。

---

## 快速开始

### 安装

```bash
git clone https://github.com/yikun-justcai/npee-vocab-statistics.git
cd npee-vocab-statistics
pip install -e ".[dev]"

# 首次运行需要下载 nltk 数据（词形还原用）
python -c "import nltk; [nltk.download(p) for p in ('wordnet','omw-1.4','averaged_perceptron_tagger_eng','punkt','punkt_tab')]"
```

### 用合成样例语料跑一遍（不需要真题）

仓库自带一份**为本项目撰写的合成语料**，题材与真题无关，可以放心跑：

```bash
python -m npee_vocab all --corpus-dir examples/sample_corpus --output-dir /tmp/demo
python -m npee_vocab compare-modes --corpus-dir examples/sample_corpus
```

### 用你自己的真题跑

**真题原文不在本仓库内**（版权原因，见 [NOTICE](NOTICE.md)）。请自备 PDF：

```bash
# 1. 把真题 PDF 放进 pdfs/，文件名用年份，如 2019.pdf
python -m npee_vocab extract --pdf-dir pdfs --corpus-dir raw

# 2. 跑全部产出
python -m npee_vocab all
```

### 命令行

```bash
python -m npee_vocab extract         # PDF -> raw/*.txt
python -m npee_vocab stats           # 主统计 -> stats.json + 统计报告 + 高频内容词表
python -m npee_vocab coverage        # token 覆盖率曲线（不依赖任何词表）
python -m npee_vocab reading         # 阅读生词密度
python -m npee_vocab tiers           # 分层复习清单 T0–T4
python -m npee_vocab a-list          # A 类词表（按功能分组）
python -m npee_vocab ab              # A / B 类词假设检验
python -m npee_vocab all             # 全部写入 reports/
python -m npee_vocab compare-modes   # 量化管线口径差异
```

所有路径都是参数，没有硬编码：

```bash
python -m npee_vocab stats \
  --corpus-dir raw \
  --wordlist data/kaoyan_syllabus_verified.txt \
  --output-dir reports \
  --clean-mode blocks \
  --token-mode lemma
```

---

## 方法论

### 语料清洗

一份试卷 PDF 抽出的文本里混着大量非正文内容。**不做清洗的统计毫无意义**——
本项目参考的上游仓库最大的问题就是没剔除 `Directions` 指令行。

剔除的内容：`Directions` 指令块（共 3 行）、题型标题（`Section I` / `Part A` / `Text N`）、
题干、选项、中文解析、页码、盗版水印。

保留的判据：连续可用行切块，块长 ≥3 行且 ≥40 词。
2022 年那份 PDF 是「试卷 + 34 页中文解析」合订本，已在第 678 行截断。

### 词形还原

`was→be`、`children→child`、`better→well`、`making→make`（NLTK WordNet + POS 标注）。

**这一步有个容易踩的坑**：还原之后再去比对大纲词表，
意味着语料里根本不会以 `is`/`was`/`children` 这些表层形态去查表。
曾经有一个版本因为忽略这一点，误判「大纲词表缺 is/are/was，所以不是完整考纲」——
实际上那些词元表里全都有。详见
[词表修订说明](docs/methodology/wordlist-revision.md)。

### 词表必须独立于语料

**红线：不能把语料里挖出来的词补进词表来抬覆盖率。**
覆盖率只有在词表独立于语料时才有意义，否则等于把答案抄进考卷。

本项目用的 `data/kaoyan_syllabus_verified.txt`（5,501 条）只收**有外部依据**的补丁：
官方大纲的 `a/an` 词条，以及 5 个英美拼写变体（`program`/`center`/`analyze`/`realize`/`judgment`）。

### 口径差异与修订记录

整理成仓库时发现上游的清理逻辑被复制了 4 份且并不一致：
同一份 README 里并列的两个结论，其实建立在不同口径的语料上。

**本项目把管线统一为 `blocks`（清洗）+ `lemma`（计数）**，并把差异与全部数字更正
记录在案：[管线口径、修订记录与已知局限](docs/methodology/pipeline-and-corrections.md)。

其中最重要的一条更正：**4000 词汇量每篇生词从 34 个修正为 19 个**
（上游用表层形态计数，把 `was`/`is`/`been` 当成了 3 个独立生词）。
结论方向全部不变，但难度被上游高估了。

---

## 项目结构

```
src/npee_vocab/
├── corpus.py       语料加载与清洗（两条路径：blocks / flat）
├── lemmatize.py    词形还原（NLTK WordNet + POS）
├── wordlist.py     词表读取（编码自适应）+ 覆盖率口径
├── lexicon.py      全部人工归纳词表（功能词 / A 类分组 / 专名 / 派生词）
├── analysis.py     纯计算层：统计、分档、覆盖率曲线、A/B 检验
├── render.py       渲染层：markdown / json / 控制台
└── cli.py          命令行入口

data/               大纲词表（版本与依据见 data/README.md）
docs/               方法论与学习策略（手写）
reports/            管线产出（自动生成，勿手工编辑）
examples/           合成样例语料（可安全公开）
tests/              pytest 测试
scripts/            辅助脚本
```

**分层约定**：`analysis.py` 只吃数据吐数据结构，不 print、不写文件、不读命令行；
`render.py` 只做格式化。所以每个统计口径都能被单元测试直接断言，
不用去解析输出文本。

---

## 测试

```bash
pytest -q
```

测试**全部基于 `examples/sample_corpus/` 的合成语料**，不使用任何真题文本。
那份样例是刻意构造的：里面混着 Directions 指令行、题干、选项、水印和中文解析，
因此它同时是清洗逻辑的回归夹具。

CI 在 Linux 与 Windows 上跑 Python 3.10 / 3.12 / 3.13，
并有一道独立的检查确保 `raw/`、`pdfs/` 与 `.pdf` 永远不会被提交。

---

## 已知局限

1. **`blocks` 清洗偏保守**：段落中间夹一行水印会被切断，
   残块不足 3 行 / 40 词时整块丢弃。因此语料是**下界**。
   完整说明见[修订记录](docs/methodology/pipeline-and-corrections.md#blocks-自己的局限如实记录)。
2. **只统计正文，不含题干与选项**：题干词汇通常更简单，因此本报告偏保守。
3. **缩写会被切分**：`don't`→`don`+`t`。高频词表已剔除这些碎片。
4. **`numbered` 是残留**：来自 Directions 的 "numbered blank"，已单列进 T4 档。
5. **专名 / 派生词名单是人工归纳**：见 `src/npee_vocab/lexicon.py`，可能有遗漏。
6. **「文章」是机械切片**：每篇 400 词元是机械切的，不是真题真实的 Text 边界。
7. **没有做词性区分**：还原后 `work`（名词/动词）合并为一个词元。

欢迎提 issue 或 PR 补充。

---

## 授权

代码以 [MIT](LICENSE) 发布。仓库内第三方数据的权利归属与使用条件见 [NOTICE](NOTICE.md)。

**真题原文与抽取文本不在本仓库内。**

---

## English

**What this is.** A reproducible corpus-analysis pipeline for the vocabulary of China's
National Postgraduate Entrance Examination (NPEE) English (I) paper, built on the
prose of 25 past papers (2002–2026).

**Headline results.** Syllabus coverage is **76.8%** by distinct word form but
**88.2%** weighted by token — the latter is the number that matches how reading
actually feels. The 146 lemmas occurring 50+ times account for **51.6%** of all tokens,
while 47% of distinct forms occur exactly once and contribute just 5.3%.
Reaching the 98% coverage usually taken as the threshold for fluent reading requires
about **5,926 lemmas**, so finishing the official syllabus list is necessary but
not sufficient.

**The actionable split.** Vocabulary problems divide cleanly in two.
*Class A* — logical and abstract words (`however`, `therefore`, `assumption`, …) —
is a **closed set of 140 items**, about 6 per article, and can be mastered exhaustively.
*Class B* — the long tail — is 5,940 forms occurring ≤2 times, about 69 per article,
and cannot be memorised; the only lever is lowering the cost of each unknown word.

**Engineering notes.** The pipeline cleans exam-booklet noise (`Directions` blocks,
question stems, multiple-choice options, Chinese commentary, watermarks) before
counting, lemmatises with NLTK WordNet, and keeps the syllabus word list
**independent of the corpus** — back-filling words mined from the corpus would
trivially inflate coverage and destroy the measurement.

The original scripts disagreed with each other about both cleaning and tokenisation,
which made two published headline numbers non-comparable. This repository unifies the
pipeline and documents every resulting correction in
[docs/methodology/pipeline-and-corrections.md](docs/methodology/pipeline-and-corrections.md).

**Licensing.** Code is MIT. Exam papers are copyrighted and are **not** included;
`examples/sample_corpus/` contains synthetic text written for this repository.
See [NOTICE](NOTICE.md).
