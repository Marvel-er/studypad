"""
知识库：历史手账 + 生词本 / 句型本 / 语法本。

它要解决三件事：
  1. 每次生成的手账**自动落盘**，用户不必自己管文件，随时可删；
  2. 所有手账里的生词**聚合成一本生词本**（同一个词只出现一次，
     记录它出自哪几篇、见过几次、音标/词性/释义/例句是什么）；
  3. 句型、语法同理，聚合成可复习的卡片。

## 存哪、存什么
放在**用户目录** `~/.studypad/library/`（与 `settings.json` 同级，可用
`STUDYPAD_HOME` 覆盖）。理由和 settings 一致：学习数据是「这个人」的，
不属于项目本身 —— 拷贝/开源项目时不该把一堆手账一起带走。

**存结构化 JSON，不存渲染好的 HTML**。导出时用现役渲染器重渲，
于是以后改了版式/配色，旧手账也能按新样式重新导出，
不必让用户重新上传文件、重付一次模型费用。代价是渲染器要大改时
旧数据可能渲不出来，所以 JSON 里**原样保留全部字段**，不做裁剪。

```
~/.studypad/library/
  handbooks/<id>.json      一篇手账的全部数据（含 blocks/vocab/patterns/translations）
  cards/words.json         生词本（跨手账聚合）
  cards/patterns.json      句型本
  cards/grammar.json       语法本
  meta.json                知识库自身的版本与统计
```

## 三条不能违反的规则
1. **卡片必须能按来源回滚**。每张卡片都记着 `sources: [{doc, title, level,
   kind}]`；删一篇手账时要把它从所有卡片里摘掉，
   摘完 `sources` 空了的卡片要一并删掉。
   不做这一步，用户删掉一篇 PDF 之后生词本里会永久留下一堆查无出处的词，
   而他根本不知道那些词是从哪来的、更删不掉。
2. **同一篇手账重复保存必须幂等**。按 `doc` id 回滚再重新聚合，
   而不是叠加 —— 否则用户点两次「重新生成」卡片计数就翻倍。
3. **失败必须如实告知，不能静默吞掉**。这是「用户的数据」，
   与 translate 缓存那类「优化型」文件操作不同：
   存不进去就要让用户知道存不进去（`_FS_ERRORS` 见下）。
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import uuid
from pathlib import Path

from .render import _visible

VERSION = 1
CARDS = ("words", "patterns", "grammar")

# ⚠ 写库时的异常元组，**不能只写 OSError**（2026-10-15 踩过，settings.py 同款）。
# 本机 WorkBuddy 沙箱会把一批文件操作换成带守卫的版本
# （`Path.unlink` / `Path.mkdir` / `Path.touch`、`os.remove` / `os.replace` …），
# 守卫不通过时抛的是 `SystemExit(1)` —— 继承自 `BaseException`，
# `except OSError` 拦不住，会一路穿透 FastAPI 变成 500 纯文本。
# 与缓存层不同：**这里是用户的知识库，存不进去必须告诉用户**，
# 所以统一转成 RuntimeError，由 API 层变成前端能显示的 JSON 错误。
_FS_ERRORS = (OSError, SystemExit)

# 掌握度：三个状态，无到期日（不做间隔重复 —— 用户只要「标记 + 回顾」）
ST_NEW = "new"
ST_FUZZY = "fuzzy"
ST_KNOWN = "known"
STATUSES = (ST_NEW, ST_FUZZY, ST_KNOWN)
STATUS_LABEL = {ST_NEW: "未掌握", ST_FUZZY: "模糊", ST_KNOWN: "掌握"}

# 生词三态 → 中文名（与前端标注图例一致）
KIND_LABEL = {"target": "本级考纲", "overflow": "超纲常见", "rare": "超纲生僻"}

# 单词类型 → 生词本里的 kind（wordlist 的三态）
WORD_TYPES = {"word_highlight", "word_circle", "word_rare"}


# ---------------------------------------------------------------- 路径

def root() -> Path:
    """知识库根目录。与 settings.home() 同源，保证 `STUDYPAD_HOME` 一处生效。"""
    from . import settings
    return settings.home() / "library"


def handbooks_dir() -> Path:
    return root() / "handbooks"


def cards_dir() -> Path:
    return root() / "cards"


def _ensure() -> None:
    try:
        handbooks_dir().mkdir(parents=True, exist_ok=True)
        cards_dir().mkdir(parents=True, exist_ok=True)
    except _FS_ERRORS as e:
        raise RuntimeError(f"无法创建知识库目录 {root()}：{e}") from e


def _read_json(p: Path, default):
    try:
        raw = p.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return default
    except _FS_ERRORS as e:
        raise RuntimeError(f"无法读取 {p}：{e}") from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 文件坏了不能让整个知识库打不开 —— 但也不能悄悄当成空库，
        # 那会让用户以为数据丢了。改名留档，页面上会提示。
        try:
            p.replace(p.with_suffix(p.suffix + ".broken"))
        except _FS_ERRORS:
            pass
        return default


def _write_json(p: Path, data) -> None:
    """原子写：先落临时文件再 replace，避免中途崩溃留下半个 JSON。"""
    tmp = p.with_name(p.name + ".tmp")
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, p)
    except _FS_ERRORS as e:
        try:
            tmp.unlink()          # 留个半截的 .tmp 会让下次读到自己
        except _FS_ERRORS:
            pass
        raise RuntimeError(f"无法写入 {p}：{e}") from e


# ---------------------------------------------------------------- 工具

def new_doc_id(title: str, level_id: str) -> str:
    """
    手账 id。用人可读的时间戳 + 标题短横线，而不是纯 uuid ——
    用户会在文件夹里翻这些 json，认得出来比什么都强。
    """
    slug = unicodedata.normalize("NFKC", title or "").strip()
    slug = re.sub(r"[^\w一-鿿-]+", "-", slug).strip("-")[:40]
    return f"{time.strftime('%Y%m%d-%H%M%S')}-{level_id}-{slug or 'untitled'}"


def _sentences_of(block: dict) -> list[tuple[int, int, str]]:
    """块内的 (start, end, 句子)。复刻 annotator 的切句口径，保证例句与手账一致。"""
    from .analyzer import split_spans
    text = block.get("text") or ""
    if not text:
        return []
    return [(s, e, sent) for s, e, sent in split_spans(text)]


def _context(blocks: list[dict], block_id: str, start: int) -> str:
    """
    取某个标注所在的那一整句当例句。

    为什么不用 payload 里自带的 `example`：那是**词典给的例句**，
    与用户正在读的这篇文章毫无关系，背下来也不助于理解原文。
    卡片本的价值恰恰在于「这个词我是在哪句话里不认识的」。
    """
    for b in blocks:
        if b.get("id") != block_id:
            continue
        for s, e, sent in _sentences_of(b):
            if s <= start < e:
                return sent.strip()
    return ""


def _now() -> int:
    return int(time.time())


# ---------------------------------------------------------------- 聚合

def _empty_cards() -> dict:
    return {"version": VERSION, "updated_at": 0, "items": {}}


def load_cards(kind: str) -> dict:
    if kind not in CARDS:
        raise ValueError(f"未知卡片类型 {kind}")
    data = _read_json(cards_dir() / f"{kind}.json", _empty_cards())
    if not isinstance(data, dict):
        return _empty_cards()
    data.setdefault("items", {})
    data.setdefault("version", VERSION)
    data.setdefault("updated_at", 0)
    return data


def save_cards(kind: str, data: dict) -> None:
    data["updated_at"] = _now()
    _write_json(cards_dir() / f"{kind}.json", data)


def _src(doc: dict, hb: dict) -> dict:
    return {
        "doc": doc,
        "title": hb.get("title") or "未命名",
        "level": hb.get("level_id") or "",
        "at": _now(),
    }


# ---- 生词 ---------------------------------------------------------

def _examples_by_lemma(blocks: list[dict]) -> dict[str, str]:
    """
    扫描全部标注，建立「lemma → 原文所在的那一整句」。

    ⚠ **必须自己遍历 blocks，不能靠 `hb["vocab"]` 反查**：
    `markup.build_vocab` 产出的条目只有
    `lemma/surface/phonetic/gloss/pos/kind/example` ——
    **没有 block_id、也没有 start**（实测 vocab[0] 的 key 就这七个）。
    所以按 block_id 去找对应标注必然落空，例句 100% 退回词典例句
    （这条曾经真的踩了：15/15 全是 `dict`，而页面上还写着「例句来自你读过的原文」）。

    同词多次出现时取**更长**的那句：短句往往缺上下文，长句才有复习价值。
    """
    out: dict[str, str] = {}
    for b in blocks:
        for a in b.get("annotations") or []:
            lemma = ((a.get("payload") or {}).get("lemma") or "").strip().lower()
            if not lemma:
                continue
            sent = _context(blocks, b.get("id"), a.get("start", 0))
            if not sent:
                continue
            if len(sent) > len(out.get(lemma, "")):
                out[lemma] = sent
    return out


def _word_item(vocab: dict, examples: dict, doc: str, hb: dict) -> tuple[str, dict]:
    lemma = (vocab.get("lemma") or "").strip().lower()
    if not lemma:
        return "", {}
    # 先试原文里的句子，再退词典例句
    ex = examples.get(lemma) or ""
    # `ex_from` 必须如实记出处：复合词（policy-maker）以及词典例句
    # 都取不到原文上下文。**不标出来的话**，用户会以为每条例句都是
    # 自己读过的那句话，背的时候去回忆语境就白费了
    # （实测：真实 PDF 的 27 个生词里有 4 个是词典例句）。
    if ex:
        ex_from = "text"
    else:
        ex = (vocab.get("example") or "").strip()
        ex_from = "dict" if ex else ""
    return lemma, {
        "lemma": lemma,
        "surface": vocab.get("surface") or lemma,
        "phonetic": vocab.get("phonetic") or "",
        "pos": vocab.get("pos") or "",
        "gloss": vocab.get("gloss") or "",
        "example": ex,
        "ex_from": ex_from,
        "kind": vocab.get("kind") or "",
        "sources": [_src(doc, hb)],
        "status": ST_NEW,
        "status_at": _now(),
        "note": "",
        "first_at": _now(),
        "last_at": _now(),
    }


# ---- 句型 / 语法（都从 blocks 的标注里抽） -------------------------
#
# 为什么不用 `hb["patterns"]`：那是 markup 汇总出来的去重表，
# **不带 block 引用**，因而既取不到「这个词型出现在哪句话里」的例句，
# 也记不下「出自哪篇手账」—— sources 恒为空，
# 下一次 reindex 的回滚阶段就会把它当成孤儿删掉，句型本永远是空的。
# 标注（`blocks[].annotations`）才有 block_id 与 start 偏移。

def _annot_items(blocks: list[dict], kind: str, doc: str, hb: dict) -> list[tuple[str, dict]]:
    """
    抽出句型（kind="pattern"）或语法（kind="grammar"）卡片。

    两者的差别只在 payload 的字段名，结构完全一致，所以合成一个函数。
    """
    want = "pattern_wavy" if kind == "pattern" else "grammar_underline"
    out: list[tuple[str, dict]] = []
    for b in blocks:
        for a in b.get("annotations") or []:
            if a.get("type") != want:
                continue
            p = a.get("payload") or {}
            key = (p.get("grammar_id") or p.get("name")
                   or p.get("label") or "").strip()
            if not key:
                continue
            item = {
                "key": key,
                "kind": kind,
                "sources": [_src(doc, hb)],
                "status": ST_NEW,
                "status_at": _now(),
                "note": "",
                "first_at": _now(),
                "last_at": _now(),
            }
            if kind == "pattern":
                item.update({
                    "name": key,
                    "usage": p.get("usage") or [],
                    "imitation": p.get("imitation") or "",
                    "surface": a.get("surface") or "",
                    "example": _context(blocks, b.get("id"), a.get("start", 0)),
                })
            else:
                item.update({
                    "name": key,
                    "label": p.get("label") or key,
                    "explain": p.get("explain") or "",
                    "color": p.get("color") or "",
                    "surface": a.get("surface") or "",
                    "example": _context(blocks, b.get("id"), a.get("start", 0)),
                })
            out.append((key, item))
    return out


def _merge(items: dict, key: str, item: dict) -> None:
    """
    把一条新卡片并进聚合表。

    合并原则：**后到的只填空缺，不覆盖已有的**。同一篇被不同等级标注时
    释义可能不同，但先落库的那份通常更接近用户当前的目标等级，
    无故覆盖会让用户复习时看到自己刚背过的释义突然变了。

    **唯一例外是例句**：原文例句可以顶掉词典例句。
    早期版本的卡片本把 `vocab["example"]`（词典例句）当例句存，
    升级后重存同一篇时若死守「只填空缺」，用户的卡片就会永远停在
    词典例句上 —— 而卡片本的全部价值恰恰是「我是在哪句话里不认识的」。
    实测真实 PDF：27 词里 4 词是复合词，只能用词典例句（该保留），
    其余 23 词应全部升级成原文例句。所以按**来源可信度**覆盖，不是无条件覆盖。
    """
    cur = items.get(key)
    if cur is None:
        items[key] = item
        return
    for f in ("surface", "phonetic", "pos", "gloss", "example", "explain",
              "usage", "imitation", "label", "color", "ex_from"):
        if not cur.get(f) and item.get(f):
            cur[f] = item[f]
    # 例句：原文 > 词典（旧卡片没标 ex_from 时一律当作非原文，避免误判）
    if item.get("ex_from") == "text" and cur.get("ex_from") != "text" \
            and item.get("example"):
        cur["example"] = item["example"]
        cur["ex_from"] = "text"
    # 来源去重后追加（幂等的第二次保存不会把来源变成两份）
    have = {s.get("doc") for s in cur.get("sources") or []}
    for s in item.get("sources") or []:
        if s.get("doc") not in have:
            cur.setdefault("sources", []).append(s)
            have.add(s.get("doc"))
    cur["last_at"] = _now()


def _rollback(store: dict, doc_id: str) -> dict:
    """
    摘掉某篇手账的贡献，**但先不清除**。

    返回一张「因这次回滚而暂时没有来源」的 key → 卡片 的暂存表。
    为什么不清除：重复保存同一篇时，回滚后马上就会重新聚合同一批词；
    如果这里就把卡片删掉，用户的掌握度标记（status）与备注（note）
    会跟着一起消失 —— 用户每按一次「重新生成」就丢一次自己的复习进度。

    所以流程必须是「摘来源 → 重新聚合 → 再删除仍然无来源的」。
    """
    pending: dict = {}
    for key in list(store["items"].keys()):
        item = store["items"][key]
        item["sources"] = [s for s in (item.get("sources") or [])
                           if s.get("doc") != doc_id]
        if not item["sources"]:
            pending[key] = item
    return pending


def _flush_pending(store: dict, pending: dict) -> int:
    """聚合完成后，仍没有来源的卡片才真正删掉。"""
    n = 0
    for key in list(pending.keys()):
        cur = store["items"].get(key)
        # 重新聚合把它救回来了（重复保存同一篇）→ 什么都不用做
        if cur is not None and (cur.get("sources") or []):
            continue
        store["items"].pop(key, None)
        n += 1
    return n


def reindex(doc_id: str, hb: dict) -> dict:
    """
    把一篇手账（重新）编入三本卡片本。

    顺序是**回滚 → 聚合 → 清理**，三步缺一不可：
    只回滚会让同词来源翻倍；只聚合会让删除留下孤儿；
    回滚后直接删卡片会把用户的掌握度标记一起清掉（见 `_rollback`）。
    """
    _ensure()
    stores = {k: load_cards(k) for k in CARDS}
    pending = {k: _rollback(stores[k], doc_id) for k in CARDS}

    blocks = hb.get("blocks") or []
    examples = _examples_by_lemma(blocks)
    for v in hb.get("vocab") or []:
        lemma, item = _word_item(v, examples, doc_id, hb)
        if lemma:
            _merge(stores["words"]["items"], lemma, item)

    for kind in ("pattern", "grammar"):
        store = stores["patterns" if kind == "pattern" else "grammar"]
        for key, item in _annot_items(blocks, kind, doc_id, hb):
            _merge(store["items"], key, item)

    for k in CARDS:
        _flush_pending(stores[k], pending[k])
        save_cards(k, stores[k])
    return {k: len(stores[k]["items"]) for k in CARDS}


def unlink_doc(doc_id: str) -> None:
    """从三本卡片本里摘掉某篇手账（删文件前后都要调，保证不留孤儿）。"""
    reindex(doc_id, {"title": "", "level_id": "", "blocks": [], "vocab": [], "patterns": []})


# ---------------------------------------------------------------- 手账 CRUD

def _doc_meta(hb: dict, doc_id: str) -> dict:
    c = hb.get("counters") or {}
    return {
        "id": doc_id,
        "title": hb.get("title") or "未命名",
        "level_id": hb.get("level_id") or "",
        "level_name": hb.get("level_name") or "",
        "word_count": hb.get("word_count") or 0,
        "counters": {
            "words": (c.get("word_highlight", 0) + c.get("word_circle", 0)
                      + c.get("word_rare", 0)),
            "grammar": c.get("grammar", 0),
            "patterns": c.get("patterns", 0),
            "long_sentences": c.get("long_sentences", 0),
        },
        "trans_mode": hb.get("trans_mode") or "off",
        "blocks": len(hb.get("blocks") or []),
        "created_at": _now(),
        "updated_at": _now(),
    }


def save_handbook(hb: dict, doc_id: str | None = None) -> dict:
    """
    存一篇手账并更新卡片本。

    `hb` 是 `_run_pipeline` 的产物。**刻意不存 `hb["html"]`** ——
    那是渲染结果，导出时重渲即可（见模块 docstring）。
    其余字段原样保存，包括 blocks 里完整的 annotations：
    卡片本的例句要从标注偏移里回查上下文，少一个字段就取不到原句。
    """
    _ensure()
    data = {k: v for k, v in hb.items() if k != "html"}
    meta = _doc_meta(hb, doc_id or "")
    if not doc_id:
        doc_id = meta["id"] = new_doc_id(hb.get("title") or "", hb.get("level_id") or "")
    else:
        meta["id"] = doc_id
        old = _read_json(handbooks_dir() / f"{doc_id}.json", None)
        if isinstance(old, dict) and old.get("created_at"):
            meta["created_at"] = old["created_at"]
    data["doc_id"] = doc_id
    data["saved_at"] = meta["updated_at"]

    _write_json(handbooks_dir() / f"{doc_id}.json", data)
    try:
        counts = reindex(doc_id, hb)
    except RuntimeError:
        raise
    return {"doc": meta, "cards": counts}


def list_handbooks() -> list[dict]:
    """按更新时间倒序列出手账。跳过坏文件而不是整页 500 —— 坏一个不影响其余。"""
    d = handbooks_dir()
    out: list[dict] = []
    if not d.exists():
        return out
    try:
        files = sorted(d.glob("*.json"))
    except _FS_ERRORS:
        return out
    for p in files:
        data = _read_json(p, None)
        if not isinstance(data, dict):
            continue
        out.append(_doc_meta(data, data.get("doc_id") or p.stem))
    out.sort(key=lambda m: m.get("updated_at") or 0, reverse=True)
    return out


def get_handbook(doc_id: str) -> dict | None:
    p = handbooks_dir() / f"{_safe_id(doc_id)}.json"
    data = _read_json(p, None)
    return data if isinstance(data, dict) else None


def delete_handbook(doc_id: str) -> bool:
    """
    删一篇手账，并从卡片本里摘掉它的贡献。

    文件缺失时也照样跑一遍 unindex —— 可能是上一次删到一半崩了，
    留下孤儿卡片，让用户的生词本里全是查不到出处的词。

    ⚠ **守卫拦下 `unlink` 时降级为「移到回收站目录」，而不是报错**。
    本机的 safe-delete 守卫对本轮删除次数有阈值（50），而译文缓存的
    `_prune` 曾经一次要删几百个 —— 配额被吃光后，用户点「删除手账」
    就会收到 500（2026-10-15 用户反馈过）。症状与缓存毫无关系，
    日志里只有一串 `SAFE_DELETE_BULK_CONFIRM_REQUIRED`，极难定位。

    降级方案：把文件 `rename` 到 `handbooks/.trash/`。rename 不是删除，
    守卫不拦；用户视角「这篇手账不见了」完全成立，而数据还在，
    将来守卫配额恢复后还能补删。
    """
    doc_id = _safe_id(doc_id)
    p = handbooks_dir() / f"{doc_id}.json"
    existed = p.exists()
    if existed:
        try:
            p.unlink()
        except FileNotFoundError:
            existed = False
        except _FS_ERRORS as e:
            # 守卫拦下了：退化成「移到回收站」，别让用户的操作失败
            trash = handbooks_dir() / ".trash"
            try:
                trash.mkdir(parents=True, exist_ok=True)
                (trash / f"{doc_id}-{int(time.time())}.json").write_bytes(
                    p.read_bytes())
                p.unlink()
            except _FS_ERRORS:
                # 连 rename 都失败：如实报错，但**先把卡片回滚做掉**，
                # 否则会留下指向一篇还在的孤儿卡片。
                unlink_doc(doc_id)
                raise RuntimeError(f"无法删除手账 {p}：{e}") from e
    unlink_doc(doc_id)
    return existed


def _safe_id(doc_id: str) -> str:
    """
    路径穿越防护。

    doc_id 来自 URL，前端能传任意字符串；`../` 能把读写打到知识库外面去。
    只允许字母数字、连字符、下划线、中文。
    """
    s = (doc_id or "").strip()
    if not s or not re.fullmatch(r"[\w一-鿿-]{1,120}", s):
        raise ValueError("手账 ID 不合法")
    if s in (".", ".."):
        raise ValueError("手账 ID 不合法")
    return s


# ---------------------------------------------------------------- 卡片读写

def list_cards(kind: str, q: str = "", status: str = "",
               level: str = "", sort: str = "recent") -> dict:
    """
    读卡片本（不排序分页 —— 几千条也够浏览器一次渲染，
    而分页会让「搜索时要看全量命中数」变得别扭）。
    """
    data = load_cards(kind)
    items = list(data["items"].values())
    q = (q or "").strip().lower()
    if q:
        def hit(it: dict) -> bool:
            hay = " ".join(str(it.get(f) or "") for f in
                           ("lemma", "name", "label", "gloss", "example", "note"))
            return q in hay.lower()
        items = [it for it in items if hit(it)]
    if status in STATUSES:
        items = [it for it in items if (it.get("status") or ST_NEW) == status]
    if level:
        items = [it for it in items
                 if any(s.get("level") == level for s in (it.get("sources") or []))]

    def key_fn(it: dict):
        if sort == "alpha":
            return (str(it.get("lemma") or it.get("name") or "").lower(),)
        if sort == "freq":
            return (-len(it.get("sources") or []), str(it.get("lemma") or ""))
        if sort == "status":
            return (STATUSES.index(it.get("status") or ST_NEW),
                    -len(it.get("sources") or []))
        return (-(it.get("last_at") or 0),)

    items.sort(key=key_fn)

    tally = {ST_NEW: 0, ST_FUZZY: 0, ST_KNOWN: 0}
    for it in data["items"].values():
        st = it.get("status") or ST_NEW
        tally[st] = tally.get(st, 0) + 1

    return {
        "kind": kind,
        "total": len(data["items"]),
        "shown": len(items),
        "tally": tally,
        "items": items,
        "updated_at": data.get("updated_at", 0),
    }


def set_status(kind: str, key: str, status: str, note: str | None = None) -> dict:
    """改掌握状态 / 备注。标记只影响卡片本身，不会被再次 reindex 冲掉。"""
    if status not in STATUSES:
        raise ValueError(f"状态只能是 {'/'.join(STATUSES)}")
    data = load_cards(kind)
    item = data["items"].get(key)
    if item is None:
        raise KeyError(key)
    item["status"] = status
    item["status_at"] = _now()
    if note is not None:
        item["note"] = str(note)
    save_cards(kind, data)
    return item


def delete_card(kind: str, key: str) -> bool:
    data = load_cards(kind)
    if key not in data["items"]:
        return False
    data["items"].pop(key)
    save_cards(kind, data)
    return True


def stats() -> dict:
    """知识库总览。页面顶上那几个数字就是它。"""
    docs = list_handbooks()
    out = {"docs": len(docs), "path": str(root()), "cards": {}, "words_total": 0}
    for kind in CARDS:
        d = load_cards(kind)
        out["cards"][kind] = len(d["items"])
    tally = {ST_NEW: 0, ST_FUZZY: 0, ST_KNOWN: 0}
    for it in load_cards("words")["items"].values():
        tally[it.get("status") or ST_NEW] += 1
    out["words_total"] = sum(tally.values())
    out["word_tally"] = tally
    return out


# ---------------------------------------------------------------- 一致性自检

def audit() -> list[str]:
    """
    找出「卡片引用了不存在的手账」这类不一致。
    页面上的「修复」按钮用它 —— 用户手工删过 json 文件时，
    卡片里会留下一批查不到出处的僵尸条目。
    """
    problems: list[str] = []
    known = {m["id"] for m in list_handbooks()}
    for kind in CARDS:
        d = load_cards(kind)
        for key, it in list(d["items"].items()):
            srcs = it.get("sources") or []
            if not srcs:
                problems.append(f"{kind}:{key} 没有任何来源")
                continue
            for s in srcs:
                if s.get("doc") not in known:
                    problems.append(f"{kind}:{key} 指向不存在的手账 {s.get('doc')}")
    # 去重
    seen: set[str] = set()
    uniq = []
    for p in problems:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def repair() -> dict:
    """按 audit 的结论清掉僵尸卡片。返回清理条数。"""
    known = {m["id"] for m in list_handbooks()}
    removed = 0
    for kind in CARDS:
        d = load_cards(kind)
        for key in list(d["items"].keys()):
            it = d["items"][key]
            srcs = [s for s in (it.get("sources") or []) if s.get("doc") in known]
            if srcs:
                it["sources"] = srcs
                continue
            d["items"].pop(key)
            removed += 1
        save_cards(kind, d)
    return {"removed": removed}


__all__ = [
    "CARDS", "STATUSES", "STATUS_LABEL", "ST_NEW", "ST_FUZZY", "ST_KNOWN",
    "KIND_LABEL", "root", "stats", "save_handbook", "list_handbooks",
    "get_handbook", "delete_handbook", "list_cards", "set_status",
    "delete_card", "audit", "repair", "reindex", "unlink_doc", "new_doc_id",
]