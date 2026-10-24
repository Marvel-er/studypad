# CET-6 Vocabulary — 六级高频核心词汇表

> 基于 **2020-2025 年 35 套六级真题** 的词频统计分析 + AI 精炼，分级输出 Top100/300/500 高频核心词汇。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 项目简介

这个项目从 2020 年至 2025 年共 35 套大学英语六级（CET-6）考试真题中，提取全部英文文本，进行词频统计、词形还原（lemmatization）、基础词过滤、话题分类、中文释义匹配，最终产出多级词表。

**核心特点**：

- **数据驱动**：不是照搬任何现有词书，而是从真题中实打实统计
- **AI 精炼**：自动过滤初中/高中基础词（如 science、animal、university）、考试说明词（如 question、passage）、泛化词
- **分级输出**：Top100（考前3天冲刺）→ Top300（2周）→ Top500（1个月）
- **双格式**：每组都有「精炼版」（含词性/搭配/话题标签）和「简洁版」（纯表格速查）

---

## 文件说明

### 🟢 精炼版（实际背诵用）

| 文件 | 内容 | 适合场景 |
|------|------|----------|
| `cet6_emergency_words_top100_simple.md` | 100词纯表格 | 考前3天快速扫读 ⭐ |
| `cet6_emergency_words_top100_refined.md` | 100词分组精讲 | 考前3天深度学习 |
| `cet6_core_words_top300_simple.md` | 300词纯表格 | 快速查漏补缺 |
| `cet6_core_words_top300_refined.md` | 300词分15组 | 考前2周，每天40词 |
| `cet6_core_words_top500_simple.md` | 500词纯表格 | 想全面扫一遍用 |
| `cet6_core_words_top500_refined.md` | 500词分20组 | 考前1个月，每天25词 |
| `refined_vocab_summary.md` | 使用指南 | 了解各文件区别 |
| `refined_vocab_quality_check.md` | 质量检查报告 | 验证无基础词/考试词残留 |

### 🔴 原始数据

| 文件 | 内容 |
|------|------|
| `cet6_high_frequency_words.csv` | 完整 5,821 词数据表，含词频、年份分布、词性、中文释义，可用 Excel 打开 |

---

## 数据来源

- **真题文本**：来自 [AndrewYuZhenYu/cet6_exam_questions_txt_collection](https://github.com/AndrewYuZhenYu/cet6_exam_questions_txt_collection)（GitHub 开源仓库）
- **考试范围**：2020-2025 年 CET-6，共 35 套卷，覆盖 13 个考试月份
- **中文释义**：基于 AI 辅助整理

---

## 使用方法

### 只看不背（纯扫读）

打开任何一个 `_simple.md` 文件，直接在 GitHub 上浏览表格。

### 下载到本地

```bash
git clone https://github.com/wangjiuyi543-ui/cet6-vocabulary.git
```

用 Typora、VS Code 或任何 Markdown 阅读器打开 `.md` 文件。

### Excel 分析

用 Excel / WPS 打开 `cet6_high_frequency_words.csv`，可按年份分布、词性、话题标签筛选。

---

## 筛选逻辑

1. 从 35 套真题中提取全部英文文本
2. 词形还原（lemmatization）+ 词频统计
3. 排除 1,100+ 基础词（初中/高中已学）、考试说明词、泛化词
4. 对学术词、抽象词、写作高分词加权加分
5. 强制每个入选词匹配中文释义
6. 按话题（教育/科技/环境/经济/社会/心理/健康等）分组

> 详细说明见 `refined_vocab_summary.md`

---

## 局限性

- 不是官方 CET-6 大纲词表，是统计 + 筛选的结果
- 中文释义为 AI 辅助整理，部分词可能无释义或释义不够精确
- 听力原文缺失，听力场景词汇覆盖可能不足

---

## License

MIT — 随意使用、修改、分发，注明出处即可。
