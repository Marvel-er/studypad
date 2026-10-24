"""
探针：量清楚「译文慢」到底慢在哪一环。

只做一件坏事 —— 花一次极小的真实调用（2 句、约 60 字符）测出**单次请求的真实耗时**。
不计这一下，后面所有「优化」都是猜的：
单次 3 秒说明慢在往返次数（该并发/合批），单次 30 秒说明慢在模型本身
（该换更快的模型或砍输出），两种结论对应的改法完全不同。

输出：out/_llm_latency.txt
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

# 故意不设 STUDYPAD_HOME：这里要看的就是用户真实保存的那份配置
from app import llm, settings  # noqa: E402

LOG: list[str] = []
p = settings.path()
LOG.append(f"配置文件 = {p}   存在={p.exists()}")
saved = settings.load()
cfg = llm.LLMConfig(
    provider=saved.get("provider", ""),
    api_key=saved.get("api_key", ""),
    base_url=saved.get("base_url", ""),
    model=saved.get("model", ""),
)
r = cfg.resolved()
LOG.append(f"provider={r.provider!r} model={r.model!r}")
LOG.append(f"base_url={r.base_url!r}")
LOG.append(f"ready={r.ready}  timeout={r.timeout}s")
if not r.ready:
    LOG.append("未配置可用模型，探针结束")
    (ROOT / "out" / "_llm_latency.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))
    sys.exit(0)

SYS = ('You will receive numbered English sentences, one per line. Translate each into '
       'natural, fluent Simplified Chinese. Return STRICT JSON: {"t": ["...", "..."]} '
       'with exactly one item per input line.')
user = "1. The committee decided to proceed.\n2. The results are promising."

LOG.append("")
LOG.append("发一次真实请求（2 句 / %d 字符）……" % len(user))
t0 = time.time()
try:
    out = llm.chat(cfg, [{"role": "system", "content": SYS},
                         {"role": "user", "content": user}], max_tokens=400)
    dt = time.time() - t0
    LOG.append(f"✓ 往返耗时 = {dt:.2f} 秒")
    LOG.append(f"  原始回复（前 200 字）= {out[:200]!r}")
    try:
        parsed = llm.parse_json(out)
        LOG.append(f"  解析后 = {json.dumps(parsed, ensure_ascii=False)[:200]}")
    except Exception as e:  # noqa: BLE001
        LOG.append(f"  ！解析失败：{e}")
except Exception as e:  # noqa: BLE001
    dt = time.time() - t0
    LOG.append(f"✗ 失败（耗时 {dt:.2f} 秒）：{type(e).__name__}: {e}")

LOG.append("")
LOG.append("判读：")
LOG.append("  单次 < 5 秒  → 慢在往返次数，并发/合批能直接砍掉大半")
LOG.append("  单次 > 15 秒 → 慢在模型本身（长思考或输出冗长），改往返次数收益有限")

(ROOT / "out" / "_llm_latency.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
print("\n".join(LOG))
