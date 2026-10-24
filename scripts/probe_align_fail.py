"""
探针：揪出「某一批怎么也对不起」的原始回复。

`probe_translate_speed.py` 量到：23 句的文档本该 2 次调用，实际发了 **6 次**、94 秒里
**57 秒是白等的** —— 第 2 批（5 句）模型两次都对不齐，二分后右半（3 句）又两次对不齐，
最后整整一段译文被放弃。

不查清这一批模型到底回了什么，「优化」就只能靠猜：
是 JSON 断了？是并成一条了？是被截断了？三种原因三种改法。

这个探针把**原始回复原样打出来**，并把那几句单独再发一次做对照。
输出：out/_align_fail.txt
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app import llm, settings  # noqa: E402,F401

_real = settings.load()
CFG = llm.LLMConfig(
    provider=_real.get("provider", ""),
    api_key=_real.get("api_key", ""),
    base_url=_real.get("base_url", ""),
    model=_real.get("model", ""),
)

TMP = Path(tempfile.gettempdir()) / "_studypad_align"
TMP.mkdir(parents=True, exist_ok=True)
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import parsers, translate  # noqa: E402

LOG: list[str] = []
SEEN: list[dict] = []
_orig_chat = llm.chat


def capture_chat(cfg, messages, **kw):
    user = messages[-1]["content"] if messages else ""
    t0 = time.time()
    try:
        out = _orig_chat(cfg, messages, **kw)
        SEEN.append({"user": user, "out": out, "s": round(time.time() - t0, 2)})
        return out
    except Exception as e:  # noqa: BLE001
        SEEN.append({"user": user, "out": f"<异常> {type(e).__name__}: {e}",
                     "s": round(time.time() - t0, 2)})
        raise


llm.chat = capture_chat
translate.llm.chat = capture_chat


def show(i: int, note: str = "") -> None:
    s = SEEN[i]
    LOG.append(f"--- 调用 #{i + 1}（{s['s']}s，输入 {len(s['user'])} 字符）{note}")
    LOG.append("输入：")
    for line in s["user"].split("\n")[:12]:
        LOG.append("    " + line[:150])
    LOG.append("原始回复：")
    LOG.append("    " + repr(s["out"])[:1500])
    # 尽力还原「模型给了几条」
    try:
        data = llm.parse_json(s["out"])
        arr = translate._extract_array(data)
        LOG.append(f"    解析成功：类型={type(data).__name__} 取出 {len(arr) if arr else 0} 条")
    except Exception as e:  # noqa: BLE001
        LOG.append(f"    解析失败：{type(e).__name__}: {str(e)[:120]}")
    LOG.append("")


def main() -> None:
    text = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
    blocks = [b.as_dict() for b in parsers.parse_text(text)]
    todo: list[str] = []
    for b in blocks:
        t = (b.get("text") or "").strip()
        if len(t) < 2:
            continue
        for _s, _e, sent in translate.split_spans(t):
            todo.append(sent)

    batches = translate._batches(todo)
    LOG.append(f"共 {len(todo)} 句，切成 {len(batches)} 批："
               + " / ".join(str(len(b)) for b in batches))
    LOG.append("")

    errors: list[str] = []
    for k, idxs in enumerate(batches, 1):
        sents = [todo[i] for i in idxs]
        before = len(SEEN)
        try:
            got = translate._translate_group(CFG, sents, errors, f"第 {k} 批")
            LOG.append(f"第 {k} 批（{len(sents)} 句）：成功 {sum(1 for z in got if z)}/{len(sents)}，"
                       f"新发 {len(SEEN) - before} 次调用")
            for i in range(before, len(SEEN)):
                show(i)
        except Exception as e:  # noqa: BLE001
            LOG.append(f"第 {k} 批抛异常：{e}")

        if errors and any("条数" in e for e in errors):
            # 定位到病句：把这批逐句单独发一遍，看是不是某一句特有问题
            LOG.append(f"★ 第 {k} 批出现对齐失败，逐句单发做对照：")
            for s in sents:
                before = len(SEEN)
                try:
                    got = translate._translate_batch(CFG, [s])
                    LOG.append(f"    单句成功（{len(s)} 字符）→ {got[0][:60]!r}")
                except Exception as e:  # noqa: BLE001
                    LOG.append(f"    单句失败（{len(s)} 字符）：{type(e).__name__}: {str(e)[:80]}")
                    for i in range(before, len(SEEN)):
                        show(i, "（单句对照）")
            break

    LOG.append("")
    LOG.append(f"合计真实调用 {len(SEEN)} 次，"
               f"模型耗时合计 {sum(x['s'] for x in SEEN):.1f} 秒")
    LOG.append("错误记录：" + (" | ".join(errors) if errors else "无"))
    (ROOT / "out" / "_align_fail.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))


try:
    main()
except BaseException:  # noqa: BLE001
    import traceback
    LOG.append(traceback.format_exc())
    (ROOT / "out" / "_align_fail.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))
    raise
