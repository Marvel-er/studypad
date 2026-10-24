"""
探针：把模型返回的**原始 JSON**打出来 —— 定案「为什么回复是空的」。

`probe_align_fail.py` 已经证明：失败的那些调用，`message.content` 是**空字符串**，
而加了「上次给错了几条」提示的重试就成功了。空回复的可能原因只剩几种，
但它们对应的修法完全不同，所以必须看原始响应：

  · `finish_reason == "length"` + `usage.completion_tokens` 顶到 `max_tokens`
      → **输出被预算截断**（推理模型先花掉预算去思考，content 还没开始写就没了）。
        修法：抬高预算 + 把「空回复/被截断」当成可重试的独立状况。
  · `finish_reason == "stop"` 但 content 为空
      → 模型压根没写（拒答/格式异常），抬预算没用。
        修法：改提示词或缩批次。
  · 出现 `reasoning_content` 字段
      → 说明这是个会「先思考」的模型，预算必须按「思考 + 正文」两段来估。

输出：out/_raw_response.txt
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import httpx  # noqa: E402

from app import llm, settings  # noqa: E402

_real = settings.load()
CFG = llm.LLMConfig(
    provider=_real.get("provider", ""),
    api_key=_real.get("api_key", ""),
    base_url=_real.get("base_url", ""),
    model=_real.get("model", ""),
)

LOG: list[str] = []
r = CFG.resolved()
LOG.append(f"模型 = {r.provider} / {r.model}   base_url = {r.base_url}")
LOG.append("")

# 用真实文章的前 18 句做输入 —— 复现「大批次返回空」的那个形态
sys.path.insert(0, str(ROOT / "backend"))
os.environ["STUDYPAD_HOME"] = str(Path(os.environ.get("TEMP", ".")) / "_studypad_raw")
from app import parsers, translate  # noqa: E402

text = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
blocks = [b.as_dict() for b in parsers.parse_text(text)]
sents: list[str] = []
for b in blocks:
    t = (b.get("text") or "").strip()
    if len(t) >= 2:
        sents += [x[2] for x in translate.split_spans(t)]
big = sents[:18]
small = sents[:9]


def probe(label: str, ss: list[str]) -> None:
    user = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(ss))
    chars = sum(len(s) for s in ss)
    budget = min(4000, 300 + int(chars * 1.5))
    payload = {
        "model": r.model,
        "messages": [{"role": "system", "content": translate._SYS},
                     {"role": "user", "content": user}],
        "temperature": 0.25,
        "max_tokens": budget,
        "response_format": {"type": "json_object"},
    }
    LOG.append(f"=== {label}：{len(ss)} 句 / {chars} 字符 / max_tokens={budget}")
    t0 = time.time()
    try:
        with httpx.Client(timeout=r.timeout) as c:
            resp = c.post(f"{r.base_url.rstrip('/')}/chat/completions",
                          json=payload,
                          headers={"Content-Type": "application/json",
                                   "Authorization": f"Bearer {r.api_key}"})
        dt = time.time() - t0
        LOG.append(f"    HTTP {resp.status_code}  耗时 {dt:.2f}s")
        data = resp.json()
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        LOG.append(f"    finish_reason = {choice.get('finish_reason')!r}")
        LOG.append(f"    usage = {json.dumps(data.get('usage'), ensure_ascii=False)}")
        LOG.append(f"    message 的字段 = {sorted(msg.keys())}")
        content = msg.get("content")
        LOG.append(f"    content 长度 = {len(content) if isinstance(content, str) else content!r}")
        if isinstance(content, str) and content:
            LOG.append(f"    content 前 160 字 = {content[:160]!r}")
        for k in msg:
            if k != "content" and isinstance(msg[k], str) and msg[k]:
                LOG.append(f"    {k} 长度={len(msg[k])}  前 200 字 = {msg[k][:200]!r}")
    except Exception as e:  # noqa: BLE001
        LOG.append(f"    请求失败：{type(e).__name__}: {e}")
    LOG.append("")


probe("大批次（当前切法）", big)
probe("半批（当前的二分结果）", small)

LOG.append("判读：")
LOG.append("  finish_reason=length 或 completion_tokens == max_tokens → 预算不够，抬 max_tokens；")
LOG.append("  出现 reasoning_content → 预算要按「思考 + 正文」估，且思考越长越要留足余量；")
LOG.append("  finish_reason=stop 且 content 空 → 与预算无关，得改提示词/缩批次。")

(ROOT / "out" / "_raw_response.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
print("\n".join(LOG))
