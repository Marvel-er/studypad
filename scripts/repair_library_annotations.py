"""把知识库里**已有**的手账按当前规则重新标注一遍。

为什么需要单独一个脚本：
- `/api/library/repair` 只清「僵尸卡片」，不会重跑标注；
- 而词形还原、词典层、断词规则（`--` 这类）的修复只影响**新生成**的手账 ——
  用户手里已经存下的那几篇，生词表里那几行空着的、或者词头写着
  `anticipation--anticipation` 的行会一直是坏的。

本脚本用同样的原文重算一遍，用户不必重新上传、也不必重付模型的钱。

会**保留**的：
  · 中文译文 `translations`（按句哈希缓存，不重翻、不花钱）
  · 大模型写的语法讲解 `payload.explain`：按 `block_id:start` 这个键原样贴回新标注上
    （这个键就是 `_enrich_with_llm` 用的键，所以能对上）
  · 标题 / 等级 / 时间戳 / 讲解模型与翻译模型的记录
会**重算**的：blocks 里的标注、vocab、counters、patterns、raw_counters、budget。

安全：先整目录备份到 `out/_library_backup_<时间戳>/`，再逐篇覆盖；
`library.save_handbook` 内部会走 reindex 的回滚→聚合→清理，
所以旧的错误卡片（比如 `anticipation--anticipation`）会被摘掉，
而用户标过的「已掌握 / 模糊」状态不受影响。
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, library, markup  # noqa: E402


def _empty_rows(vocab: list[dict]) -> list[dict]:
    """音标或释义缺其一的行（就是用户说的「信息没有完全显示」）。"""
    return [v for v in vocab if not (v.get("phonetic") and v.get("gloss"))]


def _dash_rows(vocab: list[dict]) -> list[dict]:
    """词头里带 `--` 的行（断词没做好时的产物）。"""
    return [v for v in vocab if "--" in (v.get("surface") or "")]


def main() -> int:
    d = library.handbooks_dir()
    files = sorted(d.glob("*.json")) if d.exists() else []
    if not files:
        print(f"知识库里没有手账（{d}）")
        return 0

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "out" / f"_library_backup_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, backup / f.name)
    print(f"已备份 {len(files)} 篇 → {backup}\n")

    problems = 0
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        doc_id = rec.get("doc_id") or f.stem
        level_id = rec.get("level_id") or "cet4"

        # 1) 先把大模型写的讲解按 `block_id:start` 存下来
        explains: dict[str, str] = {}
        for b in rec.get("blocks") or []:
            for c in b.get("candidates") or []:
                ex = ((c.get("payload") or {}).get("explain") or "").strip()
                if ex:
                    explains[f'{b["id"]}:{c.get("start")}'] = ex

        # 2) 用原文重跑标注（只喂 id/type/text/meta，丢掉旧标注）
        raw = [{"id": b["id"], "type": b.get("type"),
                "text": b.get("text") or "", "meta": b.get("meta") or {}}
               for b in rec.get("blocks") or []]
        if not raw:
            print(f"  跳过 {doc_id}：没有 blocks")
            continue
        parsed = annotator.analyze_document(raw, level_id)

        # 3) 把讲解贴回去（键对不上的就丢，绝不乱贴）
        n_back = 0
        for b in parsed["blocks"]:
            for c in b.get("candidates") or []:
                key = f'{b["id"]}:{c.get("start")}'
                ex = explains.get(key)
                if ex:
                    (c.setdefault("payload", {}))["explain"] = ex
                    n_back += 1

        # 4) 重建手账，保留不该重算的字段
        hb = markup.build(parsed, level_id)
        for k in ("title", "llm_note", "llm_model", "mt_model",
                  "trans_mode", "trans_note", "translations"):
            if k in rec:
                hb[k] = rec[k]

        before_empty, after_empty = _empty_rows(rec.get("vocab") or []), _empty_rows(hb["vocab"])
        before_dash, after_dash = _dash_rows(rec.get("vocab") or []), _dash_rows(hb["vocab"])
        print(f"  {doc_id}")
        print(f"    生词表 {len(rec.get('vocab') or [])} → {len(hb['vocab'])} 行")
        print(f"    词头带 `--` 的行   {len(before_dash)} → {len(after_dash)}"
              f"{'  ' + str([v['surface'] for v in before_dash]) if before_dash else ''}")
        print(f"    信息不全的行       {len(before_empty)} → {len(after_empty)}"
              f"{'  ' + str([v['surface'] for v in after_empty]) if after_empty else ''}")
        print(f"    贴回大模型讲解     {n_back}/{len(explains)} 处")

        library.save_handbook(hb, doc_id)
        if after_dash or len(after_empty) > len(before_empty):
            problems += 1

    print(f"\n完成：{len(files)} 篇已重新标注，回滚备份在 {backup}")
    if problems:
        print(f"⚠ 仍有 {problems} 篇存在未修好的行，见上面明细")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
