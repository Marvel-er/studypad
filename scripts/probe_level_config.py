"""探针：六档能力画像里的参数，是否每一个都真的被代码消费。

为什么值得单独写：`levels.py` 的设计承诺是「切换等级 = 换一份参数，不改任何代码」。
这个承诺成立的前提是**每个参数都真的有接线**。一旦某个键只写不读，
它就从「可调参数」退化成「装饰性注释」—— 有人照着调它，页面不会有任何变化，
而这种失效是**完全静默**的（不报错、不告警、测试也照样全绿）。

已查实的两个死键（2026-10-14）：
  · `grammar_density`（0.75 / 0.6 / 0.45 / 0.4 / 0.3 / 0.2）
    —— 注释写「每句被语法标注的概率上限系数」，但 `markup.select` 只读
       `grammar_max_per_para`，从没人读它。
  · `explain`（"zh" / "bi" / "en"）
    —— ielts 声明「双语讲解」、toefl 声明「英文讲解」，
       但 `patterns.explainat` 只返回中文文本，这个字段从没被读过。

这里把「键被声明」和「键被读取」两边都对上，漏一个就报错。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.levels import LEVELS  # noqa: E402

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# 每个等级自己独有的、不参与逻辑的展示性字段 —— 这些只被序列化出去，不算死键
DISPLAY_ONLY = {"id", "name", "en", "bit"}

# 已知的、**登记在案**的死键。放在这里而不是静默放过，是为了让
# 「我们知道它没接线」这件事有据可查；同时防止新的死键悄悄混进来
# （不在这个表里的键一旦只写不读，探针立刻红）。
#
# 两笔都记在案、等产品决策，没有偷偷改数据撒谎：
#   · grammar_density —— 注释说「每句被语法标注的概率上限系数」，
#     但 markup.select 只读 grammar_max_per_para。要接的话得先决定
#     「按句数封顶」和「按段封顶」哪个优先，会改变现有标注密度，需重新做视觉核验。
#   · explain —— ielts 声明 "bi"（双语）、toefl 声明 "en"（英文），
#     但 patterns.py 的 explain_map 里**只有中文文本**，没有可显示的英文内容。
#     要么补一套英文讲解（内容工作），要么把配置改回 "zh"（承认现状）。
KNOWN_GAPS = {
    "grammar_density": "只写不读；接线需先定「按句封顶 vs 按段封顶」的优先级",
    "explain": "只有中文讲解文本，bi/en 无可显示内容；待补英文讲解或改回 zh",
}

# 全部后端源码（用于判断某个键是否被真正读取）
SRC = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                for p in sorted((BACKEND / "app").glob("*.py"))
                if p.name != "levels.py")

keys: list[str] = []
for lv in LEVELS:
    for k in lv:
        if k not in keys:
            keys.append(k)

out.append(f"六档共声明 {len(keys)} 个参数：")
for k in keys:
    # 只认「从等级对象读」的用法：lv["k"] / level["k"] / lv.get("k")。
    # 不能宽泛地匹配 `["k"]` —— 那会把 payload 里同名的字典键也算成接线
    # （`explain` 就是这样被漏掉的：`g["explain"]` 是语法讲解内容，
    #  而等级上的 `explain`（"zh"/"bi"/"en"）其实从没被读过）。
    esc = re.escape(k)
    n_read = len(re.findall(rf'\b(?:lv|level|_lv|_level|L)\s*\[\s*"{esc}"\s*\]', SRC))
    n_get = len(re.findall(rf'\b(?:lv|level|_lv|_level|L)\s*\.\s*get\(\s*"{esc}"', SRC))
    used = (n_read + n_get) > 0
    if used:
        tag = "仅展示" if k in DISPLAY_ONLY else f"被读 {n_read} 处 / .get {n_get} 处"
    elif k in KNOWN_GAPS:
        tag = f"已知缺口（登记在案）：{KNOWN_GAPS[k]}"
    elif k in DISPLAY_ONLY:
        tag = "仅展示"
    else:
        tag = "死键（从没被读过，且未登记）"
    out.append(f"  {k:<26} {tag}")
    if not used and k not in KNOWN_GAPS and k not in DISPLAY_ONLY:
        check(False, f"参数 {k} 有接线（不是死配置）", "只写不读，也未登记进 KNOWN_GAPS")

# 登记在案的缺口要如实列出，不能只藏在代码里
out.append("")
for k, why in KNOWN_GAPS.items():
    out.append(f"  [登记] {k}：{why}")
    check(k in keys, f"登记的缺口 {k} 仍然存在于 LEVELS（没被偷偷删掉）")

out.append("")
# 反向：别把「展示性字段」也一并要求有接线，那会是错报
for k in DISPLAY_ONLY:
    check(k in keys, f"展示性字段 {k} 仍然保留在 LEVELS 里")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
