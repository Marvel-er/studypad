# 大纲词表修订说明

> 日期：2026-10-01 ｜ 目的：解决「5495 大纲词汇表不可靠导致覆盖率结论作废」这一历史遗留问题
> 结论：**原判定是误判；覆盖率结论已恢复，并换用经复核的词表**

---

## 一、结论摘要

| 项目 | 2026-09-26 的判定 | 2026-10-01 复核结论 |
|---|---|---|
| 覆盖率数字是否可用 | ❌ 作废 | ✅ **有效，已恢复** |
| 旧词表是否"不是完整考纲" | ❌ 是 | ⚠️ **判断依据不成立**；旧表其实是正常的考纲词表 |
| 是否需要换词表 | — | ✅ 已换，但**不是因为旧表坏**，而是为了补齐 6 个真实缺口 |

**恢复后的结果**：不同词口径 **76.8%**，次数口径 **88.2%**（原为 76.5% / 87.8%）。

---

## 二、误判是怎么发生的（关键）

2026-09-26 的作废理由是：**词表缺 `is`、`are`、`was`、`were`、`had`、`does`、`did`、`children`、`an`、`been`**，
并由此推断"没有真实考纲会缺这些词，所以这表不是考纲"。

**这个检验口径是错的。** 原因：

`vocab_stats.py` 的比对发生在 **词形还原（lemmatization）之后**：

```python
# vocab_stats.py: lemmatize()
out.append(wnl.lemmatize(w.lower(), p if p in "nvar" else "n"))
```

实测还原效果：

```
was      -> be
children -> child
had      -> have
does     -> do
```

也就是说，**语料里根本不会出现 `is`/`was`/`children` 这些形态**，比对时问的是
"`be` 在词表里吗？""`child` 在词表里吗？"——而这些词元**旧表全都有**：

| 词元 | 旧表 | 新表 NPEE |
|---|---|---|
| `be` | ✓ | ✓ |
| `have` | ✓ | ✓ |
| `do` | ✓ | ✓ |
| `child` | ✓ | ✓ |

**用一个 pipeline 永远不会去查的表层形态，去判定词表"缺词"，必然得出错误结论。**

---

## 三、候选词表评估（可复现）

复核引入了第二份真实考纲词表作交叉验证：

- **旧表**：`5495大纲词汇.txt`（原用，gb18030，5,491 条）
- **新表**：`NPEE_Wordlist.txt` — 来源 [mahavivo/english-wordlists](https://github.com/mahavivo/english-wordlists)
  （NPEE = National Postgraduate Entrance Examination，即考研；5,391 条，utf-8）
  下载走 jsDelivr（本机 GitHub 直连不通）：
  `https://cdn.jsdelivr.net/gh/mahavivo/english-wordlists@master/NPEE_Wordlist.txt`
  文件大小 300,430 B，与 GitHub API 报告值一致；SHA256 已校验。

**用同一份语料（25 套真题，63,174 token，7,189 个词元）评测：**

| 词表 | 条目 | covA 不同词口径 | covB 加权口径 |
|---|---|---|---|
| 旧表 5495大纲词汇 | 5,491 | **76.5%** | **87.8%** |
| 新表 NPEE_Wordlist | 5,391 | 75.4% | 87.0% |
| 两表并集 | 5,495 | 76.5% | 87.8% |
| 并集 + 补 `an` | 5,496 | 76.6% | 88.1% |
| **并集 + `an` + 5 个英美变体（最终采用）** | **5,501** | **76.8%** | **88.2%** |

**关键发现：旧表反而比新表更完整。**
- 仅旧表独有：**104 个真词**（`use`、`useful`、`usually`、`urban`、`value`、`vague`…）
- 仅新表独有：**4 个**（`abatement`、`acceptable`、`according`、`coordinates`）
- 新表独缺的高频词：`use`(136 次)、`very`(49)、`view`(35)、`value`(31)

**所以"直接换成另一份真考纲"会让覆盖率下降**，不是正确的修法。

---

## 四、剩余缺口的成因分解

旧表∪新表仍缺 3,583 个词元（占 12.2% 词次）。逐项分解：

| 成因 | 词元数 | 词次 | 占词次 | 词表能修吗 |
|---|---|---|---|---|
| 专有名词 / 品牌（AI、UK、GDP、Google…） | 883 | 2,011 | **3.18%** | ❌ 大纲本就不收 |
| 派生词（consumer←consume、researcher←research） | 674 | 1,729 | **2.74%** | ❌ 大纲要求靠构词法识别 |
| 屈折变形残留（还原器未归并） | 253 | 457 | 0.72% | ❌ 非词表问题 |
| 缩写切分残留（don't→don+t） | 19 | 298 | 0.47% | ❌ 语料噪声 |
| **其余真未收录** | 1,754 | 3,233 | **5.12%** | ⚠️ 以低频词为主 |

**约 7.1% 的缺口在结构上就不是词表能覆盖的**（专名 + 构词法 + 还原/切分噪声）。

> ⚠️ **方法论红线：不能把语料里挖出来的词补进词表来抬覆盖率。**
> 覆盖率只有在词表**独立于语料**时才有意义；把上面那 3,233 个词补进去，
> 只是把答案抄进考卷。本轮补丁只收**有外部依据**的词。

---

## 五、最终词表构成

文件：`data/kaoyan_syllabus_verified.txt`（5,501 条，utf-8，制表符分隔）

| 来源 | 条目数 | 说明 |
|---|---|---|
| 旧表 `5495大纲词汇.txt` | 5,490 | 原表主体，gb18030 |
| 新表 `NPEE_Wordlist.txt` 独有部分 | +5 | 交叉验证中确认旧表缺失的 |
| **手工补丁** | **+6** | 见下表 |
| **合计** | **5,501** | |

### 6 个补丁及其依据

| 补丁 | 依据 |
|---|---|
| `an` | 大纲将「a/an」列为同一词条，旧表只收了 `a`。语料中 `an` 出现 **233 次**，是最大的单个真实缺口（补后 covB 87.8%→88.1%） |
| `program` ← `programme` | 旧表为英式拼写，真题语料为美式。语料 33 次 |
| `center` ← `centre` | 同上，语料 11 次 |
| `analyze` ← `analyse` | 同上，语料 9 次 |
| `realize` ← `realise` | 同上，语料 9 次 |
| `judgment` ← `judgement` | 同上，语料 8 次 |

释义沿用英式对应词条，并标注 `(美式拼写=xxx)`。

---

## 六、覆盖率结果

**当前（verified 词表）**：不同词口径 **76.8%**，次数口径 **88.2%**

逐年（次数口径）：2002 92.1% → 2021 85.2% → 2026 87.3%
- 前 5 年 2002–2006：78.3% / 88.8%
- 后 5 年 2022–2026：75.7% / 87.5%

> 注意：**次数口径（88.2%）才是贴近实感的那个**——它问的是"你实际读到的词次里，
> 有多少在大纲内"。出现次数最多的那批词（the/of/and/be…）几乎全在大纲内。
> 真正"超纲"的是偶尔露面的低频词，这也是为什么不同词口径只有 76.8%。

---

## 七、代码改动

上游 `vocab_stats.py` 做了 3 处改动（都已实测无偏差），本仓库把这三点固化为默认行为：

1. **默认词表**是 `data/kaoyan_syllabus_verified.txt`
2. **`--wordlist PATH`** —— 便于换表对比并留痕：
   ```bash
   python -m npee_vocab stats --wordlist 某个词表.txt
   ```
3. **编码自适应读取**（`wordlist.read_any()`）—— 先 utf-8 后 gb18030，新旧表都能读

**回归验证**：用旧表跑，精确复现 76.5% / 87.8%，证明改造未引入偏差。

---

## 八、如何复现

```bash
# 前置：自备真题 PDF 放在 pdfs/ 下
python -m npee_vocab extract --pdf-dir pdfs --corpus-dir raw

# 1. 用旧表复现历史数字（应得 76.5% / 87.8%）
python -m npee_vocab stats --wordlist 旧表路径/5495大纲词汇.txt --output-dir /tmp/old

# 2. 用 NPEE 新表（应得 75.4% / 87.0%）
python scripts/fetch_npee_wordlist.py -o /tmp/NPEE_Wordlist.txt
python -m npee_vocab stats --wordlist /tmp/NPEE_Wordlist.txt --output-dir /tmp/npee

# 3. 正式结果（verified 词表，默认）
python -m npee_vocab all
```

> 词表替换的**评测口径是 `blocks` + `lemma`**（63,174 词元 / 7,189 个词元）。
> 换成 surface 口径会得到完全不同的覆盖率数字，那是口径差异而非词表差异。
> 见 `pipeline-and-corrections.md`。

---

## 九、文件清单

| 位置 | 说明 |
|---|---|
| `data/kaoyan_syllabus_verified.txt` | **当前使用的词表**（5,501 条） |
| `docs/methodology/wordlist-revision.md` | 本文件 |
| `scripts/fetch_npee_wordlist.py` | 拉取交叉验证用的第二份词表（含 SHA256 校验） |
| `reports/stats.json` | 已按新词表重算 |
| `reports/高频内容词表.md` | 已按新词表重算（「大纲内」列现已可信） |
| `reports/统计报告.md` | 第六、七节已按新数据重算 |

> **未随仓库分发**：旧表 `5495大纲词汇.txt`（gb18030）与 `NPEE_Wordlist.txt`
> 均属第三方词表，仓库只带最终合并结果与拉取脚本。想复现第一、二节的历史数字，
> 需自备旧表——它也是本项目引用的
> [YSMull/words-statistics](https://github.com/YSMull/words-statistics) 所用词表。
