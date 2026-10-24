# 本地翻译模型选型与接入（Hy-MT2-1.8B）

> 结论：**`tencent/Hy-MT2-1.8B`（官方 GGUF Q4_K_M，Apache-2.0）** —— 已装好并跑通本项目全链路。
> 版本：v1.0 ｜ 2026-10-15 ｜ 实测机型：RTX 4060 Laptop 8GB

---

## 一、为什么是它

本项目的翻译链路有三个硬约束（见 `backend/app/translate.py` 文件头）：

1. **必须走大模型，无规则兜底** —— 词对词拼接的假译文比不翻更糟；
2. **必须能返回「条数与输入严格相等」的 JSON** —— `_translate_batch` 对每批做条数硬校验，
   对不上就重试、二分，最终宁可整块放弃也不猜（`AlignmentError`）；
3. **一次请求要塞进 8 句 / 800 字符**（`BATCH_SENTENCES` / `BATCH_CHARS`），并且要能并发 4 路。

这三个约束直接决定了选型：

| 候选类别 | 代表 | 能否零改动接入 | 结论 |
|---|---|---|---|
| **指令型翻译 LLM** | **tencent/Hy-MT2-1.8B** | ✅ 能：说人话、能照 JSON 契约输出 | **采用** |
| 通用指令 LLM | Qwen3-4B 等 | ✅ 能 | 质量不一定更好，且体积更大 |
| 专用 NMT 小模型 | Helsinki-NLP/opus-mt-en-zh（77M） | ❌ 不能：只会输出纯译文，**不会输出 `{"t":[...]}`**，必须改 `translate.py` 新增一条非 chat 通道 | 备选，需改代码 |
| 多语 NMT 大模型 | facebook/nllb-200-distilled-600M | ❌ 不能（同上），且许可 **cc-by-nc-4.0 禁商用** | 排除 |

选 Hy-MT2-1.8B 的四个理由：

- **许可干净**：Apache-2.0。本项目明确排除 GPL/AGPL 传染性许可（见 `docs/开源复用方案.md`），
  同时也排除了 NLLB / Tower 这类 `cc-by-nc`（禁商用）。Hy-MT2 全系（1.8B/7B/30B-A3B）都是 Apache-2.0。
- **体积与显存刚好**：Q4_K_M 1.08GB，实测常驻显存 **≈1.8 GB / 8 GB**，留给并发和系统绰绰有余。
- **中英双语在支持列表里**（官方支持 33 语，含 zh / en / zh-Hant / yue）。
- **官方专门为「翻译指令跟随」做了训练和评测**（同仓库开源了 IFMTBench），
  这正是本项目要的能力——照自定义 system prompt 的 JSON 契约输出。

体积/性能对照（本项目真实负载，见第四节）：

| 模型 | 磁盘 | 显存 | 许可 | 备注 |
|---|---|---|---|---|
| **Hy-MT2-1.8B Q4_K_M** | **1.08 GB** | **1.8 GB** | **Apache-2.0** | ✅ 已采用 |
| Hy-MT2-7B Q4 | ≈4.7 GB | ≈5.5 GB | Apache-2.0 | 8GB 显存可跑但并发会紧张，质量更高 |
| Hy-MT2-30B-A3B | ≈18 GB | 装不下 | Apache-2.0 | 排除（本机跑不动） |

---

## 二、已经装好了什么（无需再动手）

| 项 | 值 |
|---|---|
| 模型名 | **`hy-mt2:1.8b`** |
| 运行时 | 你已装的 Ollama（`0.32.15`，服务端口 `11434`） |
| 模型库位置 | **`F:\ollama_models`**（Ollama 现在的默认库，不在 C 盘） |
| 官方源文件 | `tencent/Hy-MT2-1.8B-GGUF` 的 `Hy-MT2-1.8B-Q4_K_M.gguf`，sha256 已核对 |
| 本地留存 | `F:\models\hy-mt2\ok\Hy-MT2-1.8B-Q4_K_M.gguf`（备份，1.06GB，可删） |
| 端点 | `http://localhost:11434/v1`（OpenAI 兼容，**不需要 API Key**） |

装它的命令（已执行，此处留档）：

```bash
# 1) 从镜像下载官方 GGUF（huggingface.co 本机直连不通，走 hf-mirror）
export HF_ENDPOINT=https://hf-mirror.com
hf download tencent/Hy-MT2-1.8B-GGUF Hy-MT2-1.8B-Q4_K_M.gguf --local-dir F:/models/hy-mt2/ok

# 2) 建 Ollama 模型（Modelfile 见 F:\models\hy-mt2\Modelfile.final）
ollama create hy-mt2:1.8b -f F:/models/hy-mt2/Modelfile.final

# 3) 冒烟测试
curl -s http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model":"hy-mt2:1.8b",
  "messages":[{"role":"user","content":"将以下文本翻译为中文，注意只需要输出翻译后的结果，不要额外解释：\n\nToday the weather is lovely."}],
  "max_tokens":100}'
```

### ⚠ 踩过的坑（改动前必读）

Hy-MT2 的对话模板是 **Jinja 写法**（官方 `chat_template.jinja`），
但 **Ollama 的 `TEMPLATE` 只吃 Go template 语法**：把 Jinja 原样贴进 Modelfile 会直接
报 `function "system_message" not defined` 建不出来。
而且从 GGUF 直接 `ollama create` 时，Ollama 不会自动采用 GGUF 里的 Jinja 模板
（`ollama show --modelfile` 显示 `TEMPLATE {{ .Prompt }}`），
**症状是模型原样把英文抄回来、不翻译**——很像「模型不支持中文」，其实是模板没生效。

正确做法：用等价的 Go template 显式指定（已固化在 `Modelfile.final` 里）：

```
TEMPLATE """{{- $bos := "<｜hy_begin▁of▁sentence｜>" -}}{{- if eq (index .Messages 0).Role "system" -}}{{ $bos }}{{ (index .Messages 0).Content }}<｜hy_place▁holder▁no▁3｜>{{- range $i, $m := .Messages -}}{{- if gt $i 0 -}}{{- if eq $m.Role "user" -}}<｜hy_User｜>{{ $m.Content }}{{- else if eq $m.Role "assistant" -}}<｜hy_Assistant｜>{{ $m.Content }}<｜hy_place▁holder▁no▁2｜>{{- end -}}{{- end -}}{{- end -}}{{- else -}}{{ $bos }}{{- range $m := .Messages -}}{{- if eq $m.Role "user" -}}<｜hy_User｜>{{ $m.Content }}{{- else if eq $m.Role "assistant" -}}<｜hy_Assistant｜>{{ $m.Content }}<｜hy_place▁holder▁no▁2｜>{{- end -}}{{- end -}}{{- end -}}<｜hy_Assistant｜>"""
PARAMETER stop "<｜hy_place▁holder▁no▁2｜>"
```

---

## 三、接入方式：翻译与讲解分离（已完成改造）

2026-10-15 起，本项目把**翻译**与**手账内容生成**拆成两套独立模型配置：

| | 干什么 | 配置键 | 默认 |
|---|---|---|---|
| **大模型** | 重写语法讲解、生成考点 brief | `provider` / `base_url` / `model` / `api_key` / `enabled` | 云端 API（DeepSeek 等） |
| **翻译模型** | 只做中英翻译 | `mt_provider` / `mt_base_url` / `mt_model` / `mt_api_key` / `mt_enabled` / `mt_fallback` | 本机 Ollama 的 `hy-mt2:1.8b` |

### 界面怎么用（默认已可用，不用配）

打开「中文译文」面板 → 展开「翻译模型设置」：

1. **翻译服务** 选「本地翻译模型（Hy-MT2-1.8B）」
2. **模型名** `hy-mt2:1.8b`，**Base URL** `http://localhost:11434/v1`，**Key 不用填**
3. 点「测试翻译模型」→ 通了就自动保存
4. 想换更高文风：把「翻译服务」切到「Hy-MT2-7B」（需先 `ollama pull` 7B 版），下拉会**自动填好** Base URL 与模型名

两个开关：

- **翻译交给这个模型**（默认开）：关掉 → 退回用大模型翻译（并在译文说明里写明本次消耗主模型额度）
- **它连不上时自动退回大模型翻译**（默认开）：不勾 → 宁可这一篇不出译文，也不偷偷花额度

### 改动的文件与「为什么」

| 文件 | 改了什么 | 关键理由 |
|---|---|---|
| `backend/app/settings.py` | 新增 `mt_*` 六个键；`_truthy()` 统一解析真假 | form 表单传的是字符串，`bool("false")` 是 **True** —— 不修的话「关掉本地翻译」勾选状态和服务端理解会相反 |
| `backend/app/llm.py` | 新增 `MT_PRESETS` / `MT_DEFAULT` | 两套预设不可互换：把手账讲解填成 1.8B 会得到满篇机翻味讲解，把翻译填成 deepseek 则本次优化白做 |
| `backend/app/main.py` | 新增 `_is_local` / `_resolve_mt_cfg` / `_translation_cfg` / `_autosave_mt_cfg`；`/api/llm/config`、`/api/llm/presets`、`/api/llm/test`、`/api/translate/status`、两个 analyze 接口全部区分两套模型 | 见下三条「踩过的坑」 |
| `backend/app/progress.py` | `plan()` 新增 `translate_local`，本地翻译阶段权重 35 → 10，等待文案改写 | 权重是「预期耗时占比」：本地 3.3 秒翻完还按 35 算，进度条会在最后一段凭空慢下来，看着像卡住 |
| `backend/app/translate.py` | 未改代码，但语义变了：它现在只被 `mt_cfg` 调用 | 翻译链路本身是对的，问题只在于「拿谁的配置调它」 |
| `backend/static/index.html` | 新增「翻译模型设置」区块 + 独立测试按钮 + 独立开关 | 与后端一样，两套配置互不干扰 |

### ⚠ 这次踩到的三个坑（改动前必读）

1. **`_autosave_cfg` 的守卫会吃掉「只翻译不讲解」的配置。**
   原逻辑是「调通了云端才落盘」，而翻译默认走本机、**根本不需要云端 Key** ——
   于是用户填完翻译模型、下次打开又变回默认，且**完全不报错**。
   修法：新增 `_autosave_mt_cfg`，翻译配置独立回写，不受云端守卫约束。

2. **`/api/llm/test` 的翻译分支读错了字段名。**
   前端发的是 `mt_base_url`，后端读的是 `base_url` → 用户填了个错的翻译端点去点测试，
   后端拿「已保存的默认端点」测出「连接成功」。**这个按钮永远说通，比不提供更糟。**
   修法：翻译分支优先读 `mt_` 前缀，同时容忍无前缀写法（手写 curl / 自检脚本更顺手）。

3. **不能只靠 `cfg.ready` 判断本地模型可用。**
   `ready` 对 localhost 一律放行（本机端点不需要 Key），
   所以 **Ollama 没启动时它照样「就绪」**：整篇翻译会按 4 路并发发出去、各自等到 90 秒超时，
   用户看到的是「卡两分钟然后没有译文」。
   修法：翻译前用 `llm.test_connection` 做一次 1 token 探活（本机约几十毫秒），
   失败则按 `mt_fallback` 决定退回大模型还是如实报不可用。
   探活只做一次：`_begin_job` 排进度计划与 `_run_pipeline` 共用同一份解析结果。

### 手账返回里的机器可读字段

| 字段 | 含义 |
|---|---|
| `llm_model` | 本次真正干了讲解的模型（未启用/失败时为空串） |
| `mt_model` | 本次真正干了翻译的模型（如 `mt_local / hy-mt2:1.8b`） |
| `trans_note` | 人看的说明：译文段数、复用缓存数、**以及换过模型/不可用的原因** |

自检与前端据此断言「翻译确实没走云端」，不必去解析中文文案。

---

## 四、界面验证与接口实测

### 已验证（真实 HTTP 服务，非直接调函数）

| 场景 | 期望 | 实测 |
|---|---|---|
| 清空所有配置（全新用户）后生成 | 仍要出译文 | ✅ 11/11 段、23 句，`mt_model = mt_local / hy-mt2:1.8b`，`llm_model = ''` |
| 云端 Key 有效、本地翻译可用 | 讲解走云端、翻译走本地 | ✅ 两者各归各位 |
| **云端 Key 是假的** | 讲解失败降级，**译文照样有** | ✅ `llm_note` 报 HTTP 401 降级为纯规则标注，译文 11/11 段 |
| 翻译模型配置保存后再读 | 两套配置互不覆盖；空 Key 不清空已存 Key | ✅ |
| 翻译端点填成死端口 + 点测试 | 必须如实报失败 | ✅ `ok:false`、`[WinError 10061] 目标计算机积极拒绝` |
| 关掉「翻译交给这个模型」 | 退回大模型并写明 | ✅ `mt_model = deepseek / deepseek-chat`，说明写明本次消耗主模型额度 |
| 前端内联 JS（`scripts/check_inline_js.py`） | 语法 + id/class 全命中 | ✅ 结果：全部通过 |

> 未做：浏览器里手动点一遍。本机 Chromium 未安装（`npx playwright install chromium` 可补），
> 因此界面部分是靠项目自带的检查器（语法 + id 交叉校验 + class 交叉校验）保证的。

### 翻译这一段的 token 用量（= 从云端省下来的量）

`STUDYPAD_LLM_DEBUG=1` 跑一遍 23 句 / 2357 字符的文章（4 个批次）：

```
[llm] hy-mt2:1.8b  prompt=339  completion=28
[llm] hy-mt2:1.8b  prompt=456  completion=143
[llm] hy-mt2:1.8b  prompt=465  completion=133
[llm] hy-mt2:1.8b  prompt=449  completion=105
合计 prompt 1709 + completion 409 = 2118 tokens
```

即：**这一篇原本要发给云端的 ~2.1k tokens 现在全部由本机承担**，耗时 3.3 秒。
规模随原文线性增长：11.5k 字符的长文（103 句）约 7k tokens、本地 15.5 秒。
（缓存按句命中，同一篇换等级重标不会重复翻译，所以实际节省按「新文章」计。）

---

## 五、实测数据（走本项目真实链路，非模拟）

用 `samples/sample_article.md`（23 句 / 2357 字符）与 `samples/long_article.md`（43 段 / 103 句 / 11512 字符），
调用 `backend/app/translate.py::translate_blocks`，`TRANSLATE_WORKERS=4`：

| 语料 | 耗时 | 段落成功率 | 对齐失败 | 截断 | partial | 速度 |
|---|---|---|---|---|---|---|
| sample_article（23 句） | **3.3 s** | **11/11** | 0 | 否 | 0 | — |
| long_article（103 句） | **15.5 s** | **43/43** | 0 | 否 | 0 | 745 字符/秒 |

- 生成速度：**≈140 tokens/s**（8GB 4060，Q4_K_M）
- 常驻显存：**≈1807 MiB / 8188 MiB**
- 首字延迟：冷启动首次请求要加载模型（约 2 s），之后按 Ollama 的 keep-alive 常驻

### 质量对照（本地 vs `samples/translations_zh.json` 里的参考译文）

| 原文 | 本地 Hy-MT2-1.8B | 参考译文 |
|---|---|---|
| Not until the pandemic had forced millions of employees out of their offices did companies discover… | 直到疫情迫使数百万员工离开办公室后，企业才意识到他们的成功在很大程度上依赖于在走廊和厨房中一直进行的非正式交流。 | 直到疫情把数百万员工赶出办公室，企业才发现：自己的成功有多大程度依赖那些一直发生在走廊和茶水间里的非正式交流。 |
| Organizations that strip away every unnecessary interaction… | 那些剔除所有不必要的互动的组织往往也失去了创新所需的交流方式。 | 那些把所有「不必要」互动都砍掉的组织常常发现，被一并砍掉的，正是创新赖以产生的那些交流。 |
| What matters most is not the speed of a process… | 最重要的不是流程的速度，而是其周围联系的密度。 | 真正重要的不是流程跑得多快，而是它周围连接的密度。 |
| Why Efficiency Is Not Enough（小标题） | 效率远远不够 | 为什么效率还不够 |

**评价**：意思准确、中文通顺、断句与条目一一对齐（硬校验全部通过，23/23 句无缺口）；
**比参考译文更「平」一点** —— 参考译文有更强的中文再组织（如「赖以产生」「事后补丁」），
本地模型偏直译，标题的问句语气偶尔会被抹平成陈述。

### 全篇逐句复核后发现的一类具体缺陷：抽象名词会掉进同一个泛词

23 句全量对照里，句子结构、时态、语态都没翻错，**唯一反复出问题的是抽象名词**：

| 原文 | 本地 | 参考 | 问题 |
|---|---|---|---|
| …by the negotiation of new **limits** | …由新**规则**的协商定义 | …就新的**边界**展开的协商 | limits → 规则（应为「边界」） |
| deciding who gets to set its **objectives** | 由谁来设定其**规则** | 由谁来设定它的**目标** | objectives → 规则（应为「目标」） |
| invest in prevention rather than **remediation** | 而非**修复已存在的问题** | 而不是**补救** | 过度展开，丢了对仗 |
| **What Should Be Done**（小标题） | 应采取的措施是什么？ | 应该怎么办 | 标题被改成问句，register 漂移 |
| Hardly had … been deployed **when** complaints began to mount | **刚刚**首次部署…**时**，投诉就纷纷出现 | **刚**上线，抱怨**就**开始层层累积 | 倒装强调结构被抹平 |

两个不同的英文词（limits / objectives）都被译成「规则」，说明是**词表覆盖的倾向，不是随机噪声**。

**两条对策**（都不用换模型）：

1. **注入术语表**——Hy-MT2 官方提示词表里就有 Terminology 变体（`参考下面的翻译：<en> 翻译成 <zh> …`），
   把「考纲词/固定译法」按这个格式前置即可。本项目 `translate.py::_SYS` 已经是自定义 system prompt，
   加一段术语前缀是零风险改动（注意它对 `{"t":[...]}` 的 JSON 契约不变）。
2. **把模型换成 Hy-MT2-7B**（Apache-2.0，Q4 约 4.7GB，8GB 显存可跑，代价是并发降到 2 路左右），
   接入方式完全相同（只改模型名）。

---

## 五、日常维护

```bash
ollama list                       # 看模型
ollama ps                         # 看当前是否驻留显存
ollama rm hy-mt2:1.8b             # 删除
ollama create hy-mt2:1.8b -f F:/models/hy-mt2/Modelfile.final   # 重建
```

- **Ollama 服务没起来**时，本项目会走它原本的逻辑报「未配置可用的模型服务」，不会编造译文。
- **译文缓存**在 `~/.studypad/trans_cache/`，与模型无关；换模型后想重新翻，点界面的「清除译文缓存」。
- 若把模型库换盘：改环境变量 `OLLAMA_MODELS` 后重启 Ollama；
  注意 `C:\Users\刘永键\.ollama\models\blobs` 目前是一个**指向已不存在目录的悬空符号链接**
  （库里实际是 `F:\ollama_models`），排查问题时别被它带偏。

---

## 六、复现/回归脚本（本次验证用，都在 `F:\models\hy-mt2\`）

| 脚本 | 用途 |
|---|---|
| `test_project_contract.py` | 跑项目真实链路 + 逐句对照参考译文 |
| `bench_local.py` | 短文基准（耗时/成功率/errors/进度） |
| `bench_long.py` | 长文压力基准 |
| `probe_prompts.py` | 5 种提示词形态探针（验证 JSON 契约是否被遵守） |
| `gguf_meta.py` | 读 GGUF metadata（确认 chat_template / 上下文长度） |
| `make_templates.py` | 从 GGUF 提取 Jinja 并生成两个候选 Modelfile |
| `pget.py` | 多线程分段下载器（hf-mirror 单连接会卡死，用它续传） |
