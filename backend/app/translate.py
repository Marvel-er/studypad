"""
整篇译文生成：把英文原文逐句译成自然流利的中文，供手账做「逐句对照 / 整段附译」。

三个不妥协的设计决定：

1. **翻译必须走大模型，没有规则兜底。**
   规则引擎能做的「翻译」只有词对词拼接，读起来是乱码 —— 那比不给译文更糟，
   会让人以为自己读懂了。所以没配模型时**明确告知不可用**，而不是糊一份假译文出来。

2. **对齐错了比不翻更糟。** 译文挂错句子会直接误导阅读理解。
   所以这里对每一批做「条数必须相等」的硬校验，对不上就重试，
   重试仍对不上就**整块放弃**（并在结果里报告），绝不猜。

3. **缓存按原文哈希，不按等级。** 同一篇文章换等级重新标注时，
   译文可以直接复用 —— 否则用户在六个等级间来回试，就要付六次翻译费。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import llm, settings
from .analyzer import split_spans

# ---- 成本护栏 ----------------------------------------------------------
# 一次上传可能是一份 20 页 PDF。翻译是逐句生成，不加护栏会烧掉大量 token。
MAX_CHARS = 24000          # 整篇最多翻译这么多英文字符（约 8 页 A4）
BATCH_SENTENCES = 8        # 单次请求最多几句（配合并发，见下）
BATCH_CHARS = 800          # 单次请求最多多少字符
MAX_RETRY = 1              # 对齐失败时重试次数
MAX_SPLIT_DEPTH = 1        # 一批始终对不齐时，拆成两半再试的层数

# 并发发几批。
#
# 改并发之前，批次是**串行**发的：整篇耗时 ≈ 各批耗时之和。
# 实测一篇 23 句的文章切成 2 批、各 36 s / 16 s，串起来 52 秒全是在等。
# 各批之间本来就互不依赖（合批只影响 token 效率，不影响正确性），
# 所以并发是白捡的：N 批的时间从「求和」变成「取最大值」。
#
# 为什么顺带把批调小（18 句/1800 字符 → 8 句/800 字符）：
# 单批耗时几乎全部来自模型生成输出，而输出长度与批大小成正比。
# 批越小，单批越快（并发时总时长取最慢那批），而且小批更容易对齐、
# 万一失败二分也更便宜；代价只是多几次请求，而系统提示词有前缀缓存
# （实测 prompt_cache_hit_tokens ≈ 600），多出来的开销很小。
#
# 上限取 4 是保守值：多数服务对并发请求数有限制（尤其按 RPM/TPM 计费的），
# 真要调可以用环境变量，不必改代码。
try:
    TRANSLATE_WORKERS = max(1, min(16, int(os.environ.get("STUDYPAD_TRANSLATE_WORKERS", "4"))))
except ValueError:
    TRANSLATE_WORKERS = 4

# 不翻译的区块类型
SKIP_TYPES = {"code", "figure", "table"}

# 缓存
CACHE_DIRNAME = "trans_cache"
CACHE_MAX_FILES = 400

# 每轮淘汰的上限。刻意远小于守卫的批量阈值（50）——
# 理由见 `_prune` 的 docstring：缓存淘汰是后台优化，
# 而同一轮里用户的「删除手账」是明确操作，不能被它挤掉配额。
_PRUNE_BATCH = 20

_SYS = """You are a professional literary and academic translator working into Simplified Chinese.

You will receive numbered English sentences, one per line. Translate each into natural,
fluent Simplified Chinese.

Hard requirements:
1. Return STRICT JSON: {"t": ["<译文1>", "<译文2>", ...]}
   The array length MUST equal the number of input lines, in the SAME order.
2. Translate each line independently as one complete unit.
   Do NOT merge lines. Do NOT split one line into several. Do NOT renumber.
3. Faithful: convey the full meaning. Do not add, omit, or explain anything.
   No notes, no pinyin, no alternatives, no parentheses with the English原文.
4. Natural Chinese, not translationese:
   - Reorder clauses the way Chinese would.
   - Avoid mechanical 被-constructions; prefer active or 无主句 when natural.
   - Avoid a reflexive "一个/一种" for every English "a/an".
   - Drop English plural -s and articles where Chinese does not need them.
   - Keep the register of the original (academic stays academic; narrative stays vivid).
5. Proper nouns and technical terms: use the established Chinese rendering when one exists
   (e.g. ChatGPT, Python, 联合国); otherwise keep the original spelling.
6. If a line is a heading or title, translate it as a concise heading, not a sentence.
7. Never output anything except the JSON object."""


class AlignmentError(RuntimeError):
    """模型返回的条数与输入对不上 —— 不能猜，必须报错。"""


# =====================================================================
# 缓存
# =====================================================================

# ⚠ 缓存层统一用的异常元组，**不能只写 OSError**（2026-10-15 踩过，改动前必读）。
#
# 本机的 WorkBuddy 沙箱会把 pathlib 的一批文件操作换成带守卫 / broker 的版本：
#     pathlib.Path.unlink = _safe_path_unlink     （safe-delete 守卫）
#     pathlib.Path.mkdir  = _brokered_path_mkdir  （broker）
#     pathlib.Path.touch  = _brokered_path_touch  （broker）
# 守卫不通过时抛的是 **`SystemExit(1)`** —— 它继承自 `BaseException`，
# `except OSError` 和 `except Exception` **都拦不住**，会一路穿透 anyio 的
# 线程池和 FastAPI，把整次请求打成 500。
#
# 实测后果：翻译缓存淘汰时触发，用户在前端看到的是
# 「Unexpected token 'I', "Internal S"... is not valid JSON」——
# 那是前端把 500 的纯文本响应当 JSON 解析的报错，真正的病因在这里。
#
# 缓存整层都是「优化」，所以铁律是：
# **任何文件操作失败都只当「这次没命中 / 没写成」，绝不让它影响用户的手账生成。**
# 没有直接捕 `BaseException` 的原因：KeyboardInterrupt 该放行，让进程能被打断。
_CACHE_ERRORS = (OSError, ValueError, SystemExit)


def cache_dir() -> Path:
    return settings.home() / CACHE_DIRNAME


def _key(text: str, target: str = "zh") -> str:
    return hashlib.sha1(f"{target}\x00{text}".encode("utf-8")).hexdigest()


def cache_get(text: str, target: str = "zh") -> str | None:
    p = cache_dir() / f"{_key(text, target)}.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except _CACHE_ERRORS:
        return None
    if not isinstance(d, dict):
        return None
    zh = d.get("zh")
    if isinstance(zh, str) and zh.strip():
        # 触碰 mtime，便于按最近使用淘汰。touch 也被沙箱 broker 包过，
        # 所以同样按 _CACHE_ERRORS 兜 —— 摸不到 mtime 只是淘汰顺序糙一点。
        try:
            p.touch()
        except _CACHE_ERRORS:
            pass
        return zh
    return None


def _safe_unlink(p: Path) -> bool:
    """删一个缓存文件，失败只当「没删掉」，绝不影响主流程。

    这里就是 2026-10-15 那个 500 的出事点：`_prune` 淘汰旧缓存时 `unlink`
    被沙箱守卫拦下并抛 `SystemExit(1)`，而旧代码只捕 `OSError`，
    异常一路穿透到 FastAPI，用户的前端于是收到一个纯文本 500。
    """
    try:
        p.unlink()
        return True
    except _CACHE_ERRORS:
        return False


def cache_put(text: str, zh: str, target: str = "zh") -> None:
    d = cache_dir()
    try:
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{_key(text, target)}.json").write_text(
            json.dumps({"en": text[:2000], "zh": zh}, ensure_ascii=False),
            encoding="utf-8",
        )
    except _CACHE_ERRORS:
        return          # 缓存写不进去不该让翻译失败
    # 淘汰单独包一层：它纯是维护，哪怕整段炸掉也不能让已经拿到的译文白费
    try:
        _prune(d)
    except _CACHE_ERRORS:
        pass


def _prune(d: Path) -> None:
    """
    按最近使用时间淘汰，避免缓存无限膨胀。

    ⚠ **必须限量**（2026-10-15 踩过，用户点删除手账时报 500）。
    守卫对本轮的删除次数有阈值（50）；而缓存一旦涨过 `CACHE_MAX_FILES`
    （400），这里要一次删几百个 —— 超出阈值的部分**全被拦下**，
    拦下的行为还会继续消耗配额，于是同一轮里**用户点「删除手账」
    会被误判成批量删除而失败**。症状与缓存毫无关系，极难定位：
    日志里只有一串 `SAFE_DELETE_BULK_CONFIRM_REQUIRED`，看不出因果。

    正解：**每轮最多删 `_PRUNE_BATCH` 个**，剩下的留给下一次写入时再淘汰。
    缓存是纯优化，慢一点淘汰完全没影响；而「删手账」是用户的明确操作，
    必须永远可用 —— 两者的优先级不能因为配额而颠倒。
    """
    try:
        files = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime)
    except _CACHE_ERRORS:
        return
    over = max(0, len(files) - CACHE_MAX_FILES)
    if not over:
        return
    # 留一点余量：一次真删满阈值会挤掉后面的用户操作
    budget = max(1, min(over, _PRUNE_BATCH))
    for p in files[:budget]:
        _safe_unlink(p)


def clear_cache() -> int:
    """用户显式点「清除译文缓存」—— 这里**不限量**。

    它是用户的明确意图，而且**不与其它删除抢配额**：
    `_prune` 已经改成每轮只删 `_PRUNE_BATCH` 个，把配额让了出来。
    """
    n = 0
    try:
        files = list(cache_dir().glob("*.json"))
    except _CACHE_ERRORS:
        return 0
    for p in files:
        if _safe_unlink(p):
            n += 1
    return n


# =====================================================================
# 单批翻译
# =====================================================================

_NUM_PREFIX = re.compile(r"^\s*(?:\d{1,3}\s*[.、)．]|[①-⑳]|[-–—*])\s*")


def _clean(s: str) -> str:
    t = (s or "").strip()
    t = _NUM_PREFIX.sub("", t)                 # 模型爱给译文加序号
    t = t.strip().strip('"').strip()
    return t


def _extract_array(data) -> list[str] | None:
    """从模型的各种返回形态里取出译文数组。"""
    if isinstance(data, list):
        arr = data
    elif isinstance(data, dict):
        arr = None
        for k in ("t", "translations", "translation", "zh", "items", "result"):
            v = data.get(k)
            if isinstance(v, list):
                arr = v
                break
        if arr is None:
            # 只有一个 list 值时就用它
            lists = [v for v in data.values() if isinstance(v, list)]
            arr = lists[0] if len(lists) == 1 else None
    else:
        return None
    if not isinstance(arr, list):
        return None
    out = []
    for x in arr:
        if isinstance(x, str):
            out.append(_clean(x))
        elif isinstance(x, dict):
            out.append(_clean(x.get("zh") or x.get("text") or x.get("translation") or ""))
        else:
            out.append("")
    return out


def _budget_for(chars: int) -> int:
    """
    单批的输出 token 预算。

    为什么不能「够写正文就行」：推理模型会先花掉一大笔思考 token。
    早先按纯正文估的 `300 + 1.5×字符数` 实测不够 —— 实测 18 句那批
    （1843 字符）completion_tokens=2710，其中 **2439 是思考**，正文只写了 271 个
    就没了预算，`content` 直接是空字符串；下游看不出是「被思考吃穿」，
    只能判成「条数对不上」→ 重试 → 再二分，一串连锁浪费。

    现在按 3 倍估并给 400 打底（`llm.chat` 默认还会关掉思考，算双保险）。
    上限仍留 4000：不设上限会在上下文窗口小的本地模型上过不了校验。
    """
    return min(4000, 400 + int(chars * 3))


def _translate_batch(cfg: llm.LLMConfig, sents: list[str]) -> list[str]:
    """翻一批句子。条数对不上直接抛 AlignmentError（不猜）。"""
    chars = sum(len(s) for s in sents)
    user = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(sents))
    budget = _budget_for(chars)

    prev_n: int | None = None
    for attempt in range(MAX_RETRY + 1):
        # 重试时要告诉模型「上次给错了几条」，否则它不知道该修什么。
        # 注意这里必须记**条数**：早先写的是 len(上一次的原文)，那是个字符数，
        # 对模型毫无意义 —— 相当于拿着一串乱码去质问它。
        hint = "" if attempt == 0 else (
            f"\n\nNOTE: your previous reply had the wrong number of items "
            f"(expected exactly {len(sents)}, got {prev_n if prev_n is not None else 'an unparsable reply'}). "
            f"Return exactly {len(sents)} items this time.")
        out = llm.chat(cfg, [
            {"role": "system", "content": _SYS},
            {"role": "user", "content": user + hint},
        ], max_tokens=budget, temperature=0.25 if attempt == 0 else 0.05)
        try:
            arr = _extract_array(llm.parse_json(out))
        except Exception:  # noqa: BLE001 — 解析失败也算这一轮没对上
            arr = None
        if arr is not None and len(arr) == len(sents):
            return arr
        prev_n = len(arr) if arr is not None else None

    raise AlignmentError(
        f"译文条数与原文不符（期望 {len(sents)} 条，模型多次返回未能对齐）")


def _translate_group(cfg: llm.LLMConfig, sents: list[str],
                     errors: list[str], where: str, depth: int = 0) -> list[str]:
    """
    翻一组句子，返回**与 `sents` 等长**的译文列表，失败的位置是空串。

    为什么要二分：合批之后一批里会装进好几个段落的句子，
    万一模型这一批整体对不齐，一刀切会让无关的几个段落一起没译文。
    拆成两半各试一次，能把「读不懂的那个句子」隔离出来，保住剩下的。

    只有 `AlignmentError`（对不齐）才值得二分 —— 网络/鉴权/额度这类错误
    拆多细都一样失败，二分只会把一次失败放大成好几次请求。
    `MAX_SPLIT_DEPTH = 1` 就是为了给这个放大加个上限：一批 18 句最坏 6 次请求。
    """
    try:
        return _translate_batch(cfg, sents)
    except AlignmentError as ex:
        if len(sents) > 1 and depth < MAX_SPLIT_DEPTH:
            mid = len(sents) // 2
            return (_translate_group(cfg, sents[:mid], errors, where, depth + 1)
                    + _translate_group(cfg, sents[mid:], errors, where, depth + 1))
        errors.append(f"{where}: {str(ex)[:80]}")
        return [""] * len(sents)
    except Exception as ex:  # noqa: BLE001 — 请求本身就没发出去
        errors.append(f"{where}: {str(ex)[:80]}")
        return [""] * len(sents)


# =====================================================================
# 整篇翻译
# =====================================================================

def _batches(texts: list[str]) -> list[list[int]]:
    """把句子下标按条数 / 字符数上限切成批。"""
    out: list[list[int]] = []
    cur: list[int] = []
    chars = 0
    for idx, txt in enumerate(texts):
        if cur and (len(cur) >= BATCH_SENTENCES or chars + len(txt) > BATCH_CHARS):
            out.append(cur)
            cur, chars = [], 0
        cur.append(idx)
        chars += len(txt)
    if cur:
        out.append(cur)
    return out


def translate_blocks(blocks: list[dict], cfg: llm.LLMConfig,
                     target: str = "zh", on_progress=None) -> dict:
    """
    翻译整篇。返回：

        {
          "blocks": {block_id: {"sentences": [{start,end,en,zh}], "zh": "整段译文"}},
          "total": 段落数, "done": 成功段数, "skipped": 未翻译段数,
          "cache_hits": 命中缓存的段数, "chars": 实际翻译字符数,
          "truncated": 是否因超长而截断, "errors": [说明...]
        }

    `on_progress(done, total, note)` 可选，按**批**上报。
    为什么用批而不是段做分母：真正的耗时几乎全在「等模型回这一批」上，
    用批做分母，进度条才和用户的等待感受对得上（用段做分母会一步跨得太大）。
    缓存命中的句子不进批，所以分母只统计真要发出去的请求。

    分三趟走：

    1. 挑出要翻的句子（跳过代码/图表/表格、超长截断、命中缓存的先摘掉），
       算出本次真正要发给模型的句子清单；
    2. **跨段落合批 + 并发**翻译。手账原文常是一段一两句，按段发请求会让一份 20 页 PDF
       变成上百次往返；合批后通常十几次就翻完，既省 token 也省等待。
       各批之间互不依赖，所以并发发（`TRANSLATE_WORKERS` 路），
       整篇耗时从「各批求和」变成「取最慢那批」；
    3. 按段把译文装回去。句子缺译时整段译文留空并置 `partial`，
       免得读到一段真假混杂的文字还以为翻全了。
    """
    result: dict[str, dict] = {}
    errors: list[str] = []
    total = done = skipped = cache_hits = 0
    chars_used = 0
    truncated = False

    def _tick(d: int, t: int, note: str) -> None:
        if on_progress:
            try:
                on_progress(d, t, note)
            except Exception:  # noqa: BLE001 — 进度丢了是小事
                pass

    # ---- 第一趟：决定翻哪些句子，并把缓存命中的先摘掉 ----
    spans_of: dict[str, list[tuple[int, int, str]]] = {}
    zh_of: dict[str, dict[int, str]] = {}
    todo: list[tuple[str, int, int, str]] = []

    for b in blocks:
        if b.get("meta", {}).get("skip"):
            continue
        if (b.get("type") or "") in SKIP_TYPES:
            continue
        raw = b.get("text") or ""
        text = raw.strip()
        if len(text) < 2:
            continue

        total += 1

        if chars_used + len(text) > MAX_CHARS:
            truncated = True
            skipped += 1
            continue

        # ⚠ span 必须用**未 strip** 的原文算，不能用 strip 后的。
        #
        # 全链路有三处独立调用 `split_spans`，它们必须落在同一套偏移上：
        #   · annotator.analyze_block  —— 用 `b["text"]` 原文，产出标注的 start/end
        #   · render._render_block_sentence —— 用 `block["text"]` 原文，按 span 切原文
        #   · translate（这里）            —— 产出 `sentences[].start`，译文就挂在这个键上
        # 这里一旦先 strip，前导空白被吃掉，第二句及以后的起始位置整体前移
        # （实测 `[(2,69),(70,178)]` → `[(0,67),(68,176)]`），
        # 于是 render 拿着 70 去 zh_map 里找、只找到 68 → **一个绿框都不出**，
        # 还顺手误报「本段另有 N 句未取到译文」和「中文译文只覆盖 0/N 句」。
        # 属于静默全丢，比报错更难发现。
        spans = split_spans(raw)
        if not spans:
            skipped += 1
            continue

        chars_used += len(text)
        bid = b["id"]
        spans_of[bid] = spans
        zh_of[bid] = {}
        for s, e, sent in spans:
            hit = cache_get(sent, target)
            if hit:
                zh_of[bid][s] = hit
                cache_hits += 1
            else:
                todo.append((bid, s, e, sent))

    # ---- 第二趟：合批并发翻译 ----
    # 先一次性切好批，这样才知道要发几个请求（进度条的分母）
    texts = [t[3] for t in todo]
    batches = _batches(texts)
    n_batches = len(batches)
    if n_batches == 0:
        _tick(1, 1, "全部命中缓存" if total else "无需翻译")
    else:
        _tick(0, n_batches, f"准备并发翻译 {n_batches} 批（{min(TRANSLATE_WORKERS, n_batches)} 路）")
        # 每批的错误先各自记，最后按批次顺序合并 —— 从多个线程往同一个 list 里 append
        # 虽然不会崩，但顺序会随机，测试里断言错误内容时就会变成偶发假失败。
        batch_errors: list[list[str]] = [[] for _ in batches]
        finished = 0

        def _one(k: int) -> list[str]:
            idxs = batches[k]
            return _translate_group(cfg, [texts[i] for i in idxs],
                                    batch_errors[k], f"第 {k + 1} 批")

        with ThreadPoolExecutor(max_workers=min(TRANSLATE_WORKERS, n_batches)) as pool:
            # 必须按**完成顺序**处理（as_completed），不能按提交顺序 fut.result()：
            # 后者会被最慢的那一批堵住，后面早早回来的批次也回填不了，
            # 进度条就变成「一直不动、最后一次性跳到底」，白做了并发。
            futures = {pool.submit(_one, k): k for k in range(n_batches)}
            for fut in as_completed(futures):
                k = futures[fut]
                try:
                    got = fut.result()
                except BaseException as ex:  # noqa: BLE001 — 单批炸了也不能拖垮整篇
                    batch_errors[k].append(f"第 {k + 1} 批: {type(ex).__name__}: {str(ex)[:80]}")
                    got = [""] * len(batches[k])
                # 回填、写缓存、报进度**一律在主线程做**：不必加锁，
                # 也不会出现两个线程同时往同一段落的 zh_of 里写。
                for i, zh in zip(batches[k], got):
                    if not zh:
                        continue
                    bid, s, _e, sent = todo[i]
                    zh_of[bid][s] = zh
                    cache_put(sent, zh, target)
                finished += 1
                _tick(finished, n_batches,
                      f"已完成 {finished}/{n_batches} 批"
                      + ("，还在等其余批次" if finished < n_batches else ""))
        for e in batch_errors:
            errors.extend(e)

    # ---- 第三趟：按段组装 ----
    for b in blocks:
        bid = b.get("id")
        spans = spans_of.get(bid)
        if not spans:
            continue
        zs = zh_of[bid]
        sentences = [
            {"start": s, "end": e, "en": sent, "zh": zs[s]}
            for s, e, sent in spans if zs.get(s)
        ]
        if not sentences:
            skipped += 1
            continue
        all_zh = len(sentences) == len(spans)
        result[bid] = {
            "sentences": sentences,
            # 缺句时不能拿空串拼，否则读起来像「这里原文就没有东西」
            "zh": "".join(x["zh"] for x in sentences) if all_zh else "",
            "partial": not all_zh,
        }
        done += 1

    return {
        "blocks": result,
        "total": total, "done": done, "skipped": skipped,
        "cache_hits": cache_hits, "chars": chars_used,
        "truncated": truncated, "errors": errors,
    }


def flatten(trans: dict) -> str:
    """把 block 级译文压成纯文本（给「整段附译」以外的场景用）。"""
    parts = []
    for bid in sorted(trans):
        d = trans[bid]
        zh = d.get("zh") or "".join(s["zh"] for s in d.get("sentences", []))
        if zh:
            parts.append(zh)
    return "\n".join(parts)


def stats() -> dict:
    """缓存与护栏的当前状态，给 /api 与前端提示用。"""
    try:
        n = len(list(cache_dir().glob("*.json")))
    except OSError:
        n = 0
    return {
        "cache_entries": n,
        "cache_dir": str(cache_dir()),
        "max_chars": MAX_CHARS,
        "batch_sentences": BATCH_SENTENCES,
        "batch_chars": BATCH_CHARS,
        "workers": TRANSLATE_WORKERS,
        "required": "llm",          # 翻译必须由大模型完成，无规则兜底
    }
