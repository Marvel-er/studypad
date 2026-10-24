"""
端到端验证：打**真在跑的服务**，确认本轮改动真的生效。

为什么要打真服务而不是直接调函数：
模块改动生效的前提是进程被重启过。直接调函数永远是「新代码」，
验不出「服务还挂着旧模块」这种最常见的假成功。所以这里走 HTTP。

验四件事：
  ① 新打印分页规则进了产物（.block 允许断、句对不拆）
  ② 译文覆盖按**句**报数，且页眉 chip 如实
  ③ 产物里没有空译文框，也没有「（本句未译出）」占位框
  ④ 生词表每一行都有音标/词性/释义（用户明确要求补全的那三列）

用法：python scripts/run_selftest.py scripts/verify_render_api.py out/_verify_api.txt
传输：优先打真在跑的服务（`STUDYPAD_API` 可指定地址）；
      本机沙箱会挡掉回环（直连 TimeoutError / 走代理 502），此时自动退回
      **进程内 ASGI** 并在开头打印实际传输方式 —— 这条路验不出「服务挂着旧模块」，
      所以看到「进程内 ASGI」时，改完代码请用 scripts/restart_server.py 重启再看。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8300"
TEXT = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")

sys.path.insert(0, str(ROOT / "scripts"))
import _api  # noqa: E402

# 优先真服务；沙箱挡掉回环时退回进程内 ASGI（见 scripts/_api.py）。
# 注意：进程内这条验不出「服务还挂着旧模块」，所以下面把实际传输方式打印出来。
C = _api.client()

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def post(path: str, payload: dict) -> dict:
    # `timeout` 由 scripts/_api.py 统一处理：真服务会传，ASGI 客户端自动丢掉。
    r = C.post(BASE + path, json=payload, timeout=900)
    r.raise_for_status()
    return r.json()


print("=" * 96)
print("端到端验证")
print(f"传输方式：{_api.MODE}")
print("=" * 96)

# ---------------- ① 只标注，不翻译（快，纯规则） ----------------
print("\n--- ① 标注路径（translate=false）---")
hb = post("/api/analyze-text", {"text": TEXT, "level_id": "cet4",
                                "title": "api-check", "use_llm": False,
                                "translate": False, "trans_mode": "sentence",
                                # 不往用户知识库里灌自检数据。
                                # ⚠ 这条走的是**真服务**，库目录是服务端进程读的
                                # `STUDYPAD_HOME`，自检子进程改自己的环境变量毫无用处 ——
                                # 所以只能靠接口上的 no_save 开关。
                                "no_save": True})
html = hb.get("html") or ""
check(bool(html), "服务返回了 html", f"{len(html)} 字节")
check(".block{break-inside:auto}" in html, "新分页规则已生效（.block 允许断开）")
check(".tr-pair{break-inside:avoid}" in html, "句对不拆页规则已生效")
check(".tr-miss{break-inside:avoid}" in html, "未译出提示也不跨页")
check(".hb-note{" in html, "降级提示条样式已随产物下发")

vocab = hb.get("vocab") or []
check(len(vocab) > 0, "生词表非空", f"{len(vocab)} 词")
miss_p = [v["surface"] for v in vocab if not v.get("phonetic")]
miss_pos = [v["surface"] for v in vocab if not v.get("pos")]
miss_t = [v["surface"] for v in vocab if not v.get("gloss")]
miss_s = [v["surface"] for v in vocab if not v.get("example")]
check(not miss_p, "生词表每行都有音标", f"缺 {miss_p}" if miss_p else "全有")
check(not miss_pos, "生词表每行都有词性", f"缺 {miss_pos}" if miss_pos else "全有")
check(not miss_t, "生词表每行都有释义", f"缺 {miss_t}" if miss_t else "全有")
check(not miss_s, "生词表每行都有例句", f"缺 {miss_s}" if miss_s else "全有")

# ---------------- ② 带翻译（走真模型 / 真缓存） ----------------
print("\n--- ② 翻译路径（translate=true，逐句对照）---")
hb2 = post("/api/analyze-text", {"text": TEXT, "level_id": "cet4",
                                 "title": "api-check", "use_llm": False,
                                 "translate": True, "trans_mode": "sentence",
                                 "no_save": True})
html2 = hb2.get("html") or ""
mode = hb2.get("trans_mode")
note = hb2.get("trans_note") or ""
print(f"       trans_mode={mode}  trans_note={note}")
check(bool(html2), "服务返回了 html", f"{len(html2)} 字节")

boxes = re.findall(r'<div class="tr-zh[^"]*">(.*?)</div>', html2, re.S)
plain = [re.sub(r"<[^>]+>", "", b).strip() for b in boxes]
empty = [t for t in plain if not t]
ph = [t for t in plain if "本句未译出" in t]
print(f"       译文框 {len(boxes)} 个（空 {len(empty)} / 占位 {len(ph)}）")
check(not empty, "没有空的译文框", f"发现 {len(empty)} 个")
check(not ph, "没有「（本句未译出）」占位框", f"发现 {len(ph)} 个")

cov = re.search(r"中文译文 (\d+)/(\d+) 句", html2)
if cov:
    got, tot = int(cov.group(1)), int(cov.group(2))
    print(f"       页眉覆盖率：{got}/{tot} 句")
    check(True, "页眉按句报覆盖率")
    if got < tot:
        check('class="hb-note"' in html2, "覆盖不足时给出了降级提示条")
        check('class="chip warn"' in html2, "覆盖不足时 chip 转为告警色")
    else:
        check('class="hb-note"' not in html2, "覆盖完整时不出告警条（页面保持干净）")
else:
    check(False, "页眉出现了「中文译文 N/M 句」", "没找到")

check(all(ch not in html2 for ch in "\u200b\u200c\u200d\u2060\ufeff"),
      "产物里没有零宽字符")

print()
print("=" * 96)
print(f"结果：{'全部通过' if not FAILS else str(len(FAILS)) + ' 项失败 — ' + '、'.join(FAILS)}")
print("=" * 96)
sys.exit(1 if FAILS else 0)
