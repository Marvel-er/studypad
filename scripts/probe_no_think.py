"""
探针：试出「关掉思考」到底该在请求体里写哪个字段。

背景（已由 `probe_raw_response.py` 查实）：`deepseek-v4-pro` 是推理模型，
翻 18 句要花 2439 个思考 token、只写 271 个正文 token —— **90% 的预算与时间
都花在翻译根本不需要的推理上**，而且思考一超预算，`content` 直接是空的，
被判成「对不齐」→ 重试 → 再二分，一串连锁浪费。

各家的关法不统一，写错字段轻则被忽略（照样思考），重则 400。
所以逐个试、看 `reasoning_tokens` 是否真的归零：

  · `thinking: {"type": "disabled"}`      —— DeepSeek 新版 / Anthropic 风格
  · `chat_template_kwargs: {thinking: false}` —— DeepSeek v3.1/v3.2 文风
  · `enable_thinking: false`             —— Qwen / vLLM 系
  · `reasoning_effort: "none" | "minimal"` —— OpenAI 风格

输出：out/_no_think.txt
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import httpx  # noqa: E402

from app import llm, settings  # noqa: E402

_real = settings.load()
r = llm.LLMConfig(
    provider=_real.get("provider", ""),
    api_key=_real.get("api_key", ""),
    base_url=_real.get("base_url", ""),
    model=_real.get("model", ""),
).resolved()

SENTS = [
    "Economists have long assumed that productivity could be improved simply by removing friction.",
    "Yet the evidence, which has accumulated over two decades of workplace research, suggests something rather different.",
    "What matters most is not the speed of a process but the density of the connections that surround it.",
    "There is no denying that remote work has reshaped how firms measure output.",
]

SYS = ('You will receive numbered English sentences, one per line. Translate each into natural, '
       'fluent Simplified Chinese. Return STRICT JSON: {"t": ["...", "..."]} with exactly one '
       'item per input line. Do not merge or split items. Never output anything except the JSON object.')

VARIANTS: list[tuple[str, dict]] = [
    ("baseline（不传任何字段）", {}),
    ('thinking: {"type": "disabled"}', {"thinking": {"type": "disabled"}}),
    ("chat_template_kwargs: {thinking: false}", {"chat_template_kwargs": {"thinking": False}}),
    ("enable_thinking: false", {"enable_thinking": False}),
    ('reasoning_effort: "none"', {"reasoning_effort": "none"}),
    ('reasoning_effort: "minimal"', {"reasoning_effort": "minimal"}),
]

LOG: list[str] = [f"模型 = {r.provider} / {r.model}   base_url = {r.base_url}",
                  f"输入 = {len(SENTS)} 句，max_tokens = 800", ""]
OK_VARIANTS: list[str] = []

for label, extra in VARIANTS:
    user = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(SENTS))
    payload = {"model": r.model,
               "messages": [{"role": "system", "content": SYS},
                            {"role": "user", "content": user}],
               "temperature": 0.25, "max_tokens": 800,
               "response_format": {"type": "json_object"}}
    payload.update(extra)
    t0 = time.time()
    try:
        with httpx.Client(timeout=90) as c:
            resp = c.post(f"{r.base_url.rstrip('/')}/chat/completions",
                          json=payload,
                          headers={"Content-Type": "application/json",
                                   "Authorization": f"Bearer {r.api_key}"})
        dt = time.time() - t0
        if resp.status_code != 200:
            LOG.append(f"✗ {label}")
            LOG.append(f"    HTTP {resp.status_code}  {resp.text[:200]}")
            LOG.append("")
            continue
        d = resp.json()
        choice = (d.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        usage = d.get("usage") or {}
        det = usage.get("completion_tokens_details") or {}
        rt = det.get("reasoning_tokens")
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        n_items = None
        try:
            arr = llm.parse_json(content)
            n_items = len(arr.get("t") or arr) if isinstance(arr, dict) else len(arr)
        except Exception:  # noqa: BLE001
            n_items = None
        LOG.append(f"{'✓' if (rt or 0) == 0 and n_items == len(SENTS) else '·'} {label}")
        LOG.append(f"    HTTP 200  耗时 {dt:.2f}s  completion={usage.get('completion_tokens')} "
                   f"reasoning_tokens={rt}  content={len(content)}字 "
                   f"reasoning_content={len(reasoning)}字  条数={n_items}")
        LOG.append(f"    content 前 130 字 = {content[:130]!r}")
        LOG.append("")
        if (rt or 0) == 0 and n_items == len(SENTS):
            OK_VARIANTS.append(label)
    except Exception as e:  # noqa: BLE001
        LOG.append(f"✗ {label}  异常：{type(e).__name__}: {e}")
        LOG.append("")

LOG.append("可以关掉思考的写法：" + ("；".join(OK_VARIANTS) if OK_VARIANTS else "（一个都不行）"))
(ROOT / "out" / "_no_think.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
print("\n".join(LOG))
