# 词典数据来源与许可

生词表里的词条按下面的顺序查，**先命中的赢**。同一层里，直接命中（词本身有词条）
优先于靠词形还原猜出来的命中（`stolidity` 不能被 `stolid` 顶掉）。

| # | 层 | 文件 | 条数 | 来源 | 许可 |
|---|---|---|---|---|---|
| 1 | 六档考纲词表 | `data/wordlists/*.json` + `_index.json` | 13,354 词头 | KyleBing/english-vocabulary | MIT |
| 2 | 补充词典 | `data/dict/general.json` | 8,319 | 同上的完整词条 | MIT |
| 3 | 手写补充 | `data/dict/extra.json` | 49 | 本项目手写（见文件内 `_meta`） | 本项目 |
| 4 | ECDICT 精筛 | `data/dict/ecdict.json` | 8,673 | skywind3000/ECDICT | MIT |
| 5 | **全量兜底** | `data/dict/lexicon.sqlite` | **349,692** | ECDICT 全量 + CMUdict + Open English WordNet | 见下 |

第 5 层由 `scripts/build_lexicon.py` 生成，是这次为「生词表出现空白格」加的兜底层。
前四层都是**预先筛过的小子集**，第 4 层更是拿 BNC 排名当「太生僻没人查」的闸门，
于是文学/旧文本里最需要的词反被丢掉（`caisson` 在源数据里音标、中文释义俱全，
只因 `bnc=0` 就被筛了）。第 5 层改用全量。

## 第 5 层的三个数据源

| 数据 | 用途 | 许可 | 要求 |
|---|---|---|---|
| **ECDICT**（`vendor/ecdict/`） | 音标、中文释义、词性、词频排名、柯林斯星级 | MIT | 保留版权声明 |
| **CMUdict**（`pip install cmudict`，数据随包） | 补 ECDICT 没有的音标（126,052 词，ARPAbet 转 IPA） | BSD-2-Clause | 保留版权声明 |
| **Open English WordNet 2024**（`.cache/wn/oewn-2024.xml.gz`） | 英释、例句 | CC BY 4.0 | **署名** |

WordNet 那部分在数据文件里没有逐条署名，署名放在这里：

> Princeton WordNet / Open English WordNet (https://en-word.net/), CC BY 4.0.
> CMU Pronouncing Dictionary, Copyright (C) 1993-2015 Carnegie Mellon University, BSD-2-Clause.
> ECDICT (https://github.com/skywind3000/ECDICT), MIT.

## 关于柯林斯（Collins）

**本项目不包含柯林斯词典内容。** Collins COBUILD / Collins English Dictionary 是
HarperCollins 的商业版权产品，没有免费许可；网上流传的 MDX / StarDict / mobi 版本
均为未授权转载，引入即侵权，因此不下载、不打包。

需要区分的是 ECDICT 里的 `collins` 列：那是**柯林斯星级**（常用词的 1~5 星难度标记），
只有难度、没有释义，本项目把它存在 `lex.band` 字段里当难度标签用
（形如 `柯林斯5星`，另外还有 `牛津3000` 与考纲标签）。

## 关于数据准确性

- ECDICT 是对多个来源的**聚合**（含汉英/英汉词典、机器翻译成分），条目质量参差；
  它的 README 自己也说明了来源链不完整。本项目把它放在**最后一层**，
  只有前面四层全落空时才轮到它。
- WordNet 是英释与例句那一栏的来源，是学术界的标准英语词网，释义质量高于 ECDICT。
- CMUdict 是发音词典，只提供读音，不含释义。
- 三样都可能出错。**生词表里显示的音标/释义不是权威判据**，可疑时请以纸质词典为准。

### 已知的一个取舍：派生词按原形归并

生词表是**按原形去重**的（`convulsive` 与 `convulsion` 并成一行，用后者的词条解释前者），
这是本项目的既有设计：一个词族只占一行预算，免得「划满等于没划」。
副作用是**派生词显示的是原形的释义**，词性可能与文章里的词形不一致 ——
例如 `stolidity`（名词，迟钝）会显示 `stolid`（形容词，不易激动的）的释义。

试过让「词本身有词条就直接用它的」优先，`stolidity` 确实能拿到自己的词条，
但那会同时改掉「档位 → 补充词典」的优先级（`convulsive` 会从 cet4 档的 `convulsion`
变成 general 里它自己那条），影响全站每个派生词的解析结果，风险大于收益，
所以维持原形归并。真要逐词准确，得给 `build_vocab` 的去重键单独做一版设计。

## 音标：为什么有的词「看着少了一截」

音标列的语义是「**显示出来的这个词**怎么读」，但词条是按**原形归并**的 ——
`flapping` 的词条来自 `flap`（释义「拍打」没错），音标若跟着用 `flæp`，读起来就像 -ing 被吞了。
实测那篇手账 85 行里 **36 行**是这么来的（`beads` → `bid`、`dragged` → `dræg`、
`shutters` → `'ʃʌtɚ` …），另有源数据本身残缺的（`oath` → `oθ`，整个 əʊ 没了；
`diabolical` → `/'daiə'bɔlik / -kəl/`，一格里塞了两套读音）。

现在音标统一由**发音词典**供给，数据在 `lexicon.sqlite` 的 `pron` 表（275,185 条）：

| 来源 | 条数 | 说明 |
|---|---|---|
| CMUdict（ARPAbet→IPA） | 125,923 | 主源。按**词形**收录，含 `beads`/`dragged`/`flapping` 这类屈折形 |
| ECDICT 音标（归一化后兜底） | 149,262 | CMUdict 没有的词形才用；先把多套读音、可选读法、`ˈ/ˌ`、`:` 归一 |

查询顺序（`wordlist.pronunciation`）：**词形本身** → 连字符词**去掉连字符**再查
（`arm-chairs` ↔ `armchairs`，实测多救回 3,751 个词，`arm-chairs` 的复数 /z/ 就是这么来的）
→ 都不中才**沿候选表找第一个有读音的词形**（`tradesman's` → tradesman、`cabmen` → cabman）。

**不做后缀合成**：试过「词干音标 + 后缀音素」合成，并用发音词典做留出验证，
命中率只有 `'s` 93.4% / `s` 62.3% / `ing` 51.5% / `ed` 47.7% / `ly` 2.6% ——
反例多是「词干选错 + 两套记法混在一起」，错得没规律。宁可显示**真值**（哪怕那是原形的），
也不给拼出来的假值。**残留**（4 篇 274 行里 4 行 = 1.5%）：双重屈折（`hootings`）、
组合词的所有格（`tradesman's`）、源数据本身有误（`fakirs`）。

顺带修的一处词形还原缺口：**不规则复数 `-men` → `-man`**（`cabmen` → `cabman`，
两者同音）—— 原来候选表里只有 `cabmen` 自己，而 ECDICT 那一行没给音标，音标列就是空的。

## 重建

```bash
# 只用本地数据（ECDICT + CMUdict，不需要联网）
python scripts/build_lexicon.py --no-wordnet

# 带上 WordNet（需要先下 .cache/wn/oewn-2024.xml.gz，约 13 MB）
mkdir -p .cache/wn
curl -L -o .cache/wn/oewn-2024.xml.gz \
     https://en-word.net/static/english-wordnet-2024.xml.gz
python scripts/build_lexicon.py

# 建完把已有手账按新词典重标一遍（不重翻、不重花 token）
python scripts/repair_library_annotations.py
```

> ⚠ **重建前先停掉 StudyPad 服务**，建完再重启。
> Windows 上 SQLite 连接会按住库文件，`build_lexicon.py` 重命名替换时会拿到
> `PermissionError [WinError 32]`；脚本第 1 步就是探这个，看到「库文件被占用」就是服务还在跑。
> 反过来，建完不重启服务也一样看不到新数据 —— 库连接是**按线程缓存**在进程里的，
> 不会自动切到新文件（症状是「库明明更新了，页面还是旧的」）。

> ⚠ WordNet 那个 gz **必须从单一来源一次下完**。本机实测：从 `en-word.net` 下到 733 KB
> 断流，改用 `-C -` 从 GitHub 代理（`gh-proxy.org`）续传，拼出来的文件 CRC 校验失败
> （`invalid compressed data--crc error`）—— 两个源的分段字节流不能拼接。
> 断流就删掉重下。
