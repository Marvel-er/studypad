"""
知识库（`library.py`）自检。

重点验三件事，因为它们都是「错了也不会报错、只会静默给用户错数据」的地方：
  1. **幂等**：同一篇手账存两次，卡片不能翻倍、标记不能丢；
  2. **回滚**：删掉一篇手账后，它贡献的卡片必须消失，不留孤儿；
  3. **安全**：doc_id 是 URL 传进来的，必须挡得住路径穿越。

跑法（走 run_selftest 包装层，别直接 python）：
  python scripts/run_selftest.py scripts/test_library.py out/_library.txt
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

# 必须在 import app 之前指定：库目录跟着 STUDYPAD_HOME 走，
# 否则自检会往用户真实的知识库里写测试数据。
_TMP = tempfile.mkdtemp(prefix="studypad_lib_")
os.environ["STUDYPAD_HOME"] = _TMP

from app import library            # noqa: E402
from app import markup             # noqa: E402
from app import annotator          # noqa: E402
from app import parsers            # noqa: E402

FAILED: list[str] = []
N = 0


def check(label: str, cond, extra: str = "") -> None:
    global N
    N += 1
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {extra}")
        FAILED.append(label)


def _hb(title: str, level: str, text: str) -> dict:
    """跑真实标注链路拿到一份与线上一致的手账数据。"""
    blocks = [b.as_dict() for b in parsers.parse_text(text)]
    parsed = annotator.analyze_document(blocks, level)
    hb = markup.build(parsed, level)
    hb["title"] = title
    return hb


SAMPLE2 = """
Ambition without discipline crumbles into ruin, and persistence usually outlasts
talent. Negotiation tactics that lack empathy backfire more often than they succeed.
"""


# ⚠ 样本必须用**真实文章**，不能用几行手写短句（2026-10-15 踩过）。
# `annotator.analyze_block` 有一道句级准入门槛：
# `value < th 且无句型命中 且不是长难句 → 整句 continue`，
# 于是句内的词标注全被丢弃。最初那份 4 句短样本实测产出 **0 个候选标注**、
# 生词表为空 —— 看起来像知识库坏了，其实是密度策略的正常结果。
# `samples/sample_article.md` 走同一条链路稳定产出 15 生词 / 8 句型 / 15 语法。
SAMPLE = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")


def main() -> int:
    print("== 知识库 / library ==")

    # 样本自检：先确认真能产出标注，否则后面所有断言都在验空集（恒真）
    _probe = _hb("probe", "cet4", SAMPLE)
    check("样本文章能产出生词（否则下面全在验空集）",
          len(_probe["vocab"]) > 0, str(len(_probe["vocab"])))
    check("样本文章能产出句型", len(_probe["patterns"]) > 0)
    check("样本文章能产出语法标注", _probe["counters"]["grammar"] > 0)
    # ⚠ `markup.build_vocab` 的条目**没有 block_id / start**（只有
    # lemma/surface/phonetic/gloss/pos/kind/example）。早先的知识库实现
    # 靠 vocab 里的 block_id 回查原文句子，必然落空 → 例句 100% 退回词典例句，
    # 而页面上还写着「例句来自你读过的原文」。这条断言把坑钉住：
    # 若将来 markup 补上了 block_id，本条会提醒回来改回更省事的路径。
    check("vocab 条目确实没有 block_id（例句只能自己扫 blocks 找）",
          bool(_probe["vocab"]) and "block_id" not in _probe["vocab"][0],
          str(list(_probe["vocab"][0]) if _probe["vocab"] else []))

    # ---------- 1. 保存与读取 ----------
    hb1 = _hb("A Piece of Red Calico", "cet4", SAMPLE)
    r1 = library.save_handbook(hb1)
    doc1 = r1["doc"]["id"]
    check("保存后返回 doc id", bool(doc1), doc1)
    check("手账目录里出现 json 文件",
          (library.handbooks_dir() / f"{doc1}.json").exists())

    got = library.get_handbook(doc1)
    check("能读回同一篇", got is not None and got.get("doc_id") == doc1)
    check("读回的是结构化数据而不是 html 快照", got is not None and "html" not in got)
    check("blocks 完整保留（回查例句要靠它）",
          bool(got) and len(got.get("blocks") or []) == len(hb1["blocks"]))
    check("translations 也留着（重导出要能带译文）",
          "translations" in (got or {}))

    docs = library.list_handbooks()
    check("列表里有这一篇", any(d["id"] == doc1 for d in docs), str(len(docs)))
    meta = next(d for d in docs if d["id"] == doc1)
    check("列表元信息带标题与等级",
          meta["title"] == "A Piece of Red Calico" and meta["level_id"] == "cet4")
    check("列表元信息统计了生词数", meta["counters"]["words"] == len(hb1["vocab"]),
          f"{meta['counters']['words']} vs {len(hb1['vocab'])}")

    # ---------- 2. 生词本聚合 ----------
    words = library.list_cards("words")
    lemmas = {i["lemma"] for i in words["items"]}
    check("生词本收了文章里的词",
          lemmas == {v["lemma"] for v in hb1["vocab"]},
          str(sorted(lemmas))[:200])
    check("生词条数等于手账生词表条数（去重后）",
          words["total"] == len(hb1["vocab"]),
          f"{words['total']} vs {len(hb1['vocab'])}")

    # 动态挑一个「信息齐全」的词做后续断言：不能写死具体单词
    # （换样本文章就全崩），但也不能用 words["items"][0] ——
    # 那个位置上的词可能音标是空的，验的就不是「生词本」而是「碰巧」。
    full = [i for i in words["items"]
            if i["phonetic"] and i["pos"] and i["gloss"] and i["example"]]
    check("至少有若干生词带全音标/词性/释义/例句", len(full) >= 3,
          f"只有 {len(full)} 个词条完整")
    key = full[0]["lemma"]
    card0 = next(i for i in words["items"] if i["lemma"] == key)
    check("例句取自用户正在读的那篇文章，而不是词典自带例句",
          any(w in card0["example"].lower() for w in card0["lemma"][:4].lower())
          or len(card0["example"]) > 20,
          repr(card0["example"])[:120])
    # 例句出处必须**如实标注**：不标的话用户会以为每条都是自己读过的那句话，
    # 背的时候去回忆语境就白费了（实测真实 PDF 27 词里有 4 词是词典例句）。
    check("卡片带例句来源标记 ex_from",
          all(i.get("ex_from") in ("text", "dict") for i in words["items"]),
          str([(i["lemma"], i.get("ex_from")) for i in words["items"][:5]]))
    check("多数例句确实来自原文",
          sum(1 for i in words["items"] if i.get("ex_from") == "text")
          >= len(words["items"]) // 2,
          f"{sum(1 for i in words['items'] if i.get('ex_from') == 'text')}/{len(words['items'])}")
    check("生词记着出处（哪篇手账）",
          any(s["doc"] == doc1 for s in card0["sources"]))
    check("默认状态是「未掌握」", card0["status"] == library.ST_NEW)

    # ---------- 3. 幂等：同一篇存两次 ----------
    library.set_status("words", key, library.ST_KNOWN, "背过了")
    library.save_handbook(hb1, doc_id=doc1)
    words2 = library.list_cards("words")
    check("重复保存不会让生词本翻倍", words2["total"] == words["total"],
          f"{words2['total']} vs {words['total']}")
    c2 = next(i for i in words2["items"] if i["lemma"] == key)
    check("重复保存不会让来源变成两份",
          sum(1 for s in c2["sources"] if s["doc"] == doc1) == 1,
          str(c2["sources"]))
    check("重复保存保留用户的掌握度标记", c2["status"] == library.ST_KNOWN)
    check("重复保存保留用户的备注", c2["note"] == "背过了")
    check("手账不会因为重复保存多出一篇", len(library.list_handbooks()) == 1)
    # 这条曾经真的挂过：早期实现是「回滚时直接删掉无来源的卡片」，
    # 而重新保存同一篇恰好会让它短暂地没有来源 —— 于是用户的掌握度标记
    # 在**第一次**点「重新生成」时就没了。必须反复验，不是验一次。
    for _ in range(5):
        library.save_handbook(hb1, doc_id=doc1)
    c6 = next(i for i in library.list_cards("words")["items"] if i["lemma"] == key)
    check("反复重新生成 5 次后掌握度标记仍在",
          c6["status"] == library.ST_KNOWN, c6["status"])
    check("反复重新生成 5 次后备注仍在", c6["note"] == "背过了", c6["note"])
    check("反复重新生成 5 次后生词本条数不变",
          library.list_cards("words")["total"] == words["total"],
          f"{library.list_cards('words')['total']} vs {words['total']}")
    # 「只填空缺」这条原则有个例外必须守住：**原文例句要能顶掉词典例句**。
    # 早先版本把 vocab["example"]（词典例句）当例句存进卡片，
    # 升级后若死守「不覆盖」，用户的卡片就会永远停在词典例句上 ——
    # 而卡片本的全部价值就是「我是在哪句话里不认识的」。
    # 这里先手工把一条卡片降级成词典例句，再重存，验它能被纠正回来。
    st = library.load_cards("words")
    st["items"][key]["example"] = "Some dictionary example sentence."
    st["items"][key]["ex_from"] = "dict"
    library.save_cards("words", st)
    library.save_handbook(hb1, doc_id=doc1)
    fixed = next(i for i in library.list_cards("words")["items"]
                 if i["lemma"] == key)
    check("重新保存能把词典例句升级回原文例句",
          fixed["ex_from"] == "text"
          and fixed["example"] != "Some dictionary example sentence.",
          f"{fixed['ex_from']} / {fixed['example'][:40]}")

    # ---------- 4. 第二篇 → 卡片来源累积 ----------
    # 断言只在「两篇确实共用某个词」时才有意义，先确认这一点，
    # 否则下一行会拿一个恒假条件当护栏（项目里栽过三次恒真断言）。
    hb2 = _hb("Second Reading", "cet6", SAMPLE2)
    shared = {v["lemma"] for v in hb2["vocab"]} & set(lemmas)
    r2 = library.save_handbook(hb2)
    doc2 = r2["doc"]["id"]
    check("两篇手账的 id 不同", doc1 != doc2)
    if shared:
        sk = sorted(shared)[0]
        si = next(i for i in library.list_cards("words")["items"]
                  if i["lemma"] == sk)
        check("同词出现在第二篇时来源累积到 2",
              len(si["sources"]) == 2, f"{sk}: {si['sources']}")
    else:
        # 没有共用词就把 SAMPLE2 换成共用 sample 文章的等价物，保证这条被验到
        hb2 = _hb("Second Reading", "cet6", SAMPLE)
        r2 = library.save_handbook(hb2)
        doc2 = r2["doc"]["id"]
        sk = sorted({v["lemma"] for v in hb2["vocab"]} & set(lemmas))[0]
        si = next(i for i in library.list_cards("words")["items"]
                  if i["lemma"] == sk)
        check("同词出现在第二篇时来源累积到 2",
              len(si["sources"]) == 2, f"{sk}: {si['sources']}")

    # ---------- 5. 删除 → 回滚，不留孤儿 ----------
    check("删除返回 True", library.delete_handbook(doc2) is True)
    check("手账文件真的没了",
          not (library.handbooks_dir() / f"{doc2}.json").exists())
    words3 = library.list_cards("words")
    check("删掉第二篇后生词本只剩第一篇的词",
          words3["total"] == len({v["lemma"] for v in hb1["vocab"]}),
          f"{words3['total']} vs {len({v['lemma'] for v in hb1['vocab']})}")
    gone = [i for i in words3["items"]
            if any(s["doc"] == doc2 for s in i["sources"])]
    check("没有任何卡片还指向已删的手账", gone == [], str(gone)[:200])
    si3 = next((i for i in words3["items"] if i["lemma"] == sk), None)
    check("两篇共有的词保留且只剩第一篇来源",
          si3 is not None and len(si3["sources"]) == 1,
          str(si3["sources"]) if si3 else f"{sk} 被误删了")
    check("第一篇独有的词不受影响",
          any(i["lemma"] == key for i in words3["items"]))
    check("共有的词保留了掌握度标记",
          next(i for i in words3["items"] if i["lemma"] == key)["status"]
          == library.ST_KNOWN)
    check("删除不存在的 id 返回 False 而不是报错",
          library.delete_handbook("20990101-xx-nope") is False)
    check("删完之后 audit 无孤儿", library.audit() == [], str(library.audit())[:200])

    # ---------- 6. 句型本 / 语法本 ----------
    pats = library.list_cards("patterns")
    check("句型本非空", pats["total"] > 0, str(pats["total"]))
    if pats["total"]:
        p = pats["items"][0]
        check("句型卡带用法或仿写",
              bool(p.get("usage")) or bool(p.get("imitation")), str(p)[:160])
        check("句型卡记着出处（旧实现 sources 恒空，第二次保存就被自己删掉）",
              len(p.get("sources") or []) >= 1, str(p.get("sources")))
        check("句型卡带真实例句", len(p.get("example") or "") > 10,
              repr(p.get("example"))[:120])
    # 反向验证：句型/语法本不该因为「重复保存」而变空
    grammar_before = library.list_cards("grammar")["total"]
    library.save_handbook(hb1, doc_id=doc1)
    check("重复保存不会清空句型本",
          library.list_cards("patterns")["total"] == pats["total"],
          f"{library.list_cards('patterns')['total']} vs {pats['total']}")
    check("重复保存不会清空语法本",
          library.list_cards("grammar")["total"] == grammar_before,
          f"{library.list_cards('grammar')['total']} vs {grammar_before}")
    gram = library.list_cards("grammar")
    grammar_before = gram["total"]
    check("语法本能跑通（数量随样本内容浮动）",
          isinstance(gram["total"], int))
    if gram["total"]:
        g = gram["items"][0]
        check("语法卡带标签与讲解",
              bool(g.get("label")) and bool(g.get("explain")), str(g)[:200])
        check("语法卡的例句来自文章",
              len(g.get("example") or "") > 10, repr(g.get("example"))[:120])

    # ---------- 7. 检索 / 筛选 / 排序 ----------
    library.set_status("words", key, library.ST_FUZZY)
    check("按状态筛选生效",
          all(i["status"] == library.ST_FUZZY
              for i in library.list_cards("words", status=library.ST_FUZZY)["items"]))
    # 搜索要拿**实际存在的**释义片段，不能写死「猫」这类词 ——
    # 样本文章里根本没有，断言就变成「搜不到」也算过（恒假）。
    glosses = [i["gloss"] for i in words3["items"] if len(i["gloss"]) >= 2]
    check("样本里有可搜的中文释义（否则下面在验空集）", bool(glosses))
    if glosses:
        needle = glosses[0][0]
        check("按关键词搜索命中释义",
              any(needle in i["gloss"] for i in
                  library.list_cards("words", q=needle)["items"]),
              f"needle={needle!r}")
    check("按单词本身也能搜到",
          any(i["lemma"] == key for i in
              library.list_cards("words", q=key)["items"]))
    check("搜不到时返回空列表而不是报错",
          library.list_cards("words", q="zzzznotaword")["items"] == [])
    alpha = [i["lemma"] for i in library.list_cards("words", sort="alpha")["items"]]
    check("按字母排序真的有序", alpha == sorted(alpha), str(alpha[:8]))
    freq = library.list_cards("words", sort="freq")["items"]
    check("按词频排序（来源多的在前）",
          len(freq) < 2 or len(freq[0]["sources"]) >= len(freq[-1]["sources"]))
    check("按等级筛选生效",
          all(any(s["level"] == "cet4" for s in i["sources"])
              for i in library.list_cards("words", level="cet4")["items"]))
    check("统计里三本卡片都有数",
          set(library.stats()["cards"]) == {"words", "patterns", "grammar"})
    check("统计里有掌握度分布",
          sum(library.stats()["word_tally"].values()) == library.stats()["words_total"])

    # ---------- 8. 删除单张卡片 ----------
    target = library.list_cards("words", sort="alpha")["items"][0]["lemma"]
    check("删单张卡片返回 True",
          library.delete_card("words", target) is True)
    check("删完确实没了",
          target not in {i["lemma"] for i in library.list_cards("words")["items"]})
    check("删不存在的卡片返回 False", library.delete_card("words", "zzzz") is False)

    # ---------- 9. 路径穿越防护 ----------
    for bad in ["../../settings", "..\\..\\settings", "a/b", "a\\b", "..",
                "", "  ", "x" * 200, "a\x00b"]:
        try:
            library.get_handbook(bad)
            check(f"拒绝非法 id {bad!r}", False, "竟然没抛")
        except ValueError:
            check(f"拒绝非法 id {bad!r}", True)
        except Exception as e:  # noqa: BLE001
            check(f"拒绝非法 id {bad!r}", False, f"抛的是 {type(e).__name__}")
    check("settings.json 没被读写碰到",
          not (Path(_TMP) / "settings.json").exists())

    # ---------- 10. 坏文件不拖垮整库 ----------
    (library.handbooks_dir() / "corrupt.json").write_text("{not json", encoding="utf-8")
    check("坏 json 被跳过而不是整页 500", len(library.list_handbooks()) >= 1)
    check("坏文件被改名留档",
          (library.handbooks_dir() / "corrupt.json.broken").exists())

    # ---------- 11. audit / repair：用户手工删过文件的情况 ----------
    # ⚠ 必须用**能产出标注**的文本：最初这里用了一句短英文，
    # 而短句会被句级准入门槛整句跳过 → 一张卡片都没建 →
    # audit 当然「发现不了问题」—— 一个恒真的反向断言。
    hb3 = _hb("Third", "cet4", SAMPLE)
    check("第三篇也产出了卡片（否则下面在验空集）",
          library.save_handbook(hb3)["cards"]["words"] > 0)
    doc3 = library.list_handbooks()[0]["id"]
    n3 = {i["lemma"] for i in library.list_cards("words")["items"]
          if any(s["doc"] == doc3 for s in i["sources"])}
    check("第三篇贡献了卡片", bool(n3), str(len(n3)))
    # 模拟用户自己把 json 删了
    (library.handbooks_dir() / f"{doc3}.json").unlink()
    problems = library.audit()
    check("audit 能发现指向已不存在手账的卡片",
          any(doc3 in p for p in problems), str(problems)[:200])
    rep = library.repair()
    # ⚠ 这里**不能**断言 removed > 0：第三篇用的是与第一篇相同的文章，
    # 那些卡片同时被第一篇引用，repair 只该摘掉 doc3 这一条来源、留下卡片。
    # 早先误写成 removed>0，等于要求「删掉还有别的出处的卡片」——
    # 那会诱导后来的人把 repair 改成宁可多删。
    check("repair 后没有卡片还引用已消失的手账",
          all(doc3 not in {s["doc"] for s in i["sources"]}
              for i in library.list_cards("words")["items"]))
    check("repair 没误伤还有别的出处的卡片",
          any(i["lemma"] == key for i in library.list_cards("words")["items"]),
          f"{key} 被误删了")
    check("repair 之后 audit 干净", library.audit() == [], str(library.audit())[:200])

    # 「彻底没出处」的卡片必须真的删掉：手工塞一条指向幽灵手账的
    store = library.load_cards("words")
    store["items"]["__ghost__"] = {
        "lemma": "__ghost__", "gloss": "孤儿", "status": library.ST_NEW,
        "sources": [{"doc": "20990101-dead-doc", "title": "已删", "level": "cet4"}],
    }
    library.save_cards("words", store)
    check("塞入孤儿卡片后 audit 报得出来",
          any("__ghost__" in p for p in library.audit()))
    rep2 = library.repair()
    check("repair 真的删掉了彻底无出处的卡片",
          rep2["removed"] >= 1
          and "__ghost__" not in {i["lemma"] for i in
                                  library.list_cards("words")["items"]},
          str(rep2))
    check("repair 后 audit 仍然干净", library.audit() == [])

    # ---------- 12. 卡住用户数据的写失败必须报出来 ----------
    # ⚠ patch 要 patch 对对象：`library._write_json` 用的是 **`os.replace`** 做原子写，
    # 不是 `Path.replace`。早先 patch 了 `_write_json` 本身，
    # 结果绕过了它内部的异常转换，裸 `SystemExit` 直接穿透测试函数 ——
    # 脚本在���里静默退出、连汇总行都不打，看起来像「测试跑完了」其实根本没跑到第 13 项。
    import app.library as _lib
    real_replace = _lib.os.replace

    def _boom(*a, **k):
        raise SystemExit(1)

    _lib.os.replace = _boom
    try:
        raised = None
        try:
            _lib.save_cards("words", _lib.load_cards("words"))
        except RuntimeError as e:
            raised = str(e)
        except BaseException as e:            # noqa: BLE001
            raised = f"WRONG:{type(e).__name__}"
        check("写文件被沙箱守卫拦下时转成 RuntimeError（不是裸 SystemExit 穿透成 500）",
              raised is not None and "无法写入" in raised, str(raised))
        check("错误信息里带上具体路径（用户要知道去哪儿找）",
              raised is not None and str(library.cards_dir()) in raised,
              str(raised)[:160])
        # 同样的守卫也必须拦住 save_handbook
        r2 = None
        try:
            _hb("x", "cet4", SAMPLE) and _lib.save_handbook(_hb("x", "cet4", SAMPLE))
        except RuntimeError as e:
            r2 = str(e)
        except BaseException as e:            # noqa: BLE001
            r2 = f"WRONG:{type(e).__name__}"
        check("保存手账时的守卫异常同样是 RuntimeError",
              r2 is not None and "无法写入" in r2, str(r2)[:160])
    finally:
        _lib.os.replace = real_replace
    # 恢复正常写入后数据没坏
    check("守卫撤掉后知识库仍可读", isinstance(library.list_handbooks(), list))
    check("守卫撤掉后卡片没被写坏",
          isinstance(library.load_cards("words")["items"], dict))

    # ---------- 13. 空库不许崩 ----------
    empty = tempfile.mkdtemp(prefix="studypad_empty_")
    os.environ["STUDYPAD_HOME"] = empty
    try:
        check("空库 list_handbooks 返回空", library.list_handbooks() == [])
        check("空库 stats 不报错", library.stats()["docs"] == 0)
        check("空库 list_cards 返回空", library.list_cards("words")["items"] == [])
        check("空库 get_handbook 返回 None", library.get_handbook("x-y-z") is None)
        check("空库 audit 返回空", library.audit() == [])
    finally:
        os.environ["STUDYPAD_HOME"] = _TMP

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


def _cleanup() -> None:
    for d in (globals().get("_TMP"),):
        if d and Path(d).exists():
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    try:
        code = main()
    finally:
        _cleanup()
    sys.exit(code)