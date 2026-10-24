# CET-6 精炼版词表最终质量检查报告

> 检查日期：2026-06-03 | 自动化审查

---

## 一、检查了哪些文件

| 文件 | 检查结果 |
|------|----------|
| `cet6_emergency_words_top100_refined.md` | ✅ 通过 |
| `cet6_emergency_words_top100_simple.md` | ✅ 通过 |
| `cet6_core_words_top300_refined.md` | ✅ 通过 |
| `cet6_core_words_top300_simple.md` | ✅ 通过 |
| `cet6_core_words_top500_refined.md` | ✅ 通过 |
| `cet6_core_words_top500_simple.md` | ✅ 通过 |

---

## 二、删除或降权的词

### 已从 Top100 排除的基础词

| 被排除的词 | 原因 |
|-----------|------|
| science | 初中词 |
| animal | 初中词 |
| university | 高中词 |
| information | 高中词 |
| work, human, change, long, real | 基础词 |
| careful, example, learn, study | 初中/高中词 |
| author, music, computer, company | 基础词 |
| health, job, student, school | 过于基础 |
| scientist, activity, difference, knowledge | 基础词 |
| social, public, personal, natural | 过于泛化 |
| state, actual, base | 泛化+考试说明 |

### 已从 Top300 降权的词

部分高频但偏基础的词降到了 Top500 后段或排除（如 economy, culture, industry, career, college, music 等）。

---

## 三、各项检查结果

| 检查项 | 结果 |
|--------|------|
| 人名 | ✅ 无 |
| 地名 | ✅ 无 |
| 国家名 | ✅ 无 |
| 机构名 | ✅ 无 |
| 月份/星期 | ✅ 无 |
| 考试说明词 | ✅ 无（question/passage/answer/base/conclusion 等全部过滤） |
| 乱码 | ✅ 无 |
| 拼写异常 | ✅ 无 |
| 重复单词 | ✅ 无（按 lemma 去重） |
| Top100 中文释义覆盖率 | ✅ 100/100 |
| Top100 词性覆盖率 | ✅ 100/100 |
| 简洁版三列格式 | ✅ 序号/英文/中文意思 |
| refined 版分组格式 | ✅ 紧凑6列表格 |

---

## 四、Top100 概况

- **分组**：4组 × 25词，方便每天背一组
- **跨年覆盖**：平均 5.6 年，92% 跨 5 年以上
- **主题分布**：通用 48、社会 11、环境 8、科研 6、经济 5、科技 5、心理 4、教育 3、工作 3、文化 3、健康 2

---

## 五、剩余问题

1. **Top300 中约 40% 词暂无中文释义**：主要是频次相对较低的词。Top100 已全覆盖，不影响核心使用。
2. **「常见搭配」覆盖约 15%**：后续可继续补充。

---

## 六、最终建议

- **考前 3 天冲刺** → `cet6_emergency_words_top100_simple.md`（纯表格，一页扫完）
- **考前 2 周** → `cet6_core_words_top300_refined.md`（每天2组=40词）
- **考前 1 个月** → `cet6_core_words_top500_refined.md`（每天1组=25词）
- **只想看中文** → 所有 `_simple.md` 文件

> ⚠️ 这个词表不能替代做真题。背完词后务必配合 2020-2025 年六级真题练习。
