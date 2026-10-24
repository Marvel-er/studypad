# 数据目录

## `kaoyan_syllabus_verified.txt`

考研英语（一）大纲词汇表，**5,501 条**，utf-8，制表符分隔：

```
abandon	vt.离弃，丢弃；遗弃，抛弃；放弃
abatement	n.减(免)税,打折扣,冲销
```

SHA256：`7F4CE175B3C1DC796D717A800E9AF630BF105621A03E3C4B4410157619367901`

### 它是怎么来的

| 来源 | 条目数 |
|---|---|
| 旧表（gb18030，流传较广的考纲词表整理） | 5,490 |
| NPEE 词表独有部分（交叉验证确认旧表缺失的） | +5 |
| 手工补丁 | +6 |
| **合计** | **5,501** |

6 条补丁及其依据：

| 补丁 | 依据 |
|---|---|
| `an` | 大纲把「a/an」列为同一词条，旧表只收 `a`。语料中 `an` 出现 233 次 |
| `program` ← `programme` | 旧表是英式拼写，语料是美式。33 次 |
| `center` ← `centre` | 11 次 |
| `analyze` ← `analyse` | 9 次 |
| `realize` ← `realise` | 9 次 |
| `judgment` ← `judgement` | 8 次 |

完整论证见 [`docs/methodology/wordlist-revision.md`](../docs/methodology/wordlist-revision.md)。

### ⚠️ 方法论红线

**不允许把语料里挖出来的词补进这份词表来抬高覆盖率。**

覆盖率只有在词表**独立于语料**时才有意义。把从真题里挖出来的 3,233 个词补进去，
覆盖率会立刻升到很高——但那等于把答案抄进考卷，统计就失去了全部意义。

上面 6 条补丁只收**有外部依据**的词（官方大纲的 a/an 词条、英美拼写变体），
不是从语料里反向补的。

### 想换一份词表对比

```bash
python -m npee_vocab stats --wordlist 你的词表.txt --output-dir /tmp/mine
```

脚本支持两种格式：`词<TAB>释义`，以及纯词表（每行一词，可带音标）。

---

## 关于真题语料

**本目录不含真题语料。** 真题原文与抽取文本不进仓库（版权原因，见 [`NOTICE.md`](../NOTICE.md)）。

想自己跑全量统计：

```bash
# 1. 把你的真题 PDF 放进 pdfs/
# 2. 抽取文本
python -m npee_vocab extract --pdf-dir pdfs --corpus-dir raw
# 3. 跑统计
python -m npee_vocab all
```

只想看看管线长什么样，用合成样例：

```bash
python -m npee_vocab all --corpus-dir examples/sample_corpus --output-dir /tmp/demo
```
