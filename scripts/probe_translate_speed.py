"""
探针：量整篇翻译的真实耗时构成（每次调用分别计时）。

为什么要它：`probe_llm_latency.py` 已经证明**单次往返只要 2 秒多**，
那整篇慢就只可能慢在「串起来发了几次」或「单次输出太长」。
这两件事对应完全不同的改法，必须量出来再动手：

  · 若 N 次调用各自都不慢、总时长 ≈ N × 单次 → 慢在**串行往返**，并发即可成倍改善；
  · 若某次调用异常长（几十秒）→ 慢在**那一次的输出**（截断重试/长思考），
    并发救不了，得改单次的预算或降批次规模。

**不碰用户的真实缓存**：先读真实配置，再把 `STUDYPAD_HOME` 指到临时目录，
所以缓存写在临时目录里，每次都是「冷缓存」，量到的才是真实耗时。

输出：out/_translate_speed.txt
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app import llm, settings  # noqa: E402,F401  — 先拿真实配置

_real = settings.load()
CFG = llm.LLMConfig(
    provider=_real.get("provider", ""),
    api_key=_real.get("api_key", ""),
    base_url=_real.get("base_url", ""),
    model=_real.get("model", ""),
)

# 配置读完了，再切走 home：缓存落到临时目录，不污染用户真实缓存
TMP = Path(tempfile.gettempdir()) / "_studypad_speed"
TMP.mkdir(parents=True, exist_ok=True)
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import parsers, translate  # noqa: E402

LOG: list[str] = []
CALLS: list[dict] = []
_orig_chat = llm.chat


def timed_chat(cfg, messages, **kw):
    """只包一层计时，不改任何业务逻辑。"""
    user = messages[-1]["content"] if messages else ""
    t0 = time.time()
    err = ""
    try:
        out = _orig_chat(cfg, messages, **kw)
        return out
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        raise
    finally:
        CALLS.append({"s": round(time.time() - t0, 2), "chars": len(user),
                      "max_tokens": kw.get("max_tokens"), "err": err})


llm.chat = timed_chat
translate.llm.chat = timed_chat


def main() -> None:
    r = CFG.resolved()
    LOG.append(f"模型 = {r.provider} / {r.model}   缓存目录 = {TMP}")
    LOG.append(f"合批参数 = {translate.BATCH_SENTENCES} 句 / {translate.BATCH_CHARS} 字符"
               f" / 总上限 {translate.MAX_CHARS} 字符")
    LOG.append(f"并发参数 = workers={getattr(translate, 'TRANSLATE_WORKERS', '（尚无）')}")
    LOG.append("")

    text = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
    blocks = [b.as_dict() for b in parsers.parse_text(text)]

    # 每次都要冷缓存。临时目录会跨次留存，不清的话第二次跑全是缓存命中、
    # 只发一两个请求，量出来的「快了 30 倍」是假的（第一次踩过）。
    cleared = translate.clear_cache()
    LOG.append(f"已清空临时缓存 {cleared} 条（保证是冷启动测量）")

    n_sent = sum(len(translate.split_spans((b.get("text") or "").strip()))
                 for b in blocks if len((b.get("text") or "").strip()) >= 2)
    chars = sum(len((b.get("text") or "").strip()) for b in blocks)

    LOG.append(f"文档：{len(blocks)} 个区块 / {n_sent} 句 / {chars} 字符")
    LOG.append("开始翻译（冷缓存）……")
    LOG.append("")

    ticks: list[str] = []

    def on_prog(d, t, note):
        ticks.append(f"{d}/{t} {note}  t={time.time() - T0:.1f}s")

    T0 = time.time()
    res = translate.translate_blocks(blocks, CFG, on_progress=on_prog)
    total = time.time() - T0

    LOG.append("进度上报序列：")
    for x in ticks:
        LOG.append("    " + x)
    LOG.append("")
    LOG.append("每次模型调用：")
    for i, c in enumerate(CALLS, 1):
        LOG.append(f"    #{i}  {c['s']:>6.2f}s  输入 {c['chars']:>5} 字符  "
                   f"max_tokens={c['max_tokens']}" + (f"  失败 {c['err']}" if c["err"] else ""))
    LOG.append("")
    LOG.append(f"▶ 调用 {len(CALLS)} 次，串行总耗时 {total:.2f} 秒"
               f"（模型时间合计 {sum(c['s'] for c in CALLS):.2f} 秒）")
    LOG.append(f"  译出段数 {res['done']}/{res['total']}，句数 "
               f"{sum(len(v['sentences']) for v in res['blocks'].values())}，"
               f"错误 {len(res['errors'])} 条")
    if res["errors"]:
        LOG.append("  错误：" + " | ".join(res["errors"][:3]))
    if CALLS:
        LOG.append(f"  单次平均 {sum(c['s'] for c in CALLS) / len(CALLS):.2f} 秒")

    (ROOT / "out" / "_translate_speed.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))


try:
    main()
except BaseException:  # noqa: BLE001
    import traceback
    LOG.append(traceback.format_exc())
    (ROOT / "out" / "_translate_speed.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))
    raise
