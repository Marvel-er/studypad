"""
用**真实配置的大模型**生成手账成品（含中文译文），保存成可直接打开的 HTML。

和 `make_translated_demo.py` 的分工：
  · `make_translated_demo.py` 用手人译文，**不依赖任何模型**，用来验收版式、做渲染回归；
  · 这个脚本打真实服务、走真实模型，用来验收**译文质量**。

它只调用已经在跑的服务的 HTTP 接口，不重复实现任何链路逻辑 ——
所以它验的就是用户真正会拿到的那份东西。

用法：
    python scripts/make_llm_handbook.py [level_id] [模式]
    模式：sentence（逐句对照，默认）/ paragraph（整段附译）/ both
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8300"
SRC = ROOT / "samples" / "sample_article.md"
OUT = ROOT / "out"

level = sys.argv[1] if len(sys.argv) > 1 else "cet4"
mode_arg = sys.argv[2] if len(sys.argv) > 2 else "both"

# 等级必须是服务端认识的 id。不校验的话，一个拼错的参数会一路走到
# 「拼文件名」那一步才炸，报出来的是权限错或非法路径，看不出真正原因。
KNOWN = {"high_school", "cet4", "cet6", "kaoyan", "ielts", "toefl"}
if level not in KNOWN:
    print(f"未知等级 {level!r}，可用：{' / '.join(sorted(KNOWN))}")
    sys.exit(2)

modes = [("sentence", "逐句对照"), ("paragraph", "整段附译")] if mode_arg == "both" \
    else [(mode_arg, "逐句对照" if mode_arg == "sentence" else "整段附译")]


def main() -> int:
    st = httpx.get(f"{BASE}/api/translate/status", timeout=30, trust_env=False).json()
    lines = [f"模型     : {st.get('provider')} / {st.get('model')}",
             f"可翻译   : {st.get('available')}",
             f"缓存条目 : {st.get('cache_entries')}"]
    if not st.get("available"):
        lines.append("未配置可用模型 —— 译文需要大模型，先配置再跑。")
        (OUT / "_llm_handbook.txt").write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines))
        return 2

    for mode, label in modes:
        with open(SRC, "rb") as f:
            r = httpx.post(f"{BASE}/api/analyze", timeout=600, trust_env=False,
                           files={"file": (SRC.name, f, "text/markdown")},
                           data={"level_id": level, "use_llm": "false",
                                 "translate": "true", "trans_mode": mode})
        if r.status_code != 200:
            lines.append(f"[{label}] {r.status_code} {r.text[:200]}")
            continue
        d = r.json()
        tr = d.get("translations") or {}
        pairs = [s for t in tr.values() for s in t["sentences"]]
        p = OUT / f"handbook-{level}-真实译文-{label}.html"
        p.write_text(d["html"], encoding="utf-8")
        lines.append(f"[{label}] trans_mode={d['trans_mode']} 段={len(tr)} 句={len(pairs)} "
                     f"→ {p.name} ({len(d['html'])} 字符)")
        lines.append(f"          trans_note = {d.get('trans_note')}")
        for s in pairs[:3]:
            lines.append(f"          EN: {s['en'][:66]}")
            lines.append(f"          ZH: {s['zh'][:66]}")

    (OUT / "_llm_handbook.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
